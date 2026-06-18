# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6prm.h

Purpose: exposes the PRM LPASS clock/core ID namespace and the small exported PRM control API used by Qualcomm QDSP6 clock providers and machine/backend drivers.

Important definitions: the file maps MI2S clocks (`PRI`, `SEC`, `TER`, `QUAD`, `QUI`, `SEN`, `INT0` through `INT6`), speaker OSR, WSA/VA/TX/RX macro MCLK and NPL/2X clocks, and newer WSA2/RX-core TX IDs to numeric DSP resource IDs. It also defines `Q6PRM_LPASS_CLK_SRC_INTERNAL`, `Q6PRM_LPASS_CLK_ROOT_DEFAULT`, `Q6PRM_HW_CORE_ID_LPASS`, and `Q6PRM_HW_CORE_ID_DCODEC`.

Important APIs: `q6prm_set_lpass_clock()` requests or releases a clock depending on whether `freq` is non-zero. `q6prm_vote_lpass_core_hw()` and `q6prm_unvote_lpass_core_hw()` vote/unvote PRM hardware cores.

Control flow and state: no code or state lives here. The header is a compile-time contract between `q6prm.c`, the PRM clock provider, and clients that need stable IDs.

Dependencies and integration: requires `struct device` and `uint32_t` from Linux headers through includers. The numeric values must align with Qualcomm DSP firmware and dt-binding expectations.

Risks: typo-level mismatches are high impact because these IDs are sent directly to firmware. The exported API includes `client_name` and `client_handle` parameters for vote compatibility, but the current implementation ignores them, which may surprise callers expecting handle tracking.

Test signals: compile users with no duplicate/missing IDs, exercise every listed clock through `clk_prepare_enable()`/`clk_set_rate()`, and verify DSP-side PRM responses on representative boards.
