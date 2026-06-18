# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_entropymode.h

## Purpose
`rockchip_av1_entropymode.h` defines the AV1 entropy-mode constants, enums, and CDF structures used by Rockchip/Hantro AV1 decode support. It is the layout contract between AV1 entropy default generation, AV1 hardware programming, and per-context reference CDF state.

## Important APIs, Types, And Functions
The header defines many AV1 dimension constants such as `AV1_INTRA_MODES`, `NUM_REF_FRAMES`, `TX_SIZES`, `TOKEN_CDF_Q_CTXS`, and `SIG_COEF_CONTEXTS`. Enums cover block sizes, filter intra modes, frame type, transform size, prediction mode, and partition type. `struct mvcdfs` contains motion-vector CDF groups. `struct av1cdfs` contains the full hardware-facing AV1 entropy state, including partition, mode, segment, reference, transform, palette, CFL, motion, eob, coefficient, and padding fields. Declared functions are `rockchip_av1_store_cdfs`, `rockchip_av1_get_cdfs`, `rockchip_av1_set_default_cdfs`, and `rockchip_av1_default_coeff_probs`.

## Control Flow
The header has no executable control flow. AV1 decode setup allocates or embeds `struct av1cdfs`/`struct mvcdfs`, initializes defaults through the declared functions, selects reference CDF state for each frame, then stores updated state into refreshed reference slots after decode.

## State And Persistence
The structures represent per-context, per-reference entropy state that persists across frames in a decode session. Padding fields are explicit because hardware layout and DMA/register programming expect stable offsets.

## Dependencies And Integration Points
It includes Linux integer types and forward-declares `struct hantro_ctx`. It is included by `rockchip_av1_entropymode.c` and AV1 decoder hardware code. The V4L2 AV1 frame controls and Hantro AV1 context structures depend on these constants matching AV1 specification dimensions and hardware expectations.

## Risks
This is a high-coupling layout header: changing constants, enum order, array dimensions, or padding affects table copies and hardware interpretation. Some enum aliases preserve AV1 naming relationships, so cleanup refactors can accidentally alter semantic values. The large `struct av1cdfs` would benefit from layout assertions against hardware documentation.

## Test Signals
Build coverage catches missing declarations, but functional coverage requires AV1 decode tests across prediction modes, transform sizes, palette/CFL/intrabc features, and reference refresh behavior. Size/layout checks would be useful additions.
