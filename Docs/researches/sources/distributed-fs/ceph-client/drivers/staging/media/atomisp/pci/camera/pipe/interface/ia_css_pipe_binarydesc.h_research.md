# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/interface/ia_css_pipe_binarydesc.h

Purpose: declares helpers that construct CSS binary descriptors for copy, preview, video, capture, viewfinder post-processing, scaler, and multi-stage ISP pipelines.

Important APIs/types/functions: exported descriptor builders include `ia_css_pipe_get_copy_binarydesc()`, `ia_css_pipe_get_vfpp_binarydesc()`, `ia_css_pipe_get_preview_binarydesc()`, `ia_css_pipe_get_video_binarydesc()`, `ia_css_pipe_get_yuvscaler_binarydesc()`, `ia_css_pipe_get_capturepp_binarydesc()`, `ia_css_pipe_get_primary_binarydesc()`, `ia_css_pipe_get_pre_gdc_binarydesc()`, `ia_css_pipe_get_gdc_binarydesc()`, `ia_css_pipe_get_post_gdc_binarydesc()`, `ia_css_pipe_get_pre_de_binarydesc()`, `ia_css_pipe_get_pre_anr_binarydesc()`, `ia_css_pipe_get_anr_binarydesc()`, `ia_css_pipe_get_post_anr_binarydesc()`, `ia_css_pipe_get_ldc_binarydesc()`, `sh_css_bds_factor_get_fract()`, and `binarydesc_calculate_bds_factor()`.

Control flow: callers pass a configured `ia_css_pipe` plus input/output/vf frame-info buffers. Implementations populate `ia_css_binary_descr` fields used by binary lookup and may modify frame-info structures.

State and persistence: no state is stored in the header. Implementations can update `pipe->required_bds_factor` as a side effect.

Dependencies and integration: depends on CSS pipe, frame, and binary descriptor types. It is a core interface between high-level pipe configuration and firmware binary selection.

Risks and test signals: output parameters are in/out and some may be nullable by convention, so callers must match each function's expectations. Tests should cover every pipe mode, raw/YUV input changes, BDS/fractional downscale combinations, and descriptor fields that control firmware binary lookup.
