# subset-b-004190 research

Grouped research report for Vivid media test-driver controls, streaming worker threads, metadata, OSD, radio/RDS, SDR, touch, and VBI support files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-ctrls.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-ctrls.c

Purpose: implements the V4L2 control surface for the Vivid virtual media driver. It defines the custom Vivid control IDs, control configurations, control callbacks, control handler construction, handler sharing between video/radio/SDR/meta/touch devices, and teardown for all per-instance control handlers.

Important APIs and functions: exported APIs are `vivid_create_controls` and `vivid_free_controls`. Important callbacks are `vivid_user_gen_s_ctrl`, `vivid_fb_s_ctrl`, `vivid_user_vid_g_volatile_ctrl`, `vivid_user_vid_s_ctrl`, `vivid_vid_cap_s_ctrl`, `vivid_vbi_cap_s_ctrl`, `vivid_vid_out_s_ctrl`, `vivid_streaming_s_ctrl`, `vivid_sdtv_cap_s_ctrl`, `vivid_radio_rx_s_ctrl`, `vivid_radio_tx_s_ctrl`, `vivid_sdr_cap_s_ctrl`, and `vivid_meta_cap_s_ctrl`. The file also owns many `struct v4l2_ctrl_config` definitions for Vivid-specific menus, buttons, arrays, rectangles, HDMI/S-video routing menus, image-generation controls, error injection controls, radio RDS controls, SDR deviation, and metadata flags.

Control flow: `vivid_create_controls` initializes a separate `v4l2_ctrl_handler` for each functional node, creates common class controls, conditionally creates controls based on device capabilities and module options, checks handler errors, clusters related controls such as auto-gain and selected SDTV/DV timing controls, and then adds common handlers into device-specific handlers. Runtime `s_ctrl` callbacks translate control changes into `struct vivid_dev` state, test-pattern-generator settings, source-change events, queue errors, CEC/HDMI hotplug state, radio RDS mode changes, and metadata generation flags. `VIVID_CID_DISCONNECT` clears `V4L2_FL_REGISTERED` on all enabled video devices and wakes events, which emulates device removal.

State and persistence: all state is volatile per `struct vivid_dev`. Controls persist only while the vivid instance exists. Important state updates include input brightness arrays, test pattern generator settings, hotplug/power-present masks, HDMI/S-video output-to-input mappings, sequence and timestamp wrap injection, queue error flags, RDS capability mode flags, and metadata PTS/SCR booleans. `vivid_free_controls` releases every handler owned by the device.

Dependencies and integration points: depends on V4L2 control/event/common APIs, Vivid core structures, video capture/output helpers, radio common helpers, and OSD helpers. It integrates with videobuf2 through queue-error injection, with the test pattern generator through `tpg_s_*` setters, with HDMI/CEC state through output routing controls and CEC physical-address invalidation, with workqueues for HDMI/S-video control menu refresh, and with every Vivid video_device by assigning `ctrl_handler`.

Risks: this file is a central coupling point for most Vivid features, so missing capability checks or handler sharing mistakes can break unrelated device nodes. The HDMI/S-video routing controls mutate global skip masks and cross-instance pointers under spinlocks and queued work; ordering bugs can leave menus or hotplug state stale. Error injection controls intentionally make queues fail and can disrupt compliance tests unless `no_error_inj` is used. Some controls are created conditionally but grabbed later by streaming threads, so NULL-safe `v4l2_ctrl_grab` behavior is important. Disconnect intentionally leaves devices registered in the kernel object model but not V4L2-registered, which is a deliberate test behavior.

Test signals: strong signals are `v4l2-compliance` across all enabled node types with and without error injection, control enumeration/get/set coverage, auto-cluster behavior, HDMI/S-video loopback routing tests, CEC hotplug/source-change event observation, queue-error injection behavior, and RDS control/block-I/O mode switching. Build coverage should include configurations with and without media controller and OSD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-ctrls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-ctrls.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-ctrls.h

Purpose: declares the Vivid control subsystem entry points and the hardware seek mode enum shared with radio receiver code.

Important APIs and types: `enum vivid_hw_seek_modes` defines bounded seek, wraparound seek, and both-capability seek modes. `vivid_create_controls` builds all V4L2 control handlers for a Vivid instance, and `vivid_free_controls` releases them.

Control flow: Vivid core initialization calls `vivid_create_controls` after device capabilities have been populated. Teardown calls `vivid_free_controls` before the device object is destroyed.

State and persistence: the header stores no state. The implementation uses the passed `struct vivid_dev` to allocate and attach volatile `v4l2_ctrl_handler` state.

Dependencies and integration points: consumers must already know `struct vivid_dev`; the header is included by core, radio, streaming, and node setup code that needs seek modes or control lifecycle functions.

Risks: the public create API takes several capability booleans, so caller and implementation must stay aligned as new node types or controls are added.

Test signals: compile coverage for all Vivid configurations and runtime initialization of all enabled node combinations validate this boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-ctrls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-cap.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-cap.c

Purpose: implements the shared capture-side kernel thread for Vivid video capture, VBI capture, and metadata capture. It schedules frame ticks, fills video test-pattern buffers or looped output buffers, processes VBI and metadata buffers, handles sequence/timestamp wrapping, and manages stream start/stop lifecycle.

Important APIs and functions: exported APIs are `vivid_start_generating_vid_cap` and `vivid_stop_generating_vid_cap`. Major helpers include `vivid_fillbuff`, `vivid_thread_vid_cap_tick`, `vivid_thread_vid_cap`, `vivid_cap_update_frame_period`, `vivid_precalc_copy_rects`, `vivid_copy_buffer`, `scale_line`, `blend_line`, and `plane_vaddr`.

Control flow: starting any video/VBI/meta capture stream either reuses an existing capture thread and records that stream's sequence start, or starts `vivid_thread_vid_cap`. The thread computes how many buffers should have elapsed from `jiffies`, handles resync after format/timing changes, derives per-stream sequence counts, calls `vivid_thread_vid_cap_tick`, and sleeps until the next frame deadline. Each tick optionally drops buffers, dequeues one active buffer from video, VBI, and metadata lists under `dev->slock`, sets up request controls, fills/processes the buffers, completes requests, marks buffers done or error, assigns timestamps, clears `dqbuf_error`, and advances test pattern movement.

State and persistence: state is volatile in `struct vivid_dev`: active buffer lists, sequence offsets/counts, per-stream sequence starts, `jiffies_vid_cap`, stream start time, frame period/eof offset, timestamp wrap offset, `must_blank` flags, loopback rectangles, cached scaled/blended lines, and test-pattern generator counters. When stream types stop, their active buffers are completed with error; the kthread stops only after video, VBI, and metadata capture streams are all inactive.

Dependencies and integration points: depends on Linux kthreads/freezer/jiffies/random, videobuf2-vmalloc, V4L2 request controls/events/rect helpers, Vivid video capture/output/common helpers, radio headers for shared core state, SDR/VBI/meta/OSD helpers, and the media test pattern generator. Video loopback integrates with output streams by copying from `out_dev->vid_out_active` and optionally blending the OSD framebuffer.

Risks: loopback across different Vivid instances uses `mutex_trylock`; failed locking deliberately falls back to generated noise, which can produce transient frame changes. Scaling and overlay blending assume compatible geometry and two-pixel alignment for packed YUV. Timestamp assignment occurs after `vb2_buffer_done` in the current code, so behavior depends on vb2/V4L2 buffer lifetime expectations. Shared capture thread behavior means a problem in one stream type can affect scheduling for video, VBI, and metadata capture. Sequence resync and long-jiffies rollover math are subtle.

Test signals: useful tests include video capture frame cadence, alternate-field sequence behavior, VBI and metadata capture running alone and together with video capture, timestamp source selection, sequence/time wrap controls, percentage dropped buffers, loopback with crop/compose/scaler/OSD/chromakey/alpha, request API controls per buffer, streamoff cleanup, freezer suspend/resume, and `v4l2-compliance` streaming tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-cap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-cap.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-cap.h

Purpose: declares the shared video/VBI/meta capture generation thread lifecycle.

Important APIs and types: `vivid_start_generating_vid_cap(struct vivid_dev *dev, bool *pstreaming)` starts or joins the capture kthread for the stream represented by `pstreaming`; `vivid_stop_generating_vid_cap` stops one stream and tears down the kthread when the last dependent stream stops.

Control flow: capture queue operations in video, VBI, and metadata modules call these helpers from their `start_streaming` and `stop_streaming` callbacks.

State and persistence: the header owns no state. The implementation mutates stream flags, kthread pointer, active buffer lists, and sequence counters in `struct vivid_dev`.

Dependencies and integration points: included by capture queue modules and the control path that needs to coordinate stream generation.

Risks: the `bool *pstreaming` argument is a stream identity token, so callers must pass exactly the address of the matching `struct vivid_dev` streaming flag.

Test signals: compile coverage and streaming video, VBI, and metadata independently and concurrently validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-cap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-out.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-out.c

Purpose: implements the shared output-side kernel thread for Vivid video output, VBI output, and metadata output. It advances output sequence counters, completes queued output buffers at the configured frame cadence, processes sliced VBI and metadata payloads, and holds the latest video output buffer available for loopback capture.

Important APIs and functions: exported APIs are `vivid_start_generating_vid_out` and `vivid_stop_generating_vid_out`. Internal functions are `vivid_thread_vid_out_tick`, `vivid_thread_vid_out`, and `vivid_grab_controls`.

Control flow: starting an output stream starts `vivid_thread_vid_out` if no output thread exists, or records a per-stream sequence start if one does. The thread calculates elapsed buffers from `jiffies`, applies resync and timestamp wrap offsets, updates per-stream sequence counts, ticks the active lists, then sleeps until the next output deadline. Ticks optionally drop buffers, dequeue video buffers only when more than one is queued so loopback can keep using the last buffer, dequeue eligible VBI and metadata buffers, run request setup/complete, process VBI/meta payloads, stamp sequence/timestamp fields, complete buffers, and clear `dqbuf_error`.

State and persistence: state is volatile in `struct vivid_dev`: `kthread_vid_out`, stream flags, output sequence counters/offsets, active buffer lists, `jiffies_vid_out`, timestamp wrap offset, VBI output cached WSS/CC flags, and controls grabbed while streaming. Stop completes remaining active buffers with error for the stream being stopped and stops the kthread only after video, VBI, and metadata output streams are all inactive.

Dependencies and integration points: depends on Linux kthreads/freezer/jiffies/random, videobuf2, V4L2 request controls, Vivid core/video/radio/SDR/VBI/OSD/control headers, and metadata output processing. Capture loopback depends on this file leaving the newest video output buffer on `vid_out_active`.

Risks: the deliberate "keep one video output buffer pending" behavior is important for loopback but can surprise output-only tests expecting every queued buffer to complete immediately. Shared `dqbuf_error` affects any output stream tick. The control grab set must stay in sync with output controls created in `vivid-ctrls.c`. Timing depends on `timeperframe_vid_out` and field mode, so resync math and alternate-field sequence handling are sensitive.

Test signals: output stream cadence, streamoff buffer cleanup, video loopback stability, VBI output-to-capture WSS/CC propagation, metadata output control updates, queue error injection, sequence/time wrap controls, and `v4l2-compliance` output streaming are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-out.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-out.h

Purpose: declares the shared output generation lifecycle for video, VBI, and metadata output streams.

Important APIs and types: `vivid_start_generating_vid_out(struct vivid_dev *dev, bool *pstreaming)` and `vivid_stop_generating_vid_out(struct vivid_dev *dev, bool *pstreaming)`.

Control flow: output queue operations call these helpers from `start_streaming` and `stop_streaming`; the boolean pointer identifies which output stream is joining or leaving the shared kthread.

State and persistence: no header-owned state. The implementation mutates `struct vivid_dev` output flags, active buffer lists, and kthread state.

Dependencies and integration points: used by video output, VBI output, and metadata output modules.

Risks: callers must pass the correct stream flag address; otherwise sequence starts and shutdown decisions can affect the wrong stream class.

Test signals: compile coverage plus concurrent video/VBI/meta output streaming validates this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-out.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-touch.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-touch.c

Purpose: implements the touch capture kernel thread for the Vivid touch input device. It schedules touch buffers at `timeperframe_tch_cap`, fills synthetic touch pressure maps, completes request controls, stamps timestamps, and handles stream lifecycle.

Important APIs and functions: exported APIs are `vivid_start_generating_touch_cap` and `vivid_stop_generating_touch_cap`. Internal functions are `vivid_thread_tch_cap_tick` and `vivid_thread_touch_cap`.

Control flow: start creates `kthread_touch_cap` unless one already exists, initializes the sequence start offset from `seq_wrap`, and marks touch streaming active. The kthread computes elapsed buffers from `jiffies`, handles resync, updates `touch_cap_with_seq_wrap_count`, calls the tick to dequeue one active touch buffer and fill it with `vivid_fillbuff_tch`, then sleeps until the next scheduled frame. Stop clears streaming, completes all queued touch buffers with error, stops the kthread, and clears the pointer.

State and persistence: volatile state lives in `struct vivid_dev`: touch active list, kthread pointer, stream flag, sequence counters and offsets, `jiffies_touch_cap`, timestamp wrap offset, and request-control state. No generated touch pattern persists beyond queued buffers except the random seed cached in `dev->tch_pat_random`.

Dependencies and integration points: depends on Linux freezer/jiffies, Vivid core, touch kthread header, and touch capture buffer generator. It integrates with videobuf2 through the active list and `vb2_buffer_done`, and with V4L2 requests through `ctrl_hdl_touch_cap`.

Risks: the resync path assigns `dev->cap_seq_resync = false` instead of `dev->touch_cap_seq_resync = false`, and the long-jiffies resync path writes `dev->cap_seq_offset` instead of `dev->touch_cap_seq_offset`; those look like copy/paste bugs that can leave touch resync state inconsistent. `dropped_bufs` is computed but unused by the tick. Timestamp assignment happens after buffer completion.

Test signals: touch capture stream cadence, sequence wrap behavior, changing timeperframe while streaming, streamoff cleanup, request API completion, timestamp wrap, and static analysis for the suspicious resync fields are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-touch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-touch.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-touch.h

Purpose: declares the touch capture generation thread lifecycle.

Important APIs and types: `vivid_start_generating_touch_cap(struct vivid_dev *dev)` starts touch generation, and `vivid_stop_generating_touch_cap(struct vivid_dev *dev)` stops it and drains queued buffers.

Control flow: touch capture queue operations call these helpers from `start_streaming` and `stop_streaming`.

State and persistence: no header-owned state. Implementation state is in `struct vivid_dev`.

Dependencies and integration points: included by the touch capture module and implementation.

Risks: the include guard and comment use `_VIVID_KTHREAD_CAP_H_` / "vivid-kthread-cap.h", duplicating the video capture kthread header guard name. If both headers are included in one translation unit in the wrong order, the touch declarations can be skipped.

Test signals: compile coverage of translation units including both kthread headers and touch streaming tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-touch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-cap.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-cap.c

Purpose: implements UVC-style metadata capture for Vivid webcam mode. It exposes meta capture format operations, videobuf2 queue operations, and a buffer filler that emits timing metadata tied to the video capture clock.

Important APIs and functions: exported symbols are `vivid_meta_cap_qops`, `vidioc_enum_fmt_meta_cap`, `vidioc_g_fmt_meta_cap`, and `vivid_meta_cap_fillbuff`. Internal vb2 callbacks include `meta_cap_queue_setup`, `meta_cap_buf_prepare`, `meta_cap_buf_queue`, `meta_cap_start_streaming`, `meta_cap_stop_streaming`, and `meta_cap_buf_request_complete`.

Control flow: queue setup validates webcam mode and requires a single plane sized for `struct vivid_uvc_meta_buf`. Buffer prepare supports error injection, validates plane size, and sets payload. Queued buffers are appended to `meta_cap_active`. Streaming starts by joining the shared capture kthread with `meta_cap_streaming`; stop leaves through `vivid_stop_generating_vid_cap`. During capture ticks, `vivid_meta_cap_fillbuff` writes a UVC metadata header, optional PTS from start-of-exposure time, optional SCR from EOF time, SOF counters, flags, sequence, and debug output.

State and persistence: state is volatile in `struct vivid_dev` and queued buffers. `meta_pts` and `meta_scr` controls decide whether PTS/SCR fields are generated. Sequence comes from `meta_cap_seq_count`, divided for alternate-field capture.

Dependencies and integration points: depends on V4L2 meta formats, videobuf2, Linux UVC stream flag definitions, shared capture kthread, and Vivid core state. It is synchronized with video capture timing through the shared capture thread and `cap_frame_eof_offset`.

Risks: several multi-byte metadata values are assigned through single-byte lvalues such as `meta->buf[0] = div_u64(...)`, so only the low byte is explicitly set despite debug casts reading 32-bit fields; this is intentional-looking test data but could mislead consumers expecting full UVC values. Meta capture is rejected outside webcam mode. Timestamp is generated independently from the buffer timestamp.

Test signals: `v4l2-compliance` meta capture, webcam-mode format enumeration, buffer-size validation, PTS/SCR control toggles, concurrent video+meta capture timestamps, and UVC metadata parser checks are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-cap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-cap.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-cap.h

Purpose: defines the Vivid UVC metadata capture payload shape and declares metadata capture queue/format helpers.

Important APIs and types: `VIVID_META_CLOCK_UNIT` is the 100 MHz clock divisor used for PTS/SCR generation. `struct vivid_uvc_meta_buf` is a packed UVC-like metadata buffer with timestamp, SOF, length, flags, and a ten-byte PTS/STC/SOF payload. Public APIs are `vivid_meta_cap_fillbuff`, `vidioc_enum_fmt_meta_cap`, `vidioc_g_fmt_meta_cap`, and `vivid_meta_cap_qops`.

Control flow: queue setup and capture ticks in the `.c` file use this structure size as the meta buffer contract.

State and persistence: no persistent state in the header. It defines the binary ABI exposed through meta capture buffers.

Dependencies and integration points: consumers need V4L2/vb2 types and `struct vivid_dev`/`struct vivid_buffer` declarations from Vivid core headers.

Risks: because `struct vivid_uvc_meta_buf` is packed and exported as buffer contents, field layout changes are ABI-visible to tests.

Test signals: size/layout assertions through userspace metadata reads and format buffersize checks validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-cap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-out.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-out.c

Purpose: implements Vivid metadata output for webcam mode. Metadata output buffers carry image-control values that are applied to the video test generator controls when output buffers are consumed.

Important APIs and functions: exported symbols are `vivid_meta_out_qops`, `vidioc_enum_fmt_meta_out`, `vidioc_g_fmt_meta_out`, and `vivid_meta_out_process`. Internal vb2 callbacks mirror meta capture: queue setup, prepare, queue, start/stop streaming, and request completion.

Control flow: queue setup accepts one plane sized for `struct vivid_meta_out_buf` in webcam mode. Buffer prepare validates size and supports error injection. Queued buffers enter `meta_out_active`; streaming joins the shared output kthread through `vivid_start_generating_vid_out`. Output ticks run request setup/complete, call `vivid_meta_out_process`, assign sequence/timestamp, and complete the buffer.

State and persistence: metadata output persists by changing V4L2 controls on `dev->brightness`, `dev->contrast`, `dev->saturation`, and `dev->hue`. The buffer itself is transient; the control values remain until changed again.

Dependencies and integration points: depends on V4L2 metadata output format `V4L2_META_FMT_VIVID`, videobuf2, Vivid core, shared output kthread, and user video controls created by `vivid-ctrls.c`.

Risks: metadata output assumes the image controls exist and are valid for the current device mode. Applying controls from queued metadata can race conceptually with normal userspace control changes, though V4L2 control locking handles serialization. The declared `vidioc_s_fmt_meta_out` prototype in the header is not implemented in this file.

Test signals: webcam-mode meta output format enumeration, streaming a metadata buffer and observing video control values, request completion tests, error injection, and build warnings for unused/missing prototypes are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-out.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-out.h

Purpose: defines the metadata output payload and declares metadata output queue/format helpers.

Important APIs and types: `struct vivid_meta_out_buf` contains brightness, contrast, saturation, and hue values. Public declarations include `vivid_meta_out_process`, `vidioc_enum_fmt_meta_out`, `vidioc_g_fmt_meta_out`, `vidioc_s_fmt_meta_out`, and `vivid_meta_out_qops`.

Control flow: userspace writes buffers matching `struct vivid_meta_out_buf`; the output kthread processes them and updates controls.

State and persistence: no header-owned state. The payload values become persistent V4L2 control values when processed.

Dependencies and integration points: depends on Vivid core buffer/device types and V4L2/vb2 types from including code.

Risks: declares `vidioc_s_fmt_meta_out`, but the corresponding source file in this subset does not define it, so either another file must provide it or the declaration is stale.

Test signals: compile/link coverage and metadata output format ioctl coverage validate this boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-meta-out.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-osd.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-osd.c

Purpose: implements optional framebuffer-backed on-screen display/overlay support for Vivid. It allocates a small 16-bit framebuffer, registers it with fbdev, initializes display mode/fix information, provides color maps and simple ioctls, and supplies helpers used by video loopback overlay blending.

Important APIs and functions: exported APIs are `vivid_fb_init`, `vivid_fb_deinit`, `vivid_fb_clear`, and `vivid_fb_green_bits`. Internal framebuffer operations include `vivid_fb_ioctl`, `vivid_fb_check_var`, `vivid_fb_set_par`, `vivid_fb_setcolreg`, `vivid_fb_pan_display`, and `vivid_fb_blank`. Initialization helpers are `vivid_fb_init_vidmode` and `vivid_fb_release_buffers`.

Control flow: `vivid_fb_init` allocates `video_vbase`, stores a physical address via `virt_to_phys`, initializes a 720x576 16-bit mode, clears the framebuffer with color bars, registers the framebuffer, and applies parameters. The fbdev callbacks validate/normalize mode requests, update stride and fixed info, manage pseudo-palette entries, handle `FBIOGET_VBLANK`, and ignore blanking. `vivid_fb_deinit` unregisters fbdev and frees the cmap, palette, and backing buffer.

State and persistence: framebuffer memory and fbdev state are volatile per device. `video_vbase`, `video_pbase`, display dimensions, byte stride, `fb_info`, `fb_defined`, and `fb_fix` live in `struct vivid_dev`. Pixel contents persist until cleared or overwritten by fbdev userspace.

Dependencies and integration points: depends on Linux fbdev APIs, V4L2 device logging, Vivid core, and video loopback code that reads `video_vbase` for OSD blending. Header stubs make this optional under `CONFIG_VIDEO_VIVID_OSD`.

Risks: fbdev is optional and legacy; configurations without `CONFIG_VIDEO_VIVID_OSD` use stubs. `virt_to_phys` on kmalloc memory is only suitable for this synthetic test use and is not a real hardware mapping. The code only supports 16-bit RGB555/RGB565 and ignores most mode changes and blanking requests. `vivid_fb_deinit` assumes the framebuffer was registered.

Test signals: build with and without `CONFIG_VIDEO_VIVID_OSD`, framebuffer registration/removal, fbset/fbdev mmap or write tests, clear-framebuffer control, overlay loopback rendering, palette updates, and unload leak checks validate the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-osd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-osd.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-osd.h

Purpose: declares OSD framebuffer helpers and provides no-OSD stubs when framebuffer overlay support is disabled.

Important APIs and types: `vivid_fb_init`, `vivid_fb_deinit`, `vivid_fb_clear`, and `vivid_fb_green_bits`. In non-OSD builds, init returns `-ENODEV`, cleanup/clear are no-ops, and green bits default to 5.

Control flow: core device initialization can call `vivid_fb_init` unconditionally when OSD support is desired, while compile-time configuration selects real or stub behavior.

State and persistence: the header owns no state. Real implementation manages framebuffer state in `struct vivid_dev`.

Dependencies and integration points: depends on `CONFIG_VIDEO_VIVID_OSD` and the including context providing `struct vivid_dev` and `-ENODEV`.

Risks: callers must tolerate `-ENODEV` in stub builds. The fallback `vivid_fb_green_bits` value influences RGB555/RGB565 behavior in code that may run without a real framebuffer.

Test signals: compile and runtime coverage of both config paths validate the stubs and real declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-osd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-common.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-common.c

Purpose: provides shared AM/FM/SW radio frequency-band handling, signal-quality emulation, and RDS generator initialization for Vivid radio receiver and transmitter nodes.

Important APIs and functions: exports `vivid_radio_bands`, `vivid_radio_rds_init`, `vivid_radio_g_frequency`, and `vivid_radio_s_frequency`. `vivid_radio_calc_sig_qual` is the internal quality and RDS-looping calculator.

Control flow: set-frequency selects the nearest supported band, clamps the requested frequency, stores it through the caller-provided pointer, recalculates signal quality against ideal channels and optional transmitter frequency, and reinitializes RDS data. RDS initialization either copies TX RDS controls when radio loopback is active, leaves block-I/O TX-provided data alone, or generates standard alternate RDS/RBDS content from frequency. When RX RDS controls are enabled, it mirrors generated values into RX RDS controls.

State and persistence: state is volatile in `struct vivid_dev`: RX/TX frequencies, `radio_rx_sig_qual`, `radio_rds_loop`, RDS generator contents, RDS alternate toggle, and V4L2 RDS control values. Generated RDS blocks persist until regenerated or overwritten by TX block I/O.

Dependencies and integration points: depends on V4L2 tuner/frequency definitions, Vivid core, control helpers, and `vivid-rds-gen.c`. It is used by both receiver and transmitter ioctl paths.

Risks: `vivid_radio_s_frequency` updates `*pfreq` before calling `vivid_radio_calc_sig_qual`, so quality calculation depends on the correct field pointer being passed. RDS loop state depends on both RX and TX frequencies and can clear generated data when switching modes. The band selection uses midpoint thresholds rather than explicit requested modulation.

Test signals: set/get frequency for AM/SW/FM, clamp boundaries, signal strength near/off channel, RX/TX same-frequency loopback, RDS controls vs block I/O, and alternate radiotext behavior are primary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-common.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-common.h

Purpose: defines shared radio frequency ranges, band identifiers, and common frequency/RDS helper declarations for Vivid radio RX/TX.

Important APIs and types: FM, AM, and SW ranges are defined in V4L2 low-frequency units (`kHz * 16`). `enum { BAND_FM, BAND_AM, BAND_SW, TOT_BANDS }` indexes `vivid_radio_bands`. Public helpers are `vivid_radio_g_frequency`, `vivid_radio_s_frequency`, and `vivid_radio_rds_init`.

Control flow: RX and TX ioctl implementations call the common helpers to avoid duplicating range handling and RDS setup.

State and persistence: no header-owned state. It defines constants used to mutate per-device frequency and RDS state.

Dependencies and integration points: consumers need V4L2 frequency-band types and Vivid device declarations.

Risks: frequency units must remain consistent with V4L2 radio APIs; callers passing raw Hz or kHz would get incorrect clamping.

Test signals: compile coverage plus frequency ioctl tests at all range boundaries validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-rx.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-rx.c

Purpose: implements Vivid radio receiver userspace operations: RDS block reading, poll, frequency band enumeration, hardware seek simulation, tuner status reporting, and audio mode setting.

Important APIs and functions: exported functions are `vivid_radio_rx_read`, `vivid_radio_rx_poll`, `vivid_radio_rx_enum_freq_bands`, `vivid_radio_rx_s_hw_freq_seek`, `vivid_radio_rx_g_tuner`, and `vivid_radio_rx_s_tuner`.

Control flow: RDS read rejects control-mode RDS, serializes ownership of block I/O to one filehandle, initializes/regenerates RDS blocks based on elapsed `VIVID_RDS_NSEC_PER_BLK`, blocks or returns `-EWOULDBLOCK` until data is available, injects block errors based on signal quality, and copies whole `v4l2_rds_data` records to userspace. Hardware seek validates mode/range/wrap constraints and computes the next channel spacing but does not store the new frequency in this snapshot. `g_tuner` reports capability flags, signal strength, AFC, mono/stereo/RDS subchannels, and optionally refreshes RDS controls.

State and persistence: state is volatile in `struct vivid_dev`: RDS owner filehandle, last block counters, RDS alternate state, generated RDS data, RX frequency, signal quality, RDS enable/control mode flags, hardware seek mode/prog-limits, and RX audio mode.

Dependencies and integration points: depends on V4L2 common/event/timing APIs, Linux sleep/signal handling, Vivid core, common radio helpers, RDS generator, and V4L2 filehandle ownership.

Risks: hardware seek currently computes `freq` but returns without assigning `dev->radio_rx_freq`, so it may validate seek behavior without moving the tuner. RDS read uses time-based block generation and sleeps in 20 ms increments, which can be timing-sensitive. Only one RDS block-I/O reader is allowed. Signal-quality error injection is random and can make tests nondeterministic unless tuned to strong signal.

Test signals: RDS blocking/nonblocking reads, one-reader ownership, weak-signal error injection, RDS enable/disable, tuner capability flags for seek modes and RDS mode, hardware seek with bounded/wrap/prog-limits, and RX/TX RDS loopback validate this module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-rx.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-rx.h

Purpose: declares Vivid radio receiver file and ioctl operations.

Important APIs and types: declarations cover RDS `read`, `poll`, frequency band enumeration, hardware seek, tuner get, and tuner set operations.

Control flow: the Vivid radio RX video_device ioctl/file-operation tables reference these functions.

State and persistence: no header-owned state. Implementations read and mutate radio RX fields in `struct vivid_dev`.

Dependencies and integration points: requires V4L2 tuner/frequency/file/poll types from including contexts.

Risks: this header exposes only operation functions; lifecycle and shared frequency handling live elsewhere, so callers must compose it with `vivid-radio-common.h`.

Test signals: compile coverage and V4L2 radio receiver ioctl/read tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-tx.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-tx.c

Purpose: implements Vivid radio transmitter operations for RDS block output, poll, modulator get, and modulator set.

Important APIs and functions: exported functions are `vivid_radio_tx_write`, `vivid_radio_tx_poll`, `vidioc_g_modulator`, and `vidioc_s_modulator`.

Control flow: RDS write rejects control-mode TX RDS, requires whole `v4l2_rds_data` records, serializes block I/O to one filehandle, waits for time slots based on `VIVID_RDS_NSEC_PER_BLK`, copies blocks from userspace, and, when RX/TX RDS loopback is active, stores valid non-error blocks into the shared generator data array. Modulator get reports AM/FM/SW range, stereo/RDS/block-I/O capabilities, and current subchannels. Modulator set validates supported subchannel bits and stores them.

State and persistence: state is volatile in `struct vivid_dev`: TX RDS owner, last block counter, TX subchannels, RDS generator data, and TX capability/control mode flags. Written RDS blocks persist in the generator buffer until overwritten or regenerated.

Dependencies and integration points: depends on V4L2 common/event/timing APIs, Linux sleep/signal handling, Vivid core, controls, common radio definitions, and radio loopback state maintained by `vivid-radio-common.c`.

Risks: write timing is synthetic and can block indefinitely until RDS subchannel is enabled unless nonblocking is used. Only one writer can own TX RDS block I/O. Invalid/error RDS blocks are silently ignored for loopback after counting as consumed. `vidioc_s_modulator` permits only bit mask `0x13`, so capability changes must keep that mask aligned with V4L2 subchannel definitions.

Test signals: blocking/nonblocking writes, single-writer ownership, TX subchannel toggles, RX loopback of valid blocks, control-mode rejection, modulator capability queries, and userspace RDS block size validation are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-tx.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-tx.h

Purpose: declares Vivid radio transmitter file and ioctl operations.

Important APIs and types: declarations cover RDS `write`, `poll`, `VIDIOC_G_MODULATOR`, and `VIDIOC_S_MODULATOR` handlers.

Control flow: radio TX file-operation and ioctl tables call these functions for userspace interaction.

State and persistence: no header-owned state. Implementation mutates TX fields and shared RDS generator state in `struct vivid_dev`.

Dependencies and integration points: requires V4L2 file, poll, and modulator types from including contexts.

Risks: the header does not expose shared frequency helpers; users must combine it with `vivid-radio-common.h`.

Test signals: compile coverage and radio transmitter write/modulator ioctl tests validate this boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-rds-gen.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-rds-gen.c

Purpose: generates synthetic RDS/RBDS block streams for the Vivid radio receiver and transmitter loopback tests.

Important APIs and functions: exported functions are `vivid_rds_generate` and `vivid_rds_gen_fill`. Internal helpers include `vivid_get_di` for decoder information bits and time/date generation inside group 4A.

Control flow: `vivid_rds_gen_fill` populates PI, PTY, PS name, radiotext, traffic, stereo, and RBDS/RDS defaults based on frequency and alternate state. `vivid_rds_generate` fills 57 groups of four blocks: repeated group 0B for PI/PS, group 2A for radiotext, group 4A for current time, and group 15B filler elsewhere. It encodes block IDs in the `block` field and stores payload bytes in `lsb`/`msb`.

State and persistence: all generator state is in `struct vivid_rds_gen`: source fields plus the generated `v4l2_rds_data` block array. Time group contents are generated from current real time and timezone when generation runs.

Dependencies and integration points: depends on Linux time/string/kernel helpers and V4L2 RDS data definitions. It is called by radio common initialization and read/write loopback paths.

Risks: uses `sys_tz` and wall-clock time, so time blocks vary across systems and timezones. RDS group scheduling and payload layout are hand-encoded; off-by-one errors would be visible only to RDS decoders. Generated PS name derives from V4L2 low-frequency units, so unit mistakes in callers propagate into display text.

Test signals: decode generated RDS blocks for PI/PTY/PS/radiotext/time, alternate text toggling, RBDS vs RDS defaults, and block count/timing constants validate the generator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-rds-gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-rds-gen.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-rds-gen.h

Purpose: defines RDS generator constants, state, and public generator APIs for Vivid radio.

Important APIs and types: constants define 57 groups, four blocks per group, total block count, and nanoseconds per block for a roughly five-second cycle. `struct vivid_rds_gen` stores generated block data and source PI/PTY/flags/PS/radiotext fields. APIs are `vivid_rds_gen_fill` and `vivid_rds_generate`.

Control flow: callers fill source fields, then generate the block array, then radio read/write paths stream blocks according to `VIVID_RDS_NSEC_PER_BLK`.

State and persistence: the structure is the persistent per-device RDS buffer until regenerated or overwritten.

Dependencies and integration points: depends on `struct v4l2_rds_data`, Linux time constants, and radio common code.

Risks: PS name and radiotext fixed array sizes match RDS limits; callers must provide NUL-terminated strings or use bounded copies.

Test signals: compile coverage and userspace RDS block stream decoding validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-rds-gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-sdr-cap.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-sdr-cap.c

Purpose: implements Vivid software-defined-radio capture. It exposes SDR formats, ADC/RF tuner/frequency ioctls, a vb2 capture queue, a sample-rate-driven kthread, and a synthetic FM-modulated complex sample generator.

Important APIs and functions: exported symbols are `vivid_sdr_cap_qops`, `vivid_sdr_enum_freq_bands`, `vivid_sdr_g_frequency`, `vivid_sdr_s_frequency`, `vivid_sdr_g_tuner`, `vivid_sdr_s_tuner`, `vidioc_enum_fmt_sdr_cap`, `vidioc_g_fmt_sdr_cap`, `vidioc_s_fmt_sdr_cap`, `vidioc_try_fmt_sdr_cap`, and `vivid_sdr_cap_process`. Internal functions include `vivid_thread_sdr_cap_tick`, `vivid_thread_sdr_cap`, and vb2 queue callbacks.

Control flow: queue setup/prepare validates a single plane sized for `SDR_CAP_SAMPLES_PER_BUF * 2`. Start streaming initializes sequence start, launches `vivid_thread_sdr_cap`, or returns injected errors. The kthread computes elapsed buffers from `jiffies` and `sdr_adc_freq`, handles resync after ADC frequency changes, updates sequence counters, ticks one queued buffer, then sleeps until the next sample-buffer deadline. `vivid_sdr_cap_process` generates I/Q samples for CU8 or CS8 from fixed-point sine/cosine phases, a 1 kHz source tone, and the FM deviation control.

State and persistence: volatile state in `struct vivid_dev` includes SDR active list, kthread pointer, ADC/RF frequencies, pixel format, buffer size, sequence counters, timestamp wrap offset, fixed-point phases, and FM deviation. Frequency and format settings persist for the device until changed.

Dependencies and integration points: depends on V4L2 SDR/tuner/frequency APIs, videobuf2, kthreads/freezer/jiffies, Linux fixed-point trig helpers, Vivid controls, and streaming error injection shared from `vivid-ctrls.c`.

Risks: the generated samples are synthetic and not tied to `sdr_fm_freq`, so RF frequency is only control-plane state. Fixed-point math and modulo behavior can produce artifacts but is adequate for test data. ADC frequency changes while streaming rely on `sdr_cap_seq_resync`. The queue always sizes buffers for the largest 8-bit complex sample representation.

Test signals: SDR format enum/try/set/get, ADC/RF frequency clamp boundaries, streaming cadence at each ADC band, CU8 and CS8 sample value ranges, FM deviation effects, nonblocking streamoff cleanup, and v4l2-compliance SDR tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-sdr-cap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-sdr-cap.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-sdr-cap.h

Purpose: declares Vivid SDR capture queue operations, tuner/frequency ioctls, format ioctls, and sample-buffer generation helper.

Important APIs and types: declarations cover frequency bands, get/set frequency, get/set tuner, enum/get/set/try SDR format, `vivid_sdr_cap_process`, and `vivid_sdr_cap_qops`.

Control flow: Vivid SDR video_device ioctl and queue setup tables reference these functions.

State and persistence: no header-owned state. Implementations mutate SDR fields in `struct vivid_dev`.

Dependencies and integration points: requires V4L2 SDR/tuner/frequency/file types and Vivid buffer/device types from including code.

Risks: adding SDR formats requires keeping the implementation's format table and users of `sdr_buffersize` aligned with this header's operation surface.

Test signals: compile coverage and SDR ioctl/streaming tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-sdr-cap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-touch-cap.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-touch-cap.c

Purpose: implements the Vivid touch capture node. It exposes touch format/input/stream-parameter ioctls, vb2 queue operations, and synthetic pressure-map generation for repeatable touch gestures.

Important APIs and functions: exported symbols are `vivid_touch_cap_qops`, `vivid_enum_fmt_tch`, `vivid_g_fmt_tch`, `vivid_g_fmt_tch_mplane`, `vivid_g_parm_tch`, `vivid_enum_input_tch`, `vivid_g_input_tch`, `vivid_set_touch`, `vivid_s_input_tch`, and `vivid_fillbuff_tch`. Internal helpers generate noise, pressure blobs, and gesture patterns.

Control flow: `vivid_set_touch` fixes the format to `V4L2_TCH_FMT_DELTA_TD16` with a 21x12 single-plane signed-16 image. Queue setup/prepare validate this size, queue appends buffers to `touch_cap_active`, and start/stop streaming use the touch kthread. `vivid_fillbuff_tch` sets sequence, fills low-level random noise, then cycles through single/double/triple tap, left-to-right motion, zoom in/out, palm press, and multiple-press patterns based on sequence modulo constants.

State and persistence: touch format, timeperframe, sequence counters, and cached random gesture seed live in `struct vivid_dev`. Buffer contents are transient, while selected touch input/format are fixed to a single supported input.

Dependencies and integration points: depends on Vivid core, touch kthread, Vivid video common format conversion, videobuf2, and V4L2 touch pixel formats. Multiplanar get-format uses `fmt_sp2mp` even though the underlying touch format is single-plane.

Risks: random noise and pressure offsets make output nondeterministic at sample values, though gesture timing is deterministic by sequence. Big-endian conversion is conditional at the end; early returns for idle frames before conversion mean noise-only frames may not be byte-swapped on big-endian systems. Only get-format is provided; format is fixed through input setup.

Test signals: format enumeration/get for single- and multi-planar modes, streamparm reporting, input enumeration/set/get, gesture sequence inspection, big-endian sample layout review, stream start/stop cleanup, and `v4l2-compliance` touch node tests validate this module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-touch-cap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-touch-cap.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-touch-cap.h

Purpose: defines touch dimensions, pressure/pattern constants, gesture enum values, queue operations, and touch ioctl/generator declarations.

Important APIs and types: constants include `VIVID_TCH_HEIGHT`, `VIVID_TCH_WIDTH`, pressure limits, sequence/pattern counts, and `enum vivid_tch_test`. Public APIs cover touch format/input/streamparm operations, `vivid_fillbuff_tch`, `vivid_set_touch`, and `vivid_touch_cap_qops`.

Control flow: core setup initializes the touch format through `vivid_set_touch`; queue and ioctl tables use the declared operations.

State and persistence: no header-owned state. Constants define the ABI-visible buffer dimensions and gesture cycle.

Dependencies and integration points: consumers need V4L2/vb2 types and Vivid core declarations.

Risks: changing width/height or pressure constants changes userspace-visible touch buffer shape and expected gesture output.

Test signals: compile coverage plus touch format and buffer-size validation tests cover this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-touch-cap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-cap.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-cap.c

Purpose: implements Vivid raw and sliced VBI capture support. It generates or loops closed-caption/WSS/teletext data, exposes VBI format/capability ioctls, and provides vb2 queue operations for VBI capture streams.

Important APIs and functions: exported APIs are `vivid_raw_vbi_cap_process`, `vivid_sliced_vbi_cap_process`, `vidioc_g_fmt_vbi_cap`, `vidioc_s_fmt_vbi_cap`, `vivid_fill_service_lines`, `vidioc_g_fmt_sliced_vbi_cap`, `vidioc_try_fmt_sliced_vbi_cap`, `vidioc_s_fmt_sliced_vbi_cap`, `vidioc_g_sliced_vbi_cap`, and `vivid_vbi_cap_qops`. Internal helpers include `vivid_sliced_vbi_cap_fill` and `vivid_g_fmt_vbi_cap`.

Control flow: queued VBI buffers join `vbi_cap_active`; start streaming joins the shared capture kthread. Capture processing sets sequence, generates sliced VBI data for 525/625-line standards, optionally substitutes looped WSS/CC data from VBI output, fills raw buffers with blanking level, then renders raw waveforms or copies sliced records when signal mode is valid. Format ioctls derive sizes and service lines from current SDTV standard and configured service set.

State and persistence: state is volatile in `struct vivid_dev`: VBI active list, service set, interlaced flag, generated `vbi_gen` data, output-looped WSS/CC fields, current input standard/signal mode, and sequence counters. Selected sliced capture service set persists until changed.

Dependencies and integration points: depends on V4L2 VBI structures, videobuf2, shared capture kthread, VBI generator, Vivid video common helpers, and Vivid output-loop state from `vivid-vbi-out.c`.

Risks: `vidioc_s_fmt_vbi_cap` and `vidioc_s_fmt_sliced_vbi_cap` check `fmt->type != ... && vb2_is_busy(...)`, which only rejects busy queues when the type is not the expected type; this may be intentional Vivid test behavior but looks suspicious compared with usual busy checks. Raw and sliced sizes depend on current standard, so standard changes while buffers are queued must be controlled. Loopback substitutions rely on output state freshness.

Test signals: raw and sliced VBI capture for 525/625 standards, service set negotiation, VBI output-to-capture loopback for CC/WSS, invalid/no-signal capture behavior, queue size validation, interlaced flag control, and `v4l2-compliance` VBI tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-cap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-cap.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-cap.h

Purpose: declares Vivid VBI capture processing, sliced VBI output processing shared capability helper, VBI format ioctls, service-line helper, and queue operations.

Important APIs and types: declarations include raw/sliced capture processors, `vivid_sliced_vbi_out_process`, raw and sliced get/set/try format handlers, sliced VBI capability handler, `vivid_fill_service_lines`, and `vivid_vbi_cap_qops`.

Control flow: capture kthread and VBI queue/ioctl tables use these declarations; VBI output code also includes this header for shared service-line and capability behavior.

State and persistence: no header-owned state. Implementations use `struct vivid_dev` service-set and VBI generator state.

Dependencies and integration points: requires V4L2 VBI/vb2/file types and Vivid device/buffer declarations.

Risks: declaring `vivid_sliced_vbi_out_process` here as well as in the output header creates cross-header coupling and can obscure ownership.

Test signals: compile coverage of both capture and output VBI modules and VBI ioctl tests validate the boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-cap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-gen.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-gen.c

Purpose: generates synthetic raw and sliced VBI payloads for Vivid, including 525-line closed captions, 625-line WSS, teletext packets, and time-of-day packets.

Important APIs and functions: exported APIs are `vivid_vbi_gen_raw` and `vivid_vbi_gen_sliced`. Internal helpers encode WSS bits, teletext raw waveform data, closed-caption parity/preamble, odd parity, teletext time-of-day packets, and teletext row packets.

Control flow: `vivid_vbi_gen_sliced` clears the 25-record buffer and fills either 625-line teletext plus WSS records or 525-line caption records plus field-2 time-of-day fragments based on standard and sequence. `vivid_vbi_gen_raw` walks sliced records, computes the raw buffer line offset according to VBI format and field layout, and renders CC/WSS/teletext waveforms into the raw GREY buffer.

State and persistence: generator state is in `struct vivid_vbi_gen_data`, especially the sliced records and cached 16-byte time-of-day packet. Generated time packets vary with current real time and timezone.

Dependencies and integration points: depends on Linux bitops/time/string helpers and V4L2 sliced VBI definitions. Called by VBI capture code to fill both raw and sliced output buffers.

Risks: raw waveform rendering uses hand-coded sampling-rate conversions and line offsets; wrong VBI format parameters can write unexpected positions. Time-of-day and timezone use make some generated bytes nondeterministic. Teletext/hamming/parity encoding is compact and easy to regress without decoder tests.

Test signals: decode generated closed captions, WSS aspect bits, teletext rows, raw VBI line placement for interlaced/noninterlaced formats, and time-of-day packet parity/checksum to validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-gen.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-gen.h

Purpose: defines the VBI generator state structure and declares raw/sliced VBI generation APIs.

Important APIs and types: `struct vivid_vbi_gen_data` contains 25 sliced VBI records and a 16-byte time-of-day packet cache. `vivid_vbi_gen_sliced` fills sliced records for a standard and sequence number; `vivid_vbi_gen_raw` renders those records into a raw VBI buffer using a `v4l2_vbi_format`.

Control flow: VBI capture first calls sliced generation, optionally adjusts records for loopback/aspect, then calls raw generation for raw VBI buffers.

State and persistence: the structure persists generated records across processing steps within a capture tick.

Dependencies and integration points: consumers need V4L2 sliced/raw VBI types.

Risks: the fixed 25-record array reflects current generated services; adding more service lines requires resizing the structure and dependent loops.

Test signals: generated sliced record count and raw conversion tests validate this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-out.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-out.c

Purpose: implements Vivid raw and sliced VBI output support. It exposes VBI output queue operations and format ioctls, and parses sliced VBI output buffers so capture loopback can reuse WSS and closed-caption data.

Important APIs and functions: exported symbols are `vivid_vbi_out_qops`, `vidioc_g_fmt_vbi_out`, `vidioc_s_fmt_vbi_out`, `vidioc_g_fmt_sliced_vbi_out`, `vidioc_try_fmt_sliced_vbi_out`, `vidioc_s_fmt_sliced_vbi_out`, and `vivid_sliced_vbi_out_process`. Internal vb2 callbacks handle queue setup, prepare, queue, start/stop streaming, and request completion.

Control flow: queue setup/prepare validate raw or sliced VBI output buffer sizes based on output standard. Starting joins the shared output kthread through `vivid_start_generating_vid_out`; stopping leaves the output thread and clears cached WSS/CC flags. Format setters select raw vs sliced queue type and service set when the queue is idle. `vivid_sliced_vbi_out_process` scans completed sliced records, caches field-0/field-1 CC bytes for 525-line output and WSS bytes for 625-line output.

State and persistence: state is volatile in `struct vivid_dev`: VBI output active list, service set, stream mode, cached CC/WSS data and valid flags, output standard, and sequence counters. Cached CC/WSS state persists until another sliced output buffer or stream stop clears it.

Dependencies and integration points: depends on V4L2 VBI structures, videobuf2, shared output kthread, Vivid core, and `vivid_fill_service_lines` from VBI capture support. Capture loopback reads the cached WSS/CC fields.

Risks: raw VBI output payload itself is not parsed in this file; only sliced output affects loopback. Queue type is mutated on the video_device queue when format changes, so userspace must not change formats while busy. The raw output format uses `dev->vbi_cap_interlaced` for flags, tying output raw format to a capture-side control.

Test signals: raw/sliced VBI output format switching, queue size checks, streamoff clearing cached data, output-to-capture CC/WSS loopback, service set negotiation for 525/625 standards, request completion, and v4l2-compliance VBI output tests validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-out.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-out.h

Purpose: declares Vivid VBI output processing, raw/sliced VBI output format handlers, and queue operations.

Important APIs and types: declarations include `vivid_sliced_vbi_out_process`, raw VBI get/set format handlers, sliced VBI get/try/set format handlers, and `vivid_vbi_out_qops`.

Control flow: VBI output queue/ioctl tables use these functions, and the shared output kthread calls the process helper for sliced output buffers.

State and persistence: no header-owned state. Implementations cache WSS/CC loopback state in `struct vivid_dev`.

Dependencies and integration points: requires V4L2 file/format/vb2 types and Vivid device/buffer declarations.

Risks: the processing declaration overlaps with `vivid-vbi-cap.h`; ownership is split because capture uses output-derived data for loopback.

Test signals: compile coverage and VBI output ioctl/streaming tests validate this boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-out.h -->
