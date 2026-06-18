# subset-b-005494 USB gadget function research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uac1.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uac1.c

## Purpose
This file implements the configfs USB Audio Class 1.0 gadget function named `uac1` using the shared `u_audio` engine. It exposes a virtual ALSA-backed audio function without requiring a physical codec. The implemented topology is configurable in both directions: USB OUT to ALSA capture, and ALSA playback to USB IN. It builds UAC1 AudioControl and AudioStreaming descriptors dynamically from `struct f_uac1_opts`, including optional feature units for mute and volume controls.

## Important APIs, types, and functions
`struct f_uac1` embeds `struct g_audio` and tracks the assigned AC, AS IN, and AS OUT interface numbers, current alternate settings, an EP0 setup copy, optional interrupt endpoint state, and current capture/playback sample rates. `f_audio_alloc_inst()` creates the configfs instance with defaults from `u_uac1.h`; `f_audio_alloc()` creates one function object and wires `bind`, `unbind`, `set_alt`, `get_alt`, `setup`, `disable`, `suspend`, and `free_func`. `f_audio_bind()` is the main descriptor and ALSA setup path. `setup_descriptor()`, `build_ac_header_desc()`, and `build_fu_desc()` patch class descriptors and descriptor arrays based on channel masks and feature-unit options. `f_audio_setup()` dispatches UAC1 class control requests to feature-unit handlers and endpoint sample-rate handlers. `f_audio_set_alt()` starts and stops `u_audio` capture/playback streams.

## Control flow
Allocation starts with configfs defaults and a refcount-protected option object. Binding validates channel masks, sample sizes, sample rates, and volume ranges; attaches strings; allocates dynamic AC and feature-unit descriptors; assigns interface IDs; autoconfigures optional interrupt, OUT isochronous, and IN isochronous endpoints; assigns FS/SS descriptors; copies options into `audio->params`; and calls `g_audio_setup()`. Runtime interface selection restarts the AC interrupt endpoint for alt 0 and maps AS OUT alt 1 to `u_audio_start_capture()` and AS IN alt 1 to `u_audio_start_playback()`. EP0 class requests read or update mute, volume, and endpoint sampling frequency, then queue the composite EP0 request.

## State and persistence
Persistent configuration lives in configfs attributes on `struct f_uac1_opts` until a function is linked; stores reject changes while `opts->refcnt` is nonzero. Runtime state is in `struct f_uac1`: alternate settings, `int_count`, interrupt endpoint pointer, and current sample rates. The actual audio data state lives in `u_audio` and ALSA objects created by `g_audio_setup()`. No on-disk persistence is implemented.

## Dependencies and integration points
The file depends on the composite gadget framework, Linux USB audio descriptor definitions, `u_audio.h`, and `u_uac1.h`. It integrates with configfs through generated `CONFIGFS_ATTR` attributes, with the ALSA-backed gadget audio layer through `g_audio_setup()`, `u_audio_start_*()`, `u_audio_stop_*()`, and `u_audio_set/get_*()` calls, and with host UAC1 control behavior through EP0 setup callbacks. It registers through `DECLARE_USB_FUNCTION_INIT(uac1, ...)`.

## Risks and edge cases
The static global descriptor objects and global dynamic descriptor pointers are patched during bind, so concurrent instances depend on configfs refcounting and gadget serialization to avoid cross-instance descriptor mutation. Rate-list configfs parsing clears the existing array before fully validating all tokens, so invalid input can leave an empty list while still under the lock. Endpoint sample-rate handling expects exactly three data bytes and recognizes hard-coded endpoint IDs `(USB_DIR_IN | 2)` and `(USB_DIR_OUT | 1)`, which is sensitive to descriptor layout assumptions. Unsupported entity/control combinations log errors and stall or return `-EOPNOTSUPP`.

## Test signals
Useful tests include configfs attribute read/write coverage before and after linking, invalid channel mask/sample size/rate/volume validation, enumeration on FS and SS gadgets with IN-only, OUT-only, and duplex settings, UAC1 host GET/SET mute and volume requests, sample-rate SET_CUR requests, altsetting stream start/stop, suspend/disable cleanup, and interrupt notification throttling via `UAC1_DEF_INT_REQ_NUM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uac1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uac1_legacy.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uac1_legacy.c

## Purpose
This file implements the older `uac1_legacy` USB Audio Class 1.0 function. Unlike the modern UAC1 function, it does not use the newer `g_audio`/`u_audio` parameter model for both directions. It exposes a fixed UAC1 descriptor topology with one AudioControl interface, one playback-oriented AudioStreaming interface, one isochronous OUT endpoint, and a simple feature unit for mute and volume.

## Important APIs, types, and functions
`struct f_audio` embeds `struct gaudio`, tracks AC/AS interface state, owns the OUT endpoint, maintains a spinlock-protected playback queue, and stores the active class-specific SET control. `struct f_audio_buf` is the temporary buffer queued to deferred playback work. `f_audio_set_alt()` enables the OUT endpoint and prequeues USB requests. `f_audio_out_ep_complete()` accumulates USB OUT data into `audio->copy_buf` and schedules `f_audio_playback_work()` when a buffer is full. `audio_set_intf_req()` and `audio_get_intf_req()` implement class requests over the feature-unit control list. `control_selector_init()` installs the static mute and volume controls, backed by `generic_set_cmd()` and `generic_get_cmd()`.

## Control flow
`f_audio_alloc_inst()` creates a configfs instance with request buffer size, request count, audio buffer size, and ALSA file path options. `f_audio_alloc()` allocates the function, initializes the queue, lock, control selector list, and playback work. `f_audio_bind()` initializes the ALSA gadget once per options object with `gaudio_setup()`, assigns string and interface IDs, builds descriptors from the playback parameters reported by `u_audio_get_playback_*()`, autoconfigures the OUT endpoint, and assigns FS descriptors. When the host selects AS alt 1, the function enables the endpoint, allocates an accumulation buffer, allocates and queues `req_count` OUT requests, and then cycles each completion back to the endpoint. Switching back to alt 0 queues any partial copy buffer to playback work.

## State and persistence
Configuration is stored in `struct f_uac1_legacy_opts` and locked by `opts->lock`; stores reject changes while the function is referenced. Runtime audio data is buffered in heap-allocated `f_audio_buf` objects on `play_queue` and drained by a workqueue callback into `u_audio_playback()`. Control values are kept in the static `usb_audio_control.data[]` arrays rather than persisted or synchronized to a real mixer.

## Dependencies and integration points
The file depends on `u_uac1_legacy.h`, the composite gadget framework, and the older `gaudio` helper API. Its configfs attributes expose low-level buffering knobs and legacy ALSA file names. It registers as `uac1_legacy` with `DECLARE_USB_FUNCTION_INIT`. The USB host-visible surface is static UAC1 descriptors and class requests for interface and endpoint controls.

## Risks and edge cases
The implementation is narrow: comments note only playback support, descriptors are mostly static, and `f_audio_disable()` is empty. The OUT request allocation path does not unwind already queued requests on a later allocation failure. The string attribute store appears inverted: it treats a non-NULL `kstrndup()` result as `-ENOMEM`, preventing updates and leaking the successful allocation path intent. Control request lookup can leave `set_con` NULL while still accepting the data stage, causing the completion to ignore the payload. Static control descriptors and control objects are shared across instances.

## Test signals
Exercise configfs buffer attributes, invalid writes while linked, enumeration of the fixed AC/AS descriptor set, alt 1 enable with different request counts and buffer sizes, continuous OUT streaming and queue rollover, alt 0 partial-buffer flush, mute/volume GET and SET requests, and disconnect/unbind behavior while OUT requests are queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uac1_legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uac2.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uac2.c

## Purpose
This file implements the USB Audio Class 2.0 gadget function named `uac2`. It exposes configurable UAC2 playback and capture paths backed by `u_audio`, with UAC2 clock sources, optional feature units, isochronous streaming endpoints, optional asynchronous feedback for capture, and FS/HS/SS descriptor sets.

## Important APIs, types, and functions
`struct f_uac2` embeds `struct g_audio`, tracks interface and alternate-setting state, stores a setup request copy, owns an optional interrupt endpoint, and records a transient clock ID while handling sample-rate SET_CUR. `afunc_alloc_inst()` creates default `struct f_uac2_opts` configfs state. `afunc_bind()` validates options, builds and patches descriptors, computes endpoint packet sizes, autoconfigures endpoints, assigns descriptors, fills `g_audio` parameters, and registers the virtual ALSA card. `set_ep_max_packet_size_bint()` and `get_max_bw_for_bint()` calculate bandwidth requirements from channel count, sample size, sample rates, feedback margin, speed, and bInterval. `in_rq_cur()`, `in_rq_range()`, `out_rq_cur()`, and `uac2_cs_control_sam_freq()` implement UAC2 class control requests.

## Control flow
Binding validates channel masks, sample sizes, sample rates, volume ranges, and HS/SS bInterval options. It attaches strings, creates feature-unit descriptors when mute or volume is enabled, assigns terminal, feature-unit, and clock IDs, assigns interface numbers, chooses capture sync mode, computes FS/HS/SS packet sizes, autoconfigures OUT, feedback IN, audio IN, and optional interrupt endpoints, copies endpoint addresses across speed descriptors, builds descriptor arrays, and calls `g_audio_setup()`. At runtime, AC alt 0 restarts the interrupt endpoint; AS OUT alt 1 starts capture; AS IN alt 1 starts playback; disabling resets alt state and stops both streams.

## State and persistence
Configfs options persist in memory under `opts->lock` until the function instance is freed; stores return `-EBUSY` while linked. Runtime state includes current altsettings, endpoint enablement, notification request count, and clock-control request context. Current sample rate, mute, and volume values are delegated to `u_audio`. There is no persistent storage beyond configfs state.

## Dependencies and integration points
The file depends on USB audio v2 descriptor definitions, the composite gadget framework, `u_audio.h`, and `u_uac2.h`. It integrates with `u_audio` for PCM streaming and control values, configfs for options, and the host through UAC2 class-specific interface requests. It registers with `DECLARE_USB_FUNCTION_INIT(uac2, ...)`.

## Risks and edge cases
Descriptor templates are static globals patched at bind time, with dynamic global feature-unit pointers; multi-instance behavior is sensitive to bind/unbind serialization. The rate-list configfs parser does not bound `i` before writing into the fixed-size array, so malformed long lists are risky. Several error returns after feature-unit allocation in `afunc_bind()` return directly instead of going through cleanup labels, which can leak descriptors on rare failures. Packet-size calculation clamps and warns when bandwidth exceeds endpoint limits, which may enumerate but drop audio. Unsupported controls return `-EOPNOTSUPP` or log TODO messages.

## Test signals
Test UAC2 enumeration on FS, HS, SS, and SSP; duplex, IN-only, and OUT-only configurations; adaptive versus async capture; feedback endpoint presence; bInterval auto and fixed settings; high sample-rate packet-size warnings; class GET_CUR/GET_RANGE for clocks and volume; SET_CUR for clock frequency, mute, and volume; interrupt notifications; and configfs mutation rejection while active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uac2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uvc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uvc.c

## Purpose
This file implements the USB Video Class gadget function named `uvc`. It bridges USB UVC control and streaming state to a V4L2 video-output device so userspace can provide video frames and respond to UVC control requests. Most format/frame descriptors come from configfs, while this file builds the standard interface, endpoint, and copied descriptor arrays required by the composite framework.

## Important APIs, types, and functions
`uvc_alloc_inst()` initializes default camera, processing, output terminal, control descriptor arrays, streaming endpoint defaults, and attaches the UVC configfs tree. `uvc_alloc()` creates `struct uvc_device`, resolves configfs streaming headers, snapshots descriptor pointers, and wires the `usb_function` callbacks. `uvc_function_bind()` clamps endpoint options, autoconfigures interrupt and streaming endpoints, assigns strings/interfaces, copies descriptors for each speed using `uvc_copy_descriptors()`, preallocates the EP0 control request, initializes V4L2 and video state, and registers the video node. `uvc_function_setup()`, `uvc_function_set_alt()`, and `uvc_function_disable()` translate USB events to V4L2 events. `uvc_function_setup_continue()`, `uvc_function_connect()`, and `uvc_function_disconnect()` are exported to the UVC userspace/video side.

## Control flow
On bind, the function normalizes streaming interval, max packet, and max burst, computes HS multiplier and SS companion fields, autoconfigures the highest applicable streaming endpoint to reserve UDC resources, assigns endpoint addresses into all speed descriptors, resolves extension-unit string IDs, attaches fallback strings, allocates control and streaming interface IDs, deep-copies descriptors, allocates EP0 request storage, registers V4L2, initializes `uvc_video`, and registers a V4L2 video device. Class-specific setup requests are not answered directly; they are queued as `UVC_EVENT_SETUP`, and OUT data stages later queue `UVC_EVENT_DATA`. Streaming alt 1 enables the video endpoint and queues `UVC_EVENT_STREAMON`; alt 0 queues `UVC_EVENT_STREAMOFF`; both use delayed status so userspace can coordinate completion.

## State and persistence
Configfs `struct f_uvc_opts` owns descriptor templates, extension-unit lists, endpoint knobs, optional string indexes, and refcount state. Runtime `struct uvc_device` tracks connection state, function unbind state, interface IDs, endpoint pointers, EP0 buffers, V4L2 device/video device objects, wait queues, and video streaming state. No durable persistence exists; state is rebuilt from configfs on function allocation and bind.

## Dependencies and integration points
The file depends on Linux USB gadget/composite APIs, V4L2 device and event APIs, UVC class descriptors, and local `uvc_configfs`, `uvc_v4l2`, and `uvc_video` helpers. It integrates with userspace through `/dev/video*`, V4L2 events, and ioctls such as the response path that eventually calls `uvc_function_setup_continue()`. It registers as the `uvc` USB function.

## Risks and edge cases
Descriptor copying assumes configfs control and streaming descriptor graphs are complete and linked; missing descriptors fail allocation. Endpoint options are clamped but still rely on the UDC supporting the requested resources. Unbind is complex: it waits for clean userspace disconnect and video-device release to avoid use-after-free, so regressions can deadlock or delay teardown. Control requests larger than `UVC_MAX_REQUEST_SIZE` are stalled. The delayed-status model requires userspace participation; absent or crashed userspace can stall host-visible control/stream transitions.

## Test signals
Test configfs descriptor graph creation and missing-header failures, enumeration at FS/HS/SS/SSP, interrupt endpoint enabled/disabled modes, extension-unit descriptor copying, UVC control GET/SET event delivery, userspace response completion, stream on/off altsetting with delayed status, disconnect while userspace holds the video node, and endpoint max packet/max burst combinations on different UDCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uvc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uvc.h

## Purpose
This header exposes the small cross-module control surface for the UVC gadget function. It forward-declares `struct uvc_device` and declares helpers used by the UVC V4L2/video implementation to resume delayed USB control handling and to publish userspace-driven connect/disconnect state to the USB composite function.

## Important APIs, types, and functions
The declared functions are `uvc_function_setup_continue(struct uvc_device *uvc, int disable_ep)`, `uvc_function_connect(struct uvc_device *uvc)`, and `uvc_function_disconnect(struct uvc_device *uvc)`. The first continues a delayed EP0 setup transaction and can disable the video endpoint first. The connect/disconnect helpers call into `usb_function_activate()` and `usb_function_deactivate()` in the implementation.

## Control flow
The header is included by UVC support files that do not need the full function implementation. Userspace-facing V4L2 code can receive a UVC event, prepare a response, and call back into `uvc_function_setup_continue()` after queuing the EP0 response. V4L2 open/close or stream lifecycle code can call connect/disconnect to let the host see the function become active or inactive.

## State and persistence
No state is defined here. All state is opaque behind `struct uvc_device` and owned by `f_uvc.c` plus the local UVC video/V4L2 modules.

## Dependencies and integration points
This is an internal header for the USB gadget function directory. It intentionally avoids including USB or V4L2 headers, reducing dependency spread and preserving encapsulation around `struct uvc_device`.

## Risks and edge cases
Because the functions operate on an opaque pointer, callers must only pass live `struct uvc_device` objects. Calling these helpers after unbind or without respecting the UVC locking/connection protocol can race teardown, though `f_uvc.c` includes guards for the disconnect path.

## Test signals
Compile coverage is the main signal. Runtime tests should verify that V4L2 response paths continue delayed EP0 setup successfully and that connect/disconnect helpers handle normal and unbind-adjacent paths without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_uvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/g_zero.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/g_zero.h

## Purpose
This header defines shared constants, option structures, and utility declarations for Gadget Zero function drivers. Gadget Zero is a USB gadget test/demo composition, and this header centralizes its source/sink and loopback configuration knobs.

## Important APIs, types, and functions
Constants define default buffer lengths, queue lengths, isochronous interval, packet sizes, and SuperSpeed queue defaults. `struct usb_zero_options` is a plain aggregate of module/config options. `struct f_ss_opts` stores source/sink function-instance state, including pattern, isochronous parameters, bulk parameters, a configfs mutex, and a refcount. `struct f_lb_opts` stores loopback function-instance state. The declared functions are `lb_modinit()`, `lb_modexit()`, and `disable_endpoints()`.

## Control flow
The header itself has no executable flow. Source/sink and loopback implementation files include it to interpret configfs or module options, guard option changes while a function is linked, and call `disable_endpoints()` during teardown or reset paths.

## State and persistence
The option structures hold in-memory configfs state for Gadget Zero function instances. The mutex comments document the intended concurrency model: configfs handles attribute read/write entry points, while the local lock protects against simultaneous attribute access and symlink create/remove operations. Refcounts indicate active users.

## Dependencies and integration points
The declarations integrate with the USB composite framework through `struct usb_function_instance`, `struct usb_composite_dev`, and endpoint pointers. The header is consumed by Gadget Zero-specific function drivers rather than exporting a standalone module API.

## Risks and edge cases
The option structures expose raw unsigned fields with validation expected in users. Incorrect validation can request unsupported endpoint intervals, packet sizes, bursts, or queue depths. The shared `disable_endpoints()` declaration implies callers must pass valid endpoint pointers and tolerate NULL or disabled endpoints according to the implementation contract.

## Test signals
Compile both source/sink and loopback functions, exercise configfs attributes for each option, link/unlink functions while reading and writing options, and verify endpoint disable behavior during disconnect and configuration changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/g_zero.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/ndis.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/ndis.h

## Purpose
This header provides small NDIS structure definitions used by the RNDIS gadget implementation for power-management and packet-pattern OIDs. It is a local adaptation of NDIS definitions needed to format or parse host-visible RNDIS data structures.

## Important APIs, types, and functions
`enum NDIS_DEVICE_POWER_STATE` defines D0 through D3 and sentinel power states. `struct NDIS_PM_WAKE_UP_CAPABILITIES` records minimum wake states for magic-packet, pattern, and link-change wake. `struct NDIS_PNP_CAPABILITIES` wraps flags and wake capabilities in little-endian form. `struct NDIS_PM_PACKET_PATTERN` describes a wake packet pattern with priority, mask size, offsets, size, and flags.

## Control flow
There is no executable control flow. The structures are included by `rndis.h` so RNDIS OID handling code can refer to NDIS PnP and wakeup payload layouts when those optional OID paths are enabled.

## State and persistence
No state is stored here. The structures describe wire-format or protocol-format data with explicit little-endian integer fields where appropriate.

## Dependencies and integration points
The header depends on Linux fixed-width endian typedefs such as `__le32`. It is an internal protocol companion for the USB gadget RNDIS code and not a general NDIS implementation.

## Risks and edge cases
The definitions must match host expectations exactly if optional power-management OIDs are enabled. Since RNDIS power-management behavior is historically underspecified, callers need conservative validation before trusting host-provided offsets and lengths.

## Test signals
Build coverage with RNDIS optional PM/wakeup configuration enabled is the main signal. Protocol tests should issue PnP and wakeup OIDs and confirm response sizes and endian layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/ndis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/rndis.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/rndis.c

## Purpose
This file implements the Remote NDIS message parser and response engine used by USB Ethernet gadget functions. It translates host RNDIS control messages into NDIS OID responses, updates network-device carrier/filter state, queues RNDIS responses for the USB notification/data path, and wraps or unwraps Ethernet SKBs with RNDIS packet headers.

## Important APIs, types, and functions
Public exported APIs include `rndis_register()`, `rndis_deregister()`, `rndis_set_param_dev()`, `rndis_set_param_vendor()`, `rndis_set_param_medium()`, `rndis_msg_parser()`, `rndis_get_next_response()`, `rndis_free_response()`, `rndis_add_hdr()`, `rndis_rm_hdr()`, `rndis_signal_connect()`, `rndis_signal_disconnect()`, `rndis_uninit()`, and `rndis_set_host_mac()`. Internally, `gen_ndis_query_resp()` handles supported OID queries, `gen_ndis_set_resp()` handles packet-filter and multicast-list sets, and message-specific helpers build INIT, QUERY, SET, RESET, KEEPALIVE, and status-indication responses.

## Control flow
An Ethernet function calls `rndis_register()` with a response-available callback, then sets netdev, vendor, medium, speed, filter, and host MAC parameters. Host control messages enter `rndis_msg_parser()`, which reads the unaligned little-endian message type and length, updates `params->state` for INIT/HALT, and dispatches to response builders. Response builders allocate `rndis_resp_t` entries with `rndis_add_response()`, fill little-endian message structures, and invoke `params->resp_avail()`. The USB function later drains unsent responses with `rndis_get_next_response()` and releases them with `rndis_free_response()`. Data TX uses `rndis_add_hdr()`; RX uses `rndis_rm_hdr()` to strip the RNDIS packet message and queue the Ethernet SKB.

## State and persistence
`struct rndis_params` contains the per-instance state: allocated config number, RNDIS state machine value, saved packet filter pointer, media state, medium/speed, host MAC pointer, netdev pointer, vendor metadata, callback context, and a spinlock-protected response queue. IDs are allocated from a process-wide IDA up to 999. Optional debug proc entries expose and mutate link state. No state persists beyond the registered object lifetime.

## Dependencies and integration points
The code depends on Linux netdevice APIs, SKB helpers, procfs debug support, RNDIS protocol constants from `<linux/rndis.h>`, local `rndis.h`, and `u_rndis.h`. It integrates with the USB Ethernet function through exported symbols and the `gether` receive path. Packet-filter SET has side effects on `netif_carrier_*()` and `netif_{wake,stop}_queue()`.

## Risks and edge cases
RNDIS host input is untrusted. Some query debug dumping reads 16-byte chunks from the provided buffer without checking that the final chunk is complete when debugging is enabled. `rndis_msg_parser()` reads message headers before validating `MsgLength` against the actual control request length, so callers must pass a sufficiently sized buffer. Response queue entries are heap-allocated with GFP_ATOMIC and must be freed by the caller after transmission. `rndis_rm_hdr()` validates packet type and pull length but does not use the `port` argument. State transitions are host-driven and Windows-specific behavior is explicitly accommodated.

## Test signals
Protocol tests should cover INIT, QUERY for every supported OID, unsupported OID status, SET packet filter on/off and resulting netdev queue/carrier state, RESET queue drain, KEEPALIVE, HALT, connect/disconnect indications, response queue ordering and freeing, SKB header add/remove round trips, malformed packet headers, and optional procfs debug commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/rndis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/rndis.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/rndis.h

## Purpose
This header defines RNDIS message layouts, per-instance state, response queue records, and exported function prototypes for the USB gadget RNDIS implementation. It is the contract between `rndis.c` and USB Ethernet function code.

## Important APIs, types, and functions
Wire-format typedefs cover INIT, HALT, QUERY, SET, RESET, INDICATE_STATUS, KEEPALIVE, packet, and configuration-parameter messages. `struct rndis_packet_msg_type` is packed and used as the data-plane header. `enum rndis_state` models uninitialized, initialized, and data-initialized states. `rndis_resp_t` stores queued control responses. `rndis_params` stores netdev, filter, state, medium/speed, media state, host MAC, vendor metadata, response callback, callback context, and a spinlock-protected response list. Prototypes expose registration, parser, parameter setters, response draining, header conversion, state signals, and host MAC update.

## Control flow
Consumers allocate a `rndis_params` with `rndis_register()`, provide the netdev/filter and metadata, feed EP0 control payloads into `rndis_msg_parser()`, transmit queued responses obtained from `rndis_get_next_response()`, and release them with `rndis_free_response()`. Data packets are converted through `rndis_add_hdr()` and `rndis_rm_hdr()`.

## State and persistence
All state is per registered `rndis_params`. The response queue is protected by `resp_lock`; the packet filter pointer is supplied by the CDC/RNDIS Ethernet function and is updated by SET OID handling. There is no persistent storage.

## Dependencies and integration points
The header includes `<linux/rndis.h>` for constants, `u_ether.h` for `struct gether`, and `ndis.h` for NDIS PM structures. It exports the API shape that `f_rndis`/Ethernet gadget code relies on.

## Risks and edge cases
Wire structures use little-endian fields and fixed offsets; changes must preserve RNDIS host ABI. `rndis_params` contains raw pointers to netdev, filter, host MAC, and vendor description, so lifetime must be managed by the caller. The packed packet header must remain layout-compatible with host RNDIS framing.

## Test signals
Build all RNDIS gadget functions, verify structure sizes and offsets used by protocol tests, run RNDIS enumeration with a host, exercise response queue APIs, and validate SKB header conversion against known packet captures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/rndis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/storage_common.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/storage_common.c

## Purpose
This file provides shared descriptors and logical-unit helper functions for USB mass-storage gadget functions. It centralizes FS/HS/SS bulk endpoint descriptors, interface descriptors, backing-file open/close logic, CD-ROM address formatting, and configfs/sysfs show/store helpers for LUN attributes.

## Important APIs, types, and functions
Exported descriptor objects include `fsg_intf_desc`, FS/HS/SS bulk IN and OUT endpoint descriptors, SuperSpeed companion descriptors, and descriptor arrays. `fsg_lun_open()` opens and validates a file or block device as LUN backing storage, sets block size and sector counts, handles CD-ROM minimum/maximum sizing, and updates read-only state. `fsg_lun_close()` releases the backing file. `fsg_lun_fsync_sub()` flushes writable media. Attribute helpers include `fsg_show_ro()`, `fsg_store_ro()`, `fsg_show_file()`, `fsg_store_file()`, `fsg_store_cdrom()`, `fsg_store_removable()`, `fsg_store_nofua()`, `fsg_store_inquiry_string()`, and `fsg_store_forced_eject()`.

## Control flow
Mass-storage functions import and patch shared descriptors during their bind paths, typically assigning endpoint addresses after autoconfiguration. LUN file changes flow through `fsg_store_file()`: prevent removal is checked, a trailing newline is stripped in place, `filesem` is taken for writing, and the helper either opens a new medium or closes the existing one while setting unit-attention sense data. `fsg_lun_open()` tries read-write first unless initially read-only, falls back to read-only on access/EROFS failures, validates regular or block devices, checks readability/writability, computes logical block size, enforces CD-ROM constraints, closes any prior medium, and installs the new file.

## State and persistence
The function mutates `struct fsg_lun`: backing `filp`, file length, sector count, `ro`, `initially_ro`, removable/CD-ROM flags, no-FUA flag, sense data, block size fields, and inquiry string. Backing files are persistent external objects, but the gadget stores only open file references and in-memory LUN state. Caller-provided `filesem` protects media changes and path display.

## Dependencies and integration points
The file depends on block device, VFS, USB composite, SCSI/storage constants, and `storage_common.h`. It exports symbols to mass-storage function implementations such as file-backed mass storage and related composite functions. It uses Linux VFS helpers like `filp_open()`, `fput()`, `i_size_read()`, `file_path()`, and `vfs_fsync()`.

## Risks and edge cases
`fsg_store_file()` casts away const and edits the input buffer to strip a newline, which assumes the caller supplies mutable sysfs/configfs storage. Read-only changes are rejected while media is open, but CD-ROM store uses a read lock while calling the same helper. Opening block devices depends on logical block-size reporting and size alignment. Forced eject clears `prevent_medium_removal` and detaches media regardless of host state, intentionally bypassing normal SCSI removal protection.

## Test signals
Test descriptor export consumers at FS/HS/SS, open regular files and block devices read-write and read-only, fallback on EROFS/EACCES, too-small and too-large CD-ROM images, ro/cdrom/removable/nofua attribute transitions, forced eject while prevented, path display for open and empty media, inquiry string formatting, and fsync behavior when toggling no-FUA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/storage_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/storage_common.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/storage_common.h

## Purpose
This header defines shared USB mass-storage gadget data structures, constants, descriptors, logging helpers, SCSI sense constants, and exported helper prototypes. It is the common contract for mass-storage function implementations that share LUN and descriptor handling.

## Important APIs, types, and functions
`struct fsg_lun` stores backing file state, sector geometry, flags, sense data, device object, names, and inquiry string. `struct fsg_buffhd` models a pipeline buffer with IN/OUT USB requests and buffer state. `enum fsg_buffer_state`, `enum fsg_state`, and `enum data_direction` describe transport and command-processing state used by mass-storage engines. Macros define `FSG_BUFLEN`, `FSG_MAX_LUNS`, command size, sense-code helpers, and inquiry string length. Extern declarations expose the shared descriptors and all LUN show/store/open/close helpers.

## Control flow
The header has no executable flow, but it shapes mass-storage command loops. Implementations use `fsg_buffhd` rings to receive CBWs, transfer data, and send CSWs; use `fsg_state` to handle resets, aborts, config changes, and exits; and call the LUN helpers to manage backing media under their own locks.

## State and persistence
State is in `struct fsg_lun` and buffer heads owned by including modules. The header documents fields that persist for the lifetime of a configured LUN, including open file references, media geometry, sense/unit attention data, and user-visible strings. Debug macros conditionally emit per-LUN messages.

## Dependencies and integration points
The header includes Linux device, USB storage, SCSI, and unaligned-access definitions. It integrates with the composite framework through descriptor externs and with SCSI command processing through sense constants and CDB sizes. `fsg_lun_from_dev()` maps device objects back to LUNs for sysfs callbacks.

## Risks and edge cases
Callers must respect locking around `fsg_lun` media fields and not dereference `filp` without checking `fsg_lun_is_open()`. Sense constants are packed integers interpreted by helper macros, so additions must preserve the SK/ASC/ASCQ encoding. Buffer state values include negative in-flight states, which can be mishandled if treated as booleans.

## Test signals
Compile all mass-storage functions, exercise LUN sysfs/configfs callbacks, run SCSI command tests for sense reporting, stress buffer state transitions under reset/disconnect, and validate FS/HS/SS descriptor consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/storage_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/tcm.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/tcm.h

## Purpose
This header defines the shared state for the USB gadget target-core fabric function, supporting USB Attached SCSI Protocol (UASP) and Bulk-Only Transport (BOT) modes. It connects USB composite function state to Linux target-core sessions, portal groups, command objects, streams, and endpoint resources.

## Important APIs, types, and functions
`struct tcm_usbg_nexus` holds the target-core session. `struct usbg_tpg` represents a target portal group with mutex, tag, target port pointer, workqueue, `se_portal_group`, connection flag, nexus, port count, and function instance. `struct usbg_tport` stores WWPN identity and `se_wwn`. `struct usbg_cmd` combines USB command metadata, target-core `se_cmd`, work item, request pointer, data buffer, reference count, UAS IU fields, task-management fields, and BOT CSW fields. `struct uas_stream` groups per-stream IN/OUT/status requests and completion/hash linkage. `struct f_uas` embeds `struct usb_function`, endpoint pointers, UAS streams/hash, BOT status, and BOT request state.

## Control flow
The header has no executable flow, but it defines how implementation files manage commands: BOT and UAS requests are converted into `usbg_cmd`, queued to target-core through `se_cmd`, processed on a workqueue, and completed through endpoint-specific requests. UAS mode uses stream IDs and a hash table; BOT mode uses a single command/status flow and flags such as `USBG_BOT_CMD_PEND` and `USBG_BOT_WEDGED`.

## State and persistence
Runtime state spans target portal groups, sessions, command objects, request objects, stream completions, endpoint pointers, and function flags. No durable persistence is defined here; identity such as WWPN lives in memory and is tied to target-core configuration.

## Dependencies and integration points
The header depends on USB composite, UAS and USB storage protocol definitions, Linux target-core base/fabric APIs, krefs, hash tables, workqueues, and completions. `fuas_to_gadget()` links `struct f_uas` back to the active USB gadget. The structures are consumed by the TCM USB gadget function implementation.

## Risks and edge cases
Command lifetime is reference-counted and crosses USB completion, workqueue, and target-core completion contexts, so leaks and use-after-free are primary risks. Stream counts derive from SuperSpeed companion stream settings. BOT and UAS share `f_uas` but have different flags and endpoint assumptions, so mode transitions must reset the correct state. Fixed command buffer size `USBG_MAX_CMD` must be respected when unpacking CDBs.

## Test signals
Build the TCM USB gadget function, enumerate BOT and UAS altsettings, run SCSI I/O and task-management commands, stress disconnect during outstanding commands, test stream allocation and hash lookup, validate BOT wedge/error handling, and run target-core session teardown tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/tcm.h -->
