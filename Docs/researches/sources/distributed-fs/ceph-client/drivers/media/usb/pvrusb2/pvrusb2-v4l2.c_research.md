## sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-v4l2.c

### Purpose
`pvrusb2-v4l2.c` exposes the pvrusb2 hardware/context layer as V4L2 video and radio device nodes. It translates V4L2 file operations and ioctls into pvrusb2 channel claims, hardware controls, MPEG stream reads, tuner/input changes, crop/selection controls, and device registration/lifetime management.

### Important APIs, Types, And Functions
The local `struct pvr2_v4l2` owns the parent channel and registered video/radio devices. `struct pvr2_v4l2_dev` embeds `struct video_device` first and records stream configuration, VFL type, and pvrusb2 minor type. `struct pvr2_v4l2_fh` wraps `v4l2_fh`, a per-open `pvr2_channel`, lazy `pvr2_ioread`, wait queue, firmware-read mode flag, and an input ordinal map. Main functions are `pvr2_v4l2_create()`, `pvr2_v4l2_dev_init()`, `pvr2_v4l2_open()`, `pvr2_v4l2_release()`, `pvr2_v4l2_read()`, `pvr2_v4l2_poll()`, and the `pvr2_ioctl_ops` handlers.

### Control Flow
Creation initializes a pvrusb2 channel, registers a video node, and registers a radio node only when radio input is available. Open validates hardware readiness, initializes a file handle, limits inputs by node type, builds a compact V4L2 input index to pvrusb2 input-id map, and records whether CPU firmware readback mode is active. `read()` either reads firmware bytes by offset or lazily claims the stream, creates an MPEG ioread object, installs a stream callback, sets the pvrusb2 stream type, starts hardware streaming, and copies data to userspace. `poll()` performs the same lazy setup and waits on the per-file wait queue. Release stops streaming, clears callbacks, destroys ioread state, drops the channel, and triggers parent destruction if a disconnect already happened and no handles remain.

### State, Persistence, And Dependencies
State is in kernel memory: registered `video_device`s, channel ownership, input masks, module minor-number parameters, stream callbacks, and pvrusb2 hardware controls. Persistent user-visible effects are registered device nodes and stored minor numbers in the hardware layer. The file depends on `pvrusb2-context`, `pvrusb2-hdw`, `pvrusb2-ctrl`, `pvrusb2-ioread`, V4L2 core, and pvrusb2 tracing.

### Integration Points
V4L2 ioctls call pvrusb2 control helpers for standard, input, audio, tuner, frequency, MPEG format, crop/selection, and extended controls. `video_register_device()` integrates with V4L2 device-node creation. Stream ownership integrates with `pvr2_context_stream` and the lower `pvr2_stream` callback path.

### Risks
Lifetime is subtle around disconnect: parent device pointers are disassociated, but destruction waits for open file handles. `pvr2_v4l2_internal_check()` dereferences `vp->dev_video` and conditionally `dev_radio`, so registration failure paths and partial teardown need care. Control setters commonly commit even after partial failures, which may leave hardware in a partially updated state. Read-mode stream claims must be released on every setup failure to avoid blocking other consumers.

### Test Signals
Useful signals include opening video and radio nodes, enumerating and switching inputs, tuning TV/radio frequencies, reading MPEG data in blocking and nonblocking modes, polling readiness, forcing disconnect while files are open, exercising firmware-read mode, and validating extended control query/get/set error indexes.
