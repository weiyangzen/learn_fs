# sources/distributed-fs/ceph-client/arch/x86/include/asm/mach_traps.h

## Purpose
Defines default x86 machine-specific NMI reason handling and NMI reassertion support.

## Important APIs, Types, And Functions
Defines NMI reason port `0x61`, SERR/IOCHK reason and clear masks, `default_get_nmi_reason()`, and `reassert_nmi()`. It uses CMOS lock helpers from `mc146818rtc.h`.

## Control Flow
`default_get_nmi_reason()` reads port `0x61`. `reassert_nmi()` preserves or acquires the CMOS index lock, toggles RTC index registers `0x8f` and `0x0f` with dummy reads to reassert an NMI, then restores the previous CMOS index or unlocks.

## State And Persistence
Only transient port and CMOS index state is touched. The CMOS lock tracks ownership on 32-bit builds.

## Dependencies And Integration Points
Depends on RTC/CMOS accessors and x86 port I/O. It integrates with trap/NMI handling code that diagnoses system error and I/O check NMIs.

## Risks And Edge Cases
NMI context is fragile: CMOS lock ownership must be restored exactly. Port `0x70/0x71` access can race with RTC users if locking rules are broken. Hardware behavior is legacy-platform-specific.

## Test Signals
Build coverage plus NMI injection or hardware error tests that exercise unknown, SERR, and IOCHK NMI paths. Regression signals include lost CMOS index state or stuck NMI sources.
