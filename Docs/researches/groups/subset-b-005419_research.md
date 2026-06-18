# Research: subset-b-005419 IPU7 ISYS CSI2, queue, video, MMU, and syscom sources

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi2-regs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi2-regs.h

## Purpose
Defines the IPU7/IPU7P5 CSI-2 input-system register map used by the CSI receiver, adapter layer, legacy interrupt controller, GP registers, PHY control, MIPI generator, and selected IS main blocks. It is a hardware contract header: no code executes here, but CSI2 enable/disable, IRQ handling, PHY programming, and test-pattern paths depend on these offsets and masks being exact.

## Important APIs, Types, and Constants
Important register base macros include `IS_MAIN_BASE`, `IS_IO_BASE`, `IS_IO_CDPHY_BASE(i)`, `IS_IO_CSI2_HOST_BASE(i)`, `IS_IO_CSI2_ADPL_PORT_BASE(i)`, `IS_IO_CSI2_ERR_LEGACY_IRQ_CTL_BASE(i)`, `IS_IO_CSI2_SYNC_LEGACY_IRQ_CTL_BASE(i)`, `IS_IO_CSI2_LEGACY_IRQ_CTRL_BASE`, `IS_IO_GPREGS_BASE`, `IS_IO_CSI2_GPREGS_BASE`, `PORT_ARB_BASE`, and `IS_IO_MGC_BASE`. Generic IRQ register offsets are `IRQ_CTL_*` plus IPU7P5-specific `IRQ1_CTL_*` for frame-end status. Masks such as `IPU7_CSI_IS_IO_IRQ_MASK`, `IPU7_CSI_ADPL_IRQ_MASK`, `IPU7_CSI_RX_LEGACY_IRQ_MASK`, `IPU7_CSI_RX_ERROR_IRQ_MASK`, `IPU7_CSI_RX_SYNC_IRQ_MASK`, and `IPU7P5_CSI_RX_SYNC_FE_IRQ_MASK` drive top-level and per-port ISR filtering. Enums `CSI_FE_MODE_TYPE`, `CSI_FE_INPUT_MODE`, `MGC_CSI_ADPL_TYPE`, and `CSI2HOST_SELECTION` describe PHY/input-generator mode values.

## Control Flow and State
This header participates in control flow through MMIO sites in `ipu7-isys-csi2.c` and `ipu7-isys.c`: stream enable writes adapter input mode, APB divider, aggregation, PHY/IRQ registers; stream disable clears IRQs and powers down PHY; ISYS setup enables firmware and CSI legacy interrupts; ISRs read and clear per-port legacy error/sync status. State is persisted only in device registers; the header itself has no runtime storage.

## Dependencies and Integration Points
The constants integrate with Linux `readl()`/`writel()` users, CSI PHY helpers, firmware response handling, and platform register definitions. Hardware-version conditionals in the driver interpret IPU7 versus IPU7P5 sync/FE masks differently, so tests and reviews must validate both register layouts.

## Risks and Test Signals
Offset mistakes can silently break stream bring-up, interrupt clearing, or PHY readiness. Notable review risks are duplicated macro names (`SCRAMBLING`, `SPARE_RW`, `SPARE_RO`) and several sync masks currently set to zero, which disables direct FS/FE legacy sync handling unless firmware SOF/EOF responses cover the path. Test signals are successful CSI stream-on/off on each port, correct receiver error logging, no interrupt storms after streamoff, and hardware trace showing expected writes to adapter, legacy IRQ, and PHY registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi2-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi2.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi2.c

## Purpose
Implements the IPU7 CSI-2 V4L2 subdevice: supported media-bus formats, event subscription, CSI receiver stream enable/disable, crop handling, stream routing, subdevice registration, SOF/EOF event delivery, and remote sensor frame descriptor lookup.

## Important APIs, Types, and Functions
The exported functions are `ipu7_isys_csi2_get_link_freq()`, `ipu7_isys_csi2_init()`, `ipu7_isys_csi2_cleanup()`, `ipu7_isys_csi2_sof_event_by_stream()`, `ipu7_isys_csi2_eof_event_by_stream()`, and `ipu7_isys_csi2_get_remote_desc()`. Internal operations are wired through `csi2_sd_core_ops`, `csi2_sd_pad_ops`, and `csi2_entity_ops`. `csi2_supported_codes[]` is the source list for `enum_mbus_code`. `csi2_irq_enable()` and `csi2_irq_disable()` program per-port legacy error/sync interrupt registers. `ipu7_isys_csi2_enable_streams()` and `ipu7_isys_csi2_disable_streams()` bridge V4L2 stream enablement to receiver power/IRQ setup and the upstream sensor subdevice.

## Control Flow
Initialization stores `isys`, base address, port, and hardware-specific legacy IRQ mask, initializes the shared `ipu7_isys_subdev`, finalizes V4L2 subdev state, and registers it. Stream enable powers the CSI block only on the first active stream, sets APB divider and adapter input mode, optionally enables port A/B aggregation on non-IPU7 hardware, powers the PHY through `ipu7_isys_csi_phy_powerup()`, enables legacy IRQs, resolves the routed upstream sink stream, and calls `v4l2_subdev_enable_streams()` on the remote sensor. Stream disable reverses the upstream call, decrements `stream_count`, and when it reaches zero powers down PHY and disables IRQs.

## State and Persistence Behavior
Persistent driver state is held in `struct ipu7_isys_csi2`: `base`, `port`, `nlanes`, `phy_mode`, `legacy_irq_mask`, `receiver_errors`, and `stream_count`. Crop and format state live in V4L2 subdev active state. SOF events atomically increment `stream->sequence`; EOF is logged but does not change sequence state. Hardware state persists in CSI and GP registers until streamoff or runtime suspend cleanup.

## Dependencies and Integration Points
Depends on media-controller graph helpers, V4L2 subdev streams/routing APIs, CSI PHY helpers, `ipu7-isys-subdev` format/routing helpers, and register constants from `ipu7-isys-csi2-regs.h`. It integrates with `ipu7-isys-video.c` through remote descriptor lookup and source stream metadata, with `ipu7-isys.c` through CSI error/SOF ISR handling, and with sensor drivers through `get_frame_desc` and stream enable operations.

## Risks and Test Signals
Risks include incomplete unwind if upstream stream enable fails after receiver hardware is already enabled, stream-mask handling that selects only the first set bit up to stream 63, zero sync masks that may make direct legacy FS/FE paths inactive, and crop logic allowing only vertical cropping while bayer order conversion still depends on top offset. Test with multiple virtual channels, sensors with and without `get_frame_desc`, bayer crop offsets, IPU7 and IPU7P5 IRQ masks, and repeated stream-on/off cycles watching PHY power and event sequence behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi2.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi2.h

## Purpose
Declares the CSI-2 receiver object and public CSI2 helper API for the IPU7 ISYS driver. It is the shared contract between CSI2 subdevice setup, video stream preparation, and top-level ISYS interrupt handling.

## Important APIs, Types, and Constants
Constants describe media topology limits: `IPU7_NR_OF_CSI2_VC` is 16, `IPU7_NR_OF_CSI2_SINK_PADS` is 1, `IPU7_NR_OF_CSI2_SRC_PADS` is 8, and `IPU7_CSI2_PAD_SINK`/`IPU7_CSI2_PAD_SRC` identify pad numbering. `INVALID_VC_ID` is used during stream initialization. `struct ipu7_isys_csi2` embeds the generic `ipu7_isys_subdev`, backpointers to platform and ISYS state, eight capture video nodes, MMIO base, receiver error accumulator, legacy IRQ mask, lane count, port number, PHY mode, and active stream count. Conversion macros `ipu7_isys_subdev_to_csi2()` and `to_ipu7_isys_csi2()` are used throughout the stream and ISR paths.

## Control Flow and State
The header does not execute code, but its fields are mutated by `ipu7_isys_csi2_init()`, async sensor binding, stream enable/disable, CSI PHY helpers, and ISRs. `stream_count` gates physical receiver power, `receiver_errors` accumulates legacy error bits until `ipu7_isys_csi2_error()` logs and clears them, and `legacy_irq_mask` maps top-level CSI IRQ status to this receiver instance.

## Dependencies and Integration Points
Includes `ipu7-isys-subdev.h` and `ipu7-isys-video.h`, so it couples CSI receivers to both V4L2 subdev state and capture queues. Exported APIs are consumed by `ipu7-isys.c`, `ipu7-isys-video.c`, and `ipu7-isys-queue.c` indirectly through stream setup.

## Risks and Test Signals
The object owns both subdevice and video-node arrays, so lifetime ordering matters: video cleanup and CSI subdev cleanup must not run while queued stream references remain. The VC limit must match remote CSI descriptors and firmware ABI expectations. Test signals include correct eight capture nodes per port, no stale `stream_count` after failed enable, valid VC rejection for `vc >= 16`, and clean cleanup after partial registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-queue.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-queue.c

## Purpose
Implements videobuf2 queue operations and the runtime bridge from user capture buffers to IPU7 ISYS firmware frame-buffer commands. It coordinates multi-output streams by collecting one buffer from every capture queue before sending a firmware capture request.

## Important APIs, Types, and Functions
Exported functions are `ipu7_isys_buffer_list_queue()`, `ipu7_isys_buffer_to_fw_frame_buff()`, `ipu7_isys_queue_buf_ready()`, and `ipu7_isys_queue_init()`. The `vb2_ops` table provides `queue_setup`, `buf_init`, `buf_prepare`, `buf_cleanup`, `start_streaming`, `stop_streaming`, and `buf_queue`. Important internals include `buffer_list_get()`, `ipu7_isys_stream_start()`, `ipu7_isys_link_fmt_validate()`, `return_buffers()`, `get_sof_sequence_by_timestamp()`, and `ipu7_isys_buf_calc_sequence_time()`.

## Control Flow
Buffer initialization maps the scatterlist into IPU DMA/IOMMU space and stores the DMA address in the per-buffer wrapper. `buf_queue()` adds the buffer to the queue's incoming list; once media pipeline and all stream queues are ready, it attempts to pull a synchronized list. If the firmware stream is not yet running, it calls `ipu7_isys_stream_start()`, otherwise it converts the list into an `ipu7_insys_buffset`, moves buffers to active lists before firmware submission, and sends `IPU_INSYS_SEND_TYPE_STREAM_CAPTURE`. `start_streaming()` builds the media pipeline, validates link format, prepares stream metadata, waits until all queues in the stream are streaming, opens firmware, sets up hardware, and starts the initial capture. `stop_streaming()` stops firmware/subdevices, drops stream references, returns active/incoming buffers with error, and closes firmware.

## State and Persistence Behavior
Each `ipu7_isys_queue` owns spinlock-protected `incoming` and `active` lists. `struct ipu7_isys_buffer` tracks list membership and `str2mmio_flag`, while `struct ipu7_isys_video_buffer` persists mapped DMA address. `stream->buf_id` generates modulo-256 firmware frame IDs and `stream->sequence`/`seq[]` map SOF timestamps to V4L2 sequence numbers. State transitions are list-based and must remain consistent under spinlocks and `stream->mutex`.

## Dependencies and Integration Points
Depends on videobuf2 DMA-SG memory ops, IPU DMA mapping helpers, firmware ABI structs, firmware command submission, media pipelines, V4L2 subdev format helpers, TSC timestamp conversion, and `ipu7-isys-video.c` for stream open/close and setup. Firmware responses return through `ipu7_isys_queue_buf_ready()` via output pin callbacks configured by video stream setup.

## Risks and Test Signals
Critical risks are buffer leaks or double completion on stream-start failure, races between firmware buffer-ready responses and active-list insertion, missing cleanup when `ipu7_get_fw_msg_buf()` fails inside `ipu7_isys_stream_start()`, and timestamp fallback when TSC is zero or SOF history misses. Tests should cover single and multi-output streams, queued buffers before stream-on, insufficient synchronized buffers, stream-on failure unwinds, firmware timeout paths, DMA map/unmap balance, and matching returned firmware pin addresses to active buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-queue.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-queue.h

## Purpose
Declares the videobuf2 queue wrappers, per-buffer state, grouped buffer-list abstraction, and queue-facing APIs used by IPU7 ISYS capture.

## Important APIs, Types, and Constants
`struct ipu7_isys_queue` embeds `struct vb2_queue`, a stream queue-node, device pointer, spinlock, incoming/active lists, and firmware output pin index. `struct ipu7_isys_buffer` is the list node plus an atomic error flag. `struct ipu7_isys_video_buffer` embeds `vb2_v4l2_buffer`, the ISYS buffer wrapper, and DMA address. Buffer-list flags `IPU_ISYS_BUFFER_LIST_FL_INCOMING`, `IPU_ISYS_BUFFER_LIST_FL_ACTIVE`, and `IPU_ISYS_BUFFER_LIST_FL_SET_STATE` control list requeue/completion behavior. Conversion macros map between vb2 queues, video objects, and buffer wrappers. Public functions expose list requeueing, firmware frame-buffer conversion, firmware-ready completion, and queue initialization.

## Control Flow and State
The header defines the state containers used by `ipu7-isys-queue.c`. Incoming buffers await synchronization across stream queues; active buffers have been submitted to firmware. A temporary `ipu7_isys_buffer_list` groups one buffer per active queue so the firmware command can describe all output pins for the same frame.

## Dependencies and Integration Points
Depends on Linux lists, spinlocks, atomics, `videobuf2-v4l2`, and forward declarations of firmware response/buffer set types. It is included by video and queue code, and its `fw_output` field is populated by firmware pin configuration in `ipu7-isys-video.c`.

## Risks and Test Signals
The data model assumes one DMA address per capture buffer and one active/incoming list membership at a time. Incorrect flag combinations can requeue buffers to the wrong list or complete them prematurely. Test signals are stable list lengths under stress, no WARNs from buffer-list count mismatches, correct error completion when `str2mmio_flag` is set, and valid `fw_output` indices for every configured output pin.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-subdev.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-subdev.c

## Purpose
Provides shared V4L2 subdevice helpers for IPU7 ISYS bridge entities: media-bus-code to MIPI data-type conversion, bayer format detection and order conversion, format propagation, route setup, active-state format lookup, and generic subdevice initialization/cleanup.

## Important APIs, Types, and Functions
Exports `ipu7_isys_mbus_code_to_mipi()`, `ipu7_isys_is_bayer_format()`, `ipu7_isys_convert_bayer_order()`, `ipu7_isys_subdev_set_fmt()`, `ipu7_isys_subdev_enum_mbus_code()`, `ipu7_isys_get_stream_pad_fmt()`, `ipu7_isys_subdev_set_routing()`, `ipu7_isys_subdev_init()`, and `ipu7_isys_subdev_cleanup()`. Internal `subdev_set_routing()` validates routing with one-to-one and no-source-multiplexing flags, normalizes source streams to zero, and installs a default 4096x3072 SGRBG10 format.

## Control Flow
Format setting clamps dimensions to ISYS bounds, selects the requested supported media-bus code or falls back to the first supported code, writes sink format state, propagates to the opposite source stream, and resets crop to the propagated frame. Source-pad `set_fmt` returns current format because the bridge does not transcode. Initialization allocates pads, marks sink pads as mandatory connections and source pads as outputs, initializes media entity pads, optionally initializes controls, and installs default subdev flags for devnode/events/streams.

## State and Persistence Behavior
Subdevice state is managed through V4L2 active state and media entity pad arrays allocated with devm. `asd->source` is initialized to -1 and later set by concrete subdevices such as CSI2. Crop reset happens whenever sink format changes; routing state persists in V4L2 subdev state.

## Dependencies and Integration Points
Depends on media-controller and V4L2 subdev streams APIs, MIPI CSI2 media-bus definitions, and ISYS min/max geometry constants. CSI2 subdevices reuse the pad ops for format, enum, and routing; video setup uses `ipu7_isys_get_stream_pad_fmt()` for link validation and firmware pin configuration.

## Risks and Test Signals
Risks include WARNs for unsupported bus codes, bayer order conversion only covering 8/10/12-bit bayer codes, crop pointers not checked before reset, and forced `source_stream = 0` simplifying routing in ways that may reject future multiplexed use cases. Test with invalid routes, multiple sink streams, format propagation across active routes, bayer crop parity, and all supported/non-supported media-bus codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-subdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-subdev.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-subdev.h

## Purpose
Declares the generic ISYS V4L2 subdevice wrapper and helper API shared by CSI2 and other IPU7 ISYS bridge subdevices.

## Important APIs, Types, and Constants
`struct ipu7_isys_subdev` embeds `struct v4l2_subdev`, links to the parent `ipu7_isys`, points to a zero-terminated supported-code array, owns media pads and an optional control handler, carries an optional control initializer, and records `source` as the SSI/CSI stream source. `to_ipu7_isys_subdev()` converts from a V4L2 subdev. Prototypes expose MIPI data-type conversion, bayer helpers, format/routing operations, active stream format retrieval, init, and cleanup.

## Control Flow and State
The header is a contract for concrete subdevices. Concrete users initialize `isys`, supported codes, optional control callbacks, and source IDs, then call `ipu7_isys_subdev_init()`. V4L2 active-state routing and formats drive later video setup and link validation.

## Dependencies and Integration Points
Includes media entity, V4L2 controls, and V4L2 subdev headers. CSI2 uses it directly, video code treats remote subdevices as `ipu7_isys_subdev`, and queue/video validation depends on its active-format helper.

## Risks and Test Signals
Because `supported_codes` is expected to be zero-terminated, missing a sentinel would overrun enumeration. `source` defaults to -1 and must be set before streaming. Test signals include correct devnode creation, mandatory sink pad flags, successful route initialization, clean control-handler cleanup, and correct source ID propagation into firmware stream setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-subdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-video.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-video.c

## Purpose
Implements IPU7 ISYS V4L2 capture video nodes, pixel-format negotiation, media link validation, firmware stream configuration/open/start/flush/close, shared stream allocation, runtime firmware open reference counting, and video device registration/cleanup.

## Important APIs, Types, and Functions
Exports `ipu7_isys_pfmts[]`, `ipu7_isys_get_isys_format()`, `ipu7_isys_video_prepare_stream()`, `ipu7_isys_put_stream()`, `ipu7_isys_query_stream_by_handle()`, `ipu7_isys_query_stream_by_source()`, `ipu7_isys_video_set_streaming()`, `ipu7_isys_fw_open()`, `ipu7_isys_fw_close()`, `ipu7_isys_setup_video()`, `ipu7_isys_video_init()`, and `ipu7_isys_video_cleanup()`. Internal V4L2 ioctls implement querycap, format enumeration, frame-size enumeration, get/try/set format, reqbufs, and create_bufs. Firmware helpers include `ipu7_isys_fw_pin_cfg()`, `start_stream_firmware()`, `stop_streaming_firmware()`, and `close_streaming_firmware()`.

## Control Flow
Format negotiation clamps geometry, aligns bytes-per-line to 64 bytes, maps V4L2 formats to media-bus codes and firmware frame formats, and adds an overshoot allowance to `sizeimage`. `ipu7_isys_setup_video()` resolves the remote CSI2 pad and external sensor, finds active route metadata, obtains CSI2 frame descriptors or falls back to media-bus-code MIPI type, starts/joins the media pipeline, and obtains a shared stream keyed by CSI source and virtual channel. `ipu7_isys_video_set_streaming(1)` opens firmware stream configuration, waits for open completion, submits the initial start-and-capture buffer set, waits for start ACK, then enables the connected subdevice stream. State 0 flushes firmware, disables the subdevice, closes the firmware stream, and drops open counts.

## State and Persistence Behavior
`struct ipu7_isys_video` stores current pixel format, capture queue, stream pointer, CSI2 pointer, current VC/DT, and `streaming` flag. Shared `struct ipu7_isys_stream` instances are allocated from the parent ISYS array with spinlock-protected refcounts and are reused by multiple queues on the same source/VC. Firmware open is reference-counted in `isys->ref_count`, protected by `isys->mutex`, and runtime PM is held while firmware is open. Completion objects in the stream persist across commands and are reinitialized before each wait.

## Dependencies and Integration Points
Depends on media-controller pipeline APIs, V4L2 ioctl/vb2 helpers, firmware ABI and command wrappers, CSI2 descriptor helpers, queue callbacks, runtime PM, PM QoS via top-level ISYS, and TSC support indirectly through queue timestamping. Firmware pin setup wires `stream->output_pins[pin].pin_ready` to `ipu7_isys_queue_buf_ready()`.

## Risks and Test Signals
Risks include `ipu7_isys_vidioc_s_fmt_vid_cap()` ignoring the return from try-format on busy queues, firmware open/stream completion timeouts leaving partially opened state, subdevice enable failure after firmware start requiring robust flush, and refcount misuse for shared streams. Test format alignment/overshoot, busy queue `S_FMT`, sensors with multi-entry frame descriptors sharing a VC, multi-video-node stream startup ordering, firmware open/start/flush/close timeout paths, runtime PM reference balance, and media link mismatch rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-video.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-video.h

## Purpose
Declares capture video-node state, firmware stream state, pixel-format descriptors, output-pin callbacks, and public video/firmware stream APIs for IPU7 ISYS.

## Important APIs, Types, and Constants
`IPU_INSYS_OUTPUT_PINS` is 11 and `IPU_ISYS_MAX_PARALLEL_SOF` is 2. `struct ipu7_isys_pixelformat` maps V4L2 pixel formats to bit depth, packed depth, media-bus code, and firmware frame format. `struct ipu7_isys_stream` models one firmware stream/CSI virtual channel with mutex, source entity, sequence and buffer counters, SOF timestamp ring, stream source/handle, output pins, queue counts, completions, parent pointer, error code, and VC. `struct ipu7_isys_video` wraps queue, mutex, media pad, video device, current pix format, parent ISYS, CSI2 receiver, stream pointer, streaming flag, VC, and DT.

## Control Flow and State
The header defines the shared state used by queue and video implementation. Queues call into video APIs to prepare streams and change streaming state; firmware ISRs use query helpers to find streams by handle or source/VC; pin-ready callbacks complete buffers. Sequence state and completion objects are long-lived per stream and reused across stream commands.

## Dependencies and Integration Points
Includes media entity and V4L2 device headers plus `ipu7-isys-queue.h`. It bridges `ipu7-isys.c`, `ipu7-isys-queue.c`, `ipu7-isys-video.c`, and CSI2 code. The firmware ABI defines concrete stream config, response, and format values consumed by these declarations.

## Risks and Test Signals
The SOF ring has only two entries, so high parallelism or delayed buffer-ready responses can fall back to current sequence. `output_pins` must be sized to firmware pin IDs and guarded in ISR. Tests should watch sequence/timestamp correctness under multiple in-flight frames, stream refcount lifetime, output pin index bounds, and cleanup of completion waiters during stream errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys.c

## Purpose
Implements the IPU7 ISYS auxiliary driver: probe/remove, media/V4L2 device registration, CSI2 and capture-node topology creation, async sensor binding, runtime/system PM, hardware IRQ setup/cleanup, firmware message-buffer pool management, CSI2 error handling, and top-level interrupt dispatch.

## Important APIs, Types, and Functions
Key internal subsystems are async notifier callbacks (`isys_notifier_bound()`, `isys_notifier_complete()`), device registration helpers (`isys_register_devices()`, `isys_register_video_devices()`, `isys_csi2_register_subdevices()`, `isys_csi2_create_media_links()`), PM hooks, firmware message-buffer pool functions (`alloc_fw_msg_bufs()`, `ipu7_get_fw_msg_buf()`, `ipu7_put_fw_msg_buf()`, `ipu7_cleanup_fw_msg_bufs()`), and ISR functions (`isys_isr()`, `isys_isr_one()`, `ipu7_isys_csi2_isr()`). Exported-to-local headers include `ipu7_isys_setup_hw()` and `isys_isr_one()`.

## Control Flow
Probe waits for IPU bus readiness, allocates `struct ipu7_isys`, powers the aux device, initializes MMU hardware, allocates CSI2 receivers and firmware message buffers, initializes firmware, registers media/video/CSI2 entities, initializes firmware logging, then releases runtime PM. Async binding parses firmware graph endpoints, links external sensor source pads to CSI2 sink pads, stores lane count and PHY mode, and registers subdev nodes. Stream startup from queue code later opens firmware and calls `ipu7_isys_setup_hw()`, which enables UC-to-SW and CSI legacy interrupts. The ISR checks power, reads CSI and firmware IRQ status, clears sources, dispatches per-port CSI handlers, drains firmware responses through `isys_isr_one()`, completes stream command completions, routes pin-ready events to queues, records SOF/EOF, logs errors, and loops until no handled status remains.

## State and Persistence Behavior
The parent state owns media/V4L2 devices, CSI2 array, stream array/refcounts, runtime power flag, IRQ masks, PM QoS request, firmware log, firmware message-buffer free/in-fw lists, async notifier, and subsystem config DMA pointer. Locks: `power_lock` protects power in ISR/PM, `streams_lock` protects stream refs, `listlock` protects firmware message pools, `mutex` protects firmware open refcount, and `stream_mutex` serializes stream start/stop around hardware/firmware transitions.

## Dependencies and Integration Points
Integrates with auxiliary bus, PCI media device registration, IPU bridge sensor discovery, V4L2 async notifier, CSI2/video/queue modules, firmware ISYS command/response code, IPU DMA allocator, MMU init/cleanup, PM runtime/QoS, buttress TSC sync, and platform/CSI register maps.

## Risks and Test Signals
Risks include partial probe unwind leaks, async binding ignoring the return from `isys_complete_ext_device_registration()` in the bound callback, ISR refcount churn while handling responses, firmware message buffers not returned on all command-failure paths, and suspend refusal based only on `stream_opened`. Test probe/remove cycles, missing graph endpoints, unsupported bus types, partial video/CSI registration failures, runtime suspend/resume during idle and active streaming, IRQ drain under multiple firmware responses, CSI receiver errors, and stream-opened suspend blocking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys.h

## Purpose
Declares the top-level IPU7 ISYS driver state, firmware message wrapper, async sensor connection metadata, global geometry/queue limits, and cross-file helper prototypes.

## Important APIs, Types, and Constants
Defines `IPU_ISYS_ENTITY_PREFIX`, `IPU_ISYS_MAX_STREAMS` as 16, firmware queue sizing constants, min/max image dimensions, and `FW_CALL_TIMEOUT_JIFFIES`. `struct isys_fw_log` tracks firmware log buffer state under a mutex. `struct ipu7_isys` owns media/V4L2 devices, bus device, power state and lock, CSI IRQ mask, stream array/refcounts, PHY flags, firmware open and stream-open counts, mutexes, platform data, CSI2 receivers, firmware log, request and firmware-message lists, PM QoS, async notifier, and subsystem config DMA. `struct isys_fw_msgs` stores one DMA-backed firmware command union plus list node and DMA address. Sensor async metadata stores CSI2 lane/port/bus information.

## Control Flow and State
This header describes state initialized in probe and consumed by video, queue, CSI2, firmware, and ISR paths. Firmware message buffers move between `framebuflist` and `framebuflist_fw`; streams move through refcounted allocation, command completions, and release; power and interrupt state are coordinated with runtime PM.

## Dependencies and Integration Points
Includes Linux locking/list/PM QoS primitives, media and V4L2 device/notifier types, firmware ABI headers, and CSI2/video declarations. Public functions are used by queue/video/firmware modules to obtain command buffers, return buffers, clean stale firmware buffers, handle one firmware ISR response, and set up hardware.

## Risks and Test Signals
Shared lists and refcounts are central correctness points. Risks include unsigned `ref_count` underflow if close paths mispair, stale `stream_opened` blocking suspend, firmware buffer union pointer assumptions in `ipu7_put_fw_msg_buf()`, and locks being acquired in inconsistent order across stream setup and ISR. Test with lockdep, repeated stream open/close, failed firmware command submissions, runtime PM transitions, and message-pool exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-mmu.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-mmu.c

## Purpose
Implements the IPU7 MMU/IOMMU page-table management and hardware initialization used by IPU child devices. It builds a two-level 4 KiB page-table hierarchy, maps and unmaps IOVA ranges, programs MMU/ZLX hardware blocks, invalidates TLBs, manages a trash-buffer IOVA range, and creates/destroys DMA mapping domains.

## Important APIs, Types, and Functions
Exported functions are `ipu7_mmu_hw_init()`, `ipu7_mmu_hw_cleanup()`, `ipu7_mmu_iova_to_phys()`, `ipu7_mmu_map()`, `ipu7_mmu_unmap()`, `ipu7_mmu_init()`, and `ipu7_mmu_cleanup()`. Important internals include `tlb_invalidate()`, dummy page/table allocation, `l2_map()`, `l2_unmap()`, `allocate_trash_buffer()`, `__mmu_at_init()`, `__mmu_zlx_init()`, `ipu7_mmu_alloc()`, `alloc_dma_mapping()`, and `ipu7_mmu_destroy()`.

## Control Flow
Initialization validates hardware variants, copies MMU block descriptors with MMIO base offsets, allocates an IOVA domain and `ipu7_mmu_info`, creates a dummy page, dummy L2 table, L1 table initialized to dummy L2, and per-L1 L2 pointer array. Runtime hardware init writes page-table base, user info bits, refill/collapse/ZLX configuration, TLB stream block sizes, UAO plane mappings, IRQ masks, allocates/maps the trash range if needed, and marks the MMU ready. Mapping validates alignment, allocates L2 tables on first use, maps them for DMA, writes L1/L2 PTEs, and flushes cache lines. Unmapping resets L2 entries to dummy page PTEs. TLB invalidation writes invalidate registers and polls completion while `ready` is true.

## State and Persistence Behavior
`ipu7_mmu_info` owns software page tables, dummy PTEs, aperture bounds, pgsize bitmap, lock, and DMA mapping backpointer. `ipu7_mmu` owns copied hardware descriptors, MMID, DMA mapping, trash page DMA/IOVA, ready flag/lock, and invalidate callback. Hardware register state persists between runtime PM init/cleanup; software tables persist until `ipu7_mmu_cleanup()`.

## Dependencies and Integration Points
Depends on PCI DMA mapping, Linux IOVA allocator, cache flushing, register constants from `ipu7-mmu.h`, platform secure-mode firmware address limits, and IPU DMA integration. ISYS runtime resume calls `ipu7_mmu_hw_init()` and suspend calls `ipu7_mmu_hw_cleanup()`.

## Risks and Test Signals
Risks include error unwind in `l2_map()` using adjusted `iova/paddr`, `ipu7_mmu_iova_to_phys()` assuming an allocated L2 table, cache coherency of page-table writes, trash-buffer cleanup correctness, and no explicit TLB invalidation inside map/unmap paths unless callers invoke the callback. Test aligned/unaligned map and unmap, crossing L1 boundaries, allocation failure unwind, secure vs non-secure apertures, runtime PM init/cleanup loops, TLB invalidate timeout logging, and IOVA-to-physical lookups for dummy/unmapped ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-mmu.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-mmu.h

## Purpose
Defines MMU, UAO, and ZLX register offsets/counts for IPU7, IPU7P5, and IPU8 variants, plus the software MMU state structures and public mapping API.

## Important APIs, Types, and Constants
Constants identify ISYS/PSYS MMIDs and many variant-specific block offsets: firmware read/write MMUs, data read/write MMUs, UAO planes, and ZLX blocks. Register offsets include `MMU_REG_INVALIDATE_*`, `MMU_REG_PAGE_TABLE_BASE_ADDR`, `MMU_REG_USER_INFO_BITS`, `MMU_REG_AXI_REFILL_IF_ID`, `MMU_REG_COLLAPSE_ENABLE_BITMAP`, `MMU_REG_INVALIDATION_STATUS`, IRQ registers, and ZLX config registers. `struct ipu7_mmu_info` stores L1/L2 page tables, dummy page/table PTEs, aperture, page-size bitmap, lock, and DMA mapping. `struct ipu7_mmu` stores hardware descriptors, MMID, DMA mapping, trash page state, ready lock, and TLB invalidation callback.

## Control Flow and State
The header state is allocated by `ipu7_mmu_init()`, programmed by `ipu7_mmu_hw_init()`, used by map/unmap callers, and freed by `ipu7_mmu_cleanup()`. Variant constants feed hardware descriptor construction elsewhere in the driver and are copied into per-device `ipu7_mmu_hw` arrays.

## Dependencies and Integration Points
Depends on Linux DMA/list/spinlock types and `ipu7_hw_variants` definitions from the broader IPU platform code. ISYS and PSYS bus devices use the same mapping API and hardware init/cleanup hooks.

## Risks and Test Signals
The header is dense hardware data; wrong stream counts or block register offsets cause memory translation failures that may look like firmware or DMA bugs. Test signals include successful MMU init on each supported hardware variant, correct L1/L2 block programming from descriptor counts, no out-of-bounds stream count rejection, and DMA capture buffers translating to expected physical pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-platform-regs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-platform-regs.h

## Purpose
Provides common IPU7 platform register offsets for ISYS/PSYS microcontroller control, firmware code/data bases, printf/logging registers, software interrupt controls, local DMEM/SPC offsets, CSI port count, PSYS IRQ controls, and PSYS buttress subdomain power masks.

## Important APIs, Types, and Constants
Key bases are `IS_BASE`, `IS_UC_CTRL_BASE`, `PS_BASE`, and `PS_UC_CTRL_BASE`. Interrupt definitions include `TO_SW_IRQ_MASK`, `TO_SW_IRQ_FW`, `IS_UC_TO_SW_IRQ_MASK`, `IPU_REG_PSYS_TO_SW_IRQ_CNTL_*`, and `IRQ_FROM_LOCAL_FW`. Firmware/debug offsets include `FW_CODE_BASE`, `FW_DATA_BASE`, `PRINTF_*`, and `LOCAL_DMEM_BASE_ADDR`. `IPU_ISYS_SPC_OFFSET`, `IPU7_PSYS_SPC_OFFSET`, `IPU_ISYS_DMEM_OFFSET`, and `IPU_PSYS_DMEM_OFFSET` describe local memory windows. `enum ipu7_device_buttress_psys_domain_pos` and power masks define PSYS subdomain control bits.

## Control Flow and State
The header contains no runtime code. `ipu7-isys.c` uses IS UC interrupt and printf offsets to set up hardware and service firmware IRQs. Firmware-loading and PSYS code elsewhere use the same base offsets and power masks.

## Dependencies and Integration Points
Depends on `BIT()` from Linux bit macros in including C files. It is included by ISYS queue/video/top-level code and MMU/platform code that needs shared IPU address layout.

## Risks and Test Signals
Wrong offsets can break firmware IRQ delivery, debug logging, or subdomain power sequencing. Test signals include firmware-to-host IRQs being observed and cleared, printf AXI control being programmed, PSYS power masks matching hardware generation, and no spurious IRQ after runtime suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-platform-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-syscom.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-syscom.c

## Purpose
Implements the small syscom queue helper layer used by IPU7 firmware communication. It obtains queue token pointers from shared memory ring buffers, advances read/write indices in MMIO-visible queue index memory, and locates queue configuration records after the firmware syscom config header.

## Important APIs, Types, and Functions
Exports `ipu7_syscom_get_token()`, `ipu7_syscom_put_token()`, and `ipu7_syscom_get_queue_config()` in the `INTEL_IPU7` namespace. Internal `ipu7_syscom_get_indices()` computes the per-queue index register block address from `ctx->queue_indices` and `sizeof(struct syscom_queue_indices_s)`.

## Control Flow
For output queues (`q < num_output_queues`), `get_token()` reads firmware write and driver read indices, returns NULL if empty, otherwise returns the token at `read_index`. For input queues, it returns NULL if advancing the write index would equal read index (full), otherwise returns the token at `write_index`. `put_token()` advances read index for output queues or write index for input queues modulo queue capacity. Queue config lookup returns the array immediately following `struct syscom_config_s`.

## State and Persistence Behavior
State is split between driver memory (`queue_configs`, token arrays) and MMIO/shared index memory (`queue_indices`). The helper does not lock; callers must serialize queue access if multiple contexts can touch the same queue. Indices persist in shared firmware-visible memory.

## Dependencies and Integration Points
Depends on firmware syscom ABI definitions and Linux MMIO accessors. Firmware ISYS response/command paths use this layer indirectly to exchange tokens with local firmware.

## Risks and Test Signals
Risks include no bounds checking for `q`, no memory barriers around token payload visibility beyond `readl()`/`writel()`, and caller-responsibility for concurrency. Test with empty/full ring edges, wraparound at `max_capacity`, invalid queue indices under defensive instrumentation, and firmware command/response stress where tokens are repeatedly acquired and released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-syscom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-syscom.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-syscom.h

## Purpose
Declares syscom queue configuration and context state plus public token queue APIs for IPU7 firmware communication.

## Important APIs, Types, and Constants
`struct syscom_queue_config` stores token array base, total queue size, token size, and max capacity. `struct ipu7_syscom_context` stores input/output queue counts, queue configs, shared queue indices MMIO pointer, DMA address of queue memory, CPU queue memory pointer, and queue memory size. Public functions are `ipu7_syscom_put_token()`, `ipu7_syscom_get_token()`, and `ipu7_syscom_get_queue_config()`.

## Control Flow and State
The header defines the context consumed by `ipu7-syscom.c`. Queue indices are maintained outside normal kernel heap state and must remain coherent with firmware. Token arrays are addressed by fixed-size offsets derived from queue config.

## Dependencies and Integration Points
Depends on Linux types and firmware syscom config forward declarations. It is used by firmware communication code under the `INTEL_IPU7` namespace and by bus/firmware setup code that allocates queue memory.

## Risks and Test Signals
The API assumes initialized queue counts, capacities, token sizes, and index memory. Bad configuration can produce out-of-bounds token pointers. Test signals include correct queue config parsing from firmware config memory, token pointer alignment, ring wraparound, and balanced get/put behavior across all configured input and output queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-syscom.h -->
