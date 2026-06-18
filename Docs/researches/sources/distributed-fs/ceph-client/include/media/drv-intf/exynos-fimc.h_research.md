# sources/distributed-fs/ceph-client/include/media/drv-intf/exynos-fimc.h

Purpose: Shared Samsung S5P/Exynos FIMC camera/media-pipeline definitions for inputs, bus types, formats, group IDs, and media pipeline operations.

Important APIs/types/functions: Defines `enum fimc_input`, `enum fimc_bus_type`, input-class macros, subdevice group IDs, `fimc_source_info`, notification `S5P_FIMC_TX_END_NOTIFY`, `fimc_fmt`, `exynos_media_pipeline_ops`, `exynos_video_entity`, `exynos_media_pipeline`, `vdev_to_exynos_video_entity`, and `fimc_pipeline_call`.

Control flow: Media graph entities use group IDs and source info to configure input muxes and bus formats. Video nodes call pipeline ops for prepare/unprepare/open/close/set_stream, with `fimc_pipeline_call` returning `-ENOENT` or `-ENOIOCTLCMD` when the pipeline/op is absent.

State and persistence: Pipeline state is carried by `exynos_media_pipeline`, embedded `media_pipeline`, video entity pointers, and driver-owned format tables. No persistence beyond device lifetime.

Dependencies and integration: Depends on media entity, V4L2 device, and media bus definitions. It integrates camera sensors, CSI receivers, FIMC/FLITE, writeback paths, and video nodes.

Risks and test signals: Risks are wrong bus/mux classification, format-plane metadata mismatches, aliasing writeback enum values, and missing pipeline ops. Test all input types, pipeline stream sequencing, single-frame notification, format table selection, and absent-op error propagation.
