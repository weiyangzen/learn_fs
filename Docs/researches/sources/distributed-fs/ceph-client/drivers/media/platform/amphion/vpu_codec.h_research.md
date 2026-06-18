<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_codec.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_codec.h

Purpose: defines codec parameter payloads shared between V4L2-facing code and firmware-specific iface implementations.

Important types: `struct vpu_encode_params` carries input/output formats, profile/level/tier, frame rate, source stride and dimensions, crop, output dimensions, GOP/B-frame settings, rate-control fields, QP limits, SAR, and colorimetry. `struct vpu_decode_params` carries codec/output formats, display-delay controls, non-frame mode, frame count, end flag, and userdata buffer address/size.

Control/state behavior: encoder and decoder private state owns these structs and mutates them from V4L2 controls/format ioctls. Firmware iface implementations serialize them into Windsor/Malone shared memory and update fields such as decoder `end_flag`.

Dependencies and integration: requires V4L2 fraction and rectangle types. Included indirectly by codec and firmware ABI code.

Risks and test signals: fields are a contract between userspace-visible V4L2 behavior and firmware ABI packing. Tests should verify controls update firmware params as expected and that color/SAR/rate-control fields survive format negotiation and parameter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_codec.h -->
