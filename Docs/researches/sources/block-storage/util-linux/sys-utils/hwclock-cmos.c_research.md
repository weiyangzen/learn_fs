# File Research: sources/block-storage/util-linux/sys-utils/hwclock-cmos.c

Purpose: Provides the direct ISA/CMOS hardware-clock backend for `hwclock`, used when direct port access is selected and `USE_HWCLOCK_CMOS` is enabled.

Core behavior:
- Reads and writes classic RTC CMOS registers through `outb()`/`inb()` at ports `0x70` and `0x71`.
- Converts RTC fields between BCD/binary and 12/24-hour formats according to status register B.
- Reads time only when the update-in-progress bit in status register A is clear, then rechecks seconds to reduce the chance of reading a mixed update.
- Sets the clock by setting the SET bit, stopping/resetting the prescaler, writing time fields, then restoring control and frequency registers in the required order.
- Synchronizes to a clock tick by polling the update-in-progress bit for a rise and fall with bounded spin loops.

Important implementation details:
- Years are interpreted without using a century byte: values 69-99 map to 1969-1999 and 00-68 map to 2000-2068.
- `get_permissions_cmos()` requests I/O privilege through `iopl(3)` when available, otherwise uses `ioperm()` over the two CMOS ports.
- The backend exports a `clock_ops` instance with no device path and the label "Using direct ISA access to the clock".

Dependencies and integration:
- Implements `probe_for_cmos_clock()` declared in `hwclock.h`.
- Used by `hwclock.c` only when direct ISA support is compiled and `--directisa` is requested.

Risks and edge cases:
- The `atomic()` wrapper is only a direct call and does not provide real interrupt exclusion; comments acknowledge only the kernel can make CMOS access truly atomic.
- Direct port access requires privileges and platform support; failure is reported as an access-method failure.
