# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_wt.h

## Purpose
Defines register address macros and voice state for the AU88x0 wavetable engine.

## Important APIs, Types, And Functions
Macros include `NR_WT_PB`, `WT_BAR`, `WT_BANK`, bank registers `WT_CTRL`, `WT_SRAMP`, `WT_DSREG`, `WT_MRAMP`, `WT_GMODE`, `WT_ARAMP`, and voice registers `WT_STEREO`, `WT_MUTE`, `WT_RUN`, `WT_PARM`, and `WT_DELAY`. The parameter enum names `param0` through `delay`. `wt_voice_t` caches four WT parameter words.

## Control Flow
No executable flow. `au88x0_synth.c` uses these macros to calculate MMIO addresses for all WT initialization, routing, and register writes.

## State And Persistence
`wt_voice_t` state lives in `vortex_t`; register macros target volatile hardware state. No persistent storage exists.

## Dependencies And Integration Points
Consumed by WT/synth code and indirectly by PCM WT setup. It assumes `NR_WT` and Vortex MMIO access exist in the including environment.

## Risks
Address macros encode bank and voice layout through shifts and masks; mistakes would corrupt adjacent WT or FIFO registers. The header has no validation for voice range, leaving checks to callers such as `vortex_wt_SetReg()`.

## Test Signals
Compile coverage and successful WT init are the main signals. Runtime validation requires WT register writes to affect expected voices/banks and not interfere with ADB playback paths.
