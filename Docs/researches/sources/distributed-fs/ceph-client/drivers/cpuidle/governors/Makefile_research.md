<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/Makefile -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/governors/Makefile

## Purpose

This Makefile selects which cpuidle governor objects are built from Kconfig symbols.

## Important APIs, Types, And Functions

It maps `CONFIG_CPU_IDLE_GOV_LADDER` to `ladder.o`, `CONFIG_CPU_IDLE_GOV_MENU` to `menu.o`, `CONFIG_CPU_IDLE_GOV_TEO` to `teo.o`, and `CONFIG_CPU_IDLE_GOV_HALTPOLL` to `haltpoll.o`.

## Control Flow

There is no runtime flow. Build-time object inclusion determines which governors can register at postcore init and appear in `/sys/devices/system/cpu/cpuidle/available_governors`.

## State And Persistence Behavior

The Makefile owns no runtime state, but missing object inclusion means no persistent governor registration for that algorithm.

## Dependencies And Integration Points

It integrates Kconfig choices with the cpuidle governor registration source files under `drivers/cpuidle/governors`.

## Risks And Test Signals

Risks include Kconfig symbols not matching object names or adding a governor without updating the Makefile. Test by building each governor configuration and checking available governors at boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/Makefile -->
