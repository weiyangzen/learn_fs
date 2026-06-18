# sources/distributed-fs/ceph-client/drivers/hwmon/ultra45_env.c

## Purpose
Platform hwmon driver for the Sun Ultra 45 PIC16F747 environmental monitor. It exposes fan speeds/setpoints, fan fault bits, several board temperatures, status bits, firmware version, and a legacy `name` attribute.

## Important APIs, Types, and Functions
`struct env` stores MMIO base, spinlock, and hwmon device. `env_read()` and `env_write()` serialize indirect register access through `REG_ADDR`/`REG_DATA`. Sysfs callbacks implement fan RPM conversion, fan speed writes, fan fault/status bits, temperature reads, firmware version, and name. `env_probe()` maps OF resources, creates a static sysfs attribute group, and registers hwmon.

## Control Flow
The OF platform driver matches `SUNW,ebus-pic16f747-env`. Probe allocates state, initializes the spinlock, maps the PIC register window with `of_ioremap()`, creates the custom sysfs group, registers the hwmon device, and stores drvdata. Reads and writes access indirect PIC registers under the spinlock except status/firmware direct register reads. Remove reverses sysfs, hwmon registration, and MMIO mapping.

## State and Persistence
No periodic cache is maintained. Fan speed writes persist in the environmental controller register. The only driver state is the mapped base and lock. Status/fault/temp reads reflect current controller data; the controller may independently mark data stale/busy/faulted through status bits exposed by sysfs.

## Dependencies and Integration Points
Depends on OF platform resources, MMIO accessors, legacy hwmon sysfs macros, and Sun EBus/OpenFirmware node naming. It uses `hwmon_device_register()` plus a manually created sysfs group rather than channel-info APIs.

## Risks
Temperature values are returned as whole degrees Celsius after subtracting 64, not millidegrees as modern hwmon convention expects for standard `temp*_input` names; attribute names are mostly board-specific legacy names. Fan conversion only stores the high byte of the period, limiting precision. Direct status reads are not spinlock-protected, though they do not use the indirect address register. Error unwinding is manual and must keep sysfs/hwmon/iounmap ordering correct.

## Test Signals
Validate OF match/probe/remove unwinding, sysfs file presence, fan RPM zero/invalid-period handling, rejecting zero RPM writes, spinlock coverage for indirect access, status bit mapping, firmware version upper-nibble extraction, and expected board-specific temperature naming/units.
