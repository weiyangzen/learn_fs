<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ali15x3.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ali15x3.c

Purpose: polling SMBus host driver for ALi M1514/M1543-era south bridge controllers.

Important APIs and flow: `ali15x3_setup` unlocks address registers, reads or forces the I/O base (`force_addr` module parameter), checks ACPI conflicts, requests I/O space, enables SMBus device/controller bits, and sets SMBus clock. `ali15x3_access` writes transaction registers for quick/byte/byte-data/word/block transfers, calls `ali15x3_transaction`, then fetches readback data. `ali15x3_transaction` clears stale status, tries timeout reset on busy state, starts the transaction, polls for done/error, and reports collision/no-response, device error, or timeout.

State and dependencies: static `ali15x3_smba`, `force_addr`, and one static adapter define persistent state. Integration is PCI ID based, HWMON-class I2C adapter registration, I/O ports, ACPI conflict checks, and module parameters.

Risks and tests: forced addresses can collide with platform firmware; collision/no-response are indistinguishable; busy recovery can require power reset. Test normal and forced probe, resource conflict rejection, all SMBus sizes, block pointer reset, timeout handling, and unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ali15x3.c -->
