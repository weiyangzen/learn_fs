# sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk-mmsys.h

Purpose: This MediaTek header defines multimedia system routing and configuration APIs for display/video pipelines.

Important APIs/types/functions: It forward-declares `enum mtk_ddp_comp_id`, defines DPI output format enum values, enumerates many DDP component IDs, and declares `mtk_mmsys_ddp_connect`, `mtk_mmsys_ddp_disconnect`, `mtk_mmsys_ddp_dpi_fmt_config`, merge async config, HDR config, mixer input alpha/channel configuration, VPP resize/merge config, and VPP resize DCM config.

Control flow: Display drivers connect DDP components for a pipeline, configure format/mixer/HDR/merge blocks, then disconnect routes during teardown or mode changes.

State and persistence: MMSYS route registers, mixer configuration, HDR parameters, and clock-gating/DCM state persist in the multimedia syscon until changed or reset.

Dependencies and integration: Uses `struct device`, DDP component IDs, and MediaTek DRM/video drivers. Often coordinated with CMDQ and mutex APIs.

Risks and test signals: Wrong routing can produce blank display or conflicting paths. Test every display pipeline route, format conversion, HDR/mixer settings, atomic enable/disable, and suspend/resume.
