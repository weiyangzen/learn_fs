# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/io.c

## Purpose
Provides 16-bit top-register read/write helpers on top of wlcore 32-bit register access for WiLink 8 PRCM/top-register programming.

## Important APIs, types, and functions
- `wl18xx_top_reg_write()` validates 2-byte alignment, reads the containing 32-bit word, replaces the lower or upper halfword, and writes it back.
- `wl18xx_top_reg_read()` validates 2-byte alignment, reads the containing 32-bit word, and extracts the lower or upper halfword.

## Control flow
The helpers branch on `addr % 4`: 32-bit-aligned addresses use the low halfword; 2-byte-offset addresses access the previous word and use the high halfword. Odd addresses trigger `WARN_ON()` and `-EINVAL`.

## State and persistence behavior
No host persistent state. Successful writes mutate hardware top registers; reads populate the caller-provided output pointer when non-NULL.

## Dependencies and integration points
Depends on `wlcore_read32()` and `wlcore_write32()` after the caller has selected the correct partition. Used by wl18xx clock and interrupt polarity setup in `main.c`.

## Risks and test signals
Read-modify-write can clobber adjacent halfwords if concurrent access is not serialized by higher-level locking. Wrong partition selection by callers accesses the wrong register bank. Test signals include successful clock setup, IRQ inversion setup for low/falling IRQs, and warnings on invalid odd addresses in fault injection.
