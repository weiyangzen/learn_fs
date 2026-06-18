<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2-plat.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2-plat.c

Purpose: ACPI platform-side AMD MP2 I2C adapter driver. It creates I2C adapters for MP2 bus IDs and delegates command transport to the PCI-side MP2 driver.

Important APIs and flow: `i2c_amd_probe` reads ACPI UID as bus ID, finds the MP2 PCI device, registers a callback, configures adapter quirks and speed, enables the bus, and calls `i2c_add_adapter`. `i2c_amd_xfer` runtime-PM gets the PCI device, sends each message via `i2c_amd_xfer_msg`, then releases PM. Messages over 32 bytes are mapped with DMA; completion waits on a per-adapter completion and then calls `amd_mp2_process_event`. Suspend/resume disable and re-enable the MP2 bus.

State and dependencies: `struct amd_i2c_dev` wraps shared `amd_i2c_common`, platform device, adapter, and completion. It depends on ACPI `AMDI0011`, MP2 PCI exports, DMA-safe I2C buffers, runtime PM, and I2C core.

Risks and tests: probe assumes one MP2 PCI device; remove must block transfers while clearing callbacks; DMA unmap on timeout is delicate. Test ACPI UID 0/1, deferred probe, long transfers, timeout, suspend/resume, removal during bus lock, and speed mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2-plat.c -->
