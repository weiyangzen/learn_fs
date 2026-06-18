# sources/distributed-fs/ceph-client/include/media/v4l2-isp.h

Purpose: declares generic V4L2 ISP parameter/statistics validation helpers for extensible ISP parameter buffers.

Important APIs/types: `v4l2_isp_params_buffer_size(max_params_size)` computes the size of `struct v4l2_isp_params_buffer` plus a variable data payload. `v4l2_isp_params_validate_buffer_size()` validates a vb2 buffer size against a maximum and the minimum needed for at least one ISP configuration block. `struct v4l2_isp_params_block_type_info` stores expected size per block type. `v4l2_isp_params_validate_buffer()` validates copied parameter-buffer content against supported block type information.

Control flow: ISP drivers validate the vb2 buffer in `.buf_prepare()` or equivalent, copy userspace-provided content into kernel-only memory to avoid post-submit modification, then validate block layout/type/size using the per-type table before programming hardware.

State and persistence: no framework-owned persistent state. The driver owns the vb2 buffer, copied parameter buffer, max size, and type-info table.

Dependencies and integration: includes UAPI `linux/media/v4l2-isp.h` plus forward declarations for `device` and `vb2_buffer`. Integrates with videobuf2 parameter queues and ISP drivers consuming extensible block payloads.

Risks: using the payload before copying from userspace can race with modification; wrong `max_size` or type-size table can accept truncated or oversized blocks; block type indexes must match the UAPI enum; and integer overflow in caller-provided max sizes would affect buffer-size calculations if not bounded by implementation.

Test signals: validate minimum buffer size, max-size rejection, malformed block length, unknown block type, per-type expected-size mismatch, multiple blocks, zero blocks, and user-modification prevention by validating the kernel copy.
