# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-cap.h

Purpose: defines the Vivid UVC metadata capture payload shape and declares metadata capture queue/format helpers.

Important APIs and types: `VIVID_META_CLOCK_UNIT` is the 100 MHz clock divisor used for PTS/SCR generation. `struct vivid_uvc_meta_buf` is a packed UVC-like metadata buffer with timestamp, SOF, length, flags, and a ten-byte PTS/STC/SOF payload. Public APIs are `vivid_meta_cap_fillbuff`, `vidioc_enum_fmt_meta_cap`, `vidioc_g_fmt_meta_cap`, and `vivid_meta_cap_qops`.

Control flow: queue setup and capture ticks in the `.c` file use this structure size as the meta buffer contract.

State and persistence: no persistent state in the header. It defines the binary ABI exposed through meta capture buffers.

Dependencies and integration points: consumers need V4L2/vb2 types and `struct vivid_dev`/`struct vivid_buffer` declarations from Vivid core headers.

Risks: because `struct vivid_uvc_meta_buf` is packed and exported as buffer contents, field layout changes are ABI-visible to tests.

Test signals: size/layout assertions through userspace metadata reads and format buffersize checks validate this header.
