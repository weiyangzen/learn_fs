# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta.h

Purpose: defines the central Delta decoder data model, state machine, frame/access-unit types, decoder operation interface, device/context structures, helper string functions, and shared function prototypes.

Important APIs and types: key types include `enum delta_state`, `struct delta_streaminfo`, `struct delta_au`, `struct delta_frameinfo`, `struct delta_frame`, `struct delta_dts`, `struct delta_buf`, `struct delta_ipc_ctx`, `struct delta_ipc_param`, `struct delta_dec`, `struct delta_ctx`, and `struct delta_dev`. It declares default frameinfo/recycle helpers, frame allocation, and runtime PM helpers.

Control flow: the header describes the codec contract: decoders open/close, receive prepared frames, parse stream info, negotiate frame info, synchronously decode AUs, return decoded frames, recycle frames, and optionally flush/drain. The V4L2 layer drives these operations according to the instance state machine from waiting-for-format through EOS.

State and persistence: all fields are runtime-only. Context state tracks selected decoder, IPC context, stream/frame info validity, decoded/output/drop/error counters, DTS FIFO, buffer/frame lifecycle, work serialization, and codec-private data. Device state tracks registered decoders and rpmsg binding.

Dependencies and integration points: includes rpmsg, V4L2 device/mem2mem, and `delta-cfg.h`. It is shared by all Delta source files and forms the internal ABI between generic V4L2 code, firmware IPC, and codec backends.

Risks: many state flags and frame lifecycle bits cross module boundaries, so incomplete transitions can leak buffers or stall mem2mem jobs. The decoder ops documentation contains duplicated comments for some members, which can obscure the intended call sequence. `frame_state_str` relies on caller-provided buffers and is diagnostic only.

Test signals: compile every Delta object after struct changes, then validate decoder open/decode/recycle/flush/drain sequencing, timestamp FIFO behavior, frame state dumps, and multi-instance operation through `delta_dev->instance_id`.
