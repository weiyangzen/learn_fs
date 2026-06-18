# subset-b-005496 Research

Grouped source research for USB gadget UVC function support, the USB function registry, and selected legacy precomposed gadget drivers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_configfs.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_configfs.c

## Purpose

`uvc_configfs.c` builds the configfs interface for the UVC gadget function. It exposes the UVC control and streaming descriptor graph under the function instance, lets users create headers, formats, frames, color matching descriptors, and extension units, and materializes linked configfs items into descriptor arrays consumed by the runtime UVC function. It also exposes root UVC options such as streaming interval, max packet, max burst, and function name.

## Important APIs, Types, and Functions

The public entry point is `uvcg_attach_configfs(struct f_uvc_opts *opts)`, which initializes `opts->func_inst.group` and creates the default `control` and `streaming` child groups. Most implementation uses `struct uvcg_config_group_type`, `uvcg_config_create_group()`, `uvcg_config_create_children()`, and `uvcg_config_remove_children()` to build and tear down static configfs subtrees.

Attribute generation is macro-heavy. `UVC_ATTR()` and `UVC_ATTR_RO()` create configfs attributes. Control-side handlers cover `control/header/<name>`, default processing/camera/output terminal descriptors, extension units, and `control/class/{fs,ss}` symlink targets. Streaming-side handlers cover `streaming/header/<name>`, `uncompressed`, `mjpeg`, `framebased`, `color_matching`, and `streaming/class/{fs,hs,ss}`.

Descriptor assembly centers on `uvcg_streaming_header_allow_link()`, `uvcg_streaming_class_allow_link()`, `__uvcg_iter_strm_cls()`, `__uvcg_cnt_strm()`, and `__uvcg_fill_strm()`. Those functions walk linked headers, formats, frames, and color matching descriptors, size an array of `struct uvc_descriptor_header *`, allocate one contiguous descriptor block, and copy configfs state into USB descriptor layouts.

## Control Flow

On function-instance creation, `uvcg_attach_configfs()` initializes the top-level config group and recursively creates default children. Users then populate dynamic groups: control headers, extension units, streaming headers, format instances, frame entries, and color matching entries. Stores validate numeric ranges, parse newline-delimited arrays through `__uvcg_iter_item_entries()`, and usually reject changes with `-EBUSY` once a descriptor is linked or `opts->refcnt` shows the function is active.

Configfs symlinks commit descriptor relationships. Control class links accept only headers under the matching `control/header` group and install the selected header into `opts->uvc_fs_control_cls` or `opts->uvc_ss_control_cls`. Streaming header links accept only direct children of streaming format groups and append `struct uvcg_format_ptr` entries. Streaming class links accept only streaming headers, compute final descriptor arrays for full/high/super speed, and store them in the corresponding `f_uvc_opts` fields.

## State and Persistence Behavior

State is runtime configfs state held in `f_uvc_opts` and per-item allocations. Lists in `opts->extension_units`, `uvcg_streaming_header.formats`, and `uvcg_format.frames` preserve user-created topology. `linked`, `refcnt`, and class-array pointers freeze descriptor edits once configfs symlinks or active function users depend on them. No state is persisted by this file; userspace must recreate configfs layout after reboot or module reload.

## Dependencies and Integration Points

The file depends on configfs, libcomposite function instances, UVC and USB video descriptor definitions, `u_uvc.h`/`f_uvc_opts`, gadget strings, `uvc_format_by_guid()`, and core kernel helpers for sorting, allocation, hex parsing, and endian conversion. It is the bridge between configfs layout and `f_uvc.c` descriptor binding, and its output feeds the V4L2/video code through `uvc->header` and `opts` descriptor arrays.

## Risks and Test Signals

Risks are concentrated in configfs hierarchy navigation, symlink validation, descriptor sizing, and memory ownership. Many handlers climb fixed parent chains; tree changes or bad assumptions can target the wrong `f_uvc_opts`. Extension-unit arrays are reallocated on size writes, and streaming class arrays allocate a pointer array plus contiguous descriptor data that must be freed on link drop. The framebased copy path intentionally translates from the internal packed frame layout into `struct uvc_frame_framebased`; descriptor-length mistakes would break host enumeration.

Useful tests include creating and deleting all dynamic groups; writing invalid numeric values, oversized arrays, and malformed hex; changing attributes before and after links; linking control headers for FS/SS; linking multiple formats and frames into a streaming header; creating framebased H.264 descriptors; linking and dropping color matching descriptors; enabling interrupt endpoint; binding the UVC function after configfs setup; and unbinding while descriptors and strings are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_configfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_configfs.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_configfs.h

## Purpose

`uvc_configfs.h` declares the private configfs data model used by the UVC gadget function. It defines wrapper structures that combine configfs items/groups with UVC descriptor state for control headers, streaming headers, formats, frames, color matching descriptors, and extension units.

## Important APIs, Types, and Functions

`to_f_uvc_opts()` maps a configfs item back to its owning `struct f_uvc_opts`. `UVCG_STREAMING_CONTROL_SIZE` defines the one-byte per-format streaming control field stored in input headers. `struct uvcg_control_header`, `struct uvcg_streaming_header`, `struct uvcg_format`, `struct uvcg_frame`, `struct uvcg_uncompressed`, `struct uvcg_mjpeg`, `struct uvcg_framebased`, `struct uvcg_color_matching`, and `struct uvcg_extension` are the core state carriers.

Inline conversion helpers such as `to_uvcg_control_header()`, `to_uvcg_streaming_header()`, `to_uvcg_format()`, `to_uvcg_frame()`, and format-specific `to_uvcg_*()` helpers provide type-safe container lookups for configfs callbacks. The one exported declaration is `uvcg_attach_configfs()`.

## Control Flow

The header has no independent execution path. `uvc_configfs.c` allocates these structures when users create configfs groups/items, initializes their embedded descriptors, links them into list heads, and later walks those lists to assemble runtime USB descriptors.

## State and Persistence Behavior

All structures are in-memory configfs state. `linked` counters prevent unsafe mutation after descriptors are selected. `refcnt` on color matching entries prevents edits while referenced by formats. Format and frame lists preserve ordering, which becomes the UVC format/frame index order. Extension units own dynamically allocated `baSourceID` and `bmControls` arrays. No persistent storage is represented.

## Dependencies and Integration Points

The header depends on `linux/configfs.h` and `u_uvc.h`, and indirectly on UVC descriptor declarations used by `f_uvc_opts`. It is private to the UVC function implementation but forms a key boundary between configfs callbacks, V4L2 format discovery, and descriptor materialization.

## Risks and Test Signals

Risks include packed internal frame layout assumptions, list lifetime errors, conversion-helper misuse, and descriptor structures with flexible-array semantics (`DECLARE_UVC_HEADER_DESCRIPTOR(1)` and `uvc_input_header_descriptor`) being copied with exact sizes. Compile coverage plus configfs create/link/drop tests for every declared type are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_configfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_queue.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_queue.c

## Purpose

`uvc_queue.c` implements UVC gadget video-buffer management using videobuf2. It translates V4L2 buffer operations into a queue consumed by the USB video pump and provides IRQ-safe access to the current buffer list.

## Important APIs, Types, and Functions

The vb2 callbacks are `uvc_queue_setup()`, `uvc_buffer_prepare()`, and `uvc_buffer_queue()`, collected in `uvc_queue_qops`. Public helpers include `uvcg_queue_init()`, `uvcg_free_buffers()`, `uvcg_alloc_buffers()`, `uvcg_query_buffer()`, `uvcg_queue_buffer()`, `uvcg_dequeue_buffer()`, `uvcg_queue_poll()`, `uvcg_queue_mmap()`, `uvcg_queue_cancel()`, `uvcg_queue_enable()`, `uvcg_complete_buffer()`, and `uvcg_queue_head()`.

## Control Flow

`uvcg_queue_init()` sets up a single-plane V4L2 output queue supporting MMAP, USERPTR, and DMABUF. It uses scatter-gather memory ops when the gadget reports SG support and falls back to vmalloc otherwise. `uvcg_alloc_buffers()` calls `vb2_reqbufs()` and retries in non-SG mode if SG allocation fails.

When userspace queues a buffer, `uvc_buffer_prepare()` validates payload size, records either SG or virtual-memory backing, initializes byte counters, and computes per-request payload sizing for isochronous transfer when `reqs_per_frame` is known. `uvc_buffer_queue()` appends the prepared buffer to `irqqueue` under `irqlock`, or immediately returns it with error if the queue has been disconnected. The video path calls `uvcg_queue_head()` to fetch the first active buffer and `uvcg_complete_buffer()` to return it to vb2 when a frame has been transmitted.

## State and Persistence Behavior

Queue state is in `struct uvc_video_queue`: vb2 queue, `flags`, sequence number, current `buf_used`, SG mode flag, `irqlock`, and IRQ-side buffer list. Per-buffer state is in `struct uvc_buffer`: state enum, backing pointer/SG cursor, current offset, length, bytes used, and request payload size. State is transient and reset across stream enable/disable.

## Dependencies and Integration Points

The file depends on videobuf2 core, V4L2 buffer types, `videobuf2-dma-sg`, `videobuf2-vmalloc`, USB composite gadget capabilities, and UVC video state from `struct uvc_video`. It is called by `uvc_v4l2.c` for ioctl operations and by `uvc_video.c` for streaming completion and cancellation.

## Risks and Test Signals

Important risks are lock ordering between vb2 mutexes and `irqlock`, stale buffers on disconnect, incomplete-frame handling through `UVC_QUEUE_DROP_INCOMPLETE`, SG fallback behavior, and correctness of `req_payload_size` for isochronous transfers. Tests should cover REQBUFS in SG and vmalloc modes, QBUF after disconnect, streamon/streamoff cycles, nonblocking DQBUF, mmap/poll, dropped incomplete frames, and buffer sequence/timestamp propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_queue.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_queue.h

## Purpose

`uvc_queue.h` declares the UVC gadget video queue abstraction shared by V4L2 and USB streaming code. It wraps videobuf2 objects with UVC-specific state needed for request encoding and completion.

## Important APIs, Types, and Functions

The header defines `UVC_MAX_FRAME_SIZE`, `UVC_MAX_VIDEO_BUFFERS`, `enum uvc_buffer_state`, `struct uvc_buffer`, and `struct uvc_video_queue`. Public operations mirror the implementation in `uvc_queue.c`: initialization, buffer allocation/query/queue/dequeue, poll, mmap, cancellation, stream enable/disable, completion, and head lookup. `uvc_queue_streaming()` is an inline `vb2_is_streaming()` wrapper.

## Control Flow

V4L2 code calls allocation and queue/dequeue helpers from ioctl paths. USB video code calls `uvcg_queue_head()` while filling USB requests and `uvcg_complete_buffer()` when the final request for a buffer completes. Stream transitions pass through `uvcg_queue_enable()`, while disconnect/error paths call `uvcg_queue_cancel()`.

## State and Persistence Behavior

`UVC_QUEUE_DISCONNECTED` gates new queued buffers after disconnect. `UVC_QUEUE_DROP_INCOMPLETE` marks the next completed buffer as an error after transfer loss. `sequence` and `buf_used` are per-stream counters. The IRQ list is transient and protected by `irqlock`.

## Dependencies and Integration Points

The header depends on list, poll, spinlock, and `videobuf2-v4l2` APIs. It is included by UVC V4L2 and video-transfer implementation files and forms their shared buffer contract.

## Risks and Test Signals

Risks include callers touching `irqqueue` without holding `irqlock`, incorrect state transitions between queued/active/done/error, and forgetting that SG cursor fields are meaningful only when `use_sg` is set. Test signals are compile coverage, streamon/streamoff transitions, disconnect cancellation, and both SG and non-SG streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_trace.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_trace.c

## Purpose

`uvc_trace.c` instantiates the UVC gadget tracepoints declared in `uvc_trace.h`. Its only job is to define `CREATE_TRACE_POINTS` before including the trace header.

## Important APIs, Types, and Functions

The file has no callable functions of its own. Including `uvc_trace.h` with `CREATE_TRACE_POINTS` causes tracepoint storage and registration metadata for `uvcg_video_queue` and `uvcg_video_complete` to be emitted in this translation unit.

## Control Flow

There is no runtime control flow beyond tracepoint registration handled by the kernel trace infrastructure when the object is loaded. Calls are made from `uvc_video.c` through `trace_uvcg_video_queue()` and `trace_uvcg_video_complete()`.

## State and Persistence Behavior

Tracepoint enablement and event buffers are managed by ftrace/perf infrastructure. This file stores no UVC runtime state and persists nothing.

## Dependencies and Integration Points

The file depends entirely on the kernel tracepoint system and the local trace header. It must be compiled exactly once with `CREATE_TRACE_POINTS`; otherwise tracepoint symbols would be missing or multiply defined.

## Risks and Test Signals

Risks are build-time: incorrect include path, duplicate creation, or trace header changes that break `define_trace.h` generation. Test signals are successful module build and visibility of `uvcg:*` events under tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_trace.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_trace.h

## Purpose

`uvc_trace.h` declares tracepoints for UVC gadget USB request queueing and completion. The events expose request pointer, request length, and the current queued-request count.

## Important APIs, Types, and Functions

`DECLARE_EVENT_CLASS(uvcg_video_req, ...)` defines the shared event payload for `struct usb_request *req` and `u32 queued`. `DEFINE_EVENT()` creates `uvcg_video_complete` and `uvcg_video_queue`. The trace header also sets `TRACE_SYSTEM` to `uvcg` and configures `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` for `define_trace.h`.

## Control Flow

Callers invoke generated functions such as `trace_uvcg_video_queue(req, count)` and `trace_uvcg_video_complete(req, count)`. When tracing is disabled, static-key machinery keeps overhead low. When enabled, the fast assignment copies `req`, `req->length`, and `queued` into the trace record.

## State and Persistence Behavior

The header defines trace event schema, not device state. Event records are transient tracing data controlled by kernel tracing consumers.

## Dependencies and Integration Points

It depends on `linux/tracepoint.h`, USB gadget request definitions, and `trace/define_trace.h`. It integrates with `uvc_video.c` request lifecycle instrumentation and with userspace ftrace/perf tooling.

## Risks and Test Signals

Risks include dereferencing `req->length` after invalid request lifetime if trace calls are moved, mismatched trace include path, and ABI expectations from existing tracing tools. Test signals are enabling the tracepoints during UVC streaming and observing queue/complete counts track `atomic queued`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_v4l2.c

## Purpose

`uvc_v4l2.c` exposes the UVC gadget function as a V4L2 video-output device. It lets userspace enumerate configured UVC formats/frames, choose stream parameters, queue video buffers, receive UVC control events, and send control responses to the USB host.

## Important APIs, Types, and Functions

The exported tables are `uvc_v4l2_ioctl_ops` and `uvc_v4l2_fops`. Format helpers include `to_uvc_format()`, `uvc_v4l2_get_bytesperline()`, `uvc_get_frame_size()`, `find_format_by_index()`, `find_frame_by_index()`, `find_format_by_pix()`, and `find_closest_frame_by_size()`. Request handling uses `uvc_send_response()` for `UVCIOC_SEND_RESPONSE`.

Core ioctl handlers cover querycap, get/try/set format, get/set frame interval, enumerate formats/sizes/intervals, REQBUFS/QUERYBUF/QBUF/DQBUF, STREAMON/STREAMOFF, event subscribe/unsubscribe, and default UVC response ioctl. File operations cover open, release, mmap, poll, and no-MMU unmapped-area lookup.

## Control Flow

Open allocates a `struct uvc_file_handle`, initializes V4L2 file-handle state, and points the handle at `uvc->video`. Userspace subscribes to UVC events; the first `UVC_EVENT_SETUP` subscriber becomes the active UVC application handle and triggers `uvc_function_connect()`. Host setup events are later answered by `UVCIOC_SEND_RESPONSE`, which queues data on EP0 or stalls for negative lengths.

Format ioctls derive the supported V4L2 format list from configfs-created UVC streaming headers and formats. `S_FMT` first calls `TRY_FMT`, then updates `video->fcc`, dimensions, bpp, and `imagesize`. Queue ioctls delegate to `uvc_queue.c`; QBUF wakes the video pump if the USB side is already streaming. STREAMON enables the USB video engine, continues delayed UVC setup, and marks state streaming. STREAMOFF disables video, returns to connected state, and continues setup with failure status if needed.

## State and Persistence Behavior

Persistent-in-memory state lives in `struct uvc_video`: selected pixel format, width, height, bpp, image size, and frame interval. Per-open state lives in `struct uvc_file_handle`, especially `is_uvc_app_handle`, which controls cleanup responsibility. `uvc->func_connected` gates exclusive SETUP-event ownership. No state is stored outside kernel memory.

## Dependencies and Integration Points

This file integrates UVC configfs descriptor state, V4L2 core, videobuf2 queue helpers, libcomposite EP0 setup continuation, and UVC event definitions from `linux/usb/g_uvc.h`. It also drives `uvc_video.c` through `uvcg_video_enable()` and `uvcg_video_disable()`.

## Risks and Test Signals

Risks include format selection mismatches between configfs UVC descriptors and V4L2 pixel formats, missing locking around video format fields, exclusive event-owner handling, and cleanup on release/unsubscribe while streaming. Tests should enumerate all configured formats, set exact and closest frame sizes, reject invalid sizeimage for uncompressed formats, stream buffers through QBUF/DQBUF, send UVC control responses, enforce one setup-event owner, and release the active UVC application handle while streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_v4l2.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_v4l2.h

## Purpose

`uvc_v4l2.h` declares the V4L2 operation tables implemented by `uvc_v4l2.c` for the UVC gadget video node.

## Important APIs, Types, and Functions

It exports `uvc_v4l2_ioctl_ops` and `uvc_v4l2_fops`. The ioctl table is consumed when registering the `video_device`; the file-operations table handles open, release, ioctl dispatch, mmap, poll, and optional no-MMU support.

## Control Flow

There is no runtime logic in the header. UVC function setup code assigns these tables into the V4L2 video device so all userspace interactions enter `uvc_v4l2.c`.

## State and Persistence Behavior

The header defines no state. It declares immutable operation-table symbols.

## Dependencies and Integration Points

It depends on V4L2 type declarations being visible at the use site and integrates UVC gadget registration code with the V4L2 implementation.

## Risks and Test Signals

Risks are limited to symbol mismatch or missing includes after refactors. Build coverage of the UVC function and successful video-device registration are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_v4l2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_video.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_video.c

## Purpose

`uvc_video.c` moves queued V4L2 video buffers into USB requests for the UVC gadget streaming endpoint. It encodes UVC payload headers, supports bulk and isochronous transfer modes, manages USB request pools, and coordinates request completion with videobuf2 buffer completion.

## Important APIs, Types, and Functions

Public functions are `uvcg_video_init()`, `uvcg_video_enable()`, and `uvcg_video_disable()`. Encoding functions are `uvc_video_encode_header()`, `uvc_video_encode_data()`, `uvc_video_encode_bulk()`, `uvc_video_encode_isoc()`, and `uvc_video_encode_isoc_sg()`. Request management uses `uvc_video_alloc_requests()`, `uvc_video_free_requests()`, `uvc_video_free_request()`, `uvc_video_prep_requests()`, `uvcg_video_usb_req_queue()`, `uvcg_video_ep_queue()`, and completion callback `uvc_video_complete()`.

Asynchronous execution is split between workqueue `uvcg_video_pump()` and kthread work `uvcg_video_hw_submit()`. Tracepoints `trace_uvcg_video_queue()` and `trace_uvcg_video_complete()` instrument queue depth.

## Control Flow

`uvcg_video_init()` initializes request lists, locks, work items, a high-priority workqueue, a FIFO kthread worker, default YUYV format state, and the vb2 queue. `uvcg_video_enable()` starts vb2 streaming, allocates USB requests sized for bulk or isochronous bandwidth, selects the encoder, resets counters, queues initial hardware submit work, and wakes the pump.

The pump repeatedly takes a free USB request under `req_lock`, takes the first queued video buffer under queue `irqlock`, encodes header and payload, and either queues directly to a bulk endpoint or places isochronous requests on `req_ready`. Completions decrement the queued count, handle USB status errors, complete any `last_buf`, recycle the request to `req_free`, wake the pump, and schedule hardware submit. The hardware-submit worker feeds isochronous endpoints from `req_ready` and may send bounded zero-length requests to keep the endpoint moving.

## State and Persistence Behavior

Streaming state includes `is_enabled`, `ureqs`, `req_free`, `req_ready`, `req_lock`, queued request count, interrupt-throttling counter, payload size, FID toggle, request sizing, and selected encode callback. Buffer progress uses `queue.buf_used`, SG cursors, and `ureq->last_buf`. State is runtime only and reset on every enable/disable cycle.

## Dependencies and Integration Points

The file depends on USB gadget endpoints/requests, UVC payload flags, unaligned endian helpers, V4L2 timestamps, the UVC queue API, and UVC tracepoints. It is driven by V4L2 STREAMON/STREAMOFF and QBUF paths and feeds the gadget endpoint selected by the UVC function bind path.

## Risks and Test Signals

Risks are concurrency-heavy: request free/ready/owned transitions cross completion context, workqueue context, and kthread context; disable must return in-flight buffers without racing completions; isochronous SG encoding mutates SG cursors under queue lock; and bulk EOF/zero-packet behavior depends on `payload_size` and `max_payload_size`. The pump tail path also re-adds `req`, so null or stale request handling should be watched. Tests should cover bulk and isochronous endpoints, SG and vmalloc memory, short/missed transfers (`-EXDEV`), disconnect (`-ESHUTDOWN`), repeated stream enable/disable, zero-length isochronous request limits, frame timestamp headers, EOF/FID toggling, and release while requests are in flight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_video.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_video.h

## Purpose

`uvc_video.h` declares the UVC gadget video streaming lifecycle functions used outside `uvc_video.c`.

## Important APIs, Types, and Functions

The header forward-declares `struct uvc_video` and exports `uvcg_video_enable()`, `uvcg_video_disable()`, and `uvcg_video_init()`. These are the control surface for V4L2 stream operations and UVC function setup.

## Control Flow

UVC device initialization calls `uvcg_video_init()`. V4L2 STREAMON calls `uvcg_video_enable()`, and STREAMOFF, release, unsubscribe, or disconnect paths call `uvcg_video_disable()`.

## State and Persistence Behavior

The header stores no state; it declares functions that mutate `struct uvc_video` runtime state.

## Dependencies and Integration Points

It is included by V4L2, queue, and UVC function code that needs to manage video streaming without depending on private implementation details.

## Risks and Test Signals

Risks are limited to API drift between callers and implementation. Build coverage and successful stream lifecycle tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/functions.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/functions.c

## Purpose

`functions.c` implements the libcomposite USB function-driver registry. It lets composite gadgets look up function instances by name, autoload missing function modules, allocate/free function instances, allocate/free concrete functions, and register/unregister function drivers.

## Important APIs, Types, and Functions

Exported symbols are `usb_get_function_instance()`, `usb_get_function()`, `usb_put_function_instance()`, `usb_put_function()`, `usb_function_register()`, and `usb_function_unregister()`. Internal helper `try_get_usb_function_instance()` searches `func_list` under `func_lock`, takes the provider module reference, calls `alloc_inst()`, and links the returned instance to its `usb_function_driver`.

## Control Flow

Composite gadget code calls `usb_get_function_instance("name")`. The registry first searches registered drivers. If absent, `usb_get_function_instance()` calls `request_module("usbfunc:%s", name)` and retries. Once a function instance exists, callers call `usb_get_function(fi)` to allocate a concrete `struct usb_function` from the driver's `alloc_func()` callback. Put paths call driver-provided free callbacks and drop module references.

## State and Persistence Behavior

The global `func_list` stores registered `struct usb_function_driver` entries for the lifetime of their modules. Function instances and functions are dynamic in-memory objects owned by composite gadget bind/unbind paths. No state is persisted.

## Dependencies and Integration Points

The file depends on libcomposite types, Linux module reference counting, kernel lists, and module autoload aliases. It is used by configfs gadgets and legacy precomposed gadgets throughout `drivers/usb/gadget`.

## Risks and Test Signals

Risks include module-reference leaks on allocation failures, duplicate driver names, use-after-unregister if consumers hold stale instances, and autoload failures returning the correct errno. Tests should load/unload function modules, request present and absent function names, hit duplicate registration, and exercise bind/unbind error paths in legacy gadgets that call these APIs repeatedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/functions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/Kconfig

## Purpose

`legacy/Kconfig` defines build-time configuration for precomposed USB gadget drivers. These entries select libcomposite and the specific USB function modules needed to build fixed-purpose gadget modules such as audio, ethernet, serial, MIDI, HID, FunctionFS, UVC webcam, mass storage, and debug-port gadgets.

## Important APIs, Types, and Functions

This is Kconfig data, not C code. Important symbols include `USB_ZERO`, `USB_AUDIO`, `GADGET_UAC1`, `GADGET_UAC1_LEGACY`, `USB_ETH`, `USB_ETH_RNDIS`, `USB_ETH_EEM`, `USB_G_NCM`, `USB_GADGETFS`, `USB_FUNCTIONFS`, `USB_FUNCTIONFS_ETH`, `USB_FUNCTIONFS_RNDIS`, `USB_FUNCTIONFS_GENERIC`, `USB_MASS_STORAGE`, `USB_GADGET_TARGET`, `USB_G_SERIAL`, `USB_MIDI_GADGET`, `USB_G_PRINTER`, `USB_CDC_COMPOSITE`, `USB_G_ACM_MS`, `USB_G_MULTI`, `USB_G_HID`, `USB_G_DBGP`, `USB_G_WEBCAM`, and `USB_RAW_GADGET`.

## Control Flow

Menu selection controls which modules are built and which lower-level function drivers are selected. For example, `USB_G_WEBCAM` selects `USB_F_UVC` and videobuf2 memory backends; `USB_AUDIO` selects UAC1/UAC2 function implementations based on sub-options; `USB_ETH` selects ECM/subset and optionally RNDIS/EEM; `USB_FUNCTIONFS` selects `USB_F_FS` and optional ethernet/RNDIS/generic configurations.

## State and Persistence Behavior

Kconfig choices are persisted only in the kernel build configuration (`.config`). They have no runtime state here, but they determine which module parameters, descriptors, and composite bind paths exist in the built kernel.

## Dependencies and Integration Points

The file integrates the legacy gadget directory with libcomposite, function drivers under `drivers/usb/gadget/function`, ALSA, networking, block layer, TTY, target core, V4L2, and raw gadget support. It also controls help text and module names consumed by users and distributions.

## Risks and Test Signals

Risks include missing `select` lines causing link failures, overbroad selects pulling invalid dependencies, config combinations that expose functions without prerequisites, and help text drifting from behavior. Test signals are allmodconfig/allnoconfig builds, targeted builds for every tristate, dependency-resolution checks, and module-load tests for each enabled legacy gadget.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/Makefile

## Purpose

`legacy/Makefile` maps legacy USB gadget Kconfig symbols to module objects and sets include paths needed by precomposed gadget sources.

## Important APIs, Types, and Functions

The file defines `ccflags-y` include paths for gadget core, UDC, and function headers. It maps module objects such as `g_zero-y := zero.o`, `g_audio-y := audio.o`, `g_ether-y := ether.o`, `g_hid-y := hid.o`, `g_dbgp-y := dbgp.o`, and `g_acm_ms-y := acm_ms.o`. It then uses `obj-$(CONFIG_...) += ...` to include each object in the build.

## Control Flow

Kbuild expands the selected `obj-*` entries based on `.config`, compiles the corresponding source file, and links built-in or module objects according to tristate values. Composite object names determine resulting module names such as `g_audio`, `g_ether`, `g_hid`, and `g_acm_ms`.

## State and Persistence Behavior

There is no runtime state. The Makefile affects build artifacts only.

## Dependencies and Integration Points

It integrates Kconfig selections with Kbuild and depends on headers in sibling gadget core/function/UDC directories. Source files rely on those include paths for `u_*` option headers and libcomposite declarations.

## Risks and Test Signals

Risks include stale object mappings, missing new legacy gadget entries, or module name mismatches with Kconfig help and userspace expectations. Test signals are clean builds for each `CONFIG_USB_*` selection and module-install output matching expected names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/acm_ms.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/acm_ms.c

## Purpose

`acm_ms.c` implements the legacy `g_acm_ms` composite gadget: one configuration containing CDC ACM serial and mass storage functions.

## Important APIs, Types, and Functions

Key functions are `acm_ms_bind()`, `acm_ms_do_config()`, and `acm_ms_unbind()`. The driver uses `usb_get_function_instance("acm")`, `usb_get_function_instance("mass_storage")`, `usb_get_function()`, `usb_add_function()`, and mass-storage helpers such as `fsg_config_from_params()`, `fsg_common_set_num_buffers()`, `fsg_common_set_cdev()`, `fsg_common_create_luns()`, and `fsg_common_set_inquiry_string()`.

## Control Flow

Bind obtains ACM and mass-storage function instances, configures mass-storage options from module parameters, allocates string IDs, optionally allocates an OTG descriptor, and registers one USB configuration. The configuration callback obtains concrete ACM and mass-storage functions and adds them in order, unwinding on failures. Unbind drops functions and instances and frees the OTG descriptor.

## State and Persistence Behavior

Global state includes `f_acm_inst`, `f_acm`, `fi_msg`, `f_msg`, `otg_desc`, device descriptor strings, and mass-storage module parameters. LUN and backing-storage state is owned by the mass-storage common layer. Runtime state is not persisted by this file.

## Dependencies and Integration Points

The file depends on libcomposite, `u_serial`, `f_mass_storage`, module parameters from `FSG_MODULE_PARAMETERS`, gadget OTG helpers, and composite overwrite options. Host-visible integration is through Linux Foundation ACM+MS vendor/product IDs, dynamic strings, and a self-powered configuration.

## Risks and Test Signals

Risks include incomplete error unwind for partially created mass-storage resources, stale global function pointers across bind failure, OTG descriptor lifetime, and module parameters producing invalid LUN setup. Tests should load with valid and invalid backing files, enumerate at full/high/super speed, verify both ACM and storage interfaces, test OTG-capable controllers, and unload after failed bind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/acm_ms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/audio.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/audio.c

## Purpose

`audio.c` implements the legacy `g_audio` composite gadget. Depending on build options it exposes UAC2, modern UAC1, or legacy UAC1 audio function support with module parameters for channel masks, sample rates, sample sizes, endpoint intervals, or legacy PCM device names and buffers.

## Important APIs, Types, and Functions

Key functions are `audio_bind()`, `audio_do_config()`, and `audio_unbind()`. The driver obtains `"uac2"`, `"uac1"`, or `"uac1_legacy"` function instances, fills their option structures (`f_uac2_opts`, `f_uac1_opts`, or `f_uac1_legacy_opts`), allocates string IDs, creates optional OTG descriptors, and adds a single configuration.

## Control Flow

Module parameters are selected by preprocessor branch. Bind obtains the chosen audio function instance, copies parameter values into the instance options, allocates manufacturer/product string IDs, optionally builds an OTG descriptor, and registers `audio_config_driver`. The config callback gets one concrete audio function and adds it. Unbind releases the concrete function, function instance, and OTG descriptor.

## State and Persistence Behavior

Configuration state is global module-parameter state plus the selected function instance options. Runtime audio streaming state is owned by the lower-level UAC function and ALSA virtual-card helpers. This file persists nothing outside module parameters and kernel memory.

## Dependencies and Integration Points

The file depends on libcomposite, UAC option headers, ALSA/PCM infrastructure selected by Kconfig, USB string assignment, OTG descriptor helpers, and composite overwrite parameters. It integrates with host USB Audio Class drivers and exposes a virtual ALSA path through the function implementation.

## Risks and Test Signals

Risks include invalid sample-rate arrays, branch-specific option drift, failed string/OTG allocation unwinds, and differences between UAC1 legacy and non-legacy descriptor behavior. Tests should build all three mode combinations, enumerate on host audio stacks, validate playback/capture with requested channel/rate/sample-size settings, test HS bInterval parameters for UAC2, and unload after active audio streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/cdc2.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/cdc2.c

## Purpose

`cdc2.c` implements the legacy `g_cdc` composite gadget with CDC ECM ethernet and CDC ACM serial in one configuration.

## Important APIs, Types, and Functions

Core functions are `cdc_bind()`, `cdc_do_config()`, and `cdc_unbind()`. It uses `can_support_ecm()`, `usb_get_function_instance("ecm")`, `usb_get_function_instance("acm")`, ethernet option helpers (`gether_set_qmult()`, `gether_set_host_addr()`, `gether_set_dev_addr()`), string ID assignment, and `usb_add_config()`.

## Control Flow

Bind rejects controllers that cannot support ECM, obtains ECM and ACM function instances, applies ethernet module parameters to the ECM network device, allocates string IDs, optionally creates an OTG descriptor, and registers one configuration. The configuration callback adds ECM first and ACM second, unwinding any partially added function on failure. Unbind releases functions, instances, and the OTG descriptor.

## State and Persistence Behavior

Global state includes ECM/ACM function instances and concrete functions, OTG descriptor storage, static descriptors, and ethernet module parameters. Network device state is owned by the ECM/gether layer. No runtime state is persisted by this file.

## Dependencies and Integration Points

It depends on libcomposite, `u_ether`, `u_serial`, `u_ecm`, the networking stack, and gadget OTG support. It exposes a NetChip CDC composite vendor/product ID and integrates with host CDC ECM and ACM drivers.

## Risks and Test Signals

Risks include ECM capability checks differing by UDC, ethernet address parameter validation, cleanup asymmetry on partial config-add failures, and host compatibility when descriptors or class values change. Tests should enumerate on ECM-capable and incapable controllers, verify host sees both network and serial interfaces, pass custom MAC addresses, exercise OTG descriptors, and unload after network traffic and serial I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/cdc2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/dbgp.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/dbgp.c

## Purpose

`dbgp.c` implements the standalone EHCI Debug Port gadget `g_dbgp`. It is not a libcomposite gadget; it registers a raw `usb_gadget_driver` that responds to debug descriptors and enters debug mode through a standard SET_FEATURE request.

## Important APIs, Types, and Functions

Global `struct dbgp` stores the gadget, EP0 request, IN/OUT endpoints, and optional `gserial` state. Important functions are `dbgp_bind()`, `dbgp_unbind()`, `dbgp_setup()`, `dbgp_disconnect()`, `dbgp_configure_endpoints()`, and module init/exit. In `CONFIG_USB_G_DBGP_PRINTK` mode, `dbgp_enable_ep()`, `dbgp_enable_ep_req()`, `dbgp_complete()`, and `dbgp_consume()` receive OUT data and print it. In serial mode, `gserial_connect()` and `gserial_disconnect()` bridge endpoints to TTY.

## Control Flow

Init registers the gadget driver. Bind allocates an EP0 request buffer, optional serial object and tty line, autoconfigures two 8-byte bulk debug endpoints, and fills the USB debug descriptor. EP0 setup handles `GET_DESCRIPTOR` for device and debug descriptors and `SET_FEATURE USB_DEVICE_DEBUG_MODE`, which either enables printk receive requests or connects the serial function. Disconnect disables endpoints or disconnects serial; unbind frees EP0 and optional serial state.

## State and Persistence Behavior

The singleton `dbgp` object holds all runtime state. Endpoint descriptors are static but have endpoint addresses and max-packet values filled during autoconfiguration. Printk mode owns one queued OUT request at a time. Serial mode owns a tty line until module exit. Nothing is persisted.

## Dependencies and Integration Points

The file depends on low-level gadget APIs, Chapter 9 descriptors, optional `u_serial`, and EHCI debug-device semantics. It bypasses libcomposite because the debug device has specialized enumeration behavior.

## Risks and Test Signals

Risks include singleton assumptions, modifying the const control request length for oversized IN descriptors, endpoint enable/disable ordering, request lifetime in printk completion, and serial-line allocation/free balance. Tests should request device/debug descriptors, issue debug-mode SET_FEATURE, stream data in printk and serial modes, disconnect/reset repeatedly, verify endpoint max packet is 8, and unload after active debug traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/dbgp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/ether.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/ether.c

## Purpose

`ether.c` implements the legacy `g_ether` ethernet gadget. It provides CDC ECM, CDC subset/gether, CDC EEM, and optionally RNDIS configurations depending on Kconfig, controller capability, and module parameters.

## Important APIs, Types, and Functions

Core functions are `eth_bind()`, `eth_do_config()`, `rndis_do_config()`, `eth_unbind()`, and `has_rndis()`. It uses function instances for `"ecm"`, `"eem"`, `"geth"`, and `"rndis"`, gether helpers for MAC addresses, queue multiplier, netdev registration, and RNDIS netdev sharing through `rndis_borrow_net()`.

## Control Flow

Bind chooses the primary non-RNDIS mode: EEM if requested, ECM if the UDC supports it, otherwise CDC subset/gether. It obtains that function instance, applies ethernet module parameters, and, when RNDIS is compiled in, registers the shared netdev, obtains a RNDIS instance, borrows the same netdev, updates product IDs, and exposes two configurations with RNDIS first. It then allocates strings, optional OTG descriptor, adds RNDIS config if present, and adds the ethernet config. Config callbacks instantiate and add the selected function.

## State and Persistence Behavior

State is global per module: function instances/functions, static descriptors, `use_eem`, optional OTG descriptor, and network module parameters. The lower-level gether/netdev layer owns packet queues, MAC state, and link lifecycle. No persistent storage is used.

## Dependencies and Integration Points

The file depends on libcomposite, Linux networking, `u_ether`, `u_ecm`, `u_gether`, `u_eem`, optional `u_rndis`/`rndis`, and gadget capability detection. Host integration varies by configuration: CDC ECM/EEM, subset/SAFE, or RNDIS.

## Risks and Test Signals

Risks include mode-selection differences across UDCs, shared-netdev ownership when RNDIS and ECM/subset coexist, cleanup when one config add fails, host-driver compatibility tied to vendor/product IDs, and `use_eem` changing expected descriptors. Tests should cover ECM-capable and non-ECM controllers, EEM module parameter, RNDIS and non-RNDIS builds, MAC parameter validation, simultaneous host network traffic, config switching, OTG descriptors, and unload after interface up/down cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/ether.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/g_ffs.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/g_ffs.c

## Purpose

`g_ffs.c` implements the legacy FunctionFS gadget `g_ffs`. It waits for one or more userspace FunctionFS functions to become ready, then registers a composite gadget containing those userspace functions and optional ECM/RNDIS networking configurations.

## Important APIs, Types, and Functions

Important lifecycle functions are `gfs_init()`, `gfs_exit()`, `functionfs_ready_callback()`, `functionfs_closed_callback()`, `gfs_bind()`, `gfs_unbind()`, `gfs_do_config()`, `eth_bind_config()`, and `bind_rndis_config()`. It allocates `"ffs"` function instances, assigns FunctionFS device names through `ffs_single_dev()` or `ffs_name_dev()`, installs callbacks on `ffs_dev`, and conditionally obtains `"ecm"`, `"geth"`, and `"rndis"` instances.

## Control Flow

Module init normalizes the `functions=` module parameter, allocates per-configuration function arrays, creates one FunctionFS instance per named function, marks it non-configfs, and sets ready/closed/acquire/release callbacks. Each userspace FunctionFS mount calls the ready callback when descriptors are written. When all expected functions are ready, the callback registers the composite driver. If any FunctionFS closes, the close callback increments `missing_funcs` and unregisters the composite driver.

During bind, optional ethernet/RNDIS instances and netdev sharing are prepared, string IDs and OTG descriptors are allocated, and every enabled configuration is added. `gfs_do_config()` optionally adds networking first, then instantiates and adds each FunctionFS function for that configuration. It also clears the next interface array slot to avoid stale interface pointers after changing userspace descriptors.

## State and Persistence Behavior

Global state includes `missing_funcs`, `gfs_registered`, `gfs_single_func`, `fi_ffs`, `f_ffs`, optional network function instances/functions, static strings/descriptors, and OTG descriptor storage. FunctionFS descriptor/interface state is supplied by userspace and lives in `f_fs` data structures. No state is persisted by the kernel file; userspace must remount and rewrite descriptors.

## Dependencies and Integration Points

The file integrates libcomposite, FunctionFS, optional ethernet/RNDIS gether functions, module autoloading through the function registry, USB strings, OTG helpers, and userspace FunctionFS daemons. It is sensitive to `ffs_lock` context, as comments state callbacks and bind/unbind are called under FunctionFS locking.

## Risks and Test Signals

Risks include readiness accounting with multiple functions, composite register/unregister races on close, memory ownership across `f_ffs` matrix entries, stale interface pointers from prior FunctionFS descriptors, and error unwind for optional networking. Tests should run single and multi-function modes, close one FunctionFS while configured, use ECM-only/RNDIS-only/both/generic builds, verify interface arrays after descriptor shape changes, pass custom MACs, and unload while FunctionFS endpoints are mounted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/g_ffs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/gmidi.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/gmidi.c

## Purpose

`gmidi.c` implements the legacy `g_midi` composite gadget. It exposes a single USB MIDI function backed by ALSA raw MIDI support.

## Important APIs, Types, and Functions

Key functions are `midi_bind()`, `midi_bind_config()`, and `midi_unbind()`. The driver obtains a `"midi"` function instance, fills `struct f_midi_opts` with module parameters (`index`, `id`, `buflen`, `qlen`, `in_ports`, `out_ports`), assigns string IDs, adds one configuration, and releases function resources on unbind.

## Control Flow

Bind obtains the MIDI function instance, copies module parameter values into options, assigns manufacturer/product/configuration string IDs, adds `midi_config`, and applies composite overwrite options. The config callback obtains the concrete MIDI function and adds it. Unbind releases the function and function instance.

## State and Persistence Behavior

State is module parameters plus global function pointers. ALSA card, rawmidi endpoints, queues, and USB request state are owned by the lower-level MIDI function. No state is persisted by this file.

## Dependencies and Integration Points

It depends on libcomposite, ALSA init defaults, USB MIDI function options in `u_midi.h`, dynamic string IDs, and composite options. Host integration is through USB Audio/MIDI class descriptors created by the MIDI function.

## Risks and Test Signals

Risks include invalid queue/buffer/port parameter combinations, cleanup after config-add failure, and host compatibility tied to descriptor strings and vendor/product IDs. Tests should enumerate as a MIDI device, verify ALSA rawmidi ports match parameter counts, exercise IN and OUT MIDI traffic, vary queue/buffer lengths, and unload after active I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/gmidi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/hid.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/hid.c

## Purpose

`hid.c` implements the legacy `g_hid` composite gadget. Unlike configfs HID gadgets, this driver discovers HID function descriptors from platform data registered through a `hidg` platform device and builds a composite configuration containing one function per descriptor.

## Important APIs, Types, and Functions

`struct hidg_func_node` stores a HID function instance, concrete function, list node, and platform-provided `hidg_func_descriptor`. Core functions are `hidg_plat_driver_probe()`, `hidg_plat_driver_remove()`, `hid_bind()`, `do_config()`, `hid_unbind()`, `hidg_init()`, and `hidg_cleanup()`. It uses `usb_get_function_instance("hid")`, fills `struct f_hid_opts`, and adds each HID function to one configuration.

## Control Flow

Module init first probes the platform driver to collect HID descriptors, then registers the composite driver. Platform probe adds descriptors to `hidg_func_list`. Composite bind requires at least one descriptor, obtains a HID function instance for each node, copies subclass/protocol/report length/report descriptor into options, assigns strings, optionally creates an OTG descriptor, and registers one configuration. The configuration callback instantiates and adds every HID function, unwinding already added functions on failure. Cleanup unregisters composite and platform drivers.

## State and Persistence Behavior

The global `hidg_func_list` is populated from platform data and holds descriptor pointers, function instances, and concrete functions. USB string and OTG descriptor state are static globals. HID report descriptors come from platform data and must remain valid for the function lifetime. No persistent storage is used.

## Dependencies and Integration Points

It depends on libcomposite, platform-device infrastructure, `linux/usb/g_hid.h`, and `u_hid.h`. It integrates board/platform code that supplies HID descriptors with the USB HID function implementation and host HID class drivers.

## Risks and Test Signals

Risks include platform descriptor lifetime, no HID descriptors resulting in `-ENODEV`, global list cleanup removing all nodes on any platform remove, partial bind cleanup for multiple functions, and report descriptor validity. Tests should provide one and multiple platform HID descriptors, enumerate keyboard/mouse/vendor reports, validate report length, exercise read/write on `/dev/hidg*`, test OTG controllers, and remove platform devices or unload after enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/hid.c -->
