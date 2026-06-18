# subset-b-004168 research

Grouped research report for the requested STMicroelectronics STi BDisp, Delta, and HVA media platform driver files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-hw.c

Purpose: implements the low-level programming path for the STi BDisp 2D blitter. It converts V4L2 mem2mem context state into BDisp linked-list nodes, allocates coherent node/filter memory, resets the engine, acknowledges hardware interrupts, and submits a request to AQ1.

Important APIs and functions: exported entry points are `bdisp_hw_reset`, `bdisp_hw_get_and_clear_irq`, `bdisp_hw_alloc_nodes`, `bdisp_hw_free_nodes`, `bdisp_hw_alloc_filters`, `bdisp_hw_free_filters`, and `bdisp_hw_update`. Internal helpers choose resize filter tables (`bdisp_hw_get_hf_addr`, `bdisp_hw_get_vf_addr`), compute 6.10 scaling increments, derive operation flags in `bdisp_hw_get_op_cfg`, map V4L2 fourcc values to BDisp color encodings, and build one or more `struct bdisp_node` descriptors.

Control flow: probe-time code allocates global horizontal and vertical filter tables from static coefficient arrays. Per-file contexts allocate up to `MAX_NB_NODE` contiguous DMA descriptors. On each job, `bdisp_hw_update` calls `bdisp_hw_build_all_nodes`, saves a debug copy, enables AQ1 last-node interrupts, writes the first node address, then writes the last node address to start processing. Node construction handles source/destination plane count, RGB/YUV conversion matrices, scaling or 4:2:0 chroma resampling, interlaced source half-height handling, flips, target plane selection, and source splitting into up to two vertical strides for widths over 2048 pixels.

State and persistence: persistent driver state is limited to DMA-backed node/filter buffers and the debug copy in `bdisp_dev->dbg`; hardware state lives in MMIO registers and is reset for every run. Filter address arrays are file-static globals shared by all BDisp instances.

Dependencies and integration points: depends on `bdisp.h`, `bdisp-reg.h`, `bdisp-filter.h`, DMA coherent/write-combine allocation, Linux MMIO accessors, V4L2 pixel formats, and the V4L2 mem2mem context maintained by `bdisp-v4l2.c`.

Risks: scaling accepts a wide range but rejects extreme ratios via increment underflow/overflow. The static global filter arrays assume one allocation lifetime and can be risky if multiple devices probe independently. Node math has many chroma/interlace/stride coordinate transformations, so off-by-one and odd-alignment bugs are plausible. `bdisp_hw_save_request` uses `GFP_ATOMIC` devm allocation for debug copies during submission.

Test signals: useful tests are mem2mem conversions among RGB565/RGB24/XBGR/ABGR/NV12/YUV420, scaling up/down, 2048+ width split jobs, hflip/vflip combinations, interlaced output input handling, interrupt timeout paths, and DMA/IOMMU validation that filter and node physical addresses are visible to the blitter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-reg.h

Purpose: defines the hardware-facing BDisp descriptor layout, MMIO register offsets, bit fields, filter table geometry, and hardware color format codes used by `bdisp-hw.c`.

Important APIs and types: `struct bdisp_node` mirrors the BDisp node register groups, including general node chaining, target, color fill, three sources, clipping, filters, matrix conversion, deinterlace, pace, and gradient fields. Register constants cover global control/status, AQ1 command queue, plug registers, node register windows, coefficient table bases, and static filter dimensions. Bit definitions include reset, interrupt, idle, instruction source selectors, scaling/color-conversion flags, target/source type flags, and BDisp color encodings.

Control flow: no executable flow exists in this header. Its structure and constants are consumed by the hardware builder and reset/interrupt paths, where descriptor fields are filled in memory and then referenced through AQ1 register writes.

State and persistence: the header has no runtime state. It defines the ABI between the driver and hardware, so changes affect every submitted node and register access.

Dependencies and integration points: requires standard kernel integer and `BIT()` definitions from including compilation units. It is included by `bdisp-hw.c` and indirectly tied to debugfs node dumps in the BDisp driver.

Risks: field order in `struct bdisp_node` must remain exactly aligned with hardware expectations. Several names/comments show typo-like artifacts (`BTL_S1TY_SUBBYTE`, `BTL_S2TY_SUBBYTE`, "firect fill"), which are harmless if unused but can confuse maintenance. Constants are largely raw hardware values, so incorrect edits can silently corrupt DMA programming.

Test signals: compile coverage is necessary but insufficient. Real validation comes from node dump comparison against the hardware manual, successful color format conversions, AQ1 interrupt delivery, and regression tests around scaling/filter programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-v4l2.c

Purpose: implements the BDisp platform driver and V4L2 mem2mem interface. It exposes a `/dev/video*` M2M device for blit, scale, crop/compose, flip, and color conversion operations backed by the BDisp hardware helpers.

Important APIs and functions: platform entry points are `bdisp_probe` and `bdisp_remove`; PM hooks are `bdisp_runtime_resume`, `bdisp_runtime_suspend`, `bdisp_suspend`, and `bdisp_resume`. File operations are `bdisp_open`, `bdisp_release`, `video_ioctl2`, mem2mem mmap and poll. IOCTL handlers cover querycap, enum/g/try/s format, g/s selection, streamon/off, buffer operations, and control events. Queue and job functions include `queue_init`, `bdisp_device_run`, `bdisp_job_finish`, `bdisp_job_abort`, `bdisp_start_streaming`, and IRQ handlers.

Control flow: probe allocates `struct bdisp_dev`, maps registers, prepares the clock, installs a threaded IRQ, registers V4L2 and debugfs, enables runtime PM, allocates filter tables, and registers the mem2mem video device. Open allocates a per-file `bdisp_ctx`, node descriptors, V4L2 controls, default formats, and V4L2 M2M queues. Streaming requires both source and destination formats to have been set. When both queues have buffers, `bdisp_device_run` resolves contiguous DMA addresses, resets hardware, builds and submits nodes, queues a timeout work item, and marks the engine running. The hard IRQ validates/clears AQ1 last-node status and wakes the threaded handler, which finishes buffers or coordinates suspend. Timeout work resets the device and completes buffers with error.

State and persistence: `bdisp_dev` owns global locks, clock, registers, workqueue, current M2M context, state bits, and debug data. Each `bdisp_ctx` stores source/destination `bdisp_frame`, flip controls, state flags, V4L2 file handle, and node DMA addresses. Runtime PM gates the clock around streaming; no persistent on-disk state exists.

Dependencies and integration points: depends on V4L2 core, V4L2 controls/events, videobuf2 DMA-contig, V4L2 mem2mem, platform OF match `st,stih407-bdisp`, runtime PM, clocks, IRQs, and `bdisp-hw.c`/debugfs helpers.

Risks: the selection setter aligns `out.height` with `frame->fmt->w_align` rather than `h_align`, which can be wrong for formats with different dimensions. The IRQ path and stop request path rely on state bits protected by a single spinlock and waitqueue; regressions can hang streamoff/suspend. The code accepts only single-plane vb2 buffers and computes multi-plane offsets manually, so stride and sizeimage mismatches are important. Hardware is reset for each job, which simplifies state but increases latency.

Test signals: validate V4L2 compliance for M2M queues, format negotiation, selection flags, hflip/vflip controls, streamon requirements, PM suspend/resume during active jobs, forced IRQ timeout behavior, and real DMA output comparisons for supported formats. Kernel build with `CONFIG_VIDEO_STI_BDISP` and `COMPILE_TEST` catches API drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp.h

Purpose: provides the shared BDisp driver data model and internal function declarations used by the V4L2, hardware, and debugfs implementation files.

Important APIs and types: defines `BDISP_NAME`, node count limits, `struct bdisp_fmt`, `struct bdisp_frame`, `struct bdisp_request`, `struct bdisp_ctx`, `struct bdisp_m2m_device`, `struct bdisp_dbg`, and `struct bdisp_dev`. Function declarations expose hardware lifecycle/submission helpers and debugfs/performance hooks across compilation units.

Control flow: no executable flow is present, but the types define the ownership graph. A platform-level `bdisp_dev` owns the V4L2 device, mem2mem device, register/clock resources, IRQ waitqueue, timeout work, and debug state. Each open file owns a `bdisp_ctx`, which carries the active source/destination frames, controls, and DMA node descriptors.

State and persistence: all state is runtime-only. `bdisp_frame` records negotiated geometry, colorspace, crop, and DMA plane addresses. `bdisp_request` and `bdisp_dbg` preserve the last submitted operation for diagnostics. `bdisp_dev->state` and `bdisp_ctx->state` are in-memory synchronization flags.

Dependencies and integration points: includes Linux clock/platform/spinlock/time headers, V4L2 controls/devices/mem2mem, and videobuf2 DMA-contig. It deliberately forward-shares internals across the local BDisp driver rather than exposing a public kernel API.

Risks: because this header carries cross-file internals, changing structure fields affects hardware programming, V4L2 control logic, and debugfs simultaneously. `MAX_NB_NODE` encodes current assumptions of two output planes and two width strides; new formats or wider hardware capabilities require revisiting node allocation and build logic.

Test signals: compile all BDisp compilation units after structural changes, then run open/close, format negotiation, debugfs last-node/request inspection, and multi-plane/large-width jobs to confirm the shared structures remain coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/Kconfig

Purpose: defines Kconfig symbols for the STMicroelectronics Delta video decoder driver and its MJPEG decoder support.

Important APIs and symbols: `VIDEO_STI_DELTA` is the user-visible tristate for the multi-format Delta V4L2 decoder, depending on V4L mem2mem drivers, `VIDEO_DEV`, and `ARCH_STI || COMPILE_TEST`. `VIDEO_STI_DELTA_MJPEG` is a bool child option defaulting to enabled. `VIDEO_STI_DELTA_DRIVER` is the internal tristate that becomes buildable only when the base driver and MJPEG support are selected; it selects `VIDEOBUF2_DMA_CONTIG`, `V4L2_MEM2MEM_DEV`, and `RPMSG`.

Control flow: Kconfig selection determines whether the `st-delta` module is built and whether MJPEG-specific objects are linked. The base prompt explicitly warns that the driver builds only when at least one decoder is selected.

State and persistence: no runtime state. The selected symbols persist in the kernel build configuration and control module availability.

Dependencies and integration points: integrates with the media platform driver menu, videobuf2, V4L2 mem2mem, rpmsg firmware transport, and STi SoC architecture support.

Risks: only MJPEG exists in this snapshot, so disabling `VIDEO_STI_DELTA_MJPEG` effectively disables the driver object through `VIDEO_STI_DELTA_DRIVER`. Users may expect the base multi-format symbol alone to produce a module, but the hidden driver symbol prevents that without a decoder.

Test signals: menuconfig visibility, allmodconfig/allnoconfig with `COMPILE_TEST`, and module build checks for `VIDEO_STI_DELTA=m` plus MJPEG enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/Makefile

Purpose: maps Delta Kconfig selections to the `st-delta` module object list.

Important APIs and entries: `obj-$(CONFIG_VIDEO_STI_DELTA_DRIVER) += st-delta.o` creates the module. Core objects are `delta-v4l2.o`, `delta-mem.o`, `delta-ipc.o`, and `delta-debug.o`. MJPEG support conditionally adds `delta-mjpeg-hdr.o` and `delta-mjpeg-dec.o`.

Control flow: kbuild links the core V4L2, memory, IPC, and debug code into one module, then appends codec-specific objects according to `CONFIG_VIDEO_STI_DELTA_MJPEG`.

State and persistence: no runtime state. It controls compilation units and therefore which decoder registrations are possible at runtime.

Dependencies and integration points: must stay aligned with `Kconfig`, `delta-cfg.h` external decoder declarations, and the `delta_decoders[]` registry in `delta-v4l2.c`.

Risks: adding a decoder requires coordinated updates in Kconfig, this Makefile, and the decoder registry. Missing a core object would leave unresolved internal symbols such as `delta_ipc_open` or `delta_get_frameinfo_default`.

Test signals: `make M=drivers/media/platform/st/sti/delta` with MJPEG enabled validates the build shape; disabling MJPEG should omit MJPEG objects and avoid unresolved `mjpegdec` references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-cfg.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-cfg.h

Purpose: centralizes Delta driver limits, defaults, firmware version text, frame-buffer counts, autosuspend timing, and decoder declarations.

Important APIs and constants: defines firmware version `21.1-3`, min/max dimensions 32x32 to 4096x2400, 32-pixel frame alignment, default MJPEG-to-NV12 formats, max access units, DPB/user frame limits, max private frame data, 5 ms runtime-PM autosuspend, and `DELTA_MAX_DECODERS`. Under MJPEG configuration it declares `extern const struct delta_dec mjpegdec`.

Control flow: these constants drive V4L2 format bounding, frame size/allocation calculations, output queue buffer inflation, decoder registry sizing, and device naming.

State and persistence: no state; it establishes compile-time policy and hardware/firmware constraints consumed across the module.

Dependencies and integration points: depends on V4L2 fourcc constants and `VIDEO_MAX_FRAME` from media headers included by consumers. It is included by `delta.h`, so its values flow into every Delta implementation.

Risks: frame count is capped against `VIDEO_MAX_FRAME`, so platform assumptions can silently reduce theoretical DPB/user buffering. Defaults and limits must match firmware capabilities; mismatches can lead to rejected IPC decode requests or undersized buffers. The firmware version is only a string and does not enforce compatibility with the rpmsg firmware endpoint.

Test signals: run V4L2 try/s_fmt around min/max/unaligned sizes, output queue allocation at high DPB counts, and firmware boot against the advertised version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-debug.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-debug.c

Purpose: provides small formatting and summary helpers for Delta stream/frame information and decoder instance statistics.

Important APIs and functions: `delta_streaminfo_str` formats compressed stream metadata; `delta_frameinfo_str` formats decoded frame metadata; `delta_trace_summary` emits a debug log summary at context release when stream info is known.

Control flow: V4L2 negotiation and release paths call these helpers to produce consistent debug messages. The functions consume already-populated `delta_streaminfo`, `delta_frameinfo`, and counter fields and do not mutate decode flow.

State and persistence: no independent state. Output reflects transient per-context fields such as decoded/output/dropped frame counts and error counters.

Dependencies and integration points: depends on `delta.h`, V4L2 field/fourcc conventions, and the local debug header. The release path in `delta-v4l2.c` uses `delta_trace_summary`.

Risks: formatting uses fixed caller-provided buffers and compact strings; malformed or uninitialized profile/level/other arrays can produce sparse output. `delta_frameinfo_str` checks `DELTA_STREAMINFO_FLAG_*` names against frame flags, relying on equal numeric values with `DELTA_FRAMEINFO_FLAG_*`; that coupling is fragile if flags diverge.

Test signals: enable dynamic debug and inspect GET/S_FMT and release logs for MJPEG streams with crop/pixel-aspect metadata. Static builds catch prototype drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-debug.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-debug.h

Purpose: declares Delta debug formatting and summary helpers shared with the V4L2 implementation.

Important APIs and functions: exposes `delta_streaminfo_str`, `delta_frameinfo_str`, and `delta_trace_summary`.

Control flow: callers pass existing stream/frame/context objects and caller-owned buffers to format state for logging. There is no control logic in the header.

State and persistence: none. The declared functions only observe runtime context state.

Dependencies and integration points: requires consumers to have visible `struct delta_streaminfo`, `struct delta_frameinfo`, and `struct delta_ctx` definitions, typically through `delta.h`.

Risks: the header has a narrow internal API, but it does not include `delta.h` itself, so include order matters. Prototype changes must be kept in sync with `delta-debug.c`.

Test signals: compile coverage from `delta-v4l2.c` and `delta-debug.c`; runtime signal is correct dynamic-debug output during format negotiation and release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-ipc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-ipc.c

Purpose: implements Delta host-to-firmware IPC over rpmsg. It opens/closes firmware decoder instances and sends synchronous set-stream/decode commands using a DMA shared command buffer.

Important APIs and functions: exported APIs are `delta_ipc_init`, `delta_ipc_exit`, `delta_ipc_open`, `delta_ipc_set_stream`, `delta_ipc_decode`, and `delta_ipc_close`. Internal pieces define rpmsg message structures, command IDs, sanity tag validation, DMA virtual-to-physical translation, data range validation, callback completion, and rpmsg probe/remove binding.

Control flow: `delta_ipc_init` registers an rpmsg driver for `"rpmsg-delta"`. Probe stores the rpmsg device in `delta_dev`. `delta_ipc_open` validates parameters, allocates a write-combined DMA buffer through `hw_alloc`, copies open parameters into it, sends `DELTA_IPC_OPEN`, waits up to 100 ms for completion, stores the firmware handle, and returns the shared buffer and host handle. Set-stream and decode require parameter/status data to live inside that shared buffer, translate those pointers to physical addresses, send rpmsg commands, wait for the callback, and map firmware errors to `-EIO`. Close frees the IPC buffer, sends `DELTA_IPC_CLOSE`, and waits for acknowledgement.

State and persistence: each `delta_ctx` embeds a `delta_ipc_ctx` with callback error, firmware handle, completion, and shared buffer metadata. `delta_dev` stores the currently bound rpmsg device. No persistent storage exists; firmware-side state is represented by `copro_hdl`.

Dependencies and integration points: depends on rpmsg, DMA allocation from `delta-mem.c`, `delta_ctx` counters, and MJPEG decoder code that fills firmware-specific command structures.

Risks: command completion is single-flight per context and assumes firmware always echoes the host handle and sanity tag correctly. `delta_ipc_open` references `ctx->ipc_buf->size` in an error message before `ctx->ipc_buf` is assigned, which could fault if `param->size > ipc_buf_size`. The callback length error message swaps received length/source values. All timeouts are fixed at 100 ms, which may be tight under firmware stalls. Closing frees the shared buffer before sending the close command, so firmware close must not need command data beyond the header.

Test signals: rpmsg endpoint bind/unbind, timeout injection, malformed callback tag/host handle tests, MJPEG decode under load, and error-path checks for DMA buffer leaks and `sys_errors` counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-ipc.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-ipc.h

Purpose: declares the Delta IPC API and documents the shared-buffer contract between codec code and the rpmsg transport.

Important APIs and functions: exposes initialization/exit functions plus `delta_ipc_open`, `delta_ipc_set_stream`, `delta_ipc_decode`, and `delta_ipc_close`. The comments define `struct delta_ipc_param` expectations: command parameter and status pointers must be virtual addresses inside the allocated IPC shared buffer for set-stream and decode.

Control flow: a decoder calls open with initial parameters and desired shared buffer size, receives a buffer and handle, writes later command structures into that buffer, uses set-stream/decode synchronously, then calls close during teardown.

State and persistence: no header-owned state. The API mutates `delta_ctx->ipc_ctx`, firmware instance state, and DMA buffer ownership in the implementation.

Dependencies and integration points: requires `struct delta_dev`, `struct delta_ctx`, `struct delta_buf`, and `struct delta_ipc_param` definitions from `delta.h`. It is consumed by MJPEG decoder code and initialized by `delta-v4l2.c`.

Risks: the API is synchronous and only supports one pending command per context. Passing stack or unrelated heap data to set-stream/decode violates the documented address-range requirement and will be rejected. The close function returns void, so close errors are only logged/counted.

Test signals: compile coverage, open/decode/close sequencing with a live firmware endpoint, and range-validation tests that deliberately pass command data outside the IPC buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mem.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mem.c

Purpose: provides small DMA allocation/free helpers for Delta firmware command buffers and other hardware-visible allocations.

Important APIs and functions: `hw_alloc` allocates write-combined DMA memory, fills a caller-provided `struct delta_buf`, logs the allocation, and increments `ctx->sys_errors` on failure. `hw_free` logs and frees a previously allocated buffer with the stored attributes.

Control flow: codec and IPC code call `hw_alloc` when they need contiguous memory visible to the Delta firmware or hardware. The caller owns the `delta_buf` object and must call `hw_free` exactly once after successful allocation.

State and persistence: allocated memory is runtime DMA state only. Metadata stored in `delta_buf` includes size, virtual address, physical address, name, and DMA attributes.

Dependencies and integration points: depends on `delta.h`, Linux DMA APIs, and `delta_ctx->dev` for the device handle. Used by `delta-ipc.c` to allocate the shared IPC buffer.

Risks: `hw_free` assumes `buf`, `buf->vaddr`, and metadata are valid; no null guard exists. Allocation uses `__GFP_NOWARN`, so callers must rely on explicit driver errors and counters. Write-combine memory is suitable for hardware but requires care if CPU reads are expected.

Test signals: allocation failure injection, open/close leak checks, DMA mapping visibility to firmware, and repeated MJPEG instance creation/destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mem.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mem.h

Purpose: declares Delta hardware-visible memory allocation helpers.

Important APIs and functions: exports `hw_alloc(struct delta_ctx *ctx, u32 size, const char *name, struct delta_buf *buf)` and `hw_free(struct delta_ctx *ctx, struct delta_buf *buf)`.

Control flow: callers allocate a `delta_buf` metadata structure, request a DMA buffer with a debug name, then free the same metadata through `hw_free`.

State and persistence: none in the header. Allocated DMA state is owned by the implementation and caller-provided `delta_buf`.

Dependencies and integration points: requires `struct delta_ctx` and `struct delta_buf` from `delta.h`. It is the local memory-management boundary for Delta IPC and future codec code.

Risks: the terse `hw_alloc`/`hw_free` names are generic inside the kernel tree and should remain file-local through includes to avoid confusion. Include order matters because this header does not include `delta.h`.

Test signals: compile coverage and allocation/free exercised by `delta_ipc_open` and `delta_ipc_close`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg-dec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg-dec.c

Purpose: implements the Delta MJPEG decoder backend for compressed MJPEG input to NV12 output using local JPEG header parsing plus firmware IPC decode commands.

Important APIs and functions: exports `const struct delta_dec mjpegdec`. Key functions include `delta_mjpeg_open`, `delta_mjpeg_close`, `delta_mjpeg_decode`, `delta_mjpeg_get_streaminfo`, `delta_mjpeg_get_frame`, `delta_mjpeg_ipc_open`, `delta_mjpeg_ipc_decode`, and status/error formatting helpers.

Control flow: opening allocates private `delta_mjpeg_ctx`. The first `decode` call parses a JPEG header with `delta_mjpeg_read_header`, checks resolution budget, stores stream dimensions, and returns without firmware decode so V4L2 can negotiate frame info. Later decode calls lazily open a firmware instance, parse each AU header and data offset, acquire a free destination frame from the M2M queue, fill firmware JPEG decode parameters in the IPC buffer, request auxiliary decimated NV12 output with `JPEG_ADDITIONAL_FLAG_420MB`, call `delta_ipc_decode`, interpret firmware status, marks the output frame as keyframe/decoded, and exposes it through `get_frame`.

State and persistence: `delta_mjpeg_ctx` stores the parsed header, IPC handle/buffer, one pending output frame, and a large string buffer for command dumps. `delta_ctx` counters track decoded frames, stream errors, decode errors, and system errors. Firmware instance state persists until close.

Dependencies and integration points: depends on Delta V4L2 frame management, `delta-ipc`, `delta-mem`, MJPEG header parser, and firmware ABI structures from `delta-mjpeg-fw.h`.

Risks: the first AU is consumed for header discovery rather than producing output, so users must expect stream-info discovery behavior. `delta_mjpeg_ipc_decode` passes `au_dma + au_size - 1` after adding `data_offset` but does not subtract the offset from `au_size`, so the effective end address can extend past the parsed payload window. Firmware error classification distinguishes stream versus decode errors but only returns failure when IPC itself fails. Only progressive MJPEG to NV12 is implemented.

Test signals: V4L2 MJPEG header-first streaming, malformed JPEG markers, oversized resolution rejection, firmware error-code injection, NV12 payload correctness, timestamp FIFO behavior, and output frame recycling under limited capture buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg-dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg-fw.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg-fw.h

Purpose: defines the MJPEG firmware ABI structures, enumerations, and status codes exchanged through Delta IPC.

Important APIs and types: includes decoded/display buffer address structures, reconstruction-output enable flags, horizontal/vertical decimation factors, `enum jpeg_decoding_error_t`, decode mode and additional flags, `struct jpeg_video_decode_init_params_t`, `struct jpeg_decode_params_t`, and `struct jpeg_decode_return_params_t`.

Control flow: no executable code. `delta-mjpeg-dec.c` fills init/decode parameter structures in the IPC shared buffer and firmware writes the return-params structure after decode.

State and persistence: no driver state. These layouts are part of the host/firmware binary contract and must remain fixed-width and alignment-compatible.

Dependencies and integration points: depends on kernel integer types. The fields are consumed by the MJPEG decoder and transported by `delta-ipc.c`.

Risks: enum and structure sizes must match firmware expectations across compiler/architecture combinations. All physical-address fields are `u32`, which assumes firmware-visible addresses fit 32 bits. A typo-like vertical decimation value `0x000000208` should be treated cautiously even if unused. Extending structures without firmware coordination will break IPC.

Test signals: firmware interoperability, decode command dumps, status error-code mapping, and builds on 32/64-bit configurations to confirm structure sizes remain expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg-fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg-hdr.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg-hdr.c

Purpose: parses enough of an MJPEG/JPEG access unit to find SOI/SOF markers and extract frame dimensions and component count for stream negotiation.

Important APIs and functions: exported function `delta_mjpeg_read_header` scans for `0xffd8` SOI followed by SOF0/SOF1 and calls internal `delta_mjpeg_read_sof`. `header_str` formats parsed header fields for debug logging.

Control flow: `delta_mjpeg_read_header` walks the input byte stream until it sees SOI, records the data offset, then requires a later SOF marker. `delta_mjpeg_read_sof` reads big-endian length/height/width plus precision and component count, bounds the component count, and ensures component metadata fits in the input before returning.

State and persistence: the parser fills the caller-provided `struct mjpeg_header` and `data_offset`. It does not allocate memory or store global state.

Dependencies and integration points: used by `delta-mjpeg-dec.c` on the first AU and every decode AU. Depends on `delta.h` for logging context and `delta-mjpeg.h` for header structures.

Risks: the parser is intentionally minimal and does not parse quantization/Huffman tables or validate all marker segment lengths. It requires SOI before SOF and returns `-ENODATA` if a partial header is supplied. Component details are not actually copied into `header->components`, only bounds-checked.

Test signals: sample MJPEG streams with SOF0/SOF1, partial/truncated buffers, SOF before SOI, component count at/above `MJPEG_MAX_COMPONENTS`, and data offset correctness for firmware decode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg-hdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg.h

Purpose: declares the lightweight MJPEG header representation and parser API used by the Delta MJPEG decoder.

Important APIs and types: defines `struct mjpeg_component`, `MJPEG_MAX_COMPONENTS`, `struct mjpeg_header`, and `delta_mjpeg_read_header`.

Control flow: the decoder passes an AU virtual address, size, output header, and data-offset pointer to `delta_mjpeg_read_header` before negotiating stream info or invoking firmware decode.

State and persistence: no owned state. The header structure is stored in `delta_mjpeg_ctx` by the decoder after parsing.

Dependencies and integration points: includes `delta.h` for decoder context types. The parser implementation lives in `delta-mjpeg-hdr.c` and the consumer is `delta-mjpeg-dec.c`.

Risks: `MJPEG_MAX_COMPONENTS` is five, and the parser rejects component counts greater than or equal to that value, so a stream with exactly five components is not accepted despite the array length. The component structure is defined for future detail but current parser does not populate its fields.

Test signals: compile coverage and parser tests using representative MJPEG headers with varying component counts and dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-v4l2.c

Purpose: implements the Delta V4L2 mem2mem platform driver, queue management, decoder registry, stream/frame negotiation, timestamp tracking, EOS handling, runtime PM, and module lifecycle.

Important APIs and functions: platform entry points are `delta_probe` and `delta_remove`; file operations are `delta_open` and `delta_release`; IOCTL handlers cover formats, selection, decoder commands, events, and mem2mem buffers. Core helpers include `delta_open_decoder`, `delta_run_work`, `delta_job_ready`, AU/frame vb2 operations, `delta_get_free_frame`, `delta_recycle_default`, `delta_get_frameinfo_default`, `delta_get_sync`, and `delta_put_autosuspend`.

Control flow: probe sets up clocks, runtime PM, rpmsg IPC, decoder registry, supported formats, V4L2 device, workqueue, and video node. Open creates a `delta_ctx`, initializes M2M queues, sets default MJPEG/NV12 parameters, and enables coprocessor clocks. Output `start_streaming` opens a decoder when the stream format is known, consumes the first source buffer as header data, decodes it to populate stream/frame info, and moves the instance to READY. Normal mem2mem work removes one AU, powers the hardware if the decoder does not self-manage PM, calls decoder `decode`, queues DTS unless the AU is discarded, drains all decoded frames from the decoder, marks source/capture buffers done, requeues free frames, and finishes the M2M job. Capture buffers are registered with the decoder during prepare and recycled when userspace requeues them. STOP decoder command drains pending frames and emits EOS through an empty `V4L2_BUF_FLAG_LAST` capture buffer plus an EOS event.

State and persistence: `delta_dev` holds global V4L2/rpmsg/clock/workqueue state and decoder lists. `delta_ctx` holds state machine phase, selected decoder, streaminfo/frameinfo, AU/frame counters, DTS FIFO, frame array, error counters, abort flag, and codec private data. State is in-memory only and destroyed at release.

Dependencies and integration points: depends on V4L2 mem2mem, videobuf2 DMA-contig, rpmsg IPC, runtime PM clocks (`delta`, `delta-st231`, `delta-flash-promip`), and codec backends such as `mjpegdec`.

Risks: header decoding occurs in output start_streaming and returns buffers to QUEUED on failure, so userspace sequencing is strict. `delta_job_abort` only sets `aborting`; it does not cancel in-flight firmware work. Frame state transitions depend on userspace recycling capture buffers promptly, and EOS may be delayed until a free capture buffer arrives. The AU size estimate is MJPEG-oriented and may need revisiting if additional compressed formats are added.

Test signals: V4L2 compliance for mem2mem decoder queues, header-first MJPEG streaming, resolution renegotiation after streaminfo discovery, EOS event/buffer behavior, capture-buffer starvation/recycling, rpmsg timeout/failure handling, runtime-PM autosuspend, and build coverage with MJPEG enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta.h

Purpose: defines the central Delta decoder data model, state machine, frame/access-unit types, decoder operation interface, device/context structures, helper string functions, and shared function prototypes.

Important APIs and types: key types include `enum delta_state`, `struct delta_streaminfo`, `struct delta_au`, `struct delta_frameinfo`, `struct delta_frame`, `struct delta_dts`, `struct delta_buf`, `struct delta_ipc_ctx`, `struct delta_ipc_param`, `struct delta_dec`, `struct delta_ctx`, and `struct delta_dev`. It declares default frameinfo/recycle helpers, frame allocation, and runtime PM helpers.

Control flow: the header describes the codec contract: decoders open/close, receive prepared frames, parse stream info, negotiate frame info, synchronously decode AUs, return decoded frames, recycle frames, and optionally flush/drain. The V4L2 layer drives these operations according to the instance state machine from waiting-for-format through EOS.

State and persistence: all fields are runtime-only. Context state tracks selected decoder, IPC context, stream/frame info validity, decoded/output/drop/error counters, DTS FIFO, buffer/frame lifecycle, work serialization, and codec-private data. Device state tracks registered decoders and rpmsg binding.

Dependencies and integration points: includes rpmsg, V4L2 device/mem2mem, and `delta-cfg.h`. It is shared by all Delta source files and forms the internal ABI between generic V4L2 code, firmware IPC, and codec backends.

Risks: many state flags and frame lifecycle bits cross module boundaries, so incomplete transitions can leak buffers or stall mem2mem jobs. The decoder ops documentation contains duplicated comments for some members, which can obscure the intended call sequence. `frame_state_str` relies on caller-provided buffers and is diagnostic only.

Test signals: compile every Delta object after struct changes, then validate decoder open/decode/recycle/flush/drain sequencing, timestamp FIFO behavior, frame state dumps, and multi-instance operation through `delta_dev->instance_id`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/Kconfig

Purpose: defines Kconfig options for the STMicroelectronics HVA hardware video encoder V4L2 driver and optional debugfs support.

Important APIs and symbols: `VIDEO_STI_HVA` is the user-visible tristate, depending on V4L mem2mem drivers, `VIDEO_DEV`, and `ARCH_STI || COMPILE_TEST`, and selecting `VIDEOBUF2_DMA_CONTIG` plus `V4L2_MEM2MEM_DEV`. `VIDEO_STI_HVA_DEBUGFS` is a bool child option depending on `VIDEO_STI_HVA` and `DEBUG_FS`.

Control flow: selected symbols determine whether `st-hva` is built and whether `hva-debugfs.o` is included.

State and persistence: no runtime state. Values persist in the kernel build configuration and affect module capabilities.

Dependencies and integration points: integrates with the media platform encoder tree, videobuf2, V4L2 mem2mem, STi architecture support, and debugfs.

Risks: debugfs is optional and should not be assumed by diagnostics. The driver help calls HVA multi-format, but this subset only provides H.264 encoders for NV12/NV21 input through `hva-h264.c`.

Test signals: menuconfig visibility, `COMPILE_TEST`, module builds with debugfs on/off, and boot-time probe on STi hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/Makefile

Purpose: defines the object composition of the `st-hva` video encoder module.

Important APIs and entries: `obj-$(CONFIG_VIDEO_STI_HVA) += st-hva.o`; core objects are `hva-v4l2.o`, `hva-hw.o`, `hva-mem.o`, and `hva-h264.o`; `hva-debugfs.o` is conditional on `CONFIG_VIDEO_STI_HVA_DEBUGFS`.

Control flow: kbuild links the V4L2 front end, hardware executor, DMA memory helpers, and H.264 backend into one module.

State and persistence: no runtime state. It controls what implementation files are present in the module.

Dependencies and integration points: must stay aligned with HVA Kconfig and the encoder registry in `hva-v4l2.c`; the H.264 backend exports encoder descriptors referenced by that registry.

Risks: forgetting to add a new codec object or conditional symbol will produce a driver that enumerates fewer formats than expected or fails to link.

Test signals: build with `CONFIG_VIDEO_STI_HVA=m`, with and without `CONFIG_VIDEO_STI_HVA_DEBUGFS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-debugfs.c

Purpose: implements optional debugfs views and performance accounting for HVA device and per-context encoder state.

Important APIs and functions: exported hooks are `hva_debugfs_create`, `hva_debugfs_remove`, `hva_dbg_ctx_create`, `hva_dbg_ctx_remove`, `hva_dbg_perf_begin`, and `hva_dbg_perf_end`. Debugfs show functions expose device identity, registered encoders, last completed context, hardware registers, and currently running contexts.

Control flow: device probe creates a debugfs directory with `device`, `encoders`, `last`, and `regs` files. Context creation adds a numbered per-context file and initializes min performance metrics. Encoding paths call perf begin/end around hardware work. Context removal snapshots the last stream-info-bearing context for later inspection, then removes the file. Show handlers compute averages and format frame/stream/control/error/performance details.

State and persistence: runtime-only debug state lives in `hva->dbg` and `ctx->dbg`, including timestamps, min/max/total durations, periods, bitrate windows, and debugfs dentries. The last context snapshot persists only until device removal or overwrite by a later context.

Dependencies and integration points: depends on debugfs, seq_file show helpers, V4L2 control menu strings, HVA core types, and `hva_hw_dump_regs` from `hva-hw.c`.

Risks: debugfs reads wake hardware to dump registers, so they interact with runtime PM. Snapshotting an entire `hva_ctx` into `last_ctx` copies pointers and transient fields for diagnostics only; it must not be treated as a live context. Min metrics start at `UINT_MAX`, so displays before samples can look odd.

Test signals: mount debugfs and inspect files during idle, active encoding, after release, and with runtime PM suspended. Compare reported frames, bitrate, and durations against V4L2 buffer timestamps and payload sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-h264.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-h264.c

Purpose: implements HVA H.264 encoding backend descriptors for NV12 and NV21 input, including firmware/hardware task descriptor construction, codec-private buffer allocation, slice/SEI/filler NAL handling, and task execution.

Important APIs and functions: exports `nv12h264enc` and `nv21h264enc`. Key functions are `hva_h264_open`, `hva_h264_close`, `hva_h264_encode`, `hva_h264_prepare_task`, `hva_h264_fill_slice_header`, `hva_h264_fill_sei_nal`, `hva_h264_fill_data_nal`, and helpers to read output size/stuffing from hardware post-output.

Control flow: open validates ESRAM capacity, allocates codec-private sequence info, reference frame, reconstructed frame, and task descriptor buffers. For each frame, prepare fills `hva_h264_td` with dimensions, GOP-derived picture type, BRC mode, entropy mode, bitrate/CPB clamping based on H.264 level/profile, framerate workaround for hardware BRC overflow, source/reference/output addresses, ESRAM subregions, slice header placement, SPS/PPS payload handling, optional SEI stereo info, and non-VCL size. Encode executes the task through `hva_hw_execute_task`, adds hardware-reported bitstream bytes to existing payload, appends filler NAL bytes if requested, increments stream count, and swaps reference/reconstructed buffers.

State and persistence: `struct hva_h264_ctx` stores allocated hardware buffers across frames for one encoder instance. `pctx->stream_num`, controls, error counters, and stream buffer metadata drive per-frame state. Reference/reconstructed frames persist between encodes until close.

Dependencies and integration points: depends on HVA core structures and controls from `hva.h`, DMA allocation helpers, hardware executor command `H264_ENC`, V4L2 H.264 controls, and the V4L2 front end that pre-fills SPS/PPS payloads in keyframe stream buffers.

Risks: task descriptor fields are a dense hardware ABI, and many addresses are truncated to `u32`, requiring 32-bit reachable DMA. Level indexing assumes V4L2 level enum values align with `h264_infos_list` order. The keyframe SPS/PPS check compares flags for exact equality to `V4L2_BUF_FLAG_KEYFRAME`, which may miss keyframes with additional flags. Framerate correction can divide by computed `td->framerate_num`; very low rates need validation. Only one slice is configured.

Test signals: encode NV12 and NV21 at supported sizes, IDR/P-frame GOP transitions, bitrate/CPB clamp behavior for each H.264 level/profile, CABAC/CAVLC, SPS/PPS payload length, optional SEI, buffer-size exhaustion, ESRAM-size rejection, and hardware error interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-h264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-hw.c

Purpose: implements the low-level HVA hardware interface: MMIO resource setup, clocks/runtime PM, IRQ handling, task FIFO submission, hardware version detection, and optional register dumping.

Important APIs and functions: exported APIs are `hva_hw_probe`, `hva_hw_remove`, `hva_hw_runtime_suspend`, `hva_hw_runtime_resume`, `hva_hw_execute_task`, and debugfs-only `hva_hw_dump_regs`. IRQ handlers cover status completion and hardware memory-interface errors.

Control flow: probe maps registers, records ESRAM resource address/size, prepares the clock, installs status and error threaded IRQs, disables them until task execution, initializes mutex/completion, enables runtime PM, and reads the IP version. Runtime resume enables the clock and sets it to 300 MHz; suspend disables it. `hva_hw_execute_task` serializes with `protect_mutex`, enables IRQs, resumes PM, enables command-specific clock gating, programs byte-swap and memory-interface registers, pushes command/client id and task descriptor physical address to the FIFO, waits up to 2 seconds for completion, maps interrupt-reported `ctx->hw_err` to return status, disables IRQs/gating, and autosuspends PM.

State and persistence: `hva_dev` stores registers, ESRAM range, clock, IRQ numbers, completion, hardware status/error registers, IP version, and context slots. `hva_ctx->hw_err` and error counters are updated by IRQ threads. Hardware register state is programmed per task and gated off afterward.

Dependencies and integration points: depends on platform resources, two IRQ lines, runtime PM, clocks, `hva.h` context/device helpers, and task descriptors produced by codec backends such as `hva-h264.c`.

Risks: `hva_hw_get_ip_version` unlocks `protect_mutex` on PM failure even though this function did not lock it, which is dangerous on that error path. Probe resumes PM and then calls `hva_hw_get_ip_version`, which itself takes/puts PM, making PM reference accounting worth reviewing. IRQs are disabled/enabled for every task; missed completions or shared IRQ semantics can deadlock the 2-second wait. Task addresses are passed directly from DMA metadata, so DMA mask/IOMMU setup in the V4L2 layer is critical.

Test signals: probe on valid/invalid HVA versions, runtime suspend/resume cycles, forced status and memory-interface error IRQs, FIFO timeout path, multi-context serialization, clock-rate failure injection, and debugfs register reads while suspended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-hw.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-hw.h

Purpose: declares the HVA hardware support interface and command identifiers used by encoder backends and the V4L2 platform layer.

Important APIs and types: defines hardware version constants `HVA_VERSION_UNKNOWN` and `HVA_VERSION_V400`, `enum hva_hw_cmd_type` with `H264_ENC` plus client/all freeze/start/remove commands, and prototypes for probe/remove, runtime PM, task execution, and debugfs register dumping.

Control flow: V4L2 probe calls `hva_hw_probe`, PM hooks delegate to runtime suspend/resume, codec backends call `hva_hw_execute_task` with a DMA task descriptor, and remove calls `hva_hw_remove`.

State and persistence: no header-owned state. The API mutates `struct hva_dev` and `struct hva_ctx` state in the implementation.

Dependencies and integration points: includes `hva-mem.h` for `struct hva_buffer` and requires `struct platform_device`, `struct device`, `struct hva_dev`, and `struct hva_ctx` visibility from including files. It is consumed by `hva-h264.c`, `hva-debugfs.c`, and the V4L2 core.

Risks: command IDs are hardware ABI values. Unsupported command enum members are declared, but `hva_hw_execute_task` currently handles only `H264_ENC`; callers must not assume all enum values are implemented.

Test signals: compile coverage, H.264 task submission through `hva_h264_encode`, and debugfs register dump availability when `CONFIG_VIDEO_STI_HVA_DEBUGFS` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-mem.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-mem.c

Purpose: allocates and frees DMA buffers used by HVA codec backends for task descriptors, sequence/context data, and reference/reconstructed frames.

Important APIs and functions: `hva_mem_alloc` allocates a devm-managed `struct hva_buffer` plus write-combined DMA memory, fills metadata, logs, and returns the buffer pointer. `hva_mem_free` releases the DMA memory and frees the metadata object.

Control flow: codec open paths allocate private hardware buffers through `hva_mem_alloc`; codec close paths call `hva_mem_free` for each successful allocation.

State and persistence: allocated buffers persist for the lifetime of an encoder context. Metadata includes name, DMA physical address, CPU virtual address, and size. No global state exists.

Dependencies and integration points: depends on `hva.h` for `ctx_to_dev` and error counters, Linux devm and DMA allocation APIs, and `hva-mem.h`.

Risks: `hva_mem_free` assumes non-null valid metadata. Mixing devm allocation for metadata with explicit DMA free is correct only if close paths run before device teardown; double-free paths must be avoided. Write-combined memory favors hardware writes and may surprise CPU read-heavy code.

Test signals: H.264 open/close leak checks, allocation failure injection after each buffer allocation stage, DMA address range validation, and repeated multi-instance create/destroy cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-mem.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-mem.h

Purpose: defines the HVA DMA buffer metadata structure and declares allocation helpers.

Important APIs and types: `struct hva_buffer` stores a debug name, physical DMA address, CPU virtual address, and byte size. Functions are `hva_mem_alloc` and `hva_mem_free`.

Control flow: encoder code requests named buffers through `hva_mem_alloc`, keeps the returned pointer in codec-private state, and frees it at close.

State and persistence: no header-owned state; `struct hva_buffer` instances describe runtime DMA allocations.

Dependencies and integration points: requires `dma_addr_t`, `u32`, and `struct hva_ctx` visibility from including files. Included by `hva-hw.h` and used directly by `hva-h264.c`.

Risks: the buffer abstraction carries no DMA attributes field, so allocation/free policy is fixed in `hva-mem.c`. Callers must not free buffers allocated elsewhere through this API.

Test signals: compile coverage and successful H.264 context allocation/free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-mem.h -->
