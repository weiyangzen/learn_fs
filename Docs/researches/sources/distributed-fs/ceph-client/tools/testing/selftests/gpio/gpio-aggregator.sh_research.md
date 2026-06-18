<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-aggregator.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-aggregator.sh

## Purpose
This shell test validates the `gpio-aggregator` module using `gpio-sim` chips as backends, covering configfs/sysfs creation, reconfiguration rules, module unload behavior, forwarding functionality, and a race stress test.

## Important APIs, Types, And Functions
It defines simulator helpers `sim_enable_chip()`, `sim_disable_chip()`, `sim_configfs_cleanup()`, `sim_get_chip_label()` and aggregator helpers for chip/line create/remove, key/offset/name setting, live toggles, configfs device/chip name lookup, line count, chip label, and line name. It uses `/sys/kernel/config/gpio-sim`, `/sys/kernel/config/gpio-aggregator`, and `/sys/bus/platform/drivers/gpio-aggregator`.

## Control Flow
The script loads modules, verifies configfs, cleans stale devices, creates two simulated chips with two banks each, then runs numbered scenarios for configfs creation/deletion, sysfs creation/deletion, offline/online/deferred-probe reconfiguration, module unload, forwarding set values/config, and concurrent new/delete plus module load/unload stress.

## State And Persistence
It creates configfs simulator and aggregator devices, toggles `live`, starts temporary `gpio-mockup-cdev` processes, manipulates sysfs `new_device`/`delete_device`, and loads/unloads modules. EXIT cleanup removes devices.

## Dependencies And Integration Points
It depends on root, `gpio-sim`, `gpio-aggregator`, configfs, helper binaries `gpio-chip-info`, `gpio-line-name`, and `gpio-mockup-cdev`.

## Risks
The test is invasive to module state and can unload/reload `gpio-aggregator`. Many checks assume immediate sysfs/configfs consistency except where sleeps are added. The race loop intentionally hammers module load/unload and device creation.

## Test Signals
Expected signal is final `GPIO gpio-aggregator test PASS`, with intermediate assertions confirming invalid configs stay non-live, deferred sysfs devices later become live, online config is immutable, forwarding changes backend values, and module unload is blocked only for configfs-owned devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-aggregator.sh -->
