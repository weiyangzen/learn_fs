
# sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-reg.h

## Purpose
This header defines TW68xx register offsets, interrupt bits, I2C/SBUS bits, decoder/scaler/control registers, RISC DMA instruction opcodes, video standard IDs, and pixel format encodings.

## Important APIs, Types, And Functions
It is macro-only. Important groups include DMA/interrupt registers (`TW68_DMAC`, `TW68_DMAP_SA`, `TW68_INTSTAT`, `TW68_INTMASK`), video decoder/scaler registers (`TW68_INFORM`, `TW68_OPFORM`, `TW68_CROP_HI`, `TW68_VDELAY_LO`, `TW68_HACTIVE_LO`, `TW68_*SCALE*`), controls (`TW68_BRIGHT`, `TW68_CONTRAST`, `TW68_SAT_U`, `TW68_HUE`), RISC opcodes (`RISC_SYNCO`, `RISC_SYNCE`, `RISC_JUMP`, `RISC_LINESTART`, `RISC_INLINE`), video standards, and `ColorFormat*` encodings.

## Control Flow
The header has no executable flow. Its constants are consumed by `tw68-core.c`, `tw68-video.c`, and `tw68-risc.c` to program reset defaults, construct DMA programs, configure scaling/cropping, handle interrupts, and map V4L2 formats to hardware output formats.

## State And Persistence
The header describes hardware state locations. Writes through these constants persist in device registers until reset or reprogramming.

## Dependencies And Integration Points
It is included by `tw68.h`, making the register map available through the driver's common MMIO helper macros. The RISC instruction constants are shared with the buffer-program generator and queue chaining logic.

## Risks
The direct register space mixes byte and long accesses; using the wrong helper can target wrong byte lanes. RISC instruction bit fields are encoded manually, so changes require matching `tw68-risc.c`. Interrupt bit definitions are used in masks that differ by chip generation.

## Test Signals
Validation is indirect through successful register initialization, correct V4L2 control effects, stable DMA interrupts, and readable debug register dumps. Format tests should verify all `ColorFormat*` mappings produce expected byte order.
