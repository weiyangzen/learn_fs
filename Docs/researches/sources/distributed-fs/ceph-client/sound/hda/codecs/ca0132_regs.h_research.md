# sources/distributed-fs/ceph-client/sound/hda/codecs/ca0132_regs.h

## Purpose

This header is the register-map and address helper layer for Creative CA0132 DSP memory, DSP DMA, and debug/control blocks. It does not execute code by itself; it gives the CA0132 codec driver symbolic names for X/Y/auxiliary RAM spaces, microcontroller memory, DMA channel registers, bit fields, valid memory ranges, and logical offsets.

## Important APIs, types, and functions

The file exports only preprocessor definitions. Important groups are `DSP_DBGCNTL_*` for debug-control fields, `XRAM_*`, `YRAM_*`, `UC_*`, `AXRAM_*`, and `AYRAM_*` for memory-space sizes and instance offsets, and `DSPDMAC_*` for per-channel DMA config, DSP address offsets, transfer counts, interrupt counts, audio channel selection, channel start/status/property, and active status. The functional macros include `*_INST_OFFSET(chan)`, `X_RANGE_*`, `Y_RANGE_*`, `UC_RANGE`, `X_OFF`, `Y_OFF`, `AX_OFF`, `AY_OFF`, and split-size helpers for transfers crossing main/aux memory boundaries.

## Control flow

There is no runtime control flow. The macros are expanded by CA0132 code that validates memory addresses, chooses address spaces, composes coefficient/register addresses, and programs DSP DMA transactions. The range macros use start address plus `(size - 1) * increment` tests to decide whether an operation fits into main memory, auxiliary memory, extended memory, or all valid memory.

## State and persistence behavior

The header stores no state. Persistence is entirely in the hardware registers and DSP memory addressed by these constants. Because many macros map logical indices to physical chip offsets, wrong values can persist as corrupted DSP memory or stalled DMA state in the codec until reset/reinitialization.

## Dependencies and integration points

It is included by the CA0132 HDA codec implementation. Its constants integrate with HDA verb/coefficient accessors and CA0132 firmware/DSP loader code that needs stable hardware offsets. It depends only on C preprocessor arithmetic and unsigned integer semantics.

## Risks and test signals

Risks are off-by-one range validation, integer overflow in `(a) + ((s)-1) * incr`, address-space confusion between main and auxiliary RAM, channel index overflow beyond the 12 DMA channels, and field masks drifting from hardware documentation. Test signals include CA0132 firmware load success, DSP DMA read/write round trips across X/Y/UC and aux boundaries, invalid-address rejection, suspend/resume with DSP reinitialization, and audio-path tests that exercise DSP effects and microphone processing.
