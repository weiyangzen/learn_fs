# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_filmgrain.h

## Purpose
`rockchip_av1_filmgrain.h` declares the AV1 film grain block generation helpers used by Rockchip/Hantro AV1 decode support. It exposes the exact block dimensions and parameter contracts needed by the implementation and callers.

## Important APIs, Types, And Functions
The header declares `rockchip_av1_generate_luma_grain_block` for 73-by-82 luma grain blocks and `rockchip_av1_generate_chroma_grain_block` for 38-by-44 Cb/Cr grain blocks. Parameters include bit depth, point counts, grain scale shift, autoregressive lag and coefficients, coefficient shift, min/max clamps, chroma scaling mode, and random seed.

## Control Flow
There is no executable control flow in the header. Callers allocate correctly shaped grain arrays, pass parsed AV1 film grain parameters, call luma generation first when chroma may depend on luma, and then call chroma generation.

## State And Persistence
The header defines no storage. It declares pure generation-style routines that fill caller-owned buffers deterministically from frame parameters.

## Dependencies And Integration Points
It includes Linux integer types. AV1 hardware setup code and `rockchip_av1_filmgrain.c` share this interface. The array pointer dimensions are part of the compile-time safety contract between caller buffers and implementation loops.

## Risks
Because dimensions are encoded in function parameter types, any caller-side buffer mismatch becomes a compile-time issue, but changing those dimensions is an ABI-level driver change. The header does not document valid ranges for shifts, lags, or point counts, so validation must remain in the AV1 frame-parameter parsing path.

## Test Signals
Build coverage validates array type compatibility. Runtime AV1 film grain tests should verify deterministic output for known seeds and parameter combinations, especially chroma-from-luma cases.
