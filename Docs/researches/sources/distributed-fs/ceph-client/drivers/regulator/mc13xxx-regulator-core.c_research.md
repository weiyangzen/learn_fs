<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mc13xxx-regulator-core.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mc13xxx-regulator-core.c

## Purpose
Provides shared regulator operations and OF parsing helpers for MC13xxx-family PMIC regulator drivers.

## Important APIs, Types, And Functions
Exports `mc13xxx_regulator_ops`, `mc13xxx_fixed_regulator_ops`, `mc13xxx_fixed_regulator_set_voltage()`, `mc13xxx_get_num_regulators_dt()`, and `mc13xxx_parse_regulators_dt()`. Runtime callbacks include enable, disable, is_enabled, table voltage listing, selector set, and voltage read through `struct mc13xxx_regulator_priv` and per-chip `struct mc13xxx_regulator` metadata.

## Control Flow
Generic regulator ops retrieve private state with `rdev_get_drvdata()`, index the chip descriptor by regulator ID, and call MC13xxx register read/modify/write helpers. OF helpers locate the parent MFD `regulators` child, count children, allocate init-data records, match child node names against descriptor names, and return a compact parsed list while updating `priv->num_regulators` to the parsed count.

## State And Persistence
The core does not own long-lived state beyond data stored by chip drivers in `mc13xxx_regulator_priv`. It reads and writes PMIC registers through the parent MFD. DT parse results are devm-managed and persist for the platform device lifetime.

## Dependencies And Integration Points
Depends on MC13xxx MFD APIs, OF regulator parsing, platform devices, exported GPL symbols, and regulator core helpers. Chip drivers include `mc13xxx.h` and use this file as their common implementation.

## Risks And Test Signals
Risks include `BUG_ON()` if a hardware selector exceeds table length, descriptor IDs not matching array indexes, OF child names silently skipped except for warnings, and fixed-voltage constraints rejecting valid board data if tables are wrong. Test through MC13783 and MC13892 probe paths, OF parsing with known and unknown children, selector read/write for every table-backed regulator, and module symbol linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mc13xxx-regulator-core.c -->
