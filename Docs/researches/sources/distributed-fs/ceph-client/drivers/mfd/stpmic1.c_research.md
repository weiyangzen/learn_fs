# sources/distributed-fs/ceph-client/drivers/mfd/stpmic1.c

## Purpose
`stpmic1.c` is the I2C MFD parent for STPMIC1 PMICs. It defines regmap access rules, exposes PMIC interrupts through regmap-irq, registers child devices from DT, and installs a power-off handler.

## Important APIs, Types, and Functions
Regmap access tables define readable, writable, and volatile ranges. `stpmic1_irqs` maps PMIC interrupt bits. `stpmic1_regmap_irq_chip` defines pending, mask, unmask, and ACK bases. `stpmic1_power_off()` requests software switch-off with retries. `stpmic1_probe()` initializes the regmap, reads version, registers the IRQ chip and power-off handler, and populates children. PM callbacks are `stpmic1_suspend()` and `stpmic1_resume()`.

## Control Flow
Probe allocates `struct stpmic1`, creates an 8-bit cached regmap, gets the main IRQ from DT, reads `VERSION_SR`, creates the regmap IRQ domain on the main IRQ, registers the system power-off callback, and populates OF child devices. Suspend disables the main IRQ. Resume syncs the regcache and re-enables the IRQ.

## State and Persistence
State includes the parent regmap, IRQ number, IRQ chip data, and device pointer. Regmap maple cache preserves writable register values for resume synchronization. Interrupt pending/source and status registers are volatile.

## Dependencies and Integration Points
It depends on I2C, OF IRQ parsing, regmap/regmap-irq, reboot sys-off handlers, and STPMIC1 child devices under the PMIC DT node.

## Risks and Edge Cases
The power-off path retries because I2C access can transiently time out, but even repeated failure returns `NOTIFY_DONE`. Resume depends on `regcache_sync()` restoring cached writable state. Main IRQ acquisition is mandatory.

## Test Signals
Verify version read, all regmap IRQ lines and masks, child OF population, system power-off register update with retry behavior, suspend/resume regcache sync, and access-table enforcement for invalid registers.
