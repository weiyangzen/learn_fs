<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2-pci.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2-pci.c

Purpose: PCI-side communication driver for AMD MP2 I2C hardware. It owns the PCI device, MMIO mailbox, IRQ, runtime PM, and shared command serialization used by platform I2C adapters.

Important APIs and flow: exported functions include `amd_mp2_bus_enable_set`, `amd_mp2_rw`, `amd_mp2_process_event`, `amd_mp2_rw_timeout`, callback register/unregister, and `amd_mp2_find_device`. Commands are encoded into C2P message registers; small transfers use C2P message data, larger transfers pass DMA addresses. The IRQ handler reads per-bus P2C event registers, clears them, disables interrupt generation, stores the event, and calls the registered platform completion callback. Event processing validates response/status, length, and slave address, copies read data when needed, and unlocks the shared C2P mutex.

State and dependencies: `struct amd_mp2_dev` tracks two bus callbacks, MMIO, lock owner, PCI state, and IRQ. Dependencies are PCI, DMA, runtime PM, and the shared MP2 header.

Risks and tests: the single C2P mailbox makes lock/unlock correctness critical; timeout paths must release locks; only one MP2 device is discoverable by platform code. Test two-bus concurrency, DMA and <=32-byte paths, interrupts, suspend/resume, timeout recovery, and remove register clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2-pci.c -->
