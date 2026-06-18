# subset-b-004223 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_status.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_status.c

## Purpose
`uvc_status.c` implements the UVC driver's interrupt status endpoint handling. It receives asynchronous device notifications, dispatches streaming button/error events and control value-change events, and owns the lifetime of the status URB. When `CONFIG_USB_VIDEO_CLASS_INPUT_EVDEV` is enabled it also exposes compatible camera trigger buttons as a Linux input device reporting `KEY_CAMERA`.

## Important APIs, types, and functions
The public entry points are `uvc_status_init()`, `uvc_status_unregister()`, `uvc_status_cleanup()`, `uvc_status_resume()`, `uvc_status_suspend()`, `uvc_status_get()`, and `uvc_status_put()`. They operate on status fields in `struct uvc_device`: `int_ep`, `int_urb`, `status`, `status_lock`, `status_users`, `flush_status`, `input`, `input_phys`, and `async_ctrl`. `uvc_status_complete()` is the USB completion callback. `uvc_event_streaming()` handles streaming status packets. `uvc_event_control()` validates control status packets and calls `uvc_ctrl_status_event_async()` for value changes. The helper pair `uvc_event_find_ctrl()` and `uvc_event_entity_find_ctrl()` resolve the originator and selector in a status packet to a `struct uvc_control` inside a `struct uvc_video_chain`.

## Control flow
Initialization allocates `dev->status`, allocates `dev->int_urb`, computes the receive interrupt pipe, applies the high-speed interval quirk when requested, fills the URB, and optionally registers an input device. The status endpoint is demand-started: `uvc_status_get()` submits the URB when the first user arrives, increments `status_users`, and `uvc_status_put()` stops it when the last user leaves. Completion accepts only success and benign shutdown/unlink errors. On successful packets it switches on `bStatusType & 0x0f`; control events may transfer URB resubmission to the asynchronous control worker, while streaming events are handled inline and the URB is normally resubmitted in atomic context.

## State and persistence behavior
All persistent state is in memory and tied to the USB device lifetime. `status_users` is a reference count guarded by `status_lock`; it controls whether the interrupt URB is active across open/close and suspend/resume. `flush_status` is a cross-CPU stop flag coordinated with release stores to prevent the asynchronous control work item from requeuing the URB during stop. Input device registration persists from init until unregister; there is no disk persistence.

## Dependencies and integration points
This file integrates with USB core URBs, Linux input, the UVC control subsystem, and V4L2 device chains. It relies on `uvcvideo.h` structures, `uvc_ctrl_status_event_async()`, `uvc_ctrl_status_event()`, and the entity/control graph populated by UVC descriptor parsing. Runtime PM users in `uvc_v4l2.c` call `uvc_status_get()` and `uvc_status_put()` through `uvc_pm_get()`/`uvc_pm_put()`.

## Risks and edge cases
The highest-risk area is stop/resume ordering: `uvc_status_stop()` must cancel pending work, kill the URB, then cancel work again because completion can queue work during teardown. Incorrect memory ordering around `flush_status` can cause URB requeue races. Status packet validation is intentionally conservative; malformed control events are ignored. Input support depends on trigger descriptor bits, so devices with nonstandard button reporting may not expose an input device. URB resubmission failures are logged but leave the status path inactive.

## Test signals
Useful tests include open/close cycles that exercise `status_users`, suspend/resume with active users, unplug while status URB is active, cameras that emit control-change interrupts, and devices with physical shutter/snapshot buttons. Debug categories `STATUS` and input event traces should show valid button/control event flow. Race testing should focus on simultaneous status events and stream or file-handle teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_v4l2.c

## Purpose
`uvc_v4l2.c` is the UVC driver's V4L2 userspace API layer. It implements file operations and ioctl callbacks for format negotiation, frame interval selection, input selection, controls, event subscription, dynamic extension-unit control mapping, and runtime PM wrapping for hardware-touching operations.

## Important APIs, types, and functions
The exported operation tables are `uvc_ioctl_ops` and `uvc_fops`. Runtime PM helpers `uvc_pm_get()` and `uvc_pm_put()` pair USB autosuspend references with status endpoint references. Format negotiation is centered on `uvc_v4l2_try_format()`, `uvc_ioctl_g_fmt()`, `uvc_ioctl_s_fmt()`, and `uvc_ioctl_try_fmt()`. Frame interval handling uses `uvc_ioctl_g_parm()`, `uvc_ioctl_s_parm()`, `uvc_try_frame_interval()`, and `v4l2_fraction_to_interval()`. Control ioctls use `uvc_ioctl_g_ext_ctrls()`, `uvc_ioctl_s_try_ext_ctrls()`, `uvc_ctrl_begin()`, `uvc_ctrl_get()`, `uvc_ctrl_set()`, `uvc_ctrl_commit()`, and rollback. UVC-specific extension ioctls are handled by `uvc_ioctl_xu_ctrl_map()`, `uvc_control_add_xu_mapping()`, and `uvc_ioctl_default()`.

## Control flow
Opening a node allocates `struct uvc_fh`, initializes a V4L2 file handle, and attaches the current chain and stream. Release cleans pending controls and delegates buffer cleanup to vb2. `S_FMT` calls the shared try-format helper, refuses changes while the vb2 queue is busy, then commits `stream->ctrl`, `cur_format`, and `cur_frame`. `S_PARM` refuses active streaming, finds the closest supported interval among matching-size frames, probes the device, and updates current frame/stream control state. Hardware-dependent ioctls are routed through `uvc_v4l2_unlocked_ioctl()`, which takes runtime PM and status references, calls `video_ioctl2()`, and releases them afterward.

## State and persistence behavior
Per-open state lives in `struct uvc_fh` and includes the V4L2 file handle, chain, stream, and pending async control count. Per-stream negotiated state is in memory in `struct uvc_streaming`: `ctrl`, `cur_format`, `cur_frame`, and queue state. Dynamic XU mappings alter in-kernel control mapping state through `uvc_ctrl_add_mapping()` but are not persisted to disk. Runtime PM references are transient and scoped to ioctl execution.

## Dependencies and integration points
The file sits between V4L2 core (`video_ioctl2`, v4l2 events, v4l2 controls), videobuf2 file/ioctl helpers, USB runtime PM, and the UVC control/video implementation. Format probing calls `uvc_probe_video()` from `uvc_video.c`; control requests call into UVC control code; selector-unit input switching uses `uvc_query_ctrl()`. It also supplies compat ioctl translation for 32-bit userspace when `CONFIG_COMPAT` is enabled.

## Risks and edge cases
Format selection trusts device probe responses but falls back when devices return unknown format/frame indexes. `uvc_try_frame_interval()` assumes descriptor intervals are ordered well enough for distance comparison. XU mapping copies user-provided menu values/names and therefore must bound counts and clean temporary allocations on all exits. Runtime PM wrapping must include every ioctl that touches the device; missing one can access suspended hardware, while unnecessary wrapping can wake devices. Busy checks around format/input changes prevent stream-time reconfiguration bugs.

## Test signals
Exercise `VIDIOC_ENUM_FMT`, `TRY_FMT`, `S_FMT`, `G/S_PARM`, stream-on busy rejection, selector input get/set, control get/set/try, XU mapping/query, 32-bit compat ioctls, and event subscription. Hardware tests should include devices with invalid probe responses, multiple frame intervals at the same size, extension controls with menus, and autosuspend enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_video.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_video.c

## Purpose
`uvc_video.c` implements UVC video transport. It performs USB class control transactions for video probe/commit, fixes known device-specific descriptor/control defects, converts payload timestamps, decodes capture payloads, encodes output payloads, captures metadata headers, allocates and submits video URBs, and starts/stops streaming across normal operation and suspend/resume.

## Important APIs, types, and functions
Public entry points include `uvc_query_ctrl()`, `uvc_probe_video()`, `uvc_video_clock_update()`, `uvc_video_stats_dump()`, `uvc_video_init()`, `uvc_video_suspend()`, `uvc_video_resume()`, `uvc_video_start_streaming()`, and `uvc_video_stop_streaming()`. Probe/commit helpers include `__uvc_query_ctrl()`, `uvc_get_video_ctrl()`, `uvc_set_video_ctrl()`, `uvc_fixup_video_ctrl()`, and `uvc_commit_video()`. Streaming data flow uses `uvc_video_complete()`, `uvc_video_decode_isoc()`, `uvc_video_decode_bulk()`, `uvc_video_encode_bulk()`, `uvc_video_decode_start()`, `uvc_video_decode_data()`, `uvc_video_decode_end()`, and `uvc_video_next_buffers()`. URB memory management is handled by `uvc_alloc_urb_buffers()`, `uvc_init_video_isoc()`, `uvc_init_video_bulk()`, `uvc_video_start_transfer()`, and `uvc_video_stop_transfer()`.

## Control flow
Initialization resets the streaming interface to alternate setting 0, retrieves default/current probe controls, selects default/current format and frame descriptors, chooses the decode or encode function, and initializes async copy work. Starting streaming initializes the timestamp clock, commits negotiated controls, selects an isochronous alternate setting or bulk endpoint, allocates URBs and noncoherent buffers, submits all URBs, and optionally restores controls for affected devices. Completion fetches current video and metadata buffers, decodes or encodes payloads, queues async memcpy work if needed, and resubmits the URB. Stop poisons URBs, flushes the async workqueue, frees URBs and optionally buffers, resets the interface or clears bulk halt, and releases clock samples.

## State and persistence behavior
All state is volatile and stream-scoped. `struct uvc_streaming` stores negotiated `ctrl`, current format/frame, `sequence`, `last_fid`, bulk payload accumulator state, URB contexts, async workqueue, metadata queue configuration, statistics, and the timestamp clock ring buffer. `struct uvc_buffer` tracks bytes used, sequence, error state, PTS, and async reference count. No data persists beyond device/stream lifetime, but quirk behavior encodes long-lived compatibility policy for known devices.

## Dependencies and integration points
This file integrates with USB control and data paths, videobuf2 queues, UVC descriptor-derived format/frame tables, UVC control restore logic, JPEG marker helpers, debugfs statistics consumers, and V4L2 buffer timestamp semantics. It consumes module parameters such as `uvc_timeout_param`, `uvc_clock_param`, `uvc_hw_timestamps_param`, and quirk flags from `struct uvc_device`.

## Risks and edge cases
The main risks are concurrency and malformed device behavior. URBs can complete during teardown; poisoning plus workqueue flushing prevents resubmission after stop. Async memcpy takes buffer references and must release them exactly once. Payload parsing must handle missing EOF, missing/toggling FID, short headers, error bits, empty packets, bulk payloads spanning URBs, overflow, and queue cancellation with `buf == NULL`. Timestamp interpolation depends on enough SCR samples, SOF wrap handling, and device clock quality. Probe/commit code contains many workarounds; changing them can regress real hardware.

## Test signals
Test with isochronous and bulk cameras, capture and output devices, suspend/resume while streaming, unplug during active URBs, autosuspend wake quirks, multiple resolutions/intervals, metadata capture, hardware timestamps enabled/disabled, MJPEG streams with lost EOF, malformed short packets, and low-memory URB allocation fallback. Debug categories `VIDEO`, `FRAME`, `STATS`, and `CLOCK` provide strong runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvcvideo.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvcvideo.h

## Purpose
`uvcvideo.h` is the internal header for the UVC kernel driver. It defines driver constants, quirk bits, core device/stream/entity/control/buffer structures, debug helpers, and internal function prototypes shared across UVC source files.

## Important APIs, types, and functions
Key types are `struct uvc_device`, `struct uvc_streaming`, `struct uvc_video_chain`, `struct uvc_entity`, `struct uvc_control`, `struct uvc_control_mapping`, `struct uvc_format`, `struct uvc_frame`, `struct uvc_video_queue`, `struct uvc_buffer`, `struct uvc_urb`, `struct uvc_status`, and statistics/clock structs. Macros classify entities (`UVC_ENTITY_IS_*`), define transfer sizing (`UVC_URBS`, `UVC_MAX_PACKETS`), expose quirk flags, and implement debug logging (`uvc_dbg`, `uvc_warn_once`). It declares the V4L2 operation tables, video functions, status functions, control functions, queue functions, media-controller hooks, PM helpers, metadata registration, debugfs support, and utility helpers.

## Control flow
The header does not execute control flow directly, but it shapes module interactions. `uvc_device` owns the global USB/V4L2/media state and lists of streams/chains/entities. `uvc_streaming` owns a stream's negotiated parameters, queue, URBs, decode callback, metadata queue, bulk accumulator, sequence/FID tracking, statistics, and timestamp clock. `uvc_video_chain` groups entities and control priority/mutex state for V4L2-facing file handles. Function prototypes define the flow from probe/registration through V4L2 ioctls, queue streaming, USB transfer, status events, controls, suspend/resume, and cleanup.

## State and persistence behavior
All structures are runtime kernel objects. Important state boundaries include device lifetime (`uvc_device`), streaming-interface lifetime (`uvc_streaming`), open-file lifetime (`uvc_fh`), queued buffer lifetime (`uvc_buffer`), and URB lifetime (`uvc_urb`). Synchronization fields include `status_lock`, `ctrl_mutex`, queue mutex/spinlock, clock spinlock, krefs, atomics, and work structs. There is no persistent storage; descriptor-derived data and dynamic mappings live until cleanup.

## Dependencies and integration points
The header binds UVC code to Linux USB, input, media controller, V4L2 device/event/fh/subdev APIs, and videobuf2. It includes public UVC and videodev2 headers while keeping internal declarations private to the driver. It also provides the interface between UVC-specific code and generic V4L2 core files through operation tables and ioctl callbacks.

## Risks and edge cases
Because this header defines shared structure layouts, small changes can have wide blast radius across controls, video, queueing, status, and registration code. Bitfields and flags such as buffer state, `frozen`, `flush_status`, and quirks must remain consistent with locking expectations. The `uvc_status` and related structs are packed to match USB payloads; alignment or size changes would break parsing. Function prototype changes require coordinated updates across the driver.

## Test signals
Any change should trigger broad UVC build coverage across configurations: media controller on/off, input evdev on/off, metadata, compat, and multiple architectures. Runtime tests should cover open/close, streaming, controls, status events, suspend/resume, metadata, and disconnect because this header connects all those paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvcvideo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/Kconfig

## Purpose
This Kconfig fragment defines V4L2 core feature symbols and helper module symbols used by media drivers. It controls optional subdevice APIs, advanced debug behavior, old fixed minor allocation, tuner support, codec/helper modules, mem2mem support, flash LED integration, fwnode/async support, CCI register helpers, and ISP support.

## Important symbols
`VIDEO_V4L2_I2C` is an internal bool enabled by default when both I2C and VIDEO_DEV are available. `VIDEO_V4L2_SUBDEV_API` exposes the pad-level subdevice userspace API and depends on media controller support. `VIDEO_ADV_DEBUG` and `VIDEO_FIXED_MINOR_RANGES` are user-visible toggles. `VIDEO_TUNER`, `V4L2_JPEG_HELPER`, `V4L2_H264`, `V4L2_VP9`, `V4L2_MEM2MEM_DEV`, `V4L2_FLASH_LED_CLASS`, `V4L2_FWNODE`, `V4L2_ASYNC`, `V4L2_CCI`, `V4L2_CCI_I2C`, and `V4L2_ISP` determine which helper objects or modules are built.

## Control flow
Kconfig has declarative dependency flow. Selecting `V4L2_FLASH_LED_CLASS` pulls in media controller, async, and subdev API support. Selecting `V4L2_FWNODE` pulls in async support. Selecting `V4L2_CCI_I2C` depends on I2C and selects both regmap I2C support and the base CCI helper. `V4L2_MEM2MEM_DEV` and `V4L2_ISP` depend on videobuf2 core.

## State and persistence behavior
The file persists build-time configuration, not runtime state. The resulting `.config` choices decide which V4L2 objects, exported symbols, and APIs are available to drivers. User-visible bools can affect compatibility with legacy userspace or debugging workflows.

## Dependencies and integration points
This fragment is paired with `drivers/media/v4l2-core/Makefile`. Symbols here gate compilation of files such as `tuner-core.c`, `v4l2-async.c`, `v4l2-cci.c`, `v4l2-fwnode.c`, codec helpers, and mem2mem helpers. Driver Kconfigs outside this directory select or depend on these symbols.

## Risks and edge cases
Incorrect dependencies can cause link failures, hidden APIs, or invalid user-visible configurations. Overusing `select` can silently enable dependencies without their prerequisites; underusing it can make helper symbols unavailable to drivers. Legacy `VIDEO_FIXED_MINOR_RANGES` should remain opt-in because it conflicts with modern udev-based allocation expectations.

## Test signals
Build matrix tests should cover VIDEO_DEV with and without I2C, MEDIA_CONTROLLER, LED flash class, V4L2_FWNODE, CCI over I2C, mem2mem, and helper modules as built-in and module. `make oldconfig`/`savedefconfig` diffs are useful signals for accidental prompt or default changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/Makefile

## Purpose
This Makefile maps V4L2 core Kconfig symbols to built objects. It assembles the main `videodev` object, the `tuner` object, and optional helper modules such as async notifier, CCI, fwnode, codec helpers, flash LED support, media-controller support, SPI/I2C support, tracepoints, and mem2mem.

## Important build rules
The file adds include paths for DVB frontends and tuners because `tuner-core.c` dynamically attaches tuner frontend implementations. `tuner-objs := tuner-core.o` defines the tuner module body. `videodev-objs` combines core V4L2 files including device, ioctl, fh, event, subdev, common, and controls code. Conditional `videodev-$(CONFIG_*)` entries add compat ioctl, media controller, SPI, trace, and I2C support. Top-level `obj-$(CONFIG_*)` lines build individual helper modules and the main `videodev.o`.

## Control flow
Build flow is Kbuild-driven. If `CONFIG_VIDEO_DEV` is enabled, `videodev.o` is built from the base and conditional `videodev-*` object lists. If `CONFIG_VIDEO_TUNER` is enabled, `tuner.o` is built from `tuner-core.o`. Optional helpers are compiled independently according to their Kconfig symbols.

## State and persistence behavior
The file has no runtime state. Its persistent effect is the kernel build graph and module composition. Object ordering in `videodev-objs` can matter for readability and, in rare cases, initialization/link behavior.

## Dependencies and integration points
The Makefile is tightly coupled to the local Kconfig names and source file names. It integrates V4L2 core with media controller, tracepoints, I2C/SPI helper code, codec helpers, async registration, fwnode parsing, CCI helpers, and tuner support.

## Risks and edge cases
Adding a source file without a matching Kconfig rule can leave symbols undefined or code unreachable. Removing or renaming entries can break module builds only for specific configurations. The comments require conditional lists to remain alphabetically sorted by Kconfig name; violating that makes maintenance harder and may fail style review.

## Test signals
Run representative `make M=drivers/media/v4l2-core` builds for built-in and modular combinations of VIDEO_DEV, VIDEO_TUNER, V4L2_ASYNC, V4L2_CCI, MEDIA_CONTROLLER, CONFIG_COMPAT, CONFIG_SPI, CONFIG_VIDEO_V4L2_I2C, and CONFIG_TRACEPOINTS. Link errors are the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/tuner-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/tuner-core.c

## Purpose
`tuner-core.c` is the generic I2C analog TV/FM tuner subdevice driver. It presents a single V4L2 subdev driver named `tuner`, autodetects some tuner chips by address/probing, accepts bridge-provided tuner setup, attaches the chip-specific DVB tuner/analog demod implementation, tracks current tuner mode and frequency, and exposes V4L2 tuner operations to bridge drivers.

## Important APIs, types, and functions
The central runtime object is `struct tuner`, which embeds `struct dvb_frontend`, `struct i2c_client *`, `struct v4l2_subdev`, list linkage, current standard/frequencies/audmode/mode, mode mask, standby flag, type/config/name, and optional media pads. Important functions include `tuner_probe()`, `tuner_remove()`, `set_type()`, `tuner_s_type_addr()`, `tuner_s_config()`, `tuner_lookup()`, `set_mode()`, `set_freq()`, `set_tv_freq()`, `set_radio_freq()`, `tuner_fixup_std()`, `tuner_g_frequency()`, `tuner_s_frequency()`, `tuner_g_tuner()`, `tuner_s_tuner()`, `tuner_standby()`, `tuner_suspend()`, and `tuner_resume()`. Operation tables are `tuner_analog_ops`, `tuner_core_ops`, `tuner_tuner_ops`, `tuner_video_ops`, and `tuner_ops`.

## Control flow
Probe allocates `struct tuner`, initializes it as a V4L2 I2C subdev, seeds default radio and TV frequencies, optionally dumps I2C bytes, performs limited autodetection based on I2C address, determines radio/TV mode mask by scanning existing tuners on the same adapter, initializes media entity pads when enabled, selects a default mode, calls `set_type()`, and adds the object to the global `tuner_list`. `set_type()` detaches any previous tuner frontend, switches on the tuner type, attaches the chip-specific module, sets analog callbacks, updates media entity name, stores the mode mask, and often tunes immediately to the stored frequency. V4L2 tuner ops validate the requested mode, update mode/frequency/audmode/std state, and call analog frontend callbacks.

## State and persistence behavior
State is in memory per I2C client. `tv_freq`, `radio_freq`, `std`, `audmode`, `mode`, `mode_mask`, `standby`, `type`, and `config` are retained while the subdevice exists and restored or re-applied on resume. Module parameters (`debug`, `tv_range`, `radio_range`, `pal`, `secam`, `ntsc`, `addr`, `no_autodetect`, `show_i2c`) provide global configuration and compatibility behavior. There is no disk persistence.

## Dependencies and integration points
The file integrates V4L2 subdev APIs, I2C driver core, DVB frontend tuner ops, analog demod ops, media controller entities/pads, and many tuner-specific attach/probe functions (`tda829x`, `tea576x`, `xc2028`, `xc5000`, `tda18271`, `xc4000`, simple tuner, and others). With `CONFIG_MEDIA_ATTACH`, attach symbols are requested dynamically to avoid static links.

## Risks and edge cases
Autodetection is address-based and intentionally heuristic; wrong detection can bind the wrong chip or suppress a radio/TV peer. `set_type()` detaches prior ops before reattaching, so error paths must leave a safe absent state. Frequency units differ between TV and radio, making conversion bugs easy. Global `tuner_list` is not explicitly locked in this file and relies on I2C core serialization during probe plus normal driver call context. Module parameters can force nonstandard video standard variants and should be tested carefully.

## Test signals
Test probing with common tuner addresses, bridge-driven `s_type_addr`, separate radio and TV tuners on one adapter, TDA9887 IF demod special media entity setup, TV/radio frequency range clamping, PAL/SECAM/NTSC fixup parameters, suspend/resume with active and standby tuners, and remove after failed or repeated type setup. `VIDIOC_LOG_STATUS`, `g_frequency`, `s_frequency`, `g_tuner`, and `s_tuner` provide visible behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/tuner-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-async.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-async.c

## Purpose
`v4l2-async.c` implements the V4L2 asynchronous subdevice registration and notifier framework. It lets bridge devices and subdevices describe expected peers by I2C address or firmware node, matches those expectations against asynchronously registered subdevices, invokes bound/unbind/complete callbacks, supports nested notifier trees, and exposes debugfs visibility for pending matches.

## Important APIs, types, and functions
Public APIs include `v4l2_async_nf_init()`, `v4l2_async_subdev_nf_init()`, `v4l2_async_nf_register()`, `v4l2_async_nf_unregister()`, `v4l2_async_nf_cleanup()`, `__v4l2_async_nf_add_fwnode()`, `__v4l2_async_nf_add_fwnode_remote()`, `__v4l2_async_nf_add_i2c()`, `v4l2_async_subdev_endpoint_add()`, `v4l2_async_connection_unique()`, `__v4l2_async_register_subdev()`, and `v4l2_async_unregister_subdev()`. Key internal lists are global `subdev_list` and `notifier_list`, plus per-notifier `waiting_list` and `done_list`, all protected by `list_lock`.

## Control flow
Notifier registration validates each match descriptor for type and global uniqueness, attempts to match all already-registered subdevices, tries nested subdevice notifiers, attempts completion from the root notifier, and finally stores the notifier in the global list. Subdevice registration initializes its async connection list, normalizes its fwnode, scans all notifiers for matches, binds repeatedly while matches exist, triggers nested notifier matching, tries completion, and if unmatched adds the subdevice to `subdev_list`. Binding registers the subdev with the root `v4l2_device` if needed, calls the notifier `bound` callback, creates ancillary media links for lens/flash entities when applicable, links the async connection to the subdev, and moves it from waiting to done.

## State and persistence behavior
All state is in-memory list topology. A notifier's `waiting_list` represents unresolved async connections; `done_list` represents bound connections. `asc->sd`, `sd->asc_list`, `notifier->parent`, and `sd->subdev_notifier` encode binding and nested notifier relationships. Fwnode match descriptors take references and release them during cleanup. Debugfs state is read-only and derived from the live lists.

## Dependencies and integration points
The file integrates V4L2 device/subdev registration, fwnode graph APIs, I2C client matching, media controller ancillary links, subdev privacy LED cleanup, debugfs, and module init/exit. Bridge drivers typically allocate notifier-specific async connection wrappers and use these APIs to wait for sensors, lenses, flashes, codecs, or other media subdevices.

## Risks and edge cases
List mutation during matching is subtle: successful binding can register new notifiers, so matching restarts from the beginning. Completion must walk the root notifier tree and ensure all child notifiers are complete. Error paths need to unbind only the connections introduced by the failing path without corrupting other notifiers. Fwnode endpoint-vs-device matching and secondary fwnodes broaden matching semantics but increase duplicate-match risk. The global mutex is critical; any callback that re-enters async APIs must avoid deadlocks.

## Test signals
Test bridge-first and subdevice-first registration order, I2C and fwnode matches, endpoint endpoint lists, duplicate match rejection, nested notifier completion, bound callback failure, complete callback failure, unregister of bound and unbound subdevices, media ancillary links for lens/flash, debugfs pending output, and fwnode reference cleanup under leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-cci.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-cci.c

## Purpose
`v4l2-cci.c` provides MIPI Camera Control Interface register access helpers on top of regmap. It lets sensor drivers describe register address, width, and endianness through encoded `CCI_REG_*` values and then perform typed reads, writes, masked updates, register sequences, and I2C regmap initialization.

## Important APIs, types, and functions
Exported functions are `cci_read()`, `cci_write()`, `cci_update_bits()`, `cci_multi_reg_write()`, and, when `CONFIG_V4L2_CCI_I2C` is enabled, `devm_cci_regmap_init_i2c()`. They use `struct regmap`, `struct cci_reg_sequence`, `CCI_REG_LE`, `CCI_REG_WIDTH_BYTES()`, and `CCI_REG_ADDR()` from `<media/v4l2-cci.h>`.

## Control flow
`cci_read()` short-circuits if an optional accumulated error pointer is already set, decodes width/endianness/address, bulk-reads up to eight bytes, converts the buffer into a `u64`, and stores errors back through `err`. `cci_write()` mirrors that flow by encoding a `u64` into a byte buffer and bulk-writing it. `cci_update_bits()` reads the current value, applies `(readval & ~mask) | (val & mask)`, and writes it back. `cci_multi_reg_write()` writes each register sequence entry until one fails. The I2C initializer creates an 8-bit-value regmap with big-endian register formatting and disabled regmap locking.

## State and persistence behavior
The helpers do not keep private state. Register values persist only in the target hardware. The optional `int *err` parameter supports caller-side error accumulation across a sequence; once nonzero, later helper calls return that error without issuing more I/O.

## Dependencies and integration points
This file integrates camera sensor drivers with Linux regmap, I2C regmap support, unaligned endian accessors, and device logging. It is built under `CONFIG_V4L2_CCI`, with the I2C initializer gated by `CONFIG_V4L2_CCI_I2C`.

## Risks and edge cases
Unsupported encoded widths return `-EINVAL`; callers must use valid CCI register macros. Disabled regmap locking assumes callers provide any necessary serialization or that sensor register access is otherwise safe. `cci_update_bits()` is read-modify-write and is not atomic at the hardware level. Error accumulation is convenient but can hide later intended operations if callers reuse a stale nonzero error variable.

## Test signals
Unit-style tests can use a fake regmap to verify 1-, 2-, 3-, 4-, and 8-byte reads/writes in both endian modes, invalid width handling, accumulated-error short-circuiting, masked updates, and sequence abort on first error. Hardware tests should confirm sensor probe tables and runtime control updates produce expected bus transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-cci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-common.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-common.c

## Purpose
`v4l2-common.c` contains generic exported V4L2 helper APIs shared by many media drivers. It covers legacy query-control filling, image dimension alignment, nearest-size lookup, subdev frame interval get/set helpers, a large pixel-format information table, single- and multi-planar format filling, media-controller link frequency helpers, active CSI-2 lane discovery, fraction/frame interval conversion, firmware-vs-driver link-frequency bitmap creation, and sensor clock acquisition/fallback.

## Important APIs, types, and functions
Exported helpers include `v4l2_ctrl_query_fill()`, `v4l_bound_align_image()`, `__v4l2_find_nearest_size_conditional()`, `v4l2_g_parm_cap()`, `v4l2_s_parm_cap()`, `v4l2_format_info()`, `v4l2_apply_frmsize_constraints()`, `v4l2_fill_pixfmt_mp()`, `v4l2_fill_pixfmt()`, `v4l2_get_link_freq()`, `v4l2_get_active_data_lanes()`, `v4l2_simplify_fraction()`, `v4l2_fraction_to_interval()`, `v4l2_link_freq_to_bitmap()`, and `__devm_v4l2_sensor_clk_get()`. Internal helpers compute block width/height, plane stride, plane height, and plane size from `struct v4l2_format_info`.

## Control flow
Control fill delegates to `v4l2_ctrl_fill()` and copies the resolved metadata into legacy queryctrl fields. Image alignment clamps dimensions and increases width/height alignment to satisfy combined size alignment. Format lookup linearly scans a static table of RGB, YUV, tiled, multiplanar, Bayer, and raw formats. Pixel-format filling computes bytesperline and sizeimage differently for single-memory-plane and multi-memory-plane formats. Link frequency first asks the subdev pad for `get_mbus_config`, then falls back to `V4L2_CID_LINK_FREQ` or an estimate from pixel rate. Sensor clock acquisition tries `devm_clk_get_optional()`, optional `clock-frequency`, optional rate setting, and finally a dummy fixed-rate clock on supported non-OF or legacy paths.

## State and persistence behavior
Most helpers are stateless. The static format table is read-only. `v4l2_simplify_fraction()` temporarily allocates continued-fraction terms. `__devm_v4l2_sensor_clk_get()` may register a devm-managed fixed clock whose lifetime follows the device. Link-frequency and lane helpers read live subdev control or media bus state but do not store it.

## Dependencies and integration points
The file integrates V4L2 controls, subdev pad operations, media controller pads, videodev2 pixel formats, common clock framework, firmware properties, and device logging. UVC code uses `v4l2_simplify_fraction()` and `v4l2_fraction_to_interval()` for frame interval conversions, and many camera/codec drivers use the format and link helpers.

## Risks and edge cases
The pixel-format table is central: wrong bpp, divisor, plane count, subsampling, or block dimensions will miscompute buffer sizes across drivers. `v4l2_simplify_fraction()` silently returns unchanged values if allocation fails. `v4l2_fraction_to_interval()` saturates on overflow and must handle denominator zero. Link frequency fallback from pixel rate is explicitly approximate and warns once. Sensor clock fallback behavior differs for OF, non-OF, and legacy callers, so dependency changes can alter probe timing.

## Test signals
Test format size calculations for representative RGB, packed YUV, planar, multiplanar, tiled, Bayer, and packed raw formats. Check nearest-size selection with predicates, alignment constraints, frame interval conversions, link-frequency matching against firmware arrays, active lane validation, and sensor clock paths with provided clocks, `clock-frequency`, missing clocks, fixed-rate requests, and deferred probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-common.c -->
