# subset-b-004143 Research

This grouped report covers MediaTek VPU/vcodec decoder and encoder files under `sources/distributed-fs/ceph-client`. Each file section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_vp9_req_lat_if.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_vp9_req_lat_if.c

Purpose: implements the stateless VP9 frame decoder backend for MediaTek vcodec hardware, including both pure single-core decode and split LAT/core decode. It exports `vdec_vp9_slice_lat_if`, a `vdec_common_if` selected for `V4L2_PIX_FMT_VP9_FRAME`, and translates V4L2 VP9 controls plus queued VB2 buffers into firmware-visible VSI structures.

Important APIs/types/functions: the file defines firmware ABI payloads such as `vdec_vp9_slice_vsi`, `vdec_vp9_slice_pfc`, frame headers, tile metadata, VP9 probability/count tables, and per-instance state in `vdec_vp9_slice_instance`. Main entry points are `vdec_vp9_slice_init`, `vdec_vp9_slice_decode`, `vdec_vp9_slice_get_param`, and `vdec_vp9_slice_deinit`; important helpers include working-buffer allocation/free, probability context mapping/adaptation, LAT/core setup, and `vdec_vp9_slice_core_decode`.

Control flow: init allocates an instance, initializes `vdec_vpu_inst`, maps the firmware VSI and core VSI, and caches a shared default VP9 frame context from firmware memory. Decode dispatches by hardware architecture: single-core mode prepares source/destination buffers, copies a local VSI to firmware, sends `vpu_dec_start`, waits for core IRQ, sends `vpu_dec_end`, copies firmware state back, and updates probability/reference metadata. LAT mode initializes `vdec_msg_queue`, dequeues a LAT buffer, builds per-frame context from the VP9 V4L2 control, starts LAT firmware, updates UBE write pointer, and queues the LAT buffer for core work. Core work obtains a capture buffer, resolves reference VB2 buffers by timestamps, invokes `vpu_dec_core`, waits for core IRQ, updates UBE read pointer, and hands the capture buffer to display or marks it failed.

State and persistence behavior: state is per V4L2 context except `vdec_vp9_slice_default_frame_ctx`, which is process-global and protected by `vdec_vp9_slice_frame_ctx_lock`. Per-instance state tracks sequence number, resolution class, last frame dimensions/type/show flag, DPB dimensions indexed by VB2 buffer index, dirty VP9 frame contexts, and allocated DMA work buffers. Working buffers are reallocated when resolution class changes between FHD and 4K and freed on deinit. Flush waits for LAT buffers to drain when split hardware is active, then resets firmware.

Dependencies and integration points: depends on V4L2 stateless VP9 controls, VP9 probability adaptation helpers, vb2 DMA-contig addresses, MediaTek firmware mapping/IPI, vcodec interrupt wait helpers, and `vdec_msg_queue` for LAT/core transfer. Integration with userspace is indirect through the decoder framework dispatch in `vdec_drv_if.c` and the platform decode callbacks in `ctx->dev->vdec_pdata`.

Risks: tile parsing reads bitstream bytes directly and must maintain bounds for malformed sizes; probability/count table layout must match firmware and kernel VP9 helper structures exactly; global default context lifetime is never freed, intentionally shared but risky for module unload expectations; LAT/core buffer reallocation comments depend on flush/drain ordering; UBE pointer math mixes offsets and DMA base addresses and is sensitive to firmware conventions; reference lookup by request timestamp can fall back to zeroed refs if userspace provides missing references.

Test signals: exercise stateless VP9 decode on single-core and LAT/core SoCs, key/intra/inter frames, frame-context reset modes, frame-parallel and non-frame-parallel adaptation, multi-tile streams including max 4x64 bounds, resolution class changes, malformed/truncated tiles, flush/seek, missing references, and timeout/full UBE paths. Useful instrumentation is IRQ status, `state.full`, `state.timeout`, UBE read/write pointers, CRC debug output, and V4L2 mem2mem capture completion flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec/vdec_vp9_req_lat_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_drv_base.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_drv_base.h

Purpose: defines the common decoder backend vtable used by codec-specific MediaTek decoder implementations. It gives the generic decoder layer a uniform contract for initialization, decode, parameter query, and teardown.

Important APIs/types/functions: the only exported type is `struct vdec_common_if` with callbacks `init`, `decode`, `get_param`, and `deinit`. Callback signatures use `struct mtk_vcodec_dec_ctx`, `struct mtk_vcodec_mem`, `struct vdec_fb`, and `enum vdec_get_param_type` from the decoder interface headers.

Control flow: no runtime flow exists in the header. Implementations such as the VP9 LAT backend populate a constant `vdec_common_if`; `vdec_drv_if.c` selects the correct table based on FourCC and invokes callbacks while managing hardware power/current context.

State and persistence behavior: the header owns no state. It defines that implementations store opaque backend state in `ctx->drv_handle` after `init`, use it during `decode`/`get_param`, and release it during `deinit`.

Dependencies and integration points: includes `vdec_drv_if.h` and is included by dispatcher and codec files. It is an internal ABI between generic V4L2 decoder code and codec-specific hardware/firmware drivers.

Risks: callback contract comments mention an output handle for `init`, but the actual signature only returns status and relies on `ctx->drv_handle`; implementations must remain consistent. Because the vtable has no capability flags, dispatch logic must know which callback table is valid for each format and hardware architecture.

Test signals: compile coverage should catch signature drift. Runtime validation comes from opening each supported decoder format and verifying `vdec_if_init`, decode, param query, and deinit route to the expected backend without null callback or stale `drv_handle` use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_drv_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_drv_if.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_drv_if.c

Purpose: generic decoder dispatch layer. It maps V4L2 compressed formats to codec-specific `vdec_common_if` tables, handles hardware enable/disable around backend calls, validates DMA alignment for decode buffers, and serializes parameter queries.

Important APIs/types/functions: public functions are `vdec_if_init`, `vdec_if_decode`, `vdec_if_get_param`, and `vdec_if_deinit`. `vdec_if_init` selects backends including H.264, VP8, VP9, HEVC, AV1, and multi-core/LAT variants. `vdec_if_decode` validates 64-byte bitstream alignment and 512-byte frame-buffer plane alignment before invoking `ctx->dec_if->decode`.

Control flow: init chooses `ctx->dec_if` and `ctx->hw_id` based on FourCC plus platform hardware architecture and subdev support, powers the selected block, calls backend init, then disables hardware. Decode checks optional bitstream and framebuffer alignment, rejects missing `drv_handle`, powers hardware, installs current context for IRQ routing, calls backend decode, clears current context, and powers down. Get-param requires a driver handle and wraps backend query in `mtk_vdec_lock`. Deinit powers hardware, calls backend deinit, powers down, and clears `ctx->drv_handle`.

State and persistence behavior: this layer mutates `ctx->dec_if`, `ctx->hw_id`, and `ctx->drv_handle` indirectly through backend init/deinit. It does not persist buffers itself, but controls when hardware context is active and visible to interrupt handlers.

Dependencies and integration points: depends on format constants, MediaTek decoder platform data, hardware power helpers, current-context routing, and backend symbols declared in `vdec_drv_if.h`. It is the key integration point between the V4L2 decoder frontend and codec backend implementations.

Risks: wrong FourCC-to-backend mapping can select incompatible firmware ABI or hardware block. Alignment checks reject only provided buffers, so header-only/flush calls rely on backend handling. Init/deinit power sequencing assumes backend init/deinit may touch hardware even when most firmware state is remote. Hardware ID selection for LAT architectures must match interrupt and queue routing.

Test signals: verify each advertised decode FourCC initializes on each compatible SoC data path, including subdev-supported H.264 and LAT VP9/AV1. Negative tests should cover unsupported FourCC, uninitialized decode, misaligned bitstream/framebuffer DMA, and deinit after partial init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_drv_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_drv_if.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_drv_if.h

Purpose: declares the decoder interface used by generic V4L2 decoder code and codec-specific backends. It also defines frame-buffer status values and parameter-query types shared across decoder implementations.

Important APIs/types/functions: `enum vdec_fb_status` marks normal/display/free buffer states. `enum vdec_get_param_type` includes display/free frame buffer, picture info, crop info, and DPB size queries. `struct vdec_fb_node` links `vdec_fb` instances into state lists. The header declares all backend `vdec_common_if` instances and public dispatcher functions.

Control flow: this file has no implementation flow, but its declarations define the expected sequence: `vdec_if_init` after format selection, repeated `vdec_if_decode`, optional `vdec_if_get_param`, and `vdec_if_deinit` during teardown. Passing `bs == NULL` to decode is documented as flush/end-of-stream behavior.

State and persistence behavior: state is represented by caller-owned `mtk_vcodec_dec_ctx`, backend-owned `drv_handle`, and frame-buffer lists using `vdec_fb_node`. Query comments explicitly state that returned display/free buffers are not owned by the caller and remain valid only until decoder deinit.

Dependencies and integration points: includes `mtk_vcodec_dec.h`, depends on `struct vdec_common_if` from the base header for backend symbols, and is consumed by decoder frontend, codec backends, and VPU interface code.

Risks: ownership comments are important because misuse of returned frame buffers can cause use-after-free or double-free in frontend code. Extending `enum vdec_get_param_type` requires updating all backend switch statements and decoder firmware parameter paths. The `bs == NULL` flush convention must remain consistent across all implementations.

Test signals: compile-time coverage for all declared backend symbols; runtime tests for parameter queries and flush behavior per codec; static analysis for switch exhaustiveness after enum changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_drv_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_ipi_msg.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_ipi_msg.h

Purpose: defines the decoder AP-to-firmware and firmware-to-AP IPI message ABI. These structures are the wire format used by `vdec_vpu_if.c` to initialize, start, end, reset, core-decode, deinitialize, and query decoder firmware instances.

Important APIs/types/functions: `enum vdec_ipi_msgid` reserves AP IDs from `0xA000` and VPU ack IDs from `0xB000`. Message structs include generic command/ack formats, `vdec_ap_ipi_init`, `vdec_ap_ipi_dec_start`, `vdec_vpu_ipi_init_ack`, `vdec_ap_ipi_get_param`, and `vdec_vpu_ipi_get_param_ack`. The ABI supports both legacy `vpu_inst_addr` and ABI v2 `inst_id`.

Control flow: init sends AP init with codec type and AP instance pointer; firmware replies with status, VPU instance address, ABI version, and optional instance ID. Start messages send up to three codec-specific data words. Generic commands are used for end, reset, core, core end, and deinit. Get-param sends request data and param type; firmware returns data interpreted by the VPU interface.

State and persistence behavior: messages carry remote instance identity across calls. The init ack establishes `vpu_inst_addr`, `vdec_abi_version`, and `inst_id`, which persist in `struct vdec_vpu_inst`. Parameter acks update host-side cached sizes such as frame-buffer plane sizes.

Dependencies and integration points: included by decoder firmware interface and codec backends that rely on firmware-managed VSI memory. The layout must match firmware compiled for MediaTek VPU/SCP, including 32-bit firmware expectations and 64-bit AP pointers.

Risks: any field reorder, width change, or enum renumbering breaks firmware compatibility. ABI version handling is chip-dependent: MT8173 VPU lacks valid version fields, while SCP firmware uses them. Data arrays are small and call sites must enforce bounds. Misspelled/ambiguous comments do not affect behavior but can hide ABI assumptions.

Test signals: IPI init/start/reset/get-param smoke tests with both legacy and ABI v2 firmware; negative tests for unsupported ABI versions; build checks on 32-bit and 64-bit kernels to catch padding/layout assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_ipi_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_msg_queue.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_msg_queue.c

Purpose: implements the LAT-to-core message queue used by MediaTek split decoder architectures. It allocates reusable LAT buffers, tracks UBE transfer-buffer read/write pointers, schedules core decode work, and coordinates flush completion.

Important APIs/types/functions: public functions are `vdec_msg_queue_init_ctx`, `vdec_msg_queue_qbuf`, `vdec_msg_queue_dqbuf`, `vdec_msg_queue_update_ube_rptr`, `vdec_msg_queue_update_ube_wptr`, `vdec_msg_queue_wait_lat_buf_full`, `vdec_msg_queue_deinit`, and `vdec_msg_queue_init`. Static helpers choose list heads, update atomic list counts, wait for LAT buffers, and run `vdec_msg_queue_core_work`.

Control flow: initialization sets up LAT and core queue contexts, allocates a WDMA/UBE buffer sized by resolution, creates three `vdec_lat_buf` objects with error/slice buffers and optional AV1 buffers, allocates codec-private per-buffer data, and enqueues all buffers to LAT availability. LAT backends dequeue from `lat_ctx`, fill a buffer, then queue to `core_ctx`. Core queueing schedules `core_work`; the worker dequeues one core buffer, runs its codec `core_decode` callback under core hardware power/current context, then returns it to LAT availability. Flush inserts an `empty_lat_buf` sentinel and waits for `flush_done`.

State and persistence behavior: queue state lives in `struct vdec_msg_queue` embedded in the decoder context. It persists allocated DMA memory, ready lists, atomic LAT/core counts, WDMA read/write DMA addresses, status flags, and a waitqueue for flush completion. Deinit frees all buffers and cancels pending work if initialized.

Dependencies and integration points: depends on kthread/freezer headers, workqueues, spinlocks, waitqueues, MediaTek decoder power helpers, and codec-specific core callbacks. VP9/AV1 LAT backends use the transfer pointers and private payloads to bridge LAT and core phases.

Risks: queue counters and lists must stay consistent across error paths or LAT buffers can leak from the pool. Core work only processes one buffer per invocation and reschedules based on `core_list_cnt`, so races around `CONTEXT_LIST_QUEUED` matter. Flush waits unbounded after queuing the sentinel. WDMA size is chosen from current `picinfo`, so stale dimensions can undersize large streams. Deinit must not race with active core work or freed private data.

Test signals: run split decode with multiple queued frames, backpressure, flush while core work is active, AV1 allocation path, allocation failures at each buffer, and repeated init/deinit. Trace `lat_list_cnt`, `core_list_cnt`, `ready_num`, `status`, and UBE pointers for stuck or duplicated buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_msg_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_msg_queue.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_msg_queue.h

Purpose: declares the data structures and public API for MediaTek decoder LAT/core message queues.

Important APIs/types/functions: `NUM_BUFFER_COUNT` fixes the LAT pool at three buffers. `core_decode_cb_t` is the codec-specific callback executed by core work. `enum core_ctx_status` tracks empty, queued, and decode-done status. `struct vdec_msg_queue_ctx` models one hardware queue. `struct vdec_lat_buf` carries per-frame LAT output, V4L2 timestamp/request metadata, codec-private data, list nodes, and the core callback. `struct vdec_msg_queue` owns the buffer pool, WDMA/UBE pointers, work item, counts, flush sentinel, waitqueue, and decoder context pointer.

Control flow: callers initialize the queue once, dequeue available LAT buffers from `lat_ctx`, enqueue completed LAT buffers to `core_ctx`, and use read/write pointer update functions to synchronize UBE consumption. Core work returns buffers to `lat_ctx` after callback completion. Deinit releases all queue resources.

State and persistence behavior: all state is per decoder context and persists across frames. The `src_buf_req` media request and `ts_info` timestamp snapshot are stored in `vdec_lat_buf` so core completion can preserve userspace buffer metadata even though decode is split across hardware stages.

Dependencies and integration points: depends on Linux lists, waitqueues, spinlocks, VB2 V4L2 buffers, MediaTek decoder memory structs, and codec-specific callbacks. It is shared by stateless LAT backends such as VP9 and AV1.

Risks: the fixed three-buffer pool constrains throughput and is assumed by flush logic. `private_data` is untyped, so caller and callback must agree on size and layout. List heads for LAT/core are embedded in the same buffer, so a buffer must never be enqueued to both contexts simultaneously. Media requests stored in `src_buf_req` must remain valid until core completion.

Test signals: static checks for correct private size at queue initialization; runtime tests for list/counter balance under decode, EAGAIN, errors, and flush; V4L2 request API tests verifying metadata propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_msg_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_vpu_if.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_vpu_if.c

Purpose: implements decoder firmware/VPU communication for MediaTek vcodec backends. It registers IPI handlers, sends decoder commands, maps firmware VSI memory, validates AP instance pointers, and caches firmware-returned state.

Important APIs/types/functions: exported functions are `vpu_dec_init`, `vpu_dec_start`, `vpu_dec_get_param`, `vpu_dec_core`, `vpu_dec_end`, `vpu_dec_core_end`, `vpu_dec_deinit`, and `vpu_dec_reset`. Key internal handlers are `vpu_dec_ipi_handler`, `handle_init_ack_msg`, `handle_get_param_msg_ack`, `vcodec_vpu_send_msg`, and `vcodec_send_ap_ipi`.

Control flow: init sets the waitqueue, stores the AP `vdec_vpu_inst` on the decoder context, registers the IPI handler for LAT and optionally core IDs, sends init, and expects the handler to map remote VSI memory. Generic command sending chooses LAT or core IPI ID for LAT single-core architecture, fills legacy address or ABI v2 instance ID, sends via `mtk_vcodec_fw_ipi_send`, and returns firmware status. The interrupt-context handler validates that the AP instance still belongs to a live decoder context and that the message ID is in range, handles init/get-param acks, stores failure status, and marks the instance signaled.

State and persistence behavior: `struct vdec_vpu_inst` retains remote VSI pointer, remote instance address, firmware ABI version, instance ID, failure status, codec type, and framebuffer sizes. The handler writes these fields asynchronously during IPI callbacks. The context’s `vpu_inst` pointer is used as a liveness guard.

Dependencies and integration points: depends on `mtk_vcodec_fw_*` abstraction for VPU/SCP transport, decoder context lists guarded by `dev_ctx_lock`, message layouts from `vdec_ipi_msg.h`, and codec backends that copy data into mapped VSI memory before sending commands.

Risks: `signaled` and `wq` are initialized but this layer relies on synchronous `mtk_vcodec_fw_ipi_send` semantics rather than explicitly waiting here. AP instance pointers arrive from firmware, so liveness validation is critical. Unsupported ABI versions set failure but callers must propagate it. Core/LAT IPI routing depends on accurate platform architecture flags.

Test signals: firmware init with VPU and SCP transports, ABI v1/v2 handling, invalid ACK ID and stale AP instance injection, get-param picture info updates, core command routing on LAT single-core hardware, and timeout/failure propagation from `mtk_vcodec_fw_ipi_send`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_vpu_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_vpu_if.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_vpu_if.h

Purpose: declares the host-side decoder VPU instance and command API used by codec-specific decoder backends.

Important APIs/types/functions: `struct vdec_vpu_inst` records IPI IDs, shared VSI pointer, firmware failure status, legacy remote address, ABI version, ABI v2 instance ID, signal flag, decoder context, waitqueue, IPI handler, codec/capture type, and frame-buffer sizes. Public commands cover init, start, end, deinit, reset, core/core-end, and get-param.

Control flow: codec backends allocate or embed `vdec_vpu_inst`, fill IDs/context/codec type, call `vpu_dec_init`, exchange data through `vpu->vsi`, then issue start/end/reset/get-param commands as frames are decoded. LAT/core codecs additionally call `vpu_dec_core` and `vpu_dec_core_end`.

State and persistence behavior: one `vdec_vpu_inst` persists per decoder instance and is the anchor for remote firmware state. It stores both AP-visible status and firmware-visible identity. `fb_sz` is populated by get-param acknowledgements and consumed by picture-info query paths.

Dependencies and integration points: depends on `struct mtk_vcodec_dec_ctx` and the common firmware IPI handler type. It is included by decoder backends and the VPU interface implementation.

Risks: callers must not use `vsi` before successful init or after deinit. ABI version and instance ID rules differ between old VPU firmware and newer SCP firmware. The waitqueue/signal fields can imply asynchronous waiting, but actual synchronization is in the firmware abstraction.

Test signals: backend init/deinit tests should assert `vsi` validity and `ctx->vpu_inst` setup; ABI v2 tests should confirm commands use `inst_id`; get-param tests should confirm `fb_sz` is updated before picture-info consumers read it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_vpu_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/Makefile -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/Makefile

Purpose: defines the objects linked into the MediaTek vcodec encoder module when `CONFIG_VIDEO_MEDIATEK_VCODEC` is enabled.

Important APIs/types/functions: no C API is defined. The build target is `mtk-vcodec-enc.o`, composed from VP8 and H.264 codec backends, V4L2 encoder frontend/driver files, power management, encoder dispatch, and VPU transport.

Control flow: Kbuild compiles listed objects into one module object. Link order ensures backend symbols such as `venc_vp8_if` and `venc_h264_if` are available to `venc_drv_if.o` and frontend code.

State and persistence behavior: build-only file with no runtime state.

Dependencies and integration points: tied to kernel Kbuild, the parent MediaTek vcodec Kconfig, and the source files in the encoder directory. Adding a new encoder backend requires updating this object list and dispatch logic.

Risks: missing objects cause unresolved symbols or unavailable formats. The trailing backslash after `venc_vpu_if.o` is tolerated by Kbuild in this context but is a style footgun when appending lines. Conditional per-codec builds are not present, so all listed encoder backends build together under the shared config.

Test signals: kernel build with `CONFIG_VIDEO_MEDIATEK_VCODEC=m/y`, link checks for H.264 and VP8 backend symbols, and module load smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc.c

Purpose: implements the V4L2 mem2mem encoder frontend: controls, format negotiation, VB2 queue operations, encoder command/flush handling, workqueue-driven encode jobs, and default per-context parameters.

Important APIs/types/functions: exports `mtk_venc_ioctl_ops`, `mtk_venc_m2m_ops`, `mtk_vcodec_enc_queue_init`, `mtk_vcodec_enc_ctrls_setup`, `mtk_vcodec_enc_set_default_params`, `mtk_venc_lock`, `mtk_venc_unlock`, and `mtk_vcodec_enc_release`. Core internal paths include control setter `vidioc_venc_s_ctrl`, format helpers, queue setup/prepare/start/stop, `mtk_venc_encode_header`, `mtk_venc_param_change`, and `mtk_venc_worker`.

Control flow: userspace sets formats and controls through V4L2 ioctls. Capture format selection initializes the codec backend with `venc_if_init`. Start-streaming waits until both output and capture queues are active, translates V4L2 params into `venc_enc_param`, sends `VENC_SET_PARAM_ENC`, and for H.264 joined-header mode requests header prepending. The m2m scheduler calls `device_run`; H.264 may first emit SPS/PPS into a capture buffer, then queue encode work. The worker removes source/destination buffers, handles the synthetic flush source buffer, maps DMA addresses into `venc_frm_buf`/`mtk_vcodec_mem`, calls `venc_if_encode`, propagates timestamps/keyframe flags, completes buffers, and finishes the m2m job.

State and persistence behavior: per-context state includes source/capture `q_data`, colorspace fields, encoder params, state machine (`FREE`, `INIT`, `HEADER`, `ABORT`), latched `param_change`, an ordered `encode_work`, and a synthetic `empty_flush_buf`. Parameter changes are copied into `mtk_video_enc_buf` at source-buffer queue time so changes apply to a specific frame. `is_flushing` persists until the zero-payload LAST capture buffer is dequeued or streamoff clears it.

Dependencies and integration points: integrates with V4L2 controls/ioctls/events, v4l2-mem2mem scheduling, videobuf2 DMA-contig, codec dispatch in `venc_drv_if.c`, and platform capabilities from `mtk_vcodec_enc_drv.c`.

Risks: `mtk_venc_worker` intentionally avoids `dev_mutex`, so it races with ioctls and must only touch state protected by queue/m2m semantics. Format size calculations must match hardware alignment and userspace buffer sizes. Flush handling depends on recognizing the synthetic source buffer and zero-payload LAST capture buffer. Some controls are accepted but not fully enforced by firmware paths, such as B-frame count.

Test signals: v4l2-compliance for mem2mem encoders, H.264 header separate/joined modes, STOP/START encoder commands, streamoff during flush, dynamic bitrate/framerate/GOP/force-keyframe changes, unsupported bitrate mode, buffer too small, 4K capability frame sizes, and abort-state behavior after backend errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc.h

Purpose: declares encoder frontend constants and helper APIs shared between the encoder platform driver and V4L2 frontend implementation.

Important APIs/types/functions: defines encoder IRQ status bits and register offsets for status/acknowledge. `struct mtk_video_enc_buf` extends `v4l2_m2m_buffer` with per-buffer parameter-change flags and a snapshot of `mtk_enc_params`. It declares V4L2 ioctl/m2m operation tables plus lock, queue initialization, release, control setup, and default-parameter functions.

Control flow: source VB2 buffers are allocated with `struct mtk_video_enc_buf` as private storage, allowing `vb2ops_venc_buf_queue` to latch pending control changes onto the specific frame before m2m scheduling.

State and persistence behavior: per-buffer state persists from QBUF until the encode worker consumes the source buffer. IRQ constants are stateless register ABI definitions used by the IRQ handler and codec backends waiting for SPS/PPS/frame completion.

Dependencies and integration points: includes videobuf2 and V4L2 mem2mem headers plus `mtk_vcodec_enc_drv.h`. Consumed by `mtk_vcodec_enc.c`, `mtk_vcodec_enc_drv.c`, and codec backend files.

Risks: IRQ bit definitions must match hardware across supported SoCs. Per-buffer parameter snapshots can become stale if controls are changed after QBUF, but that is the intended frame-specific behavior and should be documented in userspace expectations.

Test signals: buffer queue tests for parameter-change latching; IRQ register tests on hardware confirming SPS/PPS/frame bits are acknowledged correctly; compile checks after modifying `mtk_enc_params`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_drv.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_drv.c

Purpose: platform driver for the MediaTek V4L2 encoder device. It probes hardware resources, registers the V4L2 mem2mem video device, owns context lifetime, handles encoder IRQs, and provides SoC-specific encoder pdata.

Important APIs/types/functions: key functions are `mtk_vcodec_probe`, `mtk_vcodec_enc_remove`, `fops_vcodec_open`, `fops_vcodec_release`, and `mtk_vcodec_enc_irq_handler`. Static format tables advertise raw output formats and H.264/VP8 capture formats. Pdata structs describe supported formats, bitrate limits, core ID, extended messaging, and 34-bit IOVA support for MT8173/MT8183/MT8188/MT8192/MT8195.

Control flow: probe allocates device state, selects VPU or SCP firmware transport from device-tree phandles, initializes clocks/runtime PM, maps registers, requests IRQ with `IRQ_NOAUTOEN`, registers V4L2 device/video node, initializes m2m device and ordered encode workqueue, and registers debugfs. Open allocates a context, initializes controls, m2m queues, defaults, loads firmware on first file handle, caches encoder capability, and links the context into `ctx_list`. Release tears down m2m context/backend, V4L2 file handle, controls, cancels pending encode work, removes from context list, and frees the context.

State and persistence behavior: device state persists across opens and includes `ctx_list`, `curr_ctx` for IRQ routing, mapped register bases, firmware handler, workqueue, mutexes/spinlocks, runtime PM state, and capabilities. Per-open context state is added to `ctx_list` for VPU IPI liveness validation. IRQ handler reads current context under `irqlock`, reads/cleans hardware IRQ status, and wakes the waiting context.

Dependencies and integration points: integrates with platform device resources/device-tree compatibles, firmware abstraction, runtime PM, v4l2-device/video-device registration, v4l2-mem2mem, VB2 DMA-contig, debugfs, and codec frontend ops from `mtk_vcodec_enc.c`.

Risks: IRQ handler assumes a valid `curr_ctx`; invalid core ID is checked but null context paths can still be sensitive. Probe error paths must match allocated resources; `pm_runtime_disable(dev->pm.dev)` depends on PM init setting `dev->pm.dev`. Release cancels work after m2m release to avoid a known use-after-free. SoC pdata must match firmware and register core IDs exactly.

Test signals: probe/remove on each compatible, open/close stress with active queued jobs, firmware-load failure handling, IRQ delivery for SPS/PPS/frame, runtime PM balance, workqueue cancellation under close, and advertised bitrate/format capabilities per SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_drv.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_drv.h

Purpose: central encoder driver header defining SoC pdata, per-context state, per-device state, inline helpers, and logging macros.

Important APIs/types/functions: `struct mtk_vcodec_enc_pdata` carries SoC capabilities including extended firmware messaging and 34-bit IOVA. `enum mtk_encode_param` flags dynamic control changes. `struct mtk_enc_params` holds user-visible encoder settings. `struct mtk_vcodec_enc_ctx` represents one V4L2 file/m2m instance. `struct mtk_vcodec_enc_dev` represents the platform encoder device. Inline helpers map file/control objects to contexts and wake interrupt waitqueues.

Control flow: this header shapes how open creates a context, how queue code stores parameters, how codec backends find device registers/firmware, and how IRQ handlers wake backends waiting in `mtk_vcodec_wait_for_done_ctx`.

State and persistence behavior: context state persists for an open file and includes queue data, backend vtable/handle, interrupt condition arrays, controls, work item, flush state, colorspace metadata, queue mutex, and VPU instance pointer. Device state persists for the platform device and includes V4L2/m2m handles, resource mappings, context list, current context, locks, IRQ, PM, capabilities, and debugfs.

Dependencies and integration points: includes common MediaTek vcodec driver, debugfs, firmware, and utility headers. It is included by nearly every encoder source file and defines the internal state contract.

Risks: broad shared state increases coupling between frontend, platform driver, VPU transport, and codec backends. `curr_ctx` plus waitqueue arrays must be indexed consistently by hardware ID. Pdata macros hide SoC behavior in backend code, so adding new SoC quirks requires careful propagation.

Test signals: compile coverage across all encoder files after state layout changes; multi-instance open/close stress; IRQ wait/wake tests; dynamic parameter tests confirming `param_change` flags map to backend commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_pm.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_pm.c

Purpose: implements encoder power-management helpers for clock discovery, runtime PM power on/off, and clock enable/disable.

Important APIs/types/functions: exported helpers are `mtk_vcodec_init_enc_clk`, `mtk_vcodec_enc_pw_on`, `mtk_vcodec_enc_pw_off`, `mtk_vcodec_enc_clock_on`, and `mtk_vcodec_enc_clock_off`.

Control flow: clock init counts `clock-names`, allocates an array of `mtk_vcodec_clk_info`, reads each clock name, and obtains a managed clock handle. Encode dispatch powers on with `pm_runtime_resume_and_get`, enables all clocks in order before backend encode, disables clocks in reverse order afterward, and releases runtime PM with `pm_runtime_put`.

State and persistence behavior: discovered clocks are stored in `dev->pm.venc_clk` for the platform device lifetime. Runtime PM reference state is maintained by the PM core; this file does not track a separate refcount.

Dependencies and integration points: depends on device-tree `clock-names`, Linux clk API, runtime PM, and common `mtk_vcodec_pm` structures. Called by platform probe and `venc_if_encode`.

Risks: `mtk_vcodec_enc_clock_on` returns void, so clock-enable failures are logged but not propagated to encode callers. Partial clock-enable rollback is handled locally. Runtime PM failure is propagated by `mtk_vcodec_enc_pw_on`; callers must avoid enabling clocks when it fails.

Test signals: probe with missing/malformed clock names, encode path runtime PM balance, fault injection for `clk_prepare_enable`, and suspend/resume or repeated stream start/stop cycles checking no clock remains enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_pm.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_pm.h

Purpose: declares encoder power-management helper functions.

Important APIs/types/functions: prototypes cover encoder clock initialization, runtime power on/off, and clock on/off. The header includes `mtk_vcodec_enc_drv.h` to access encoder device and common PM types.

Control flow: no implementation flow. The platform driver calls clock init during probe, and encode dispatch calls power/clock helpers around hardware encode operations.

State and persistence behavior: no state is owned by the header; functions operate on `struct mtk_vcodec_enc_dev` and `struct mtk_vcodec_pm` owned elsewhere.

Dependencies and integration points: shared between platform driver, encoder dispatch, and any future encoder code needing power control.

Risks: clock-on/off prototypes returning void make it impossible for callers to react to clock enable failures unless the API changes. Include dependency on the full driver header may increase recompilation/coupling.

Test signals: compile checks and runtime encode tests that verify the PM helpers are called in balanced pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc/venc_h264_if.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc/venc_h264_if.c

Purpose: codec-specific H.264 encoder backend for MediaTek hardware/firmware. It implements the `venc_common_if` contract, translates V4L2 H.264 parameters into firmware VSI configuration, manages firmware-described work buffers, emits SPS/PPS, encodes frames, and handles optional header prepending.

Important APIs/types/functions: exports `venc_h264_if`. Important types include H.264 frame/bitstream/work-buffer enums, standard and extended/34-bit VSI structs, and `struct venc_h264_inst`. Major functions include profile/level mapping, work-buffer alloc/free, SPS/PPS/header encode, frame encode, filler insertion, init, encode, set-param, and deinit.

Control flow: init allocates an instance, selects IPI ID based on extended firmware use, maps H.264 register base, calls `vpu_enc_init`, and stores the mapped VSI pointer as 32-bit or 34-bit layout. `VENC_SET_PARAM_ENC` populates VSI config, sends firmware set-param, reallocates all work buffers from firmware-provided sizes, maps/copies special RC_CODE and SKIP_FRAME buffers, and marks buffers allocated. Encode enables IRQ, handles sequence-header or frame options, sends VPU encode commands for SPS/PPS/frame, waits for expected IRQ status, reads bitstream byte count, and returns size/keyframe metadata. Prepend mode emits header, adds alignment filler if needed, then encodes the frame into the remaining bitstream buffer.

State and persistence behavior: per-instance state tracks work buffers, PPS scratch buffer, frame count, skipped frame count, prepend-header flag, VPU instance, VSI pointers, and context. Frame counters reset on force-intra/GOP/intra-period changes. Work buffers persist until reconfiguration or deinit.

Dependencies and integration points: depends on encoder VPU transport, hardware IRQ wait helpers, register base mapping, memory allocation helpers, frontend control translation, and SoC pdata flags for extended ABI and 34-bit IOVA.

Risks: firmware VSI layout and work-buffer semantics must match SoC firmware. 34-bit and 32-bit paths must stay behaviorally aligned. Prepend-header alignment/filler math can underflow available bitstream size if capture buffers are too small. Skip-frame handling copies firmware memory directly to userspace bitstream buffer. Unsupported profile/level values log and may map to defaults or zero.

Test signals: H.264 encode with separate and joined headers, IDR/I/P frame cadence, force-keyframe and GOP/intra-period changes, bitrate/framerate updates, skip-frame firmware state, 34-bit IOVA SoC, small capture buffers, expected IRQ statuses for SPS/PPS/frame, and work-buffer reallocation after format change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc/venc_h264_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc/venc_vp8_if.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc/venc_vp8_if.c

Purpose: codec-specific VP8 encoder backend implementing `venc_common_if` for MediaTek VP8 hardware/firmware.

Important APIs/types/functions: exports `venc_vp8_if`. It defines VP8 work-buffer indexes, firmware config/buffer/VSI structs, and `struct venc_vp8_inst`. Important helpers allocate/free firmware-described work buffers, wait for frame IRQ, compose a final VP8 frame bitstream, initialize, encode, set params, and deinitialize.

Control flow: init allocates an instance, sets IPI ID to `IPI_VENC_VP8`, maps VP8 encoder register base, initializes firmware, and stores the mapped VSI. `VENC_SET_PARAM_ENC` writes input format, bitrate, visible/coded dimensions, GOP size, framerate, and temporal scalability mode into VSI, sends firmware set-param, then allocates AP work buffers and copies firmware-resident RC code buffers into DMA memory. Encode only supports normal frame encoding: enables IRQ, sends `vpu_enc_encode`, waits for `MTK_VENC_IRQ_STATUS_FRM`, then composes final VP8 output by prepending the uncompressed frame tag and firmware-generated header before the hardware payload.

State and persistence behavior: per-instance state tracks work buffers, allocation flag, frame count, temporal scalability mode, VPU instance, VSI pointer, and context. Work buffers persist until reconfiguration or deinit. `frm_cnt` increments after successful frame composition.

Dependencies and integration points: integrates with frontend `venc_if_*` dispatch, VPU IPI transport, hardware IRQ wait helpers, register reads for frame/header length, and firmware memory mapping for RC buffers.

Risks: `vp8_enc_compose_one_frame` moves data in-place inside the capture bitstream buffer; incorrect length registers or insufficient buffer size can corrupt output and is guarded only by size check. VP8 keyframe tag fields use visible dimensions from VSI and must be little-endian byte split. Temporal scalability mode must be set before encoder params to be included. Unlike H.264, no 34-bit IOVA path is present here.

Test signals: VP8 keyframe and inter-frame output inspection, small capture-buffer rejection, temporal scalability mode setup before stream start, RC_CODE buffer copy, frame IRQ timeout/error, repeated parameter reconfiguration, and deinit after partial allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc/venc_vp8_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_drv_base.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_drv_base.h

Purpose: defines the common encoder backend vtable used by codec-specific H.264 and VP8 implementations.

Important APIs/types/functions: `struct venc_common_if` contains `init`, `encode`, `set_param`, and `deinit` callbacks. The encode callback accepts `enum venc_start_opt`, optional input frame buffer, output bitstream buffer, and `venc_done_result`.

Control flow: `venc_drv_if.c` selects a `venc_common_if` by capture FourCC, initializes the backend, and routes parameter and encode calls through this table while managing locks, power, clocks, and current IRQ context.

State and persistence behavior: this header owns no state. Backend init stores an opaque codec instance in `ctx->drv_handle`; deinit frees it.

Dependencies and integration points: includes encoder context definitions and `venc_drv_if.h`. It is the internal ABI between the generic encoder dispatch layer and codec-specific files.

Risks: callback signatures encode assumptions about synchronous encode completion and a single output result structure. Adding asynchronous or multi-part bitstream behavior would require extending this interface.

Test signals: compile/link coverage for all backend vtables and runtime smoke tests selecting H.264 and VP8 capture formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_drv_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_drv_if.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_drv_if.c

Purpose: generic encoder backend dispatcher. It selects codec-specific backends, serializes hardware access with the encoder mutex, manages runtime PM/clocks around encode, and routes deinit/parameter calls.

Important APIs/types/functions: public functions are `venc_if_init`, `venc_if_set_param`, `venc_if_encode`, and `venc_if_deinit`.

Control flow: init selects VP8 or H.264 backend by capture FourCC and calls backend init under `mtk_venc_lock`. Set-param calls backend `set_param` under the same lock. Encode locks, installs `ctx` as `dev->curr_ctx` under `irqlock`, powers on runtime PM, enables clocks, invokes backend encode, disables clocks/power, clears `curr_ctx`, and unlocks. Deinit no-ops if `drv_handle` is null, otherwise calls backend deinit under lock and clears the handle.

State and persistence behavior: manages `ctx->enc_if`, `ctx->drv_handle`, and `dev->curr_ctx`. It does not own codec buffers but defines the active hardware window during which IRQs are routed to the current context.

Dependencies and integration points: depends on encoder frontend lock helpers, PM helpers, codec vtables, and platform IRQ handler. It bridges V4L2 m2m worker code to backend firmware/hardware operations.

Risks: `mtk_vcodec_enc_clock_on` failures are not propagated, so backend encode may run after a logged clock-enable failure. If power-on fails, `curr_ctx` is not cleared before the goto label in the current code path, which can leave stale IRQ routing until a later encode clears it. The single encoder mutex serializes instances and may limit concurrency but protects shared hardware.

Test signals: H.264/VP8 init with unsupported FourCC, PM failure injection, encode timeout/error propagation, concurrent contexts contending for `enc_mutex`, and IRQ routing validation using `curr_ctx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_drv_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_drv_if.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_drv_if.h

Purpose: declares encoder dispatch APIs and shared parameter/result structures used between the V4L2 encoder frontend, dispatch layer, VPU transport, and codec backends.

Important APIs/types/functions: defines firmware-sensitive enums `venc_yuv_fmt`, `venc_start_opt`, and `venc_set_param_type`; structs `venc_enc_param`, `venc_frame_info`, `venc_frm_buf`, and `venc_done_result`; backend symbols `venc_h264_if` and `venc_vp8_if`; and dispatcher functions.

Control flow: the frontend converts V4L2 formats/controls into `venc_enc_param`, calls `venc_if_set_param`, then encodes sequence headers or frames through `venc_if_encode`. Codec backends pass `venc_frame_info` through the VPU transport for extended firmware paths.

State and persistence behavior: most structures are transient per configuration or per frame, but enum numeric ordering is persistent ABI with firmware. `venc_done_result` carries output bitstream size and keyframe flag back to the V4L2 worker.

Dependencies and integration points: includes encoder context definitions. The comments explicitly warn that YUV format and parameter enum ordering must match VPU code.

Risks: renumbering enums or inserting values breaks firmware. `frm_rate` is an integer FPS derived by callers, losing fractional frame-rate precision. `venc_frm_buf` assumes at most `MTK_VCODEC_MAX_PLANES`.

Test signals: ABI review for enum changes, encode tests for every supported input YUV format, dynamic parameter command tests, and validation that output `bs_size`/keyframe flags match produced bitstreams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_drv_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_ipi_msg.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_ipi_msg.h

Purpose: defines the encoder AP-to-VPU/SCP IPI message ABI for init, set-param, encode, and deinit commands plus firmware acknowledgements.

Important APIs/types/functions: message IDs start at `0xC000` for AP commands and `0xD000` for firmware replies. AP structs include init, set-param, extended set-param, encode, extended encode, 34-bit extended encode, and deinit formats. Reply structs include common, init, set-param, encode, and deinit formats. `enum venc_ipi_msg_enc_state` reports frame/partial/skip/error encode states.

Control flow: init sends AP instance pointer and receives remote VPU instance address plus ABI version. Set-param sends the remote instance address, parameter ID, and optional data words. Encode sends bitstream mode, input plane addresses, output bitstream address/size, and optional frame-info data. Firmware replies update status and, for encode, state, keyframe flag, and bitstream size.

State and persistence behavior: the init reply establishes `vpu_inst_addr` stored in `venc_vpu_inst`. Encode replies update transient per-frame state consumed by H.264/VP8 backends.

Dependencies and integration points: consumed by `venc_vpu_if.c` and codec backends. It must match 32-bit VPU firmware layout while allowing 64-bit AP pointers and 34-bit IOVA variants for newer SoCs.

Risks: struct padding and field widths are ABI-sensitive. The base encode message uses 32-bit DMA addresses, so 34-bit SoCs must take the explicit `_ext_34` path. Extended data arrays have fixed capacity and callers must keep `data_item` consistent with firmware expectations.

Test signals: IPI encode on legacy VPU, SCP extended firmware, and 34-bit IOVA SoCs; skip-frame ack handling; invalid status handling; build layout review when changing any struct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_ipi_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_vpu_if.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_vpu_if.c

Purpose: implements encoder firmware IPI transport for MediaTek vcodec. It registers the encoder IPI handler, validates AP instances, maps firmware VSI memory, sends set-param/encode/deinit messages, and caches encode reply state.

Important APIs/types/functions: exported functions are `vpu_enc_init`, `vpu_enc_set_param`, `vpu_enc_encode`, and `vpu_enc_deinit`. Key helpers include `vpu_enc_ipi_handler`, `handle_enc_init_msg`, `handle_enc_encode_msg`, `vpu_enc_send_msg`, crop/MB calculation helpers, and separate 32-bit/34-bit encode message builders.

Control flow: init registers an IPI handler for the backend-selected ID, sends AP init, and expects an init ack to set `inst_addr` and map `vsi`. Set-param builds base or extended messages; for initial encoder config on extended firmware it sends crop-right, crop-bottom, and macroblock count. Encode validates 16-byte DMA alignment for input planes, chooses 34-bit or 32-bit message format from SoC pdata, includes output bitstream address/size and optional frame info, sends the message, then leaves reply data in `vpu->state`, `bs_size`, and `is_key_frm`. Deinit sends remote instance address.

State and persistence behavior: `venc_vpu_inst` persists per codec instance and stores remote instance address, mapped VSI, last failure, last encode state/size/keyframe, IPI ID, and context. `ctx->vpu_inst` is set for liveness validation against `ctx_list`.

Dependencies and integration points: depends on firmware abstraction, encoder context list locking, ABI structs from `venc_ipi_msg.h`, dispatch structures from `venc_drv_if.h`, and SoC pdata macros for extended and 34-bit paths.

Risks: `vpu_enc_send_msg` treats any firmware failure as `-EINVAL`, losing specific error detail. IPI handler uses firmware-provided AP pointer and must validate it before dereference-sensitive operations. All input planes are checked for 16-byte alignment, including plane slots that may be unused in some formats but are initialized by frontend buffer construction. ABI version support currently accepts only version 1 for non-VPU firmware.

Test signals: init/deinit with stale or invalid AP instance acks, extended set-param values for crop and macroblock count, 16-byte alignment rejection, 34-bit encode messages on MT8188-like pdata, skip/error encode states, and firmware timeout/failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_vpu_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_vpu_if.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_vpu_if.h

Purpose: declares the host-side encoder VPU instance and the VPU command API used by H.264 and VP8 backends.

Important APIs/types/functions: `struct venc_vpu_inst` contains waitqueue, signaling/failure fields, last encode state, bitstream size, keyframe flag, remote instance address, mapped VSI pointer, IPI ID, and V4L2 encoder context. Prototypes cover init, set-param, encode, and deinit.

Control flow: codec backends embed `venc_vpu_inst`, set context and IPI ID, call init, exchange configuration through `vsi`, send parameters/encode commands through this API, and deinit during backend teardown.

State and persistence behavior: one instance persists for the codec backend lifetime. Last encode reply fields are overwritten on each encode ack and consumed immediately by backend code.

Dependencies and integration points: includes `venc_drv_if.h` for shared parameter/frame structures. It is the public internal boundary between codec-specific backends and the IPI implementation.

Risks: `signaled`/waitqueue fields are present but explicit waiting is delegated to the firmware IPI send abstraction; future changes must avoid double-waiting. `bs_size` is an int while ABI field is u32, so very large values would truncate on unusual firmware responses.

Test signals: backend initialization checking non-null `vsi`, encode reply propagation to `venc_done_result`, and deinit when init partially failed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_vpu_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/Kconfig

Purpose: declares the build configuration option for the MediaTek Video Processor Unit driver.

Important APIs/types/functions: `config VIDEO_MEDIATEK_VPU` is a tristate option named "Mediatek Video Processor Unit". It depends on mem2mem V4L2 drivers, video device support, and either MediaTek architecture or compile testing.

Control flow: selecting the option builds the `mtk-vpu` module/built-in driver from the Makefile. The help text describes firmware downloading and VPU communication for MT8173 video codec hardware.

State and persistence behavior: build-time configuration only, no runtime state.

Dependencies and integration points: controls compilation of `drivers/media/platform/mediatek/vpu/mtk_vpu.c`, which exports symbols used by older MediaTek vcodec firmware integration paths.

Risks: dependency coverage must stay aligned with driver includes and exported API users. The help text is MT8173-specific even though surrounding vcodec code may support newer SCP-based paths elsewhere.

Test signals: Kconfig build matrix with option disabled, module, and built-in; COMPILE_TEST on non-MediaTek architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/Makefile -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/Makefile

Purpose: Kbuild file for the MediaTek VPU driver.

Important APIs/types/functions: builds `mtk-vpu.o` from `mtk_vpu.o` when `CONFIG_VIDEO_MEDIATEK_VPU` is enabled.

Control flow: no runtime flow; Kbuild links the single implementation object into the module or built-in image.

State and persistence behavior: build-only file with no runtime state.

Dependencies and integration points: paired with `Kconfig` and `mtk_vpu.c`.

Risks: if additional source files are added to the VPU driver, this Makefile must be updated or symbols will be missing. The module object name must remain aligned with Kconfig help text and module aliases.

Test signals: kernel build with `VIDEO_MEDIATEK_VPU=m/y` and module load check for `mtk-vpu`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/mtk_vpu.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/mtk_vpu.c

Purpose: platform driver and exported service layer for the MT8173 MediaTek Video Processor Unit. It loads program/data firmware, manages VPU clocks/watchdog/extended memory, implements shared-memory IPI send/receive, exposes capability queries and data-memory mapping, and handles suspend/resume.

Important APIs/types/functions: exported symbols include `vpu_ipi_register`, `vpu_ipi_send`, `vpu_wdt_reg_handler`, `vpu_get_vdec_hw_capa`, `vpu_get_venc_hw_capa`, `vpu_mapping_dm_addr`, `vpu_get_plat_device`, and `vpu_load_firmware`. Internal structures model firmware memory, registers, watchdog handlers, init status, IPI descriptors, shared DTCM objects, and `struct mtk_vpu`. Platform entry points include `mtk_vpu_probe`, `mtk_vpu_remove`, suspend/resume, and IRQ handling.

Control flow: probe maps TCM/config registers, obtains and prepares the main clock, creates watchdog workqueue, initializes shared DTCM send/receive buffers, registers the firmware-init IPI handler, configures TCM size, handles 4GB mode/reserved memory, allocates extended data/program memory and programs their physical addresses, initializes waitqueues, and requests IRQ. Firmware loading downloads program and data firmware from new or legacy names into TCM plus extended memory, boots VPU by setting reset, waits for init IPI, and records firmware version/capabilities. IPI send enables the clock, waits for HOST_TO_VPU to clear, copies payload into DTCM send buffer, signals VPU, waits for ack, and disables the clock. IRQ handler dispatches IPC interrupts to registered handlers or schedules watchdog reset work for watchdog events.

State and persistence behavior: device state persists in `struct mtk_vpu`: firmware loaded flag, extmem DMA allocations, IPI descriptors, ack flags, run capabilities/version, watchdog handlers/refcount, 4GB mode, shared buffers, and mutex. Firmware loaded state avoids repeated downloads. Watchdog reset clears reset, marks firmware unloaded, and invokes registered reset callbacks. Suspend waits for VPU idle and disables timer interrupt; resume reenables it.

Dependencies and integration points: uses Linux firmware loader, clk, DMA coherent memory, reserved memory, debugfs, IRQ, platform resources, OF phandles, and exported VPU API consumed by vcodec clients through the common firmware wrapper. Shared memory layout uses DTCM offsets and 48-byte IPI payloads.

Risks: IPI payload size is limited to 48 bytes; callers must use higher-level shared memory for larger data. `vpu_ipi_send` serializes via `vpu_mutex` and busy-waits for command register clearance until timeout. Clock/watchdog refcount balance is critical, especially in IRQ timeout paths. Firmware download uses raw `memcpy` to I/O-mapped TCM memory rather than `memcpy_toio`. 4GB mode adds an address offset and reserved-memory fallback that must match hardware addressing. Watchdog reset invokes client callbacks after firmware is marked unloaded, so clients must tolerate asynchronous reset.

Test signals: firmware load success/failure with new and legacy filenames, init timeout, IPI ack timeout, registered handler dispatch, invalid IPI ID/length, watchdog interrupt and client reset callbacks, suspend while busy/idle, 4GB mode memory programming, debugfs status read, and repeated module probe/remove without DMA or clock leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/mtk_vpu.c -->
