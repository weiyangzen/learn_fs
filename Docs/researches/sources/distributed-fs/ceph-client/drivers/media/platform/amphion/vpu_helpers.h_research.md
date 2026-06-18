<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_helpers.h

Purpose: declares shared helper APIs and small inline utilities for Amphion codec, iface, and debug code.

Important APIs/types: `struct vpu_pair` supports command/message ID mapping. Declarations cover format lookup, dimension validation, plane size, circular stream-buffer copy/memset, volatile control callback, KMP helpers, start-code scan, color conversions, ID mapping, and H.264/HEVC profile/level conversion. Inline `vpu_helper_step_walk()` advances a circular DMA pointer; `vpu_helper_read_byte()` reads a byte from a stream buffer.

Control/state behavior: header functions operate on caller-owned state. Inline helpers assume a valid `struct vpu_buffer` with nonzero length and physical-pointer style positions.

Dependencies and integration: includes `vpu_defs.h` and depends on shared VPU/V4L2 types from include context. Used broadly by encoder, decoder, firmware ABI, and debug paths.

Risks and test signals: prototype drift and inline pointer arithmetic are the main risks. Build coverage plus ring-buffer wrap tests and start-code tests should cover this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_helpers.h -->
