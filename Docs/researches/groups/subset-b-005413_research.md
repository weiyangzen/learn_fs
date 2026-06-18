# subset-b-005413 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-capture.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-capture.c

## Purpose

`imx-media-capture.c` builds the V4L2 video capture node used by i.MX media subdevices. It adapts a source subdevice pad into a `/dev/video*` receiver, owns the videobuf2 DMA-contiguous queue, exposes both media-controller-centric and legacy pre-MC ioctls, and starts or stops the upstream media pipeline on stream-on/off.

## Important APIs, Types, and Functions

`struct capture_priv` is the private object behind `struct imx_media_video_dev`; it stores the owning media device, source subdevice/pad, vb2 queue, ready buffer list, queue spinlock, mutex, optional inherited control handler, and legacy API flag. Public entry points are `imx_media_capture_device_init()`, `imx_media_capture_device_register()`, `imx_media_capture_device_unregister()`, `imx_media_capture_device_remove()`, `imx_media_capture_device_next_buf()`, and `imx_media_capture_device_error()`.

Format helpers include `capture_find_format()`, `__capture_try_fmt()`, and `__capture_legacy_try_fmt()`. Queue callbacks are `capture_queue_setup()`, `capture_buf_init()`, `capture_buf_prepare()`, `capture_buf_queue()`, `capture_start_streaming()`, and `capture_stop_streaming()`. The file exposes two ioctl tables: `capture_ioctl_ops` for MC users and `capture_legacy_ioctl_ops` for legacy direct sensor-style queries.

## Control Flow

Initialization allocates `capture_priv`, a video device, a single sink media pad, and a DMA-contiguous vb2 queue with MMAP and DMABUF support. Registration initializes the default format, registers the video device, creates the source-subdev-to-video-node pad link, and adds the video device to the media device master list.

For streaming, users queue buffers into `ready_q`. `capture_start_streaming()` validates the selected video format against the active source pad format and calls `imx_media_pipeline_set_stream()` on the source entity. Hardware-owning subdevices later fetch buffers through `imx_media_capture_device_next_buf()`. On stop, the pipeline is stopped and all remaining queued buffers are returned with `VB2_BUF_STATE_ERROR`.

## State and Persistence Behavior

There is no disk persistence. Runtime state is in the video-device format, compose rectangle, selected pixel-format descriptor, queued buffers, and inherited controls. `ready_q` is protected by `q_lock`; device operations use `mutex`. The vb2 owner is cleared at release. Format changes are blocked while the queue is busy.

## Dependencies and Integration Points

The file integrates with V4L2 video-device ioctls, media controller links, V4L2 events, vb2 DMA-contiguous memory, and upstream i.MX subdevices. CSI uses this capture node at its IDMAC source pad. The legacy API delegates frame size, interval, standard, and time-per-frame operations upstream to the source subdevice.

## Risks and Edge Cases

`capture_validate_fmt()` checks size and color-space class but not every bus-code detail, so bad upstream negotiations can still fail later in hardware. The memory cap divides by `pix->sizeimage`; callers depend on format initialization to avoid zero size. On pipeline start failure, buffers are returned as queued rather than error, which is consistent with vb2 start failure but important for user-space retry behavior. Legacy format enumeration depends on the active upstream format and may return only one format for raw/bayer passthrough.

## Test Signals

Exercise MC and legacy ioctls, busy-queue format rejection, format validation mismatch returning `-EPIPE`, buffer memory cap behavior, stream start failure cleanup, stream stop buffer return, event subscription for frame-interval errors, inherited controls in legacy mode, and DMABUF/MMAP queueing through a CSI IDMAC capture pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-csc-scaler.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-csc-scaler.c

## Purpose

`imx-media-csc-scaler.c` implements a V4L2 mem2mem video device for the i.MX IPUv3 Image Converter post-processor. It provides color-space conversion, scaling, cropping/composition, and rotation/flip controls over paired OUTPUT and CAPTURE queues.

## Important APIs, Types, and Functions

`struct ipu_csc_scaler_priv` owns the video node, media device pointer, V4L2 mem2mem device, and mutex. `struct ipu_csc_scaler_ctx` is per-open state with a V4L2 file handle, source/destination queue data, image-convert context, controls, rotation mode, and sequence counter. Public lifecycle functions are `imx_media_csc_scaler_device_init()`, `imx_media_csc_scaler_device_register()`, and `imx_media_csc_scaler_device_unregister()`.

Important callbacks are `device_run()`, `job_abort()`, `ipu_ic_pp_complete()`, `ipu_csc_scaler_try_fmt()`, `ipu_csc_scaler_s_fmt()`, `ipu_csc_scaler_s_selection()`, `ipu_csc_scaler_start_streaming()`, `ipu_csc_scaler_stop_streaming()`, and `ipu_csc_scaler_s_ctrl()`.

## Control Flow

Open allocates a context, initializes a mem2mem context with two vb2 DMA-contiguous queues, installs hflip/vflip/rotate controls, and seeds both queues with a 720x576 YUV420 format. Format try/set passes source and destination images through `ipu_image_convert_adjust()` to align sizes, strides, and rotation constraints. Streaming prepare waits until both queues are streaming, then calls `ipu_image_convert_prepare()` using `md->ipu[0]`.

When the mem2mem scheduler runs a job, `device_run()` reads the next source/destination buffers, allocates an `ipu_image_convert_run`, fills physical DMA addresses, and queues conversion. Completion removes both buffers, copies metadata, assigns matched sequence numbers, reports done or error based on `run->status`, finishes the mem2mem job, and frees the run object.

## State and Persistence Behavior

State is per-open context and per-device registration only. No settings persist beyond file lifetime. The active image-convert context exists only while both queues stream and is unprepared on streamoff. Rotation and flips can force queue format changes and are rejected with `-EBUSY` if already-allocated queues would need incompatible dimensions or strides.

## Dependencies and Integration Points

The driver depends on V4L2 mem2mem, vb2 DMA-contig, V4L2 controls/events, and IPUv3 image-convert APIs. The main `imx-media` platform driver creates and registers the device after async probe completion, once IPU handles have been recorded by CSI binding.

## Risks and Edge Cases

`ipu_image_from_q_data()` maps default quantization into `ycbcr_enc` in both colorimetry branches, which looks suspicious because quantization is not assigned in the second branch. The scaler assumes `md->ipu[0]` is present, so systems where only another IPU is populated may fail. `device_run()` allocates per job and must correctly clean up on queue failure; the error path completes both buffers as error. Capture colorimetry cannot be set independently by API design.

## Test Signals

Test paired stream-on ordering, queue allocation before and after rotation changes, crop/compose bounds and 8-pixel alignment, RGB/YUV conversions, sizeimage and bytesperline adjustment, hflip/vflip/90-degree rotations, abort while a conversion is active, conversion completion error status, and device registration after probe completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-csc-scaler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-csi.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-csi.c

## Purpose

`imx-media-csi.c` is the i.MX IPUv3 CSI subdevice driver. It negotiates a sink pad plus two source pads, routes incoming parallel/BT.656/MIPI CSI-2 data either directly to VDIC/IC or through SMFC/IDMAC to memory, owns capture-node creation for the IDMAC output, handles EOF interrupts, and supports frame skipping and frame interval monitoring.

## Important APIs, Types, and Functions

`struct csi_priv` contains the V4L2 subdevice, pads, async notifier, capture video device, frame interval monitor, IPU CSI/SMFC/IDMAC handles, active formats and color descriptors, crop/compose rectangles, skip pattern, double-buffered active vb2 buffers, underrun DMA buffer, routing state, IRQs, timer, controls, stream counter, and frame-sequence state.

Key functions include `csi_get_upstream_mbus_config()`, `requires_passthrough()`, `csi_idmac_setup_channel()`, `csi_idmac_start()`, `csi_idmac_stop()`, `csi_start()`, `csi_stop()`, `csi_set_fmt()`, `csi_set_selection()`, `csi_set_frame_interval()`, `csi_link_setup()`, `csi_registered()`, and `imx_csi_probe()`. IRQ handlers are `csi_idmac_eof_interrupt()` and `csi_idmac_nfb4eof_interrupt()`.

## Control Flow

Probe creates the subdevice, initializes three pads, assigns the IPU CSI group id, selects pinctrl, and registers an async notifier for the upstream endpoint. When registered with V4L2, the driver obtains the IPU CSI block, initializes default formats/frame intervals/crop/compose, creates a FIM instance, and registers a legacy capture node on the IDMAC output pad.

Link setup records one upstream source and one downstream sink. Source pad `CSI_SRC_PAD_IDMAC` requires a video node and selects `IPU_CSI_DEST_IDMAC`; source pad `CSI_SRC_PAD_DIRECT` accepts VDIC or IC subdevices. Stream-on asks the upstream entity for its media-bus config, selects the CSI input mux, starts upstream, optionally waits out initial BT.656 frames, starts SMFC/IDMAC for memory capture, programs CSI window/downsize/interface/destination/skip, enables FIM, and finally enables CSI.

IDMAC setup obtains SMFC and IDMAC resources, allocates an underrun buffer, seeds two hardware buffers from queued capture buffers or the underrun buffer, configures CPMEM format or passthrough, burst size, watermark/high-priority behavior, double buffering, and IRQs. EOF IRQ completes the current buffer, advances sequence, loads the next buffer, selects the new hardware buffer, toggles buffer index, and refreshes the timeout timer.

## State and Persistence Behavior

All state is runtime-only. The driver stores active pad formats, crop/compose, frame intervals, selected skip descriptor, active output pad, destination, upstream subdev, downstream sink, stream count, double-buffer state, and fatal/error flags. The lock protects pad/routing/stream state; `irqlock` protects EOF-side state. Hardware resources and coherent underrun memory are acquired on stream start and released on stop.

## Dependencies and Integration Points

CSI depends on platform IPU child data, media-controller graph links, V4L2 async/fwnode discovery, V4L2 subdev pad operations, vb2 capture helper APIs, IPUv3 CSI/SMFC/IDMAC/CPMEM helpers, pinctrl, IRQs, timers, and `imx-media-fim`. It binds into the parent `imx-media` device through group ids and triggers registration of internal IPU subdevices.

## Risks and Edge Cases

Several operations require upstream `get_mbus_config()`; missing support returns an error and blocks negotiation. Passthrough choices are subtle for raw/bayer, 16-bit parallel, and non-UYVY/YUYV 8-bit buses. EOF timeout calls `imx_media_capture_device_error()` and requires a stream restart. The stop path waits for one last EOF before disabling CSI to avoid documented hangs. Cropping for interlaced BT.656 is intentionally constrained. `vc_num` is stored but not clearly set in the visible code path, so virtual-channel routing deserves validation with CSI-2 graphs.

## Test Signals

Test parallel, BT.656/BT.1120, and MIPI CSI-2 inputs; raw passthrough and IPU YUV/RGB conversions; direct links to VDIC/IC; IDMAC capture with queued and underrun buffers; frame skipping ratios; crop/compose downscale by 1/2; interlaced and alternate fields; NFB4EOF marking; EOF timeout; last-EOF streamoff wait; missing upstream mbus-config; and link busy/error behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-csi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-dev-common.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-dev-common.c

## Purpose

`imx-media-dev-common.c` contains shared media-device orchestration for i.MX5/6/7 media drivers. It initializes the `media_device` and `v4l2_device`, completes async probe, creates late CSI-2 links, builds source-pad-to-video-device reachability lists, forwards subdevice events to reachable video nodes, and refreshes inherited controls when media links change.

## Important APIs, Types, and Functions

Exported functions are `imx_media_probe_complete()`, `imx_media_dev_init()`, and `imx_media_dev_notifier_register()`. Internal helpers include `imx_media_create_csi2_links()`, `imx_media_alloc_pad_vdev_lists()`, `imx_media_create_pad_vdev_lists()`, `imx_media_add_vdev_to_pad()`, `imx_media_inherit_controls()`, `imx_media_link_notify()`, and `imx_media_notify()`.

## Control Flow

Device initialization allocates `struct imx_media_dev`, sets model and bus info, installs media ops, initializes the media device and mutex, registers a V4L2 device, initializes the video-device list, and prepares the async notifier. Notifier registration fails if no async subdevices were queued, otherwise it installs supplied or default notifier ops.

Probe completion runs under `imxmd->mutex`: it creates missing fwnode links from the CSI-2 receiver to CSI or CSI mux subdevices, allocates per-pad video-device lists for all subdevices, walks each registered video node upstream to populate reachability lists, and registers subdevice nodes. After releasing the mutex it registers the media device.

## State and Persistence Behavior

There is no file persistence. Persistent runtime state is the `imx_media_dev` object, the master video-device list, per-subdevice `host_priv` arrays of `list_head`, and devm-managed `imx_media_pad_vdev` entries. Link notifications mutate video-device control handlers based on the active graph.

## Dependencies and Integration Points

This file ties together the media-controller graph, V4L2 async notifier, V4L2 controls, V4L2 subdev nodes, and `imx-media` event forwarding. It is called by the i.MX6 platform driver and can be reused by related SoC variants.

## Risks and Edge Cases

Reachability list construction assumes each capture video device has at least one entity link and uses the first one. `sd->host_priv` is repurposed for pad vdev lists, so other users must not rely on it. Control inheritance is recursively rebuilt on link changes; failures can leave video nodes without expected upstream controls. CSI-2 link creation is broad and relies on group ids being set correctly.

## Test Signals

Verify async completion with CSI, CSI mux, and CSI-2 graphs; subdev node registration; media device registration; control inheritance before/after link enable and disable; event forwarding from subdevs to video nodes; no-subdev notifier failure; and duplicate traversal avoidance in pad vdev lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-dev-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-dev.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-dev.c

## Purpose

`imx-media-dev.c` is the platform driver for the i.MX5/6 media controller instance compatible with `fsl,imx-capture-subsystem`. It creates the top-level `imx_media_dev`, registers CSI async subdevices from device tree, adds IPU-internal subdevices when CSI devices bind, and creates the mem2mem CSC/scaler after media probe completion.

## Important APIs, Types, and Functions

The main callbacks are `imx_media_probe()`, `imx_media_remove()`, `imx_media_subdev_bound()`, and `imx6_media_probe_complete()`. The notifier ops install `.bound` and `.complete`. The platform driver matches `fsl,imx-capture-subsystem` and uses helpers from `imx-media-dev-common.c`, `imx-media-of.c`, `imx-media-internal-sd.c`, and `imx-media-csc-scaler.c`.

## Control Flow

Probe initializes the common media device, parses `ports` phandles to add CSI async matches, and registers the async notifier. Each bound CSI subdevice causes synchronous registration and linking of IPU-internal subdevices for that CSI's IPU. Completion first calls common probe completion, then creates and registers the IPU IC post-processor mem2mem device under the media mutex.

Remove unregisters the mem2mem scaler if present, unregisters and cleans up the async notifier, unregisters IPU-internal subdevices, unregisters the media and V4L2 devices, and cleans up the media device.

## State and Persistence Behavior

State lives in the devm-allocated `imx_media_dev` attached to the platform device. The file records `m2m_vdev` after successful scaler creation. No configuration is persisted across driver unload/reload.

## Dependencies and Integration Points

This is the integration root for the IMX media stack. It depends on platform device probing, OF matching, V4L2 async notifier callbacks, common media-device helpers, internal IPU subdevice registration, and the CSC/scaler video-device lifecycle.

## Risks and Edge Cases

Failure after common device initialization must clean notifier, V4L2, and media-device state. If mem2mem scaler registration fails during completion, the media graph may already have been registered by the common complete handler, making error handling important for probe behavior. Internal subdevice registration only triggers for subdevices with CSI group ids.

## Test Signals

Test probe with missing/disabled CSI ports, async bind of one and two CSIs, failure in internal-subdev registration, common completion failure, scaler init/register failure, and remove after partial or full probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-fim.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-fim.c

## Purpose

`imx-media-fim.c` implements the i.MX Frame Interval Monitor. It observes EOF timestamps, compares averaged frame intervals against a nominal interval, and emits `V4L2_EVENT_IMX_FRAME_INTERVAL_ERROR` when timing drift exceeds configured tolerances. It also defines controls for enabling the monitor and tuning averaging, skip count, tolerance bounds, and optional input-capture parameters.

## Important APIs, Types, and Functions

`struct imx_media_fim` stores the owning subdevice, control handler, control clusters, spinlock-protected active values, counters, timestamp sum, nominal interval, input-capture completion, and stream state. Exported functions are `imx_media_fim_init()`, `imx_media_fim_free()`, `imx_media_fim_add_controls()`, `imx_media_fim_set_stream()`, and `imx_media_fim_eof_monitor()`.

Internal functions include `reset_fim()`, `update_fim_nominal()`, `frame_interval_monitor()`, `send_fim_event()`, `fim_acquire_first_ts()`, `fim_s_ctrl()`, and `init_fim_controls()`.

## Control Flow

Initialization allocates the FIM object and control handler. A CSI adds those controls to its subdevice handler when the IDMAC capture link is enabled. On stream-on, `imx_media_fim_set_stream()` locks the enable control, resets cached control values, computes the nominal microsecond frame interval from the active pad interval, and optionally waits for the first input-capture timestamp. EOF monitoring skips configured initial frames, computes absolute interval error from the previous timestamp, optionally ignores out-of-range errors above `tolerance_max`, averages `num_avg` samples, and notifies the subdevice if the average exceeds `tolerance_min`.

## State and Persistence Behavior

All state is volatile. Active control values are copied into the FIM state at reset so streaming behavior is stable. The spinlock protects timing counters and cached control values; the V4L2 control lock serializes stream-on changes with control writes. Input-capture edge changes are rejected while streaming.

## Dependencies and Integration Points

FIM depends on V4L2 custom controls from `media/imx.h`, V4L2 subdevice event notification, IRQ type values for optional input capture configuration, and CSI EOF callbacks. In this source snapshot only the EOF-monitor path is implemented; input capture controls and completion scaffolding exist but no event callback is wired in this file.

## Risks and Edge Cases

If the frame interval denominator is zero, FIM disables itself. EOF-derived timestamps include interrupt latency, so averaging is used to reduce noise but cannot eliminate systematic delay. `tolerance_max <= tolerance_min` disables the upper bound. Without input capture, `num_skip` is forced to at least one because the first EOF interval cannot be measured accurately.

## Test Signals

Test control defaults and clustering, enabling/disabling while idle and streaming, denominator-zero disabling, skip and averaging behavior, tolerance-min event generation, tolerance-max ignored samples, EOF timestamp jitter, event subscription on CSI/capture nodes, and attempted input-capture edge changes during streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-fim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-internal-sd.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-internal-sd.c

## Purpose

`imx-media-internal-sd.c` describes and registers the IPU-internal media topology behind each i.MX CSI. It creates synchronous VDIC and IC subdevices, records them per IPU, and creates static media links among CSI, VDIC, PRP, PRPENC, and PRPVF blocks.

## Important APIs, Types, and Functions

The file defines `struct internal_subdev`, `struct internal_pad`, and `struct internal_link` plus the `int_subdev[]` topology table. Exported functions are `imx_media_register_ipu_internal_subdevs()` and `imx_media_unregister_ipu_internal_subdevs()`. Internal helpers are `create_internal_link()` and `create_ipu_internal_links()`.

## Control Flow

When an async CSI binds, the parent calls `imx_media_register_ipu_internal_subdevs()`. The function derives the IPU from the CSI parent device, validates the IPU id, stores the `ipu_soc`, registers missing synchronous subdevices through their `sync_register` callbacks, then walks all internal source pads and creates media pad links to already-registered sinks. CSI entries themselves are not synchronously registered because they are the async-bound subdevices.

On registration failure it unwinds already-created synchronous subdevices for that IPU. Unregistration iterates both possible IPUs and all internal subdevice slots, calling each available `sync_unregister()`.

## State and Persistence Behavior

State is held in `imxmd->ipu[]` and `imxmd->sync_sd[2][NUM_IPU_SUBDEVS]`. The topology table is static. No persistent storage is used. Registration drops the media mutex around subdevice register/unregister callbacks to avoid lock inversion with V4L2 registration internals.

## Dependencies and Integration Points

This file integrates the common media device with `imx_media_vdic_register()`, `imx_media_ic_register()`, and their unregister counterparts. It depends on IPUv3 device data, media pad link creation, group ids from `media/imx.h`, and pad constants from `imx-media.h`.

## Risks and Edge Cases

The link table assumes pad indexes and group ids stay synchronized with the subdevice implementations. `imx_media_unregister_ipu_internal_subdevs()` does not clear `sync_sd` entries after unregistering, which is safe only if the surrounding device is being torn down and no re-registration occurs. Link creation skips existing links, making repeated CSI binds idempotent for links.

## Test Signals

Test single and dual IPU registration, repeated CSI binding on the same IPU, invalid IPU device/id errors, failures from VDIC or IC registration, link creation idempotence, unwind behavior, and remove-time unregister ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-internal-sd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-of.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-of.c

## Purpose

`imx-media-of.c` parses the top-level i.MX capture subsystem device-tree node and adds CSI nodes referenced by its `ports` phandle array to the media device async notifier.

## Important APIs, Types, and Functions

The exported function is `imx_media_add_of_subdevs()`. Its helper `imx_media_of_add_csi()` validates availability and adds a fwnode async connection with `v4l2_async_nf_add_fwnode()`.

## Control Flow

`imx_media_add_of_subdevs()` iterates `of_parse_phandle(np, "ports", i)` until no phandle is found. Each CSI node is passed to `imx_media_of_add_csi()`, then released with `of_node_put()`. Disabled nodes and duplicates are treated as nonfatal and skipped; other errors abort parsing.

## State and Persistence Behavior

No local persistent state exists. The effect is to populate `imxmd->notifier.waiting_list` with fwnode matches. All node references obtained during parsing are released before returning.

## Dependencies and Integration Points

This file depends on Open Firmware graph/device APIs and V4L2 async notifier fwnode matching. The top-level platform driver calls it during probe before registering the notifier.

## Risks and Edge Cases

If all ports are disabled or duplicate, the later notifier registration path fails with "no subdevs". Device-tree schema mistakes in the `ports` phandle array directly prevent media graph discovery. The code only adds CSI nodes listed by phandle; it does not recursively discover arbitrary OF graph endpoints.

## Test Signals

Test no `ports`, disabled CSI nodes, duplicate phandles, valid one/two CSI phandles, malformed phandle references, and notifier registration after this parser returns an empty waiting list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-utils.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-utils.c

## Purpose

`imx-media-utils.c` provides shared format, colorimetry, DMA-buffer, naming, pipeline traversal, video-device registration-list, and stream-control helpers for the i.MX media stack.

## Important APIs, Types, and Functions

The central data table is `pixel_formats[]`, containing supported V4L2 FourCCs, media bus codes, bits-per-pixel, color spaces, planar/raw/IPU-internal flags, and parallel-bus cycle counts. Exported format helpers are `imx_media_find_pixel_format()`, `imx_media_find_mbus_format()`, `imx_media_enum_pixel_formats()`, `imx_media_enum_mbus_formats()`, `imx_media_init_mbus_fmt()`, `imx_media_init_state()`, `imx_media_try_colorimetry()`, and `imx_media_mbus_fmt_to_pix_fmt()`.

Other exports include `imx_media_alloc_dma_buf()`, `imx_media_free_dma_buf()`, `imx_media_grp_id_to_sd_name()`, `imx_media_add_video_device()`, `imx_media_pipeline_pad()`, `imx_media_pipeline_subdev()`, and `imx_media_pipeline_set_stream()`.

## Control Flow

Format find/enumeration functions filter `pixel_formats[]` by YUV/RGB/Bayer/IPU selectors and optional media-bus code. `imx_media_init_mbus_fmt()` initializes a default media-bus frame format and colorimetry. `imx_media_mbus_fmt_to_pix_fmt()` maps media-bus format to a V4L2 pixel format, rounds width and stride for IDMAC burst/alignment requirements, and computes `sizeimage`.

Pipeline helpers recursively traverse enabled links upstream or downstream to find pads or subdevices by group id or video buffer type. `imx_media_pipeline_set_stream()` starts a media pipeline under `graph_mutex`, calls the starting subdevice's `s_stream()`, and rolls back the pipeline on failure; stop calls `s_stream(0)` and stops the active media pipeline.

## State and Persistence Behavior

The file has no mutable global state beyond the static format table. DMA helpers allocate/free coherent memory into caller-owned `imx_media_dma_buf` records. `imx_media_add_video_device()` mutates the media device's master video-device list under mutex.

## Dependencies and Integration Points

Utilities are used by capture, CSI, VDIC, MIPI CSI-2, device-common code, and the mem2mem scaler. They depend on V4L2 media bus/pixel format definitions, media graph traversal APIs, DMA coherent allocation, IPUv3 colorspace constants, and group ids from `media/imx.h`.

## Risks and Edge Cases

Duplicate `V4L2_PIX_FMT_XRGB32` entries exist for regular and IPU-internal RGB32, so selectors must include/exclude `PIXFMT_SEL_IPU` correctly. Recursive graph traversal assumes acyclic active media pipelines. The quantization and colorimetry defaults are derived from format color space and may surprise raw formats. `imx_media_mbus_fmt_to_pix_fmt()` rounds visible width up to burst width, so compose rectangles must preserve original source dimensions where needed.

## Test Signals

Test enumeration ordering and selector filters, media-bus-code-filtered FourCC enumeration, default mbus initialization, unsupported code rejection, stride/sizeimage rounding for planar and packed formats, DMA allocation/free reuse, group-id naming, upstream/downstream graph traversal, and stream start rollback on subdevice failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-vdic.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-vdic.c

## Purpose

`imx-media-vdic.c` implements the IPUv3 VDIC deinterlacer as a V4L2 subdevice. It supports a direct CSI-to-VDIC path for high-motion mode and an indirect memory-to-VDIC path using three IDMAC input channels for previous/current/next fields.

## Important APIs, Types, and Functions

`struct vdic_priv` stores the subdevice, pads, IPU/VDI resources, three IDMAC channels, active input pad, pipeline ops, field buffer bookkeeping, source/sink entities, pad formats, frame intervals, optional IDMAC input capture video device, motion control, and stream count. Public functions are `imx_media_vdic_register()` and `imx_media_vdic_unregister()`.

Important internals include `vdic_get_ipu_resources()`, `setup_vdi_channel()`, `vdic_setup_direct()`, `vdic_setup_indirect()`, `vdic_start()`, `vdic_stop()`, `vdic_s_stream()`, `vdic_set_fmt()`, `vdic_link_setup()`, `vdic_link_validate()`, and frame interval get/set callbacks.

## Control Flow

Registration creates a three-pad subdevice: direct sink, IDMAC sink, and direct source. Registered initialization assigns default formats and frame intervals and creates the deinterlacing-mode menu control. Link setup enforces a single source and sink. The direct sink must connect from a CSI direct source pad; the IDMAC sink must connect from a video device; the source must connect to a downstream subdevice.

On stream-on, the driver chooses direct or indirect ops from link state, obtains VDI and any required IDMAC channels, configures VDI for UYVY 4:2:2 processing at the active input dimensions, sets field order and motion mode, runs path-specific setup, enables VDI, starts channels, and optionally starts upstream CSI for direct mode.

## State and Persistence Behavior

State is runtime-only and protected by `lock`. Active pad formats and intervals persist while the subdevice is registered. Hardware resources are acquired during streaming and released on streamoff. Motion mode cannot change while streaming.

## Dependencies and Integration Points

VDIC is synchronously registered by `imx-media-internal-sd.c`. It integrates with CSI direct links, IC downstream links, V4L2 controls, media pad validation, IPUv3 VDI, FSU links, CPMEM, and IDMAC. It reuses format/colorimetry helpers from `imx-media-utils.c`.

## Risks and Edge Cases

Direct CSI mode is validated to require `HIGH_MOTION`; low and medium motion need three fields and are unsupported without memory input. Indirect path buffer fields are partly scaffolded in this file, but no vb2 queue handling is visible here, so consumers must ensure the IDMAC input path supplies buffers through the broader graph. Width is limited to 968 and aligned to 16 pixels. Output is always progressive.

## Test Signals

Test direct CSI link validation for high versus low/medium motion, indirect IDMAC-link validation, interlaced input field enforcement, progressive source output, frame interval doubling in direct mode, motion-control busy rejection, resource acquisition failure cleanup, and stream count behavior across repeated stream-on/off calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-vdic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media.h

## Purpose

`imx-media.h` is the shared private header for the i.MX5/6 media stack. It defines pad indexes, internal subdevice indexes, common pixel-format and video-device structures, the top-level `imx_media_dev`, DMA buffer records, helper inlines, and cross-file function prototypes.

## Important APIs, Types, and Functions

Important enums define IPU internal subdevice slots (`IPU_CSI0`, `IPU_CSI1`, `IPU_VDIC`, `IPU_IC_PRP`, `IPU_IC_PRPENC`, `IPU_IC_PRPVF`) and pad indexes for CSI, VDIC, PRP, and PRPENC/VF. `struct imx_media_pixfmt` describes FourCC/media-bus-code mappings, bpp, bus cycles, colorspace, planar/bayer/IPU flags. `enum imx_pixfmt_sel` provides format selection masks.

`struct imx_media_video_dev` wraps a V4L2 video device, active pixel format, compose rectangle, pixel-format descriptor, and list node. `struct imx_media_dev` embeds `media_device`, `v4l2_device`, the shared media pipeline, mutex, video-device list, IPU handles, async notifier, mem2mem video device, and registered synchronous subdevices. The header prototypes utilities, device-common functions, FIM, internal subdevice registration, OF parsing, VDIC, IC, capture, and CSC/scaler entry points.

## Control Flow

The header does not execute control flow directly, but it encodes the contracts that make graph construction and streaming work across files. Pad indexes are consumed by media link creation and subdevice ops. `to_imx_media_vb()` converts vb2 buffers to the driver buffer wrapper. `to_pad_vdev_list()` accesses per-pad reachable video-device lists stored in a subdevice's `host_priv`.

## State and Persistence Behavior

The defined structures hold runtime state only. The header sets the default frame size and EOF timeout constants used by multiple drivers. No persistent storage or static mutable data is introduced here.

## Dependencies and Integration Points

It includes Linux platform-device, V4L2 controls/devices/fwnode/subdev headers, vb2 DMA-contig, and IPUv3 definitions. All IMX media implementation files depend on this header for shared structures, pad constants, and function declarations.

## Risks and Edge Cases

Changing enum order or pad constants can silently break internal link tables and subdevice ops. `to_pad_vdev_list()` depends on `sd->host_priv` being owned by imx-media common code. The header exposes many cross-file APIs without namespace isolation beyond `imx_media_*`, so lifecycle expectations must be kept consistent manually.

## Test Signals

Compile coverage is the main signal: all IMX media objects must agree on pad constants, struct fields, and prototypes. Runtime graph tests that exercise CSI, VDIC, IC, capture, FIM, and scaler together validate this header's shared contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx6-mipi-csi2.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx6-mipi-csi2.c

## Purpose

`imx6-mipi-csi2.c` implements the i.MX6 MIPI CSI-2 receiver bridge subdevice. It exposes one sensor sink pad and four virtual-channel source pads, configures the DesignWare CSI-2 D-PHY/controller, handles fwnode async binding to the upstream sensor, and forwards a single negotiated media-bus format to all source pads.

## Important APIs, Types, and Functions

`struct csi2_dev` stores the subdevice, async notifier, five pads, D-PHY/reference/pixel clocks, MMIO base, remote source subdevice and pad, configured data lanes, mutex, active format, stream count, active source, and source-pad link bitmap. Important functions include `csi2_start()`, `csi2_stop()`, `csi2_s_stream()`, `csi2_link_setup()`, `csi2_set_fmt()`, `csi2_registered()`, `csi2_async_register()`, and `csi2_probe()`.

Hardware helpers include `csi2_enable()`, `csi2_set_lanes()`, `dw_mipi_csi2_phy_write()`, `csi2_dphy_init()`, `csi2_dphy_wait_stopstate()`, `csi2_dphy_wait_clock_lane()`, `csi2ipu_gasket_init()`, and `csi2_get_active_lanes()`.

## Control Flow

Probe initializes the subdevice, pads, clocks, MMIO, mutex, enables reference and D-PHY clocks, parses endpoint lane count, creates an async remote sensor match, and registers the subdevice. On bound, it records the remote source pad and creates fwnode links to the CSI-2 sink.

Stream-on requires a linked upstream source and at least one enabled source pad. It enables the pixel clock, programs the CSI2IPU gasket for YUYV ordering when needed, derives D-PHY hs-freq-range from the source `V4L2_CID_LINK_FREQ` or a default 849 Mbps/lane, chooses active lane count from remote mbus config, deasserts CSI-2 resets, asks the sensor to enter manual LP-11 pre-stream state, waits for LP-11, starts upstream streaming, and waits for clock-lane high-speed activity. Streamoff stops upstream, calls `post_streamoff`, asserts resets, and disables the pixel clock.

## State and Persistence Behavior

State is volatile and protected by `lock`. The active format is shared by all pads; source pads mirror sink format. `stream_count` reference-counts nested stream users. Reference and D-PHY clocks stay enabled for the registered device lifetime, while pixel clock is enabled only while streaming.

## Dependencies and Integration Points

The driver depends on platform OF matching (`fsl,imx6-mipi-csi2`), V4L2 fwnode endpoint parsing, V4L2 async notifier, media-controller links, subdev pre/post stream hooks, clocks, MMIO polling, and IMX format initialization helpers. Downstream CSI devices are linked by common imx-media completion code.

## Risks and Edge Cases

If the source lacks `V4L2_CID_LINK_FREQ`, the default D-PHY frequency may be wrong for some sensors. LP-11 wait timeout only warns, but capture may fail later. Clock-lane timeout is fatal. `v4l2_set_subdevdata(&csi2->sd, &pdev->dev)` stores the device pointer rather than `csi2`; local callbacks use container-of on `sd`, so this is only risky for external users of subdevdata. Multiple source pads can be enabled independently but all share one format and one upstream stream.

## Test Signals

Test endpoint parsing for lane counts, remote mbus lane overrides, link-frequency-based D-PHY selection, missing link-frequency default, YUYV gasket programming, LP-11 warning path, clock-lane timeout cleanup, source-pad link requirements, stream reference counting, and remove cleanup of notifier/clocks/media entity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx6-mipi-csi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/Kconfig

## Purpose

`drivers/staging/media/ipu3/Kconfig` declares the build-time configuration symbol for the Intel IPU3 ImgU staging driver.

## Important APIs, Types, and Functions

The only symbol is `VIDEO_IPU3_IMGU`, a tristate option labeled "Intel ipu3-imgu driver". It depends on `PCI`, `VIDEO_DEV`, and `X86`, and selects `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, `IOMMU_IOVA`, and `VIDEOBUF2_DMA_SG`.

## Control Flow

Kconfig has no runtime control flow. During kernel configuration, selecting this option enables the corresponding Makefile object aggregation and eventually builds the `ipu3-imgu` module or built-in driver.

## State and Persistence Behavior

The selected value persists only in the kernel build configuration, such as `.config`. It creates no runtime state by itself.

## Dependencies and Integration Points

This config integrates the IPU3 staging media driver with the kernel media, V4L2, PCI, x86, IOMMU IOVA, and scatter-gather vb2 subsystems. The help text identifies Skylake/Kaby Lake SoCs with MIPI cameras and names the module `ipu3-imgu`.

## Risks and Edge Cases

The x86 and PCI dependencies prevent accidental builds on unsupported architectures. Because this is a staging driver, API churn and incomplete hardware coverage are plausible. Missing selected dependencies would surface as build failures in IPU3 objects.

## Test Signals

Test `allyesconfig`/`allmodconfig` style builds on x86, dependency exclusion on non-x86 or no-PCI configs, module build as `M`, built-in build as `Y`, and presence of the expected `ipu3-imgu` module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/Makefile

## Purpose

`drivers/staging/media/ipu3/Makefile` defines the object composition for the Intel IPU3 ImgU staging driver.

## Important APIs, Types, and Functions

The Makefile appends IPU3 component objects to `ipu3-imgu-objs`: `ipu3-mmu.o`, `ipu3-dmamap.o`, `ipu3-tables.o`, `ipu3-css-pool.o`, `ipu3-css-fw.o`, `ipu3-css-params.o`, `ipu3-css.o`, `ipu3-v4l2.o`, and `ipu3.o`. It builds `ipu3-imgu.o` when `CONFIG_VIDEO_IPU3_IMGU` is enabled.

## Control Flow

There is no runtime control flow. Kbuild uses this file to combine the listed objects into the single IPU3 ImgU driver object and then link it as a module or built-in according to the Kconfig tristate.

## State and Persistence Behavior

No runtime state is stored. Build artifacts are generated by Kbuild from the listed object files.

## Dependencies and Integration Points

The Makefile pairs directly with the `VIDEO_IPU3_IMGU` Kconfig symbol. It integrates lower-level MMU/DMA/CSS firmware/parameter/table code with the V4L2-facing IPU3 entry points into one driver.

## Risks and Edge Cases

Object ordering matters when initialization dependencies or link-time symbol resolution rely on earlier objects. Missing any listed source file breaks the build. Adding new IPU3 components requires updating this aggregation list.

## Test Signals

Test module and built-in builds with `CONFIG_VIDEO_IPU3_IMGU`, clean builds after touching individual component sources, and link failure detection when component objects are renamed or removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/Makefile -->
