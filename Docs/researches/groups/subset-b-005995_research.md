# subset-b-005995 Research

Grouped research for the listed Ceph client UAPI headers. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/userio.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/userio.h

## Purpose
Defines the userspace ABI for the `userio` virtual serio device. Applications write compact commands to `/dev/userio` to register a userspace-backed serio port, set the port type, and inject interrupt data.

## Important APIs, Types, And Constants
The exported command namespace is `enum userio_cmd_type`: `USERIO_CMD_REGISTER`, `USERIO_CMD_SET_PORT_TYPE`, and `USERIO_CMD_SEND_INTERRUPT`. `struct userio_cmd` is a two-byte packed command envelope with `type` and `data`; the header explicitly uses packed layout to keep the ABI identical across architectures. It depends only on `<linux/types.h>` for fixed-width `__u8`.

## Control Flow, State, And Persistence
The header has no executable flow, but it describes the control sequence expected by the driver: userspace sends `struct userio_cmd` records to the character device, the driver interprets `type`, and `data` carries the optional argument. Kernel-side state lives in the userio driver and serio subsystem, not in this header; persistence lasts for the device/session lifetime.

## Dependencies And Integration Points
Integrates with Linux input/serio plumbing through `/dev/userio`. Consumers must include this header when building tools that emulate serio devices or send synthetic input interrupts.

## Risks And Test Signals
ABI risk is high for struct packing and command values because userspace and kernel exchange raw bytes. Tests should cover command size (`sizeof(struct userio_cmd) == 2`), valid command dispatch, malformed command rejection, and end-to-end registration plus interrupt delivery through the serio/input stack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/userio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/utime.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/utime.h

## Purpose
Provides the legacy userspace `struct utimbuf` definition used by `utime(2)`-style file timestamp updates.

## Important APIs, Types, And Constants
The single ABI type is `struct utimbuf`, with `actime` and `modtime` fields of type `__kernel_old_time_t`. It includes `<linux/types.h>` and intentionally uses the old kernel time type rather than `time64` types for compatibility with the historical syscall interface.

## Control Flow, State, And Persistence
No code executes here. User programs pass the struct to timestamp-setting syscalls; the filesystem persists the resulting access and modification times in inode metadata. The header itself does not define validation, conversion, or timezone behavior.

## Dependencies And Integration Points
Used by libc/kernel UAPI consumers that need the raw Linux layout for `utime`. Filesystems, VFS timestamp conversion, and architecture syscall wrappers are the runtime integration points.

## Risks And Test Signals
The main risk is time-width compatibility, especially on 32-bit ABIs where `__kernel_old_time_t` can truncate modern timestamps. Test signals include ABI size/layout checks, syscall tests around epoch boundaries, negative values where supported, and filesystem round trips verifying `atime` and `mtime`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/utime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/utsname.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/utsname.h

## Purpose
Defines historical and current UTS name structures returned by Linux uname-related syscalls. It preserves fixed-size buffers for system name, node name, release, version, machine, and domain name.

## Important APIs, Types, And Constants
`__OLD_UTS_LEN` is 8 and backs `struct oldold_utsname`, which stores five 9-byte strings. `__NEW_UTS_LEN` is 64 and backs `struct old_utsname` and `struct new_utsname`, both using 65-byte null-terminated fields; `new_utsname` adds `domainname`. These are plain char-array ABI structs.

## Control Flow, State, And Persistence
The header contains no logic. Kernel uname handlers copy current UTS namespace values into these layouts. State is owned by the kernel UTS namespace; host/container namespace changes affect future syscall results, but the structs themselves are transient copy-out buffers.

## Dependencies And Integration Points
Integrated with `uname`, older uname variants, libc wrappers, and namespace code. The fixed lengths are part of the syscall ABI and cannot be changed without breaking applications.

## Risks And Test Signals
Risks include truncation, missing NUL termination, and accidentally mixing old/new layouts. Tests should validate field sizes, namespace-specific values, truncation behavior for long hostnames/domain names, and compatibility syscall paths on architectures that expose older structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/utsname.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/uuid.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/uuid.h

## Purpose
Compatibility forwarding header for UUID definitions. It delegates to `<linux/mei_uuid.h>`.

## Important APIs, Types, And Constants
This file declares no local symbols. Its API surface is whatever `linux/mei_uuid.h` exports to consumers that historically include `linux/uuid.h` from this source tree.

## Control Flow, State, And Persistence
There is no control flow or state. Inclusion simply redirects compile-time type and macro availability.

## Dependencies And Integration Points
The direct dependency is `linux/mei_uuid.h`, so build success depends on that header remaining present and suitable for UAPI inclusion. Consumers relying on this include path are integrated through the preprocessor rather than runtime code.

## Risks And Test Signals
Risk is mostly header drift: if `mei_uuid.h` changes scope or disappears, `linux/uuid.h` consumers fail. Test signals are compile-only checks for representative userspace includes and ABI checks for UUID type names supplied by the included header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/uuid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/uvcvideo.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/uvcvideo.h

## Purpose
Defines userspace controls for USB Video Class devices, especially dynamic extension unit controls and UVC metadata buffers.

## Important APIs, Types, And Constants
Control data type constants classify raw, signed, unsigned, boolean, enum, bitmask, and rectangle payloads. `UVC_CTRL_FLAG_*` describes supported GET/SET operations, suspend/resume restore, device auto-update, and asynchronous reporting; `UVC_CTRL_FLAG_GET_RANGE` combines the standard range queries. UVC-specific V4L2 controls define region-of-interest rectangle and automation bitmasks under `V4L2_CID_USER_UVC_BASE`. `struct uvc_menu_info` stores menu entries. `struct uvc_xu_control_mapping` maps a UVC extension unit selector to a V4L2 control id/type/data type and optional userspace menu array. `struct uvc_xu_control_query` describes raw UVC class-specific control requests. `UVCIOC_CTRL_MAP` and `UVCIOC_CTRL_QUERY` are the ioctl entry points. `struct uvc_meta_buf` is a packed variable-length metadata record with driver timestamp, USB SOF, payload length/flags, and copied UVC header bytes.

## Control Flow, State, And Persistence
Userspace maps extension-unit controls through `UVCIOC_CTRL_MAP`, then issues queries through `UVCIOC_CTRL_QUERY` or normal V4L2 control paths. Driver state includes registered mappings, current camera control values, and metadata queue buffers. Some control values are explicitly marked restorable across suspend/resume, but persistent storage belongs to the driver/device, not this header.

## Dependencies And Integration Points
Depends on `<linux/ioctl.h>` and `<linux/types.h>`, plus V4L2 control IDs from the broader media API. Integrates with UVC USB descriptors, V4L2 control handling, video node metadata queues, and applications such as camera control tools.

## Risks And Test Signals
Pointer fields marked `__user` and variable metadata records require careful size and bounds validation. Extension-unit mappings can expose vendor controls incorrectly if `size`, `offset`, `selector`, or data type are wrong. Tests should cover ioctl ABI sizes, mapping invalid selectors, menu-count bounds, GET/SET request paths, suspend restore behavior, and metadata buffer parsing with multiple complete records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/uvcvideo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-common.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-common.h

## Purpose
Provides V4L2 definitions shared by full video nodes and sub-device nodes. It centralizes selection target/flag values and EDID exchange layout.

## Important APIs, Types, And Constants
Selection targets cover current/default/bounds crop rectangles, native frame size, current/default/bounds compose rectangles, and padded compose area. Selection flags express greater-or-equal, less-or-equal, and keep-existing-configuration constraints. `struct v4l2_edid` carries a pad, start block, block count, reserved words, and an EDID pointer. Userspace-only backward compatibility aliases map obsolete subdev names to the common selection constants.

## Control Flow, State, And Persistence
No code runs in the header. The constants steer ioctl handlers such as selection and EDID get/set operations. Active crop/compose/EDID state belongs to media drivers and hardware; try-state may be held transiently during format negotiation.

## Dependencies And Integration Points
Depends on `<linux/types.h>`. It is intended to be included indirectly through `videodev2.h` or `v4l2-subdev.h`, and it is consumed by V4L2 applications, bridge drivers, camera sensor drivers, and display receiver/transmitter drivers.

## Risks And Test Signals
Risks center on selection target mismatch between video-node and subdev paths and unsafe EDID pointer/length handling. Tests should query/set each selection target, verify `KEEP_CONFIG` behavior, exercise EDID block ranges, and compile userspace with deprecated aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-controls.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-controls.h

## Purpose
Defines the Video4Linux2 control ID namespace, enum values, and compound control payloads. It is the core userspace ABI for configuring video, camera, radio, codec, detection, colorimetry, and stateless codec devices through V4L2 controls.

## Important APIs, Types, And Constants
The file partitions control IDs by class: user, stateful codec, camera, FM TX/RX, flash, JPEG, image source, image processing, digital video, RF tuner, detection, stateless codec, and colorimetry. The user class covers classic image/audio controls such as brightness, contrast, saturation, hue, white balance, gain, flip, power-line frequency, color effects, rotation, alpha, and minimum buffer requirements. Private user bases reserve ranges for specific drivers including bttv, UVC, Rockchip ISP1, and Mali-C55.

Codec controls include MPEG stream/audio/video settings, H.263/H.264/MPEG4/VP8/VP9/HEVC/AV1 profile and level enums, bitrate/rate-control settings, GOP and slice settings, QP controls, and legacy hardware-specific CX2341X/MFC51 ranges. Camera controls include exposure mode, pan/tilt/zoom/focus/iris, 3A lock flags, autofocus status/range, orientation, sensor rotation, and HDR sensor mode. Other classes define RDS modulation/reception, flash modes/faults/intensity, JPEG markers, sensor blanking/gains/unit cell size, image processing link frequency/pixel rate/digital gain, DV TX/RX state, RF gain controls, motion detection grids, and HDR10 CLL/mastering display structs with explicit mastering range constants.

The dense stateless codec section exports compound structs for parser-provided decode metadata. H.264 structs include SPS, PPS, scaling matrices, prediction weights, references, slice params, DPB entries, and decode params. FWHT, VP8, MPEG-2, HEVC, VP9, and AV1 each provide parameter structs for sequence/frame headers, loop filters, segmentation, quantization, reference timestamps, tile info, global motion, restoration, film grain, and codec-specific flags. Many comments specify that reserved fields must be zeroed and that some controls are dynamic arrays.

## Control Flow, State, And Persistence
This header does not implement control handling; V4L2 core and drivers use the IDs and payload structs when userspace calls control ioctls. Stateful controls persist in driver/device control state until changed or reset. Stateless codec controls are per-request decode metadata attached to queued buffers; reference state is linked through V4L2 capture buffer timestamps. Dynamic-array controls, DPB arrays, and reference timestamps create the effective control flow for stateless decode: userspace parses bitstreams, fills controls, queues bitstream buffers, and hardware consumes metadata plus reference buffers.

## Dependencies And Integration Points
Depends on `<linux/const.h>` and `<linux/types.h>`, and is included by `videodev2.h`. It integrates with V4L2 control handler internals, media codecs, camera sensors, USB cameras, HDMI/DV receivers, radio devices, and userspace frameworks such as libcamera, GStreamer, FFmpeg, and V4L2 compliance tools.

## Risks And Test Signals
ABI risk is broad: numeric control IDs are stable, compound struct layout must not change, reserved fields must be zero, and userspace/kernel must agree on enum semantics. Stateless codecs are especially sensitive to malformed bitstream-derived values, stale reference timestamps, dynamic array length mismatches, and 32/64-bit layout assumptions. Test signals include `v4l2-compliance`, compile-time struct size checks, control enumeration/query tests, invalid enum/range rejection, per-codec conformance bitstreams, DPB/reference timestamp stress tests, and media framework interop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-controls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-dv-timings.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-dv-timings.h

## Purpose
Provides compile-time initializer macros for common digital video timings used by V4L2. The catalog covers CEA-861 HDTV/HDMI modes, VESA DMT/CVT monitor modes, and a small SDI timing.

## Important APIs, Types, And Constants
`V4L2_INIT_BT_TIMINGS` works around old GCC anonymous-union initializer behavior. Each `V4L2_DV_BT_*` macro expands to a `struct v4l2_dv_timings` initializer with type `V4L2_DV_BT_656_1120` and embedded BT timings: active width/height, interlace flag, sync polarities, pixel clock, horizontal/vertical porch/sync values, timing standards (`DMT`, `CEA861`, `CVT`, `SDI`), flags such as reduced blanking, half-line, CE video, aspect/VIC presence, CEA VIC, and HDMI VIC where applicable. Several DMT modes alias CEA definitions where standards overlap.

## Control Flow, State, And Persistence
No runtime logic exists. Drivers and helper tables include these macros to advertise, validate, or set DV timings. Device state is maintained by receivers/transmitters after timing negotiation; the header only supplies canonical presets.

## Dependencies And Integration Points
The macros require `struct v4l2_dv_timings` and related `V4L2_DV_*` constants from the broader V4L2 API. They integrate with HDMI/DVI/SDI receiver drivers, EDID/DV timing enumeration, and applications that select standard modes.

## Risks And Test Signals
Risks include incorrect pixel clocks, porch values, sync polarities, flags, or VIC numbers, which can break display lock or mode matching. Tests should compare preset values against CEA/DMT/SDI references, exercise driver timing enumeration, verify aliases, and perform hardware mode set/query round trips for common and edge modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-dv-timings.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-mediabus.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-mediabus.h

## Purpose
Defines the media-bus frame format structure used between V4L2 sub-devices and preserves deprecated media-bus pixel-code aliases for userspace compatibility.

## Important APIs, Types, And Constants
`V4L2_MBUS_FRAMEFMT_SET_CSC` marks colorspace conversion intent. `struct v4l2_mbus_framefmt` carries width, height, media-bus format code, field order, colorspace, either YCbCr or HSV encoding, quantization, transfer function, flags, and reserved words. For non-kernel users, frozen `enum v4l2_mbus_pixelcode` values are generated from `MEDIA_BUS_FMT_*` constants through `V4L2_MBUS_FROM_MEDIA_BUS_FMT`, covering fixed, RGB, YUV, Bayer, JPEG, and AHSV formats.

## Control Flow, State, And Persistence
No code runs here. Media pipeline negotiation passes this struct through subdev format ioctls; active format state is held per subdev pad/stream by drivers, while try formats are temporary negotiation state.

## Dependencies And Integration Points
Depends on `linux/media-bus-format.h`, `linux/types.h`, and `linux/videodev2.h`. It is consumed by `v4l2-subdev.h`, camera sensor/bridge drivers, ISP pipelines, and userspace graph managers.

## Risks And Test Signals
Risks include mixing deprecated `V4L2_MBUS_FMT_*` aliases with canonical `MEDIA_BUS_FMT_*`, failing to zero reserved fields, and inconsistent colorspace metadata across pipeline entities. Tests should enumerate supported bus codes, set/get pad formats, validate colorspace conversion flags, and compile old userspace using the deprecated enum names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-mediabus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-subdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-subdev.h

## Purpose
Defines the userspace ioctl ABI for V4L2 sub-device nodes. Subdevs expose pad-level media-bus formats, crop/selection, frame intervals, capabilities, routing, stream-aware client capabilities, EDID/std/DV timing ioctls, and compatibility aliases.

## Important APIs, Types, And Constants
`enum v4l2_subdev_format_whence` selects try versus active configuration. Format, crop, media-bus-code enumeration, frame-size enumeration, frame interval, frame-interval enumeration, and selection structs all carry pad/index/code/dimensions plus stream fields and reserved arrays. Capability bits report read-only subdevs and stream/routing support. `struct v4l2_subdev_route` and `struct v4l2_subdev_routing` describe sink-to-source pad/stream routes; `V4L2_SUBDEV_ROUTE_FL_ACTIVE` marks active routes. Client capability bits opt userspace into stream fields and interval `which` semantics. The `VIDIOC_SUBDEV_*` ioctl macros define querycap, get/set format, intervals, crop, selection, routing, client caps, EDID, standards, and DV timing operations.

## Control Flow, State, And Persistence
Applications enumerate formats and frame sizes, negotiate try formats, commit active formats/selections, configure routing, and then video-node streaming uses those active routes. The kernel may force stream fields to zero unless the client advertises stream awareness. Persistent runtime state is per-subdev active configuration and route tables; try state is negotiation-scoped.

## Dependencies And Integration Points
Depends on `<linux/const.h>`, `<linux/ioctl.h>`, `<linux/types.h>`, `v4l2-common.h`, and `v4l2-mediabus.h`. It integrates with the media controller API, camera sensors, bridges, multiplexed streams, V4L2 video nodes, EDID/DV timing helpers, and userspace managers such as libcamera.

## Risks And Test Signals
Risks include unzeroed reserved fields, client capability mismatches that silently collapse streams to zero, route array length/`num_routes` truncation, obsolete crop API use, and inconsistent active configuration across linked pads. Tests should run `v4l2-compliance`, enumerate and set try/active formats, route multi-stream topologies, verify read-only capability behavior, and exercise EDID/DV timing passthrough.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-subdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vbox_err.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vbox_err.h

## Purpose
Publishes VirtualBox status and error code constants used by the Linux VBoxGuest UAPI and related VirtualBox guest/host communication.

## Important APIs, Types, And Constants
`VINF_SUCCESS` is zero and errors are negative `VERR_*` values. The list covers generic validation, memory, state, file/path, network/socket, resource, I/O, pipe, semaphore/deadlock, executable format, and HGCM async status (`VINF_HGCM_ASYNC_EXECUTE`). The header declares no structs or functions.

## Control Flow, State, And Persistence
The constants are returned through other ABIs such as `struct vbg_ioctl_hdr.rc`. They do not control flow by themselves, but callers branch on these numeric results after ioctl or VMMDev operations. No state or persistence is defined here.

## Dependencies And Integration Points
Included by `vboxguest.h` and expected by userspace components that speak VirtualBox guest additions protocols. The numeric values must match the VirtualBox host/VMM definitions.

## Risks And Test Signals
Risks are numeric drift and incorrect translation to Linux `errno`, especially when the VBox status is returned alongside ioctl-level errors. Tests should verify representative host requests return expected `VINF_`/`VERR_` values, map status to user-visible errors consistently, and compile all VBoxGuest headers together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vbox_err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vbox_vmmdev_types.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vbox_vmmdev_types.h

## Purpose
Defines VirtualBox VMMDev request and HGCM data structures shared by the VBoxGuest ioctl interface and other guest components such as shared folders.

## Important APIs, Types, And Constants
`VMMDEV_ASSERT_SIZE` enforces ABI struct sizes through typedefs. `enum vmmdev_request_type` enumerates VMMDev operations for mouse, host version/time, hypervisor info, guest info/capabilities/status, display changes, HGCM connect/disconnect/call/cancel, video acceleration, credentials, stats, memory ballooning, CPU hotplug, shared modules, page sharing, coredump, heartbeat, and monitor positions. `VMMDEVREQ_HGCM_CALL` selects 32-bit or 64-bit call type based on `__BITS_PER_LONG`.

Requestor flags classify user, mode, console association, VirtualBox group membership, Windows trust level, and less-trusted user device node. HGCM service location types and `struct vmmdev_hgcm_service_location` describe localhost services by fixed 128-byte name. HGCM parameter types cover 32-bit/64-bit values, linear address buffers, kernel buffers, and pagelists. Separate packed 32-bit and 64-bit function parameter structs preserve pointer-size-specific layout. `struct vmmdev_hgcm_pagelist` describes locked pages with direction flags, first-page offset, page count, and flexible page-address array.

## Control Flow, State, And Persistence
VBoxGuest builds request headers and payloads using these definitions, sends them to the VMMDev host interface, and receives status/data back. HGCM calls marshal typed parameters and optional page lists to host services. State lives in host sessions, HGCM client IDs, guest capabilities, and pinned pages; the header supplies only the wire layout.

## Dependencies And Integration Points
Depends on `<asm/bitsperlong.h>` and `<linux/types.h>`. It integrates with `vboxguest.h`, VirtualBox host services, vboxsf, display/mouse integration, memory ballooning, and guest additions daemons.

## Risks And Test Signals
Risks include packed 32/64-bit layout mismatches, incorrect request type selection, unsafe userspace pointer/page-list handling, stale request IDs versus host support, and nonzero reserved fields. Tests should compile on 32-bit and 64-bit targets, verify `VMMDEV_ASSERT_SIZE` expectations, perform HGCM connect/call/disconnect with scalar and buffer parameters, and fuzz malformed parameter types/counts/page-list offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vbox_vmmdev_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vboxguest.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vboxguest.h

## Purpose
Defines the Linux VBoxGuest character-device ioctl ABI. Userspace uses it to negotiate driver version, submit VMMDev requests, connect and call HGCM services, log messages, wait for guest events, change event filters and capabilities, handle memory ballooning, and request core dumps.

## Important APIs, Types, And Constants
`struct vbg_ioctl_hdr` is the common 24-byte header with input/output sizes, version, request type, VBox status code, output size, and reserved field. `VBG_IOC_VERSION` identifies the ioctl interface version. `struct vbg_ioctl_driver_version_info` negotiates session and driver versions. VMMDev request ioctls include a size-parameterized small request and `VBG_IOCTL_VMMDEV_REQUEST_BIG` for larger requests. HGCM structs cover connect, disconnect, and variable-length calls with client id, function, timeout, interruptible flag, and parameter count; 32/64-bit ioctl selectors follow pointer width. Other structs cover logging, event waits, filter changes, guest capability acquisition/change, balloon checks, and core dump requests.

## Control Flow, State, And Persistence
Typical userspace flow opens the VBoxGuest node, negotiates version, optionally connects to an HGCM service, issues calls or waits for events, updates filters/capabilities, and closes the session. Driver/session state includes negotiated interface version, HGCM client IDs, event wait cancellation state, per-session/global capability masks, and memory balloon requests. Some operations are handled entirely by the guest driver; VMMDev and HGCM requests cross to the host.

## Dependencies And Integration Points
Depends on `<asm/bitsperlong.h>`, `<linux/ioctl.h>`, `vbox_err.h`, and `vbox_vmmdev_types.h`. It integrates with `/dev/vboxguest` or related nodes, VirtualBox host services, guest additions daemons, vboxsf, display integration, and memory ballooning helpers.

## Risks And Test Signals
Risks include trusting user-supplied sizes, 32/64-bit HGCM parameter mismatch, incorrect `size_in`/`size_out` handling, stale session version fallback, blocked event waits after interruption, and host-returned VBox status being confused with ioctl `errno`. Tests should cover version negotiation, ioctl size validation, HGCM scalar/buffer calls on 32- and 64-bit userspace, wait cancellation, capability masks, balloon check handling, and status-code propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vboxguest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vdpa.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vdpa.h

## Purpose
Defines the generic netlink userspace ABI for vDPA device management.

## Important APIs, Types, And Constants
`VDPA_GENL_NAME` is `"vdpa"` and `VDPA_GENL_VERSION` is `0x1`. `enum vdpa_command` covers management-device discovery, vDPA device create/delete/get, configuration dump, virtqueue stats, and device attribute setting. `enum vdpa_attr` defines netlink attributes for management device bus/name/supported classes; vDPA device name, id, vendor id, queue counts and sizes; virtio-net config (MAC, status, queue pairs, MTU); negotiated/supported/provisioned features; per-queue index; vendor attributes; and virtio-blk configuration fields including capacity, block size, segments, queue count, discard/write-zeroes limits, read-only, and flush flags.

## Control Flow, State, And Persistence
Userspace sends generic netlink commands to list management devices, create vDPA devices under a management device, inspect config/stats, set selected attributes, and delete devices. Persistent state is kernel vDPA device registration and driver-backed configuration; netlink messages are transient.

## Dependencies And Integration Points
This header has no includes because it is constants-only. It integrates with the kernel vDPA subsystem, virtio device classes, vdpa tooling, management drivers such as hardware accelerators or software backends, and netlink libraries.

## Risks And Test Signals
Risks include attribute type/width mismatches, missing 64-bit alignment padding for u64 attributes, feature negotiation inconsistencies, and tool/kernel skew when new attributes are added before `VDPA_ATTR_MAX`. Tests should exercise netlink policy validation, dump/create/delete flows, feature provisioning, queue stats, and virtio-net/blk config reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vdpa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vduse.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vduse.h

## Purpose
Defines the ioctl and read/write control-message ABI for VDUSE, which lets userspace implement virtio devices and attach them through the vDPA infrastructure.

## Important APIs, Types, And Constants
`VDUSE_BASE` selects the ioctl type. API versions `0` and `1` distinguish base support from virtqueue groups and address-space IDs. Control-device ioctls get/set API version and create/destroy named devices. `struct vduse_dev_config` describes device name, virtio vendor/device ids, features, virtqueue count/alignment, optional group and ASID counts, config-space size, and variable config bytes.

Device ioctls manage IOTLB and virtqueue state. IOTLB structs describe IOVA ranges, mmap offsets, permissions, userspace memory registrations, capabilities, and v2 ASID-aware variants. Feature/config ioctls get negotiated features, update config space, and inject config interrupts. Virtqueue structs configure queue index, max size, group, split/packed state, descriptor/driver/device addresses, readiness, kick eventfds, and queue interrupt injection. Read/write control messages use `enum vduse_req_type` and request/response structs for getting vq state, setting virtio status, updating IOTLB ranges, and setting vq group ASIDs.

## Control Flow, State, And Persistence
Userspace first negotiates API version on `/dev/vduse/control`, creates a device, opens `/dev/vduse/$NAME`, sets up queues and IOTLB mappings, attaches through vDPA, then services kernel requests read from the device node and writes responses. Persistent runtime state includes created VDUSE devices, virtqueue configuration/readiness, eventfd bindings, IOVA mappings, negotiated features, config space, device status, and per-group ASIDs until destroyed or closed.

## Dependencies And Integration Points
Depends on `<linux/types.h>` and ioctl macros via normal UAPI context. It integrates with virtio drivers, vDPA bus attachment, eventfd notification, mmap/file-descriptor based IOVA access, userspace device emulators, and IOMMU/IOTLB update flows.

## Risks And Test Signals
Risks include unvalidated flexible-array sizes, page-alignment errors, IOVA overlap/ASID mistakes, stale eventfds, incorrect split versus packed queue state, request/response ID mismatches, and failure to zero reserved fields for forward compatibility. Tests should cover API negotiation, create/destroy lifetime, queue setup before attachment, IOTLB register/deregister/get-fd paths, ASID-aware v2 paths, config IRQ injection, vq kick/irq eventfds, and read/write request handling under malformed inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vduse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vesa.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vesa.h

## Purpose
Defines VESA display blanking/power-management mode values for userspace-facing video APIs.

## Important APIs, Types, And Constants
`enum vesa_blank_mode` exposes `VESA_NO_BLANKING`, `VESA_VSYNC_SUSPEND`, `VESA_HSYNC_SUSPEND`, `VESA_POWERDOWN` as the OR of vsync and hsync suspend, and `VESA_BLANK_MAX`. The header also defines same-named preprocessor aliases for compatibility with code expecting macros.

## Control Flow, State, And Persistence
There is no executable code. Userspace or framebuffer/video drivers pass these values to blanking paths; hardware state changes to no blanking, sync suspend, or powerdown until another mode is set.

## Dependencies And Integration Points
The header is standalone. It integrates with display/framebuffer/video blanking controls and legacy tools that use VESA DPMS-style values.

## Risks And Test Signals
Risks are limited but include enum/macro name collisions and drivers interpreting powerdown bits inconsistently. Tests should compile consumers with both enum and macro references, set each blanking mode on a supported device, and verify display power/sync behavior or driver state reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vesa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/veth.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/veth.h

## Purpose
Defines netlink attribute IDs for virtual Ethernet pair information.

## Important APIs, Types, And Constants
The anonymous enum exposes `VETH_INFO_UNSPEC`, `VETH_INFO_PEER`, and `__VETH_INFO_MAX`; `VETH_INFO_MAX` is `__VETH_INFO_MAX - 1`. `VETH_INFO_PEER` identifies nested peer link information in rtnetlink messages.

## Control Flow, State, And Persistence
No code runs here. During veth creation or inspection, rtnetlink messages use these attributes to describe the peer endpoint. Persistent state is the kernel network-device pair and its namespace placement, not the header.

## Dependencies And Integration Points
The header is standalone and integrates with rtnetlink, `ip link add type veth`, container/network namespace setup tools, and kernel veth driver attributes.

## Risks And Test Signals
Risks include netlink attribute policy drift and incorrect nested peer parsing by userspace. Tests should create veth pairs with peer attributes, move peers across namespaces, dump link info, and verify `VETH_INFO_MAX` bounds in netlink policy and userspace decoders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/veth.h -->
