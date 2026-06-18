# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_vp9.h

## Purpose
`hantro_vp9.h` defines the hardware memory layouts used by the Hantro G2 VP9 decoder for probabilities and symbol counts. It is consumed by VP9 context initialization and register/probability programming paths that exchange probability tables and count tables with the hardware.

## Important APIs, Types, And Functions
`struct hantro_g2_mv_probs` models motion-vector probability storage. `struct hantro_g2_probs` contains inter/intra mode, transform, partition, interpolation, reference, skip, MV, and coefficient probability arrays. `struct hantro_g2_all_probs` wraps keyframe-specific probability tables plus `hantro_g2_probs`. `struct mv_counts` and `struct symbol_counts` define the hardware-written count tables for probability adaptation.

## Control Flow
The header contains no executable code. `hantro_vp9_dec_init` uses `sizeof(struct hantro_g2_all_probs)` and `sizeof(struct symbol_counts)` to size the misc DMA area, then pointer-maps fields in `struct symbol_counts` into the V4L2 VP9 count abstraction. G2 VP9 run/done paths use the same structures when programming and reading hardware probability/count state.

## State And Persistence
These structures describe in-memory coherent DMA contents, not persistent storage. Their binary layout is effectively an ABI between the driver and hardware, so field order, padding, and dimensions are part of the state contract.

## Dependencies And Integration Points
The header relies on fixed-width integer types being available from includers. It is included by `hantro_vp9.c` and G2 VP9 hardware code. It bridges Hantro hardware memory format with V4L2 stateless VP9 probability/count update logic.

## Risks
Changing dimensions, field order, or implicit padding can silently corrupt hardware programming. The count arrays for different transform sizes must remain synchronized with `init_v4l2_vp9_count_tbl` and any VP9 library expectations. There are no compile-time layout assertions in this header.

## Test Signals
Build coverage catches type visibility issues, but functional signals require VP9 decode tests with adaptive entropy updates, motion-vector-heavy inter frames, and coefficient count readback validation.
