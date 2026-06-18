# subset-b-004222 research

Grouped research report for USBTV007 and UVC USB media driver files. Each section preserves the original source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/usbtv-audio.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/usbtv-audio.c

Purpose: implements the ALSA capture side of the Fushicai USBTV007 grabber. It registers one PCM capture device named `USBTV Audio`, accepts only 48 kHz stereo signed 16-bit little-endian samples, and streams audio from bulk endpoint `USBTV_AUDIO_ENDP` into the ALSA runtime ring buffer.

Important APIs and functions: exported entry points are `usbtv_audio_init`, `usbtv_audio_free`, `usbtv_audio_suspend`, and `usbtv_audio_resume`. ALSA callbacks are `snd_usbtv_pcm_open`, `snd_usbtv_pcm_close`, `snd_usbtv_prepare`, `snd_usbtv_card_trigger`, and `snd_usbtv_pointer`. USB streaming is handled by `usbtv_audio_start`, `usbtv_audio_stop`, and the URB completion callback `usbtv_audio_urb_received`. The hardware contract is described by `snd_usbtv_digital_hw` and constants from `usbtv.h`.

Control flow: initialization creates an ALSA card, one capture PCM, managed DMA buffer, and a work item. Open stores the current substream and installs hardware constraints. Trigger commands only flip `snd_stream` and schedule `snd_trigger`; the work item starts or stops hardware outside the PCM trigger call path. Start allocates a single bulk URB and transfer buffer, writes a vendor register setup sequence through `usbtv_set_regs`, clears the endpoint halt, and submits the URB. Each completion validates status, copies 240-byte audio payloads after 4-byte per-chunk headers into the ALSA ring buffer with wraparound, updates buffer and period positions under ALSA stream locking, signals elapsed periods, and resubmits the URB.

State and persistence: state is volatile per-device state stored in `struct usbtv`: `snd`, `snd_substream`, `snd_stream`, `snd_trigger`, `snd_bulk_urb`, `snd_buffer_pos`, and `snd_period_pos`. No audio state is persisted across disconnect; stop kills and frees the URB and transfer buffer, while suspend/resume kill or resubmit the same URB if capture is active.

Dependencies and integration points: depends on ALSA core/PCM APIs, USB bulk URBs, and the common USBTV register helper from `usbtv-core.c`. It coordinates with video capture because `usbtv-video.c` temporarily suspends audio while switching USB alternate settings for video. It is called from USB probe/disconnect in `usbtv-core.c`.

Risks: `usbtv_audio_start` ignores errors from register setup and `usb_submit_urb`, so a trigger can appear successful even when streaming failed. The completion callback assumes `snd_substream` and `runtime` are valid while `snd_stream` is set; close clears streaming asynchronously through work scheduling. Only one URB is used, which keeps the code simple but may be fragile under latency. Packet parsing trusts chunk alignment in `actual_length`. Suspend/resume uses `GFP_ATOMIC` resubmission and logs no error.

Test signals: build with ALSA and USBTV enabled; probe a USBTV007 device and verify a capture PCM appears; record 48 kHz stereo audio while video streams and while video starts/stops; exercise PCM trigger start/stop/pause/resume; test disconnect during capture, suspend/resume during capture, URB status failures, and ALSA period wakeups with `arecord` or equivalent userspace capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/usbtv-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/usbtv-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/usbtv-core.c

Purpose: provides the USB driver shell for the Fushicai USBTV007 grabber. It matches supported USB IDs, validates the expected interface layout, allocates `struct usbtv`, initializes video and audio subdrivers, and tears them down on disconnect.

Important APIs and functions: `usbtv_set_regs` is the shared vendor-control helper used by audio and video setup paths. `usbtv_probe` and `usbtv_disconnect` are the USB driver callbacks. `usbtv_id_table` matches devices `1b71:3002`, `1f71:3301`, and `1f71:3306`. `module_usb_driver(usbtv_usb_driver)` registers the module.

Control flow: probe rejects interfaces that do not have two alternate settings or whose alternate setting 1 does not expose four endpoints. It derives the isochronous packet size from endpoint 0 of alternate setting 1, allocates the device object, stores the USB device and `iso_size`, and publishes it with `usb_set_intfdata`. Video initialization runs first, then audio initialization. On success the code takes an extra V4L2 device reference so the `struct usbtv` lifetime can extend past USB disconnect while video file handles still exist. Disconnect clears interface data, frees ALSA and V4L2 frontends, nulls `udev`, and drops that V4L2 reference.

State and persistence: no persistent storage exists. Hardware register state is programmed by subdrivers with `usbtv_set_regs`, which loops over index/value pairs and sends vendor requests to endpoint zero. Device state lives in `struct usbtv` and is ultimately released by the V4L2 release callback in `usbtv-video.c`.

Dependencies and integration points: depends on Linux USB core and the USBTV video/audio modules declared in `usbtv.h`. It integrates with V4L2 lifetime management by relying on `v4l2_device_get`/`put` instead of freeing `struct usbtv` immediately when video nodes are still referenced.

Risks: endpoint validation is minimal and assumes endpoint ordering in alternate setting 1. `usbtv_set_regs` stops on the first failing control request but has no per-register diagnostics. The audio failure path deliberately manipulates V4L2 references and depends on `usbtv_video_free` undoing the extra get, so lifetime regressions would be easy if initialization ordering changes.

Test signals: validate probe with all supported product IDs, rejection of malformed descriptors, video-init failure cleanup, audio-init failure cleanup, disconnect with open V4L2 descriptors, and register write error handling through USB fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/usbtv-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/usbtv-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/usbtv-video.c

Purpose: implements the V4L2 capture device for USBTV007. It exposes a YUYV interlaced video capture node, manages vb2 buffers, programs decoder/input/norm controls through vendor registers, submits isochronous URBs, and reconstructs frames from proprietary 256-byte USB chunks.

Important APIs and functions: exported lifecycle functions are `usbtv_video_init` and `usbtv_video_free`. Capture setup uses `usbtv_configure_for_norm`, `usbtv_select_input`, `usbtv_select_norm`, and `usbtv_setup_capture`. Streaming uses `usbtv_start`, `usbtv_stop`, `usbtv_setup_iso_transfer`, `usbtv_iso_cb`, `usbtv_image_chunk`, and `usbtv_chunk_to_vbuf`. V4L2/vb2 operations are provided through `usbtv_ioctl_ops`, `usbtv_fops`, and `usbtv_vb2_ops`. Image controls are handled by `usbtv_s_ctrl`.

Control flow: init configures NTSC dimensions by default, initializes locks and the vb2 queue, creates brightness/contrast/saturation/hue/sharpness controls, registers a `v4l2_device`, and registers a video node. Streaming start suspends audio, switches to alternate setting 0, programs capture registers, applies norm/input/controls, switches to alternate setting 1, resumes audio, allocates 16 isochronous URBs, and submits them. URB completion walks packet descriptors and feeds every 256-byte chunk to the image assembler. The assembler validates magic, frame id, field bit, and chunk number, copies the 240-word payload into alternating field lines, and completes the first queued vb2 buffer when the last odd field finishes.

State and persistence: frame assembly state includes `frame_id`, `chunks_done`, `last_odd`, `sequence`, `n_chunks`, dimensions, input, norm, and the queue of user buffers protected by `buflock`. URBs are transient and freed on stream stop. No settings are persisted outside the device; control defaults are re-applied at capture setup.

Dependencies and integration points: depends on V4L2 ioctl/control APIs, videobuf2 vmalloc memory, USB isochronous transfers, and shared USBTV constants/register helper. It coordinates with audio suspend/resume around USB alternate setting changes. Userspace integration is standard V4L2 read/mmap/userptr capture with fixed format reporting.

Risks: frame completion compares `chunks_done` only to `n_chunks`, yet two fields are involved; missing chunks or field transitions can mark buffers error or drop frames. The code copies chunk data while holding a spinlock, increasing IRQ-off work. Control writes allocate small buffers and perform synchronous USB control requests under V4L2 control context. `vidioc_s_fmt_vid_cap` ignores requested format and only reports current fixed geometry. URB setup assumes `iso_size` from probe remains valid for the chosen endpoint/altsetting.

Test signals: stream NTSC and PAL/SECAM-like norms, switch composite/S-Video inputs, adjust all image controls, verify YUYV frame size and interlacing, stress slow userspace with too few buffers, inject corrupt chunk magic/frame ids/missing chunks, run video while ALSA capture is active, and test streamoff/disconnect during active URBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/usbtv-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/usbtv.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/usbtv.h

Purpose: defines the shared USBTV007 driver contract used by the core, video, and audio source files. It centralizes endpoint numbers, vendor request/register constants, chunk geometry, TV standards, common structures, and cross-module function declarations.

Important APIs and types: constants include `USBTV_VIDEO_ENDP`, `USBTV_AUDIO_ENDP`, `USBTV_BASE`, request IDs, isochronous transfer sizing, image chunk sizing, and audio buffer sizing. Header macros decode proprietary video chunk headers: `USBTV_MAGIC_OK`, `USBTV_FRAME_ID`, `USBTV_ODD`, and `USBTV_CHUNK_NO`. Types include `struct usbtv_norm_params`, `struct usbtv_buf`, and the per-device `struct usbtv`. Declared functions are `usbtv_set_regs`, video lifecycle functions, and audio lifecycle/suspend/resume functions.

Control flow: this header itself has no executable flow, but it defines how the modules interact. `usbtv-core.c` owns allocation and calls video/audio init/free. `usbtv-video.c` uses endpoint/chunk/norm definitions for capture and frame assembly. `usbtv-audio.c` uses audio endpoint and buffer constants for PCM streaming. The function prototypes make these boundaries explicit.

State and persistence: `struct usbtv` is the central volatile state object. It embeds V4L2 device/control/video/vb2 state, buffer lists and frame assembly counters, current input/norm/geometry, isochronous URB pointers, ALSA card/substream state, audio stream flag/work item, audio URB pointer, and ALSA ring positions. It contains no persistent configuration.

Dependencies and integration points: includes USB, module, slab, V4L2 device/control/vb2 headers. The header is the integration point between Linux USB probing, V4L2 capture, vb2 memory management, and ALSA capture implemented by separate translation units.

Risks: because the shared struct carries both audio and video state, locking and lifetime assumptions are spread across files. Chunk macros assume big-endian 32-bit chunk words and specific bit layout. `USBTV_ODD` shifts a masked bit field by 15 after masking `0x0000f000`, which produces non-boolean values if multiple bits appear; consumers only test truthiness. Constant changes can alter buffer sizes and frame reconstruction math across modules.

Test signals: compile all three USBTV objects together, verify structure fields used by each translation unit match lifecycle assumptions, and exercise combined audio/video streaming, disconnect, and norm changes to validate shared state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/usbtv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/Kconfig

Purpose: declares the kernel configuration switches for the USB Video Class driver and its optional input-event support.

Important symbols: `USB_VIDEO_CLASS` is a tristate named "USB Video Class (UVC)", depends on `VIDEO_DEV`, and selects `VIDEOBUF2_VMALLOC` and `UVC_COMMON`. `USB_VIDEO_CLASS_INPUT_EVDEV` is a bool for UVC input events device support, defaults to yes, depends on `USB_VIDEO_CLASS`, and requires either built-in input support or matching modular input support.

Control flow: these Kconfig symbols determine whether `uvcvideo.o` is built by the sibling Makefile and whether button/event support is compiled in elsewhere in the UVC driver. The help text describes webcam-style video input support and event reporting for device buttons.

State and persistence: no runtime state is stored here. The selected values are persisted only in the kernel build configuration and affect compile-time object inclusion and dependencies.

Dependencies and integration points: integrates with the media subsystem through `VIDEO_DEV`, videobuf2 vmalloc allocation, common UVC code, and input core constraints. The Makefile consumes `CONFIG_USB_VIDEO_CLASS` to build the module.

Risks: selecting vmalloc-backed vb2 constrains the queue implementation choice in `uvc_queue.c`. The input-event option has a compound dependency that must keep modular/built-in combinations link-safe. Help text still references the historical linux-uvc site and may not reflect current documentation.

Test signals: run Kconfig dependency checks for built-in and module combinations, build with UVC disabled/enabled, build with input event support enabled and disabled, and verify `uvcvideo` links when `INPUT` is modular or built in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/Makefile

Purpose: defines how the UVC driver module is composed from its implementation objects.

Important build entries: `uvcvideo-objs` always includes `uvc_driver.o`, `uvc_queue.o`, `uvc_v4l2.o`, `uvc_video.o`, `uvc_ctrl.o`, `uvc_status.o`, `uvc_isight.o`, `uvc_debugfs.o`, and `uvc_metadata.o`. When `CONFIG_MEDIA_CONTROLLER=y`, it also includes `uvc_entity.o`. `obj-$(CONFIG_USB_VIDEO_CLASS) += uvcvideo.o` ties the aggregate object to the Kconfig symbol.

Control flow: no runtime execution occurs, but this file controls link composition. The main driver, V4L2 ioctl layer, streaming engine, controls, status endpoint handling, Apple iSight decoder, debugfs, metadata capture, and optional media-controller graph support are linked into one `uvcvideo` module or built-in object.

State and persistence: build state only. The selected object list affects which symbols exist at runtime, especially media-controller entity registration and cleanup.

Dependencies and integration points: consumes `CONFIG_USB_VIDEO_CLASS` from Kconfig and `CONFIG_MEDIA_CONTROLLER` from the media core. It must remain consistent with prototypes and conditional stubs in `uvcvideo.h`.

Risks: adding a new UVC feature requires updating this object list or it will compile in isolation but fail to link. `uvc_entity.o` is only built for built-in media-controller support, so references to its functions must stay guarded by `CONFIG_MEDIA_CONTROLLER`.

Test signals: build UVC as a module and built in, with and without `CONFIG_MEDIA_CONTROLLER`, and run modpost/link checks for missing UVC symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_ctrl.c

Purpose: implements UVC control discovery, V4L2 control mapping, query/set transactions, extension-unit access, control events, and resume-time control restoration. It bridges UVC selector-based USB control requests to V4L2 scalar/menu/bitmask/compound controls.

Important APIs and functions: public functions include `uvc_query_v4l2_ctrl`, `uvc_query_v4l2_menu`, `uvc_ctrl_is_accessible`, `uvc_ctrl_begin`, `uvc_ctrl_get`, `uvc_ctrl_set`, `__uvc_ctrl_commit`, `uvc_xu_ctrl_query`, `uvc_ctrl_restore_values`, `uvc_ctrl_add_mapping`, `uvc_ctrl_init_device`, `uvc_ctrl_cleanup_fh`, and `uvc_ctrl_cleanup_device`. Static tables `uvc_ctrls` and `uvc_ctrl_mappings` define standard UVC controls and V4L2 mappings. Helpers translate little-endian bit fields, menu mappings, relative PTZ speeds, ROI rectangles, and power-line-frequency variants.

Control flow: device initialization walks each video chain entity, prunes blacklisted controls, allocates `struct uvc_control` arrays from entity bitmaps, initializes known standard controls, queries flags with `GET_INFO`, and attaches stock mappings. Extension-unit controls are lazily initialized with `GET_LEN` and `GET_INFO`. Query paths lock `chain->ctrl_mutex`, find mappings by V4L2 ID, populate cached boundaries with `GET_MIN/MAX/RES/DEF`, and synthesize `v4l2_query_ext_ctrl` or menu responses. Set paths use a begin/set/commit transaction: `uvc_ctrl_set` clamps and stages values in current data, marks controls dirty, and `__uvc_ctrl_commit` writes dirty controls with `SET_CUR`, rolling back cached data on errors and sending V4L2 events.

State and persistence: each control owns cached UVC data slots for current, backup, min, max, resolution, and default. Flags such as `initialized`, `cached`, `loaded`, `dirty`, and `modified` track control lifetime and restore behavior. Modified controls flagged `UVC_CTRL_FLAG_RESTORE` are written back after reset resume. Event subscriptions live on mapping lists; asynchronous controls hold a file-handle pointer and runtime PM reference until status completion clears them.

Dependencies and integration points: depends on USB control requests via `uvc_query_ctrl`, V4L2 control/event APIs, UVC entity topology from `uvc_driver.c`, runtime PM helpers, user-copy APIs for extension controls and compound payloads, and status endpoint callbacks for auto-update/asynchronous notifications.

Risks: malformed firmware control descriptors can cause permanent control disabling or mapping omission. Read-modify-write mappings require a successful current-value load when a mapping spans only part of a UVC control. Asynchronous control handling has nontrivial ownership of file handles and PM references. User-defined XU mappings are bounded by `UVC_MAX_CONTROL_MAPPINGS` but still increase attack surface. Menu filtering performs real `SET_CUR` probes and restores the initial value, which can have side effects on broken devices.

Test signals: enumerate controls with and without `NEXT_CTRL`, query min/max/default/current values, set grouped controls atomically with rollback injection, test auto/manual master-slave inactive flags, subscribe to control events including initial events, exercise XU `GET_LEN/GET_INFO/GET/SET`, run reset resume restore, and validate blacklist/fixup behavior on matching USB IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_debugfs.c

Purpose: provides debugfs support for UVC stream statistics. It creates a global `uvcvideo` debugfs directory and per-stream directories containing a read-only `stats` file.

Important APIs and functions: public functions are `uvc_debugfs_init`, `uvc_debugfs_cleanup`, `uvc_debugfs_init_stream`, and `uvc_debugfs_cleanup_stream`. File operations are `uvc_debugfs_stats_open`, `uvc_debugfs_stats_read`, and `uvc_debugfs_stats_release`, backed by `uvc_debugfs_stats_fops`. The per-open buffer type is `struct uvc_debugfs_buffer`.

Control flow: module init calls `uvc_debugfs_init` to create the root under `usb_debug_root`. Stream registration calls `uvc_debugfs_init_stream`, which names the directory from USB bus number, device number, and streaming interface number, then creates `stats`. Opening `stats` allocates a 1024-byte buffer and snapshots `uvc_video_stats_dump`; reads copy that snapshot through `simple_read_from_buffer`; release frees the buffer. Stream unregister and module cleanup remove debugfs trees recursively.

State and persistence: the global root dentry and per-stream `debugfs_dir` pointers are transient. Stats contents are snapshotted per open, not live-updated during a read. Nothing persists outside debugfs.

Dependencies and integration points: depends on Linux debugfs, USB debug root, and `uvc_video_stats_dump` from the streaming implementation. It is called from UVC module init/exit and from stream video registration/unregistration in `uvc_driver.c`.

Risks: debugfs creation failures are not checked, which is normal for optional diagnostics but means absent files are not fatal. The fixed 1024-byte stats buffer can truncate future statistics if `uvc_video_stats_dump` grows. Directory names can collide only if bus/device/interface tuples collide, which USB core should prevent for live devices.

Test signals: mount debugfs, load UVC, stream from a camera, verify `/sys/kernel/debug/usb/uvcvideo/<bus>-<dev>-<intf>/stats` appears, read it before and after streaming errors, and confirm cleanup on disconnect and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_driver.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_driver.c

Purpose: is the main USB Video Class driver. It handles USB matching/probe/disconnect/PM, parses UVC descriptors into entities and streams, builds video chains, registers V4L2 and optional media-controller devices, manages quirks/module parameters, and owns top-level device lifetime.

Important APIs and functions: exported helpers include `uvc_find_endpoint`, `uvc_entity_by_id`, and `uvc_register_video_device`. Probe/lifecycle functions include `uvc_probe`, `uvc_disconnect`, `uvc_suspend`, `uvc_resume`, `uvc_reset_resume`, `uvc_delete`, and `uvc_unregister_video`. Descriptor and topology functions include `uvc_parse_control`, `uvc_parse_standard_control`, `uvc_parse_vendor_control`, `uvc_parse_streaming`, `uvc_parse_format`, `uvc_parse_frame`, `uvc_scan_device`, `uvc_scan_chain`, and `uvc_scan_fallback`. `uvc_ids` is the large device/quirk table.

Control flow: probe allocates `struct uvc_device`, initializes lists/refcounts, applies static or module-forced quirks, names the device, initializes media-device metadata when enabled, parses the VideoControl interface, claims and parses referenced streaming interfaces, optionally creates a privacy GPIO entity, registers the V4L2 device, scans entity chains from output terminals backward with forward branch discovery, initializes controls, registers video and metadata nodes, registers media-controller entities, initializes status URB/GPIO IRQ/metadata formats, and enables autosuspend unless quirked off. Disconnect unregisters video/status/GPIO resources and drops the device reference. PM callbacks split between VideoControl status/control restore and VideoStreaming stream suspend/resume.

State and persistence: `struct uvc_device` owns entities, chains, streams, quirks, UVC version, status endpoint, metadata formats, GPIO unit, V4L2/media devices, and kref lifetime. Entities and streams are allocated from descriptors and persist until the last video node reference releases `uvc_delete`. Runtime parameters such as `clock`, `hwtimestamps`, `nodrop`, `quirks`, `trace`, and `timeout` are module state.

Dependencies and integration points: integrates USB core, V4L2 registration, videobuf2 queues, UVC control/status/video/metadata modules, optional media controller, GPIO descriptors/IRQs for privacy controls, and runtime PM/autosuspend. The ID table carries compatibility knowledge for many vendor devices and Intel RealSense metadata formats.

Risks: descriptor parsing accepts many malformed-device workarounds, so bounds checks and ID collision handling are security-critical. The chain scanner mutates entity source IDs for some broken topologies and uses a fallback heuristic for known invalid chains. Probe has many partial-registration stages; cleanup ordering must keep USB interfaces, video nodes, status URBs, GPIO IRQs, and krefs consistent. Forced quirks are useful for testing but can hide real descriptor bugs or create unsupported combinations.

Test signals: probe generic UVC 1.1/1.5 cameras and listed quirk devices, parse devices with multiple streaming interfaces and invalid descriptors, verify video and metadata node registration, media graph links, privacy GPIO events, status endpoint behavior, autosuspend, suspend/resume/reset-resume with active streams, disconnect with open file handles, and module parameters for clock/quirks/nodrop/timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_entity.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_entity.c

Purpose: implements media-controller entity registration for UVC devices when `CONFIG_MEDIA_CONTROLLER` is enabled. It turns parsed UVC entities into media entities/subdevices and creates immutable pad links that mirror the UVC topology.

Important APIs and functions: exported functions are `uvc_mc_register_entities` and `uvc_mc_cleanup_entity`. Internal helpers are `uvc_mc_init_entity` and `uvc_mc_create_links`. The file uses an empty `v4l2_subdev_ops` table because entities are represented for topology rather than active subdevice operations.

Control flow: registration first iterates chain entities and initializes each media entity. Non-streaming UVC units become V4L2 subdevices with functions selected from entity type, such as mux, processing formatter, composite/S-Video connector, or camera sensor. Streaming terminals initialize pads on the already registered video node and can be marked default. A second pass creates enabled immutable pad links from each sink pad to the source entity referenced by `baSourceID`. Cleanup tears down either subdevice media entities or video-node media entities.

State and persistence: media entity state is attached to `struct uvc_entity` subdevices or video device entities and lasts until device cleanup. Link topology is runtime-only and regenerated on probe.

Dependencies and integration points: depends on media controller core, V4L2 subdev registration, parsed UVC chain/entity data from `uvc_driver.c`, and video-node pointers filled during stream registration. It is called from `uvc_register_chains` and `uvc_delete`.

Risks: link creation depends on valid `baSourceID` and pad counts; malformed topology returns errors after some entities may already be initialized. Function classification is approximate for processing and extension units. Conditional build means declarations and call sites must remain guarded by `CONFIG_MEDIA_CONTROLLER`.

Test signals: enable media controller and inspect `media-ctl -p` output for cameras with camera, processing, selector, extension, streaming, and GPIO entities; verify immutable links, default video entity flag, cleanup on probe failure/disconnect, and behavior for missing or invalid source references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_entity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_isight.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_isight.c

Purpose: provides a custom payload decoder for Apple built-in iSight webcams that mostly implement UVC 1.0 but use a nonstandard packet format with one proprietary header packet per image instead of a UVC header on every isochronous payload.

Important APIs and functions: exported function is `uvc_video_decode_isight`. Internal helper `isight_decode` identifies proprietary headers, synchronizes buffers, copies payload data, and detects frame completion. The decoder is selected by the streaming code when the device has `UVC_QUIRK_BUILTIN_ISIGHT`.

Control flow: for each isochronous packet, `uvc_video_decode_isight` logs packet loss status and repeatedly invokes `isight_decode` because a header can both finish the previous frame and begin the next. `isight_decode` treats packets containing the `11223344 deadbeefdeadface` signature at offset 2 or 3 as headers. It drops packets until a header synchronizes the buffer, completes a nonempty active buffer when a new header arrives, skips copying header packets, copies non-header bytes into the current buffer, and marks the buffer done on overflow or exact fill.

State and persistence: no persistent device state is owned by this file. It mutates `struct uvc_buffer` state, bytes used, and memory contents through the queue supplied by the generic UVC video path.

Dependencies and integration points: depends on UVC queue helpers, isochronous URB packet descriptors, and generic streaming code in `uvc_video.c`. The main driver sets the iSight quirk in `uvc_driver.c` for Apple built-in iSight devices and suppresses normal status endpoint handling for that quirk.

Risks: header detection uses fixed magic bytes and optional one-byte prefix; any data packet matching that pattern would cause premature frame completion. Frame boundaries rely on seeing the next header, so dropped header packets can desynchronize capture. The metadata buffer argument is unused, so iSight metadata capture is not supported here.

Test signals: capture from Apple built-in iSight hardware, verify synchronization after stream start and packet loss, ensure frames complete at header transitions, test small buffers/overflow handling, and compare decoded image sizes and frame rates against expected UVC format negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_isight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_metadata.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_metadata.c

Purpose: implements UVC metadata capture node registration and metadata format negotiation. It exposes a V4L2 metadata capture device per stream and detects Microsoft UVC 1.5 extension-unit metadata support.

Important APIs and functions: exported functions are `uvc_meta_register` and `uvc_meta_init`. V4L2 ioctl handlers are `uvc_meta_v4l2_querycap`, `uvc_meta_v4l2_get_format`, `uvc_meta_v4l2_try_format`, `uvc_meta_v4l2_set_format`, and `uvc_meta_v4l2_enum_formats`. Detection helpers are `uvc_meta_find_msxu` and `uvc_meta_detect_msxu`.

Control flow: `uvc_meta_init` probes for an MSXU entity with `UVC_GUID_MSXU_1_5`, reads current metadata control state, and if needed tries to enable metadata by reading `GET_MAX` and writing that value with `SET_CUR`. It then fills the device metadata format array with generic `V4L2_META_FMT_UVC`, optional device-info metadata format such as RealSense D4XX, and optional `V4L2_META_FMT_UVC_MSXU_1_5`. `uvc_meta_register` initializes stream metadata defaults and calls the common `uvc_register_video_device` path with metadata file/ioctl operations. Format setting validates requested type, picks a supported dataformat, enforces minimum buffer size, and refuses changes while the metadata vb2 queue is busy.

State and persistence: stream metadata state is `stream->meta.format`, `stream->meta.buffersize`, and its vb2 queue/video node. Device metadata support is stored in `dev->meta_formats`, `dev->nmeta_formats`, and possibly `UVC_QUIRK_MSXU_META`. The MSXU enable write changes device runtime state but is not persisted by this file.

Dependencies and integration points: depends on V4L2 metadata APIs, vb2 vmalloc queues through `uvc_queue.c`, UVC extension-unit queries through `uvc_query_ctrl`, and the common video-device registration helper in `uvc_driver.c`. Actual metadata payload filling is done by the streaming implementation.

Risks: enabling MSXU metadata writes to device controls during probe and silently treats most query failures as lack of support. Metadata node registration failures are ignored by `uvc_register_terms`, so video capture can work without metadata. Buffer sizes are user-influenced but clamped only to a minimum; downstream payload writers must respect vb2 plane size.

Test signals: enumerate metadata formats on ordinary UVC and RealSense devices, verify MSXU metadata enablement and format exposure, set metadata buffer size before streaming, confirm `-EBUSY` during streaming, stream video plus metadata and validate payload parseability, and test video registration when metadata registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_queue.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_queue.c

Purpose: implements shared videobuf2 queue management for UVC video and metadata buffers. It initializes queues, validates buffer sizes, manages the IRQ-side buffer list consumed by streaming URB callbacks, handles stream start/stop, disconnect cancellation, and delayed buffer completion through krefs.

Important APIs and functions: public functions are `uvc_queue_init`, `uvc_queue_cancel`, `uvc_queue_get_current_buffer`, `uvc_queue_next_buffer`, and `uvc_queue_buffer_release`. Core vb2 callbacks are `uvc_queue_setup`, `uvc_buffer_prepare`, `uvc_buffer_queue`, `uvc_buffer_finish`, `uvc_start_streaming_video`, `uvc_stop_streaming_video`, and `uvc_stop_streaming_meta`. Internal helpers return or requeue buffers and complete them when references drop.

Control flow: queue initialization sets type, io modes, buffer struct size, vmalloc memory ops, timestamp flags, and selects video or metadata vb2 ops. Buffer preparation checks output payload bounds, rejects disconnected queues, records memory pointer/length, and initializes bytes-used state. Queued buffers are added to `irqqueue` under `irqlock` unless disconnected. Video stream start gets a runtime PM reference, clears `buf_used`, and starts USB video streaming; failure returns queued buffers. Stop halts USB streaming, drops PM, and returns queued buffers as errors. Metadata queues have no start callback and rely on video streaming. Streaming code obtains the current buffer, advances with `uvc_queue_next_buffer`, and releases references when async work completes.

State and persistence: `struct uvc_video_queue` owns a vb2 queue, mutex, IRQ spinlock, `irqqueue`, flags such as `UVC_QUEUE_DISCONNECTED`, stream pointer, and per-stream buffer-use accounting. `struct uvc_buffer` stores state, error flag, memory pointer, length, bytes used, list node, and kref. All state is runtime-only.

Dependencies and integration points: depends on videobuf2-v4l2/vmalloc, UVC streaming functions from `uvc_video.c`, runtime PM helpers, global `uvc_no_drop_param`, and V4L2 timestamp clock update. It is used by video nodes from `uvc_driver.c` and metadata nodes from `uvc_metadata.c`.

Risks: disconnect handling must set `UVC_QUEUE_DISCONNECTED` under the IRQ lock to avoid races with QBUF and blocking dequeue. Buffer completion can requeue erroneous buffers when `nodrop` is disabled, changing userspace-visible frame loss behavior. Metadata queues do not start hardware, so userspace can stream metadata without receiving data if video is idle. Buffer lifetime relies on kref pairing between synchronous decode and asynchronous copy paths.

Test signals: run mmap/userptr/dmabuf capture, queue too-small buffers, stream video and metadata together, disconnect while dequeues are pending, inject URB errors with `nodrop` on/off, test output payload bounds if output devices are present, and verify timestamps are updated on completed video buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_queue.c -->
