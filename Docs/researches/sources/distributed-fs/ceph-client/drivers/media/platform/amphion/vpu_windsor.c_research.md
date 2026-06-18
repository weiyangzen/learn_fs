# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_windsor.c

Purpose: Implements the Windsor/MediaIP encoder firmware RPC ABI for Amphion VPU encoding. It lays out shared RPC memory, maps generic VPU command/message ids to firmware ids, fills encoder input descriptors, configures firmware memory resources and stream buffers, and translates V4L2 encode parameters into Windsor control structures.

Important APIs and types: Exports `vpu_windsor_get_data_size()`, `vpu_windsor_init_rpc()`, log/system configuration, stream buffer sizing/config/update/descriptor reads, command packing, message id conversion, message data unpacking, memory resource configuration, frame input, version/max-instance queries, and encode parameter programming. Internal structures model `windsor_iface`, per-stream control interfaces, YUV descriptors, expert/config/static/dynamic params, encoder params, memory pools, status blocks, and picture-info messages.

Control flow: `vpu_windsor_init_rpc()` partitions one RPC buffer into firmware interface, command ring, message ring, per-stream control descriptors, and host control structures, writing firmware-relative addresses and storing host pointers in `shared->priv`. Commands are translated through lookup tables; frame encode commands include timestamp seconds/nanoseconds. Input buffers fill Y and UV physical addresses and keyframe flags, then call `vpu_session_encode_frame()`. Firmware messages unpack frame-done, memory-request, and frame-release payloads.

State and persistence: Runtime state lives entirely in shared DMA memory and `shared->priv`. Stream buffer descriptors persist firmware read/write pointers; memory pools persist physical/firmware-relative resource addresses; encode params persist until updated.

Dependencies and integration: Depends on Amphion core, RPC, command/session helpers, V4L2 controls, vb2 DMA addresses, color conversion helpers, and i.MX8Q system config helpers. `vpu_windsor.h` exposes the implementation to the interface table.

Risks: Firmware ABI structures are large and tightly packed by C layout assumptions; any mismatch breaks firmware communication. `vpu_windsor_config_stream_buffer()` lacks local instance range validation unlike memory-resource setup. Some setter return values are ignored in aggregate parameter setup. The frame-rate calculation divides denominator by numerator after checking only numerator.

Test signals: Validate RPC buffer byte usage, per-stream pointer layout, H.264 profile/level/bitrate/QP/SAR/color mappings, NV12/NV12M input rejection/acceptance, memory request handling, stream pointer wrap/32-bit handling, timestamp round trips, and multi-instance max-stream behavior.
