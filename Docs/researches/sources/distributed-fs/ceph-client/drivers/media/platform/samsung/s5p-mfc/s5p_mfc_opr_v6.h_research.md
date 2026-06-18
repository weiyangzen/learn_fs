# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr_v6.h

Purpose: declares v6+ hardware operation/register initialization and defines shared v6+ sizing and encoder limit macros.

Important APIs and types: exports `s5p_mfc_init_hw_ops_v6` and `s5p_mfc_init_regs_v6_plus`. Defines macroblock and LCU dimension helpers, H.264/HEVC motion-vector buffer size formulas, encoder multi-slice, intra-refresh, VBV, loop-filter, frame-rate, profile/level, CBR, HEVC QP, and frame-delta limits.

Control flow: the v6+ operation implementation uses these macros when computing DPB, scratch, motion-estimation, and codec parameter limits. Generic initialization calls the exported functions to install the v6+ operation table and register pointer map.

State and persistence: no state is stored here. Macros influence runtime fields such as buffer sizes, QP ranges, and version-specific register programming.

Dependencies and integration points: includes common and operation headers, uses kernel `DIV_ROUND_UP`, and defines the v6+ backend boundary consumed by `s5p_mfc_opr.c`.

Risks: formulas and limit constants must stay aligned with firmware requirements. Changing them can silently affect memory allocation and V4L2 control range behavior. Some macros use broad integer expressions and depend on caller-provided dimensions being validated elsewhere.

Test signals: compile coverage; unit-style checks of buffer-size formulas if available; hardware stress at maximum resolutions and levels; and encode-control range tests for H.264 and HEVC.
