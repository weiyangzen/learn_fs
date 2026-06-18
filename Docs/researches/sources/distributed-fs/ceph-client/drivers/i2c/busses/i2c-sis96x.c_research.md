# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sis96x.c

Purpose: Legacy SiS96x SMBus PCI driver. It exposes one SMBus adapter for PCI devices with SiS SMBus class/resource setup, relying on PCI quirks on many machines to expose the BAR correctly.

Important APIs/types/functions: global `sis96x_smbus_base` and `sis96x_adapter` implement the singleton controller. `sis96x_read()`/`sis96x_write()` access IO registers. `sis96x_transaction()` performs busy reset, clock/timeout setup, command start, polling, error mapping, and status cleanup. `sis96x_access()` maps Linux SMBus quick/byte/byte-data/word/process-call operations to hardware registers. Probe/remove register and tear down the adapter.

Control flow: probe rejects a second device, verifies PCI class `PCI_CLASS_SERIAL_SMBUS`, obtains BAR0, checks ACPI resource conflict, reserves the IO range, fills adapter parent/name, and registers the adapter. Transfers program address/command/data registers, select the protocol size, run the transaction, and read byte/word return data when applicable.

State and persistence: only one adapter/base can exist. There is no interrupt, DMA, PM, or per-transfer persistent state beyond programmed IO registers. Each transaction forces SMBus control to disable timeout interrupts and select fast host clock.

Dependencies/integration: PCI core, ACPI resource conflict checking, IO port access, I2C SMBus algorithm, HWMON class, and module PCI driver registration.

Risks: marked beta and based on SiS630 definitions without datasheet. No block data support despite constants. Busy reset may fail and return `-EBUSY`; collision maps to `-EIO`. Singleton design prevents multiple controllers. BAR setup relies on external PCI quirks for many systems. Status cleanup writes back the observed status and only logs if sticky bits remain.

Test signals: class mismatch rejection, missing BAR, ACPI conflict, IO reservation conflict, duplicate-device rejection, quick/byte/byte-data/word/process-call transfers, timeout, device error, collision, sticky status cleanup, and remove cleanup resetting `sis96x_smbus_base`.
