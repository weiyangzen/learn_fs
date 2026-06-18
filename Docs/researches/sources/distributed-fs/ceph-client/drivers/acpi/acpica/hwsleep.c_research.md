<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwsleep.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwsleep.c

## Purpose
Implements legacy ACPI sleep and wake transitions through the original FADT PM1/PM2 register model for non-reduced-hardware systems. It is the low-level half of the public sleep API: callers prepare global sleep-type values elsewhere, then this file programs `SLP_TYP`/`SLP_EN`, manages wake GPEs, waits for wake status, and restores post-resume ACPI state.

## Important APIs, Types, And Functions
Exports internal hardware routines `acpi_hw_legacy_sleep`, `acpi_hw_legacy_wake_prep`, and `acpi_hw_legacy_wake`. They use `struct acpi_bit_register_info`, fixed bit register IDs such as `ACPI_BITREG_SLEEP_TYPE`, `ACPI_BITREG_SLEEP_ENABLE`, and `ACPI_BITREG_WAKE_STATUS`, and globals including `acpi_gbl_sleep_type_a/b`, `acpi_gbl_sleep_type_a_s0/b_s0`, `acpi_gbl_system_awake_and_running`, and fixed event metadata.

## Control Flow
`acpi_hw_legacy_sleep` clears wake status, disables runtime GPEs, clears ACPI status, marks the system not awake, enables wake GPEs, reads PM1 control, writes sleep type first, flushes CPU caches for S1-S3, lets `acpi_os_enter_sleep` veto or prepare platform sleep, writes sleep enable, retries S4/S5 after a long stall if execution continues, then polls `WAK_STS`. Wake preparation optionally writes S0 sleep type back into PM1 control. Final wake disables all GPEs, enables runtime GPEs, invokes `_WAK`, clears `WAK_STS`, restores power/sleep button fixed events, and reports `_SST` working.

## State And Persistence
The file mutates ACPI global sleep type state, global awake/running state, PM1 control/status registers, fixed event enable/status bits, and GPE enable masks. Nothing is durable beyond hardware register state across suspend/resume.

## Dependencies And Integration Points
Depends on ACPICA hardware register helpers, GPE management, fixed event metadata, OS hooks for entering sleep and stalling, and AML sleep methods `_SST` and `_WAK`. It is selected by `hwxfsleep.c` when `acpi_gbl_reduced_hardware` is false.

## Risks And Edge Cases
This code must run with the documented interrupt state; wrong ordering can miss wake events or leave GPEs disabled. Firmware quirks require split `SLP_TYP`/`SLP_EN` writes and S4/S5 retry behavior. Errors while re-enabling runtime GPEs can affect wake-device behavior after resume. Polling wake status assumes the platform eventually sets `WAK_STS`.

## Test Signals
Suspend/resume tests for S1-S5 on legacy ACPI machines, wake from GPE devices, power/sleep button events after resume, PM1 control tracing, `_WAK` execution logs, and failure injection around GPE disable/enable and PM1 register writes are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwsleep.c -->
