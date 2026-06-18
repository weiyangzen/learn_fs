<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwtimer.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwtimer.c

## Purpose
Provides the exported ACPICA PM timer interface for non-reduced-hardware systems. It reports timer width, reads the current PM timer tick value, and converts two PM timer snapshots into elapsed microseconds while handling one rollover.

## Important APIs, Types, And Functions
Exports `acpi_get_timer_resolution`, `acpi_get_timer`, and `acpi_get_timer_duration`. Key inputs are `acpi_gbl_FADT.flags`, `ACPI_FADT_32BIT_TIMER`, `acpi_gbl_FADT.xpm_timer_block`, `ACPI_PM_TIMER_FREQUENCY`, and `ACPI_USEC_PER_SEC`.

## Control Flow
Resolution returns 24 bits unless the FADT advertises the 32-bit timer flag. Timer reads reject null output pointers, return `AE_SUPPORT` if ACPI 5.0-style optional PM timer address is absent, then read the GAS via `acpi_hw_read` and truncate to 32 bits. Duration validates output and timer presence, handles equal timestamps as zero, extends `end_ticks` by 2^24 or 2^32 when the interval crosses one wrap, subtracts `start_ticks`, and divides ticks times microseconds-per-second by PM timer frequency.

## State And Persistence
This file is stateless except for reads from FADT-derived global table state. It does not latch hardware or store calibration data.

## Dependencies And Integration Points
Depends on generic GAS reads and ACPICA integer division helpers. Consumers include OS/platform code needing stable firmware timer measurements across CPU C-states.

## Risks And Edge Cases
The duration helper only supports a single rollover, so long intervals on 24-bit timers produce incorrect elapsed time. Missing timer blocks must be handled by callers. Firmware with incorrect 24/32-bit FADT flags changes rollover behavior.

## Test Signals
Validate resolution on FADT variants, reads from real or emulated PM timer GAS addresses, zero-duration behavior, rollover cases for 24-bit and 32-bit timers, missing timer block handling, and comparison against known elapsed wall-clock intervals below rollover limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/hwtimer.c -->
