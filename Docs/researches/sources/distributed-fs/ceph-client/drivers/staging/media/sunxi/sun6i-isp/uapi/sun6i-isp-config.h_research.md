# sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/uapi/sun6i-isp-config.h

## Purpose
Defines the userspace-visible metadata format and configuration payload for Allwinner A31 ISP parameter buffers.

## Important APIs, Types, And Functions
`V4L2_META_FMT_SUN6I_ISP_PARAMS` identifies parameter metadata buffers with fourcc `S6IP`. `SUN6I_ISP_MODULE_BAYER` and `SUN6I_ISP_MODULE_BDNF` are `modules_used` bits. `struct sun6i_isp_params_config_bayer` carries per-channel black offsets and gains for R/Gr/Gb/B. `struct sun6i_isp_params_config_bdnf` carries denoise distance thresholds and green/RB coefficient arrays. `struct sun6i_isp_params_config` combines module selection with both configuration blocks.

## Control Flow
Userspace queues metadata buffers of this format; the params video node validates and copies the structures, then kernel code applies selected blocks to ISP registers during parameter update points.

## State And Persistence
This is a stable uAPI contract. Values persist only as queued/applied buffer contents and active driver parameter state; there is no file-backed persistence.

## Dependencies And Integration Points
Depends on Linux fixed-width uAPI types and V4L2 fourcc definitions. Integrates with the sun6i params queue and the register definitions for Bayer and BDNF fields.

## Risks And Test Signals
Any layout change would break userspace ABI. Risks include missing range validation for coefficients/gains and userspace/kernel disagreement about `modules_used`. Test signals include `VIDIOC_ENUM_FMT` on the metadata node, queueing exact-size parameter buffers, applying only selected modules, and ABI-size checks across 32/64-bit userspace.
