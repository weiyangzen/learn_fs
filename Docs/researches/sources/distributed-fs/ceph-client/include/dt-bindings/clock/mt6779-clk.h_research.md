<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6779-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6779-clk.h

Purpose: Defines MediaTek MT6779 clock IDs for TOPCKGEN, APMIXED PLLs, camera, infrastructure, GPU, image, IPE, multimedia, video decode/encode, and audio domains.

Important APIs, types, and functions: Exports `CLK_TOP_*`, `CLK_APMIXED_*`, `CLK_CAM_*`, `CLK_INFRA_*`, `CLK_MFG_*`, `CLK_IMG_*`, `CLK_IPE_*`, `CLK_MM_*`, `CLK_VDEC_*`, `CLK_VENC_*`, and `CLK_AUD_*` constants. It declares no functions or data types.

Control flow: The header is declarative. Runtime control is in MT6779 clock drivers and CCF operations.

State and persistence: Numeric values persist in DT ABI. No runtime state exists in this file.

Dependencies and integration points: Used by MT6779 DTS and consumers for camera, display, audio, video codec, GPU, image/IPE accelerators, buses, UART/SPI/MSDC, and SCP/SSPM-related clocks.

Risks and test signals: Risks include one-based TOP IDs, large INFRA domain ordering errors, and multimedia subsystem clock swaps. Test with `dtbs_check`, clk registration count checks, display and camera bring-up, audio paths, video encode/decode, GPU probe, and suspend/resume clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6779-clk.h -->
