# sources/distributed-fs/ceph-client/net/wireless/tests/Makefile

## Purpose
This Makefile wires cfg80211 KUnit test objects into the kernel build when `CONFIG_CFG80211_KUNIT_TEST` is enabled.

## Important APIs, Types, And Functions
It defines `cfg80211-tests-y` as `module.o fragmentation.o scan.o util.o chan.o` and adds `cfg80211-tests.o` to `obj-$(CONFIG_CFG80211_KUNIT_TEST)`.

## Control Flow
There is no executable runtime control flow. Kbuild combines the listed objects into one test module/object according to the config symbol.

## State And Persistence
No runtime state is maintained. The file persists the build membership contract for the cfg80211 KUnit suite.

## Dependencies And Integration Points
The Makefile integrates with Linux Kbuild, KUnit, and the corresponding C test files in this directory. `module.o` supplies module metadata, while the other objects register suites with `kunit_test_suite()`.

## Risks And Edge Cases
Forgetting to list a new test object silently excludes its suite. Renaming or removing a C file without updating this list breaks Kbuild for `CONFIG_CFG80211_KUNIT_TEST`.

## Test Signals
The direct signal is a successful kernel build with `CONFIG_CFG80211_KUNIT_TEST=y` or `m`, followed by KUnit discovering the channel, fragmentation, scan/IE-generation, inform-BSS, and 6 GHz scan suites.
