<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-asf-plat.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-asf-plat.c

Purpose: AMD Alert Standard Format platform driver layered on PIIX4-compatible SMBus resources. It supports ASF block writes and I2C slave/target receive callbacks for DASH/MCTP-style traffic.

Important APIs and flow: `amd_asf_xfer` rejects reads, enforces ASF length, requests SB800 MMIO ownership, temporarily switches controller to master mode, sends block data through `amd_asf_access`, then restores target setup. `amd_asf_reg_target` configures listening address and enables target interrupts; `amd_asf_process_target` runs in delayed work to read banks and emit `i2c_slave_event` write-request/write-received/stop events. IRQ handling schedules target work or updates controller interrupt bits and writes EOI.

State and dependencies: `struct amd_asf_dev` stores adapter, EOI MMIO, registered target, delayed work, SB800 MMIO config, and port resource. It depends on `i2c-piix4.h` helpers and imports namespace `PIIX4_SMBUS`.

Risks and tests: shared PIIX4/SB800 resource ownership, bank handling, delayed slave event timing, and PEC enablement are sensitive. Test ACPI `AMDI001A` probe, target register/unregister, block length boundaries, IRQ/EOI behavior, and coexistence with PIIX4 SMBus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-asf-plat.c -->
