<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-adsp_audio26m.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-adsp_audio26m.c

Purpose: This file registers the MT8188 ADSP audio 26 MHz gate provider.

Important APIs, types, and functions: `adsp_audio26m_cg_regs` describes the gate register; `GATE_ADSP_FLAGS` creates `adsp_audio26m_clks`; `adsp_audio26m_desc` is matched by `mediatek,mt8188-adsp-audio26m`; lifecycle uses `mtk_clk_simple_probe/remove`.

Control flow: Probe registers the ADSP audio 26 MHz gate and exposes it to ADSP/audio consumers through OF.

State and persistence behavior: Gate state is volatile hardware register state. Provider state is runtime-only.

Dependencies and integration points: It depends on MT8188 clock bindings, MediaTek gate helpers, a `clk26m` parent, and ADSP/audio firmware or driver consumers.

Risks and edge cases: This is a small reference-clock provider; disabling it at the wrong time can stall ADSP audio firmware. Gate polarity and parent naming are the main correctness risks.

Test signals: ADSP audio probe/firmware boot, audio playback through ADSP path, clk summary gate state, suspend/resume, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-adsp_audio26m.c -->
