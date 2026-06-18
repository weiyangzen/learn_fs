# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-v4l2-fwht.h

Purpose: V4L2 FWHT adapter interface and state definitions.

Important APIs/types/functions: `struct v4l2_fwht_pixfmt_info` captures pixel-format ID, bytes-per-line/sizeimage factors, component steps, subsampling, component/plane counts, and FWHT pixel encoding. `struct v4l2_fwht_state` stores selected format, geometry, stride/reference stride, GOP/QP values, colorspace metadata, reference frame, header, compressed buffer, and reference timestamp. Function prototypes expose pixel-format lookup/validation and encode/decode.

Control flow: no executable flow in the header; it defines the data contract used by vicodec core and the FWHT adapter.

State and persistence: `v4l2_fwht_state` is per vicodec context and persists across frames while queues stream. It carries the reference frame and GOP count that make stateful P-frame decoding/encoding possible. The `header` field is filled either from bytestream headers or stateless controls.

Dependencies and integration points: includes `codec-fwht.h` and uses V4L2 enum types. It is the interface between high-level V4L2 mem2mem code and the raw codec.

Risks: adding pixel formats requires keeping size multipliers, component counts, and subsampling flags consistent with both V4L2 queue sizing and raw codec pointer math.

Test signals: compile-time coverage through vicodec, per-format enumeration consistency, and stateless decode controls matching `v4l2_fwht_validate_fmt()`.
