# subset-b-004220 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-v4l2.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-v4l2.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-v4l2.h

### Purpose
`pvrusb2-v4l2.h` declares the internal V4L2 bridge constructor for the pvrusb2 driver.

### Important APIs, Types, And Functions
The header forward declares `struct pvr2_v4l2` and exposes `pvr2_v4l2_create(struct pvr2_context *)`. It includes `pvrusb2-context.h` because the constructor is tied to an existing pvrusb2 context.

### Control Flow
There is no runtime control flow in the header. Callers create a V4L2 bridge after a pvrusb2 context and hardware object are ready; ownership is then managed through pvrusb2 channel callbacks and V4L2 device release paths.

### State, Persistence, And Dependencies
No state is stored here. The header is the compile-time contract between context setup code and `pvrusb2-v4l2.c`.

### Integration Points
The constructor hooks higher-level pvrusb2 context code to V4L2 node registration without exposing bridge internals.

### Risks
Because only a constructor is exported, callers cannot explicitly destroy the object; lifetime must remain consistent with channel cleanup and disconnect callbacks in the implementation.

### Test Signals
Build coverage should ensure all users include this header rather than duplicating the opaque type. Runtime tests are covered through V4L2 node registration and disconnect handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-v4l2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-video-v4l.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-video-v4l.c

### Purpose
`pvrusb2-video-v4l.c` connects pvrusb2 input state to the V4L2 saa7115 video decoder subdevice. It maps pvrusb2 logical inputs to saa7115 routing IDs for supported board routing schemes.

### Important APIs, Types, And Functions
The file defines `struct routing_scheme`, two static route arrays for Hauppauge and OnAir-style signal routing, and `pvr2_saa7115_subdev_update(struct pvr2_hdw *, struct v4l2_subdev *)`.

### Control Flow
When `input_dirty` or `force_dirty` is set on the hardware object, the update function selects the route table from `hdw->hdw_desc->signal_routing_scheme`, validates the current input value against the table size, maps it to an saa7115 input constant, and calls `sd->ops->video->s_routing(sd, input, 0, 0)`.

### State, Persistence, And Dependencies
The file has only static routing tables. Runtime state is read from `struct pvr2_hdw`, especially `input_val`, dirty flags, and hardware descriptor fields. It depends on pvrusb2 internal hardware declarations, pvrusb2 tracing, V4L2 subdevice APIs, and `<media/i2c/saa7115.h>`.

### Integration Points
This function is called from the pvrusb2 hardware/subdevice update path when analog input selection changes. It is one link between V4L2 user-facing input ioctls and board-level I2C video decoder routing.

### Risks
Invalid routing scheme IDs or input values are logged and ignored, so a misdescribed board can leave the saa7115 on an old route. The implementation assumes `sd->ops->video->s_routing` exists for this subdevice.

### Test Signals
Tests should switch TV, radio, composite, and S-Video inputs on boards for both routing schemes and verify the saa7115 subdevice receives the expected route. Negative tests should cover unsupported route scheme IDs and out-of-range input values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-video-v4l.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-video-v4l.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-video-v4l.h

### Purpose
`pvrusb2-video-v4l.h` declares the internal saa7115 subdevice update hook used by the pvrusb2 hardware layer.

### Important APIs, Types, And Functions
It includes `pvrusb2-hdw-internal.h` and declares `pvr2_saa7115_subdev_update(struct pvr2_hdw *, struct v4l2_subdev *)`.

### Control Flow
The header has no runtime flow. It makes the implementation available to code that iterates or updates pvrusb2 I2C subdevices.

### State, Persistence, And Dependencies
There is no stored state. The dependency on the internal hardware header indicates this is not a public V4L2 API; it expects full access to pvrusb2 hardware internals.

### Integration Points
The declaration integrates the pvrusb2 video decoder adapter with lower-level subdevice synchronization code.

### Risks
Including an internal hardware header widens compile-time coupling. Changes to `struct pvr2_hdw` or V4L2 subdevice declarations may require coordinated edits.

### Test Signals
Build tests should cover configurations that compile saa7115 routing support. Runtime signals are input switching and routing verification in `pvrusb2-video-v4l.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-video-v4l.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-wm8775.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-wm8775.c

### Purpose
`pvrusb2-wm8775.c` adapts pvrusb2 input selection to the wm8775 audio ADC V4L2 subdevice. It chooses the audio input route used for radio versus other inputs.

### Important APIs, Types, And Functions
The single exported implementation function is `pvr2_wm8775_subdev_update(struct pvr2_hdw *, struct v4l2_subdev *)`.

### Control Flow
When `input_dirty` or `force_dirty` is set, the function maps `PVR2_CVAL_INPUT_RADIO` to route `1` and all other inputs to route `2`, traces the selection, and invokes `sd->ops->audio->s_routing(sd, input, 0, 0)`.

### State, Persistence, And Dependencies
No state is owned by this file. It reads pvrusb2 hardware state and depends on V4L2 subdevice audio operations plus pvrusb2 tracing.

### Integration Points
It is used by the pvrusb2 hardware update path to keep the external audio digitizer synchronized with the currently selected logical input.

### Risks
The route mapping is intentionally simple and board-specific; unsupported hardware wiring would need a descriptor-driven scheme similar to the saa7115 adapter. The function assumes the wm8775 subdevice exposes `audio->s_routing`.

### Test Signals
Switching into and out of radio input should produce different wm8775 routes. Tests should confirm non-radio analog inputs all use the expected external audio route and that dirty flags gate redundant updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-wm8775.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-wm8775.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-wm8775.h

### Purpose
`pvrusb2-wm8775.h` declares the internal wm8775 audio subdevice update hook for pvrusb2.

### Important APIs, Types, And Functions
It includes `pvrusb2-hdw-internal.h` and declares `pvr2_wm8775_subdev_update(struct pvr2_hdw *, struct v4l2_subdev *sd)`.

### Control Flow
The header has no runtime control flow. It exposes the update function to the hardware/subdevice synchronization code.

### State, Persistence, And Dependencies
No state is stored here. The dependency on internal pvrusb2 hardware structures keeps this interface private to the driver.

### Integration Points
The declaration links board audio routing updates to the wm8775-specific implementation.

### Risks
As with the implementation, the API is narrowly tailored to one audio subdevice and assumes callers already know when input state is dirty.

### Test Signals
Build coverage should include the subdevice update path, and runtime testing should verify radio/non-radio audio route changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-wm8775.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2.h

### Purpose
`pvrusb2.h` provides a small shared pvrusb2 driver constant for instance tracking.

### Important APIs, Types, And Functions
The only exported definition is `PVR_NUM`, set to `20`, the maximum number of pvrusb2 instances that receive small numeric unit IDs for array-valued module parameters.

### Control Flow
There is no control flow. Other pvrusb2 files use `PVR_NUM` to size arrays such as requested video, radio, and VBI minor numbers.

### State, Persistence, And Dependencies
No state is stored in the header. The value influences module-parameter arrays and whether extra connected devices can be addressed by per-unit options.

### Integration Points
`pvrusb2-v4l2.c` uses `PVR_NUM` for `video_nr`, `radio_nr`, and `vbi_nr`. Hardware instance numbering uses the bound as a limit when mapping unit number to preferred minor.

### Risks
If more than 20 devices are connected, driver operation continues but extra devices do not get unit-specific module parameter control. Raising the value changes static module parameter array sizes.

### Test Signals
Build-time coverage is enough for the header. Runtime testing would connect more than one device and verify per-unit module parameters map only within the allowed range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/Kconfig

### Purpose
`Kconfig` defines build options for the Philips/OEM USB webcam driver.

### Important APIs, Types, And Functions
The main symbol is `USB_PWC`, a tristate depending on `VIDEO_DEV` and selecting `VIDEOBUF2_VMALLOC`. Optional symbols are `USB_PWC_DEBUG` for verbose driver traces and `USB_PWC_INPUT_EVDEV` for snapshot-button input event support.

### Control Flow
Kconfig has no runtime flow, but it controls which code paths compile. `USB_PWC_INPUT_EVDEV` defaults to `y` when input support is compatible, and the C sources conditionally include input-device and debug code.

### State, Persistence, And Dependencies
Build configuration persists in the kernel `.config`. The selected symbols affect module contents, module parameters, debug logging, and whether an input device is registered for the camera button.

### Integration Points
The configuration integrates this driver with the media USB webcam menu, V4L2 core, videobuf2 vmalloc memory backend, and optional Linux input subsystem.

### Risks
The dependency expression for input support must remain aligned with Kconfig symbol semantics for `INPUT` and modular builds. Missing `VIDEOBUF2_VMALLOC` selection would break the vb2 queue used by `pwc-if.c`.

### Test Signals
Configuration tests should build `USB_PWC=y`, `USB_PWC=m`, debug on/off, input-event support on/off, and combinations where input is modular or disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/Makefile -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/Makefile

### Purpose
`Makefile` composes the `pwc` kernel module from its interface, control, V4L2, decompression, and mode-table objects.

### Important APIs, Types, And Functions
`pwc-objs` includes `pwc-if.o`, `pwc-misc.o`, `pwc-ctrl.o`, `pwc-v4l.o`, `pwc-uncompress.o`, `pwc-dec1.o`, `pwc-dec23.o`, `pwc-kiara.o`, and `pwc-timon.o`. `obj-$(CONFIG_USB_PWC) += pwc.o` connects the object list to the Kconfig symbol.

### Control Flow
There is no runtime flow. The object list determines link order and whether data tables/decompressors are present in the final driver.

### State, Persistence, And Dependencies
The file contributes to build-system state only. All driver runtime state lives in the linked objects.

### Integration Points
The Makefile integrates PWC with the kernel kbuild system and `CONFIG_USB_PWC`.

### Risks
Omitting any table or decompressor object would produce unresolved symbols or runtime feature loss. Adding new chipset support requires updating this object list.

### Test Signals
Build tests should verify `CONFIG_USB_PWC=m` produces `pwc.ko` and that all expected symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-ctrl.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-ctrl.c

### Purpose
`pwc-ctrl.c` sends USB vendor control messages to Philips/OEM webcams, selects video modes, initializes decompressor state for compressed modes, enumerates supported frame rates, and controls power, LEDs, and sensor queries.

### Important APIs, Types, And Functions
Important public functions are `pwc_set_video_mode()`, `pwc_get_fps()`, `pwc_get_u8_ctrl()`, `pwc_set_u8_ctrl()`, `pwc_get_s8_ctrl()`, `pwc_get_u16_ctrl()`, `pwc_set_u16_ctrl()`, `pwc_button_ctrl()`, `pwc_camera_power()`, `pwc_set_leds()`, and debug-only `pwc_get_cmos_sensor()`. Internal mode functions are `set_video_mode_Nala()`, `set_video_mode_Timon()`, and `set_video_mode_Kiara()`. The file owns Nala mode tables by including `pwc-nala.h` and consumes Timon/Kiara tables.

### Control Flow
Mode selection starts in `pwc_set_video_mode()`, which maps requested dimensions to a PWC size and dispatches by chipset family. Nala clamps frame rate to a table-supported value and uses a three-byte command. Timon and Kiara clamp to 5-30 fps, progressively raise compression until an available alternate setting is found, and use table commands of 13 or 12 bytes. When requested and compressed YUV output is selected, the relevant decompressor initializer runs. The chosen mode updates `pixfmt`, `vframes`, `valternate`, dimensions, `vbandlength`, `frame_size`, and `frame_total_size`.

### State, Persistence, And Dependencies
State is written into `struct pwc_device` and the camera over USB control endpoint zero. `cmd_buf` records the last video command for raw-frame export. `ctrl_buf` is reused as the transfer buffer. Dependencies include USB control messaging, chipset macros from `pwc.h`, mode tables, and decompressor initializers.

### Integration Points
`pwc-if.c` calls `pwc_set_video_mode()` during probe and stream start, retrying with higher compression on bandwidth errors. `pwc-v4l.c` calls control helpers from V4L2 control callbacks. LED and power helpers are used during stream start/stop and probe shutdown.

### Risks
Bandwidth retry depends on the caller preserving and increasing the compression argument. The Kiara endpoint command special case sends to endpoint 4 even though video is endpoint 5. Control helpers assume `ctrl_buf` is allocated and serialize through higher-level locks. Nala compressed YUV calls `pwc_dec1_init()`, but the actual codec1 decompressor path is not implemented.

### Test Signals
Test mode negotiation across Nala, Timon, and Kiara devices, requested frame-rate clamping, compression fallback on `-ENOSPC`, LED range clamping, power-save eligibility by device type/release, control-message error propagation, and raw-frame command metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec1.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec1.c

### Purpose
`pwc-dec1.c` contains the initialization stub for codec version 1 decompression used by older Nala webcams.

### Important APIs, Types, And Functions
The only function is `pwc_dec1_init(struct pwc_device *pdev, const unsigned char *cmd)`, which stores `pdev->release` in `pdev->dec1.version`.

### Control Flow
The function is called from Nala video-mode setup when a compressed mode is selected for YUV420 output. It does not parse the mode command or build decode tables.

### State, Persistence, And Dependencies
State is limited to `struct pwc_dec1_private.version` in the union inside `struct pwc_device`. The file depends on `pwc.h` for the device layout.

### Integration Points
`pwc-ctrl.c` invokes this initializer, while `pwc-uncompress.c` detects codec1 compressed YUV and currently returns `-ENXIO` instead of decompressing. Raw PWC1 output can still expose compressed data to userspace.

### Risks
The initializer can make codec1 compressed modes appear prepared, but kernel-side decompression is intentionally missing. Applications requesting YUV420 on compressed codec1 hardware will fail during buffer finish.

### Test Signals
Use an older codec1 camera and request raw PWC1 versus YUV420 compressed modes. Raw output should carry metadata; YUV decompression should fail clearly with the existing unsupported path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec1.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec1.h

### Purpose
`pwc-dec1.h` defines the private state and initializer declaration for legacy codec1 decompression.

### Important APIs, Types, And Functions
It forward declares `struct pwc_device`, defines `struct pwc_dec1_private { int version; }`, and declares `pwc_dec1_init()`.

### Control Flow
The header has no runtime control flow. It lets `struct pwc_device` embed codec1 state and lets `pwc-ctrl.c` call the initializer.

### State, Persistence, And Dependencies
The only state is the stored device release version. No persistent storage exists.

### Integration Points
Included by `pwc.h`, `pwc-ctrl.c`, `pwc-if.c`, and `pwc-uncompress.c` for compile-time type and function visibility.

### Risks
The minimal private state reflects the missing decompressor implementation. Future codec1 support would likely need a larger state structure and corresponding updates to `struct pwc_device`.

### Test Signals
Build coverage should catch signature mismatches. Runtime coverage is tied to codec1 mode initialization and the unsupported YUV decompression path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec23.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec23.c

### Purpose
`pwc-dec23.c` implements software decompression for PWC codec versions 2 and 3. It converts compressed Timon/Kiara camera bands into planar YUV420 output using reverse-engineered ROM tables, bitstream decoding, block reconstruction, and clamp/copy helpers.

### Important APIs, Types, And Functions
Public entry points are `pwc_dec23_init(struct pwc_device *, const unsigned char *cmd)` and `pwc_dec23_decompress(struct pwc_device *, const void *src, void *dst)`. Key internals include table builders `build_table_color()`, `build_subblock_pattern()`, `build_bit_powermask_table()`, `fill_table_dc00_d800()`, bit reservoir macros, `decode_block()`, `copy_image_block_Y()`, `copy_image_block_CrCb()`, and `DecompressBand23()`.

### Control Flow
Initialization checks whether the command byte changed; if so it derives codec bit depth and ROM version from the mode command, selects Kiara or Timon ROM tables, builds pass-one/pass-two color tables, scaling tables, subblock patterns, bit masks, and the clamp table. Decompression locks the decoder state, splits the destination into Y, U, and V planes, and processes one four-line band at a time. Each band skips the first stream byte, reads a compression index, decodes Y blocks first, then U and V blocks, and advances plane pointers to the next band.

### State, Persistence, And Dependencies
Decoder state lives in `struct pwc_dec23_private`: mutex, last command cache, bit reservoir, current stream pointer, temporary colors, and large lookup tables. The static `pwc_crop_table` is shared for clamping. The file depends on `pwc-timon.h`, `pwc-kiara.h`, and the camera mode command format established by `pwc-ctrl.c`.

### Integration Points
`pwc_set_video_mode()` initializes the decoder for compressed YUV420 modes. `pwc_decompress()` calls `pwc_dec23_decompress()` from the vb2 buffer-finish path after a full frame has been captured.

### Risks
The bitstream parser assumes valid compressed data and advances `stream` without explicit frame-length bounds inside decode macros. Decode table correctness depends on opaque reverse-engineered constants. The shared clamp table is rebuilt during init and could be touched by multiple devices, although decompression uses a per-device lock. Any mismatch between `vbandlength`, width, height, and command bytes can corrupt output or overread frame data.

### Test Signals
High-value tests include compressed YUV output for codec2 and codec3 devices at each supported resolution/fps/compression level, repeated mode changes that rebuild tables, parallel devices with different commands, malformed or short frames, and visual comparison against known-good decoded frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec23.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec23.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec23.h

### Purpose
`pwc-dec23.h` defines private state and public entry points for Timon/Kiara codec2/codec3 decompression.

### Important APIs, Types, And Functions
`struct pwc_dec23_private` contains the decoder mutex, command cache, bit depth/scaling values, bit reservoir, stream pointer, temporary 4x4 block colors, pass tables, subblock table, bit-mask table, and DC/scaling tables. It declares `pwc_dec23_init()` and `pwc_dec23_decompress()`.

### Control Flow
The header has no runtime flow, but its fields are filled during mode initialization and consumed during frame decompression.

### State, Persistence, And Dependencies
State is embedded in `struct pwc_device` through a union in `pwc.h`, so one active codec-private state exists per device. There is no persistent storage.

### Integration Points
Included by the PWC core, mode control, decompression frontend, and codec implementation. It defines the shared contract between `pwc-ctrl.c`, `pwc-uncompress.c`, and `pwc-dec23.c`.

### Risks
The structure contains large lookup tables and is embedded in every `pwc_device`, so size changes affect per-device memory. Direct field access across files would make future decoder refactors harder, though current mutation is localized mostly to `pwc-dec23.c`.

### Test Signals
Build tests should cover all include combinations. Runtime tests should validate decoder state reinitialization when mode command bytes change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec23.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-if.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-if.c

### Purpose
`pwc-if.c` is the USB and V4L2/videobuf2 core of the PWC driver. It matches supported USB webcam IDs, probes devices, registers V4L2 and optional input devices, manages isochronous USB capture, fills vb2 buffers, and handles disconnect and module parameters.

### Important APIs, Types, And Functions
Key objects are `pwc_device_table`, `pwc_driver`, `pwc_fops`, `pwc_template`, and `pwc_vb_queue_ops`. Major functions are `usb_pwc_probe()`, `usb_pwc_disconnect()`, `pwc_isoc_init()`, `pwc_isoc_handler()`, `pwc_frame_complete()`, `start_streaming()`, `stop_streaming()`, vb2 callbacks, URB allocation/free helpers, and optional input snapshot-button reporting.

### Control Flow
Probe accepts interface 0 only, maps vendor/product IDs to a camera type/name/features, allocates and constructs `struct pwc_device`, initializes locks and vb2, allocates USB control buffers, sets an initial mode, registers controls, powers down the camera, registers `v4l2_device` and `video_device`, and optionally registers an input device. Streaming powers on the camera, sets LEDs, selects a video mode, sets the USB alternate interface, allocates and submits isochronous URBs, and then repeatedly re-submits URBs from completion context. The completion handler compacts packet payloads into the current queued frame, detects short-packet frame boundaries, handles camera-specific header/trailer quirks, and marks vb2 buffers done. Stop/disconnect kill URBs, free buffers, power down, error queued buffers, unregister devices, and clear `udev`.

### State, Persistence, And Dependencies
`struct pwc_device` owns persistent runtime state: USB device pointer, endpoint/alternate selection, URB array, fill buffer, queued-buffer list, locks, frame counters, error counters, V4L2 controls, and optional input device. Dependencies include USB core, DMA mapping, V4L2 device/video APIs, videobuf2 vmalloc, Linux input, tracepoints, and PWC control/decompression helpers.

### Integration Points
`pwc-v4l.c` supplies ioctl and control operations. `pwc-ctrl.c` supplies mode, power, LED, and USB-control helpers. `pwc-uncompress.c` runs from `buffer_finish()`. V4L2 userspace interacts through read, mmap, poll, and streaming ioctls supplied by vb2.

### Risks
The isochronous handler runs in interrupt context and must not block; frame state and queued buffers require careful locking. `fill_buf` is intentionally lockless except stream start/stop and URB context, so ordering around cleanup matters. Disconnect sets `udev` under both locks; callers must check it before queueing or streaming. Packet overflow/underflow and repeated isochronous errors drop frames or mark errors, but malformed data can still reach decompression.

### Test Signals
Test probe for all supported ID families, stream start/stop, read and mmap capture, disconnect during streaming, `-ENOSPC` compression fallback, short/overflow/underflow frames, isochronous error thresholds, LED/power transitions, snapshot button events, and module parameters for `power_save`, `leds`, and debug trace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-kiara.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-kiara.c

### Purpose
`pwc-kiara.c` provides static mode-selection and ROM lookup data for Kiara-generation PWC cameras, mainly types 730, 740, and 750.

### Important APIs, Types, And Functions
The file defines `Kiara_fps_vector`, `Kiara_table[PSZ_MAX][PWC_FPS_MAX_KIARA][4]`, and `KiaraRomTable[8][2][16][8]`. Entries describe USB alternate interface, packet size, compressed band length, and twelve-byte camera mode commands for each resolution/fps/compression slot.

### Control Flow
There is no executable control flow beyond static initialization. `set_video_mode_Kiara()` indexes `Kiara_table` by size, fps, and compression preference, while `pwc_dec23_init()` indexes `KiaraRomTable` by command-derived ROM version and pass.

### State, Persistence, And Dependencies
All data is constant and shared by all devices. No runtime state is stored here. The file depends on `pwc-kiara.h` for type declarations and on PWC size constants.

### Integration Points
Mode negotiation in `pwc-ctrl.c` consumes the mode table to select alternate settings and commands. The codec23 decompressor consumes ROM tables to build decode tables for compressed YUV output.

### Risks
Data correctness is critical and hard to infer from code review. An incorrect alternate, band length, or command byte can cause USB bandwidth failures, malformed frame sizing, or bad decompression. Unsupported modes are represented by zero alternates and must remain aligned with `PSZ_MAX` and fps vectors.

### Test Signals
Exercise Kiara devices at each supported resolution and frame rate, compare selected `valternate`/`vbandlength` against expected table entries, capture raw and YUV420 formats, and verify decode output after mode changes that alter ROM versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-kiara.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-kiara.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-kiara.h

### Purpose
`pwc-kiara.h` declares Kiara chipset mode-entry structures and constant tables.

### Important APIs, Types, And Functions
It defines `PWC_FPS_MAX_KIARA`, `struct Kiara_table_entry`, and extern declarations for `Kiara_table`, `KiaraRomTable`, and `Kiara_fps_vector`.

### Control Flow
The header has no runtime flow. It provides typed access to static table data.

### State, Persistence, And Dependencies
No mutable state exists. The header includes `pwc.h` for `PSZ_MAX` and shared constants.

### Integration Points
Included by control and decompressor code to negotiate Kiara modes and build codec23 decode tables.

### Risks
The struct layout must match table initializer order and control-code expectations. Changing `PWC_FPS_MAX_KIARA` or table dimensions requires updates in both data and enumeration logic.

### Test Signals
Build coverage catches declaration/definition mismatches. Runtime tests should enumerate frame intervals and set formats on Kiara cameras.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-kiara.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-misc.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-misc.c

### Purpose
`pwc-misc.c` provides shared image-size tables and basic per-chipset construction for PWC devices.

### Important APIs, Types, And Functions
The file defines `pwc_image_sizes[PSZ_MAX][2]`, `pwc_get_size(struct pwc_device *, int width, int height)`, and `pwc_construct(struct pwc_device *)`.

### Control Flow
`pwc_get_size()` searches from largest to smallest supported image size and returns the largest mode that fits inside the request, falling back to the smallest supported mode. `pwc_construct()` initializes supported image masks, control interface, video endpoint, and frame header/trailer sizes based on codec family.

### State, Persistence, And Dependencies
The image-size table is constant. `pwc_construct()` writes initial fields into `struct pwc_device` before probe continues. It depends on chipset macros and constants from `pwc.h`.

### Integration Points
Probe calls `pwc_construct()` before mode setup. Format negotiation, mode setup, queue sizing, and frame-size enumeration all consume `pwc_image_sizes` and `pwc_get_size()`.

### Risks
The "largest size fitting request" behavior may surprise callers expecting closest size by area or exact match. Endpoint/interface values are chipset assumptions that must align with USB descriptors and mode command handling.

### Test Signals
Test requested sizes below minimum, between modes, and above maximum for each chipset family. Probe tests should verify endpoint, interface, image mask, and header/trailer sizes for codec1, codec2, and codec3 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-nala.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-nala.h

### Purpose
`pwc-nala.h` is an included data table for older Nala cameras, covering type 645/646 mode commands.

### Important APIs, Types, And Functions
The file is not a normal standalone header with guards. It contributes initializer rows for `Nala_table[PSZ_MAX][PWC_FPS_MAX_NALA]` in `pwc-ctrl.c`. Each row contains USB alternate setting, compressed flag, and a three-byte mode command.

### Control Flow
There is no executable flow. `set_video_mode_Nala()` indexes the included table after mapping requested frame rates to supported Nala rates.

### State, Persistence, And Dependencies
All data becomes static table state inside `pwc-ctrl.c`. It depends on the exact `struct Nala_table_entry` layout visible at inclusion time.

### Integration Points
The table feeds codec1/Nala video mode selection and determines which resolutions are unavailable by zero entries.

### Risks
Because this is an include-fragment rather than a guarded header, it should only be included in the intended initializer context. Table shape must remain exactly aligned with `PSZ_MAX` and `PWC_FPS_MAX_NALA`.

### Test Signals
Build tests catch initializer-shape errors. Runtime tests on Nala devices should verify SQCIF/QCIF/CIF mode selection, unavailable modes, alternate settings, compression flags, and raw PWC1 output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-nala.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-timon.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-timon.c

### Purpose
`pwc-timon.c` provides static mode-selection and ROM lookup data for Timon-generation PWC cameras, mainly types 675, 680, and 690.

### Important APIs, Types, And Functions
The file defines `Timon_fps_vector`, `Timon_table[PSZ_MAX][PWC_FPS_MAX_TIMON][4]`, and `TimonRomTable[16][2][16][8]`. Mode entries contain alternate interface, packet size, compressed band length, and thirteen-byte camera mode commands.

### Control Flow
The file itself is data-only. `set_video_mode_Timon()` indexes the mode table while increasing compression if a lower-compression entry is unavailable. `pwc_dec23_init()` uses the ROM table version selected from the mode command to build decode tables.

### State, Persistence, And Dependencies
All data is constant and shared. There is no runtime mutation. The file depends on `pwc-timon.h` and common PWC constants.

### Integration Points
Mode negotiation, frame-rate enumeration, and codec23 decompression all depend on these tables for Timon devices.

### Risks
As with Kiara data, incorrect constants can produce USB alternate-setting errors, bad frame-size calculation, or incorrect decompression. The large ROM table is opaque and difficult to validate except through device output.

### Test Signals
Test Timon devices across supported resolutions/fps values, compression fallback, raw PWC2 and YUV420 capture, visual output quality, and frame interval enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-timon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-timon.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-timon.h

### Purpose
`pwc-timon.h` declares Timon chipset mode-entry structures and constant tables.

### Important APIs, Types, And Functions
It defines `PWC_FPS_MAX_TIMON`, `struct Timon_table_entry`, and extern declarations for `Timon_table`, `TimonRomTable`, and `Timon_fps_vector`.

### Control Flow
There is no runtime flow in the header. It provides typed declarations for table consumers.

### State, Persistence, And Dependencies
No mutable state exists. It includes `pwc.h` for shared constants and dimensions.

### Integration Points
Included by PWC control and codec23 decompression code.

### Risks
Struct and dimension mismatches would break table lookup semantics. Since entries include packed camera command bytes, consumers must preserve byte count and ordering.

### Test Signals
Build coverage validates definitions. Runtime testing should cover frame interval enumeration and mode setup on Timon hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-timon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-uncompress.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-uncompress.c

### Purpose
`pwc-uncompress.c` is the frame conversion frontend. It turns captured raw PWC frame data into either userspace raw PWC metadata+payload or planar YUV420 output.

### Important APIs, Types, And Functions
The single public function is `pwc_decompress(struct pwc_device *, struct pwc_frame_buf *)`. It uses `struct pwc_raw_frame`, vb2 plane helpers, codec macros, and `pwc_dec23_decompress()`.

### Control Flow
The function obtains the output plane address and skips the camera-specific frame header in the captured buffer. For raw PWC1/PWC2 output, it writes type, band length, last mode command, and raw frame bytes into the vb2 plane. For YUV420, it sets the payload to width*height*3/2. If `vbandlength` is zero, it byte-shuffles native uncompressed camera data into Y, U, and V planes. If compressed and codec1, it returns `-ENXIO`. Otherwise it invokes codec23 decompression.

### State, Persistence, And Dependencies
The function reads `struct pwc_device` fields such as type, width, height, pixfmt, command buffer, frame sizes, header size, and band length. It writes only the vb2 output payload. Dependencies include videobuf2, PWC decompressor headers, and format constants.

### Integration Points
`pwc-if.c` calls this from `buffer_finish()` when a completed buffer is dequeued by userspace. Mode setup in `pwc-ctrl.c` determines whether the path is raw, uncompressed YUV, codec1, or codec23.

### Risks
Codec1 YUV output is unsupported despite mode initialization. The uncompressed byte-shuffle assumes the captured payload size and layout match width/height. Raw output size uses `struct_size()` and must fit the allocated vb2 plane.

### Test Signals
Test raw PWC1/PWC2 capture, uncompressed YUV420 modes, compressed codec23 YUV420 modes, unsupported codec1 YUV handling, payload sizes, and output-plane contents for small known frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-uncompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-v4l.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-v4l.c

### Purpose
`pwc-v4l.c` provides the V4L2 ioctl and control implementation for the PWC driver. It registers camera controls, maps V4L2 controls to USB vendor requests, negotiates capture formats, enumerates sizes and frame intervals, and wires vb2 ioctls into the video device.

### Important APIs, Types, And Functions
The public objects are `pwc_init_controls()` and `pwc_ioctl_ops`. Important helpers include `pwc_vidioc_try_fmt()`, `pwc_s_fmt_vid_cap()`, `pwc_g_volatile_ctrl()`, `pwc_s_ctrl()`, `pwc_set_awb()`, `pwc_set_autogain()`, `pwc_set_exposure_auto()`, `pwc_set_autogain_expo()`, and `pwc_set_motor()`. It defines custom control IDs for contour, noise reduction, AWB timing, and save/restore buttons.

### Control Flow
Probe calls `pwc_init_controls()`, which reads hardware defaults through USB control helpers, creates V4L2 controls, and clusters auto/manual controls. Volatile reads cache slow hardware values for roughly a quarter second. Set-control callbacks translate V4L2 values into PWC register encodings, including inverted boolean conventions where `0` often means auto/enabled. Format ioctls validate the buffer type, select a supported pixel format, choose the nearest supported image size, and reject active format changes while the vb2 queue is busy. Stream parameter ioctls expose and change frame rate by rerunning mode setup without sending commands immediately.

### State, Persistence, And Dependencies
Control objects and cached volatile values live in `struct pwc_device`. Hardware state persists in the camera until changed or reset, including save/restore user defaults. The file depends on V4L2 control/event APIs, PWC USB control helpers, vb2 ioctl helpers, jiffies timing, and mode tables through `pwc_get_fps()`/`pwc_set_video_mode()`.

### Integration Points
`pwc-if.c` installs `pwc_ioctl_ops` in the `video_device` and stores the control handler in the V4L2 device. Userspace reaches this file through `video_ioctl2`, V4L2 controls, frame-size and frame-interval enumeration, and vb2 streaming ioctls.

### Risks
Control availability differs by codec generation; unsupported combinations must return `-EINVAL` without dereferencing absent controls. Cached volatile values may briefly report stale auto gain/exposure/balance. Format changes while buffers are active are rejected, but parameter changes also depend on `vb2_is_busy()`. Several register encodings are inverted or model-specific, making regressions easy.

### Test Signals
Test control creation on codec1/2/3 and motorized devices, default-value fallback when USB reads fail, auto/manual clusters, volatile-cache timing, every set-control USB request, format negotiation for YUV420/PWC1/PWC2, `-EBUSY` during active queues, frame-size and frame-interval enumeration, event subscribe/unsubscribe, and stream parameter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-v4l.c -->
