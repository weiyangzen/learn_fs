# sources/distributed-fs/ceph-client/drivers/acpi/acpi_tad.c

## Purpose
`acpi_tad.c` implements the ACPI Time and Alarm Device driver for `ACPI000E`. It exposes AC/DC wake timer controls and optional real-time clock functionality through sysfs and, when RTC support is enabled, registers an RTC class device.

## Important APIs, Types, And Functions
Important capability bits include `ACPI_TAD_AC_WAKE`, `ACPI_TAD_DC_WAKE`, `ACPI_TAD_RT`, `ACPI_TAD_RT_IN_MS`, and S4/S5 wake flags. Core types are `struct acpi_tad_driver_data` and packed `struct acpi_tad_rt`. Important functions include `acpi_tad_rt_is_invalid()`, `acpi_tad_set_real_time()`, `acpi_tad_evaluate_grt()`, `acpi_tad_get_real_time()`, wake helper methods for `_STV`, `_TIV`, `_STP`, `_TIP`, `_CWS`, and `_GWS`, sysfs handlers for time/caps/ac/dc alarm/policy/status, RTC conversions and ops, `acpi_tad_register_rtc()`, `acpi_tad_remove()`, and `acpi_tad_probe()`.

## Control Flow
Probe obtains the ACPI handle, evaluates `_GCP` capabilities, clears wake capability bits if `_PRW` is missing, suppresses DC wake unless AC wake is supported, allocates driver data, enables wakeup and runtime PM assumptions, registers cleanup, and registers an RTC if real-time support is present. Sysfs time writes parse `year:month:day:hour:minute:second:tz:daylight`, validate ranges, and call `_SRT`; reads call `_GRT`. Alarm and policy writes convert either a special string (`disabled` or `never`) or a numeric value and call `_STV` or `_STP`; reads call `_TIV` or `_TIP`. Status writes accept only zero and call `_CWS`; reads call `_GWS`. RTC alarm programming computes seconds between current TAD time and target alarm, writes AC and optional DC timers, and rolls back AC if DC programming fails while enabling.

## State And Persistence
Driver state is the capability mask and runtime PM/wakeup state. Timer values, wake policies, status bits, and real time live in platform firmware and are accessed via AML methods. Sysfs attribute visibility is derived from capabilities. On removal the driver disables AC/DC timers, clears status, suspends runtime PM, and disables runtime PM.

## Dependencies And Integration Points
It depends on ACPI platform devices, ACPI methods `_GCP`, `_PRW`, `_SRT`, `_GRT`, `_STV`, `_TIV`, `_STP`, `_TIP`, `_CWS`, and `_GWS`, runtime PM, system wakeup, sysfs attribute groups, suspend support, and optional RTC class support.

## Risks
The probe uses `if (ACPI_TAD_AC_WAKE)` instead of checking `caps & ACPI_TAD_AC_WAKE`, so wakeup/runtime driver flags are enabled unconditionally; this may be intentional-by-accident and should be reviewed. Firmware method return codes are collapsed to `-EIO`, limiting diagnostics. The TAD time parser mutates a duplicated string and requires exact colon-separated fields. RTC alarms are relative seconds and reject past or too-far targets. Runtime PM acquire macro behavior must ensure matching release through scoped cleanup.

## Test Signals
Tests should cover capability combinations, missing `_GCP`, missing `_PRW`, AC-only and AC+DC timers, sysfs visibility, all wake methods, special values `disabled` and `never`, invalid time fields, RTC read/set time, RTC alarm enable/disable, rollback when DC alarm programming fails, and removal cleanup disabling timers.
