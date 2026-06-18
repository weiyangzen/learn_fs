# sources/distributed-fs/ceph-client/arch/m68k/mac/mac.h

## Purpose
Declares cross-file Macintosh platform entry points used by the m68k Mac board-support objects.

## APIs, Flow, And State
The header forward-declares `struct rtc_time` and prototypes `baboon_init()`, `iop_init()`, `mac_hwclk()`, `mac_mksound()`, `oss_init()`, `psc_init()`, `via_init()`, and `via_init_clock()`. It defines no state and contains no control flow.

## Dependencies And Integration
Included by the Mac implementation files so `config.c` can call hardware initializers and machdep hooks without exposing local definitions through broader architecture headers. It bridges board files for Baboon, IOP, RTC, sound, OSS, PSC, and VIA.

## Risks And Test Signals
The header is intentionally narrow; drift between prototypes and implementations would be caught at compile time. Its main design risk is hiding APIs that may need broader declaration if external drivers start calling them. Test signal is a clean m68k Mac build with no implicit declarations.
