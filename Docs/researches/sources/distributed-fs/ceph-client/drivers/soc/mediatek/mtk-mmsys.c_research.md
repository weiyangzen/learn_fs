# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-mmsys.c

## Purpose
This is the core MediaTek MMSYS platform driver. It binds SoC-specific route tables and reset data, exports helpers for display/video path configuration, registers an optional reset controller, creates child clock and DRM platform devices, and supports optional CMDQ register writes.

## Important APIs, Types, and Functions
Exported APIs include `mtk_mmsys_ddp_connect()`, `mtk_mmsys_ddp_disconnect()`, `mtk_mmsys_merge_async_config()`, `mtk_mmsys_hdr_config()`, `mtk_mmsys_mixer_in_config()`, `mtk_mmsys_mixer_in_channel_swap()`, `mtk_mmsys_ddp_dpi_fmt_config()`, `mtk_mmsys_vpp_rsz_merge_config()`, and `mtk_mmsys_vpp_rsz_dcm_config()`. Local core data is `struct mtk_mmsys`, containing register base, driver data, child platform devices, reset controller, spinlock, and CMDQ base.

## Control Flow and State
Probe allocates state, maps MMIO, picks match data, registers resets when available, reads optional GCE client register metadata, registers a clock platform device, and registers `mediatek-drm` unless the instance is VPPSYS. Route connect/disconnect iterates SoC route arrays and writes matching masks. Reset operations assert by clearing bits and deassert by setting bits under a spinlock; reset pulses sleep for about 1 ms. Remove unregisters child devices.

## Dependencies and Integration Points
The driver integrates with device tree compatibles for many MediaTek MMSYS/VDOSYS/VPPSYS instances, reset framework, platform device model, DRM display drivers, MediaTek clock drivers, and CMDQ helpers. SoC-specific headers provide route/reset constants.

## Risks and Test Signals
Risks include child device lifetime ordering, optional CMDQ fallback behavior, reset table translation errors, route table omissions, and `platform_device_unregister(NULL)` assumptions for VPPSYS instances. Test signals include DRM probe, clock child probe, display route switching, reset controller consumers, CMDQ and CPU write paths, and suspend/resume display recovery.
