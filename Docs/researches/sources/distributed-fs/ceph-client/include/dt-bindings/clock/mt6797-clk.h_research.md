<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6797-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6797-clk.h

Purpose: Provides clock IDs for the MediaTek MT6797 SoC across top muxes, PLLs, infrastructure, image, multimedia, video decode, and video encode domains.

Important APIs, types, and functions: Defines `CLK_TOP_MUX_*`, `CLK_APMIXED_*`, `CLK_INFRA_*`, `CLK_IMG_*`, `CLK_MM_*`, `CLK_VDEC_*`, and `CLK_VENC_*` constants. No structs, enums, or functions are declared.

Control flow: No executable flow exists. Clock providers use these IDs as DT ABI inputs to select CCF clock descriptors.

State and persistence: The definitions are stable DT ABI. Runtime enable/rate/parent state is kept by provider drivers.

Dependencies and integration points: Integrated with MT6797 DTS and drivers for UART/SPI/MSDC, USB, display, MDP, image, video codecs, GPU/MFG, camera timing, and infrastructure bus clocks.

Risks and test signals: Risks include top mux numbering starting at 1, domain-local ID reuse with the wrong provider phandle, and missing sentinel updates. Test with DT binding validation, boot-time clk registration, display and codec workloads, image path tests, USB/storage/serial probes, and clk debugfs comparisons to expected parents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6797-clk.h -->
