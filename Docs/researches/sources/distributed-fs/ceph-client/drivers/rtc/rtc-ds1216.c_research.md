# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1216.c

## Purpose
Dallas DS1216 RTC platform driver. It accesses a serial bit-stream clock embedded behind a memory-mapped register, using a magic sequence to switch the device into clock mode.

## Important APIs, types, and functions
- `struct ds1216_regs` maps the eight clock bytes including fractional seconds.
- `struct ds1216_priv` stores RTC device and MMIO base.
- `magic[]` is the 64-bit sequence used by `ds1216_switch_ds_to_clock()`.
- `ds1216_read()` and `ds1216_write()` shift 64 bits through the least significant bit of the mapped register.
- `ds1216_rtc_read_time()` switches to clock mode, reads registers, decodes BCD and 12/24-hour mode, and maps years below 70 to 2000+.
- `ds1216_rtc_set_time()` preserves the 12/24-hour mode bit, clears fractional seconds, writes BCD fields, and switches/writes back.
- Probe maps resource, registers RTC, and performs a dummy read to put the clock into a known state.

## Control flow
Every read/write begins by resetting the DS1216 pointer and writing the magic sequence. Set-time reads the existing register block first to preserve mode bits before writing the updated block.

## State and persistence behavior
All clock state persists in DS1216 hardware. Software stores only MMIO and RTC pointers. Fractional seconds are cleared on set-time.

## Dependencies and integration points
Depends on platform MMIO, BCD helpers, and RTC class. Binds through platform alias `"rtc-ds1216"`.

## Risks
- Month handling appears one-based on read and write without the usual `tm_mon - 1/+1` adjustment, so month indexing deserves targeted verification.
- Weekday write uses raw `tm_wday` while read subtracts one from hardware field.
- Bit-banged MMIO has no locking; concurrent RTC core calls rely on framework serialization.
- No validity or oscillator failure checks.

## Test signals
Read/write round trips for month and weekday, 12-hour and 24-hour modes, year 1969/1970/2000 boundaries, dummy-read probe behavior, and MMIO read/write ordering.
