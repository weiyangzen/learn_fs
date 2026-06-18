# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwesleep.c

## Purpose
`hwesleep.c` implements sleep and wake support for ACPI extended FADT v5 sleep control/status registers.

## Important APIs, Types, and Functions
Exports are `acpi_hw_execute_sleep_method()`, `acpi_hw_extended_sleep()`, `acpi_hw_extended_wake_prep()`, and `acpi_hw_extended_wake()`. Dependencies include `acpi_evaluate_object()`, `acpi_read()`, `acpi_write()`, `acpi_os_enter_sleep()`, `ACPI_FLUSH_CPU_CACHE()`, FADT sleep control/status GAS fields, and globals such as `acpi_gbl_sleep_type_a`, `acpi_gbl_sleep_type_a_s0`, and `acpi_gbl_system_awake_and_running`.

## Control Flow, State, and Persistence
Sleep-method execution builds a one-integer argument list and ignores missing methods while logging other failures. Extended sleep validates sleep registers, clears wake status, marks the system not awake, computes sleep control from `_Sx` sleep type A plus sleep enable, flushes CPU cache before S1-S3, calls `acpi_os_enter_sleep()`, writes the sleep control register unless the OS hook terminates the sequence, and polls sleep status until wake status is set. Wake prep optionally writes S0 sleep type plus enable. Wake invalidates sleep type A, runs `_SST(WAKING)` and `_WAK`, clears wake status for BIOS compatibility, marks the system awake, then runs `_SST(WORKING)`.

## Dependencies and Integration Points
This file integrates ACPICA sleep-state preparation, FADT extended registers, OS sleep entry hooks, and AML sleep/wake methods. It must be called in the interrupt state documented by each function.

## Risks and Test Signals
Risks include infinite polling if wake status never appears, incorrect interrupt-state callers, stale sleep type globals, OS hook termination semantics, missing register handling, and firmware methods with side effects. Tests should cover absent sleep registers, read/write failures, each sleep state, OS hook `AE_CTRL_TERMINATE`, wake-status polling, S0 wake prep, missing and failing `_SST`/`_WAK`, and global awake/sleep-type transitions.
