# sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_core.h

Purpose: `cyttsp_core.h` defines the public data structures and transport interface for the older Cypress TTSP core. It is included by `cyttsp_core.c`, `cyttsp_i2c.c`, and `cyttsp_spi.c`.

Important APIs, types, and functions: `struct cyttsp_tch` represents one packed touch record with big-endian X/Y and 8-bit Z. `struct cyttsp_xydata` maps the operational report block, including host/status/mode bytes, four touch records, tracking ID nibbles, gesture fields, and active-distance register. `struct cyttsp_sysinfo_data` and `struct cyttsp_bootloader_data` map sysinfo and bootloader register layouts. `struct cyttsp_bus_ops` is the core transport abstraction with a Linux input bus type plus `read()` and `write()` callbacks. `enum cyttsp_state` separates idle, active, and bootloader-wait states. `struct cyttsp` is the core runtime object and ends with cacheline-aligned flexible `xfer_buf`. The header exports `cyttsp_probe()` and `cyttsp_pm_ops`.

Control flow: transport drivers allocate no core state directly; they provide bus ops and a transfer-buffer size to `cyttsp_probe()`. The core then uses the structures in this header as packed wire-format overlays for I2C/SPI reads.

State and persistence: the header declares only in-memory state. Its packed structs mirror volatile controller registers and reports, while persistent behavior is limited to values supplied by platform properties at probe.

Dependencies and integration points: the header depends on kernel device, regulator, module, type, and error headers. It is the stable contract between bus-specific modules and the common TTSP logic. `CY_NUM_RETRY` sets the transport retry policy used by the core.

Risks: packed wire structs require exact firmware/register layout compatibility. The flexible buffer is cacheline aligned and sized by bus drivers; an undersized bus-provided buffer would break transfer helpers. `extern const struct dev_pm_ops cyttsp_pm_ops` ties bus drivers to the core module's exported PM object.

Test signals: build coverage should include both I2C and SPI modules. Static checks should confirm packed layout sizes match datasheet expectations, and runtime tests should confirm bus ops receive a sufficiently sized `xfer_buf`.
