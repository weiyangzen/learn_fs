# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_rpc.h

Purpose: Defines the Amphion VPU host/firmware RPC interface abstraction used by the codec core, instances, command path, and vb2 buffer path. It provides shared buffer descriptors, the common event packet shape, and the `vpu_iface_ops` virtual table implemented by codec-specific firmware frontends such as Windsor.

Important APIs and types: `struct vpu_rpc_buffer_desc` models firmware-visible ring/stream buffer pointers. `struct vpu_shared_addr` carries the mapped RPC memory, command/message descriptors, boot-address base, owning `vpu_core`, and private per-interface state. `struct vpu_rpc_event` is the generic command/message packet. `struct vpu_iface_ops` supplies firmware hooks for codec/format support, core boot/shutdown/restore, RPC memory setup, command packing, message unpacking, stream buffer management, memory resources, encoder/decoder parameter programming, frame input, and instance lifecycle.

Control flow: Most of the file is inline dispatch. Callers resolve operations through `vpu_core_get_iface()` or `vpu_inst_get_iface()`, validate required function pointers and instance ids, then invoke the firmware-specific operation. `vpu_iface_init()` stores `core->iface = shared`, back-links `shared->core`, and rejects over-consumed RPC buffers. `vpu_iface_input_frame()` increments `inst->total_input_count` only after the backend accepts the frame. Stream buffer configuration also validates 4-byte alignment and 32-bit firmware address range.

State and persistence: The header itself persists no data, but it standardizes persistent runtime state in `core->iface`, `shared->priv`, stream descriptors, and instance counters.

Dependencies and integration: Depends on vb2, `vpu_codec.h`, VPU core/instance structures, V4L2 formats, and backend implementations in files such as `vpu_windsor.c`. It is the boundary between generic Amphion command helpers and firmware-specific ABI layouts.

Risks: Many wrappers return success when optional hooks are missing, so feature support can silently degrade. Callers must avoid passing invalid instances; most instance-scoped operations reject `inst->id < 0`, but some optional hooks no-op. Firmware address truncation is explicitly guarded for stream buffers only.

Test signals: Exercise boot/init with undersized RPC memory, command pack/send/receive paths, stream-buffer alignment errors, invalid instance ids, encoder and decoder param updates, missing optional hooks, and frame-input counter behavior.
