<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8195-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8195-clk.h

Purpose: Provides the public DT clock-ID namespace for MediaTek MT8195 across top, infra, PLL, SCP/ADSP, peripheral, I2C wrapper, GPU, VPP/WPE, image, DIP, IPE, camera, video decode/encode, audio, impedance, MDP, and VDO domains.

Important APIs, types, and functions: Defines hundreds of `CLK_*` constants including `CLK_TOP_*`, `CLK_INFRA_AO_*`, `CLK_APMIXED_*`, `CLK_SCP_ADSP_*`, `CLK_PERI_AO_*`, `CLK_IMP_IIC_WRAP_*`, `CLK_MFG_*`, `CLK_VPP*`, `CLK_WPE*`, `CLK_IMG*`, `CLK_IPE_*`, `CLK_CAM*`, `CLK_VDEC*`, `CLK_VENC*`, `CLK_AUD_*`, `CLK_MDP_*`, `CLK_VDO0_*`, and `CLK_VDO1_*`. No functions or types.

Control flow: Declarative only. Provider drivers and DTBs must agree exactly on the numeric IDs.

State and persistence: Persistent DT ABI; runtime state belongs to CCF/provider drivers.

Dependencies and integration points: Used by MT8195 DTS and high-end media/display/camera/audio/GPU/peripheral consumers.

Risks and test signals: Risks include cross-domain swaps in very large tables, stale count constants, and display/video pipeline breakage. Test with DT validation, provider count checks, dual-display/VDO pipelines, camera, codecs, audio DSP, GPU, MDP/VPP/WPE, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8195-clk.h -->
