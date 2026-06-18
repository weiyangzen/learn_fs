# sources/distributed-fs/ceph-client/include/uapi/linux/omap3isp.h

Purpose: Defines the private V4L2 userspace ABI for TI OMAP3 ISP configuration, statistics delivery, and image-processing block tuning.

Important APIs/types/functions: Exports private ioctls `VIDIOC_OMAP3ISP_CCDC_CFG`, `VIDIOC_OMAP3ISP_PRV_CFG`, `VIDIOC_OMAP3ISP_AEWB_CFG`, `VIDIOC_OMAP3ISP_HIST_CFG`, `VIDIOC_OMAP3ISP_AF_CFG`, `VIDIOC_OMAP3ISP_STAT_REQ`, `VIDIOC_OMAP3ISP_STAT_REQ_TIME32`, and `VIDIOC_OMAP3ISP_STAT_EN`. Defines private V4L2 events for AEWB, AF, and histogram readiness. Major structs include `omap3isp_h3a_aewb_config`, `omap3isp_stat_data`, `omap3isp_hist_config`, `omap3isp_h3a_af_config`, `omap3isp_ccdc_update_config`, many nested CCDC/preview tuning structs, and `omap3isp_prev_update_config`.

Control flow: Userspace configures sensor pipeline blocks with private ioctls, enables statistics modules, waits for V4L2 events, then requests statistics buffers by frame/config counter. CCDC update flags select A-Law, low-pass, black clamp/compensation, faulty-pixel correction, culling, and lens shading. Preview update flags select luma, CFA, chroma suppression, white balance, color conversion, defect correction, noise filter, gamma, and dark-frame features.

State and persistence behavior: The header defines transient configuration snapshots and statistics buffer contracts. Persistent driver state includes hardware register configuration, buffer queues, frame numbers, config counters, and statistics readiness. Time32 and native timestamp layouts preserve compat behavior.

Dependencies and integration points: Depends on `<linux/types.h>` and `<linux/videodev2.h>`. Integrates with the OMAP3 ISP media driver, V4L2 subdev/media-controller pipelines, camera applications, and 32-bit compatibility ioctl handling.

Risks: Many structs contain `__user` pointers to secondary configuration tables, making copy-in validation and size/range checks critical. Hardware limits are encoded as constants and must match driver validation. ABI layout differs under `__KERNEL__` for timestamps and time32 compatibility, so padding and conversion bugs can break userspace.

Test signals: Run media-controller camera capture with AEWB/AF/hist events, verify all ioctl range checks, exercise compat 32-bit `STAT_REQ_TIME32`, pass invalid nested user pointers, validate buffer size maxima, and compare register programming against expected image output.
