# Research: subset-b-004133 Amphion VPU driver files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vdec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vdec.c

Purpose: implements the V4L2 mem2mem decoder personality for the Amphion/NXP VPU. It exposes decoder ioctls, default formats, decoder controls, vb2 queue callbacks via `vpu_inst_ops`, and the firmware-event handlers that turn Malone decoder messages into V4L2 buffers, source-change events, EOS, and frame-store resource responses.

Important APIs and functions: `vdec_get_ioctl_ops()` and `vdec_get_fops()` export the decoder operation tables to video-device registration. `vdec_open()` allocates `struct vpu_inst` and private `struct vdec_t`, installs `vdec_inst_ops`, and initializes default H.264 output plus tiled NV12 capture formats. Format ioctls are handled by `vdec_enum_fmt()`, `vdec_g_fmt()`, `vdec_try_fmt()`, and `vdec_s_fmt()`. Controls are created in `vdec_ctrl_init()` and include display delay plus volatile min-buffer controls. Firmware-facing callbacks include `vdec_start_session()`, `vdec_stop_session()`, `vdec_process_output()`, `vdec_process_capture()`, `vdec_frame_decoded()`, `vdec_buf_done()`, `vdec_event_seq_hdr()`, `vdec_event_resolution_change()`, `vdec_event_req_fs()`, and `vdec_event_eos()`.

Control flow: userspace opens the decoder, configures OUTPUT compressed and CAPTURE raw formats, queues buffers, and starts streaming. OUTPUT stream-on boots/configures the core through common V4L2 code, allocates a decoder userdata buffer and firmware stream ring, calls `vpu_iface_set_decode_params()`, then sends `VPU_CMD_ID_START`. Queued compressed buffers are copied into the firmware stream buffer by `vpu_iface_input_frame()` if there is enough ring space. Firmware sequence-header messages update output geometry, colorimetry, crop, min capture buffers, profile/level controls, and side-buffer sizes. Firmware frame requests are satisfied with CAPTURE vb2 buffers as frame-store allocations, while MBI/DCP requests allocate private coherent DMA buffers. Decode-done and display-ready messages copy metadata from source buffers, update internal slot state, and complete capture buffers. Decoder commands set drain state and inject EOS padding when the source queue empties.

State and persistence: persistent per-file state is in `struct vdec_t`: `seq_hdr_found`, `params`, `codec_info`, frame-store `slots`, MBI/DCP allocators, `seq_tag`, `fixed_fmt`, `reset_codec`, decoded/display counters, EOS/drain/source-change flags, and abort state. `struct vpu_inst` holds the V4L2-facing state, stream buffer, formats, crop, sequence state, and core binding. Frame-store slots bind firmware frame IDs to vb2 capture buffers by DMA luma address and survive until firmware releases them or stream stop clears them. There is no disk persistence.

Dependencies and integration: this file depends on `vpu_v4l2` helpers for queue operations, `vpu_helpers` for formats and controls, `vpu_cmds` for synchronous firmware commands, `vpu_rpc`/Malone iface hooks for stream and frame-store commands, and vb2/V4L2 event APIs. It is registered indirectly through `vpu.h` exports used by the video-device function layer.

Risks: dynamic-resolution-change handling is sensitive to done-list draining and `source_change` counts. Frame-store reuse relies on stable DMA luma addresses and correct `fs_id` bookkeeping. `vdec_open()` leaks allocations if `vpu_v4l2_open()` fails because it returns directly without freeing `vdec`/`slots`/`inst`. Several paths return `-EINVAL` or `-ENOMEM` after setting buffer state and depend on common queue code to recover. Firmware-provided `id`, `tag`, and buffer counts are bounded in some places but malformed event ordering can leave slots pending or buffers recycled unexpectedly.

Test signals: exercise V4L2 decode of H.264/HEVC and legacy formats, `V4L2_EVENT_SOURCE_CHANGE`, EOS stop/start, streamoff on each queue, display-delay mode, format renegotiation after sequence headers, min-buffer volatile controls, and debugfs slot state. Fault tests should cover firmware frame requests without capture buffers, repeated luma addresses, source-change while capture done-list is nonempty, and open failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/venc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/venc.c

Purpose: implements the V4L2 mem2mem encoder personality for Amphion VPU, currently centered on NV12 input to H.264 capture. It owns encoder controls, format/selection ioctls, firmware memory-resource allocation, encoded-frame staging, drain/EOS behavior, and the encoder `vpu_inst_ops`.

Important APIs and functions: `venc_get_ioctl_ops()` and `venc_get_fops()` export operation tables. `venc_open()` allocates the instance and private `struct venc_t`; `venc_init()` sets defaults. Format and selection paths are `venc_enum_fmt()`, `venc_enum_framesizes()`, `venc_enum_frameintervals()`, `venc_s_fmt()`, `venc_s_parm()`, and `venc_s_selection()`. Controls are installed by `venc_ctrl_init()` and applied by `venc_op_s_ctrl()`. Firmware callbacks are `venc_start_session()`, `venc_request_mem_resource()`, `venc_process_output()`, `venc_frame_encoded()`, `venc_process_capture()`, `venc_input_done()`, and `venc_stop_session()`.

Control flow: both OUTPUT and CAPTURE stream-on bits must be enabled before firmware setup begins. Start initializes the firmware instance, allocates a stream ring sized by the firmware need and CPB size, sends encode parameters, waits for a memory request from firmware, configures encoder/ref/activity buffers, sends expert-mode parameters, starts firmware, and begins feeding queued input. INPUT completion re-enables `input_ready` and pushes more raw frames. Encoded-frame messages are copied into a `venc_frame_t` list; capture buffers consume that list by copying bytes from the firmware stream ring and advancing the firmware read pointer. Stop enters drain, sends firmware stop once input is empty and ready, waits for `venc->stopped`, then frees stream and memory-resource buffers.

State and persistence: `struct venc_t` persists encoder parameters, key-frame request, `input_ready`, CPB size, bitrate-change flag, arrays of coherent encoder/ref/activity buffers, list of pending encoded frames, counters, enable mask, stop flag, and waitqueue. No durable persistence exists; all state is per open instance.

Dependencies and integration: uses V4L2/vb2 mem2mem APIs, common format helpers, command queue APIs, Windsor firmware iface hooks selected through `vpu_rpc.c`, and `vpu_v4l2` queue helpers. The average-QP control is updated through helper state stored in `struct vpu_vb2_buffer`.

Risks: `venc_open()` has the same allocation-cleanup risk if `vpu_v4l2_open()` fails. `venc_process_output()` sends parameter updates for bitrate changes inline with input submission, so firmware command latency can affect queue progress. Start fails if the firmware memory-request callback does not arrive synchronously before `vpu_session_configure_codec()` completes. Encoded frame size is checked against capture buffer length, but start-code stripping mutates `bytesused` after that check. Stop waits only `VPU_TIMEOUT` before marking core hang and sending debug, so slow firmware can force a recovery path.

Test signals: cover STREAMON order permutations, H.264 control setting before and during streaming, force-keyframe, bitrate update while active, crop validation and alignment, CPB/capture buffer too small, empty-input start, EOS drain, streamoff with queued frames, average-QP reporting, and firmware memory request limits above `VENC_MAX_BUF_CNT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu.h

Purpose: central shared header for the Amphion VPU driver. It defines platform/core/instance state, format descriptors, buffer wrappers, operation-vector contracts, timeout constants, buffer state values, exported driver APIs, and tracing helpers.

Important APIs/types: `struct vpu_dev` represents the parent platform device, media/v4l2 devices, encoder/decoder functions, registered cores, runtime reference counters, power hooks, and debugfs root. `struct vpu_core` represents a firmware core with reserved firmware/RPC/log/activity buffers, mailbox channels, workqueues, message FIFOs, instance list, state, firmware version, hang mask, and debugfs handles. `struct vpu_inst` represents a V4L2 session with formats, controls, workqueue, firmware command queue, stream buffer, vb2 state, and codec-specific private data. `struct vpu_inst_ops` is the contract implemented by `vdec.c` and `venc.c`.

Control flow and state: instances call `vpu_request_core()`/`vpu_inst_register()` to bind to an active core and acquire an instance ID. Common V4L2 and message code uses `call_vop()`/`call_void_vop()` to dispatch codec-specific behavior. Buffer state constants layer driver-specific state on top of vb2 state, especially for decode frame-store ownership and encoded output readiness.

Dependencies and integration: pulls in V4L2 device/controls/mem2mem, mailbox, and kfifo APIs. Declares exported functions implemented across `vpu_drv.c`, `vpu_core.c`, `vpu_dbg.c`, `vdec.c`, and `venc.c`.

Risks: because this header defines shared mutable structures, lifetime and locking assumptions are spread across files. `instance_mask` and `hang_mask` are bitfields stored as `unsigned long` and depend on bounds from `supported_instance_count`. The misspelled `VPU_CODEC_STATE_DYAMIC_RESOLUTION_CHANGE` is ABI-internal but easy to propagate.

Test signals: build coverage catches struct/API drift. Runtime signals are correct core allocation/release, debugfs instance visibility, reference-counted cleanup, and consistent driver buffer-state transitions under both encoder and decoder workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_cmds.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_cmds.c

Purpose: owns firmware command allocation, serialization, synchronous response tracking, timeout handling, and exported session/core command helpers.

Important APIs/functions: exported helpers include `vpu_session_configure_codec()`, `vpu_session_start()`, `vpu_session_stop()`, `vpu_session_encode_frame()`, `vpu_session_alloc_fs()`, `vpu_session_release_fs()`, `vpu_session_abort()`, `vpu_session_rst_buf()`, `vpu_session_fill_timestamp()`, `vpu_session_update_parameters()`, `vpu_core_snapshot()`, `vpu_core_sw_reset()`, `vpu_response_cmd()`, and `vpu_clear_request()`. Internal `struct vpu_cmd_t` stores the packed RPC event, expected response mapping, sequence key, and last-response pointer.

Control flow: callers request a command through `vpu_session_send_cmd()`. The command is packed through the selected iface, queued on `inst->cmd_q`, and sent under `core->cmd_lock` if no other response-waiting command is pending. Commands with expected responses become `inst->pending`. Message handling calls `vpu_response_cmd()` first with `handled=0` when a matching event is received and again with `handled=1` after handler completion; the mapping decides when the pending command is cleared. Synchronous callers wait on `core->ack_wq` using command sequence keys. Start/configure have a wakeup workaround that sends a NOOP if the first short wait times out.

State and persistence: state is in the instance command list, `pending`, monotonic `cmd_seq`, and atomic `last_response_cmd`. Core state may be marked hung via `hang_mask` on timeout. No persistent storage.

Dependencies and integration: uses iface pack/send/pre/post hooks from `vpu_rpc.c`, mailbox signaling from `vpu_mbox.c`, response events from `vpu_msgs.c`, and wait lock callbacks from codec ops.

Risks: response matching depends on firmware event order and the `handled` flag policy. A timeout clears pending and marks the core hang but queued commands may have already been sent or remain queued. `vpu_clear_request()` assumes `inst->core` exists. NOOP wakeup is explicitly a firmware workaround and can hide marginal boot/start races.

Test signals: command timeout injection, response reordering, configure/start wakeup retry, abort/reset buffer, snapshot/reset completion, concurrent queue submissions under `cmd_lock`, and streamoff while a synchronous command is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_cmds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_cmds.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_cmds.h

Purpose: declares the command/session control API used by codec implementations, debugfs, message handling, and core power-management paths.

Important APIs: session helpers cover configure, start, stop, abort, reset-buffer, encode-frame, frame-store allocation/release, timestamp submission, parameter update, and debug. Core helpers cover snapshot and software reset. `vpu_response_cmd()` and `vpu_clear_request()` expose response and cleanup hooks.

Control/state behavior: the header itself has no state; it formalizes that callers operate on `struct vpu_inst` or `struct vpu_core` and that command synchronization is centralized in `vpu_cmds.c`.

Dependencies and integration: depends on `struct vpu_inst`, `struct vpu_core`, `struct vpu_fs_info`, and `struct vpu_ts_info` definitions from shared Amphion headers.

Risks and test signals: API drift is the primary risk. Build tests should catch mismatched prototypes, while runtime testing should verify every declared command path reaches firmware and receives the expected response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_cmds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_codec.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_codec.h

Purpose: defines codec parameter payloads shared between V4L2-facing code and firmware-specific iface implementations.

Important types: `struct vpu_encode_params` carries input/output formats, profile/level/tier, frame rate, source stride and dimensions, crop, output dimensions, GOP/B-frame settings, rate-control fields, QP limits, SAR, and colorimetry. `struct vpu_decode_params` carries codec/output formats, display-delay controls, non-frame mode, frame count, end flag, and userdata buffer address/size.

Control/state behavior: encoder and decoder private state owns these structs and mutates them from V4L2 controls/format ioctls. Firmware iface implementations serialize them into Windsor/Malone shared memory and update fields such as decoder `end_flag`.

Dependencies and integration: requires V4L2 fraction and rectangle types. Included indirectly by codec and firmware ABI code.

Risks and test signals: fields are a contract between userspace-visible V4L2 behavior and firmware ABI packing. Tests should verify controls update firmware params as expected and that color/SAR/rate-control fields survive format negotiation and parameter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_codec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_color.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_color.c

Purpose: converts color metadata between V4L2 enum values and firmware integer table indices for color primaries, transfer functions, matrix coefficients, and quantization range.

Important APIs: `vpu_color_cvrt_primaries_v2i/i2v()`, `vpu_color_cvrt_transfers_v2i/i2v()`, `vpu_color_cvrt_matrix_v2i/i2v()`, and `vpu_color_cvrt_full_range_v2i/i2v()`.

Control flow and state: conversion is table-driven using static arrays and `vpu_helper_find_in_array_u8()` for V4L2-to-index lookup. Unknown or unsupported mappings usually convert to 0 or V4L2 LAST/default-like placeholders. No mutable state exists.

Dependencies and integration: used by Malone sequence-header unpacking and parameter packing paths to expose firmware color metadata through decoder formats and controls.

Risks: lossy mappings can collapse unsupported V4L2 values to index 0, and firmware indices outside the table become 0. Color metadata regressions are visible only when userspace checks format colorimetry or decoded streams include VUI.

Test signals: decode streams with Rec.709, SMPTE170M, BT.2020, full/limited range, and unknown VUI values; assert V4L2 `G_FMT` color fields and firmware parameter tables round-trip correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_color.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_core.c

Purpose: platform child-driver for individual encoder/decoder firmware cores. It maps reserved memory and registers, initializes iface shared memory, handles firmware loading/boot/reset/shutdown, manages runtime PM and mailbox lifetime, allocates instance IDs, and owns core-level DMA helpers.

Important APIs/functions: exported `csr_writel()`, `csr_readl()`, `vpu_alloc_dma()`, `vpu_free_dma()`, `vpu_core_set_state()`, `vpu_request_core()`, `vpu_release_core()`, `vpu_inst_register()`, `vpu_inst_unregister()`, `vpu_core_find_instance()`, `vpu_get_resource()`, `vpu_core_driver_init()`, and `vpu_core_driver_exit()`. Probe/remove are `vpu_core_probe()` and `vpu_core_remove()`.

Control flow: probe reads reserved boot/RPC regions, remaps them, validates uncached RPC placement, derives log/activity subregions, maps CSR registers, initializes mailbox and iface private data, configures system/log buffers, enables runtime PM, registers the core with the parent VPU, and creates debugfs. `vpu_request_core()` selects a deinitialized or least-used active core, resumes it, boots/restores if needed, and increments `request_count`. Instance registration acquires an instance bit and optional activity slice. Suspend snapshots active firmware, cancels work, and releases parent references; resume reboots or resets active cores and resumes queued message work.

State and persistence: `struct vpu_core` persists firmware/RPC/log/activity memory descriptors, instance list/mask, request count, supported instance count, firmware version, state, hang mask, mailbox handles, FIFOs, workqueues, and iface pointer. State is memory-only and rebuilt at probe/boot.

Dependencies and integration: depends on reserved-memory DT bindings, platform driver matching (`nxp,imx8q-vpu-encoder`/decoder), request_firmware, dma coherent allocations, pm_runtime, mailbox setup, iface ops from `vpu_rpc.c`, and parent `vpu_dev` from `vpu_drv.c`.

Risks: `vpu_core_parse_dt()` can leak memremap mappings on later validation failure. Pointer arithmetic on `void *` is GCC-extension style. Runtime PM calls sometimes ignore negative resume return values. Hang recovery is tied to unregister when no instances remain. Correct reserved-memory layout and uncached attributes are mandatory.

Test signals: probe/remove with valid and invalid DT reserved-memory regions, firmware too large, boot timeout, runtime suspend/resume with active sessions, core hang/reset after command timeout, multi-instance allocation bounds, mailbox request failure, and debugfs core status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_core.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_core.h

Purpose: declares the core-level helpers shared by command, debug, platform, and codec code.

Important APIs: CSR accessors, coherent DMA alloc/free for core-owned devices, instance lookup by firmware index, and core state setter.

Control/state behavior: callers use these APIs to access memory-mapped core registers, allocate DMA buffers associated with a core device, find live instances during message dispatch, and transition `enum vpu_core_state`.

Dependencies and integration: depends on `struct vpu_core`, `struct vpu_buffer`, `struct vpu_inst`, and `enum vpu_core_state` from `vpu.h`.

Risks and test signals: small header, mostly build-contract risk. Runtime validation is through core probe/boot, DMA allocation/free paths, and message dispatch to active instance IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_dbg.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_dbg.c

Purpose: provides debugfs observability and control hooks for Amphion cores and instances, including queue state, driver buffer state, format/crop data, stream-buffer usage, firmware ring pointers, firmware log extraction, command/event flow history, and manual debug/reset triggers.

Important APIs/functions: `vpu_inst_create_dbgfs_file()`, `vpu_inst_remove_dbgfs_file()`, `vpu_core_create_dbgfs_file()`, `vpu_core_remove_dbgfs_file()`, and `vpu_inst_record_flow()`. Seqfile readers are `vpu_dbg_instance()`, `vpu_dbg_core()`, and `vpu_dbg_fwlog()`. Write handlers trigger `vpu_session_debug()` for instances and a core software reset attempt for idle powered cores.

Control flow: core and instance registration create debugfs files under `amphion_vpu`. Reading an instance file reports V4L2 queues, per-buffer vb2 and VPU states, crop, stream ring usage, message FIFO length, recent command/message flow, and codec-specific debug lines through `get_debug_info`. Reading a core file reports reserved regions, power/state, firmware version, instance count, core FIFO length, and command/message ring pointers. Reading firmware log drains the firmware print ring by advancing its read pointer.

State and persistence: debugfs dentries are stored on `vpu_dev`, `vpu_core`, and `vpu_inst`. Flow history is a 16-entry ring in `struct vpu_inst`. Firmware log reads mutate firmware log read offset; otherwise no durable persistence.

Dependencies and integration: depends on V4L2/vb2 queue internals, kfifo, pm_runtime, command/reset helpers, iface power state, and codec `get_debug_info` callbacks.

Risks: debug output indexes `vb2_stat_name[vb->state]` without a local bounds check. Firmware log read mutates shared firmware memory and may race with firmware writes. Core debug write can reset an idle powered core from userspace if debugfs permissions allow it. `to_vpu_stat_name()` treats `VPU_BUF_STATE_CHANGED` as unknown because it checks `<= VPU_BUF_STATE_ERROR`.

Test signals: inspect debugfs during idle, active decode, active encode, EOS drain, source change, and firmware-log generation; write instance/core debug files; verify removal on stream close and driver remove; run with unusual vb2 buffer states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_defs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_defs.h

Purpose: defines common firmware command/message IDs, IRQ codes, memory-resource types, start-code types, firmware event payload structs, and bitrate constants.

Important APIs/types: `enum MSG_TYPE` is mailbox boot/command signaling; IRQ constants describe boot/snapshot/sync events; command IDs and message IDs provide driver-normalized firmware operations/events. Payload structs include `vpu_pkt_mem_req_data`, `vpu_enc_pic_info`, `vpu_dec_codec_info`, `vpu_dec_pic_info`, `vpu_fs_info`, and `vpu_ts_info`.

Control/state behavior: no code executes here, but the structs are the cross-file data contract for command packing/unpacking, V4L2 event generation, buffer completion, memory-resource allocation, and timestamp submission.

Dependencies and integration: consumed by command, message, encoder, decoder, Windsor/Malone iface, helpers, and debug code. It relies on V4L2 constants and `VIDEO_MAX_PLANES` through include context.

Risks: spelling `VPU_ENC_MEMORY_RESOURSE` is harmless but persistent. Any change to IDs or payload layout must be reflected in firmware-specific mapping arrays. Firmware-provided sizes and counts influence DMA allocations and buffer payloads, so validation at consumers is critical.

Test signals: compile-time use across all Amphion objects, firmware ABI compatibility tests for each message/command, and runtime validation of decoded sequence metadata, memory requests, encoded frame info, and EOS timestamp behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_drv.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_drv.c

Purpose: parent platform driver for the Amphion VPU device. It owns top-level register mapping, V4L2/media-device registration, encoder/decoder function creation, debugfs root, child core population, platform resource callbacks, and module init/exit.

Important APIs/functions: `vpu_writel()`/`vpu_readl()` access parent registers. `vpu_probe()` initializes `struct vpu_dev`, media/V4L2 devices, encoder/decoder `vpu_func` descriptors, debugfs, runtime PM, and child devices. `vpu_remove()` unwinds them. `vpu_driver_init()` registers the parent driver then the core driver; exit unregisters in reverse.

Control flow: matching `nxp,imx8qxp-vpu` or `nxp,imx8qm-vpu` selects platform resources with setup/reset hooks from `vpu_imx8q.c`. Probe registers decoder then encoder V4L2 functions, registers the media device, creates debugfs, and populates child nodes. Reference callbacks call setup hooks on first VPU/encoder/decoder use but only decrement counters on put.

State and persistence: `struct vpu_dev` holds parent state, function descriptors, media device, core list, refs, and debugfs. State is recreated on probe and removed at driver unload. No disk persistence.

Dependencies and integration: depends on OF matching/population, pm_runtime, media controller, V4L2 device registration, debugfs, and function registration helpers implemented elsewhere in the driver.

Risks: setup reference counters are not guarded against underflow on mismatched puts. `of_platform_populate()` return value is ignored. Parent runtime PM is enabled but no parent PM ops are defined here. Child population after debugfs/media registration means later child failures do not fail parent probe.

Test signals: parent probe/remove on supported compatibles, child core discovery, media graph presence, `/dev/video*` function registration, debugfs root creation/removal, module unload with active children rejected by core lifetimes, and error injection through `vpu_add_func()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_helpers.c

Purpose: provides shared utility code for format discovery, dimension validation, plane-size calculation, circular stream-buffer copying, volatile controls, start-code scanning, ID mapping, readable ID/state names, and codec profile/level conversion.

Important APIs: format helpers `vpu_helper_find_format()`, `vpu_helper_find_sibling()`, `vpu_helper_enum_format()`, and `vpu_helper_match_format()` respect iface format support. Geometry helpers clamp/align dimensions and calculate NV12/tiled/default plane sizes. Stream helpers copy/memset over circular DMA buffers and calculate used/free space from firmware descriptors. `vpu_helper_find_startcode()` strips H.264 leading garbage. `vpu_id_name()` and `vpu_codec_state_name()` feed logs/debugfs. H.264/HEVC profile/level helpers convert firmware sequence IDs to V4L2 controls.

Control flow and state: helpers are mostly pure or operate on caller-owned instance/buffer state. Stream-buffer functions update caller-provided read/write pointers but do not write firmware descriptors except through callers. Volatile control callback reads `inst->min_buffer_cap/out`.

Dependencies and integration: used by encoder, decoder, debugfs, color conversion, and firmware iface code. It calls iface format and stream descriptor operations, so helper behavior can depend on selected platform/core ops.

Risks: circular pointer validation allows `offset == end`, and `vpu_helper_step_walk()` only subtracts one length, so oversized steps could produce out-of-range pointers if callers pass sizes larger than the ring. `vpu_helper_read_byte()` indexes by `pos % length` although positions are often DMA addresses, which only works if physical base alignment does not matter for relative search use. Unknown profile/level maps to 0.

Test signals: unit-style tests for plane sizes across NV12/NV12M/tiled 8-bit/10-bit, ring copy wraparound, free/used space edge cases, H.264 start-code stripping, supported-format filtering through fuses, and profile/level controls for constrained-baseline and H.264 level 1b.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_helpers.h

Purpose: declares shared helper APIs and small inline utilities for Amphion codec, iface, and debug code.

Important APIs/types: `struct vpu_pair` supports command/message ID mapping. Declarations cover format lookup, dimension validation, plane size, circular stream-buffer copy/memset, volatile control callback, KMP helpers, start-code scan, color conversions, ID mapping, and H.264/HEVC profile/level conversion. Inline `vpu_helper_step_walk()` advances a circular DMA pointer; `vpu_helper_read_byte()` reads a byte from a stream buffer.

Control/state behavior: header functions operate on caller-owned state. Inline helpers assume a valid `struct vpu_buffer` with nonzero length and physical-pointer style positions.

Dependencies and integration: includes `vpu_defs.h` and depends on shared VPU/V4L2 types from include context. Used broadly by encoder, decoder, firmware ABI, and debug paths.

Risks and test signals: prototype drift and inline pointer arithmetic are the main risks. Build coverage plus ring-buffer wrap tests and start-code tests should cover this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_imx8q.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_imx8q.c

Purpose: implements i.MX8Q platform-specific setup, reset, firmware boot customization, memory-region classification, system-config population, and optional SCU fuse checks for codec availability.

Important APIs/functions: `vpu_imx8q_setup()`, `vpu_imx8q_setup_dec()`, `vpu_imx8q_setup_enc()`, `vpu_imx8q_reset()`, `vpu_imx8q_set_system_cfg_common()`, `vpu_imx8q_boot_core()`, `vpu_imx8q_get_power_state()`, `vpu_imx8q_on_firmware_loaded()`, `vpu_imx8q_check_memory_region()`, `vpu_imx8q_check_codec()`, and `vpu_imx8q_check_fmt()`.

Control flow: parent/core setup writes SoC block-control registers to enable clocks and release resets. Firmware boot writes the firmware physical address to CM0P CSR and clears CPUWAIT. Firmware-loaded hook patches platform type, core ID, and a flag into the firmware image. System config maps core IDs to Malone or Windsor register bases and IRQ pins. With `CONFIG_IMX_SCU`, fuse values are fetched once from SCU and used to disable whole codecs or specific H.264/HEVC decoder formats.

State and persistence: optional static `imx8q_fuse` and `fuse_got` cache SCU fuse state for the module lifetime. Hardware register state persists in the device until reset/power changes.

Dependencies and integration: used by parent resource callbacks and iface ops in `vpu_rpc.c`; depends on i.MX SCU firmware APIs when configured and register offsets from `vpu_imx8q.h`.

Risks: setup/reset sequences are SoC-specific and largely unchecked. `vpu_imx8q_check_memory_region()` requires `addr + size < region->end`, excluding exact-end regions. Firmware image patching assumes at least 19 bytes. Fuse failure returns permissive defaults in non-SCU or read-failure paths.

Test signals: boot both encoder and decoder cores, verify CSR CPUWAIT transitions, validate system config addresses for core IDs 0/1/2, run with SCU fuse configurations disabling encoder/H.264/HEVC, and test reserved memory at region boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_imx8q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_imx8q.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_imx8q.h

Purpose: declares i.MX8Q register offsets, MediaIP limits, IRQ-pin constants, the firmware `vpu_rpc_system_config` layout, and platform-specific function prototypes.

Important APIs/types: register macros cover SCB, decoder, encoder, HIF/SIF/MCX, block control, cache, and pixel interface bases. `struct vpu_rpc_system_config` mirrors the firmware-visible system topology for Malone/Windsor cores, command/message IRQs, timers, cache, heap, UART, and trace configuration.

Control/state behavior: no code executes here; it is the ABI and register map used by `vpu_imx8q.c`, `vpu_malone.c`, and Windsor code.

Dependencies and integration: included by platform and firmware iface files. Its constants determine how parent register base plus per-core offsets are written into shared memory.

Risks and test signals: incorrect offsets break firmware boot or stream-buffer register access. Build coverage plus boot tests on i.MX8QXP/i.MX8QM and firmware system-config inspection are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_imx8q.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_malone.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_malone.c

Purpose: implements the Malone decoder firmware ABI for Amphion. It lays out the decoder RPC shared memory, configures stream buffers and system settings, maps V4L2 formats to Malone formats, packs decoder commands, converts/unpacks firmware messages, inserts codec-specific start codes/padding, copies compressed input into the firmware ring, and manages Malone command FIFO readiness.

Important APIs/functions: exported iface hooks include `vpu_malone_get_data_size()`, `vpu_malone_init_rpc()`, `vpu_malone_set_log_buf()`, `vpu_malone_set_system_cfg()`, `vpu_malone_get_version()`, stream buffer get/config/update functions, `vpu_malone_set_decode_params()`, `vpu_malone_pack_cmd()`, `vpu_malone_convert_msg_id()`, `vpu_malone_unpack_msg_data()`, `vpu_malone_add_scode()`, `vpu_malone_input_frame()`, command readiness hooks, instance init, max-instance count, and format enable/check.

Control flow: core probe asks for private data size and calls init to carve the RPC reserved memory into iface structure, command/message rings, codec/jpeg/sequence/picture/GOP/qmeter/log tables, per-stream engine buffers, and encryption records. Decoder start configures stream registers and shared params. Commands are mapped from driver IDs to Malone VID_API IDs and optionally filled with frame-store or timestamp payloads. Firmware messages are mapped back to common VPU message IDs and unpacked into shared structs. Input frames may get synthetic sequence/picture headers for VC1/VP8/SPK, payload bytes are copied into the circular stream buffer, optional EOS/abort/low-latency padding is inserted, then a timestamp command informs firmware of input size.

State and persistence: `struct malone_iface` lives in shared RPC memory visible to firmware. Driver-private `struct vpu_dec_ctrl` caches pointers into RPC subregions and stream-buffer MMIO windows. Static `fmt_mappings` is mutable because RV support is enabled/disabled based on firmware version. Module parameter `low_latency` affects padding insertion.

Dependencies and integration: selected as decoder iface in `vpu_rpc.c`; used heavily by `vdec.c`. Depends on `vpu_imx8q` system config and register offsets, `vpu_helpers` ring copying and plane-size helpers, `vpu_color` conversion helpers, and command helpers for timestamp submission.

Risks: many firmware payload fields are unpacked without checking `pkt->hdr.num` except for optional constraint flags, so malformed short messages can read beyond valid event payload. Shared-memory layout assumes RPC size is sufficient; `vpu_core.c` only checks total rpc/log size, not every Malone suballocation in isolation. Static format disabling is global, so multiple decoder cores with different firmware capabilities would share it. Padding/start-code insertion must preserve ring-space assumptions made in `vdec_process_output()`.

Test signals: decode every advertised compressed format, especially VC1 Annex G/L, VP8, SPK, H.264/HEVC low-latency/display-delay paths, RV enablement by firmware version, EOS/abort padding, stream-buffer wraparound, frame-store allocation/release packing, timestamp size accounting with `extra_size`, and malformed/short firmware event fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_malone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_malone.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_malone.h

Purpose: declares the Malone decoder iface contract consumed by generic RPC dispatch and decoder code.

Important APIs: declarations cover RPC layout/init, log/system config, version, stream-buffer sizing and pointer updates, decode parameter setting, command packing, message conversion/unpacking, start-code insertion, input-frame submission, command readiness, instance initialization, max-instance count, format support, and runtime format enablement.

Control/state behavior: no state in the header; functions operate on `struct vpu_shared_addr`, instance IDs, `struct vpu_buffer`, `struct vpu_inst`, and firmware event packets.

Dependencies and integration: paired with `vpu_malone.c` and plugged into decoder entries of `imx8q_rpc_ops` in `vpu_rpc.c`.

Risks and test signals: ABI mismatch between this header and `vpu_rpc.c` iface table is the main risk. Build tests and decoder boot/start/input/message tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_malone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_mbox.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_mbox.c

Purpose: wraps Linux mailbox channels used to signal firmware command types/data and receive firmware IRQ codes.

Important APIs/functions: `vpu_mbox_init()` names `tx0`, `tx1`, and `rx`; `vpu_mbox_request()` opens all channels; `vpu_mbox_free()` releases them; `vpu_mbox_send_type()` and `vpu_mbox_send_msg()` transmit firmware notifications. `vpu_mbox_rx_callback()` forwards incoming mailbox words to `vpu_isr()`.

Control flow: runtime resume in `vpu_core.c` requests channels. Command submission writes data to shared memory then calls `vpu_mbox_send_type(COMMAND)`. Boot sync response sends PRC buffer offset, boot address, and INIT_DONE through `vpu_mbox_send_msg()`. Runtime suspend frees channels.

State and persistence: each `struct vpu_mbox` stores channel name, client, channel pointer, and blocking mode. No durable persistence.

Dependencies and integration: depends on Linux mailbox framework and `vpu_msgs.c` ISR path. Channel names must match device-tree mailbox names.

Risks: send helpers do not check `mbox_send_message()` return values or NULL channel pointers. RX callback assumes `msg` points to a `u32`. Failure to request any channel frees all channels and aborts runtime resume.

Test signals: mailbox DT binding validation, request/free across runtime suspend/resume, command interrupt delivery, boot sync sequence, RX callback with boot/snapshot/message codes, and failure injection for missing channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_mbox.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_mbox.h

Purpose: declares mailbox lifecycle and send helpers for core code and command/message code.

Important APIs: `vpu_mbox_init()`, `vpu_mbox_request()`, `vpu_mbox_free()`, `vpu_mbox_send_msg()`, and `vpu_mbox_send_type()`.

Control/state behavior: no state in header; functions operate on a `struct vpu_core` containing three `struct vpu_mbox` channels.

Dependencies and integration: implemented by `vpu_mbox.c`, called from core runtime PM, command send, and boot-sync message handling.

Risks and test signals: header drift is build-visible. Runtime validation is mailbox request, command signaling, and cleanup on suspend/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_mbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_msgs.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_msgs.c

Purpose: handles firmware interrupt codes and RPC messages, routes instance messages through workqueues/FIFOs, invokes codec callbacks, and completes pending commands.

Important APIs/functions: exported `vpu_isr()`, `vpu_inst_run_work()`, `vpu_msg_run_work()`, and `vpu_msg_delayed_work()`. Internal handlers cover start/stop, memory request, sequence header, resolution change, encode done, frame request/release, input done, picture decoded/displayed, EOS, unsupported stream, firmware exception, skipped picture, and debug string messages.

Control flow: mailbox RX calls `vpu_isr()`, which completes core boot/snapshot completions for special IRQs, enqueues the IRQ code in the core FIFO, and schedules core work. Core work handles boot sync mailbox replies or drains RPC messages from firmware. Each message is converted to a common ID, matched to a live instance, used to advance command response state with `handled=0`, recorded in flow history, queued into the instance FIFO, and later processed in instance work. Instance handlers unpack payloads through iface ops, call codec `vpu_inst_ops`, and finally call `vpu_response_cmd(..., handled=1)`.

State and persistence: uses core and instance kfifo buffers plus workqueues. It can set `core->hang_mask` and V4L2 queue error state on firmware exceptions. No durable persistence.

Dependencies and integration: depends on `vpu_rpc.c` iface conversion/unpack hooks, `vpu_cmds.c` response tracking, `vpu_mbox.c` boot-sync sends, codec ops in `vdec.c`/`venc.c`, and V4L2 error helpers.

Risks: FIFO overflow drops messages and only logs. String termination reduces `hdr.num` when full but assumes data is word-addressable as a string. Message payload validity largely depends on firmware-specific unpackers. The two-phase command response model requires handler completion to run; if instance workqueue is unavailable, sync commands can time out.

Test signals: boot IRQ, snapshot IRQ, high-volume message FIFO pressure, every handler type, unsupported stream and firmware exception, instance close while messages are queued, delayed-work recovery for nonempty FIFOs, and command completion timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_msgs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_msgs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_msgs.h

Purpose: declares the firmware interrupt/message work entry points used by mailbox and core initialization.

Important APIs: `vpu_isr()` receives a firmware IRQ word for a core. `vpu_inst_run_work()`, `vpu_msg_run_work()`, and `vpu_msg_delayed_work()` are workqueue callbacks for instance and core message draining.

Control/state behavior: header has no state; the implementation operates on core/instance FIFOs and workqueue structs embedded in `vpu_core` and `vpu_inst`.

Dependencies and integration: implemented in `vpu_msgs.c`; called by `vpu_mbox.c` RX callback and assigned during core/instance workqueue initialization.

Risks and test signals: build-contract risk only. Runtime signals are correct IRQ-to-workqueue routing and message delivery to active instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_msgs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_rpc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_rpc.c

Purpose: provides common RPC ring-buffer send/receive helpers and selects the firmware iface operation table for i.MX8Q encoder/decoder cores.

Important APIs/functions: `vpu_iface_check_memory_region()`, `vpu_core_get_iface()`, and `vpu_inst_get_iface()` are exported. Internal `vpu_rpc_send_cmd_buf()` writes command packets into the shared command ring; `vpu_rpc_receive_msg_buf()` reads firmware messages from the shared message ring; `vpu_rpc_check_buffer_space()` handles ring free/used calculations. `imx8q_rpc_ops` binds encoder cores to Windsor ops and decoder cores to Malone ops.

Control flow: command code packs a `vpu_rpc_event`, calls the selected iface send function, then mailbox-signals firmware. Message work calls receive repeatedly until no full message is available. Core/instance code uses `vpu_core_get_iface()` or `vpu_inst_get_iface()` to dispatch all firmware-specific behavior.

State and persistence: no private persistent state beyond the static iface table. Ring state lives in shared RPC memory descriptors owned by firmware and initialized by Windsor/Malone init code.

Dependencies and integration: includes i.MX8Q platform ops, Windsor encoder ABI, and Malone decoder ABI. It is the dispatch bridge between generic VPU code and firmware-specific implementations.

Risks: `imx8q_rpc_ops` is indexed by enum values where decoder is `0x10`, so the array is sparse and `ARRAY_SIZE` must remain large enough. `vpu_rpc_check_msg()` compares message payload word count to available words without adding the header word, which matches existing logic only if firmware semantics align. Ring helpers assume descriptors and memory pointers are valid and not concurrently corrupted by firmware.

Test signals: command/message ring wraparound, full/empty ring boundaries, sparse decoder iface lookup, platform type selection, encoder and decoder boot through selected ops, malformed packet `hdr.num`, and concurrent firmware message production while the driver drains messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_rpc.c -->
