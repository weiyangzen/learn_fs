# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/Makefile

## Purpose

The MLD `Makefile` defines how the `iwlmld.o` opmode object is built. It selects the module under `CONFIG_IWLMLD`, includes KUnit tests under `CONFIG_IWLWIFI_KUNIT_TESTS`, and conditionally adds debugfs, LED, and D3 power-management objects.

## Important APIs, Types, and Functions

The key build variables are `obj-$(CONFIG_IWLMLD)`, `obj-$(CONFIG_IWLWIFI_KUNIT_TESTS)`, `iwlmld-y`, and conditional `iwlmld-$(CONFIG_IWLWIFI_DEBUGFS)`, `iwlmld-$(CONFIG_IWLWIFI_LEDS)`, and `iwlmld-$(CONFIG_PM_SLEEP)`. `subdir-ccflags-y += -I$(src)/../` exposes parent iwlwifi headers to all MLD sources.

## Control Flow

Kbuild composes `iwlmld.o` from core files such as `mld.o`, `mac80211.o`, `fw.o`, `power.o`, `iface.o`, `link.o`, `rx.o`, `scan.o`, `sta.o`, `tx.o`, `agg.o`, `ap.o`, `mlo.o`, `ftm-initiator.o`, and others. Feature flags add optional files only when their kernel configuration symbols are enabled.

## State and Persistence Behavior

There is no runtime state. The file determines which code paths exist in a given kernel image or module.

## Dependencies and Integration Points

It integrates MLD with Kbuild, parent iwlwifi headers, KUnit tests, debugfs, LEDs, and PM sleep support. Missing an object here makes matching prototypes unusable at link time.

## Risks and Edge Cases

Feature-guard drift is the main risk: code that references debugfs, LED, or D3 symbols must be compiled only when the matching object is present. The broad parent include path can hide missing local includes.

## Test Signals

Build with `CONFIG_IWLMLD=y/m`, with and without debugfs, LEDs, PM sleep, and KUnit tests. Link failures and undefined references are the primary regression signal.
