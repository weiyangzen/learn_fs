<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd756.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd756.c

Purpose: polling SMBus driver for AMD756/766/768/8111 SMBus 1.0 and Nvidia nForce controllers.

Important APIs and flow: `amd756_probe` filters PCI function numbers, reads chipset-specific I/O base, validates enable bits, checks ACPI conflicts, requests I/O space, and registers one HWMON-class adapter. `amd756_access` maps SMBus quick/byte/byte-data/word/block operations into host registers and controller cycle type, then calls `amd756_transaction`. The transaction path waits for host/SMBus busy to clear, starts the cycle, polls completion, reports protocol/no-response, collision, timeout, or success, clears status bits, and aborts on stuck states.

State and dependencies: global `amd756_ioport` and static adapter limit support to one device. It depends on PCI IDs, ACPI resource checking, I/O ports, sleeps, and I2C `smbus_xfer`.

Risks and tests: singleton state, chipset-specific function filtering, and abort recovery are risks; block transfer uses simple FIFO-like host block data access. Test supported IDs/functions, all SMBus operations, collision/no-response/timeout injection, ACPI conflict rejection, and unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd756.c -->
