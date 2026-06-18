# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_params.c

Purpose: metadata-output parameter node for sun6i ISP configuration. It accepts `V4L2_META_FMT_SUN6I_ISP_PARAMS` buffers, writes module configuration into the ISP load table, manages pending parameter application synchronized to hardware PARAM_LOAD, and creates the immutable media link into the proc subdev params sink.

Important APIs/functions: `sun6i_isp_params_config_default` seeds Bayer and denoise defaults. Configuration helpers write optical black, auto-exposure defaults, Bayer offsets/gains, white balance defaults, BDNF coefficients, and module enable bits into the load table. `sun6i_isp_params_configure()` applies base config every stream start and default module config only once. State helpers queue one pending params buffer, configure modules from `vb2_plane_vaddr()`, mark it pending, and complete it on PARAM_LOAD with sequence `capture.sequence + 1`. Queue ops use vb2 vmalloc memory, prepare payload size, enqueue buffers, start/stop streaming, and trigger state update when capture is also streaming. Ioctl ops expose fixed meta format.

Control flow: userspace queues a params meta buffer; if params and capture are streaming, state update copies its config into the load table and sets PARAM_READY. When hardware emits PARAM_LOAD, the pending buffer is completed as done and tagged for the next frame. Proc stream start also calls `sun6i_isp_params_configure()` to ensure base/default parameters are present before enabling frontend.

State and persistence: `sun6i_isp_params_state` holds queue, pending buffer, `configured` flag, and streaming flag. The load table persists active/pending module register values across frames.

Dependencies/integration: uses V4L2 meta-output ioctls, vb2-vmalloc, media controller, proc media pad, capture sequence, core state lock/update, register macros, and UAPI `sun6i-isp-config.h`.

Risks: user-provided params are read directly from a vmalloc buffer as `struct sun6i_isp_params_config`; validation of module masks and coefficient ranges is minimal in this file. `sun6i_isp_params_configure_bdnf()` reads coefficient indices beyond the two initialized RB defaults and beyond three initialized G defaults; zero-initialization makes defaults safe but userspace can supply all fields. S_FMT/TRY_FMT for meta output simply returns current fixed format, which is intentional but unusual. Default config applies only once per device state, not every stream restart.

Test signals: meta format enumeration, undersized buffer rejection, params queued before/after capture streaming, PARAM_LOAD completion sequence, module enable masks for Bayer/BDNF, invalid user config fuzzing, stop streaming cleanup, and default output without user params.
