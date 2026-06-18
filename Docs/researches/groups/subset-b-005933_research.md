# Research: subset-b-005933

This grouped report covers the V4L2 media helper headers in `sources/distributed-fs/ceph-client/include/media`. Each section is bounded for reconciliation into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-ctrls.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-ctrls.h

Purpose: declares the in-kernel V4L2 control framework used by drivers, subdevices, video nodes, and request-aware memory-to-memory codecs. It centralizes control value storage, validation, clustering, notifications, event emission, ioctl helpers, and media-request control snapshots.

Important APIs/types: `union v4l2_ctrl_ptr` abstracts scalar, string, array, rectangle, and codec compound payload pointers. `struct v4l2_ctrl_ops` supplies driver callbacks for volatile reads, custom validation, and hardware writes; `struct v4l2_ctrl_type_ops` supplies type-specific equality, initialization, min/max, logging, and validation for compound controls. `struct v4l2_ctrl` is the core object with id, type, min/max/default/step, menu data, flags, cluster pointers, current/new values, array dimensions, dynamic-array allocation metadata, and state bits such as `is_new`, `has_changed`, `is_auto`, `has_volatiles`, and `call_notify`. `struct v4l2_ctrl_ref` links controls into a handler, including request-specific `p_req` values and request validity flags. `struct v4l2_ctrl_handler` owns controls, references, hash buckets, locking, notification callback, request lists, and the embedded `media_request_object`. `struct v4l2_ctrl_config` describes custom control creation.

Creation and setup APIs include `v4l2_ctrl_handler_init()`, `v4l2_ctrl_handler_free()`, `v4l2_ctrl_handler_setup()`, `v4l2_ctrl_new_custom()`, `v4l2_ctrl_new_std()`, `v4l2_ctrl_new_std_menu()`, `v4l2_ctrl_new_std_menu_items()`, `v4l2_ctrl_new_std_compound()`, and `v4l2_ctrl_new_int_menu()`. Composition APIs include `v4l2_ctrl_add_handler()`, `v4l2_ctrl_radio_filter()`, `v4l2_ctrl_cluster()`, and `v4l2_ctrl_auto_cluster()`. Runtime mutation APIs include `v4l2_ctrl_find()`, `v4l2_ctrl_activate()`, `v4l2_ctrl_grab()`, `v4l2_ctrl_modify_range()`, `v4l2_ctrl_modify_dimensions()`, `v4l2_ctrl_notify()`, scalar/string/compound setters, and getter helpers.

Control flow: drivers initialize a handler, add controls, optionally cluster related controls, attach the handler to a video node or subdevice, and call setup to push default/current values to hardware. Userspace ioctl paths call helpers such as `v4l2_queryctrl()`, `v4l2_g_ctrl()`, `v4l2_s_ctrl()`, and extended-control helpers; those helpers find refs, validate values, update new/current storage, run driver callbacks, and emit events. Request-aware devices bind per-request control handler objects, apply queued values with `v4l2_ctrl_request_setup()`, complete volatile snapshots with `v4l2_ctrl_request_complete()`, and release references with `v4l2_ctrl_request_hdl_put()`.

State and persistence: all state is in memory and scoped to the handler/control lifetime. The handler mutex serializes control access; callbacks run under the handler lock. The framework caches lookups in `handler->cached`, stores owned controls in `ctrls`, visible refs in `ctrl_refs` and hash buckets, and request state in `requests` / `requests_queued`. Compound and dynamic-array controls require careful allocation sizing through `p_array_alloc_elems`, `new_elems`, and request-side `p_req_*` fields.

Dependencies and integration: includes Linux list/mutex/videodev2 and `media-request.h`; integrates with `v4l2-fh.h` for per-file control events, `v4l2-fwnode.h` through `v4l2_ctrl_new_fwnode_properties()`, `v4l2-subdev` event/log helpers, video ioctl dispatch, stateless codec compound controls, and media requests.

Risks: deadlocks if drivers call locking helpers from inside `v4l2_ctrl_ops`; stale or undersized compound/dynamic-array storage; inconsistent clusters when auto/manual controls are not set up as the first cluster member; request confusion when dimensions are modified while requests are pending; missing event notification when drivers mutate flags outside framework helpers; and use-after-free if driver `priv` pointers outlive their owner.

Test signals: exercise standard and custom controls, menu skip masks, dynamic arrays, volatile controls, clustered auto/manual controls, request setup/complete, event subscription and merge/replace behavior, query ioctl conversions, fwnode orientation/rotation controls, and lockdep paths through `v4l2_ctrl_handler_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-ctrls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-dev.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-dev.h

Purpose: declares the V4L2 video-device node abstraction, character-device registration helpers, file operations wrapper type, priority helpers, debug flags, and optional media-controller pipeline helpers.

Important APIs/types: `enum vfl_devnode_type` classifies device nodes (`VIDEO`, `VBI`, `RADIO`, `SUBDEV`, `SDR`, `TOUCH`); `enum vfl_devnode_direction` distinguishes RX, TX, and M2M nodes. `enum v4l2_video_device_flags` defines registration, file-handle, inverted-crop compatibility, and read-only subdev-node flags. `struct v4l2_prio_state` tracks priority counts by atomic array. `struct v4l2_file_operations` mirrors the driver-facing file operations (`read`, `write`, `poll`, `unlocked_ioctl`, optional compat ioctl, mmap, open, release). `struct video_device` is the public node object with optional media entity/pipeline, fops, device capabilities, embedded `struct device`, `cdev`, parent `v4l2_device`, control handler, vb2 queue, priority state, name/type/direction/minor/num/index, file-handle list and lock, debug flags, standards, release callback, ioctl ops, valid-ioctl bitmap, and serialization lock.

Control flow: drivers allocate or embed `struct video_device`, fill fops/ioctl ops/capabilities/release/name, optionally disable unsupported ioctls with `v4l2_disable_ioctl()` before registration, then call `video_register_device()` or `video_register_device_no_warn()`. Registration delegates to `__video_register_device()` to allocate minor/node numbers and publish the device. Teardown calls `video_unregister_device()` and then the release callback path. File operations typically retrieve the node with `video_devdata()` and private data with `video_drvdata()`.

State and persistence: node identity, valid ioctl bitmap, flags, file-handle list, and `dev` driver data persist only while the video device is registered and referenced. Priority state can be per-node via `vdev->prio` or inherited from `v4l2_dev->prio`. `video_is_registered()` tests `V4L2_FL_REGISTERED`; unregister clears access for future opens. `video_register_device()` failure does not invoke `release`, so the caller keeps cleanup ownership.

Dependencies and integration: includes Linux poll/fs/device/cdev/mutex/videodev2 and `media-entity.h`. Integrates with `v4l2-device.h` parent objects, `v4l2-ioctl.h` callback tables, `v4l2-fh.h` file-handle lists, vb2 queues, debugfs via `v4l2_debugfs_root()`, and media-controller pipelines through `video_device_pipeline_start/stop/alloc_start/pipeline()` when `CONFIG_MEDIA_CONTROLLER` is enabled.

Risks: registering a non-zeroed `video_device` can leave stale fields; disabling ioctls after registration is too late; missing `release` leaks dynamically allocated devices; using static `video_device` with normal release is unsafe; invalid `vdev->fops->owner` can break module lifetime; and media pipeline helpers assume a single pad and balanced start/stop nesting.

Test signals: register/unregister every `vfl_devnode_type`, exercise requested and auto-assigned node numbers, verify valid-ioctl masking, priority open/change/check/close, file-handle list behavior, debug flags, `video_drvdata()` retrieval, media pipeline nesting, and failure cleanup when registration returns an error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-device.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-device.h

Purpose: declares the parent `v4l2_device` object that groups video nodes and subdevices, owns device-level control/priority state, and provides subdevice registration, notification, request capability checks, and bulk subdevice operation fanout macros.

Important APIs/types: `struct v4l2_device` contains parent `struct device`, optional `media_device`, `subdevs` list, spinlock, unique name, driver notification callback, device-level control handler, priority state, kref, and release callback. Lifecycle APIs include `v4l2_device_register()`, `v4l2_device_set_name()`, `v4l2_device_disconnect()`, `v4l2_device_unregister()`, `v4l2_device_get()`, and `v4l2_device_put()`. Subdevice APIs include `v4l2_device_register_subdev()`, `__v4l2_device_register_subdev()`, `v4l2_device_unregister_subdev()`, and subdev-node registration helpers for full or read-only userspace access.

Control flow: a bridge driver registers the `v4l2_device`, then registers subdevices so the core links them into `subdevs` and pins their modules. Drivers can expose subdev device nodes when `CONFIG_VIDEO_V4L2_SUBDEV_API` is enabled. Notifications go from a subdevice to the bridge through `v4l2_subdev_notify()`. Bridge-wide operations use macros such as `v4l2_device_call_all()`, `v4l2_device_call_until_err()`, mask variants, and `v4l2_device_has_op()` to iterate the subdevice list and dispatch a selected ops group member.

State and persistence: the parent object keeps the authoritative subdevice list and refcount. `v4l2_device_disconnect()` sets `dev` to NULL for hot-unplug safety. Fanout macros assume subdevices cannot be added or removed during iteration. `v4l2_device_supports_requests()` is derived from an attached media device with `mdev->ops->req_queue`.

Dependencies and integration: includes `media-device.h`, `v4l2-subdev.h`, and `v4l2-dev.h`. It binds the media controller, V4L2 subdevice API, video-device nodes, control handlers, priority handling, and media requests.

Risks: concurrent subdevice list mutation during macro iteration; ignoring `-ENOIOCTLCMD` behavior in until-error macros; stale parent pointers after USB disconnect if `v4l2_device_disconnect()` is missed; module lifetime bugs when subdev registration fails; and request support being advertised only when the media device ops are fully initialized.

Test signals: parent registration with and without a real parent `struct device`, name instance generation, subdev register/unregister idempotence, full and read-only subdev-node registration under config gates, notification callback delivery, group-id and mask fanout filtering, error propagation for until-error macros, and request support detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-dv-timings.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-dv-timings.h

Purpose: declares helper APIs for digital-video timing calculation, validation, enumeration, matching, CVT/GTF detection, EDID physical-address handling, HDMI colorimetry, and optional debugfs HDMI InfoFrame export.

Important APIs/types: `v4l2_calc_timeperframe()` derives frame period from pixel clock and blanking totals. `v4l2_dv_timings_presets[]` is the preset timing database. `v4l2_check_dv_timings_fnc` lets drivers add hardware-specific validation. `v4l2_valid_dv_timings()`, `v4l2_enum_dv_timings_cap()`, `v4l2_find_dv_timings_cap()`, `v4l2_find_dv_timings_cea861_vic()`, and `v4l2_match_dv_timings()` validate and normalize modes. `v4l2_detect_cvt()` and `v4l2_detect_gtf()` infer standard timings from measured sync values. `struct v4l2_hdmi_colorimetry` and `v4l2_hdmi_rx_colorimetry()` translate HDMI infoframes into V4L2 colorspace fields.

Control flow: HDMI/receiver drivers measure a mode or parse EDID, call validation/enumeration against `v4l2_dv_timings_cap`, optionally pass a driver callback, and expose results through DV-timings ioctls. Detection helpers map raw sync/frequency observations to CVT/GTF timing structures. EDID helpers count blocks and read/write/validate CEC physical addresses.

State and persistence: helpers are mostly stateless. Persistent data is caller-owned `v4l2_dv_timings`, EDID buffers, and optional `struct v4l2_debugfs_if` allocated by `v4l2_debugfs_if_alloc()` when debugfs is enabled. `can_reduce_fps()` is an inline predicate based on BT timing standards, vsync, and reduced-FPS flags.

Dependencies and integration: includes debugfs and videodev2; integrates with `v4l2-ioctl.h` DV timing callbacks, HDMI infoframe structures, CEC physical addressing, and debugfs. The debugfs allocation/free APIs become NULL/no-op stubs without `CONFIG_DEBUG_FS`.

Risks: invalid or partially filled timing structs produce wrong frame periods; too-wide `pclock_delta` can match the wrong mode; relying on reduced-FPS matching inconsistently can accept incompatible timings; EDID mutation must respect buffer size and checksum expectations in implementation; and debugfs readers must bound output to `V4L2_DEBUGFS_IF_MAX_LEN`.

Test signals: enumerate supported presets across caps, match measured timings with pclock tolerance, CVT/GTF detection for interlaced and reduced-blanking modes, CEA-861 VIC lookup, aspect-ratio calculation from EDID bytes and timings, EDID physical-address validation for parent/port extraction, and debugfs allocation under enabled/disabled config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-dv-timings.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-event.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-event.h

Purpose: declares the V4L2 event framework for per-filehandle subscriptions, queued kernel events, event dequeue, event wakeups, and helper subscription filters for source-change and subdevice events.

Important APIs/types: `struct v4l2_kevent` wraps a userspace `v4l2_event`, timestamp, list node, and parent subscription. `struct v4l2_subscribed_event_ops` allows event classes to run add/delete hooks and replace or merge queued events. `struct v4l2_subscribed_event` records type/id/flags, owning `v4l2_fh`, object linkage, ring-buffer indices (`elems`, `first`, `in_use`), and a flexible array of queued events.

Control flow: a driver or helper subscribes with `v4l2_event_subscribe()` or a specialized helper, queues events globally with `v4l2_event_queue()` or to one file handle with `v4l2_event_queue_fh()`, userspace dequeues through `v4l2_event_dequeue()`, and unregister paths wake blocked file handles with `v4l2_event_wake_all()`. Unsubscribe paths remove one or all subscriptions and call delete hooks.

State and persistence: event state lives in each `v4l2_fh`: subscribed list, available list, wait queue, `navailable`, and sequence counter. Subscription ring buffers may replace or merge events to cap queue length. There is no durable persistence beyond open file lifetime.

Dependencies and integration: includes videodev2 and wait queues, and forward-depends on `v4l2_fh`, `video_device`, and `v4l2_subdev`. Control events integrate with `v4l2-ctrls.h` through `v4l2_ctrl_sub_ev_ops`; source-change helpers integrate with decoder/input drivers and subdevice core ops.

Risks: incorrect `elems` sizing causes lost events; add/delete callbacks must be serialized by the filehandle subscription lock; event data fields are driver-owned while sequence/timestamp/pending are core-owned; and unregister must wake waiters to avoid blocked readers.

Test signals: subscribe/unsubscribe one and all events, queue to all file handles and one file handle, dequeue blocking and nonblocking, verify sequence/pending values, exercise replace/merge callbacks with a one-entry queue, source-change filters, and subdevice unsubscribe helper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-fh.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-fh.h

Purpose: declares the mandatory V4L2 per-open filehandle object that connects a `struct file` to a `video_device`, control handler, priority state, event queues, and optional mem2mem context.

Important APIs/types: `struct v4l2_fh` stores list linkage into `video_device->fh_list`, `vdev`, per-file `ctrl_handler`, priority, event wait queue, subscription mutex, subscribed and available event lists, available count, event sequence, and `m2m_ctx`. `file_to_v4l2_fh()` returns `file->private_data` as a `v4l2_fh`.

Control flow: drivers call `v4l2_fh_init()` in open, then `v4l2_fh_add()` to link the handle and set `file->private_data`. Simple drivers can use `v4l2_fh_open()` as the open operation. Release paths call `v4l2_fh_del()` to unlink/reset private data, then `v4l2_fh_exit()` to release framework resources; `v4l2_fh_release()` bundles delete/exit/free for simple drivers. `v4l2_fh_is_singular()` checks whether this is the only open handle for exclusive operations.

State and persistence: all state is per open file and is torn down on release. Event subscriptions and queued events are stored here; the optional mem2mem context links queue/scheduler state to this open. `v4l2_fh_init()` also sets the `V4L2_FL_USES_V4L2_FH` flag on the video device per the device header contract.

Dependencies and integration: includes fs, list, kconfig, and videodev2. It integrates with `v4l2-dev.h` file-handle lists, `v4l2-event.h` queues, `v4l2-ctrls.h` per-file control handlers, priority helpers, and `v4l2-mem2mem.h` contexts.

Risks: bypassing `v4l2_fh_add()` leaves `file->private_data` unset; failing to call `v4l2_fh_exit()` leaks event subscriptions; accessing `file->private_data` directly can hide non-V4L2 private layouts; singular checks are only meaningful while the fh list is correctly maintained.

Test signals: open/release using helper and custom paths, private-data reset on delete, event subscription cleanup on exit, singular detection with one and multiple opens, priority propagation, and mem2mem context association.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-fh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-flash-led-class.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-flash-led-class.h

Purpose: declares helpers that wrap Linux LED flash/indicator class devices as V4L2 subdevices with V4L2 controls and media-entity naming.

Important APIs/types: `struct v4l2_flash_ctrl_data` pairs a `v4l2_ctrl_config` with the created control id. `struct v4l2_flash_ops` lets drivers configure external strobe and convert between V4L2 intensity units and LED brightness. `struct v4l2_flash_config` provides media entity name, intensity constraints, supported LED fault bitmask, and external-strobe capability. `struct v4l2_flash` stores LED class-device pointers, ops, embedded subdevice, control handler, and control pointer array. Inline container helpers convert from subdev or control to `v4l2_flash`.

Control flow: LED-backed camera drivers call `v4l2_flash_init()` for flash LEDs or `v4l2_flash_indicator_init()` for indicator LEDs. The framework builds controls from LED capabilities, initializes an embedded subdevice and control handler, and later `v4l2_flash_release()` tears it down. When `CONFIG_V4L2_FLASH_LED_CLASS` is disabled, init functions return NULL and release is a no-op.

State and persistence: flash state is in the allocated `v4l2_flash`, its control handler, and LED class device. The config is not retained after init returns, while `ops` is stored. Control values define the V4L2-visible flash state; LED subsystem state is the hardware-facing backend.

Dependencies and integration: includes `v4l2-ctrls.h` and `v4l2-subdev.h`, and depends on LED flash class types. It bridges media-controller subdevices, V4L2 controls, firmware node association, LED faults, torch/flash intensity, and external strobe wiring.

Risks: callers must handle NULL when the config option is disabled; config lifetime cannot be assumed after init; conversion callbacks must be monotonic and respect LED constraints; unsupported fault bits can mislead userspace; and control-to-flash container conversion assumes controls belong to `v4l2_flash.hdl`.

Test signals: init/release with flash and indicator devices, disabled-config stubs, external strobe enable/disable, intensity/brightness round trips, fault reporting controls, fwnode association, and control handler cleanup on init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-flash-led-class.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-fwnode.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-fwnode.h

Purpose: declares firmware-node parsing helpers for V4L2 endpoints, media bus configuration, connector descriptions, endpoint links, and camera device properties such as orientation and rotation.

Important APIs/types: `struct v4l2_fwnode_endpoint` combines a generic `fwnode_endpoint`, `enum v4l2_mbus_type`, bus-specific parallel/CSI-1/CSI-2 config, and optional link-frequency array. `V4L2_FWNODE_PROPERTY_UNSET` marks absent properties. `enum v4l2_fwnode_orientation` and `struct v4l2_fwnode_device_properties` describe camera placement and rotation. `struct v4l2_fwnode_link` holds local/remote endpoint nodes and port/id numbers. Connector types and structures model analog composite/S-video connectors and their links.

Control flow: drivers zero or initialize endpoint structs, call `v4l2_fwnode_endpoint_parse()` for fixed-size properties or `v4l2_fwnode_endpoint_alloc_parse()` when `link-frequencies` are needed, validate returned bus type, then call `v4l2_fwnode_endpoint_free()` for allocated fields. Link parsers take fwnode references and require `v4l2_fwnode_put_link()`. Connector parse/add-link paths allocate labels/link nodes and require `v4l2_fwnode_connector_free()`. Device properties are parsed with `v4l2_fwnode_device_parse()`.

State and persistence: parsed data is caller-owned. Alloc-parse can allocate `link_frequencies`; connector parsing can allocate labels and link entries; link parsing takes references to local and remote nodes. Helpers guarantee endpoint state is not changed on parse failure.

Dependencies and integration: includes Linux fwnode/list/types/errno and `v4l2-mediabus.h`. It feeds async subdevice binding, media graph creation, bus configuration, camera sensor orientation controls through `v4l2_ctrl_new_fwnode_properties()`, and connector-aware analog video pipelines.

Risks: new bindings must not rely on deprecated bus-type guessing; callers must initialize structs before parsing and free allocated resources; mismatched explicit bus type returns `-ENXIO`; NULL fwnode can return `-EPROBE_DEFER`; and missing reference cleanup leaks fwnode handles.

Test signals: parse parallel, BT.656, CSI-1/CCP2, CSI-2 D-PHY and C-PHY endpoints; verify explicit bus mismatch; parse/free link frequencies; parse connector labels and multiple links; check first/last link macros; validate orientation/rotation property ranges; and confirm no state mutation on failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-fwnode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-h264.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-h264.h

Purpose: declares H.264 reference-list construction helpers for stateless decoder drivers that need spec-ordered P, B0, and B1 reference arrays for hardware programming.

Important APIs/types: `struct v4l2_h264_reflist_builder` stores per-DPB-entry top/bottom field order counts, frame number, long-term flag, current picture order count, current picture fields, an unordered `v4l2_h264_reference` list, and `num_valid`. APIs are `v4l2_h264_init_reflist_builder()`, `v4l2_h264_build_b_ref_lists()`, and `v4l2_h264_build_p_ref_list()`.

Control flow: a stateless H.264 driver receives decode params, SPS, and DPB entries from V4L2 controls, initializes the builder, then builds P or B reference lists depending on slice type before submitting hardware commands. The helper implements H.264 specification section 8.2.4 reference picture list construction.

State and persistence: the builder is caller-allocated transient decode state. It does not persist references beyond the arrays passed in; output lists are caller-provided 32-entry reference arrays.

Dependencies and integration: includes `v4l2-ctrls.h` for H.264 compound control types and constants. It integrates with stateless codec controls and mem2mem request decoding.

Risks: invalid DPB entries or mismatched SPS/decode params produce wrong list ordering; field-coded pictures require correct `cur_pic_fields`; long-term references need distinct ordering; and hardware expecting pre-modified slice reference lists may need driver-side adjustments after helper output.

Test signals: P-list and B0/B1-list construction with short-term and long-term references, frame and field pictures, empty/partial DPB, duplicate POC ordering edge cases, and conformance vectors comparing helper output to spec examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-h264.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-image-sizes.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-image-sizes.h

Purpose: provides common image dimension macros for standard frame sizes used by V4L2 drivers and format tables.

Important APIs/types: defines width/height pairs for CIF, HD 720, HD 1080, QCIF, QQCIF, QQVGA, QVGA, SVGA, SXGA, VGA, UXGA, and XGA. There are no functions or stateful structures.

Control flow: drivers include this header and use the constants in frame-size enumeration, default format setup, bounds checking, or sensor mode tables.

State and persistence: stateless preprocessor constants only.

Dependencies and integration: no external includes beyond the guard. Integrates indirectly with format enumeration helpers and driver mode definitions.

Risks: constants are conventional sizes, not capability declarations; use in drivers without checking actual hardware mode tables can advertise unsupported resolutions. `SXGA_WIDTH` equals `HD_720_WIDTH` but has different height, so name-based assumptions can be misleading.

Test signals: compile-time use in mode tables, frame-size enumeration matching hardware modes, default format initialization, and documentation/tests that distinguish similarly wide formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-image-sizes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-ioctl.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-ioctl.h

Purpose: declares the V4L2 ioctl dispatch contract, driver callback vtable, debug flags, analog-standard helpers, compat translation helpers, and core `video_ioctl2()` / `video_usercopy()` entry points.

Important APIs/types: `struct v4l2_ioctl_ops` is the central callback table for capabilities, format enum/get/set/try across video/VBI/SDR/meta and single/multiplane paths, buffer operations, streaming, standards, input/output, controls, audio, tuner, selection/crop, JPEG compression, encoder/decoder commands, stream parameters, sliced VBI, log status, hardware seek, advanced debug, frame sizes/intervals, DV timings, EDID, event subscribe/unsubscribe, and private default ioctls. Debug flags include `V4L2_DEV_DEBUG_IOCTL`, `_ARG`, `_FOP`, `_STREAMING`, `_POLL`, and `_CTRL`.

Control flow: driver file operations normally point `unlocked_ioctl` at `video_ioctl2()`. The core copies ioctl payloads through `video_usercopy()`, maps commands to typed callbacks in `v4l2_ioctl_ops`, applies core checks such as priority and valid-ioctl filtering, and lets `vidioc_default` handle private commands. Compat paths translate 32-bit userspace commands and arrays through `v4l2_compat_*` helpers.

State and persistence: this header defines dispatch contracts, not long-lived objects. Runtime state lives in `video_device` (`ioctl_ops`, `valid_ioctls`, `dev_debug`, locks), filehandles, controls, queues, and user buffers. `v4l2_event_time32` and `v4l2_buffer_time32` preserve old 32-bit time ABI layouts.

Dependencies and integration: includes poll/fs/mutex/sched signal/compiler/videodev2. Integrates with `v4l2-dev.h`, `v4l2-fh.h`, control helpers, mem2mem ioctl helpers, vb2 queues, DV timing helpers, events, and compat syscall support.

Risks: callback tables with missing try/set pairs can expose inconsistent behavior; incorrect command translation can corrupt compat ABI; drivers must not trust userspace pointers after usercopy; private ioctls need priority validation via `valid_prio`; and legacy time32 structs must remain ABI-compatible.

Test signals: ioctl coverage for every populated callback, invalid ioctl masking, priority-denied mutations, 32-bit compat query/qbuf/dqbuf/event paths, debug logging flags, private ioctl fallback, standard enumeration helpers, and fuzzing of usercopy sizes and array arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-isp.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-isp.h

Purpose: declares generic V4L2 ISP parameter/statistics validation helpers for extensible ISP parameter buffers.

Important APIs/types: `v4l2_isp_params_buffer_size(max_params_size)` computes the size of `struct v4l2_isp_params_buffer` plus a variable data payload. `v4l2_isp_params_validate_buffer_size()` validates a vb2 buffer size against a maximum and the minimum needed for at least one ISP configuration block. `struct v4l2_isp_params_block_type_info` stores expected size per block type. `v4l2_isp_params_validate_buffer()` validates copied parameter-buffer content against supported block type information.

Control flow: ISP drivers validate the vb2 buffer in `.buf_prepare()` or equivalent, copy userspace-provided content into kernel-only memory to avoid post-submit modification, then validate block layout/type/size using the per-type table before programming hardware.

State and persistence: no framework-owned persistent state. The driver owns the vb2 buffer, copied parameter buffer, max size, and type-info table.

Dependencies and integration: includes UAPI `linux/media/v4l2-isp.h` plus forward declarations for `device` and `vb2_buffer`. Integrates with videobuf2 parameter queues and ISP drivers consuming extensible block payloads.

Risks: using the payload before copying from userspace can race with modification; wrong `max_size` or type-size table can accept truncated or oversized blocks; block type indexes must match the UAPI enum; and integer overflow in caller-provided max sizes would affect buffer-size calculations if not bounded by implementation.

Test signals: validate minimum buffer size, max-size rejection, malformed block length, unknown block type, per-type expected-size mismatch, multiple blocks, zero blocks, and user-modification prevention by validating the kernel copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-isp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-jpeg.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-jpeg.h

Purpose: declares JPEG marker/header parsing structures, constants, reference Huffman/quantization tables, and `v4l2_jpeg_parse_header()` for JPEG codec drivers.

Important APIs/types: constants define component/table limits, Huffman table prefixes, reference table lengths, and 8x8 block size. `struct v4l2_jpeg_reference` points into the input buffer with start and length. Frame and scan component structs model ITU-T.81 SOF/SOS syntax. `enum v4l2_jpeg_app14_tf` records Adobe APP14 transform interpretation. `struct v4l2_jpeg_header` aggregates SOF/SOS references, DHT/DQT references and counts, parsed frame header, optional scan/quantization/Huffman output pointers, restart interval, entropy-coded segment offset, and APP14 transform flag.

Control flow: a JPEG driver initializes optional pointers in `v4l2_jpeg_header`, calls `v4l2_jpeg_parse_header(buf, len, out)`, then uses parsed dimensions, component sampling, quantization/Huffman table references, restart interval, and entropy offset to program decoder hardware. Default reference tables are available for hardware or streams that need standard tables.

State and persistence: parsed references point into the caller's buffer, so the buffer must outlive hardware setup using those references. Optional output arrays are caller-provided. No heap ownership is declared in the header.

Dependencies and integration: includes `linux/v4l2-controls.h` for JPEG chroma subsampling enum. It integrates with stateless/stateful JPEG mem2mem drivers and V4L2 JPEG controls.

Risks: references are not deep copies; malformed marker lengths can cause parser rejection and must not be bypassed; APP14 absence is represented as `V4L2_JPEG_APP14_TF_UNKNOWN`; four-component CMYK/YCCK streams need transform-aware handling; and drivers must account for missing optional scan/table storage.

Test signals: parse baseline JPEGs with one/three/four components, multiple DHT/DQT tables, restart interval, APP14 transform variants, missing optional arrays, malformed marker lengths, truncated entropy segment, and compare reference table constants against ITU-T.81 defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-jpeg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-mc.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-mc.h

Purpose: declares V4L2/media-controller integration helpers for graph creation, exclusive media-source ownership, firmware-node link creation, and deprecated pipeline power-management helpers.

Important APIs/types: with `CONFIG_MEDIA_CONTROLLER`, APIs include `v4l2_mc_create_media_graph()`, `v4l_enable_media_source()`, `v4l_disable_media_source()`, `v4l_vb2q_enable_media_source()`, `v4l2_create_fwnode_links_to_pad()`, `v4l2_create_fwnode_links()`, `v4l2_pipeline_pm_get()`, `v4l2_pipeline_pm_put()`, and `v4l2_pipeline_link_notify()`. Without media-controller support, no-op stubs are provided for graph/source/pipeline-PM helpers, but not for the fwnode link creation helpers.

Control flow: bridge drivers can create generic PC-consumer media graphs, V4L2/DVB core paths can enable/disable a shared media source before source-changing operations, and async notifier bound callbacks can translate firmware endpoint connections into media links. Deprecated pipeline PM helpers update entity use counts around opens/releases and link changes.

State and persistence: persistent state lives in `media_device`, `media_entity`, media links, source-enable callbacks, and vb2 queues. The helper declarations do not own state directly.

Dependencies and integration: includes `media-device.h`, `v4l2-dev.h`, `v4l2-subdev.h`, and Linux types. It integrates V4L2 video nodes, subdevices, firmware endpoint parsing, media graph links, and vb2 queues.

Risks: `v4l2_mc_create_media_graph()` is intentionally too simple for subdev-centric camera pipelines; enabled link flags can be invalid if multiple fwnode links are created; sink subdevices must implement `.get_fwnode_pad`; deprecated pipeline PM should not be used in new drivers; and the lack of disabled-config stubs for fwnode link helpers means call sites must be config-gated or rely on media-controller builds.

Test signals: graph creation for tuner/decoder/video entities, exclusive source enable conflicts, vb2 queue to video-device lookup, fwnode link creation to a pad and to a sink subdev, multiple-link flag validation, disabled-config stub compilation, and deprecated PM get/put/link-notify balance in legacy drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-mediabus.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-mediabus.h

Purpose: declares V4L2 media-bus configuration flags, bus-specific config structs, bus type enum, and inline format conversion helpers between media-bus frame formats and pixel formats.

Important APIs/types: parallel flags describe master/slave mode, sync polarities, pixel clock edge, data polarity, field polarity, sync-on-green, and data-enable polarity. CSI-2 flags include non-continuous clock and max data lanes. `enum v4l2_mbus_csi2_cphy_line_orders_type` describes C-PHY lane wire ordering. Bus config structs cover CSI-2 lanes/polarities/line order, parallel bus width/shift, and CSI-1/CCP2 clock/strobe/lane polarity. `enum v4l2_mbus_type` enumerates unknown, parallel, BT.656, CSI-1, CCP2, CSI-2 D-PHY, CSI-2 C-PHY, DPI, and invalid. `struct v4l2_mbus_config` pairs type, link frequency, and a bus-specific union.

Control flow: subdevices report bus configuration through pad operations; bridge drivers interpret exactly one value from each mutually exclusive flag group. Format helpers copy width/height/field/colorspace/ycbcr/quantization/xfer fields between `v4l2_mbus_framefmt` and single- or multi-plane pixel formats, adding a media-bus code when converting to mbus.

State and persistence: all structures are caller-owned configuration snapshots. Inline conversion helpers mutate only the destination format struct.

Dependencies and integration: includes UAPI `linux/v4l2-mediabus.h` and bitops. It is consumed by `v4l2-fwnode.h`, subdevice pad operations, sensor/receiver bridge drivers, and format negotiation paths.

Risks: flags can encode conflicting states because mutually exclusive choices are separate bits; TODO notes a future field-based replacement. Drivers must validate one-and-only-one choice per group. Lane arrays must honor `num_data_lanes` and the maximum of 8. Format helpers intentionally do not fill stride, image size, plane layout, or pixel format, so drivers must complete those fields.

Test signals: validate conflicting flag rejection in drivers, parse/report every bus type, CSI-2 lane and polarity mapping, C-PHY line order handling, link frequency propagation, and format conversion preserving colorimetry fields while drivers fill missing pixel-layout fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-mediabus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-mem2mem.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-mem2mem.h

Purpose: declares the V4L2 memory-to-memory framework for drivers with both source/output and destination/capture buffers, including job scheduling, per-open contexts, two vb2 queues, drain/stop state, media-controller registration, request handling, ioctl helpers, mmap, and poll.

Important APIs/types: `struct v4l2_m2m_ops` provides required `device_run` plus optional `job_ready` and `job_abort`. `struct v4l2_m2m_queue_ctx` wraps a vb2 queue, ready-buffer list, spinlock, ready count, and buffered-queue flag. `struct v4l2_m2m_ctx` is per filehandle and stores queue lock, new-frame flag, drain state (`is_draining`, `last_src_buf`, `next_buf_last`, `has_stopped`), capture-streaming override, owning `m2m_dev`, capture/output queue contexts, scheduler list node, job flags, finish waitqueue, and driver private pointer. `struct v4l2_m2m_buffer` embeds a `vb2_v4l2_buffer` with ready-list linkage.

Control flow: drivers call `v4l2_m2m_init()` at probe and `v4l2_m2m_ctx_init()` at open with a queue-init callback. vb2 `buf_queue` calls `v4l2_m2m_buf_queue()`, which adds buffers to ready lists and scheduling can proceed through `v4l2_m2m_try_schedule()`. The framework checks streaming, source/destination readiness, buffered queues, and optional `job_ready`, then invokes `device_run()`. Drivers finish work with `v4l2_m2m_job_finish()` or `v4l2_m2m_buf_done_and_job_finish()` for held capture buffers. Release paths call `v4l2_m2m_ctx_release()` and `v4l2_m2m_release()` or reference-counted `get/put()`.

Runtime APIs multiplex vb2 operations by buffer type: reqbufs, querybuf, qbuf, dqbuf, prepare, create, export, streamon/off, encoder/decoder commands, poll, mmap, and no-MMU area lookup. Ready-list helpers count, peek, iterate, remove first/last/exact/indexed buffers and copy metadata from output to capture. Request-aware drivers use `v4l2_m2m_request_queue()`.

State and persistence: per-open contexts persist until file release; per-driver `m2m_dev` serializes hardware access across contexts. Ready queues are protected by spinlocks; job completion uses wait queues and internal flags. Drain state tracks end-of-stream and LAST-buffer behavior, and suspend/resume pauses scheduling around power management.

Dependencies and integration: includes `videobuf2-v4l2.h`; integrates with `v4l2-fh` through `fh->m2m_ctx`, `v4l2-ioctl.h` helper callbacks, media requests, media-controller entity registration, vb2 queues, encoder/decoder command ioctls, and file ops for mmap/poll.

Risks: failing to call job finish stalls all queued contexts; wrong `job_ready` can run hardware without enough buffers or sleep in an atomic scheduling path; held capture buffers require `v4l2_m2m_buf_done_and_job_finish()`; drain flags must be reset on streamoff/start; ready-list manipulation must use the framework locks; shared hardware requires correct `get/put()` refcounting; and mmap offset translation must remain consistent for both queues.

Test signals: multi-instance scheduling fairness, source/destination queue readiness, buffered queue behavior, job abort and suspend/resume, drain/last-buffer transitions, held capture buffer slices, every ioctl helper, request queue integration, metadata copy, ready-list removal by buffer and index, poll read/write readiness, and media-controller registration under enabled/disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-mem2mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-rect.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-rect.h

Purpose: provides inline geometry helpers for `struct v4l2_rect` sizing, containment, equality, intersection, scaling, overlap, and enclosure checks.

Important APIs/types: helpers include `v4l2_rect_set_size_to()`, `v4l2_rect_set_min_size()`, `v4l2_rect_set_max_size()`, `v4l2_rect_map_inside()`, `v4l2_rect_same_size()`, `v4l2_rect_same_position()`, `v4l2_rect_equal()`, `v4l2_rect_intersect()`, `v4l2_rect_scale()`, `v4l2_rect_overlap()`, and `v4l2_rect_enclosed()`.

Control flow: selection/crop/compose code clamps requested rectangles to bounds, compares old/new rectangles, computes intersections for visible regions, scales rectangles between source and destination coordinate spaces, and checks overlap/enclosure before accepting formats or selections.

State and persistence: stateless inline functions mutate only caller-provided rectangle arguments. No allocation or persistent framework state.

Dependencies and integration: includes videodev2 for `struct v4l2_rect`; uses kernel `min/max` helpers. Integrates with selection APIs in ioctl/subdevice paths and any driver crop/compose implementation.

Risks: coordinate addition can overflow for extreme signed values; `v4l2_rect_scale()` rounds horizontal left/width down to even values, which is correct for many video formats but can surprise generic geometry users; zero source width/height clears the rectangle; `v4l2_rect_enclosed()` takes non-const pointers even though it does not mutate them.

Test signals: clamp below min and above max, map rectangles partially and fully outside boundaries, equality and position-only comparisons, non-overlap on touching edges, intersection with empty result, scaling with zero source dimensions, even horizontal rounding, and enclosure at exact boundary edges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-rect.h -->
