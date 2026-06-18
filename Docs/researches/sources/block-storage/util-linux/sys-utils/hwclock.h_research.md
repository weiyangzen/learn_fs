# File Research: sources/block-storage/util-linux/sys-utils/hwclock.h

Purpose: Shared interface for the `hwclock` implementation and its hardware backends.

Core contents:
- Defines debug mask bits and `DBG`/`ON_DBG` macros for hwclock-specific util-linux debugging.
- Defines `struct hwclock_control`, the central option/state bundle shared by `hwclock.c`, RTC, and CMOS backends.
- Defines `struct clock_ops`, the backend vtable for permissions, read, set, tick synchronization, and device path lookup.
- Declares CMOS and RTC probe functions, optional Alpha epoch helpers, Linux RTC parameter helpers, voltage-low helpers, `hwclock_exit()`, and `parse_date()`.

Dependencies and integration:
- Included by all hwclock source files in this group.
- Encodes platform-conditional fields so callers and backends share a single control ABI across Linux, GNU, Alpha, and direct ISA builds.

Risks and edge cases:
- Many fields in `hwclock_control` are conditional, so source files must preserve matching preprocessor guards when accessing them.
