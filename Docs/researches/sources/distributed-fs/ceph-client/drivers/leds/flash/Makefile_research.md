# sources/distributed-fs/ceph-client/drivers/leds/flash/Makefile

## Purpose
This Makefile maps flash and torch LED Kconfig symbols to their driver objects.

## Important APIs, Types, and Functions
The file contains Kbuild object assignments for MT6360, MT6370, AAT1290, AS3645A, KTD2692, LM3601X, MAX77693, Qualcomm flash, RT4505, RT8515, SGM3140, SY7802, and TPS6131X drivers.

## Control Flow
The parent LED Makefile enters `flash/` only when `CONFIG_LEDS_CLASS_FLASH` is enabled. Within this directory, each `obj-$(CONFIG_LEDS_*)` line includes the matching driver object as built-in or module according to its Kconfig tristate.

## State and Persistence
No runtime state exists in this file. The persistent effect is build composition and module naming.

## Dependencies and Integration Points
The file depends on `drivers/leds/flash/Kconfig` symbols and matching C source filenames. Driver objects rely on LED flash class helpers from the parent directory.

## Risks and Edge Cases
Missing or stale entries make enabled Kconfig symbols fail to build or produce no object. Ordering is not strictly sorted in all groups, so adding new objects should minimize merge churn while preserving readable grouping.

## Test Signals
Enable each flash Kconfig symbol as `m` and confirm the expected `.ko` file is produced. Broad `allmodconfig` catches stale filenames and missing helper dependencies.
