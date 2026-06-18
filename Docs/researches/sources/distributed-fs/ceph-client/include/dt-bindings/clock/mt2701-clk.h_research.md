<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt2701-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt2701-clk.h

Purpose: Provides MediaTek MT2701 DT clock IDs across top, PLL, DDRPHY, infrastructure, peripheral, audio, multimedia, image, video decode, high-speed interface, Ethernet, 3D, and BDP domains.

Important APIs, types, and functions: Defines `CLK_TOP_*`, `CLK_APMIXED_*`, `CLK_DDRPHY_*`, `CLK_INFRA_*`, `CLK_PERI_*`, `CLK_AUD_*`, `CLK_MM_*`, `CLK_IMG_*`, `CLK_VDEC_*`, `CLK_HIFSYS_*`, `CLK_ETHSYS_*`, `CLK_G3DSYS_*`, and `CLK_BDP_*` IDs. No functions or types are declared.

Control flow: No logic is present. The constants are used by MT2701 clock providers to resolve DT clock specifiers.

State and persistence: Numeric values are stable ABI and persist in DTBs. Runtime clock state is maintained by CCF and MediaTek drivers.

Dependencies and integration points: Used by MT2701 DTS, MediaTek clock drivers, and audio, display, image, codec, Ethernet, high-speed interface, and bus consumers.

Risks and test signals: Risks include older one-based top IDs, sentinel mismatch, and swapped media/audio clocks. Test with DT validation, clk registration counts, audio playback, display, Ethernet, high-speed I/O, image/video decode, and clock tree inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt2701-clk.h -->
