<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8186-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8186-clk.h

Purpose: Provides MT8186 Device Tree clock IDs for MCU, top, infrastructure, PLL, I2C wrapper, GPU, multimedia, WPE, image, video, camera, camera raw, and IPE domains.

Important APIs, types, and functions: Defines `CLK_MCU_*`, `CLK_TOP_*`, `CLK_INFRA_AO_*`, `CLK_APMIXED_*`, `CLK_IMP_IIC_WRAP_*`, `CLK_MFG_*`, `CLK_MM_*`, `CLK_WPE_*`, `CLK_IMG*`, `CLK_VDEC_*`, `CLK_VENC_*`, `CLK_CAM*`, and `CLK_IPE_*` constants. No functions or structs are present.

Control flow: Declarative only. Clock providers use the IDs when resolving DT phandle arguments.

State and persistence: Values are stable DT ABI; runtime clock state is maintained elsewhere.

Dependencies and integration points: Used by MT8186 DTS and consumers for display, camera/raw pipelines, WPE, image/IPE, video codecs, GPU, I2C, storage, serial, and infrastructure clocks.

Risks and test signals: Risks include camera raw domain confusion, I2C wrapper instance mismatches, and sentinel drift. Test with DT validation, clk provider counts, display, camera/raw capture, WPE/image processing, video encode/decode, GPU, and I2C bus enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8186-clk.h -->
