<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8173-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8173-clk.h

Purpose: Provides MT8173 clock IDs for top clocks, PLLs, infrastructure, peripheral, image, multimedia/display, video decode, video encode, and VENCLT domains.

Important APIs, types, and functions: Defines `CLK_TOP_*`, `CLK_APMIXED_*`, `CLK_INFRA_*`, `CLK_PERI_*`, `CLK_IMG_*`, `CLK_MM_*`, `CLK_VDEC_*`, `CLK_VENC_*`, and `CLK_VENCLT_*`. There are no functions or types.

Control flow: The header is declarative. Clock controller drivers use these numeric IDs during DT clock resolution.

State and persistence: The constants are stable DT ABI and carry no runtime state.

Dependencies and integration points: Used by MT8173 DTS and consumers for display/HDMI, multimedia, image, video codecs, USB, storage, serial, I2C/SPI, PWM, and infrastructure buses.

Risks and test signals: Risks include sparse top numbering, provider array holes, and codec/display ID swaps. Test with DT binding validation, clk provider warnings, HDMI/display output, video encode/decode, image pipeline, storage/USB/serial probes, and suspend/resume clock gating checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8173-clk.h -->
