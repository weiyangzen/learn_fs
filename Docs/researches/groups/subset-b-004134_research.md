# subset-b-004134 Research

Grouped research for the requested source-tree-aligned media driver files. Each source file section is delimited with the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_rpc.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_rpc.h

Purpose: Defines the Amphion VPU host/firmware RPC interface abstraction used by the codec core, instances, command path, and vb2 buffer path. It provides shared buffer descriptors, the common event packet shape, and the `vpu_iface_ops` virtual table implemented by codec-specific firmware frontends such as Windsor.

Important APIs and types: `struct vpu_rpc_buffer_desc` models firmware-visible ring/stream buffer pointers. `struct vpu_shared_addr` carries the mapped RPC memory, command/message descriptors, boot-address base, owning `vpu_core`, and private per-interface state. `struct vpu_rpc_event` is the generic command/message packet. `struct vpu_iface_ops` supplies firmware hooks for codec/format support, core boot/shutdown/restore, RPC memory setup, command packing, message unpacking, stream buffer management, memory resources, encoder/decoder parameter programming, frame input, and instance lifecycle.

Control flow: Most of the file is inline dispatch. Callers resolve operations through `vpu_core_get_iface()` or `vpu_inst_get_iface()`, validate required function pointers and instance ids, then invoke the firmware-specific operation. `vpu_iface_init()` stores `core->iface = shared`, back-links `shared->core`, and rejects over-consumed RPC buffers. `vpu_iface_input_frame()` increments `inst->total_input_count` only after the backend accepts the frame. Stream buffer configuration also validates 4-byte alignment and 32-bit firmware address range.

State and persistence: The header itself persists no data, but it standardizes persistent runtime state in `core->iface`, `shared->priv`, stream descriptors, and instance counters.

Dependencies and integration: Depends on vb2, `vpu_codec.h`, VPU core/instance structures, V4L2 formats, and backend implementations in files such as `vpu_windsor.c`. It is the boundary between generic Amphion command helpers and firmware-specific ABI layouts.

Risks: Many wrappers return success when optional hooks are missing, so feature support can silently degrade. Callers must avoid passing invalid instances; most instance-scoped operations reject `inst->id < 0`, but some optional hooks no-op. Firmware address truncation is explicitly guarded for stream buffers only.

Test signals: Exercise boot/init with undersized RPC memory, command pack/send/receive paths, stream-buffer alignment errors, invalid instance ids, encoder and decoder param updates, missing optional hooks, and frame-input counter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_v4l2.c

Purpose: Implements the shared Amphion V4L2 mem2mem plumbing for encoder and decoder instances: file open/close, format negotiation helpers, vb2 queues, buffer state helpers, media-device registration, EOS/source-change notifications, and buffer processing dispatch into codec-specific instance operations.

Important APIs and functions: Public helpers include `vpu_v4l2_open()`, `vpu_v4l2_close()`, `vpu_try_fmt_common()`, `vpu_get_fmt_plane_size()`, `vpu_process_output_buffer()`, `vpu_process_capture_buffer()`, `vpu_next_src_buf()`, `vpu_skip_frame()`, buffer lookup helpers, `vpu_v4l2_set_error()`, `vpu_set_last_buffer_dequeued()`, `vpu_add_func()`, and `vpu_remove_func()`. Internal vb2 callbacks cover queue setup, buffer init/prepare/finish/queue, start/stop streaming, and mem2mem queue initialization.

Control flow: Open requests a VPU core, initializes the V4L2 fh, controls, mem2mem context, ordered message workqueue, and FIFO. Queue setup derives plane counts and sizes from current negotiated formats. Starting a queue registers the instance, clears last-buffer state, and calls the codec `start` op. Queued buffers are inserted into v4l2-m2m lists and immediately attempt output/capture processing through `process_output` and `process_capture` ops when `check_ready` permits. Stop calls codec `stop`, returns queued buffers as errors, and resets output sequence.

State and persistence: Per-instance state includes mutex, core pointer, m2m context, format structures, min buffer counts, sequence number, FIFO/workqueue, buffer states, average QP metadata, and codec state. No disk persistence exists.

Dependencies and integration: Integrates V4L2 device/fh/events, v4l2-mem2mem, videobuf2 DMA-contig/vmalloc, codec ops via `call_vop`, format helpers, and Amphion core allocation. `vpu_add_func()` registers encoder/decoder video nodes and media-controller entities.

Risks: Empty `device_run`/always-not-ready `job_ready` means scheduling is intentionally driven by queue callbacks and firmware messages; tests should confirm no mem2mem scheduling assumptions are broken. `buf_prepare()` marks invalid buffers but still returns 0. Workqueue allocation failure does not fail open. Several paths depend on `inst->ops` being complete.

Test signals: Run v4l2-compliance for mem2mem nodes, format try/set coverage for compressed/raw plane mappings, queue start/stop and seek reinit paths, EOS/source-change event delivery, invalid undersized buffers, vmalloc stream-buffer mode, and open error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_v4l2.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_v4l2.h

Purpose: Declares the shared Amphion V4L2 helper API exported by `vpu_v4l2.c` for encoder, decoder, command, and message-handling code.

Important APIs: It exposes instance locking, vb2/V4L2 buffer state and average-QP accessors, open/close entry points, common format sizing/validation, output and capture processing triggers, source-buffer lookup/skip helpers, error notification, source-change notification, last-buffer-dequeued handling, buffer counts, source queue emptiness checks, physical DMA address lookup, and `vpu_get_format()`.

Control flow and state: This header has no control flow except `vpu_get_format()`, which selects `inst->out_format` for output queue types and `inst->cap_format` otherwise. Its declarations establish that V4L2-facing code manipulates per-instance lock-protected state, vb2 buffer metadata, and V4L2 event state managed by the implementation.

Dependencies and integration: Depends on Linux V4L2 type definitions and implicit Amphion structs from including contexts. Used by encoder/decoder ops, firmware frame submission, and common queue management.

Risks: Because the header forward-declares behavior without local type declarations for every struct, include order matters. Misusing `vpu_get_format()` with non-video or malformed queue types would fall through to capture format.

Test signals: Compile coverage across all Amphion units, output/capture queue format access in encoder and decoder paths, and buffer lookup helpers under queued, processing, and drained states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_v4l2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_windsor.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_windsor.c

Purpose: Implements the Windsor/MediaIP encoder firmware RPC ABI for Amphion VPU encoding. It lays out shared RPC memory, maps generic VPU command/message ids to firmware ids, fills encoder input descriptors, configures firmware memory resources and stream buffers, and translates V4L2 encode parameters into Windsor control structures.

Important APIs and types: Exports `vpu_windsor_get_data_size()`, `vpu_windsor_init_rpc()`, log/system configuration, stream buffer sizing/config/update/descriptor reads, command packing, message id conversion, message data unpacking, memory resource configuration, frame input, version/max-instance queries, and encode parameter programming. Internal structures model `windsor_iface`, per-stream control interfaces, YUV descriptors, expert/config/static/dynamic params, encoder params, memory pools, status blocks, and picture-info messages.

Control flow: `vpu_windsor_init_rpc()` partitions one RPC buffer into firmware interface, command ring, message ring, per-stream control descriptors, and host control structures, writing firmware-relative addresses and storing host pointers in `shared->priv`. Commands are translated through lookup tables; frame encode commands include timestamp seconds/nanoseconds. Input buffers fill Y and UV physical addresses and keyframe flags, then call `vpu_session_encode_frame()`. Firmware messages unpack frame-done, memory-request, and frame-release payloads.

State and persistence: Runtime state lives entirely in shared DMA memory and `shared->priv`. Stream buffer descriptors persist firmware read/write pointers; memory pools persist physical/firmware-relative resource addresses; encode params persist until updated.

Dependencies and integration: Depends on Amphion core, RPC, command/session helpers, V4L2 controls, vb2 DMA addresses, color conversion helpers, and i.MX8Q system config helpers. `vpu_windsor.h` exposes the implementation to the interface table.

Risks: Firmware ABI structures are large and tightly packed by C layout assumptions; any mismatch breaks firmware communication. `vpu_windsor_config_stream_buffer()` lacks local instance range validation unlike memory-resource setup. Some setter return values are ignored in aggregate parameter setup. The frame-rate calculation divides denominator by numerator after checking only numerator.

Test signals: Validate RPC buffer byte usage, per-stream pointer layout, H.264 profile/level/bitrate/QP/SAR/color mappings, NV12/NV12M input rejection/acceptance, memory request handling, stream pointer wrap/32-bit handling, timestamp round trips, and multi-instance max-stream behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_windsor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_windsor.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_windsor.h

Purpose: Declares the Windsor encoder firmware operations consumed by the generic Amphion RPC interface.

Important APIs: The header exports data-size discovery, RPC initialization, log/system config, stream-buffer sizing and manipulation, command packing, message conversion/unpack, memory-resource configuration, encode-parameter programming, frame input, version, and max-instance-count queries.

Control flow and state: No local state is defined here; it describes the callable surface that `vpu_iface_ops` can bind to for Windsor-capable encoder cores. The implementation stores state in `struct vpu_shared_addr`, RPC DMA memory, and private host control structures.

Dependencies and integration: Requires Amphion shared types such as `vpu_shared_addr`, `vpu_buffer`, `vpu_rpc_event`, `vpu_rpc_buffer_desc`, `vpu_encode_params`, `vpu_inst`, and vb2 buffers from including units. It integrates `vpu_windsor.c` with core interface tables.

Risks: Prototype drift from `vpu_iface_ops` would be compile-detected, but semantic mismatches such as instance bounds and address units require runtime tests.

Test signals: Build coverage and end-to-end encoder startup using the Windsor interface table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_windsor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/arm/Kconfig

Purpose: Provides the top-level ARM media platform Kconfig menu and includes the Mali-C55 ISP driver Kconfig.

Important APIs/types/functions: No C API; it defines menu structure through a comment and `source "drivers/media/platform/arm/mali-c55/Kconfig"`.

Control flow and state: Kernel configuration flow enters this file from the media platform Kconfig hierarchy and delegates all actual options to the Mali-C55 subdirectory. No runtime state exists.

Dependencies and integration: Integrated by the kernel Kconfig tree under media platform drivers. It is paired with the ARM platform `Makefile`.

Risks: Any new ARM media driver under this directory must be sourced here or it will not be configurable. Path mismatch would break menuconfig.

Test signals: `make menuconfig` visibility and `scripts/kconfig/conf` coverage for `VIDEO_MALI_C55`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/arm/Makefile

Purpose: Adds the ARM Mali-C55 media platform subdirectory to the kernel build.

Important APIs/types/functions: No C symbols; `obj-y += mali-c55/` ensures the subdirectory Makefile participates in built-in and module resolution.

Control flow and state: Kbuild descends into `mali-c55/` unconditionally, while object selection inside that directory depends on `CONFIG_VIDEO_MALI_C55`.

Dependencies and integration: Paired with `arm/Kconfig` and `arm/mali-c55/Makefile`.

Risks: Unconditional descent is normal for Kbuild, but missing subdirectory files or stale object names fail build-time.

Test signals: Compile with `CONFIG_VIDEO_MALI_C55=m`, `=y`, and unset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/Kconfig

Purpose: Defines the `VIDEO_MALI_C55` tristate option for the Arm Mali-C55 ISP platform driver.

Important APIs/types/functions: No runtime API. The option depends on supported architectures or `COMPILE_TEST`, V4L platform drivers, video device support, and OF. It selects MIPI D-PHY PHY support, Media Controller, V4L2 fwnode/subdev APIs, V4L2 ISP helpers, and vb2 DMA-contig/vmalloc support.

Control flow and state: Kconfig controls whether `mali-c55.o` is built in, built as a module, or omitted. The help text declares module name `mali-c55`.

Dependencies and integration: Enables the source files listed in the subdirectory Makefile and depends on V4L2/media infrastructure used throughout the driver.

Risks: Missing selected dependencies would surface as compile/link failures. Architecture gating may hide the driver from relevant non-listed platforms unless `COMPILE_TEST` is used.

Test signals: Kconfig dependency resolution, compile-test builds, module build/install, and allmodconfig coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/Makefile

Purpose: Defines the composite Mali-C55 driver object.

Important APIs/types/functions: No C API. `mali-c55-y` aggregates capture, core, ISP, params, resizer, stats, and TPG objects; `obj-$(CONFIG_VIDEO_MALI_C55) += mali-c55.o` ties the composite object to Kconfig.

Control flow and state: Kbuild compiles each implementation unit and links them into one module or built-in object.

Dependencies and integration: The object list must match exported functions declared in `mali-c55-common.h`; omissions become unresolved symbols.

Risks: Adding a new implementation file without updating this list leaves code unbuilt. Removing a listed file breaks build.

Test signals: `make M=drivers/media/platform/arm/mali-c55`, module load, and link-time symbol checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-capture.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-capture.c

Purpose: Implements the Mali-C55 full-resolution and optional downscale V4L2 video capture nodes, including pixel format enumeration, vb2 queue handling, capture buffer programming, interrupt completion, media link validation, and video-device registration.

Important APIs/functions: Exports `mali_c55_cap_dev_write()`, `mali_c55_format_is_raw()`, `mali_c55_set_next_buffer()`, `mali_c55_set_plane_done()`, `mali_c55_register_capture_devs()`, and unregister helpers. Internal format table maps V4L2 fourccs to media-bus codes and writer register modes.

Control flow: Queued buffers are put on an input list. On ISP start interrupt, `mali_c55_set_next_buffer()` removes the next input buffer, enables/disables writer frame-write bits, writes Y/UV DMA addresses and stride registers, and moves the buffer to a processing list. Plane-done interrupts call `mali_c55_set_plane_done()`, decrement `planes_pending`, timestamp and sequence the buffer, then complete it when all planes are done. Streaming starts runtime PM, allocates media pipeline, configures capture registers, enables the resizer stream, and may start the ISP once every required queue is streaming.

State and persistence: Each capture node stores current format, sink pad, vb2 queue, locks, register offset, input and processing lists, DMA addresses, pending plane counters, and pointer to its resizer. No persistent storage exists.

Dependencies and integration: Uses V4L2/video-device ioctls, media controller links, vb2 DMA-contig, PM runtime, resizer subdevs, ISP pipeline readiness, and register helpers.

Risks: GREY format intentionally discards the UV plane while some code still writes UV registers; single-plane formats need careful interrupt behavior. Link validation requires exact dimensions and compatible mbus codes. Buffer underflow disables writer output for the next frame.

Test signals: v4l2-compliance capture tests, FR/DS format enumeration, raw rejection on DS pipe, link-validation failures, buffer underflow, multi-plane interrupt completion, stream start/stop ordering, and runtime PM balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-common.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-common.h

Purpose: Central shared definitions for the Mali-C55 ISP driver, including constants, entity structures, buffer structures, context state, register-helper declarations, and cross-file registration/control APIs.

Important APIs/types: Defines ISP pad ids, TPG, ISP, resizer, capture, params, stats, buffer, format-info, context, and top-level `struct mali_c55`. Declares register accessors, context config writes, entity registration/unregistration functions, active-context access, capture buffer programming/completion, frame-sync events, format lookup helpers, pipeline readiness, stats filling, and parameter config writes.

Control flow and state: The top-level `struct mali_c55` is the persistent in-memory driver state containing MMIO base, clocks, resets, IRQ, capabilities, media/V4L2 devices, notifier, media pipeline, all entities, a config context shadow, and next config-space selector. Substructures define locks and queues used by vb2 and interrupt paths.

Dependencies and integration: Pulls in Linux clock/reset/io/list/mutex/spinlock/V4L2/media/vb2 headers. Every Mali-C55 implementation file includes it to share object ownership and function contracts.

Risks: This header is the ABI between all driver units; structure layout changes affect many files. Locking expectations are encoded in comments but enforced in implementation, so misuse can race ISR, stream control, and userspace queueing.

Test signals: Full driver build, sparse/lockdep runs, entity registration/unregistration paths, and compile coverage for every declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-core.c

Purpose: Implements the platform driver core for Mali-C55: MMIO/context access, media graph construction, async sensor binding, hardware capability probing, interrupt handling, runtime PM power sequencing, and platform probe/remove.

Important APIs/functions: Exports global and context register read/write/update helpers, `mali_c55_config_write()`, `mali_c55_get_active_context()`, `mali_c55_pipeline_ready()`, and platform driver entry points. Internal code creates media links, registers all sub-entities, parses firmware graph endpoints, and handles IRQs.

Control flow: Probe allocates state, maps IO, acquires clocks/resets, initializes reserved memory and vb2 DMA segment size, powers hardware, checks capabilities, initializes a shadow config context from ping space, enables runtime PM, registers media entities, then records IRQ number. Runtime resume powers on and requests a threaded IRQ; suspend frees IRQ and powers off. The ISR clears interrupt status, handles SOF by queueing events, programming next capture buffers, consuming params, filling previous stats, and swapping ping/pong config; plane interrupts complete capture buffers.

State and persistence: Persistent runtime state includes hardware capabilities, config-space shadow buffer, next ping/pong selector, media graph, notifier, IRQ number, and PM state. No disk persistence.

Dependencies and integration: Uses platform bus, OF/fwnode graph, clocks/resets, PM runtime, media controller, V4L2 async, vb2 DMA-contig, and all Mali-C55 entity registration functions.

Risks: Probe obtains `irqnum` after media init and runtime PM enable; resume requesting IRQ depends on valid sequencing. `readl_poll_timeout()` result in power-on safe-stop is not checked. Config writes currently use CPU `memcpy_toio`, so long copies happen in threaded IRQ context.

Test signals: Probe/remove, runtime suspend/resume, missing endpoint with TPG fallback, sensor async binding, capabilities without pong rejection, IRQ SOF/plane-done paths, ping/pong config swap, and media graph topology validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-isp.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-isp.c

Purpose: Implements the Mali-C55 ISP V4L2 subdevice: supported sink/source media-bus formats, crop handling, stream start/stop, frame-sync events, capabilities control, subdev registration, and ISP configuration startup.

Important APIs/functions: Exports ISP format lookup helpers, `mali_c55_isp_queue_event_sof()`, `mali_c55_register_isp()`, and `mali_c55_unregister_isp()`. Internal operations implement enum/set/get format, crop selection, stream enable/disable, event subscription, init state, and read-only capabilities control.

Control flow: Format setup accepts raw 20-bit Bayer or RGB bypass input at the sink, propagates processed RGB121212 to the main source and sink format to bypass. Stream enable resolves the active remote source pad, resets frame sequence, initializes/defaults ISP config through params code, writes ping config, starts safe-start mode, then enables the upstream source stream. Stream disable disables upstream and safe-stops the ISP.

State and persistence: ISP state stores media pads, remote source pointer, capture lock shared by streaming users, frame sequence, and control handler. Active formats/crops live in V4L2 subdev state.

Dependencies and integration: Integrates with params initialization, core register helpers, V4L2 subdev streams/events, media routing, TPG or external sensor source, resizers, stats, and params nodes.

Risks: `media_pad_remote_pad_unique()` is assumed to return a usable remote pad; invalid graph state could dereference null. Some source color metadata maps from sink colorspace unexpectedly. Only one input stream is supported.

Test signals: Subdev pad format/crop compliance, TPG and external sensor stream starts, source-change through route switching, frame-sync event sequence, capabilities control readback, and invalid link graph handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-isp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-params.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-params.c

Purpose: Implements the Mali-C55 metadata-output video node that accepts userspace ISP parameter buffers and writes validated parameter blocks into the next frame's register context.

Important APIs/functions: Exports `mali_c55_params_write_config()`, `mali_c55_params_init_isp_config()`, registration and unregistration. Block handlers program sensor offset, AEXP histograms and weights, digital gain, AWB gains/config, mesh shading config, and mesh shading selection. It defines parameter block type metadata for V4L2 ISP validation.

Control flow: vb2 prepare validates buffer size and block layout using V4L2 ISP helpers after copying userspace content into an internal `kvmalloc` scratch buffer. Queued param buffers are listed. On ISP SOF path, `mali_c55_params_write_config()` pops one buffer, walks its blocks by size, dispatches to handlers, marks the buffer done, and leaves absent buffers as "reuse previous/default config". `mali_c55_params_init_isp_config()` programs windowing and safe defaults before first stream/config writes.

State and persistence: Params state stores video node, vb2 queue, lock, and queued scratch buffers. The actual hardware-facing state is the shared context register shadow in `mali_c55->context`.

Dependencies and integration: Uses V4L2 meta output, V4L2 ISP parameter validation, vb2 DMA-contig, media controller, runtime PM, ISP pipeline readiness, and register definitions.

Risks: AEXP histogram weights compute the last value/address but do not write the final register, which looks suspicious. Handlers trust prior validation for type/size. Config updates are frame-bound and silently skipped when no params buffer is queued.

Test signals: Meta format ioctls, malformed block rejection, each parameter block disable/enable behavior, per-frame buffer completion sequence, default config after no params, pipeline start synchronization with capture/stats, and register-write traces for AEXP/AWB/LSC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-registers.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-registers.h

Purpose: Defines Mali-C55 hardware register offsets, bit masks, field encoders, interrupt indices, capability bits, config-space sizes, metering/statistics addresses, and capture/resizer writer constants.

Important APIs/types: Provides macros for common ISP registers, ping/pong config spaces, interrupts, global parameter status capabilities, TPG, input windowing, Bayer order, metering, bypass blocks, AEXP/AWB, mesh shading, color correction, capture writers, crop/scaler/gamma, and FR/DS resizer filter banks.

Control flow and state: No executable control flow. The macros drive all MMIO and context-shadow writes in core, ISP, TPG, params, capture, stats, and resizer implementation files.

Dependencies and integration: Includes `<linux/bits.h>` for `BIT()` and `GENMASK()`. It is the central hardware ABI for the driver.

Risks: Typographical macro `MALI_c55_MESH_STRENGTH_MASK` uses lowercase `c55`; code currently references that exact spelling. `MALI_C55_REG_TEST_GEN_CH0_OFF_ON` is defined without a value and must not be used as an address. Register field comments and masks are hardware-critical and hard to validate without silicon.

Test signals: Compile coverage for every used macro, register write tracing during stream start, static analysis for unused/bad defines, and hardware tests for each enabled processing block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-resizer.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-resizer.c

Purpose: Implements full-resolution and downscale Mali-C55 resizer subdevices, including routing between processed and bypass paths, crop/compose scaling, media-bus code negotiation, coefficient programming, and subdev registration.

Important APIs/functions: Exports `mali_c55_register_resizers()` and unregister helpers. Internal code includes coefficient tables, bank selection, crop/scaler programming, active-route detection, bypass mbus downshift, routing validation, format/frame-size enumeration, format and selection setters, and stream enable/disable.

Control flow: Init state sets the normal processed route active, with FR also exposing a bypass route. Source formats derive from the active sink: processed RGB can output RGB121212 or YUV10, while bypass shifts supported 20-bit formats to 16-bit raw outputs. Setting crop/compose clamps to hardware limits; compose cannot change while streaming. Enabling streams either sets raw bypass for FR bypass route or disables bypass and programs crop/scaler registers plus coefficient banks.

State and persistence: Each resizer stores id, pads, route count, owning `mali_c55`, and associated capture device. Crop/compose/routes/formats live in V4L2 subdev state; programmed registers persist in the context shadow until rewritten.

Dependencies and integration: Uses V4L2 subdev streams/routing, media entities, common ISP format helpers, capture-device register writes, and core context helpers.

Risks: `mali_c55_rsz_shift_mbus_code()` returns `-EINVAL` as `u32`, and some callers test falsy rather than `IS_ERR_VALUE`. Coefficient programming writes many global registers at stream enable. FR scaler may be absent and compose rejects scaling only in that case; DS existence is capability-gated elsewhere.

Test signals: Route switching, bypass raw capture, RGB/YUV source format enumeration, crop/compose limits including streaming `-EBUSY`, 1:8 scaling limit, scaler-absent behavior, coefficient bank selection, and DS capability gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-resizer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-stats.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-stats.c

Purpose: Implements the Mali-C55 metadata-capture video node that returns 3A/statistics data to userspace once per frame.

Important APIs/functions: Exports `mali_c55_stats_fill_buffer()`, registration, and unregistration. Internal functions provide meta format ioctls, vb2 queue setup, buffer queueing/return, stream start/stop, and CPU MMIO reads of statistics regions.

Control flow: Queued stats buffers are placed on a list with payload set to `struct mali_c55_stats_buffer`. Stream start gets runtime PM, starts the media pipeline, and may start ISP streaming when all queues are ready. On SOF handling, `mali_c55_stats_fill_buffer()` pops one buffer, stamps sequence/timestamp, copies the 1024-bin histogram and metering config-space data from the just-used ping/pong region, and completes the buffer.

State and persistence: Stats state stores video node, vb2 queue, lock, and queued buffers. No persistent storage; stats are copied from hardware MMIO to userspace buffers.

Dependencies and integration: Uses V4L2 meta capture, vb2 DMA-contig, media controller, runtime PM, core IRQ SOF path, ping/pong config-space selection, and Mali-C55 config UAPI.

Risks: `segments_remaining` and `failed` are initialized but unused, suggesting planned segmented DMA/error handling is incomplete. Stats are read synchronously by CPU in threaded IRQ flow, which can be expensive. If no stats buffer is queued, data is dropped silently.

Test signals: Meta format ioctls, queued/unqueued SOF behavior, sequence alignment with frame-sync and params, ping/pong source correctness, stream start/stop PM balancing, and buffer return on stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-tpg.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-tpg.c

Purpose: Implements the Mali-C55 internal test pattern generator subdevice used as a camera-like source when no external sensor is required or available.

Important APIs/functions: Exports `mali_c55_register_tpg()` and unregister helper. Internal code manages supported mbus codes, frame-size/format negotiation, V4L2 controls for test pattern, hblank, vblank, and pixel rate, stream enable/disable, TPG register configuration, and default bright background programming.

Control flow: Set-format clamps dimensions and supported codes, then updates vblank defaults/ranges for active formats. Controls write TPG pattern and vertical blanking only if runtime PM is active. Stream enable configures fixed hblank, multi-frame generator mode, raw/RGB pattern format, applies controls, enables pattern generation in context registers, and turns on generated video globally. Stream disable clears those bits.

State and persistence: TPG state stores subdev, single source pad, control handler, vblank control pointer, and owning `mali_c55`. Active format lives in subdev state; control values persist in the V4L2 control framework.

Dependencies and integration: Uses V4L2 subdev and control APIs, PM runtime, core/context register helpers, and ISP sink links.

Risks: The fixed pixel rate and vblank heuristic assume hardware timing that should be validated across formats. Control writes are skipped when device is suspended and rely on later handler setup at stream enable. TPG entity function is camera sensor, so graph users must distinguish it from external sensors.

Test signals: TPG-only streaming, test pattern menu changes, vblank range recalculation for min/max frame sizes, raw/RGB format propagation to ISP, suspend/resume plus control restore, and media link switching between TPG and external sensor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-tpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/aspeed/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/aspeed/Kconfig

Purpose: Defines the Aspeed Video Engine media platform driver option.

Important APIs/types/functions: No C API. `VIDEO_ASPEED` is a tristate depending on `ARCH_ASPEED || COMPILE_TEST`, V4L platform drivers, and video device support, and selects vb2 DMA-contig.

Control flow and state: Controls whether the Aspeed video engine driver is built. Help text describes AST2400/AST2500 video capture and compression support.

Dependencies and integration: Paired with `aspeed/Makefile`, which builds `aspeed-video.o` when the option is enabled.

Risks: Kconfig only references AST2400/AST2500 in help; newer SoCs need option/help updates if supported elsewhere.

Test signals: Kconfig visibility on Aspeed and compile-test builds, module build with `VIDEO_ASPEED=m`, and dependency resolution for vb2 DMA-contig.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/aspeed/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/aspeed/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/aspeed/Makefile

Purpose: Connects `CONFIG_VIDEO_ASPEED` to the Aspeed video engine object in Kbuild.

Important APIs/types/functions: No C API. `obj-$(CONFIG_VIDEO_ASPEED) += aspeed-video.o`.

Control flow and state: Kbuild includes `aspeed-video.o` as built-in or module depending on the Kconfig state.

Dependencies and integration: Depends on the Aspeed Kconfig option and the corresponding implementation file in the same directory.

Risks: Object name drift causes build failure or omitted driver.

Test signals: Build with option unset, built-in, and module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/aspeed/Makefile -->
