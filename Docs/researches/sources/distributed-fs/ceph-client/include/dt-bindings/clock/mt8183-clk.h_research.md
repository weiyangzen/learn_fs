<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8183-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8183-clk.h

Purpose: Defines MediaTek MT8183 clock IDs across APMIXED PLLs, TOPCKGEN muxes, camera, infrastructure, peripheral, GPU, image, multimedia, video, audio, IPU, and MCU domains.

Important APIs, types, and functions: Exports `CLK_APMIXED_*`, `CLK_TOP_MUX_*`, `CLK_CAM_*`, `CLK_INFRA_*`, `CLK_PERI_*`, `CLK_MFG_*`, `CLK_IMG_*`, `CLK_MM_*`, `CLK_VDEC_*`, `CLK_VENC_*`, `CLK_AUDIO_*`, `CLK_IPU_*`, and `CLK_MCU_*`. No functions or structs exist.

Control flow: No runtime behavior. Provider drivers map these IDs to CCF clocks used by DT consumers.

State and persistence: IDs are DT ABI. Runtime parent/rate/enable state is external.

Dependencies and integration points: Used by MT8183 DTS, MediaTek CCF providers, and consumers for Chromebook-class display, camera, IPU, audio, video, GPU, I2C/SPI/UART, storage, and SCP/MCU clocks.

Risks and test signals: Risks include IPU domain mismatches, large infra table ordering errors, and top mux ID drift. Test with `dtbs_check`, boot logs, display, camera, IPU, audio, video codecs, GPU probe, and peripheral suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8183-clk.h -->
