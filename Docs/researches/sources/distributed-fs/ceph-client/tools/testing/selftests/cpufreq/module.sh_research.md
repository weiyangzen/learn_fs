# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/module.sh

## Purpose

`module.sh` tests cpufreq driver and governor modules with insertion/removal, basic cpufreq operations, CPU hotplug interaction, and removal protection while a governor is in use.

## Important APIs, Types, and Functions

It defines `test_basic_insmod_rmmod()`, `module_driver_test_single()`, `module_driver_test()`, `find_gov_name()`, `module_governor_test_single()`, `module_governor_test()`, and `module_test()`. It calls `insmod`, `rmmod`, governor helpers, CPU hotplug helpers, and `cpufreq_basic_tests()`.

## Control Flow

Driver tests verify standalone insmod/rmmod, insert the driver and run basic tests, optionally offline non-boot CPUs before insertion and online them after insertion, then remove the driver and check cpufreq directories disappear. Governor tests insert a governor module, switch each policy to the new governor, attempt and expect `rmmod` failure while in use, restore the original governor, then unload. Combined tests exercise driver-before-governor and governor-before-driver orderings.

## State and Persistence Behavior

It mutates loaded kernel modules, CPU online state, cpufreq governor state, and policy sysfs layout. It uses current working directory module filenames passed by the user.

## Dependencies and Integration Points

It requires root, module unload support, cpufreq modules present as `.ko` files, and cpufreq sysfs availability. It integrates cpufreq core with module lifecycle and hotplug paths.

## Risks and Edge Cases

Module insertion/removal can fail if modules are built-in, absent, already in use, or have dependencies. The tests intentionally remove modules and offline CPUs, so they are unsuitable for shared production systems. Some failures are printed and returned rather than always hard-failing.

## Test Signals

Signals include successful insmod/rmmod cycles, successful basic cpufreq tests after insertion, failed governor module removal while active, restored governors, and absence of cpufreq directories after driver removal.
