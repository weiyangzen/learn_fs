# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-out.h

Purpose: defines the metadata output payload and declares metadata output queue/format helpers.

Important APIs and types: `struct vivid_meta_out_buf` contains brightness, contrast, saturation, and hue values. Public declarations include `vivid_meta_out_process`, `vidioc_enum_fmt_meta_out`, `vidioc_g_fmt_meta_out`, `vidioc_s_fmt_meta_out`, and `vivid_meta_out_qops`.

Control flow: userspace writes buffers matching `struct vivid_meta_out_buf`; the output kthread processes them and updates controls.

State and persistence: no header-owned state. The payload values become persistent V4L2 control values when processed.

Dependencies and integration points: depends on Vivid core buffer/device types and V4L2/vb2 types from including code.

Risks: declares `vidioc_s_fmt_meta_out`, but the corresponding source file in this subset does not define it, so either another file must provide it or the declaration is stale.

Test signals: compile/link coverage and metadata output format ioctl coverage validate this boundary.
