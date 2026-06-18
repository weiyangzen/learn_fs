<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8192-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8192-clk.h

Purpose: Defines MediaTek MT8192 clock IDs for top, infrastructure, peripheral, PLL, SCP/ADSP, audio, I2C wrappers, MSDC, GPU, multimedia, image, camera, video, IPE, display pipe, and MDP domains.

Important APIs, types, and functions: Exports `CLK_TOP_*`, `CLK_INFRA_*`, `CLK_PERI_*`, `CLK_APMIXED_*`, `CLK_SCP_ADSP_*`, `CLK_AUD_*`, `CLK_IMP_IIC_WRAP_*`, `CLK_MSDC*`, `CLK_MFG_*`, `CLK_MM_*`, `CLK_IMG*`, `CLK_CAM_*`, `CLK_VDEC_*`, `CLK_VENC_*`, `CLK_IPE_*`, `CLK_DPE_*`, and `CLK_MDP_*`. No functions or types.

Control flow: No logic is present. DT specifiers feed provider lookup tables indexed by these IDs.

State and persistence: IDs are binding ABI; runtime state is external.

Dependencies and integration points: Used by MT8192 DTS and consumers for display, camera, MDP, image/IPE/DPE, audio DSP, SCP/ADSP, codecs, GPU, storage, and buses.

Risks and test signals: Risks include large-table ordering mistakes and split image/camera domain mismatch. Test with DT schema checks, clk registration, display/camera/media workloads, ADSP/SCP/audio boot, GPU probe, storage, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8192-clk.h -->
