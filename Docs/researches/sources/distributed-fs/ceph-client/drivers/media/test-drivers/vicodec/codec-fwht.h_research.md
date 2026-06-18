# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-fwht.h

Purpose: public raw FWHT codec contract shared by the codec engine and V4L2 adapter.

Important APIs/types/functions: defines `FWHT_MAGIC1`, `FWHT_MAGIC2`, `vic_round_dim()`, `struct fwht_cframe_hdr`, `struct fwht_cframe`, `struct fwht_raw_frame`, raw codec flag bits, and prototypes for `fwht_encode_frame()` and `fwht_decode_frame()`. The header documents the compressed stream layout in detail.

Control flow: the header itself has no control flow, but it defines how encoded frames are structured: an 8-byte magic sequence, big-endian metadata, compressed-frame size, then per-plane RLE or raw payloads. Macroblock headers carry P-coded state and duplicate counts, and coefficient words carry zero-run length plus quantized coefficient.

State and persistence: `fwht_cframe_hdr` is serialized into compressed buffers. `fwht_cframe` and `fwht_raw_frame` are transient caller-owned structures for scratch and frame component layout.

Dependencies and integration points: includes Linux types, bitops, byteorder, and is consumed by `codec-fwht.c`, `codec-v4l2-fwht.h`, and `vicodec-core.c`. The serialized header interoperates with V4L2 FWHT userspace controls/formats.

Risks: the serialized ABI depends on big-endian fields and magic values; any extension must preserve sync and version handling. `vic_round_dim()` rounds dimensions after subsampling division and multiplication, so callers must understand coded versus visible dimensions.

Test signals: compile-time users of struct layout, encoded stream parser tests validating magic/version/size, and cross-endian encode/decode compatibility checks.
