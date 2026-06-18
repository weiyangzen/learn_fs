# sources/distributed-fs/ceph-client/tools/testing/selftests/power_supply/helpers.sh

## Purpose
Provides KTAP-oriented shell helpers for validating power_supply sysfs files and uevent properties.

## Important APIs, Types, and Functions
Important functions are `calc`, `test_sysfs_prop`, `to_human_readable_unit`, `_check_sysfs_prop_available`, `test_sysfs_prop_optional`, `test_sysfs_prop_optional_range`, `test_sysfs_prop_optional_list`, `dump_file`, `__test_uevent_prop`, `test_uevent_prop`, and `test_uevent_prop_optional`.

## Control Flow
Helpers build paths under `$SYSFS_SUPPLIES/$DEVNAME`, check file existence/readability, compare exact values or ranges/lists, print reported values with optional unit conversion, and emit KTAP pass/fail/skip outcomes. Uevent helpers grep `POWER_SUPPLY_<PROP>=...` and dump the file on mismatch.

## State and Persistence
State is carried through shell globals `SYSFS_SUPPLIES` and `DEVNAME`; `IFS` is temporarily changed for comma-separated list validation and restored. No files are modified.

## Dependencies and Integration Points
Depends on `awk`, `grep`, `cat`, shell arithmetic, sysfs power_supply files, and KTAP helper functions sourced by the caller.

## Risks and Test Signals
Risks include numeric comparisons on nonnumeric sysfs values, exact string matching in uevent, and a fragile unit conversion display path. Failures are exposed as KTAP failures or skips for absent optional properties.
