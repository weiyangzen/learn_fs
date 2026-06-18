<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-sim.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-sim.sh

## Purpose
This shell test validates the `gpio-sim` configfs interface, cdev-visible metadata, sysfs simulator controls, hogged lines, and functional line behavior.

## Important APIs, Types, And Functions
Helpers include `remove_chip()`, `create_chip()`, `create_bank()`, `set_label()`, `set_num_lines()`, `set_line_name()`, `enable_chip()`, `disable_chip()`, `configfs_cleanup()`, `configfs_chip_name()`, `configfs_dev_name()`, `get_chip_num_lines()`, `get_chip_label()`, `get_line_name()`, and `sysfs_set_pull()`.

## Control Flow
The script loads `gpio-sim`, waits for configfs, cleans stale chips, then runs numbered tests for chip/dev name attributes, default/custom line counts, labels, line names, invalid line directory names, multiple chips, immutable live settings, probe error propagation, no-bank rejection, duplicate label rejection, hogged lines, pull set/read/reject through sysfs, read-only value, and functional value/bias behavior through `gpio-mockup-cdev`.

## State And Persistence
It creates configfs chips/banks/lines/hogs, toggles `live`, reads platform sysfs paths, and starts temporary cdev helper processes. EXIT cleanup removes configfs devices.

## Dependencies And Integration Points
It depends on `gpio-sim`, configfs, GPIO cdev helpers `gpio-chip-info`, `gpio-line-name`, and `gpio-mockup-cdev`.

## Risks
The cleanup loop assumes all entries under configfs are chips created by tests; stale external simulator devices could be removed. Several checks depend on immediate sysfs/cdev propagation with small sleeps.

## Test Signals
Expected final `GPIO gpio-sim test PASS` plus intermediate checks for metadata, immutability, rejection paths, hog behavior, pull values, and cdev-driven value changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-sim.sh -->
