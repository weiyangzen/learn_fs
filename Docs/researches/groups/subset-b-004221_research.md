# subset-b-004221 research

This grouped report covers USB media drivers under `sources/distributed-fs/ceph-client/drivers/media/usb`. Each section preserves the original source path so reconciliation can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc.h

## Purpose
`pwc.h` is the shared internal header for the Philips/NXP USB webcam driver. It defines device limits, Philips vendor-control request selectors, frame and USB isochronous buffer sizing, codec family predicates, the central `struct pwc_device`, and prototypes used by the interface, V4L2, control, and decompression implementation files.

## Important APIs, Types, and Functions
Important constants include `PWC_VERSION`, `MAX_WIDTH`, `MAX_HEIGHT`, `MAX_ISO_BUFS`, `ISO_FRAMES_PER_DESC`, `ISO_MAX_FRAME_SIZE`, `PWC_FRAME_SIZE`, and supported size identifiers `PSZ_*`. Vendor-control selectors are grouped around luminance, chrominance, status, stream, and motorized pan/tilt requests. `struct pwc_raw_frame` describes compressed camera data, `struct pwc_frame_buf` embeds `vb2_v4l2_buffer`, and `struct pwc_device` aggregates USB state, V4L2/vb2 queues, controls, frame assembly state, decompressor private data, and optional snapshot-button input state. Declared cross-file APIs include `pwc_set_video_mode()`, `send_control_msg()`, `pwc_get_u8_ctrl()`/`pwc_set_u8_ctrl()`, `pwc_init_controls()`, `pwc_camera_power()`, `pwc_ioctl_ops`, and `pwc_decompress()`.

## Control Flow
The header itself has no executable flow, but it defines the data path used by the driver: USB isochronous completion fills `fill_buf`, raw camera payload is tracked with header/trailer sizes and `vbandlength`, then `pwc_decompress()` expands or passes data into user buffers managed by vb2. Control flow for userspace settings is routed through V4L2 control objects in `struct pwc_device`, through the `pwc_get_*_ctrl`/`pwc_set_*_ctrl` helpers, and finally through Philips vendor control transfers.

## State and Persistence
Runtime state is per camera in `struct pwc_device`: USB identity and endpoint selection, current video mode, current frame counters, isochronous URBs, queued vb2 buffers, decompressor state, cached auto white-balance/gain/exposure values with jiffies timestamps, and optional input-device state. The only durable device behavior exposed here is the camera's own save/restore user defaults and factory defaults control selectors; the Linux driver has no filesystem persistence.

## Dependencies and Integration Points
The header integrates Linux USB, V4L2 device/ioctl/control/event APIs, videobuf2-v4l2/vmalloc memory ops, wait queues, mutexes, spinlocks, and optional input evdev support. It also depends on the local codec headers `pwc-dec1.h` and `pwc-dec23.h`. Consumers of this header must respect the lock ordering comment: `vb_queue_lock` before `v4l2_lock` when both are needed.

## Risks and Edge Cases
The single large `struct pwc_device` mixes USB disconnect state, queue state, and control caches, so teardown paths must hold the documented locks before setting `udev` to NULL. Frame-size constants assume worst-case VGA YUV420 plus ToUCam header/trailer overhead; mismatched sizes can cause decompressor or vb2 payload errors. Codec-family macros depend on model-number ranges. Vendor-control cache timestamps can return stale gain/exposure/white-balance readings if invalidation is missed.

## Test Signals
Useful signals include successful probe for codec1/codec2/codec3 cameras, V4L2 format enumeration for compressed and decompressed modes, mmap/read streaming through vb2, isochronous error recovery after startup low-watermark frames, correct control get/set traffic for luminance/chrominance/status selectors, optional snapshot-button events, and clean behavior when a device is unplugged while buffers or controls are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/s2255/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/s2255/Kconfig

## Purpose
This Kconfig entry exposes the Sensoray 2255 USB video capture driver as `CONFIG_USB_S2255`.

## Important APIs, Types, and Functions
The symbol is a `tristate` named `USB_S2255` with prompt "USB Sensoray 2255 video capture device". It depends on `VIDEO_DEV`, selects `VIDEOBUF2_VMALLOC`, and documents that the module name is `s2255drv`.

## Control Flow
When enabled built-in or as a module, the media USB build includes the Sensoray driver object through the companion Makefile. The selected vb2 vmalloc dependency provides the memory backend used by the driver's V4L2 queues.

## State and Persistence
Kconfig state is compile-time configuration only. No runtime state or persistence is introduced here.

## Dependencies and Integration Points
The entry integrates with the Linux media Kconfig tree and V4L2 core. `VIDEO_DEV` is required because the driver registers V4L2 video devices; `VIDEOBUF2_VMALLOC` is selected because frame buffers are vmalloc-backed.

## Risks and Edge Cases
The entry does not explicitly depend on `USB`, assuming it is reached from USB media context. Invalid builds would show up as missing USB symbols or media core symbols if Kconfig nesting changes.

## Test Signals
Build test with `CONFIG_USB_S2255=m` and `=y`, confirm `s2255drv.ko` is produced for modular builds, and verify dependency selection pulls in videobuf2 vmalloc support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/s2255/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/s2255/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/s2255/Makefile

## Purpose
The Makefile wires the Sensoray 2255 driver object into the kernel build.

## Important APIs, Types, and Functions
It contains a single object mapping: `obj-$(CONFIG_USB_S2255) += s2255drv.o`.

## Control Flow
Kbuild compiles and links `s2255drv.c` when `CONFIG_USB_S2255` is enabled. If built as a module, the resulting module corresponds to `s2255drv`.

## State and Persistence
This file has no runtime state. Its effect is build graph state controlled by Kconfig.

## Dependencies and Integration Points
It integrates with Kbuild's `obj-*` mechanism and the `USB_S2255` Kconfig symbol.

## Risks and Edge Cases
Because there is only one object, adding helper files later requires updating this Makefile or using a composite object variable. Incorrect symbol names would silently omit the driver from builds.

## Test Signals
Run a media-driver build with `CONFIG_USB_S2255=m` and confirm `drivers/media/usb/s2255/s2255drv.o` and the final module are generated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/s2255/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/s2255/s2255drv.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/s2255/s2255drv.c

## Purpose
`s2255drv.c` is the V4L2 USB driver for Sensoray 2255/2257 multi-channel capture devices. It supports four independent video channels, firmware loading, bulk streaming, V4L2 controls, format negotiation, frame-rate decimation, JPEG/MJPEG capture, and per-channel video nodes.

## Important APIs, Types, and Functions
Core types are `struct s2255_dev` for device-global state, `struct s2255_vc` for one capture channel, `struct s2255_fw` for asynchronous DSP firmware loading, `struct s2255_pipeinfo` for the bulk read pipe, `struct s2255_mode` for DSP mode commands, and `struct s2255_buffer`/`struct s2255_bufferi` for vb2 and internal frame rings. Key entry points are `s2255_probe()`, `s2255_disconnect()`, `s2255_open()`, `s2255_probe_v4l()`, `s2255_start_readpipe()`, `s2255_start_acquire()`, `s2255_stop_acquire()`, `s2255_set_mode()`, `s2255_cmd_status()`, `save_frame()`, and the vb2/V4L2 ioctl callbacks. Module parameters are `debug`, `video_nr`, and `jpeg_enable`.

## Control Flow
USB probe allocates `struct s2255_dev`, locates the bulk-in endpoint, allocates firmware and command buffers, requests `f2255usb.bin`, verifies the firmware marker and version, resets the USB device, initializes board buffers and the read pipe, starts asynchronous firmware upload, then registers four V4L2 video devices. Firmware upload is chunked through a bulk URB; after all chunks are sent, DSP responses in the normal read stream mark all channels ready and wake `wait_fw`. Opening a video node waits for firmware success or retries failed firmware loading. Streaming starts from vb2 `start_streaming()`, resets per-channel frame state, sends `CMD_START`, and then the read-pipe URB callback parses frame markers and command-response markers. Completed frames are copied from the internal ring into queued vb2 buffers and returned with monotonic timestamps. Stopping streaming sends `CMD_STOP`, drains queued buffers with errors, and disconnect unregisters video nodes while waking firmware, setmode, and status waiters.

## State and Persistence
Device-global state includes firmware state (`S2255_FW_*`), DSP/USB firmware versions, `chn_ready`, command buffer, pipe state, current marker channel, and a refcount tracking registered video devices. Per-channel state includes selected standard, width/height/field, pixel format, JPEG quality, capture parameters, mode restart flag, requested image size, frame ring position, bad payload count, status wait queues, and vb2 queue/buffer list. Firmware is externally persisted as `f2255usb.bin`; driver state is runtime only. The board is reset on destroy so firmware can be reloaded on later probe/open.

## Dependencies and Integration Points
The driver depends on Linux USB bulk/control messaging, firmware loader, V4L2 device/ioctl/control/event APIs, videobuf2-v4l2/vmalloc, wait queues, timers, mutexes, spinlocks, and Sensoray vendor protocol markers. It registers USB IDs `0x1943:0x2255` and `0x1943:0x2257`, exports four V4L2 capture nodes, and exposes private `V4L2_CID_S2255_COLORFILTER` when firmware and board type permit.

## Risks and Edge Cases
Firmware loading is asynchronous and shares the normal read pipe for DSP responses, so opens must correctly handle `NOTLOADED`, `LOADED_DSPWAIT`, `FAILED`, and `DISCONNECTING`. `save_frame()` scans raw bulk data for markers and uses reversed channel mapping; bad marker alignment, payload sizes larger than `req_image_size`, or channel IDs outside range are discarded. JPEG payload size is separate from vb2 sizeimage and must be bounded by user buffer sizing. `s2255_vendor_req()` allocates zero bytes for some output requests and copies from a NULL transfer buffer when `TransferBufferLength` is zero; current callers rely on allocator/control behavior. Teardown depends on the video-device refcount, so all registered channels must unregister without double destroying shared device memory.

## Test Signals
Test firmware success and failure paths, immediate open after probe while firmware is still loading, firmware retry after failure, all four channels streaming concurrently under bandwidth-sensitive modes, NTSC/PAL standard changes with busy queue rejection, JPEG disable module parameter, color-filter availability for 2257 and firmware versions, video status reporting, bad signal input status, unplug during firmware wait, unplug during streaming, and vb2 read/mmap/userptr capture for each supported pixel format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/s2255/s2255drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/siano/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/siano/Kconfig

## Purpose
This Kconfig entry enables the USB transport driver for Siano SMS1xxx mobile digital TV receivers.

## Important APIs, Types, and Functions
The symbol is `SMS_USB_DRV`, a `tristate` with prompt "Siano SMS1xxx based MDTV receiver". It depends on `DVB_CORE && HAS_DMA`, uses `depends on !RC_CORE || RC_CORE`, and selects `MEDIA_COMMON_OPTIONS` and `SMS_SIANO_MDTV`.

## Control Flow
Enabling this symbol builds the USB transport and pulls in the shared Siano MDTV core. The driver then binds USB IDs and hands data and request callbacks to the common smscore layer.

## State and Persistence
The file only controls build configuration. Runtime Siano device state is implemented in `smsusb.c` and the common Siano core.

## Dependencies and Integration Points
The entry connects USB Siano support to the DVB core, DMA-capable buffer usage, optional remote-control core availability, and shared media options.

## Risks and Edge Cases
The remote-control dependency expression allows builds both with and without `RC_CORE`; changes in common Siano code could require tightening that relationship. Missing `HAS_DMA` would break URB/buffer assumptions.

## Test Signals
Build with `CONFIG_SMS_USB_DRV=m`, verify `smsusb.o` links with common Siano objects, and check Kconfig dependency resolution for DVB-only and RC-core-enabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/siano/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/siano/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/siano/Makefile

## Purpose
This Makefile builds the Siano USB transport and adds include paths needed for shared Siano headers.

## Important APIs, Types, and Functions
It maps `obj-$(CONFIG_SMS_USB_DRV) += smsusb.o` and adds `-I $(srctree)/drivers/media/common/siano`. It also appends `$(extra-cflags-y)` and `$(extra-cflags-m)` to `ccflags-y`.

## Control Flow
Kbuild compiles `smsusb.c` when the Siano USB Kconfig symbol is enabled. The include path lets `smsusb.c` include `smscoreapi.h`, `sms-cards.h`, and related common headers.

## State and Persistence
No runtime state exists here; this is build graph and compiler-flag state.

## Dependencies and Integration Points
The Makefile depends on Kbuild's object selection and the common Siano source tree.

## Risks and Edge Cases
The extra CFLAGS pass-through can affect warnings or ABI assumptions if set by parent makefiles. Moving common Siano headers requires updating this include path.

## Test Signals
Build Siano USB support and confirm `smsusb.c` resolves common Siano includes without local relative include hacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/siano/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/siano/smsusb.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/siano/smsusb.c

## Purpose
`smsusb.c` implements the USB transport for Siano SMS1xxx MDTV receivers. It binds many Siano and branded USB IDs, loads cold-state firmware for Stellar devices, allocates bulk URBs, translates Siano message endian format, registers with the common `smscore` layer, and handles suspend/resume.

## Important APIs, Types, and Functions
`enum smsusb_state` tracks disconnected, suspended, and active device states. `struct smsusb_device_t` stores the USB device, smscore device, endpoint numbers, response alignment, buffer size, and an array of `struct smsusb_urb_t`. Important functions are `smsusb_probe()`, `smsusb_disconnect()`, `smsusb_suspend()`, `smsusb_resume()`, `smsusb_init_device()`, `smsusb_term_device()`, `smsusb_start_streaming()`, `smsusb_stop_streaming()`, `smsusb_submit_urb()`, `smsusb_onresponse()`, `smsusb_sendrequest()`, `smsusb1_load_firmware()`, `smsusb1_detectmode()`, and `smsusb1_setmode()`.

## Control Flow
Probe first filters for the board's expected interface number, clears endpoint stalls, and ignores ROM interface 0 on two-interface devices. For cold Stellar ROM IDs, it loads mode-specific firmware with `smsusb1_load_firmware()` and lets the device re-enumerate. Warm devices call `smsusb_init_device()`, which discovers bulk endpoints, chooses USB1 or USB2 buffer sizes, registers a media controller device when enabled, registers with `smscore`, allocates up to ten receive URBs, submits them, marks the device active, and starts the core device. Each URB completion validates the Siano message header, handles split-message alignment, endian-converts RX data, passes the buffer to `smscore_onresponse()`, and schedules a work item to resubmit the URB from process context. Outbound messages are copied, endian-converted, and sent with `usb_bulk_msg()`. Suspend kills URBs and sets suspended state; resume clears stalls, resets the interface, and restarts streaming.

## State and Persistence
Device state is runtime-only: endpoints, response alignment, buffer pool ownership, URBs, smscore core pointer, and active/suspended/disconnected state. Firmware files are externally persisted, with board-specific names coming from `sms_get_board(board_id)->fw` or fallback `smsusb1_fw_lkup`. No driver configuration is persisted beyond smscore registry mode lookup for cold firmware choice.

## Dependencies and Integration Points
The driver depends on Linux USB bulk APIs, firmware loader, workqueues, media controller optional support, and the shared Siano `smscore`/board/endian APIs. It integrates with board descriptors via `driver_info`, calls `sms_board_load_modules()` after probe, and exposes send/detect/set-mode callbacks to smscore.

## Risks and Edge Cases
URB completion cannot sleep, so resubmission is deferred; teardown must cancel work after killing URBs to avoid use-after-free. Split-message alignment adjusts buffer offsets and copies the header; bad length or offset calculations can corrupt message delivery. `smsusb_sendrequest()` rejects non-active devices, so resume ordering matters. Cold firmware load intentionally returns after upload because the device resets and re-enumerates. Resume restarts streaming but does not explicitly set `state = SMSUSB_ACTIVE`, so behavior depends on higher-layer expectations after suspend.

## Test Signals
Test cold-to-warm Stellar firmware upload, board/interface filtering, endpoint halt clearing, USB1 and USB2 family buffer sizes, split-message reception, smscore buffer return on stop, media-controller registration cleanup, suspend/resume with live DVB applications, disconnect during queued work, and outbound request rejection while suspended or disconnected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/siano/smsusb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/Kconfig

## Purpose
This Kconfig entry exposes the STK1160 USB video capture driver.

## Important APIs, Types, and Functions
The symbol is `VIDEO_STK1160`, a `tristate` depending on `VIDEO_DEV && I2C`. It selects `VIDEOBUF2_VMALLOC` and `VIDEO_SAA711X`.

## Control Flow
When enabled, the companion Makefile builds the composite `stk1160` driver from core, V4L2, video, I2C, and AC97 source files. Selecting `VIDEO_SAA711X` provides the decoder subdevice used during probe.

## State and Persistence
This file has compile-time configuration state only.

## Dependencies and Integration Points
It integrates with V4L2, I2C, videobuf2 vmalloc, and the SAA711x decoder driver. The help text clarifies that audio capture is expected through `snd-usb-audio`, not this video driver.

## Risks and Edge Cases
The driver contains AC97 setup helpers but does not implement ALSA capture, so users may expect audio from this option alone and not get it. Dropping `I2C` or `VIDEO_SAA711X` would break decoder probing.

## Test Signals
Build with `CONFIG_VIDEO_STK1160=m`, confirm `stk1160.ko` is produced and the SAA711x dependency is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/Makefile

## Purpose
The Makefile defines the composite STK1160 module.

## Important APIs, Types, and Functions
`stk1160-y` includes `stk1160-core.o`, `stk1160-v4l.o`, `stk1160-video.o`, `stk1160-i2c.o`, and `stk1160-ac97.o`; `obj-$(CONFIG_VIDEO_STK1160) += stk1160.o`.

## Control Flow
Kbuild links the five implementation objects into one `stk1160` built-in object or module according to `CONFIG_VIDEO_STK1160`.

## State and Persistence
No runtime state exists. The file defines build composition.

## Dependencies and Integration Points
The object split mirrors the driver's internal module boundaries: USB core/probe, V4L2/vb2 policy, isochronous video transfer, I2C bridge, and AC97 setup.

## Risks and Edge Cases
Removing any object breaks cross-file prototypes declared in `stk1160.h`. Adding new split files requires updating the composite list.

## Test Signals
Build `CONFIG_VIDEO_STK1160=m` and confirm all five objects are linked into `stk1160.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-ac97.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-ac97.c

## Purpose
`stk1160-ac97.c` configures optional AC97 audio codec support exposed through STK1160 registers. It does not implement audio capture; it initializes mixer/recording register defaults when the hardware reports an external AC97 codec.

## Important APIs, Types, and Functions
Key functions are `stk1160_ac97_wait_transfer_complete()`, `stk1160_write_ac97()`, optional debug-only `stk1160_read_ac97()` and `stk1160_ac97_dump_regs()`, `stk1160_has_audio()`, `stk1160_has_ac97()`, and exported internal setup function `stk1160_ac97_setup()`.

## Control Flow
Setup reads `STK1160_POSV_L` strap bits to determine whether audio is present and whether an AC97 codec is attached. If either check fails it logs and exits. For AC97 devices it resets the AC97 interface, selects 16-bit stereo data, then writes fixed values into CD, line-in, microphone, aux, record select, master volume, and record gain codec registers. Each write programs the codec address, writes low/high command bytes, sets the command-write bit, and waits until read/write command bits clear or timeout.

## State and Persistence
The only state changed is device register and codec register state. There is no software cache. Codec settings persist only while the USB device remains powered/configured.

## Dependencies and Integration Points
The file depends on `stk1160_read_reg()`/`stk1160_write_reg()` from core and register definitions from `stk1160-reg.h`. It is called during core probe after STK1160 reset and input selection.

## Risks and Edge Cases
Timeout handling logs `AC97 transfer took too long` but `stk1160_write_ac97()` ignores the return value, so setup continues after a stuck codec. Strap-bit interpretation must match board wiring; otherwise AC97 setup can be skipped or attempted incorrectly. Fixed mixer values may not fit every clone board.

## Test Signals
Test boards with no audio, internal ADC, and AC97 codec strap combinations; check AC97 command bits clear within `STK1160_AC97_TIMEOUT`; with debug enabled, confirm register dump values after setup; verify video probe remains successful when AC97 is absent or nonresponsive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-ac97.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-core.c

## Purpose
`stk1160-core.c` is the USB probe, register-access, device-reset, and teardown core for STK1160 USB video capture devices.

## Important APIs, Types, and Functions
Important functions are `stk1160_read_reg()`, `stk1160_write_reg()`, `stk1160_select_input()`, `stk1160_reg_reset()`, `stk1160_scan_usb()`, `stk1160_probe()`, `stk1160_disconnect()`, and the v4l2 release callback `stk1160_release()`. The module parameter `input` selects the default input. USB ID support is `05e1:0408`.

## Control Flow
Probe rejects USB audio-class interfaces, allocates an alternate-setting packet-size table, scans all endpoints for video/audio isochronous endpoints, allocates `struct stk1160`, initializes vb2, locks, and V4L2 controls, registers the V4L2 device, registers the STK1160 I2C adapter, creates the SAA711x decoder subdevice, resets and stops the decoder, programs STK1160 reset defaults, selects the configured input, performs optional AC97 setup, and finally registers the video node. Disconnect clears interface data, takes vb2 and V4L locks, uninitializes isochronous URBs, returns queued buffers with errors, unregisters the video node, disconnects the V4L2 device, sets `udev` to NULL for active users, and drops the V4L2 device reference.

## State and Persistence
Runtime state is stored in `struct stk1160`: USB handle, altsetting packet sizes, current alternate, selected input, norm, frame size, format, vb2 queue, I2C adapter/client, SAA711x subdevice, locks, and isochronous control. Hardware register state is programmed at probe by `stk1160_reg_reset()` and input selection. There is no persistent storage.

## Dependencies and Integration Points
The file integrates Linux USB control messages, V4L2 core, SAA711x I2C subdevice probing, the internal STK1160 I2C bridge, videobuf2 setup from `stk1160-v4l.c`, isochronous teardown from `stk1160-video.c`, and AC97 setup from `stk1160-ac97.c`.

## Risks and Edge Cases
Probe must register the video device last so users cannot race partially initialized state. `stk1160_scan_usb()` warns but still allows non-high-speed devices, where streaming may be unreliable. Input selection depends on fixed GPIO values and SAA7115 routing. Disconnect relies on lock ordering and `udev = NULL` to make active file operations fail safely. `stk1160_release()` unregisters I2C and V4L2 resources only after all references are gone.

## Test Signals
Test probe on video and audio interfaces, high-speed and full-speed ports, all alternate settings and packet-size detection, SAA711x subdevice creation, default input parameter, clean disconnect during idle and streaming, and V4L2 device reference release after user file descriptors close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-i2c.c

## Purpose
`stk1160-i2c.c` implements an I2C adapter over the STK1160's internal serial bus registers so the driver can control the external SAA711x video decoder.

## Important APIs, Types, and Functions
Important functions are `stk1160_i2c_busy_wait()`, `stk1160_i2c_write_reg()`, `stk1160_i2c_read_reg()`, `stk1160_i2c_check_for_device()`, `stk1160_i2c_xfer()`, `functionality()`, `stk1160_i2c_register()`, and `stk1160_i2c_unregister()`. The module parameter `i2c_debug` enables transfer logging. The adapter advertises `I2C_FUNC_SMBUS_EMUL`.

## Control Flow
Register setup copies adapter/client templates, parents the adapter to the USB interface device, stores the V4L2 device in adapter data, calls `i2c_add_adapter()`, and programs the STK1160 I2C clock divider and ASIC register. Transfers are limited to probe-only zero-length device checks, one-byte-register reads represented as write-one-byte followed by read-one-byte, and two-byte writes containing subaddress and value. Each low-level access programs the STK1160 serial address and bus registers, starts a read or write command, then waits for the relevant done bit in `STK1160_SICTL+1`.

## State and Persistence
The adapter and pseudo client live in `struct stk1160`. Hardware state includes serial device address, read/write subaddress/data registers, and the I2C clock divider. No transfer cache or persistent state exists.

## Dependencies and Integration Points
The file depends on core STK1160 register read/write helpers and register definitions. It integrates with Linux I2C core and V4L2 subdevice creation in `stk1160-core.c`.

## Risks and Edge Cases
The transfer function returns `num` even on some error paths, which can hide failed I2C transactions from callers. Read-without-register-selection and lengths other than the supported one- or two-byte patterns return `-EOPNOTSUPP` internally. Busy waits sleep in 10-20 ms ranges up to `STK1160_I2C_TIMEOUT`, so failed hardware can slow probe. Adapter unregister must not race active subdevice calls during disconnect.

## Test Signals
Test SAA711x detection at expected addresses, register read/write traffic with `i2c_debug=1`, timeout behavior when the decoder is absent, unsupported I2C message shapes, and adapter cleanup on failed probe and disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-reg.h

## Purpose
`stk1160-reg.h` defines symbolic register addresses and bit fields for the STK1160 USB capture bridge.

## Important APIs, Types, and Functions
The header declares register groups for GPIO and wakeup (`STK1160_GCTRL`, `STK1160_RMCTL`), strap state (`STK1160_POSV_*`), decoder/capture control (`STK1160_DCTRL`, `STK1160_DMCTRL*`, `STK116_CFSPO*`, `STK116_CFEPO*`), internal serial/I2C bus (`STK1160_SICTL*`, `STK1160_SBUSW*`, `STK1160_SBUSR*`, `STK1160_ASIC`), PLL/timing (`STK1160_PLLSO`, `STK1160_PLLFD`, `STK1160_TIGEN`, `STK1160_TICTL`), AC97/I2S (`STK1160_AC97*`, `STK1160_I2SCTL`), and EEPROM size.

## Control Flow
The header has no executable flow. It enables other STK1160 source files to program reset defaults, capture windows, decimation, serial-bus transactions, AC97 commands, and streaming start/stop using named offsets and bits.

## State and Persistence
It describes hardware register state only. The actual values are volatile device state set by probe, format/std changes, streaming, I2C transactions, and AC97 setup.

## Dependencies and Integration Points
The header is included by STK1160 core, V4L2, I2C, and AC97 files. It depends on Linux `BIT()` being available through included headers.

## Risks and Edge Cases
Register aliases with overlapping addresses require byte-offset correctness when writing adjacent high/low values. Incorrect decimation bit use can corrupt UYVY chroma alignment. POSV strap bits determine whether AC97 setup is attempted; wrong bit definitions would affect audio initialization.

## Test Signals
Validate register writes with USB trace or debug register ioctls, standard-specific capture-window programming, decimation controls, I2C read/write completion bits, AC97 command bits, and start/stop writes to `STK1160_DCTRL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-v4l.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-v4l.c

## Purpose
`stk1160-v4l.c` implements the V4L2 ioctl surface, vb2 queue policy, format/standard/input selection, streaming start/stop orchestration, and queue cleanup for the STK1160 driver.

## Important APIs, Types, and Functions
Key helpers are `stk1160_set_std()`, `stk1160_set_fmt()`, `stk1160_set_alternate()`, `stk1160_start_streaming()`, `stk1160_stop_hw()`, `stk1160_stop_streaming()`, `stk1160_try_fmt()`, `stk1160_clear_queue()`, `stk1160_vb2_setup()`, and `stk1160_video_register()`. The V4L2 callback tables are `stk1160_fops`, `stk1160_ioctl_ops`, `stk1160_video_qops`, and `v4l_template`. The `keep_buffers` module parameter preserves allocated isochronous buffers across stream stops.

## Control Flow
Video registration initializes defaults to NTSC 720x480 UYVY, programs standard registers, propagates the standard to the SAA711x subdevice, then registers the video node. Format negotiation clamps requested size to the base standard size and computes decimation controls that preserve UYVY alignment. `VIDIOC_S_FMT` rejects busy queues, stores width/height, and writes decimation registers. Streaming start checks device presence, locks V4L state, selects a USB alternate setting with enough isochronous packet size, allocates/reallocates isochronous URBs if needed, submits them, starts the decoder subdevice, resets sequence, and writes STK1160 capture-control registers. Streaming stop cancels URBs, optionally frees them, stops hardware and decoder, resets alternate 0, and returns queued/current buffers with errors.

## State and Persistence
The file manages current norm, width, height, format, input, sequence counter, USB alternate, max packet size, and vb2 queue contents in `struct stk1160`. Hardware state includes capture window registers, decimation registers, alternate interface, decoder stream state, and DCTRL capture enable. State is volatile and reset on disconnect or reconfiguration.

## Dependencies and Integration Points
It depends on V4L2 core, videobuf2 vmalloc, SAA7115 subdevice calls, STK1160 register helpers, and isochronous allocation/cancel/free helpers from `stk1160-video.c`. It also integrates optional advanced debug register ioctls with direct STK1160 register access.

## Risks and Edge Cases
`stk1160_set_alternate()` uses a fixed `STK1160_MIN_PKT_SIZE` rather than deriving bandwidth from current size/fps, so unusual settings may select suboptimal bandwidth. Decimation math uses an unbounded search for the next divisor, though inputs are clamped to reasonable dimensions. Buffer queueing returns buffers immediately on disconnect; callers should see errors rather than hangs. Start failure must unwind URBs, alternate setting, and queued buffers without leaving the decoder streaming.

## Test Signals
Exercise `VIDIOC_ENUM_FMT`, `TRY_FMT`/`S_FMT` for standard and decimated sizes, busy-queue rejection for format/std changes, NTSC/PAL standard changes, all composite/S-Video inputs, read/mmap/userptr/dmabuf queue modes, stream start failure injection, `keep_buffers` behavior, advanced debug register access, and disconnect during active vb2 queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-v4l.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-video.c

## Purpose
`stk1160-video.c` owns STK1160 isochronous USB transfer allocation, completion handling, packet parsing, field interlacing, and copying captured video into queued vb2 buffers.

## Important APIs, Types, and Functions
Important functions are `stk1160_next_buffer()`, `stk1160_buffer_done()`, `stk1160_copy_video()`, `stk1160_process_isoc()`, `stk1160_isoc_irq()`, `stk1160_cancel_isoc()`, `stk1160_free_isoc()`, `stk1160_uninit_isoc()`, `stk1160_fill_urb()`, and `stk1160_alloc_isoc()`. The `debug` module parameter controls packet-level logging.

## Control Flow
`stk1160_alloc_isoc()` allocates up to `STK1160_NUM_BUFS` URBs, each with `STK1160_NUM_PACKETS` packet descriptors sized from the selected alternate setting. Submitted URBs complete in `stk1160_isoc_irq()`, which ignores unlink/shutdown statuses, processes packet data, clears packet status/length fields, and resubmits the URB. `stk1160_process_isoc()` walks each isochronous packet: `0xc0` starts a second field and can complete the previous frame, `0x80`/`0xc0` mark field parity and reset position, and data packets are copied into the current buffer. `stk1160_copy_video()` skips a 4-byte packet header and interlaces field lines into the destination based on the current odd/even field and line offset. When a frame completes, `stk1160_buffer_done()` sets sequence, field, timestamp, payload bytes, and marks the vb2 buffer done.

## State and Persistence
State lives in `dev->isoc_ctl`: current URB count, max packet size, per-URB transfer buffers, and the current partially filled `stk1160_buffer`. Per-buffer state tracks memory, length, bytes used, current position, and odd/even field. No state is persisted beyond active streaming.

## Dependencies and Integration Points
The file depends on Linux USB isochronous URB APIs, noncoherent USB transfer buffer allocation, vb2 buffer completion, and the queue/list state managed by `stk1160-v4l.c`. It uses endpoint `STK1160_EP_VIDEO`.

## Risks and Edge Cases
Packet parsing relies on first-byte field markers and can lose sync if the device emits unexpected packet headers. Copy code contains several bounds checks and ratelimited warnings; wrong standard/format settings can trigger out-of-bounds offsets or incomplete frames. Allocation can continue with fewer URBs only if at least `STK1160_MIN_BUFS` is available. URBs must be killed before freeing transfer buffers or clearing the current buffer.

## Test Signals
Test stable streaming with all supported alternate settings, frame sequence increments, correct field interlace ordering, bounds-warning absence under NTSC/PAL, behavior under USB packet errors (`-EOVERFLOW`, `-EPROTO`, `-EILSEQ`), partial URB allocation, URB cancellation on streamoff, and disconnect while completion callbacks are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160.h

## Purpose
`stk1160.h` is the internal shared header for the STK1160 driver. It defines constants, logging helpers, capture buffer structures, the central `struct stk1160`, and cross-file prototypes.

## Important APIs, Types, and Functions
Important constants include `STK1160_VERSION`, `STK1160_NUM_PACKETS`, `STK1160_NUM_BUFS`, `STK1160_EP_VIDEO`, `STK1160_EP_AUDIO`, input limits, AC97 timeout, and I2C timeout. Core types include `struct stk1160_buffer`, `struct stk1160_urb`, `struct stk1160_isoc_ctl`, `struct stk1160_fmt`, `struct stk1160`, and `struct regval`. Prototypes connect V4L2 setup/register/queue cleanup, isochronous allocation/free/cancel/uninit, I2C register/unregister, register read/write, input selection, and AC97 setup.

## Control Flow
The header has no executable flow, but it defines the shared object model used by all STK1160 source files: USB probe creates `struct stk1160`, V4L2 code owns `vb_vidq` and `avail_bufs`, video code owns `isoc_ctl`, I2C code owns `i2c_adap`/`i2c_client`, and core release tears the whole object down.

## State and Persistence
`struct stk1160` holds all driver runtime state: V4L2 device/node, controls, USB device, SAA711x subdevice, buffer queue, alternate-setting metadata, current norm/format/input, sequence, I2C bridge objects, locks, current file-handle owner, and experimental sound-card pointer. State is runtime-only.

## Dependencies and Integration Points
The header depends on Linux I2C, ALSA AC97/core declarations, videobuf2-v4l2, V4L2 device/control APIs, and internal register definitions included by implementation files.

## Risks and Edge Cases
The structure centralizes ownership for multiple asynchronous domains: USB callbacks, V4L2 ioctls, vb2 operations, and I2C subdevice access. Callers must consistently use `v4l_lock`, `vb_queue_lock`, and `buf_lock` as intended. Endpoint constants are noted as TODOs and may not fit every clone if endpoint descriptors differ.

## Test Signals
Compile-test all STK1160 objects together, run lockdep under stream/disconnect stress, verify endpoint assumptions against descriptors, and validate that all prototypes remain matched after any object split changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-budget/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-budget/Kconfig

## Purpose
This Kconfig entry enables DVB support for Technotrend/Hauppauge Nova-USB budget adapters.

## Important APIs, Types, and Functions
The symbol is `DVB_TTUSB_BUDGET`, a `tristate` depending on `DVB_CORE && USB && I2C && PCI`. It conditionally selects frontend/tuner helpers (`DVB_CX22700`, `DVB_TDA1004X`, `DVB_VES1820`, `DVB_TDA8083`, `DVB_STV0299`, `DVB_STV0297`, `DVB_LNBP21`) when `MEDIA_SUBDRV_AUTOSELECT` is enabled.

## Control Flow
Enabling the symbol builds the budget USB DVB driver and, under autoselect, pulls in the demodulator and LNB helper modules used by runtime frontend probing.

## State and Persistence
The file contributes compile-time configuration only. Runtime firmware and DVB state live in `dvb-ttusb-budget.c`.

## Dependencies and Integration Points
It integrates with DVB core, USB, I2C, historical PCI dependency requirements for DVB infrastructure, and the media subdevice autoselection system.

## Risks and Edge Cases
If `MEDIA_SUBDRV_AUTOSELECT` is disabled, users must manually enable the relevant frontend modules or runtime frontend attach will fail. The PCI dependency is surprising for a USB device and reflects shared DVB adapter infrastructure expectations in this tree.

## Test Signals
Build with autoselect on/off, verify frontend symbols are selected as expected, and test module loading with the required demodulator modules present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-budget/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-budget/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-budget/Makefile

## Purpose
The Makefile builds the TTUSB budget DVB driver and adds the DVB frontend include path.

## Important APIs, Types, and Functions
It maps `obj-$(CONFIG_DVB_TTUSB_BUDGET) += dvb-ttusb-budget.o` and adds `-I $(srctree)/drivers/media/dvb-frontends`.

## Control Flow
Kbuild compiles `dvb-ttusb-budget.c` when the Kconfig symbol is enabled. The include path resolves frontend configuration headers such as `stv0299.h`, `tda1004x.h`, and `ves1820.h`.

## State and Persistence
This is build-only state.

## Dependencies and Integration Points
It depends on the `DVB_TTUSB_BUDGET` Kconfig symbol and the in-tree DVB frontend headers.

## Risks and Edge Cases
Moving frontend headers or renaming the Kconfig symbol will break the build. Additional split objects would need explicit Makefile updates.

## Test Signals
Compile with `CONFIG_DVB_TTUSB_BUDGET=m` and confirm the frontend include headers resolve and `dvb-ttusb-budget.ko` links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-budget/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-budget/dvb-ttusb-budget.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-budget/dvb-ttusb-budget.c

## Purpose
`dvb-ttusb-budget.c` is the DVB driver for Technotrend/Hauppauge Nova-USB budget devices without an onboard MPEG decoder. It boots the device DSP, exposes a DVB adapter/demux/net interface, implements an I2C bridge to frontends/tuners, parses the device mux stream from isochronous USB packets, and attaches multiple possible DVB-S/T/C frontend combinations by USB product ID.

## Important APIs, Types, and Functions
The central type is `struct ttusb`, whose first field is `struct dvb_demux` to support casts from demux feed callbacks. Important functions include `ttusb_cmd()`, `ttusb_i2c_msg()`, `master_xfer()`, `ttusb_boot_dsp()`, `ttusb_init_controller()`, `ttusb_set_channel()`, `ttusb_del_channel()`, `ttusb_process_frame()`, `ttusb_process_muxpack()`, `ttusb_iso_irq()`, `ttusb_start_iso_xfer()`, `ttusb_stop_iso_xfer()`, `ttusb_start_feed()`, `ttusb_stop_feed()`, `frontend_init()`, `ttusb_probe()`, and `ttusb_disconnect()`. The driver registers USB IDs `0x0b48:0x1003`, `0x1004`, and `0x1005`.

## Control Flow
Probe binds interface 1, allocates state, sets USB interface altsetting, allocates isochronous URBs, initializes the controller by reset commands, DSP firmware upload (`ttusb-budget/dspbootcode.bin`), I2C bitrate setup, and version queries, then registers a DVB adapter, I2C adapter, demux, dmxdev, and DVB net. `frontend_init()` chooses frontend attachments by product ID and fallback probing order. Starting the first demux feed sends a device channel command for the PID and starts isochronous transfers. URB completions feed packets to `ttusb_process_frame()`, a state machine that searches for three `0xaa` sync bytes, reads muxpack count, accumulates muxpack payloads, validates checksum/counter continuity, and forwards TS packets to `dvb_dmx_swfilter_packets()`. Stopping the final feed deletes the channel and kills URBs. Disconnect stops streaming and releases DVB, frontend, I2C, URB, and adapter resources.

## State and Persistence
Runtime state includes USB pipe numbers, transaction counter, frontend pointer, I2C locks, demux/feed counts, active isochronous URBs, mux parser state, continuity counter, LNB voltage/tone state, firmware/controller revision, and last command result buffer. Firmware is persisted externally as `ttusb-budget/dspbootcode.bin`; other state is volatile.

## Dependencies and Integration Points
The driver depends on USB bulk/isochronous APIs, Linux firmware loader, I2C core, DVB adapter/demux/dmxdev/net, and numerous DVB frontend modules (`cx22700`, `tda1004x`, `ves1820`, `tda8083`, `stv0299`, `stv0297`, `lnbp21`). It exposes an I2C adapter used by attached demods and tuner callbacks and uses DVB feed callbacks for PID-based streaming.

## Risks and Edge Cases
The command helper serializes USB control traffic but uses fixed packet/result sizes, so unexpected firmware responses can desynchronize higher-level commands. The mux parser has hard `BUG_ON()` for pointer overflow and logs continuity/checksum errors; malformed USB data can cause packet loss or warnings. Hardware section filtering is disabled and incomplete. Frontend attach depends on product ID and probing order; missing modules or different board revisions leave no frontend. Isochronous streaming starts only when the first feed starts, so feed-count accounting must stay balanced.

## Test Signals
Test DSP firmware request/upload, STC/DSP version logging, frontend attach for product IDs `1003/1004/1005`, I2C transfer through each tuner path, DVB scan/lock for DVB-S/T/C variants, LNB voltage/tone for satellite boards, demux start/stop feed balance, TS packet continuity under load, DVB net traffic, disconnect while feeds are active, and operation with frontend modules absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-budget/dvb-ttusb-budget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/Kconfig

## Purpose
This Kconfig entry enables support for Technotrend/Hauppauge DEC USB DVB devices.

## Important APIs, Types, and Functions
The symbol is `DVB_TTUSB_DEC`, a `tristate` depending on `DVB_CORE && USB && INPUT && PCI`, and selecting `CRC32`.

## Control Flow
When enabled, the companion Makefile builds both the DEC USB transport and its small frontend module. `CRC32` is required for firmware validation in the driver.

## State and Persistence
The file controls compile-time configuration only. Runtime firmware and DVB state are implemented in `ttusb_dec.c` and `ttusbdecfe.c`.

## Dependencies and Integration Points
It integrates DVB, USB, input subsystem support for the optional IR remote, and CRC32 firmware checks.

## Risks and Edge Cases
The help text documents required firmware files and paths; without them probe can fail or leave the device uninitialized. The PCI dependency is inherited from the DVB stack rather than the USB hardware itself.

## Test Signals
Build with `CONFIG_DVB_TTUSB_DEC=m`, verify `CRC32` selection, and test module loading with and without the expected firmware files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/Makefile

## Purpose
The Makefile builds the TTUSB DEC transport and frontend support objects.

## Important APIs, Types, and Functions
It maps `obj-$(CONFIG_DVB_TTUSB_DEC) += ttusb_dec.o ttusbdecfe.o`.

## Control Flow
Kbuild compiles and links both C files into the DEC driver when the Kconfig symbol is enabled.

## State and Persistence
No runtime state exists here.

## Dependencies and Integration Points
The mapping ensures `ttusb_dec.c` can call the attach functions exported from `ttusbdecfe.c` in the same build unit/module set.

## Risks and Edge Cases
Both objects are required; omitting `ttusbdecfe.o` leaves unresolved attach symbols or no frontend support.

## Test Signals
Build `CONFIG_DVB_TTUSB_DEC=m` and confirm both objects are linked into the produced module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/ttusb_dec.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/ttusb_dec.c

## Purpose
`ttusb_dec.c` supports Technotrend/Hauppauge DEC2000-t, DEC2540-t, and DEC3000-s USB DVB boxes with onboard firmware and MPEG/PVA transport behavior. It handles firmware boot, command/result bulk protocol, isochronous receive parsing, DVB demux/net registration, optional IR remote input, and section/PVA stream conversion to DVB feed callbacks.

## Important APIs, Types, and Functions
Central state is `struct ttusb_dec`, containing model metadata, DVB adapter/demux/dmxdev/net/frontend, PID selections, USB pipes, ISO/IRQ URBs, packet parser state, PES-to-TS converters, frame bottom-half work, filter-info list, input device, and active flag. Important functions include `ttusb_dec_send_command()`, `ttusb_dec_get_stb_state()`, `ttusb_dec_boot_dsp()`, `ttusb_dec_init_stb()`, `ttusb_dec_init_usb()`, `ttusb_dec_init_dvb()`, `ttusb_dec_start_feed()`, `ttusb_dec_stop_feed()`, `ttusb_dec_process_urb()`, `ttusb_dec_process_urb_frame_list()`, `ttusb_dec_process_urb_frame()`, `ttusb_dec_process_packet()`, `ttusb_dec_process_pva()`, `ttusb_dec_process_filter()`, `ttusb_init_rc()`, `ttusb_dec_probe()`, and `ttusb_dec_disconnect()`.

## Control Flow
Probe allocates state, selects model/firmware name by USB product ID, initializes USB pipes and URBs, queries firmware state, boots DSP firmware if needed after CRC32 and CRC16 validation, initializes DVB adapter/demux/frontend, attaches DVB-T or DVB-S frontend wrappers, initializes parser/filter/workqueue state, switches to the input streaming interface, and optionally starts the interrupt URB for remote control. Commands are serialized with `usb_mutex`, sent as `0xaa` transaction packets on the command pipe, and answered on the result pipe. Isochronous URB completions copy frame data into `struct urb_frame` allocations and queue bottom-half work. The work parser byte-swaps frames, searches for sync, determines PVA/section/empty packets, validates checksum and packet IDs, then forwards PVA video/audio through PES-to-TS conversion or section packets to registered filters. DVB feed start programs PIDs or section filters with device commands, increments stream counts, and starts ISO transfers; stop removes filters/PIDs and stops ISO when counts reach zero.

## State and Persistence
Persistent external artifacts are model firmware files `dvb-ttusb-dec-2000t.fw`, `dvb-ttusb-dec-2540t.fw`, and `dvb-ttusb-dec-3000s.fw`. Runtime state includes USB interface mode, transaction count, iso stream count, parser state, next packet ID, PVA/filter stream counts, selected PID array, section filter mapping list, pending bottom-half frame list, optional remote input state, and whether firmware supports playback. All runtime state is freed on disconnect.

## Dependencies and Integration Points
The file depends on USB bulk/iso/int APIs, firmware loader, CRC32, input subsystem, workqueues, DVB adapter/demux/dmxdev/net APIs, and local frontend attach helpers from `ttusbdecfe.h`. It registers USB IDs `0x0b48:0x1006`, `0x1008`, and `0x1009`.

## Risks and Edge Cases
Firmware validation has multiple failure modes: unavailable file, too-small file, CRC mismatch, and command failure. Isochronous completion allocates frame wrappers with `GFP_ATOMIC`; allocation failure silently drops frames. Parser state handles odd section payloads, byte swapping, packet loss warnings, and PVA postbyte stitching; malformed streams can produce drops or warnings. `ttusb_dec_stop_iso_xfer()` decrements stream count without an explicit underflow guard. Remote-control key repeat is simplified as immediate down/up events. Disconnect cleanup only runs full teardown when `active` is set, so failures before that rely on probe error paths.

## Test Signals
Test all three model IDs, firmware boot and already-booted firmware paths, CRC failure handling, DVB-T and DVB-S frontend attach, section filters and audio/video PVA feeds, `output_pva` behavior, stream count balance under multiple feeds, packet-loss/checksum logging with corrupted data, remote control with `enable_rc=1`, suspend-like interface switches, and disconnect during queued bottom-half work and active ISO transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/ttusb_dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/ttusbdecfe.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/ttusbdecfe.c

## Purpose
`ttusbdecfe.c` implements lightweight DVB-T and DVB-S frontend wrappers for TTUSB DEC devices. It translates frontend operations into firmware commands sent through a callback supplied by `ttusb_dec.c`.

## Important APIs, Types, and Functions
`struct ttusbdecfe_state` stores the `ttusbdecfe_config`, embedded `dvb_frontend`, high-band flag, and LNB voltage. Important functions are `ttusbdecfe_dvbt_attach()`, `ttusbdecfe_dvbs_attach()`, `ttusbdecfe_release()`, `ttusbdecfe_dvbt_set_frontend()`, `ttusbdecfe_dvbt_read_status()`, `ttusbdecfe_dvbt_get_tune_settings()`, `ttusbdecfe_dvbs_set_frontend()`, `ttusbdecfe_dvbs_read_status()`, `ttusbdecfe_dvbs_diseqc_send_master_cmd()`, `ttusbdecfe_dvbs_set_tone()`, and `ttusbdecfe_dvbs_set_voltage()`. It exports both attach symbols.

## Control Flow
Attach allocates state, stores the config callback, copies the appropriate static `dvb_frontend_ops`, and returns the embedded frontend. DVB-T tuning sends command `0x71` with frequency in kHz and fixed parameters; status command `0x73` maps firmware status values to DVB frontend lock flags or timeout. DVB-S tuning adds LOF high/low offset based on tone state, sends frequency, symbol rate, band, and voltage with command `0x71`; DVB-S status currently reports lock unconditionally. DiSEqC sends command `0x72`, while tone and voltage setters update state used by the next tune command.

## State and Persistence
State is per frontend allocation: config pointer, high-band selection, and LNB voltage. No hardware state is cached beyond these fields, and no persistent storage exists.

## Dependencies and Integration Points
The file depends on DVB frontend core and `ttusbdecfe_config.send_command`, which is supplied by the parent USB driver. It defines frontend capability ranges for DVB-T and DVB-S.

## Risks and Edge Cases
DVB-S `read_status()` always reports full lock, so applications may not detect actual signal loss. Command return values from set-frontend paths are ignored, hiding firmware errors. DVB-T status requires an exact four-byte reply. DiSEqC validates maximum command length but otherwise trusts firmware delivery. State changes for tone/voltage do not immediately send hardware commands until tuning.

## Test Signals
Test DVB-T tuning/status values 1-4, DVB-S tuning with 13/18 V and tone on/off, DiSEqC length rejection and delivery, frontend release, and behavior when the parent send-command callback returns errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/ttusbdecfe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/ttusbdecfe.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/ttusbdecfe.h

## Purpose
`ttusbdecfe.h` declares the private interface between the TTUSB DEC USB transport and its frontend wrappers.

## Important APIs, Types, and Functions
The key type is `struct ttusbdecfe_config`, containing a `send_command` callback with DVB frontend pointer, command byte, parameter buffer, result length, and result buffer. It declares `ttusbdecfe_dvbs_attach()` and `ttusbdecfe_dvbt_attach()`.

## Control Flow
The parent driver provides a config with a callback that routes frontend requests to the USB command protocol. The attach functions consume that config and return a DVB frontend for registration.

## State and Persistence
The header defines no state directly. The callback pointer is stored by the frontend state allocated in `ttusbdecfe.c`.

## Dependencies and Integration Points
It depends on Linux DVB frontend declarations and is included by both the USB driver and frontend implementation.

## Risks and Edge Cases
The callback is required for all meaningful frontend operations; a NULL or invalid callback would fail at runtime. The interface is synchronous and assumes the parent driver serializes USB command traffic.

## Test Signals
Compile-test both including files, verify attach symbols link, and test callback error propagation from parent USB command failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/ttusbdecfe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/Kconfig

## Purpose
This Kconfig entry enables USBTV007-based video capture support.

## Important APIs, Types, and Functions
The symbol is `VIDEO_USBTV`, a `tristate` depending on `VIDEO_DEV && SND`, selecting `SND_PCM` and `VIDEOBUF2_VMALLOC`.

## Control Flow
Enabling the symbol builds the USBTV composite module from core, video, and audio objects through the companion Makefile. The selected ALSA PCM and vb2 vmalloc support match the driver's audio and video buffering implementations.

## State and Persistence
This file has compile-time configuration state only.

## Dependencies and Integration Points
It integrates with V4L2 video core, ALSA sound support, ALSA PCM, and videobuf2 vmalloc.

## Risks and Edge Cases
Unlike STK1160, USBTV includes its own audio object, so sound dependencies are required. Missing `SND_PCM` or vb2 vmalloc would break build/runtime capture paths.

## Test Signals
Build with `CONFIG_VIDEO_USBTV=m`, confirm ALSA PCM and vb2 vmalloc are selected, and verify `usbtv.ko` includes audio/video support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/Makefile

## Purpose
The Makefile defines the composite USBTV007 module.

## Important APIs, Types, and Functions
`usbtv-y` includes `usbtv-core.o`, `usbtv-video.o`, and `usbtv-audio.o`; `obj-$(CONFIG_VIDEO_USBTV) += usbtv.o`.

## Control Flow
Kbuild links the three implementation objects into one built-in object or module when `CONFIG_VIDEO_USBTV` is enabled.

## State and Persistence
No runtime state exists here; this file only defines build composition.

## Dependencies and Integration Points
The object list maps the driver's main subsystems: USB/core probe, V4L2 video capture, and ALSA audio capture.

## Risks and Edge Cases
All three objects are needed for the advertised Kconfig support. Adding feature splits requires updating `usbtv-y`.

## Test Signals
Build with `CONFIG_VIDEO_USBTV=m` and confirm the final `usbtv` module includes core, video, and audio objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/Makefile -->
