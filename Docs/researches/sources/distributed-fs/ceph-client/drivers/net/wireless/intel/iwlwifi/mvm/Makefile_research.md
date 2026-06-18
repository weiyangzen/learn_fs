# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/Makefile

## Purpose

Defines kbuild composition for the iwlwifi MVM object and optional MVM support objects.

## Important APIs, Types, and Functions

`obj-$(CONFIG_IWLMVM) += iwlmvm.o` enables the core object. `iwlmvm-y` lists unconditional implementation files, including RX/TX, binding, quota, station, scan, power, coexistence, FTM, RFI, MLD, PTP, and time-sync components. Optional entries include `debugfs.o debugfs-vif.o` for `CONFIG_IWLWIFI_DEBUGFS`, `led.o`, `d3.o` for `CONFIG_PM_SLEEP`, `vendor-cmd.o`, and KUnit tests.

## Control Flow

No runtime flow. kbuild expands config-dependent object lists and links selected objects into `iwlmvm.o`.

## State and Persistence Behavior

No runtime state. Build-time object membership determines which features exist in the compiled driver.

## Dependencies and Integration Points

Integrates with Linux kbuild and Kconfig. It controls inclusion of files in this subset: `binding.c` and `coex.c` are unconditional, `debugfs*.c` are debugfs-gated, and `d3.c` is PM-sleep-gated. `subdir-ccflags-y` exposes parent iwlwifi headers.

## Risks

Incorrect object gating can remove features or create unresolved symbols in specific configs. Optional declarations must stay aligned with config guards.

## Test Signals

Build representative configs with and without `CONFIG_IWLWIFI_DEBUGFS`, `CONFIG_PM_SLEEP`, LEDs, MEI, and KUnit tests.
