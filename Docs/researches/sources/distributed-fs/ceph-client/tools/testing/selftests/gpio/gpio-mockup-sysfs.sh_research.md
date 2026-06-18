<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup-sysfs.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup-sysfs.sh

## Purpose
This script overrides `gpio-mockup.sh` line helpers to test the deprecated GPIO sysfs ABI instead of the cdev ABI.

## Important APIs, Types, And Functions
It defines `find_sysfs_nr()`, `acquire_line()`, `get_line()`, `set_line()`, and `release_line()`. It uses `/sys/class/gpio/export`, `/sys/class/gpio/unexport`, `direction`, `value`, and `active_low`.

## Control Flow
When sourced, it verifies sysfs and GPIO sysfs support, maps a chip/offset to a global sysfs GPIO number through platform device `base`, exports the line on demand, then implements read/write/release operations for the parent script.

## State And Persistence
It exports GPIO lines into sysfs and unexports them during `release_line()`. It maintains `sysfs_nr` and `sysfs_ldir` shell globals.

## Dependencies And Integration Points
It is sourced by `gpio-mockup.sh -t sysfs` and relies on the parent script's `skip`, `fail`, `chip`, and `offset` variables.

## Risks
The sysfs GPIO ABI is deprecated and may be disabled. Global GPIO base numbers can be absent or dynamic, so discovery depends on mockup platform layout.

## Test Signals
Successful sourced operation lets the parent mockup tests pass through sysfs and prints the deprecation warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup-sysfs.sh -->
