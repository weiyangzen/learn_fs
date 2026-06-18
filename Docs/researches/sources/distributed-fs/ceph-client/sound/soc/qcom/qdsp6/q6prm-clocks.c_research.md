# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6prm-clocks.c

Purpose: registers a platform clock provider for AudioReach/Q6 PRM-managed LPASS clocks. It adapts static Qualcomm clock IDs and hardware-core votes into the generic `q6dsp_clock_dev_probe` infrastructure.

Important APIs and types: the `Q6PRM_CLK()` macro maps logical LPASS clock IDs to `Q6PRM_` DSP IDs with a default 19.2 MHz rate. `q6prm_clks[]` includes MI2S bit/external clocks, speaker OSR, WSA/VA/TX/RX macro clocks, and vote-only clocks for LPASS core and DCODEC hardware. `q6dsp_clk_q6prm` wires `.lpass_set_clk`, `.lpass_vote_clk`, and `.lpass_unvote_clk` to `q6prm_set_lpass_clock()`, `q6prm_vote_lpass_core_hw()`, and `q6prm_unvote_lpass_core_hw()`.

Control flow and state: probe is delegated directly to `q6dsp_clock_dev_probe`. Matching `qcom,q6prm-lpass-clocks` supplies the descriptor through OF match data. There is no mutable file-local state.

Dependencies and integration: depends on dt-bindings for Q6 DSP LPASS port/clock names, `q6dsp-lpass-clocks.h`, and the PRM command exports in `q6prm.c`. Child nodes are typically populated by the `q6prm` GPR driver.

Risks: the static table is the authoritative mapping from Linux clock IDs to DSP resource IDs. A wrong ID, missing macro clock, or bad vote clock causes audio paths to fail only when a specific board route starts. The default rate is a placeholder until clients set a rate.

Test signals: DT probe of `qcom,q6prm-lpass-clocks`, clk summary entries for all table rows, successful MI2S/SoundWire macro clock enables, and DSP PRM response status for set/vote/unvote operations.
