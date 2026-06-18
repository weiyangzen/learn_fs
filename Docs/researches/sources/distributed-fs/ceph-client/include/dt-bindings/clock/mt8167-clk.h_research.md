<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8167-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8167-clk.h

Purpose: Extends the MT8516 clock ID namespace for MT8167-specific PLL, top, GPU, multimedia, image, and video decode clocks.

Important APIs, types, and functions: Includes `<dt-bindings/clock/mt8516-clk.h>` and defines MT8167 additions such as `CLK_APMIXED_TVDPLL`, `CLK_APMIXED_LVDSPLL`, `MT8167_CLK_APMIXED_NR_CLK`, extra `CLK_TOP_*` display/video clocks, `CLK_MFG_*`, `CLK_MM_*`, `CLK_IMG_*`, and `CLK_VDEC_*`. No functions or structs exist.

Control flow: No code executes. IDs are computed by offsetting the inherited MT8516 sentinels, so provider drivers must share the same base namespace.

State and persistence: Constants are DT ABI. Runtime clock state is in MT8167/MT8516 provider drivers.

Dependencies and integration points: Tightly coupled to `mt8516-clk.h`, MT8167 DTS, and consumers for HDMI/LVDS/DSI/DPI, MFG/GPU, display, image, and VDEC.

Risks and test signals: Risks include inherited sentinel drift and broken ABI if MT8516 IDs change. Test by building both MT8516 and MT8167 DTBs, verifying provider counts, and exercising display outputs, GPU, image, VDEC, and inherited peripheral clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8167-clk.h -->
