# sources/distributed-fs/ceph-client/drivers/base/power/Makefile

## Purpose
Builds the driver-core power-management objects selected by kernel configuration.

## Important APIs, Types, And Functions
The Makefile contributes `sysfs.o`, `generic_ops.o`, `common.o`, `qos.o`, `runtime.o`, and `wakeirq.o` for `CONFIG_PM`; `main.o`, `wakeup.o`, and `wakeup_stats.o` for `CONFIG_PM_SLEEP`; `trace.o` for `CONFIG_PM_TRACE_RTC`; `clock_ops.o` for `CONFIG_HAVE_CLK`; and KUnit objects for PM QoS and runtime PM tests.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_...)` variables and compiles only the objects enabled by the configuration. `ccflags-$(CONFIG_DEBUG_DRIVER)` adds `-DDEBUG` for debug driver builds.

## State And Persistence
No runtime state is stored. The file controls which PM capabilities are present in the built kernel and therefore which exported symbols and sysfs/runtime behaviors exist.

## Dependencies And Integration
Integrates with Kbuild and the driver-core PM configuration matrix. The object split matches feature gates used throughout `power.h` and the individual PM source files.

## Risks And Test Signals
Risks are missing objects under a config combination, test object build failures, or unintended debug flag changes. Test signals are allmodconfig/allyesconfig/tiny config builds, `CONFIG_PM=n` builds, and KUnit builds for `CONFIG_PM_QOS_KUNIT_TEST` and `CONFIG_PM_RUNTIME_KUNIT_TEST`.
