<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt8365-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt8365-clk.h

Purpose: Supplies DT clock IDs for the MediaTek MT8365 SoC across top, infrastructure, peripheral, PLL, multimedia, camera, audio, MIPI CSI, MCU, MFG, VDEC, and APU domains.

Important APIs, types, and functions: Defines `CLK_TOP_*`, `CLK_IFR_*`, `CLK_PERI_*`, `CLK_APMIXED_*`, `CLK_GCE_*`, `CLK_AUD_*`, `CLK_MIPI_CSI*`, `CLK_MCU_*`, `CLK_MFG_*`, `CLK_MM_*`, `CLK_VDEC_*`, and `CLK_APU_*` constants. No callable APIs exist.

Control flow: No logic runs in this file. Its IDs are consumed as integer cells in DT `clocks` properties and resolved by MT8365 clock provider drivers.

State and persistence: Constant values are persistent DT ABI. Runtime enable, prepare, and rate state is stored by the common clock framework and provider drivers, not by the header.

Dependencies and integration points: Integrated with MT8365 DTS, MediaTek common clock infrastructure, and consumers for display, GPU, camera, audio, video decode, DMA/GCE, and APU hardware.

Risks and test signals: Risks include mixing similarly named MIPI CSI instances, APU/MFG clock mismatches, and incorrect `*_NR_CLK` limits. Test by validating DTBs, checking clk registration logs, and exercising display, CSI camera, audio playback/capture, GPU, video decode, and APU/accelerator probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt8365-clk.h -->
