# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_filmgrain.c

## Purpose
`rockchip_av1_filmgrain.c` implements AV1 film grain synthesis helpers for Rockchip/Hantro AV1 decode support. It generates deterministic luma and chroma grain blocks from the AV1 Gaussian sequence, pseudo-random LFSR state, autoregressive coefficients, bit depth, scaling shifts, and grain limits.

## Important APIs, Types, And Functions
The file contains the static `gaussian_sequence[2048]` table, helper functions `clamp`, `round_power_of_two`, `rockchip_av1_init_random_generator`, `rockchip_av1_update_random_register`, and `rockchip_av1_get_random_number`, plus exported generators `rockchip_av1_generate_luma_grain_block` and `rockchip_av1_generate_chroma_grain_block`.

## Control Flow
Luma generation initializes a random register from the frame seed, fills a 73-by-82 block with Gaussian samples when luma scaling points are present, then applies an autoregressive filter over the interior area using `ar_coeff_lag`, 24 luma coefficients, `ar_coeff_shift`, and min/max clamps. Chroma generation separately initializes random sequences for Cb and Cr, fills 38-by-44 chroma blocks when chroma points or luma-derived scaling are enabled, then applies chroma autoregressive filtering. If luma points exist, chroma filtering also averages the corresponding 2-by-2 luma grain samples and applies the final chroma coefficient.

## State And Persistence
The file has only read-only static Gaussian data. Generated grain blocks are caller-provided stack or context memory and are deterministic for the same seed and frame parameters. There is no cross-frame persistence inside this file.

## Dependencies And Integration Points
It includes `rockchip_av1_filmgrain.h` for prototypes and Linux integer types. AV1 decode hardware code calls these helpers when film grain parameters are enabled and then uses the generated blocks to program hardware or prepare grain synthesis state.

## Risks
Array dimensions and loop bounds are fixed to AV1 film grain block geometry; off-by-one changes can corrupt caller memory. `ar_coeff_lag` and coefficient array sizes must match the AV1 limits expected by callers. The helper `round_power_of_two` assumes positive shift counts in current use, so caller validation of bit depth and grain scale shift matters. Chroma luma-coordinate calculations depend on the luma block's 73-by-82 padding.

## Test Signals
Film grain conformance vectors with known seeds are the best signal. Tests should cover no-grain paths, luma-only, chroma-only, chroma-from-luma, different bit depths, multiple autoregressive lags, and clamp boundary behavior.
