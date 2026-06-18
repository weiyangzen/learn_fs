# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_regs.h

## Purpose
Defines G1 decoder and postprocessor register offsets and bitfield macros.

## Important APIs, Types, And Functions
The header is declarative. It provides `G1_SWREG`, interrupt/config/control register offsets, bitfield construction macros for H.264/MPEG2/VP8/JPEG-era decode features, reference address registers, qtable and motion-vector bases, soft reset, and G1 postprocessor register definitions.

## Control Flow And State
No runtime state lives here. The macros encode the contract between codec runners and hardware registers. Several register fields are reused by different codecs, so the same register offsets carry codec-specific meanings.

## Dependencies And Integration Points
Used by `hantro_g1.c`, G1 H.264/MPEG2/VP8 runners, and G1 postprocessor code. The macros assume Linux `BIT`, `GENMASK`, and standard integer types are available through includers.

## Risks And Test Signals
Because masks and shifts are hand-coded, a single off-by-one can silently corrupt decode. The reused fields increase maintenance risk when adding codecs or variants. Useful signals are hardware conformance suites per codec, register trace comparison against vendor BSPs, and build coverage for every includer using overlapping macro names.
