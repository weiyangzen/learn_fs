# sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss.c

Purpose: shared Intel LPSS MFD core. It maps controller private registers, determines whether the device is I2C/UART/SPI, creates iDMA and host-controller child devices, builds clock lookup trees, exposes latency tolerance controls, and implements suspend/resume context handling.

Important APIs/types/functions: exported `intel_lpss_probe()`, `intel_lpss_remove()`, and `intel_lpss_pm_ops`; internal `struct intel_lpss`; MFD cells for `i2c_designware`, `dw-apb-uart`, `pxa2xx-spi`, and `idma64`; clock helpers; LTR/debugfs helpers.

Control flow: probe validates resources, ioremaps private registers, reads capabilities, selects the child cell by type, initializes reset/remap/DMA registers, allocates a stable MFD id, registers clocks, exposes PM QoS latency tolerance, adds debugfs, optionally registers idma64 first, then adds the host-controller child. Remove reverses child registration, debugfs, PM QoS, clocks, and ID allocation.

State and persistence: stores private register context in `priv_ctx` during system/runtime suspend and restores it on resume. Latency-tolerance values are cached for debugfs. No persistent disk state exists.

Dependencies and integration: used by ACPI and PCI wrappers. Integrates with MFD core, clk/clkdev, PM QoS, runtime/system PM, debugfs, idma64 DMA, and child serial/I2C/SPI drivers.

Risks: register ordering matters: DMA must appear before host controller, remap address must reflect parent resource, and non-UART devices are reset during suspend. Clock-tree unwind must match partial registration. Capability decoding errors create wrong child devices.

Test signals: child probe order, DMA fallback logs, clock lookup by child driver, latency tolerance sysfs/debugfs behavior, suspend/resume on UART console and non-UART controllers, and runtime PM under active transfers.
