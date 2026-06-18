<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt2712-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt2712-clk.h

Purpose: Defines MT2712 Device Tree clock IDs for PLL, top clock, infrastructure, peripheral, MCU, GPU, display, image, BDP, VDEC, VENC, and JPEG decode domains.

Important APIs, types, and functions: Exports `CLK_APMIXED_*`, `CLK_TOP_*`, `CLK_INFRA_*`, `CLK_PERI_*`, `CLK_MCU_*`, `CLK_MFG_*`, `CLK_MM_*`, `CLK_IMG_*`, `CLK_BDP_*`, `CLK_VDEC_*`, `CLK_VENC_*`, and `CLK_JPGDEC_*` constants. There are no functions or structs.

Control flow: The file has no executable behavior. Driver probe paths register clock tables whose indexes must match these IDs.

State and persistence: Values are DT ABI and remain meaningful in compiled DTBs. Runtime enable/rate state is elsewhere.

Dependencies and integration points: Integrated with MT2712 DTS and MediaTek CCF providers for display, multimedia, codecs, JPEG, GPU, peripheral buses, and MCU clocks.

Risks and test signals: Risks are provider table ordering errors, missing `*_NR_CLK` updates, and media-domain miswiring. Test with `dtbs_check`, boot registration warnings, display output, JPEG decode, video encode/decode, image pipeline, GPU probe, and peripheral bus consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt2712-clk.h -->
