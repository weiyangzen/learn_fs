# sources/distributed-fs/ceph-client/drivers/hwmon/adt7x10.h

Purpose: shared header that defines the logical register namespace and exported entry points used by the ADT7x10 common core and its I2C/SPI bus wrappers.

Important APIs/types/functions: the register enum defines `ADT7X10_TEMPERATURE`, `ADT7X10_STATUS`, `ADT7X10_CONFIG`, `ADT7X10_T_ALARM_HIGH`, `ADT7X10_T_ALARM_LOW`, `ADT7X10_T_CRIT`, `ADT7X10_T_HYST`, and `ADT7X10_ID`. `adt7x10_probe(struct device *dev, const char *name, int irq, struct regmap *regmap)` is the common probe entry used by `adt7310.c` and `adt7410.c`. `adt7x10_dev_pm_ops` exposes shared suspend/resume operations for bus drivers.

Control flow: bus wrappers include this header, translate their physical registers into the logical enum where needed, create a regmap that understands these logical addresses, and call `adt7x10_probe()`. The common core then uses only this logical register namespace and the provided regmap.

State and persistence: the header stores no state, but it defines the ABI between wrapper and core. Any change to enum order or meaning changes which physical registers the wrappers read/write and therefore affects cached config, limits, status, and temperature values.

Dependencies and integration: depends on `linux/pm.h` for PM declarations and forward declarations of `struct device` and `struct regmap` from including C files. It is internal to the hwmon driver cluster rather than a user-visible UAPI header.

Risks: because the enum is positional, wrappers that use lookup tables, such as the SPI wrapper, depend on every value remaining stable. Adding registers requires updates in both common code and bus regmap callbacks. A mismatch can silently redirect writes to thresholds or config registers.

Test signals: build-test both `adt7310` and `adt7410` after enum/API changes, verify shared probe symbol linkage under modular builds, and run common hwmon attribute tests over both transports to catch logical-register mapping regressions.
