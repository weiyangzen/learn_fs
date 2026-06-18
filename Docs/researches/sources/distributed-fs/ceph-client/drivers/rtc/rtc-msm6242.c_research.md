# sources/distributed-fs/ceph-client/drivers/rtc/rtc-msm6242.c

Purpose: implements the Oki MSM6242 legacy RTC, used on m68k-era systems, using 4-bit digit registers mapped as 32-bit MMIO slots.

Important APIs/types/functions: `struct msm6242_priv` stores the MMIO register array and RTC device. `msm6242_read()`/`write()` use raw 32-bit access while masking to low nibbles. `msm6242_lock()` asserts HOLD and retries while BUSY is set, and `msm6242_unlock()` releases HOLD. `msm6242_read_time()` and `msm6242_set_time()` handle digit-by-digit BCD-like fields, weekday, month, year, and 12/24-hour conversion.

Control flow: probe gets the memory resource, maps it with `devm_ioremap()`, stores driver data, and registers a time-only RTC. Runtime reads hold the chip, read seconds/minutes/hours/day/week/month/year digit registers, map years 00-69 to 2000-2069 and 70-99 to 1970-1999, convert 12-hour PM/AM if needed, then unlock. Runtime writes hold the chip, write each digit register, preserve 12/24-hour mode semantics for the hour tens register, optionally write weekday, fold years >= 2000 to two digits, and unlock.

State and persistence: all time state lives in MSM6242 registers and persists according to board power. Driver state has no cache. No alarm or IRQ support is exposed despite control-register interrupt bits existing.

Dependencies and integration: platform-only driver named `rtc-msm6242`, no OF table, RTC class ops, raw MMIO, and legacy board resources.

Risks and test signals: `msm6242_lock()` warns but continues after BUSY timeout, so callers may read or write inconsistent values. `msm6242_set_time()` mutates `tm->tm_year` when folding to two digits. Raw 32-bit access assumes a specific bus layout where each 4-bit register occupies a word. Test HOLD/BUSY retry behavior, 12-hour midnight/noon/PM conversion, year windowing, weekday `-1` skip, resource size/alignment, and behavior when control register reads are unreliable.
