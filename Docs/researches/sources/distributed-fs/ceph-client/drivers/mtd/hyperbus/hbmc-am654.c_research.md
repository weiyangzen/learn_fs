# sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/hbmc-am654.c

Purpose: TI AM654 HyperBus Memory Controller adapter. It maps a child HyperFlash resource, optionally selects a mux, calibrates CFI access, accelerates large reads with DMA, and registers the device through the HyperBus core.

Important APIs/types/functions: `struct am654_hbmc_priv` embeds `hyperbus_ctlr`, `hyperbus_device`, and mux control. `struct am654_hbmc_device_priv` stores DMA completion, physical base, controller, and RX DMA channel. Operations are `am654_hbmc_calibrate()` and `am654_hbmc_read()` in `am654_hbmc_ops`; lifecycle is `am654_hbmc_probe()`/`am654_hbmc_remove()`.

Control flow: probe gets the first child DT node, translates its resource, optionally selects `mux-controls`, ioremaps the child memory window into `hbdev.map`, initializes controller ops, allocates private DMA state, requests a memcpy DMA channel, then calls `hyperbus_register_device()`. Reads use DMA for buffers that are not stack objects, are virt-address-valid, and have length at least 1 KiB; otherwise they fall back to `memcpy_fromio()`. Calibration sends CFI query commands until five consecutive query-present checks pass or attempts run out.

State and persistence: persistent state is HyperFlash contents. Runtime state is mux selection, mapped memory window, optional DMA channel, completion, and HyperBus/MTD registration.

Dependencies/integration: HyperBus core, MTD CFI helpers, DMA engine, mux consumer API, OF address parsing, platform bus compatible `ti,am654-hbmc`.

Risks: calibration returns the last `cfi_qry_present()` value and core treats zero as failure, so semantics must match CFI helper expectations. DMA timeout scales as `len + 1000` ms and may be excessive for large reads. DMA is skipped for stack or non-linear buffers.

Test signals: probe with/without mux, child resource parsing, DMA channel defer/unavailable paths, DMA success/fallback/timeout, calibration success/failure, HyperBus registration failure cleanup, and remove releasing DMA/mux/node.
