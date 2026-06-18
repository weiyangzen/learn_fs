# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_timestamp_regs.h

## Purpose
`psoc_timestamp_regs.h` defines the generated register addresses for the Gaudi2 PSOC timestamp counter block, a memory-mapped timer used for device time reads and counter control.

## Important APIs, Types, And Functions
The file exports `mmPSOC_TIMESTAMP_CNTCR`, `CNTSR`, `CNTCVL`, `CNTCVU`, `CNTFID0`, and CoreSight-style peripheral/component ID registers `PIDR*` and `CIDR*`. There are no C functions or types.

## Control Flow
The header has no executable flow. Callers typically disable/enable the counter through `CNTCR`, read the 64-bit counter from `CNTCVU` and `CNTCVL`, inspect status with `CNTSR`, and use `CNTFID0` as the frequency register.

## State, Persistence, And Dependencies
State lives in the hardware counter and control registers, not in this header. The counter value persists and increments according to the timestamp clock while enabled. Correct 64-bit reads depend on caller ordering or retry logic around upper/lower register reads if rollover is possible.

## Integration Points
Cross-references in older HabanaLabs device code show device time assembled from `CNTCVU` and `CNTCVL`; Gaudi2 code can use the same generated register naming. The timestamp block supports profiling, synchronization, diagnostics, and firmware/host correlation.

## Risks
The main risks are non-atomic 64-bit counter reads, using the wrong base or offset when programming control registers, and assuming a frequency without reading or configuring `CNTFID0`. Reset or clock gating of the timestamp block can break time continuity.

## Test Signals
Tests should confirm monotonic device-time reads, stable upper/lower rollover behavior, expected frequency, counter disable/enable effects, and sane PID/CID values during hardware bring-up diagnostics.
