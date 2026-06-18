# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_entropymode.c

## Purpose
`rockchip_av1_entropymode.c` supplies Rockchip/Hantro AV1 default entropy CDF tables and helper functions for initializing, selecting, and storing AV1 CDF state. Most of the file is static default probability data derived from AOM AV1 tables; the executable surface copies those defaults into hardware-facing CDF structures and manages per-reference-frame CDF snapshots.

## Important APIs, Types, And Functions
The file defines `AOM_CDF*` conversion macros around `ICDF`, many `static const u16` default CDF arrays for AV1 intra/inter modes, transforms, palette, skip, references, motion vectors, coefficient bases, eob flags, and quantizer-context coefficient probabilities. `rockchip_av1_get_q_ctx` maps base quantizer values to one of four coefficient table contexts. Exported functions are `rockchip_av1_default_coeff_probs`, `rockchip_av1_set_default_cdfs`, `rockchip_av1_get_cdfs`, and `rockchip_av1_store_cdfs`.

## Control Flow
Default initialization begins with callers providing `struct av1cdfs` and non-DV motion-vector CDF storage. `rockchip_av1_set_default_cdfs` bulk-copies every non-quantizer-selected default table into the target structures, including regular MV CDFs and intrabc/non-DV MV CDFs. `rockchip_av1_default_coeff_probs` chooses a quantizer context using thresholds 20, 60, and 120, then copies coefficient, txb-skip, eob, dc-sign, and br/base tables for that context. During decode, `rockchip_av1_get_cdfs` points the active AV1 context at a reference frame's saved CDFs. After decode, `rockchip_av1_store_cdfs` copies the active CDFs into every reference slot selected by `refresh_frame_flags`, skipping self-copy when the active pointer already targets that slot.

## State And Persistence
Static default tables are read-only kernel data. Runtime CDF state lives in `ctx->av1_dec`: active CDF pointers, arrays of last CDFs per reference frame, and non-DV motion-vector CDF snapshots. This state persists only across frames within an open decode context and models AV1 reference-frame entropy adaptation.

## Dependencies And Integration Points
The file includes `hantro.h` and `rockchip_av1_entropymode.h`. It depends on the header's AV1 constants and `struct av1cdfs`/`struct mvcdfs` layout. AV1 hardware setup code calls these helpers while preparing default state for sequence/frame parameters and while updating reference slots according to V4L2 AV1 frame controls.

## Risks
The dominant risk is layout drift: every `memcpy` assumes source table dimensions exactly match destination fields in `struct av1cdfs` and `struct mvcdfs`. CDF table values are specification-derived and hard to review manually; accidental edits can create subtle decode mismatches. Quantizer thresholds in `rockchip_av1_get_q_ctx` must stay aligned with the table grouping. `refresh_frame_flags` is trusted as an 8-bit reference mask; incorrect flag handling can poison future reference-frame entropy state.

## Test Signals
AV1 conformance streams should cover keyframes, inter frames, reference refresh combinations, intrabc, palette, transform/eob variants, and multiple quantizer ranges. Differential decode against software AV1 output is the strongest signal. Static checks comparing table sizes against destination fields would reduce risk but are not present here.
