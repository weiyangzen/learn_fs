# subset-b-004225 research

Grouped research report for V4L2 core sources under `sources/distributed-fs/ceph-client/drivers/media/v4l2-core`. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-device.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-device.c

## Purpose
`v4l2-device.c` implements the core `struct v4l2_device` lifecycle and the registration lifecycle for `struct v4l2_subdev` objects attached to a V4L2 device. It is the central glue between a physical Linux `struct device`, V4L2 priority handling, subdevice lists, optional media-controller entities, and subdevice character nodes.

## Important APIs, Types, and Functions
The exported device APIs are `v4l2_device_register`, `v4l2_device_put`, `v4l2_device_set_name`, `v4l2_device_disconnect`, and `v4l2_device_unregister`. The subdevice APIs are `__v4l2_device_register_subdev`, `__v4l2_device_register_subdev_nodes`, and `v4l2_device_unregister_subdev`. Important state lives in `struct v4l2_device`: `subdevs`, `lock`, `prio`, `ref`, `dev`, `name`, `ctrl_handler`, optional `mdev`, and optional `release`. Important subdevice state includes `sd->v4l2_dev`, `sd->owner`, `sd->owner_v4l2_dev`, `sd->list`, `sd->entity`, `sd->devnode`, and `sd->internal_ops`.

## Control Flow
`v4l2_device_register` initializes the subdevice list, spinlock, priority state, and reference counter, takes a reference on the parent device with `get_device`, stores `dev`, and derives a device name if one was not already supplied. It also installs the V4L2 device as driver data if the parent has no driver data yet. `v4l2_device_disconnect` reverses only the parent-device association: it clears driver data if it points at this V4L2 device, drops the device reference, and nulls `v4l2_dev->dev`. `v4l2_device_unregister` is the full teardown path: it disconnects, iterates the subdevice list safely, unregisters each subdevice, asks I2C/SPI helpers to remove bus-created subdevices when flagged, and clears `name[0]` to make duplicate unregisters no-ops.

`__v4l2_device_register_subdev` validates inputs, handles module ownership, attaches the subdevice to the V4L2 device, merges the subdevice control handler into the device handler, registers a media entity when a media device is present, calls the subdevice `registered` internal op, and appends the subdevice to `v4l2_dev->subdevs` under `v4l2_dev->lock`. Failure unwinds media entity registration, module references, and `sd->v4l2_dev`. `__v4l2_device_register_subdev_nodes` walks registered subdevices with `V4L2_SUBDEV_FL_HAS_DEVNODE`, allocates a `video_device`, wires it to `v4l2_subdev_fops`, registers it as `VFL_TYPE_SUBDEV`, and creates an immutable media interface link when media-controller support is enabled. `v4l2_device_unregister_subdev` removes the subdevice from the list, calls `unregistered`, unregisters media entities and devnodes, or directly releases the subdevice when no node owns the release.

## State and Persistence Behavior
The file manages in-kernel object state only; there is no on-disk persistence. Persistent-looking state is lifetime and ownership state: parent device references, module use counts, media-controller entity registration, video minor allocation, `sd->devnode`, and list membership. The `v4l2_device` reference counter calls an optional driver `release` callback when the last reference is dropped. `name[0] == '\0'` is used as an idempotence marker after unregister.

## Dependencies and Integration Points
This code integrates with the device core (`get_device`, `put_device`, driver data), module reference counting, `v4l2-ctrls`, V4L2 priority helpers, `video_device` registration, subdevice fops, I2C/SPI subdevice unregister helpers, and media-controller entity/interface link APIs under `CONFIG_MEDIA_CONTROLLER`. It is called by bridge drivers and bus helpers when assembling a V4L2 graph.

## Risks
The main risks are lifetime and unwind bugs: missing module puts, double unregisters, stale `sd->v4l2_dev`, leaked media entities, or leaked `video_device` nodes. Subdevice list operations depend on `v4l2_dev->lock`, while callbacks can have driver-specific side effects. Registering subdev nodes partially can fail, and cleanup assumes registered nodes appear first in list order until the first subdevice with no `devnode`. Drivers must not pass unnamed subdevices or subdevices already bound to another V4L2 device.

## Test Signals
Useful tests are bridge-driver probe/remove cycles, subdevice registration failure injection at control merge, media entity registration, internal `registered`, and video node registration. Runtime signals include no leaked module references after remove, correct `/dev/v4l-subdev*` node creation for `HAS_DEVNODE`, idempotent `v4l2_device_unregister`, correct media graph links, and KASAN/KCSAN/lockdep clean teardown under hot-unplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-dv-timings.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-dv-timings.c

## Purpose
`v4l2-dv-timings.c` provides helpers for digital video timings, EDID-derived information, HDMI colorimetry, CEC physical-address handling, and optional debugfs InfoFrame exposure. It contains a large table of standard CEA and DMT timing presets and algorithms for validating, matching, deriving, printing, and detecting timing modes.

## Important APIs, Types, and Functions
Key exported data is `v4l2_dv_timings_presets`. Timing helpers include `v4l2_valid_dv_timings`, `v4l2_enum_dv_timings_cap`, `v4l2_find_dv_timings_cap`, `v4l2_find_dv_timings_cea861_vic`, `v4l2_match_dv_timings`, `v4l2_print_dv_timings`, `v4l2_dv_timings_aspect_ratio`, `v4l2_calc_timeperframe`, `v4l2_detect_cvt`, and `v4l2_detect_gtf`. EDID and HDMI helpers include `v4l2_calc_aspect_ratio`, `v4l2_hdmi_rx_colorimetry`, `v4l2_num_edid_blocks`, `v4l2_get_edid_phys_addr`, `v4l2_set_edid_phys_addr`, `v4l2_phys_addr_for_input`, and `v4l2_phys_addr_validate`. Under `CONFIG_DEBUG_FS`, `v4l2_debugfs_if_alloc` and `v4l2_debugfs_if_free` create InfoFrame debugfs files.

## Control Flow
Validation starts with `v4l2_valid_dv_timings`: it accepts only `V4L2_DV_BT_656_1120`, enforces capability bounds for width, height, pixel clock, standard flags, interlaced/progressive support, and sanity bounds for porch/sync fields, then calls an optional driver callback. Enumeration and preset lookup iterate `v4l2_dv_timings_presets`, using validation and matching to return the requested index or convert a measured timing to a known preset while preserving reduced-FPS flags where appropriate.

Timing matching compares type, active dimensions, interlace, polarity, pixel clock within a caller-supplied delta, blanking fields, optional reduced-FPS flags, and interlaced bottom-field fields. Printing derives total frame width/height, frame rate, porch/sync values, pixel clock, flags, standards, aspect, CEA VIC, and HDMI VIC. Aspect and frame-period helpers reduce rational values using `rational_best_approximation`.

`v4l2_detect_cvt` implements CVT and reduced-blanking V1/V2 detection from measured frame height, horizontal frequency, vsync, active width, polarity, and interlace. It derives vertical blanking, active dimensions, horizontal blanking, pixel clock, porch/sync fields, flags, then validates the candidate against capabilities. `v4l2_detect_gtf` performs the same role for default or secondary GTF, using the supplied or default aspect ratio. HDMI colorimetry maps AVI/vendor InfoFrame fields to V4L2 colorspace, YCbCr encoding, quantization, and transfer function. EDID helpers compute block counts, manipulate CEC source physical addresses, update checksums, and validate parent/port hierarchy.

## State and Persistence Behavior
Most functions are pure computations over caller-provided structs. State mutation is limited to output structs, EDID byte arrays, and debugfs allocation. `v4l2_set_edid_phys_addr` mutates EDID in memory and recomputes the affected block checksum. Debugfs helpers allocate a `v4l2_debugfs_if` object and files under an existing dentry; cleanup removes that subtree.

## Dependencies and Integration Points
The file depends on V4L2 DV timing definitions, HDMI InfoFrame structs, CEC EDID helpers, rational arithmetic, 64-bit division helpers, debugfs, and kernel logging. It is used by receiver/transmitter drivers, ioctl handlers for DV timings, HDMI capture drivers, CEC/EDID handling, and debug tooling that exposes InfoFrames.

## Risks
Arithmetic overflow and rounding are central risks, especially pixel clock and blanking calculations that combine dimensions and horizontal frequencies. Capability validation must reject malformed timings without excluding legitimate custom modes. EDID handling relies on exact byte offsets and checksum updates; incorrect source physical address handling can break CEC routing. HDMI colorimetry support explicitly does not cover all newer HDR/DCI-P3 cases. Debugfs allocation is optional and must tolerate missing roots or callbacks.

## Test Signals
Test with preset enumeration across representative caps, custom timing validation boundaries, CVT/GTF generated modelines, reduced-blanking V1/V2 detection, interlaced half-line modes, EDID block count edge cases including EEODB, CEC physical-address parent/port derivation, EDID checksum changes after physical-address writes, and HDMI InfoFrame colorimetry cases for RGB, YCbCr, limited/full range, BT.601, BT.709, xvYCC, opRGB, and BT.2020.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-dv-timings.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-event.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-event.c

## Purpose
`v4l2-event.c` implements V4L2 event subscription, queueing, dequeueing, wakeup, and unsubscribe behavior for `struct v4l2_fh` file handles. It gives drivers a shared event queue model with per-subscription ring buffers, sequence numbers, timestamps, and type-specific merge/replace hooks.

## Important APIs, Types, and Functions
Exported APIs include `v4l2_event_dequeue`, `v4l2_event_queue`, `v4l2_event_queue_fh`, `v4l2_event_pending`, `v4l2_event_wake_all`, `v4l2_event_subscribe`, `v4l2_event_unsubscribe_all`, `v4l2_event_unsubscribe`, `v4l2_event_subdev_unsubscribe`, `v4l2_src_change_event_subscribe`, and `v4l2_src_change_event_subdev_subscribe`. Core types are `struct v4l2_fh`, `struct v4l2_subscribed_event`, `struct v4l2_kevent`, `struct v4l2_event`, and `struct v4l2_subscribed_event_ops`.

## Control Flow
`v4l2_event_subscribe` rejects `V4L2_EVENT_ALL`, normalizes queue depth to at least one, allocates a flexible `v4l2_subscribed_event`, initializes embedded event slots, and adds it to `fh->subscribed` under `fh->vdev->fh_lock` while serialized by `fh->subscribe_lock`. Duplicate subscriptions are treated as success after freeing the new allocation. Optional `ops->add` can initialize driver-specific subscription state; failure removes and frees the subscription.

Queueing starts at `v4l2_event_queue` for all file handles on a video device, or `v4l2_event_queue_fh` for one handle. Both take `fh_lock` and call `__v4l2_event_queue_fh`, which first checks whether the file handle subscribed to the event type/id. If the subscription ring is full, the oldest queued event is removed and either replaced or merged through subscription ops. The new event is filled with type, id, payload, timestamp, and incremented per-file-handle sequence number, added to `fh->available`, and waiters are woken.

`v4l2_event_dequeue` supports nonblocking dequeue directly and blocking dequeue through `wait_event_interruptible`, temporarily releasing `vdev->lock` while sleeping. Dequeue removes the oldest available event, updates pending count and timestamp, advances the subscription ring head, and decrements in-use count. Unsubscribe removes pending events from `fh->available`, calls optional `ops->del`, removes the subscription list node, and frees it. Source-change subscriptions use merge/replace hooks that OR change bits.

## State and Persistence Behavior
All event state is per open file handle and in memory only. `fh->available`, `fh->navailable`, `fh->sequence`, and each subscription's `first`, `in_use`, and event array define queue state. Timestamps are captured using `ktime_get_ns` when queued and converted to `timespec64` when dequeued. Closing a file handle via `v4l2_fh_exit` is expected to call `v4l2_event_unsubscribe_all`.

## Dependencies and Integration Points
The file depends on `v4l2-fh` initialization, `video_device` file-handle lists and locks, wait queues, spinlocks, mutexes, and V4L2 ioctl wrappers for `VIDIOC_DQEVENT`, `VIDIOC_SUBSCRIBE_EVENT`, and `VIDIOC_UNSUBSCRIBE_EVENT`. Subdevice event wrappers use the same core logic.

## Risks
Correct lock ordering is critical: subscription changes use `subscribe_lock` plus `fh_lock`, while queue/dequeue use `fh_lock` and dequeue may release/reacquire `vdev->lock`. Ring full behavior must maintain `fh->navailable` and list membership exactly or pending counts go stale. Merge/replace hooks can change payload semantics, so event types with lossy queues need tests. Blocking dequeue must handle wakeups where no event remains, retrying on `-ENOENT`.

## Test Signals
Test duplicate subscribe, queue depth one replacement, queue depth greater than one merge, blocking and nonblocking dequeue, pending counts, unsubscribe with pending events, unsubscribe-all during close, source-change bit merging, multiple file handles subscribed to the same event, and lockdep under concurrent queue/dequeue/unsubscribe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-fh.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-fh.c

## Purpose
`v4l2-fh.c` implements the standard V4L2 file-handle lifecycle. It initializes `struct v4l2_fh`, attaches it to a `struct file`, participates in per-video-device file-handle lists, owns per-open priority state, and provides close-time cleanup for media-source and event subscription state.

## Important APIs, Types, and Functions
The exported functions are `v4l2_fh_init`, `v4l2_fh_add`, `v4l2_fh_open`, `v4l2_fh_del`, `v4l2_fh_exit`, `v4l2_fh_release`, and `v4l2_fh_is_singular`. Important types are `struct v4l2_fh`, `struct video_device`, `struct file`, and the priority/event state accessed through `fh->prio`, `fh->wait`, `fh->available`, `fh->subscribed`, and `fh->subscribe_lock`.

## Control Flow
Drivers can either embed `struct v4l2_fh` or use `v4l2_fh_open`, which allocates one. `v4l2_fh_init` stores the video device pointer, inherits the video device control handler, initializes list heads and wait queues, sets the video-device `V4L2_FL_USES_V4L2_FH` flag, enables priority ioctls in `valid_ioctls`, initializes priority to unset, initializes event lists, sets sequence to `-1`, and initializes the subscription mutex.

`v4l2_fh_add` stores the file handle in `filp->private_data`, opens priority state through `v4l2_prio_open`, and adds the file handle to `vdev->fh_list` under `vdev->fh_lock`. `v4l2_fh_del` removes it from the list, closes priority state, and clears `private_data`. `v4l2_fh_exit` disables any media source associated with the video device, unsubscribes all events, destroys the subscription mutex, and nulls `fh->vdev`. `v4l2_fh_release` composes delete, exit, and free for handles allocated by `v4l2_fh_open`. `v4l2_fh_is_singular` checks whether this handle is the only entry in the video-device file-handle list.

## State and Persistence Behavior
State is per-open and in memory only. It persists for the lifetime of the open file and is exposed to other V4L2 helpers through `file_to_v4l2_fh`. Priority state affects ioctl arbitration. Event queues and subscriptions persist until explicit unsubscribe or close. `v4l2_fh_is_singular` is used by components such as flash helpers to determine first-open/last-close transitions.

## Dependencies and Integration Points
This file integrates with `v4l2-dev`, `v4l2-event`, `v4l2-ioctl`, V4L2 priority helpers, and media-controller source enabling/disabling through `v4l2-mc`. It is foundational for ioctl code that needs per-file priority, event dequeue, or control handlers.

## Risks
Drivers that mix embedded and allocated file handles must match the lifecycle correctly and not double-free. Missing `v4l2_fh_exit` leaks event subscriptions and leaves media sources enabled. The singular-open test is inherently moment-in-time and must be used under appropriate open/close serialization by callers. Clearing `private_data` affects all later helpers that assume `file_to_v4l2_fh` can return NULL.

## Test Signals
Test open/release paths, embedded-handle users, priority ioctl availability after init, event cleanup on release, media source disable on close, correct list membership under concurrent opens, and first-open/last-close consumers using `v4l2_fh_is_singular`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-fh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-flash-led-class.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-flash-led-class.c

## Purpose
`v4l2-flash-led-class.c` bridges Linux LED flash-class devices into V4L2 flash subdevices. It maps LED brightness, timeout, strobe, fault, torch, flash, indicator, and external-strobe operations to V4L2 controls and registers a V4L2 subdevice with a media entity and devnode.

## Important APIs, Types, and Functions
Public APIs are `v4l2_flash_init`, `v4l2_flash_indicator_init`, and `v4l2_flash_release`. Important internal functions include `v4l2_flash_g_volatile_ctrl`, `v4l2_flash_s_ctrl`, `v4l2_flash_init_controls`, `__sync_device_with_v4l2_controls`, `v4l2_flash_open`, `v4l2_flash_close`, and `__v4l2_flash_init`. Core state lives in `struct v4l2_flash`: LED classdev pointers, V4L2 subdev, control handler, control pointer array, and optional conversion/external-strobe ops.

## Control Flow
Initialization allocates `struct v4l2_flash`, fills LED and operation pointers, initializes a V4L2 subdevice with internal open/close ops and `V4L2_SUBDEV_FL_HAS_DEVNODE`, sets the media entity function to `MEDIA_ENT_F_FLASH`, initializes controls based on LED capabilities and `v4l2_flash_config`, takes an fwnode reference, and async-registers the subdevice. Indicator-only initialization calls the same shared path with only an indicator LED.

Control setup builds `v4l2_ctrl_config` entries from LED flash settings. It conditionally creates controls for LED mode, torch intensity, flash intensity, indicator intensity, flash timeout, strobe source, strobe, strobe stop, strobe status, and fault. The control ops route reads of volatile controls to LED update/get APIs and writes to LED brightness, flash brightness, timeout, strobe, and optional external-strobe callbacks. LED mode transitions stop active strobe, turn torch off when entering flash mode, enable torch brightness when entering torch mode, and cache strobe source until flash mode when needed.

Open and close are tied to `v4l2_fh_is_singular`: on first V4L2 open, LED sysfs access and triggers are disabled for the flash/indicator LEDs and device state is synchronized from V4L2 controls; on last close, sysfs access is re-enabled and strobe source is reset to software when present. Release unregisters the async subdevice, drops fwnode reference, frees controls, and cleans the media entity.

## State and Persistence Behavior
State persists in the control handler and LED class devices while the subdevice is registered. V4L2 control values cache desired torch intensity, flash intensity, timeout, LED mode, and strobe source. Hardware state is synchronized on first open and on relevant control writes. No on-disk persistence is involved; sysfs availability is temporarily changed while V4L2 owns the LED.

## Dependencies and Integration Points
The file depends on LED class/flash APIs, V4L2 controls, V4L2 async subdevice registration, media entity setup, fwnode references, and V4L2 file-handle singular-open detection. It is used by LED flash drivers that want V4L2 camera flash integration.

## Risks
Conversion between microamp intensity and LED brightness must honor min/step and indicator LED zero semantics. External-strobe mode is optional and has hardware-specific side effects. Open failure after sysfs disable must re-enable sysfs for both LEDs. Missing or mismatched LED capabilities produce limited controls. First-open/last-close behavior depends on correct file-handle lifecycle. Fault and strobe status are volatile and can fail at read time.

## Test Signals
Test control creation for flash-only, indicator-only, and combined devices; brightness/intensity conversion at min, max, and step boundaries; LED mode transitions; software strobe busy checks; external strobe source callbacks; volatile fault/status reads; open/close sysfs disable/enable; async registration failure unwind; and release idempotence for NULL/error pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-flash-led-class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-fwnode.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-fwnode.c

## Purpose
`v4l2-fwnode.c` parses firmware-node camera/video graph bindings and device properties into V4L2 media-bus, connector, async-subdevice, and sensor-registration structures. It supports Device Tree, ACPI, and software-node fwnodes, including CSI-2 D-PHY/C-PHY, CSI-1/CCP2, parallel, BT.656, DPI, analog connectors, orientation/rotation properties, and sensor-related references such as flash LEDs and focus lenses.

## Important APIs, Types, and Functions
Endpoint APIs are `v4l2_fwnode_endpoint_parse`, `v4l2_fwnode_endpoint_alloc_parse`, and `v4l2_fwnode_endpoint_free`. Link and connector APIs are `v4l2_fwnode_parse_link`, `v4l2_fwnode_put_link`, `v4l2_fwnode_connector_parse`, `v4l2_fwnode_connector_add_link`, and `v4l2_fwnode_connector_free`. Device/sensor APIs are `v4l2_fwnode_device_parse` and `v4l2_async_register_subdev_sensor`. Key internal helpers parse CSI-2, parallel, CSI-1, generic references, ACPI integer-property references, and common sensor references.

## Control Flow
Endpoint parsing begins by reading the fwnode `bus-type`, converting it to a V4L2 media-bus type, reconciling it with any caller-supplied expected `vep->bus_type`, then dispatching to bus-specific parsers. CSI-2 parsing handles default lane mapping, `data-lanes`, duplicate lane detection, optional `clock-lanes`, `lane-polarities`, C-PHY `line-orders`, and `clock-noncontinuous`. Invalid lane-polarity or line-order counts fail with `-EINVAL`; duplicate lanes fall back to default mapping where possible. Parallel/BT.656 parsing reads polarity, pclk, data-active, slave/master, bus-width, data-shift, sync-on-green, and data-enable properties, then infers parallel vs BT.656 when the bus type was unknown. CSI-1/CCP2 parsing reads clock/data lane and strobe properties.

`v4l2_fwnode_endpoint_alloc_parse` extends endpoint parsing by allocating and reading `link-frequencies`; callers must free with `v4l2_fwnode_endpoint_free`. Link parsing obtains the local port parent and remote endpoint/parent from graph helpers and stores local/remote ids and ports; `v4l2_fwnode_put_link` releases both parent refs. Connector parsing finds a known connector compatible string on either side of the graph edge, reads label and analog SDTV standards, and `connector_add_link` appends parsed graph links to the connector link list.

Device parsing reads `orientation` and `rotation`, validates allowed ranges, and stores unset sentinels if absent. Sensor async registration allocates a notifier, initializes it for the subdevice, obtains a privacy LED, parses sensor references (`flash-leds`, `mipi-img-flash-leds`, `lens-focus`, `mipi-img-lens-focus`) via generic fwnode references or ACPI integer-property traversal, registers the notifier, then registers the subdevice. Failure unwinds notifier registration, privacy LED, cleanup, and allocation.

## State and Persistence Behavior
The file mutates caller-provided endpoint, connector, device-property, link, and notifier structures. It allocates link-frequency arrays, connector labels/links, async notifier storage, and fwnode references that must be released by matching free/put/cleanup functions. There is no persistent storage beyond firmware descriptions supplied by platform firmware.

## Dependencies and Integration Points
It depends on firmware property APIs, fwnode graph helpers, ACPI node detection, V4L2 async notifier APIs, V4L2 subdevice privacy LED helpers, media-bus configuration structs, and kernel memory management. It is a bridge between firmware graph descriptions and the runtime media graph used by camera bridge/sensor drivers.

## Risks
Reference-count handling is the main risk: every graph parent, endpoint, child fwnode, connector label, link, and notifier allocation has a matching cleanup path. ACPI integer reference traversal is complex and can fail differently for out-of-bounds vs malformed properties. Bus-type guessing may choose CSI-2 or parallel based on partial properties, so ambiguous firmware can produce surprising defaults. Duplicate CSI lanes fall back to defaults, which may hide firmware mistakes. Sensor registration has several failure stages that must keep privacy LED and notifier ownership consistent.

## Test Signals
Test DT and ACPI endpoint parsing for CSI-2 D-PHY, C-PHY, CSI-1/CCP2, parallel, BT.656, unknown/guessed bus types, invalid lane counts, duplicate lanes, link-frequency allocation/free, connector parse/add/free with labels and SDTV standards, orientation/rotation validation, sensor async registration with duplicate references, missing references, privacy LED failures, and notifier/subdevice registration unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-fwnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-h264.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-h264.c

## Purpose
`v4l2-h264.c` provides stateless H.264 helper logic for decoder drivers that need H.264 reference picture lists derived from V4L2 controls. It builds P, B0, and B1 reference lists from decode parameters, SPS information, and the decoded picture buffer (DPB), following the H.264 specification's reference-list construction rules.

## Important APIs, Types, and Functions
Exported APIs are `v4l2_h264_init_reflist_builder`, `v4l2_h264_build_p_ref_list`, and `v4l2_h264_build_b_ref_lists`. Important internal functions are `v4l2_h264_get_poc`, P/B0/B1 sort comparators, `reorder_field_reflist`, and debug formatting/printing helpers. Important types are `struct v4l2_h264_reflist_builder`, `struct v4l2_ctrl_h264_decode_params`, `struct v4l2_ctrl_h264_sps`, `struct v4l2_h264_dpb_entry`, and `struct v4l2_h264_reference`.

## Control Flow
`v4l2_h264_init_reflist_builder` computes `max_frame_num`, current frame number, current picture order count, and current reference field type from decode parameters. It scans active DPB entries, records whether each is long-term, applies short-term frame-number wraparound relative to the current frame number, copies top/bottom POCs, and fills an unordered reference list. For frame pictures it inserts one frame reference per active DPB entry; for field pictures it inserts top and bottom field references separately when present. Unused list entries get deterministic indexes.

`v4l2_h264_build_p_ref_list` copies the unordered list, sorts it with `sort_r` using short-term-before-long-term ordering, descending short-term wrapped frame number, and ascending long-term frame number. Field pictures are then reordered to alternate references by current field parity, separately for short-term and long-term references.

`v4l2_h264_build_b_ref_lists` builds two sorted copies. B0 orders short-term references with POC less than current first in descending POC, followed by greater POC in ascending POC, with long-term references by ascending frame number. B1 uses the complementary short-term order. Field pictures get parity reordering. If B0 and B1 are identical and contain more than one entry, the first two B1 entries are swapped as required. Debug helpers print compact reference-list strings.

## State and Persistence Behavior
All state is transient in caller-provided builder and output arrays. There is no persistence or allocation in the core build functions. Debug formatting allocates a temporary string only when debug output is evaluated and frees it immediately.

## Dependencies and Integration Points
The file depends on V4L2 H.264 control structures and kernel `sort_r`. It is used by stateless H.264 decoder drivers that receive userspace-provided DPB/decode controls and need hardware-ready reference list order.

## Risks
Correctness depends on H.264 spec details: frame-number wraparound, long-term vs short-term ordering, POC comparison for frame vs fields, and field parity alternation. Invalid DPB indexes are guarded by `WARN_ON` in comparators but still return an ordering. A mismatch between userspace controls and DPB contents can produce hardware decode failures. Debug formatting can truncate long output but does not affect decode state.

## Test Signals
Test frame and field pictures, P and B slices, short-term and long-term references, frame-number wraparound, top-only and bottom-only DPB entries, identical B0/B1 swap behavior, empty and full DPB, and comparison against known H.264 reference-list examples from conformance streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-h264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-i2c.c

## Purpose
`v4l2-i2c.c` provides helper functions for V4L2 subdevices implemented as I2C clients. It initializes subdevice/client cross-links, creates board-info or probed I2C clients, registers them under a V4L2 device, unregisters non-firmware-created clients, reports subdevice addresses, and exposes common tuner probe address lists.

## Important APIs, Types, and Functions
Exported APIs include `v4l2_i2c_subdev_unregister`, `v4l2_i2c_subdev_set_name`, `v4l2_i2c_subdev_init`, `v4l2_i2c_new_subdev_board`, `v4l2_i2c_new_subdev`, `v4l2_i2c_subdev_addr`, and `v4l2_i2c_tuner_addrs`. Important types are `struct v4l2_subdev`, `struct i2c_client`, `struct i2c_adapter`, `struct i2c_board_info`, and `enum v4l2_i2c_tuner_type`.

## Control Flow
`v4l2_i2c_subdev_init` calls `v4l2_subdev_init`, marks the subdevice as I2C, sets the owner from the I2C driver's module owner, stores the device pointer, connects `sd` to `client` through V4L2 and I2C clientdata, and generates a name containing driver, adapter id, and address. `v4l2_i2c_new_subdev` builds board info from a client type and address, then delegates to `v4l2_i2c_new_subdev_board`.

`v4l2_i2c_new_subdev_board` first requests the I2C module by type. It creates either a scanned or fixed-address I2C client, checks that a driver bound, temporarily gets the I2C driver's module owner, obtains the subdevice from clientdata, registers it with the V4L2 device using `__v4l2_device_register_subdev`, then releases the temporary module reference. If any step leaves a client without a registered subdevice, the client is unregistered. `v4l2_i2c_subdev_unregister` explicitly unregisters only clients that lack firmware nodes, preserving DT/ACPI-created devices.

## State and Persistence Behavior
State is runtime-only: I2C client objects, V4L2 subdevice bindings, clientdata pointers, module references, and optional V4L2-device subdevice list membership. Firmware-created devices are not removed by this helper because the platform will not recreate them from a V4L2 driver probe alone.

## Dependencies and Integration Points
This file integrates the I2C core, module autoloading, V4L2 subdevice core, and V4L2 device registration. Bridge drivers use it to instantiate legacy board-info based sensors, tuners, and decoders.

## Risks
Autoload timing and module reference ordering are delicate: the helper explicitly loads the module before creating the client so `client->driver` and clientdata are available. Firmware-created clients must not be unregistered. Failure paths must avoid leaking clients or module references. Name construction assumes `client->dev.driver` and adapter data are valid after binding.

## Test Signals
Test fixed-address and probed-address creation, missing module/driver binding, failed V4L2 subdevice registration, firmware-node clients on unregister, address reporting with and without clientdata, tuner address list selection, and module reference balance over probe/remove cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ioctl.c

## Purpose
`v4l2-ioctl.c` is the generic V4L2 ioctl framework for video devices. It translates userspace ioctl calls into driver `struct v4l2_ioctl_ops` callbacks, validates command availability and buffer types, sanitizes user-visible structs, integrates controls/events/priority/media-source handling, supports compat/time32 translation, copies array arguments safely, and emits optional debug traces.

## Important APIs, Types, and Functions
Exported helpers include `v4l2_norm_to_name`, `v4l2_video_std_frame_period`, `v4l2_video_std_construct`, `v4l_video_std_enumstd`, `v4l_printk_ioctl`, `v4l2_translate_cmd`, and `video_ioctl2`. Important internal components are `struct v4l2_ioctl_info`, the `v4l2_ioctls[]` dispatch table, `check_ext_ctrls`, `check_fmt`, `v4l_sanitize_format`, per-command wrappers such as `v4l_querycap`, `v4l_enum_fmt`, `v4l_g_fmt`, `v4l_s_fmt`, `v4l_try_fmt`, buffer/streaming wrappers, control wrappers, crop/selection shims, debug register handlers, event wrappers, `__video_do_ioctl`, `check_array_args`, `video_get_user`, `video_put_user`, and `video_usercopy`.

## Control Flow
The top-level entry is `video_ioctl2`, which calls `video_usercopy` with `__video_do_ioctl`. `video_usercopy` translates the command for compat/time32, allocates a stack or heap argument buffer, copies in only the needed input bytes, zeros uncopied fields, detects secondary user arrays such as multiplanar planes, EDID bytes, extended controls, and subdev routes, copies those arrays to kernel memory, invokes the ioctl function, traces QBUF/DQBUF on success, copies arrays and the main struct back when needed, and frees temporary buffers.

`__video_do_ioctl` obtains `video_device`, ioctl ops, file handle, optional request queue lock for STREAMON/STREAMOFF/REQBUFS, and the correct serialization lock. Queue ioctls prefer mem2mem queue locks or vb2 queue locks; otherwise the video-device lock is used. It rejects unregistered devices, checks whether a known command is enabled in `valid_ioctls` unless a file-handle control handler can satisfy a control ioctl, enforces priority for flagged commands, calls the dispatch-table wrapper or driver default handler, and prints debug output if requested.

Per-command wrappers normalize V4L2 API behavior before calling drivers. Format paths call `check_fmt`, sanitize colorspace/extended pixel-format fields, zero reserved tails, map single vs multiplanar ops according to capabilities, and fill known format descriptions. Buffer paths validate buffer type and expose remove-buffer capabilities. Control paths prefer file-handle or video-device control handlers and fall back to ioctl ops. Selection shims map old crop APIs onto selection targets and handle the inverted-crop quirk. Input/output/frequency/std/tuner wrappers enforce media-controller and device-type rules. Event wrappers use `v4l2_event_dequeue` and driver subscribe/unsubscribe hooks. Advanced debug register handlers require `CAP_SYS_ADMIN` and can target bridge or subdevices.

## State and Persistence Behavior
The framework mutates per-open priority state, request queue serialization, control values, event queues, buffer queues, and driver/device state through callbacks. It maintains no on-disk persistence. The `valid_ioctls` bitmap on `struct video_device` is the command availability state. User-copy paths zero reserved fields and always-copy certain ioctls even on failure, which defines ABI-visible state transfer.

## Dependencies and Integration Points
This file ties together V4L2 devices, file handles, controls, events, videobuf2, mem2mem, media controller request queues, subdevices, compat ioctl support, tracepoints, and the Linux usercopy APIs. It is the primary ABI boundary for userspace tools, camera stacks, codecs, tuners, SDR, VBI, metadata, and touch devices.

## Risks
This is high-blast-radius ABI code. Risks include usercopy size mistakes, array bounds mistakes, compat/time32 translation regressions, incorrect lock selection causing queue deadlocks or races, priority bypass, stale `valid_ioctls`, leaking uninitialized reserved fields, incorrect format sanitization, buffer type confusion, and mismatch between generic shims and driver expectations. Many wrappers deliberately emulate older APIs, so changing them can break legacy userspace.

## Test Signals
Test with v4l2-compliance across video capture/output, mplane, metadata, SDR, VBI, touch, mem2mem, and media-controller devices. Exercise all usercopy array paths, compat ioctls, request queue locking, debug logging, priority checks, control handlers and fallback ops, event dequeue/subscribe/unsubscribe, crop-selection compatibility, pixel format enumeration, EDID always-copy behavior, and negative cases for invalid buffer types, excessive array counts, unregistered devices, and disabled ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-isp.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-isp.c

## Purpose
`v4l2-isp.c` provides generic validation helpers for V4L2 ISP parameter buffers. It checks the videobuf2 payload size, the `v4l2_isp_params_buffer` header, format version, total data size, and the sequence of typed ISP parameter blocks supplied to drivers.

## Important APIs, Types, and Functions
The exported APIs are `v4l2_isp_params_validate_buffer_size` and `v4l2_isp_params_validate_buffer`. Important types are `struct vb2_buffer`, `struct v4l2_isp_params_buffer`, `struct v4l2_isp_params_block_header`, and `struct v4l2_isp_params_block_type_info`.

## Control Flow
`v4l2_isp_params_validate_buffer_size` obtains plane 0 payload size, rejects payloads larger than a driver-supplied maximum destination size, rejects payloads smaller than the ISP parameter buffer header, and otherwise succeeds.

`v4l2_isp_params_validate_buffer` accepts only format versions `V4L2_ISP_PARAMS_VERSION_V0` and `V4L2_ISP_PARAMS_VERSION_V1`, allowing existing drivers that used either zero or one as their first supported version. It checks that `header_size + buffer->data_size` equals the vb2 payload size. It then walks the variable-length block data while enough bytes remain for a block header. For each block it validates that the type index is in range, the block does not exceed remaining data, ENABLE and DISABLE flags are not both set, and the block size matches the driver-provided type info. A disabled block may contain only the header. Any trailing bytes that cannot form a block header cause failure.

## State and Persistence Behavior
The helpers do not mutate buffer contents or persistent state. They read vb2 payload size and caller-provided metadata, emit `dev_dbg` diagnostics, and return success or `-EINVAL`.

## Dependencies and Integration Points
The file depends on `media/v4l2-isp.h`, `videobuf2-core`, and device debug logging. ISP/statistics drivers can call these helpers before consuming userspace parameter buffers from metadata queues.

## Risks
The main risks are malformed user buffers: integer size mismatches, block sizes that skip over data, invalid type indexes, unsupported versions, contradictory flags, and partial trailing data. Callers must still ensure that the memory pointed to by `buffer` corresponds to the validated vb2 payload and remains accessible. Type-info tables must match driver ABI definitions.

## Test Signals
Test payload too large, payload smaller than header, unsupported version, header data size mismatch, valid empty data area, valid multiple blocks, invalid block type, block size beyond remaining data, enable+disable flags together, disabled header-only blocks, incorrect block sizes, and trailing bytes after the final block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-isp.c -->
