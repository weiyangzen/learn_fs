<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6765-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6765-clk.h

Purpose: Provides clock IDs for MediaTek MT6765, including fixed 26 MHz, PLL, top, infrastructure, audio, MIPI CSI analog, multimedia, image, video encode, and camera domains.

Important APIs, types, and functions: Defines `CLK_TOP_CLK26M`, `CLK_APMIXED_*`, `CLK_TOP_*`, `CLK_IFR_*`, `CLK_AUDIO_*`, `CLK_MIPI0A_*`, `CLK_MM_*`, `CLK_IMG_*`, `CLK_VENC_*`, and `CLK_CAM_*`. No functions or types are provided.

Control flow: No code executes. DT consumers use these integer IDs; clock providers map them to registered CCF clocks.

State and persistence: IDs are persistent DT ABI. Runtime state is in CCF/provider structures and hardware registers.

Dependencies and integration points: Used by MT6765 DTS files and consumers for UART/SPI/MSDC, audio, display, camera, image processing, MIPI CSI, and video encode.

Risks and test signals: Risks include overlapping local domains being passed to the wrong provider, top/fixed clock confusion, and camera CSI clock mismatches. Test with DT validation, clock provider registration, serial/storage probes, camera capture, display, audio, image processing, and video encode scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6765-clk.h -->
