# subset-b-004207 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-dvb.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-dvb.c

Purpose: implements the em28xx digital-TV extension. It binds DVB frontends to supported Empia USB capture boards, configures board-specific GPIO/I2C/tuner/demodulator combinations, registers the DVB adapter/demux/net stack, and routes USB transport-stream URB payloads into the DVB software demux.

Important APIs/types/functions: `struct em28xx_dvb` stores frontend pointers, DVB adapter/demux/dmxdev/net objects, feed count state, DRX-K gate serialization, and I2C module clients. `em28xx_dvb_urb_data_copy()` accepts bulk or isochronous URBs and calls `dvb_dmx_swfilter()`. `em28xx_start_feed()` and `em28xx_stop_feed()` guard `nfeeds` with `dvb->lock` and start/stop USB transfers on the first/last active feed. `em28xx_register_dvb()` builds the DVB adapter, frontends, demux frontends, `dmxdev`, DVB network interface, and optional media graph. `em28xx_dvb_init()` is the large board switch that attaches demodulators/tuners via `dvb_attach()` or `dvb_module_probe()`. `em28xx_dvb_fini()`, suspend, and resume implement lifecycle.

Control flow: extension registration installs `dvb_ops`. On device init, unsupported/audio-only boards return early. Supported devices allocate `struct em28xx_dvb`, preallocate digital URBs, take `dev->lock`, switch to digital mode, run the board-specific frontend attach path, install tuner callbacks and transport bus control, register DVB core objects, set the USB alternate setting, then suspend the bridge mode until use. Runtime feed activation starts digital USB transfers with either bulk endpoint parameters or isochronous altsetting parameters. URB completion copies TS bytes into the demux. Teardown stops/uninitializes URBs, prevents frontend sleep callbacks after disconnect, unregisters DVB objects, releases probed I2C clients, frees `dvb`, and drops the device kref.

State and persistence: persistent runtime state is in `dev->dvb`, frontend operation tables, I2C client handles, `nfeeds`, `lna_gpio`, `dont_attach_fe1`, `pll_mutex`, and bridge mode/USB allocation state. Board-specific init sequences write GPIO and tuner/demod registers but do not persist beyond hardware state. The module parameter `debug` controls logging and `adapter_nr` controls DVB adapter numbering.

Dependencies and integration points: depends on the shared em28xx core (`em28xx_set_mode`, `em28xx_init_usb_xfer`, `em28xx_uninit_usb_xfer`, `em28xx_gpio_set`, tuner callbacks), Linux USB, DVB core, media controller, and many frontend/tuner drivers (`lgdt330x`, `si2168`, `si2157`, `m88ds3103`, `drxk`, `tda18271`, `mxl692`, etc.). It shares I2C adapters from `em28xx-i2c.c` and coordinates analog/digital mode with the V4L2 extension through `ts_bus_ctrl`.

Risks: the board switch has many hand-coded failure paths, so missing detach/release calls can leak frontend modules or leave bridge mode active. Several initialization arrays are magic register traces with timing dependencies. Dual-frontend boards share tuner state and require careful `dont_attach_fe1`/tuner op handling. URB errors are mostly logged and skipped; persistent packet loss manifests as demux errors rather than direct failures. LNA GPIO handling depends on legacy gpiolib availability. Tests should cover modprobe/unload, board-specific attach failures, feed start/stop under concurrent demux users, suspend/resume, disconnect during active DVB streaming, media graph creation, and transport lock/channel quality from userspace tools such as `dvbv5-scan`/`dvbv5-zap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-dvb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-i2c.c

Purpose: provides Linux I2C adapter support for em28xx bridge chips, including legacy EM2800 transactions, normal EM28XX transactions, secondary EM25XX/Bus B access, optional I2C scan logging, and EEPROM discovery/parsing.

Important APIs/types/functions: `em28xx_i2c_register()` and `em28xx_i2c_unregister()` publish/remove an `i2c_adapter` per bus. `em28xx_i2c_xfer()` is the `master_xfer` implementation and dispatches to algorithm-specific send/receive/check helpers. `em28xx_i2c_timeout()` computes transfer timeouts from bridge speed. `em28xx_i2c_read_block()` reads EEPROM/register blocks in chunks. `em28xx_i2c_eeprom()` detects EEPROM format, hashes contents, prints board configuration, and returns `dev->eedata`. `em28xx_do_i2c_scan()` probes 7-bit addresses and records `dev->i2c_hash`.

Control flow: adapter registration copies templates, attaches `struct em28xx_i2c_bus` as `algo_data`, registers the adapter, initializes the internal client, and on bus 0 attempts EEPROM parsing. Each I2C transfer rejects disconnected devices, takes `dev->i2c_bus_lock` with `rt_mutex_trylock()`, switches the hardware selected bus if needed, executes each message as presence check/read/write, and unlocks. EM2800 paths use short reversed bridge-register transactions. EM28XX paths use USB control requests and status register `0x05`. EM25XX Bus B paths use request `0x06` and status request `0x08`.

State and persistence: mutates `dev->cur_i2c_bus`, `dev->eedata`, `dev->eedata_len`, `dev->hash`, `dev->i2c_hash`, `dev->analog_xfer_mode`, and each `dev->i2c_client[bus].addr` during probing. EEPROM data is heap allocated and kept on the device for board detection and later consumers. Module parameters `i2c_scan` and `i2c_debug` alter scan behavior/logging.

Dependencies and integration points: sits below the V4L2, DVB, audio, camera, and input extensions that instantiate subdevices or direct clients on these adapters. It relies on low-level USB control callback pointers in `struct em28xx`, Linux I2C core, `v4l2-common`, and tuner/xc2028 helpers.

Risks: `rt_mutex_trylock()` returns `-EAGAIN`, so callers must tolerate transient bus contention. Presence checks on unsupported Bus B hardware may falsely succeed. The EEPROM parser assumes 256-byte hardware datasets even for new 16-bit-address EEPROM formats. Several status interpretations are empirical, especially clock-stretch timeout handling. Tests should include I2C scan on known boards, EEPROM-present/absent/corrupt cases, both primary and secondary buses, disconnect-time subdevice release, large block reads over EM2800 vs newer chips, and tuner/demod module probe sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-input.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-input.c

Purpose: implements the em28xx input extension for remote controls and board buttons. It supports external I2C IR receivers, internal bridge IR polling, snapshot buttons, and illumination toggles.

Important APIs/types/functions: `struct em28xx_IR` stores `rc_dev`, polling work, protocol state, I2C client, and key-read callbacks. I2C key readers include `em28xx_get_key_terratec()`, `em28xx_get_key_em_haup()`, `em28xx_get_key_pinnacle_usb_grey()`, and `em28xx_get_key_winfast_usbii_deluxe()`. Internal readers are `default_polling_getkey()` and `em2874_polling_getkey()`. Protocol changes are handled by `em2860_ir_change_protocol()`, `em2874_ir_change_protocol()`, and `em28xx_ir_change_protocol()`. Button handling uses `em28xx_query_buttons()`, `em28xx_init_buttons()`, and `em28xx_shutdown_buttons()`.

Control flow: extension init takes a device kref, initializes button polling work, registers a snapshot input device if configured, probes external I2C IR when requested, allocates an `rc_dev`, selects the key map and key reader based on board or chip id, and registers the rc-core device. `rc->open` starts delayed polling work; `rc->close` cancels it. Each poll reads either an external I2C chip or bridge IR registers, translates protocol/scancode, and reports `rc_keydown()`. Button polling reads configured registers, debounces via last values, clears latch registers when needed, emits snapshot key events, or toggles illumination GPIO bits.

State and persistence: stores `dev->ir`, `ir->last_readcount`, active `ir->rc_proto`, `ir->full_code`, synthetic I2C client state, delayed works, button polling address/value arrays, `dev->sbutton_input_dev`, and modified `dev->board.xclk` IR mode bits. No persistent disk state exists.

Dependencies and integration points: uses rc-core, input core, Linux I2C, USB input IDs, em28xx register callbacks, board button/LED metadata, and shared extension lifecycle. It depends on register definitions from `em28xx-reg.h` for IR and XCLK programming.

Risks: an init path that finds no remote support returns without dropping the kref acquired at function entry, so lifetime assumptions should be checked against the larger driver. Internal polling semantics differ across chip IDs because some readcount fields clear on read. Protocol switching mutates board XCLK and can affect IR decoding if a userspace keymap requests unsupported protocols. Button polling has a fixed maximum number of addresses and warns if board data exceeds it. Tests should cover rc-core open/close, protocol switching, repeated key holds, I2C receiver absence, snapshot input registration/unregistration, suspend/resume work cancellation, and LED toggle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-reg.h

Purpose: centralizes em28xx bridge register addresses, bit masks, GPIO/GPO flags, output/capture format values, transport-stream enable bits, audio source constants, and chip IDs used by the em28xx modules.

Important APIs/types/functions: this header is macro/enum only. It defines GPIO bit helpers (`EM_GPIO_*`, `EM_GPO_*`), endpoint constants, chip configuration bits, I2C clock and bus-select bits, XCLK/IR mode bits, video input/output registers (`EM28XX_R10_VINMODE`, `EM28XX_R11_VINCTRL`, `EM28XX_R27_OUTFMT`), color defaults, capture window/scaler registers, VBI registers, AC97 registers, IR registers, TS packet/enable registers, audio source values, and `enum em28xx_chip_id`.

Control flow: none directly; consumers use the constants to program bridge hardware. Video setup writes output/scaler/VBI constants, I2C code manipulates `EM28XX_R06_I2C_CLK`, input code reads IR registers and writes IR config, DVB code enables transport streams and GPIO sequences, and core/audio code controls suspend/audio paths.

State and persistence: no runtime state. The risk profile is contractual: values here encode hardware semantics and are shared across all em28xx source files.

Dependencies and integration points: included by `em28xx.h`, which exposes it to the driver family. It depends on kernel `BIT()` being available through including context. It is an integration point with datasheet/USB-trace-derived bridge programming and with board definitions in `em28xx-cards.c`.

Risks: wrong constants silently program hardware incorrectly. Several comments flag uncertain or family-specific meanings, especially camera bridge registers and built-in decoder behavior. Chip IDs are incomplete by comment, so new boards may need updates. Tests should be indirect: validate I2C bus switching, IR protocol selection, VBI capture dimensions, analog color control registers, DVB TS enablement, suspend/resume GPIO effects, and chip-id-specific branches on representative hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-v4l.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-v4l.h

Purpose: exposes the small cross-file V4L/VBI interface between `em28xx-video.c` and `em28xx-vbi.c`.

Important APIs/types/functions: declares `em28xx_start_analog_streaming()`, `em28xx_stop_vbi_streaming()`, and `extern const struct vb2_ops em28xx_vbi_qops`. These let the VBI queue reuse the analog streaming engine while keeping VBI queue setup and buffering in `em28xx-vbi.c`.

Control flow: `em28xx-vbi.c` assigns `em28xx_start_analog_streaming` and `em28xx_stop_vbi_streaming` into its `vb2_ops`; `em28xx-video.c` owns the implementations and initializes the VBI queue with `em28xx_vbi_qops`.

State and persistence: no state is stored in this header. The functions operate on `vb2_queue` driver-private `struct em28xx` state at runtime.

Dependencies and integration points: relies on videobuf2 types being visible through included implementation files. It is the compile-time contract between analog video and VBI support.

Risks: because the header is minimal, signature drift between video and VBI code would break compilation. Behavioral risk is in the shared streaming refcount/resource logic: VBI and video queues both affect `streaming_users` and USB URBs. Test signals are successful build, simultaneous/sequential video and VBI streamon/streamoff, and VBI device registration only when supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-v4l.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-vbi.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-vbi.c

Purpose: implements raw VBI videobuf2 queue operations for em28xx analog capture.

Important APIs/types/functions: `vbi_queue_setup()` computes VBI buffer size as `vbi_width * vbi_height * 2` and enforces at least two buffers. `vbi_buffer_prepare()` validates plane size and sets payload. `vbi_buffer_queue()` maps the vmalloc plane, stores buffer length, and enqueues the buffer on `dev->vbiq.active` under `dev->slock`. `em28xx_vbi_qops` wires these callbacks to the shared analog start/stop functions.

Control flow: the V4L2 init path in `em28xx-video.c` initializes `vb_vbiq` with these ops and registers a VBI video device when `em28xx_vbi_supported()` is true. Userspace queues VBI buffers; queued buffers are consumed by the analog URB parser in `em28xx-video.c` when VBI headers/data arrive. Stream start/stop is delegated back to the analog engine so VBI and video share URBs and decoder stream state.

State and persistence: modifies per-buffer `mem`/`length` and the active VBI DMA queue. Buffer completion and field placement are handled in `em28xx-video.c`, while dimensions live in `dev->v4l2`.

Dependencies and integration points: depends on videobuf2, `struct em28xx`, `struct em28xx_buffer`, the shared spinlock, and the V4L header contract. It integrates with V4L2 raw VBI ioctls implemented in `em28xx-video.c`.

Risks: the VBI buffer size depends on correct norm-derived dimensions; stale dimensions can reject valid buffers or overrun payload assumptions. Queue operations do not independently check disconnect state. VBI and video sharing `streaming_users` means imbalance in start/stop can leave URBs running or stop them early. Test signals include `VIDIOC_G_FMT`/`REQBUFS`/streaming on VBI devices for NTSC and PAL, concurrent video+VBI streaming, buffer underrun/short plane rejection, and streamoff returning queued buffers with expected states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-vbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-video.c

Purpose: implements the em28xx V4L2 analog video/radio/VBI extension. It registers V4L2 devices, initializes subdevices and tuners, configures bridge video registers, manages vb2 queues, parses analog USB payloads, and exposes video/radio ioctl operations.

Important APIs/types/functions: `format[]` maps V4L2 pixel formats to bridge output registers. `em28xx_set_outfmt()`, `em28xx_resolution_set()`, scaler/capture helpers, and `em2828X_decoder_set_std()` program hardware. `em28xx_set_alternate()` chooses USB altsetting/bulk parameters. `em28xx_urb_data_copy()` dispatches URB packets to `process_frame_data_em28xx()` or `process_frame_data_em25xx()`. `em28xx_start_analog_streaming()`, `em28xx_stop_streaming()`, and `em28xx_stop_vbi_streaming()` manage shared URBs and decoder stream state. `video_ioctl_ops`, `radio_ioctl_ops`, and vb2 ops expose userspace behavior. `em28xx_v4l2_init()` and `em28xx_v4l2_fini()` own extension lifecycle.

Control flow: init allocates `struct em28xx_v4l2`, registers the `v4l2_device`, creates decoder/audio/tuner/camera subdevices, configures audio and default format/norm/input, installs controls, registers video/VBI/radio devices, creates media entities/graph, initializes vb2 queues, and puts the tuner in standby. File open switches to analog mode on the first user, configures resolution, wakes I2C devices, and increments refs. Stream start reserves the video or VBI resource, sets USB alternate/interface, wakes subdevices, initializes analog URBs, sets tuner frequency, and starts decoder streaming. URB completion parses frame headers, queues/fills video and VBI buffers, finishes fields/frames, and returns vb2 buffers. Last close stops tuner, suspends bridge mode, and resets alternate 0.

State and persistence: stores all analog runtime state in `dev->v4l2`: users, streaming users, format, norm, width/height/scales, VBI dimensions, frequency, capture type, field state, and media pads/entities. Shared state includes `dev->resources`, `dev->vidq`, `dev->vbiq`, `dev->usb_ctl`, audio mute/volume, selected input/audio routing, and USB alt/packet parameters. Module parameters select debug, VBI disablement, forced altsetting, and device node numbers.

Dependencies and integration points: depends on em28xx core USB/register/audio helpers, I2C adapters, board tables, V4L2 core, vb2 vmalloc, media controller, tuner and decoder subdrivers (`msp3400`, `saa7115`, `tvp5150`, `tvaudio`, `xc2028`), and `em28xx-vbi.c` for VBI queue ops. It coordinates with DVB through bridge mode and, for some Hauppauge boards, through `dev->em28xx_set_analog_freq`.

Risks: stream-start failure after `res_get()` can leave the resource bit set because the function returns directly on URB init failure. The shared `streaming_users-- == 1` pattern in stop paths is sensitive to imbalance. USB packet parsing is hardware-format-specific and can silently drop/crop data on malformed headers or oversized frames. Several built-in decoder register sequences are magic values. Media graph and subdevice setup errors are partly logged but not always fatal. Tests should cover V4L2 compliance, all ioctl capability gates, read/mmap/userptr/dmabuf paths, start failure cleanup, video+VBI concurrency, radio devices, tuner frequency routing, suspend/resume/disconnect while streaming, and actual frame integrity for bulk and isochronous devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx.h

Purpose: defines the shared em28xx driver contract: board IDs, buffer types, board metadata, video/audio/I2C/device state structures, extension operations, and cross-module prototypes.

Important APIs/types/functions: `struct em28xx` is the central device object with kref, submodule pointers, board identity, flags, I2C adapters/clients, V4L2 routing state, locks, resources, EEPROM data, DMA queues, USB endpoint/altsetting state, low-level register callbacks, button state, media entities, and dual-TS linkage. `struct em28xx_v4l2`, `struct em28xx_audio`, `struct em28xx_usb_ctl`, `struct em28xx_buffer`, `struct em28xx_board`, `struct em28xx_input`, `struct em28xx_led`, and `struct em28xx_button` define submodule contracts. `struct em28xx_ops` provides extension init/fini/suspend/resume registration.

Control flow: this header does not execute code except `ac97_return_record_select()`, but it shapes all module interactions. Core/cards allocate and identify `struct em28xx`, then extension modules register `struct em28xx_ops`; the core invokes extension lifecycle callbacks. Video, DVB, audio, and input modules share queues, locks, bridge mode, I2C adapters, and board GPIO/input metadata through this header.

State and persistence: most driver state is declared here. Long-lived state includes krefs, `devlist`, EEPROM buffers/hashes, current mode, selected input/audio/frequency, USB transfer buffers, active vb2 buffers, I2C bus selection, device disconnect flag, and per-extension pointers. Hardware state is represented by register callback operations and board GPIO sequences.

Dependencies and integration points: includes Linux workqueue/I2C/mutex/kref/V4L2/vb2/rc-core headers plus tuner helper headers and `em28xx-reg.h`. It declares functions from `em28xx-core.c`, `em28xx-cards.c`, `em28xx-camera.c`, and `em28xx-i2c.c`, making it the primary compile-time integration point for the driver family.

Risks: because many fields are shared across interrupt, workqueue, file operation, and disconnect contexts, locking discipline is critical. Bitfield capability flags and board tables must stay consistent with actual hardware. `INPUT(nr)` depends on a local variable named `dev`, which is convenient but fragile in new call sites. Tests are mostly build and integration signals: compile all module combinations, probe representative boards, validate extension load/unload order, check kref release on disconnect with open fds, and run V4L2/DVB/input/audio smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/go7007/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/go7007/Kconfig

Purpose: declares kernel configuration options for the WIS GO7007 MPEG encoder family, USB transport support, firmware loader support, and Sensoray 2250/2251 board support.

Important APIs/types/functions: Kconfig symbols are `VIDEO_GO7007`, `VIDEO_GO7007_USB`, `VIDEO_GO7007_LOADER`, and `VIDEO_GO7007_USB_S2250_BOARD`. `VIDEO_GO7007` depends on V4L2/I2C/SND/USB, selects vb2 vmalloc, tuner, Cypress firmware, PCM audio, and multiple possible media subdevice drivers under autoselect. USB, loader, and Sensoray symbols layer on top of the base symbol.

Control flow: build-time only. Enabling the base driver exposes the core module; enabling USB adds the transport module; enabling loader adds the firmware loader; enabling Sensoray adds board-specific support. Defaults make the loader `y` when the base is enabled unless overridden.

State and persistence: no runtime state. It controls which object files/modules are compiled and which dependency modules are selected.

Dependencies and integration points: integrates with the media Kconfig tree, V4L2, I2C, ALSA, USB, Cypress firmware helper, and optional subdevice drivers (`saa711x`, `tw2804`, `tw9903`, `tw9906`, `uda1342`, `ov7640`, Sony tuner support).

Risks: broad `select` usage can force extra media/ALSA code into builds and hide missing direct dependencies in source files. `VIDEO_GO7007_LOADER` defaulting to y may surprise minimal configurations. Tests should include `allyesconfig`, `allmodconfig`, minimal module builds for each symbol, and dependency-resolution checks with `MEDIA_SUBDRV_AUTOSELECT` both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/go7007/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/go7007/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/go7007/Makefile

Purpose: maps GO7007 Kconfig symbols to module objects and declares composite object membership.

Important APIs/types/functions: `obj-$(CONFIG_VIDEO_GO7007)` builds `go7007.o`; USB, loader, and Sensoray configs build `go7007-usb.o`, `go7007-loader.o`, and `s2250.o`. `go7007-y` links `go7007-v4l2.o`, `go7007-driver.o`, `go7007-i2c.o`, `go7007-fw.o`, and `snd-go7007.o` into the core module. `s2250-y` links `s2250-board.o`. A conditional `ccflags` include path is added for loader-as-built-in with common media firmware headers.

Control flow: build-system only. Kbuild uses these assignments to decide which translation units become module components.

State and persistence: none at runtime. Build products and module composition are controlled here.

Dependencies and integration points: ties the researched `go7007-driver.c` into the core `go7007` module with V4L2, I2C, firmware-construction, and ALSA support. It also coordinates with USB transport and board-specific modules controlled by Kconfig.

Risks: object membership must match exported symbols and Kconfig dependencies. The conditional include path is narrow and could break if loader/common headers move. Tests should include clean builds for built-in and module permutations, especially `CONFIG_VIDEO_GO7007_LOADER=m/y`, and modpost symbol checks for `go7007-usb`/`s2250` consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/go7007/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/go7007/go7007-driver.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/go7007/go7007-driver.c

Purpose: implements core GO7007 encoder lifecycle, boot/encode firmware transfer, board initialization, V4L2/I2C/audio registration glue, encoded stream parsing, motion-detection event extraction, and core object allocation.

Important APIs/types/functions: exported functions include `go7007_read_interrupt()`, `go7007_read_addr()`, `go7007_boot_encoder()`, `go7007_register_encoder()`, `go7007_start_encoder()`, `go7007_parse_video_stream()`, `go7007_alloc()`, and `go7007_update_board()`. Internal helpers include `go7007_load_encoder()`, `go7007_init_encoder()`, `init_i2c_module()`, `go7007_remove()`, `frame_boundary()`, `go7007_motion_regions()`, and `write_bitmap_word()`. Hardware operations are abstracted through `go->hpi_ops`.

Control flow: hardware-specific probe code allocates `struct go7007` with `go7007_alloc()`, boots firmware via `go7007_boot_encoder()` when needed, then calls `go7007_register_encoder()`. Registration binds a `v4l2_device`, initializes board registers, controls, onboard I2C, subdevices, tuner type, V4L2 device, and ALSA audio when present. Streaming calls `go7007_start_encoder()`, configures motion detection mode, constructs encode firmware, sends it, sets parser state, and starts transport streaming. Transport code feeds bytes into `go7007_parse_video_stream()`, whose state machine detects MPEG/MJPEG frame boundaries, skips timestamp/VBI chunks, parses motion maps, completes vb2 buffers, and queues V4L2 motion events.

State and persistence: `struct go7007` holds boot firmware cache, hw lock, interrupt wait state, V4L2 device, I2C adapter online flag, subdevice pointers, board identity, encoder dimensions/format/bitrate/fps/aspect, parser state, active video buffer, sequence numbers, motion detection maps/status, and audio/V4L2 flags. Boot firmware is cached until removal or transfer error. Runtime state is not persisted beyond the device.

Dependencies and integration points: depends on firmware loading (`go7007/go7007fw.bin`), V4L2 core/events/controls, I2C subdevice creation, tuner setup, ALSA helper `go7007_snd_init()`, GO7007 firmware image construction, and transport-specific HPI ops supplied by USB or other bus modules.

Risks: `go7007_read_interrupt()` checks `wait_event_timeout() < 0`, but timeout returns 0 on timeout; the following availability check catches it, but logging may be misleading. Firmware validation is minimal beyond magic and length. Registration has several early returns after `v4l2_device_register()` where release paths depend on later cleanup behavior. Stream parsing drops oversized frames and depends on start-code detection; malformed streams can desynchronize buffer boundaries. Motion map logic assumes dimensions/map sizes remain coherent. Tests should cover missing/bad firmware, boot/reset/register failures, module unload after partial registration, V4L2 streaming for MJPEG/MPEG1/2/4, oversized frame handling, motion detection events, I2C subdevice probe failures, audio-enabled boards, and disconnect while buffers are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/go7007/go7007-driver.c -->
