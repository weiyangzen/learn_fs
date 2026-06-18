# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/reg.h

## Purpose
Central PowerPC special-purpose register and bitfield helper header for selftests.

## Important APIs, Types, and Functions
Defines SPR numbers for PMU, DEXCR/HDEXCR, DSCR, TM, AMR, PVR, BESCR, MSR/TEXASR bits, VSX instruction encodings, `mfspr`/`mtspr` style macros, and prototypes for register save/load assembly helpers.

## Control Flow
No standalone flow; macros compile to SPR reads/writes and raw instruction words in callers.

## State and Persistence
Callers may mutate hardware/thread SPR state through macros; the header itself is static definitions only.

## Dependencies and Integration Points
Included broadly by DEXCR, DSCR, PMU, math, and register tests. Works with `lib/reg.S` implementations.

## Risks and Test Signals
Risk is ABI/SPR number drift or unsafe privileged SPR access. Hardware feature checks and signal handling in tests mitigate some cases.
