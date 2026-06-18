<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/virtual.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/virtual.c

Purpose: Implements a testing/debug virtual regulator consumer that lets userspace set voltage constraints, current constraints, and mode through sysfs.

Important APIs and types: `struct virtual_consumer_data` stores a mutex, regulator handle, enabled flag, min/max voltage/current requests, and current mode. Sysfs attributes expose `min_microvolts`, `max_microvolts`, `min_microamps`, `max_microamps`, and `mode`. Update helpers call `regulator_set_voltage()`, `regulator_set_current_limit()`, `regulator_enable()`, and `regulator_disable()`.

Control flow: Probe warns once that the driver is for testing only, obtains a supply from platform data or OF `"default"` supply, creates the sysfs group, reads the current regulator mode, and stores private data. Attribute writes parse numeric or string input, update cached constraints under lock, then apply the requested regulator operation and enable or disable according to whether constraints are nonzero. Remove deletes sysfs and disables the regulator if this consumer enabled it.

State and persistence: Cached constraints and mode are software-only. Hardware state persists in the underlying regulator. The enabled flag tracks only operations performed by this driver.

Dependencies and integration points: Depends on regulator consumer APIs, sysfs, optional OF compatible `regulator-virtual-consumer`, and platform data naming for non-OF use.

Risks: Parse failures and invalid modes return `count`, so userspace may not see write errors. Voltage and current helpers share one enabled flag; clearing one constraint class can disable a regulator still needed by the other class. This is intentionally unsuitable for production.

Test signals: Sysfs create/remove, all attribute writes, invalid input behavior, voltage and current enable/disable interactions, mode changes, OF default supply lookup, and cleanup after partial probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/virtual.c -->
