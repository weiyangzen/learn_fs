# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/skfbiinc.h

## Purpose
`skfbiinc.h` provides assembler-friendly and shared include definitions for the FBI hardware layer: interrupt masks, FORMAC physical register aliases, transfer modes, and default empty driver callback hooks.

## Important APIs, Types, And Functions
Important definitions are `ERR_FLAGS`, `IMASK_FAST`, `ISR_MASK`, `FMA_FM_*` aliases, transfer mode aliases (`TMODE_RRQ`, `TMODE_WAQ0`, `TMODE_WAQ2`, `TMODE_WSQ`), `HSRA`, and default `DRV_PCM_STATE_CHANGE()`/`DRV_RMT_INDICATION()` macros.

## Control Flow
`drvfbi.c` uses `ISR_MASK` during `card_start()` to initialize board interrupts. Optional platform code can override the driver callback macros to receive PCM/RMT notifications.

## State And Persistence
No state is declared. Interrupt mask constants are written into `smc->hw.is_imask` and hardware interrupt mask registers.

## Dependencies And Integration Points
It includes `supern_2.h` and uses `skfbi.h` address macros such as `FMA()`. It is included by board-dependent driver code and legacy assembly-oriented paths.

## Risks And Edge Cases
Mask definitions must include all fast interrupt sources required by timer, RTM, PLC, MAC, RX, and TX error handling. Missing a bit can silently suppress state-machine progress. Default empty callbacks can hide OS integration if an expected override is absent.

## Test Signals
Interrupt mask validation during init, callback override builds, assembler/include consumers, and ISR coverage for timer, token, PLC, MAC, RX parity/encoding, and TX encoding sources.
