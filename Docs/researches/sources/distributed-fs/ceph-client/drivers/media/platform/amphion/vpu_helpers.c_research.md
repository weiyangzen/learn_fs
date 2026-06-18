<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_helpers.c

Purpose: provides shared utility code for format discovery, dimension validation, plane-size calculation, circular stream-buffer copying, volatile controls, start-code scanning, ID mapping, readable ID/state names, and codec profile/level conversion.

Important APIs: format helpers `vpu_helper_find_format()`, `vpu_helper_find_sibling()`, `vpu_helper_enum_format()`, and `vpu_helper_match_format()` respect iface format support. Geometry helpers clamp/align dimensions and calculate NV12/tiled/default plane sizes. Stream helpers copy/memset over circular DMA buffers and calculate used/free space from firmware descriptors. `vpu_helper_find_startcode()` strips H.264 leading garbage. `vpu_id_name()` and `vpu_codec_state_name()` feed logs/debugfs. H.264/HEVC profile/level helpers convert firmware sequence IDs to V4L2 controls.

Control flow and state: helpers are mostly pure or operate on caller-owned instance/buffer state. Stream-buffer functions update caller-provided read/write pointers but do not write firmware descriptors except through callers. Volatile control callback reads `inst->min_buffer_cap/out`.

Dependencies and integration: used by encoder, decoder, debugfs, color conversion, and firmware iface code. It calls iface format and stream descriptor operations, so helper behavior can depend on selected platform/core ops.

Risks: circular pointer validation allows `offset == end`, and `vpu_helper_step_walk()` only subtracts one length, so oversized steps could produce out-of-range pointers if callers pass sizes larger than the ring. `vpu_helper_read_byte()` indexes by `pos % length` although positions are often DMA addresses, which only works if physical base alignment does not matter for relative search use. Unknown profile/level maps to 0.

Test signals: unit-style tests for plane sizes across NV12/NV12M/tiled 8-bit/10-bit, ring copy wraparound, free/used space edge cases, H.264 start-code stripping, supported-format filtering through fuses, and profile/level controls for constrained-baseline and H.264 level 1b.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_helpers.c -->
