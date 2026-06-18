# subset-b-004218 Research

Grouped research for `subset-b-004218`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hackrf/hackrf.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hackrf/hackrf.c

Purpose: V4L2 SDR USB driver for HackRF One. It exposes one SDR capture node and one SDR output node, moves complex signed 8-bit IQ samples over USB bulk endpoints, and maps V4L2 tuner/modulator/frequency/control operations onto HackRF vendor control requests.

Important APIs/types/functions: `struct hackrf_dev` is the persistent device object, holding both `video_device`s, two vb2 queues, queued RX/TX buffer lists, control handlers, USB URB/coherent-buffer arrays, cached ADC/DAC/RF frequencies, and dirty bits. `hackrf_ctrl_msg()` serializes vendor commands. `hackrf_set_params()` consumes dirty bits for sample rate, baseband bandwidth, RF frequency, and gain programming. `hackrf_start_streaming()` and `hackrf_stop_streaming()` own the stream lifecycle. `hackrf_urb_complete_in()` and `hackrf_urb_complete_out()` bridge URB completions to vb2 buffers. The V4L2 ABI is assembled in `hackrf_ioctl_ops`, `hackrf_fops`, and the RX/TX control callbacks.

Control flow: probe allocates `hackrf_dev`, reads board ID and firmware string, initializes RX/TX vb2 vmalloc queues, creates RX and TX RF controls, registers a `v4l2_device`, then registers two SDR video nodes. Format ioctls accept only `V4L2_SDR_FMT_CS8`. Frequency/control setters update cached values, set dirty bits, and call `hackrf_set_params()`; that function is a no-op while neither RX nor TX is active. Streaming chooses RX or TX exclusively, allocates six coherent bulk buffers and URBs, submits them, applies current parameters, then sends `CMD_SET_TRANSCEIVER_MODE`. URB callbacks pull or fill one vb2 buffer per transfer, set payload/timestamp/sequence, complete it, and resubmit the URB.

State and persistence: state is in memory only: device flags, current format, frequencies, V4L2 control values, RX/TX buffer queues, drop counters, sample-rate accounting, and URB allocation/submission counters. Hardware-visible state persists in the HackRF firmware until changed by vendor commands or stream stop. No filesystem persistence exists.

Dependencies and integration: depends on USB core, V4L2 device/ioctl/control/event helpers, vb2 V4L2 and vmalloc memory ops. It binds USB ID `1d50:6089`, registers with `module_usb_driver()`, and advertises SDR capture/output, tuner/modulator, read/write, mmap/userptr/dmabuf, and streaming capabilities.

Risks: RX and TX share one `urb_list` and coherent buffer array, so the exclusive RX/TX check is critical. `hackrf_set_params()` mirrors some dirty bits between RX and TX because several firmware controls are shared; mistakes can reprogram the inactive direction later. URB callbacks resubmit even after many transfer errors except disconnect/kill statuses. `hackrf_ctrl_msg()` copies into a fixed 24-byte buffer and relies on callers respecting command sizes. `hackrf_return_all_buffers()` calls `vb2_buffer_done()` before `list_del()`, which is common in this style but callback side effects should be considered. RF amplifier controls are intentionally grabbed by default because enabling them can damage hardware.

Test signals: build `hackrf.o`; plug a HackRF One and verify two SDR nodes register; use `v4l2-ctl --list-formats-sdr-*`, frequency-band enumeration for tuner/modulator 0/1, RF/bandwidth/gain control changes before and during streaming, RX read/mmap capture, TX write/output streaming, RX/TX mutual exclusion, disconnect while streaming, and dynamic-debug logs for sample-rate/dropped-packet counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hackrf/hackrf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/Kconfig

Purpose: Kconfig entry for Hauppauge HD PVR USB support. It enables the `hdpvr` V4L2 driver as a tristate option.

Important APIs/types/functions: `config VIDEO_HDPVR` is the only symbol. It depends on `VIDEO_DEV` and documents that modular builds produce the `hdpvr` module.

Control flow: when selected, Kbuild includes `drivers/media/usb/hdpvr/Makefile`, which links the core, control, video, and I2C sources into one driver. The symbol does not select helper libraries itself; it relies on media core dependencies around `VIDEO_DEV`.

State and persistence: build-time configuration only. It creates no runtime state and no persistent data.

Dependencies and integration: integrates the HD-PVR USB driver into the media USB menu. Runtime USB matching is implemented in `hdpvr-core.c`, not here.

Risks: the dependency is minimal. If optional I2C/IR support is expected, the source uses `IS_ENABLED(CONFIG_I2C)` rather than a Kconfig dependency here, so configurations without I2C still build the driver but omit adapter registration.

Test signals: `oldconfig`, `allmodconfig`, and `make M=drivers/media/usb/hdpvr`; verify `CONFIG_VIDEO_HDPVR=m` produces `hdpvr.ko` and that `CONFIG_VIDEO_DEV=n` hides the option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/Makefile

Purpose: Kbuild composition for the HD-PVR driver.

Important APIs/types/functions: `hdpvr-objs` combines `hdpvr-control.o`, `hdpvr-core.o`, `hdpvr-video.o`, and `hdpvr-i2c.o`; `obj-$(CONFIG_VIDEO_HDPVR) += hdpvr.o` links them as the selected module or built-in object.

Control flow: Kbuild folds all listed objects into the single `hdpvr` driver. Optional I2C code is guarded inside `hdpvr-i2c.c`, so the object is always compiled but may contain no symbols when I2C is disabled.

State and persistence: no runtime state. It controls build artifacts only.

Dependencies and integration: pairs with `hdpvr/Kconfig` and the parent media USB build.

Risks: object ordering is conventional; missing any object causes unresolved driver entry points declared in `hdpvr.h`. Always compiling `hdpvr-i2c.o` relies on the preprocessor guard being correct.

Test signals: compile with `CONFIG_VIDEO_HDPVR=y`, `m`, and disabled; inspect `hdpvr.o` symbol resolution for control/video/I2C functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-control.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-control.c

Purpose: firmware-control helper layer for the HD-PVR driver. It translates driver options and V4L2 control values into HD-PVR vendor USB control messages and queries input timing/status information.

Important APIs/types/functions: `hdpvr_config_call()` sends one-byte control settings for video standard/input, bitrate mode, GOP mode, and picture controls. `get_video_info()` reads width, height, and frame rate. `get_input_lines_info()` reads detected line data. `hdpvr_set_bitrate()` writes average/peak bitrate. `hdpvr_set_audio()` configures audio input and, when firmware supports it, AAC/AC3 encoding. `hdpvr_set_options()` pushes the full cached `struct hdpvr_options` block to hardware.

Control flow: callers update `dev->options`, then invoke these helpers under higher-level idle/streaming checks. Each helper locks `dev->usbc_mutex`, writes or reads through `dev->usbc_buf`, issues `usb_control_msg()`, unlocks, and returns a Linux error or zero for normalized success. `hdpvr_set_options()` is used during device initialization and after default option setup.

State and persistence: cached state lives in `dev->options`, `dev->flags`, and the shared `usbc_buf`; hardware state persists in the encoder firmware after successful control requests. The file does not store state outside `struct hdpvr_device`.

Dependencies and integration: depends on USB core, `v4l2_common` logging, and constants/prototypes in `hdpvr.h`. It is called by probe initialization and `hdpvr-video.c` V4L2 controls/ioctls.

Risks: most setters accept short successful USB writes by returning the raw positive length, while some normalize only specific lengths; callers often treat nonzero as failure, so positive partial lengths can be ambiguous. `get_input_lines_info()` suppresses `ret` outside debug and returns data from `usbc_buf` even if the USB transfer failed. `hdpvr_set_options()` ignores individual helper failures and always returns 0.

Test signals: probe with known firmware versions; change all picture controls and bitrate controls through V4L2; switch RCA/SPDIF and AAC/AC3 on AC3-capable and older firmware; query video info with valid/no signal; enable USB/control debug and confirm request values match `hdpvr.h` comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-core.c

Purpose: USB probe/disconnect and device initialization for the Hauppauge HD PVR driver. It owns module parameters, USB ID matching, firmware authorization, endpoint discovery, initial option programming, buffer allocation, optional I2C/IR setup, and video-node registration.

Important APIs/types/functions: `hdpvr_probe()` is the main USB bind path. `hdpvr_disconnect()` tears down active I/O and registered interfaces. `hdpvr_device_init()` performs firmware authorization and initial hardware setup. `device_authorization()` reads status/firmware data and sends the challenge response. `challenge()` mutates the firmware challenge bytes. `hdpvr_delete()` releases stream buffers and the USB device reference. Module parameters include `video_nr`, `hdpvr_debug`, `default_video_input`, `default_audio_input`, and `boost_audio`.

Control flow: probe allocates `struct hdpvr_device`, registers a V4L2 device early for logging, initializes locks/waitqueues/control-transfer buffer/default options, discovers the bulk-in endpoint, authorizes the device, sends default options/filter/fan/audio-boost requests, allocates 64 USB transfer buffers, registers I2C and IR when enabled, assigns a device number, then calls `hdpvr_register_videodev()`. Disconnect marks status disconnected under `io_mutex`, wakes readers and buffer submitter, calls `v4l2_device_disconnect()`, flushes work, cancels queued URBs, unregisters I2C and video device, and decrements the device count.

State and persistence: persistent runtime state is `struct hdpvr_device`: USB handle, V4L2/video structures, options, firmware version/capability flags, bulk endpoint geometry, status, queue lists, waitqueues, I2C adapter, and shared control buffer. Firmware programming persists on the hardware until reset or reconfigured. No on-disk state exists.

Dependencies and integration: uses USB core, V4L2 device/common helpers, Linux I2C when enabled, and the HD-PVR control/video/I2C functions. It binds Hauppauge USB IDs `2040:4900/4901/4902/4903/4982` and registers through `module_usb_driver()`.

Risks: the `dev_nr` atomic is a monotonically incremented slot counter decremented on disconnect, so device-number reuse under out-of-order disconnects is coarse. `device_authorization()` uses `dev->usbc_buf[46]` after allocating 64 bytes, which is safe but depends on the fixed allocation. Probe error paths must stay aligned with whether I2C adapter/client registration succeeded; video release also unregisters I2C, so double-delete risks require path review. Firmware challenge behavior is opaque and hardware-version sensitive.

Test signals: probe each supported USB ID; run with default input/audio module parameters; check firmware version/capability logging; test no-bulk-endpoint and authorization failure paths with fault injection; plug/unplug during read streaming; verify no URB or I2C adapter leaks under repeated bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-i2c.c

Purpose: optional I2C bridge for the HD-PVR, primarily to expose the Zilog IR receiver/transmitter device through the Linux I2C and `ir-kbd-i2c` infrastructure.

Important APIs/types/functions: `hdpvr_register_i2c_adapter()` activates IR hardware and registers an `i2c_adapter`. `hdpvr_register_ir_i2c()` creates an `ir_z8f0811_hdpvr` client with Hauppauge RC map/protocol metadata. `hdpvr_transfer()` implements I2C master transfers over USB control messages. `hdpvr_i2c_read()` and `hdpvr_i2c_write()` wrap firmware read/write/status request types. `hdpvr_algo` and `hdpvr_quirks` define adapter behavior.

Control flow: probe calls `hdpvr_register_i2c_adapter()`, which sends activation writes to the device, copies the adapter template, sets parent/adapdata, and calls `i2c_add_adapter()`. The IR client is then registered. I2C users enter `hdpvr_transfer()`, which serializes operations with `i2c_mutex`, converts the 7-bit address to the device format, and supports single read/write or combined write-then-read transactions.

State and persistence: `dev->i2c_adapter`, `dev->i2c_mutex`, `dev->i2c_buf`, and `dev->ir_i2c_init_data` persist for the device lifetime. The IR activation writes persist in firmware/hardware until reset. No filesystem persistence exists.

Dependencies and integration: compiled only when `CONFIG_I2C` is enabled. Integrates with USB control transport, Linux I2C core, `ir-kbd-i2c`, remote-control protocol maps, and cleanup paths in core/video release.

Risks: the adapter supports only a narrow transaction set and marks zero-length reads unsupported; clients outside the intended IR path may fail. `hdpvr_activate_ir()` ignores read/write return values, so IR registration can proceed after activation failures. `hdpvr_i2c_write()` validates completion by checking `i2c_buf[1] == len - 1`, which is firmware-specific. Shared `i2c_buf` requires all transfer users to obey `i2c_mutex`.

Test signals: build with and without `CONFIG_I2C`; verify adapter registration and IR client creation; test remote key events; run I2C transfer fault injection for read/write/status failures; unbind while IR polling is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-video.c

Purpose: V4L2 userspace interface and MPEG transport streaming engine for HD-PVR. It exposes a read/poll video capture node, encoder start/stop commands, input/audio/timing ioctls, and V4L2 controls for MPEG and picture settings.

Important APIs/types/functions: `struct hdpvr_fh` tracks per-file legacy DV-timing mode. Buffer management uses `hdpvr_alloc_buffers()`, `hdpvr_free_buffers()`, `hdpvr_cancel_queue()`, `hdpvr_submit_buffers()`, and `hdpvr_transmit_buffers()`. Streaming is controlled by `hdpvr_start_streaming()` and `hdpvr_stop_streaming()`. User I/O is in `hdpvr_read()` and `hdpvr_poll()`. V4L2 ioctls include standard/DV timing/input/audio/MPEG format/encoder command handlers. `hdpvr_register_videodev()` registers controls and the `video_device`.

Control flow: read or poll on an idle device starts streaming after validating `get_video_info()`, sends firmware start requests, sets status streaming, schedules the worker, and records the owning filehandle. The worker submits all available coherent bulk buffers as URBs and sleeps until a buffer returns to the free list. URB completion marks buffers ready and wakes readers. `hdpvr_read()` copies ready URB payloads to userspace, recycles fully consumed buffers to the free list, and restarts streaming after a one-second data timeout. Stop sends the firmware stop request, wakes/flushed the worker, kills queued URBs, drains residual device data with bulk reads, and returns status to idle.

State and persistence: stream state persists in `dev->status`, `owner`, free/in-progress lists, per-buffer status/position/URB, waitqueues, and cached width/height/std/DV timing/options/control values. Hardware encoder and low-pass/input/audio/bitrate settings persist in firmware until changed. There is no on-disk persistence.

Dependencies and integration: uses USB bulk URBs, V4L2 file/ioctl/control/event helpers, DV timing helpers, `copy_to_user()`, workqueues, and control helpers from `hdpvr-control.c`. It integrates with `hdpvr-core.c` probe and release lifecycle.

Risks: this driver is read-based, not vb2, so queue ownership and waits are manually implemented. `hdpvr_get_next_buffer()` returns a list entry after releasing `io_mutex`, so status/list transitions rely on the broader single-reader/owner discipline. `hdpvr_read()` restarts streaming after timeout without holding `io_mutex` for the second `hdpvr_start_streaming()` call, which contrasts with the function comment. `hdpvr_device_release()` unregisters I2C even though disconnect/probe failure paths may also do so. Legacy-mode behavior intentionally changes `G_FMT` semantics per filehandle.

Test signals: `v4l2-compliance` for read-only capture; `v4l2-ctl --query-dv-timings`, `--set-dv-bt-timings`, std/input/audio enumeration; read MPEG data from component and composite/S-video sources; encoder start/stop commands and owner exclusion; nonblocking read/poll; timeout recovery; disconnect during active read; control changes only while idle where required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr.h

Purpose: private HD-PVR driver header. It centralizes product IDs, firmware versions, statuses, control request constants, runtime structures, option enums, and cross-file prototypes.

Important APIs/types/functions: `struct hdpvr_device` carries all device state shared by core/control/video/I2C code. `struct hdpvr_options` caches firmware options. `struct hdpvr_buffer` wraps one coherent bulk URB and stream-list state. `struct hdpvr_video_info` carries queried input geometry. Enums define device statuses, buffer statuses, video/audio inputs, video standard, bitrate mode, and GOP mode. Function prototypes expose deletion, hardware control, V4L2 registration, I2C registration, queue cancellation, and buffer allocation/free.

Control flow: all HD-PVR C files include this header and manipulate the same state layout. Probe fills `hdpvr_device`, control helpers program options, video code owns streaming and V4L2 registration, and I2C code uses the embedded adapter fields.

State and persistence: this header declares persistent in-memory state: locks, waitqueues, work item, buffer lists, current owner, cached options, firmware version, endpoint address/size, I2C state, and shared USB control buffer. It also documents firmware control values that persist in device hardware.

Dependencies and integration: includes USB, I2C, mutex/workqueue, V4L2 device/control, and `ir-kbd-i2c` declarations. It is the private ABI binding the four HD-PVR objects.

Risks: many fields are shared across files with locking comments rather than type-enforced access. Status values and buffer states are simple bytes, so invalid transitions can go undetected. The product ID naming order is nonmonotonic (`PRODUCT_ID4` before `PRODUCT_ID3`). Several long comment blocks document reverse-engineered USB controls; implementation must stay aligned with them.

Test signals: compile all HD-PVR objects; static checking for lock coverage on `io_mutex`, `i2c_mutex`, and `usbc_mutex`; runtime exercise of every status transition and all enums through V4L2 ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/msi2500/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/msi2500/Kconfig

Purpose: Kconfig entry for the Mirics MSi2500/MSi3101 SDR USB driver.

Important APIs/types/functions: `config USB_MSI2500` is a tristate depending on `VIDEO_DEV` and `SPI`. It selects `VIDEOBUF2_VMALLOC` and `MEDIA_TUNER_MSI001`.

Control flow: selecting the symbol builds `msi2500.o`; the SPI dependency is required because the USB device exposes an SPI bridge used to instantiate the `msi001` tuner subdevice.

State and persistence: build-time configuration only.

Dependencies and integration: integrates the SDR USB driver with V4L2, vb2 vmalloc, SPI core, and the MSI001 tuner driver.

Risks: no explicit help text beyond the prompt string, so users get little guidance. The selected tuner driver must remain compatible with the SPI messages emitted by `msi2500.c`.

Test signals: `COMPILE_TEST`/allmodconfig coverage; verify the option is unavailable without SPI; modular build should pull `msi001` support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/msi2500/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/msi2500/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/msi2500/Makefile

Purpose: Kbuild rule for the MSi2500 driver.

Important APIs/types/functions: `obj-$(CONFIG_USB_MSI2500) += msi2500.o` links the single source file as a module or built-in object.

Control flow: Kbuild includes `msi2500.c` only when the Kconfig symbol is enabled.

State and persistence: no runtime state. It controls object inclusion only.

Dependencies and integration: pairs with `msi2500/Kconfig` and parent media USB build.

Risks: all functionality lives in one object, so missing dependencies surface as compile/link failures in `msi2500.o`.

Test signals: compile with `CONFIG_USB_MSI2500=m/y` and disabled; inspect `modinfo msi2500` for USB aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/msi2500/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/msi2500/msi2500.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/msi2500/msi2500.c

Purpose: V4L2 SDR capture driver for Mirics MSi2500/MSi3101 USB SDR dongles. It captures isochronous USB ADC packets, converts device sample layouts into V4L2 SDR formats, and creates an SPI controller to attach the MSI001 RF tuner as a V4L2 subdevice.

Important APIs/types/functions: `struct msi2500_dev` stores the video device, V4L2 device, tuner subdev, SPI controller, vb2 queue, USB URBs, controls, current ADC frequency/format, and packet counters. `msi2500_convert_stream()` parses 1024-byte device transactions and converts signed/unsigned sample formats. `msi2500_isoc_handler()` moves completed ISO frames into vb2 buffers. `msi2500_set_usb_adc()` programs ADC/USB registers and fractional-N sample-rate synthesis. `msi2500_transfer_one_message()` implements the SPI bridge used by `msi001`. Probe registers vb2, V4L2, SPI, tuner subdev, controls, and one SDR video node.

Control flow: probe initializes `struct msi2500_dev`, creates a vb2 SDR capture queue, registers a V4L2 device, allocates/registers an SPI host, instantiates the `msi001` tuner subdevice through `v4l2_spi_new_subdev()`, imports subdevice controls, then registers the SDR node. `S_FMT` changes sample format only while vb2 is idle. `S_FREQUENCY` tuner 0 updates the ADC rate and programs the USB ADC, while tuner 1 is forwarded to the RF subdevice. Streaming powers the tuner, programs ADC/filter state, sets USB interface altsetting 1, allocates/submits eight ISO URBs, and sends start. Stop kills/frees URBs, returns queued vb2 buffers with error, stops the USB ADC, and powers down the tuner.

State and persistence: runtime state is in memory: current format, `f_adc`, imported tuner controls, ISO error/drop counters, queued vb2 buffers, `next_sample` sequence tracking, and URB arrays. Hardware state persists in MSi2500 registers and MSI001 tuner registers until reprogrammed. No on-disk persistence exists.

Dependencies and integration: depends on USB, V4L2 device/ioctl/control/event, vb2 V4L2/vmalloc, SPI core, `MEDIA_TUNER_MSI001`, and V4L2 subdev tuner ops. USB IDs include `1df7:2500` and `2040:d300`.

Risks: `msi2500_start_streaming()` overwrites `ret` after `msi2500_set_usb_adc()` and after `msi2500_isoc_init()`, so an ADC or ISO initialization failure can be masked by the later start command path. Some sample formats are called emulated and hidden unless the module parameter is set, but conversion support remains in code. ISO callbacks submit a new URB even after many contiguous errors, only logging after the threshold. Packet parsing assumes 1024-byte transactions and fixed 16-byte headers. The SPI bridge assumes each transfer has at least three bytes of TX data.

Test signals: build with MSI001; plug both USB IDs; verify SDR format enumeration with and without `emulated_formats=1`; tune ADC and RF frequencies; stream each exposed sample format with mmap/read; check lost-sample debug logs; disconnect during streaming; run SPI/tuner control changes and bandwidth-auto behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/msi2500/msi2500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/Kconfig

Purpose: Kconfig menu for the Hauppauge WinTV-PVR USB2 driver and its optional sysfs, DVB, and debug interfaces.

Important APIs/types/functions: `VIDEO_PVRUSB2` is the main tristate and depends on `VIDEO_DEV`, `I2C`, and `DVB_CORE`; it selects tuner, tveeprom, cx2341x encoder, decoder/audio subdevice drivers. `VIDEO_PVRUSB2_SYSFS` enables sysfs controls. `VIDEO_PVRUSB2_DVB` enables digital-TV integration and selects demod/tuner frontends under autoselect. `VIDEO_PVRUSB2_DEBUGIFC` enables the sysfs-hosted debug command interface.

Control flow: Kconfig controls which optional objects are appended by the Makefile. DVB is constrained so modular pvrusb2 is not built against modular-incompatible DVB core combinations.

State and persistence: no runtime state; it controls build inclusion.

Dependencies and integration: integrates pvrusb2 with V4L2, I2C subdevices, cx2341x firmware controls, DVB core/frontends/tuners, sysfs, and media subdriver autoselection.

Risks: the main driver depends on `DVB_CORE` even when DVB support is later disabled, which broadens required configuration. Default-y sysfs and DVB suboptions enlarge the module surface. `VIDEO_PVRUSB2_DEBUGIFC` depends on sysfs, so debug coverage can silently disappear without sysfs.

Test signals: build matrix for main/sysfs/DVB/debug options; ensure selected demod/tuner modules resolve; verify disabled optional features remove sysfs debug or DVB nodes as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/Makefile

Purpose: Kbuild composition for the multi-file `pvrusb2` driver.

Important APIs/types/functions: variables `obj-pvrusb2-sysfs-*`, `obj-pvrusb2-debugifc-*`, and `obj-pvrusb2-dvb-*` conditionally add optional objects. `pvrusb2-objs` lists I2C, audio, encoder, V4L2 video, EEPROM, main, hardware, control, standard, device-attribute, context, I/O, subdevice-routing, DVB/sysfs/debug objects. Include paths add tuner and DVB frontend headers.

Control flow: Kbuild folds all selected objects into one `pvrusb2.o`, then links it according to `CONFIG_VIDEO_PVRUSB2`.

State and persistence: build artifact control only.

Dependencies and integration: tightly paired with `pvrusb2/Kconfig` and with source files that reference tuner/frontend headers via the added include paths.

Risks: optional object variables use `-y` expansion, so only built-in booleans append optional objects; this matches bool suboptions but must remain aligned with Kconfig types. Missing include path updates can break frontend/tuner configuration tables.

Test signals: compile all combinations of sysfs/DVB/debug; `nm pvrusb2.o` for optional symbols; module load with digital and analog devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-audio.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-audio.c

Purpose: routes pvrusb2 input selections to the MSP3400 audio subdevice.

Important APIs/types/functions: `routing_scheme0[]` maps pvrusb2 input control values to `MSP_INPUT()` routes. `pvr2_msp3400_subdev_update()` is the exported update hook called by hardware/subdevice management when input routing is dirty.

Control flow: when `hdw->input_dirty` or `force_dirty` is set, the function looks up the device routing scheme, validates `input_val`, computes the MSP input, and calls `sd->ops->audio->s_routing()` with a DSP SCART output route.

State and persistence: no private state. It reads `struct pvr2_hdw` fields and programs the MSP3400 subdevice, whose state persists until another route change or reset.

Dependencies and integration: depends on pvrusb2 hardware internals, debug tracing, `msp3400` driver interface macros, and V4L2 subdev audio routing.

Risks: only `PVR2_ROUTING_SCHEME_HAUPPAUGE` is represented. Invalid routing/input combinations are logged and skipped, leaving stale audio route state. The code calls subdev ops directly without NULL checks, relying on registration to match capabilities.

Test signals: switch TV/radio/composite/S-video inputs on 29xxx-style devices; enable `PVR2_TRACE_CHIPS`; verify audio follows the selected source and invalid routing schemes warn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-audio.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-audio.h

Purpose: private declaration for the MSP3400 audio-routing bridge.

Important APIs/types/functions: declares `pvr2_msp3400_subdev_update(struct pvr2_hdw *, struct v4l2_subdev *)`.

Control flow: hardware/subdevice code includes this header to call the MSP3400 update hook when pvrusb2 input state changes.

State and persistence: no state; it exposes a routing helper prototype.

Dependencies and integration: includes `pvrusb2-hdw-internal.h`, so it is private to the pvrusb2 hardware layer.

Risks: including the internal hardware header couples users to private layout rather than a narrow forward declaration.

Test signals: compile users that register MSP3400 clients; ensure the prototype matches `pvrusb2-audio.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-context.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-context.c

Purpose: central context/channel coordinator for pvrusb2. It serializes asynchronous hardware initialization, notification delivery, disconnect cleanup, channel ownership, input-limit arbitration, and MPEG stream wrapping.

Important APIs/types/functions: global lists track existing contexts and contexts needing notification. `pvr2_context_thread_func()` is the driver worker thread. `pvr2_context_create()`, `pvr2_context_disconnect()`, `pvr2_context_global_init()`, and `pvr2_context_global_done()` manage context lifetime. `pvr2_channel_init()`, `pvr2_channel_done()`, `pvr2_channel_limit_inputs()`, and `pvr2_channel_claim_stream()` manage user channels. `pvr2_channel_create_mpeg_stream()` creates an `ioread` wrapper with MPEG pack sync key.

Control flow: creating a context links it into the global existence list, creates hardware state, and enqueues notification. The global thread drains the notify list, initializes hardware in thread context, installs the video stream, invokes the setup callback, runs each channel check callback, and destroys a disconnected context once no channels remain. Channels attach to the context list, may claim the shared video stream exclusively, and can reduce allowed hardware inputs; input masks across channels are intersected and committed to hardware.

State and persistence: persistent state includes global context lists, notify flags, cleanup flags, the kernel thread, each `struct pvr2_context`, and each linked `struct pvr2_channel`. State is memory-only and tied to device lifetime.

Dependencies and integration: depends on pvrusb2 hardware, stream, and ioread layers plus waitqueues, kthreads, mutexes, and trace flags. V4L2, sysfs, and DVB frontends create channels through this layer.

Risks: global cleanup waits for all contexts to disappear before stopping the thread; leaked channels can block module unload. `pvr2_context_disconnect()` calls hardware disconnect before setting `disconnect_flag`, creating a short ordering window. Input-limit arbitration is subtle and depends on every channel clearing masks on teardown. `pvr2_channel_claim_stream()` kills any previously claimed stream when switching.

Test signals: module load/unload with multiple devices; disconnect while V4L2/DVB/sysfs channels are open; concurrent stream claim attempts returning `-EBUSY`; input-limit conflicts between analog and DVB paths; context trace logs for init/destroy ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-context.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-context.h

Purpose: private declarations for pvrusb2 central context and channel management.

Important APIs/types/functions: defines `struct pvr2_context_stream`, `struct pvr2_context`, and `struct pvr2_channel`, plus prototypes for context creation/disconnect/global init/done, channel init/done/input limits/stream claims, and MPEG stream creation.

Control flow: higher-level interfaces embed or allocate `pvr2_channel`, initialize it against a `pvr2_context`, optionally set `check_func`, claim `video_stream`, and release it on teardown.

State and persistence: declares the fields that persist for device lifetime: linked-list pointers, hardware pointer, video stream wrapper, context mutex, notify/initialized/disconnect flags, per-channel stream/input mask/check callback.

Dependencies and integration: includes Linux mutex/USB/workqueue and forward-declares hardware/stream/ioread objects. It is the ABI between main hardware setup and pvrusb2 interface layers.

Risks: list linkage is open-coded rather than `list_head`, so pointer maintenance bugs are easy. Channel callbacks execute from the global context thread and must avoid blocking indefinitely.

Test signals: compile all pvrusb2 interfaces; static checks for channel lifecycle pairing; runtime open/close/disconnect tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cs53l32a.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cs53l32a.c

Purpose: audio-routing bridge for CS53L32A ADC subdevices on pvrusb2 OnAir hardware.

Important APIs/types/functions: `routing_scheme1[]` maps pvrusb2 input values to CS53L32A input numbers. `pvr2_cs53l32a_subdev_update()` validates the routing scheme and calls `sd->ops->audio->s_routing()`.

Control flow: on dirty or forced input state, the function selects the route for `PVR2_ROUTING_SCHEME_ONAIR`; invalid scheme/input logs a warning and leaves the current subdevice route unchanged.

State and persistence: no local state. It reads `hdw->input_val` and programs subdevice state.

Dependencies and integration: depends on pvrusb2 hardware internals, V4L2 subdev audio ops, and trace logging.

Risks: only OnAir routing is supported. Direct subdev op calls assume the audio operation exists. Invalid inputs leave stale audio selection.

Test signals: OnAir Creator/USB2 analog input switching; trace logs; audio capture from TV/radio/composite/S-video paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cs53l32a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cs53l32a.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cs53l32a.h

Purpose: private declaration for the CS53L32A audio-routing bridge.

Important APIs/types/functions: declares `pvr2_cs53l32a_subdev_update()`.

Control flow: hardware subdevice update code calls this helper when input routing changes on devices using the CS53L32A.

State and persistence: no state.

Dependencies and integration: includes pvrusb2 hardware internals and references V4L2 subdev types.

Risks: private-header coupling and direct reliance on internal `struct pvr2_hdw` layout.

Test signals: compile with CS53L32A selected and exercise OnAir routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cs53l32a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ctrl.c

Purpose: generic pvrusb2 control abstraction used by V4L2, sysfs, and internal code to get/set hardware controls and convert values to/from symbolic strings.

Important APIs/types/functions: `pvr2_ctrl_set_value()`, `pvr2_ctrl_set_mask_value()`, `pvr2_ctrl_get_value()`, min/max/default/count/mask/name/description accessors, V4L ID/flag helpers, custom symbol hooks, `pvr2_ctrl_sym_to_value()`, and `pvr2_ctrl_value_to_sym()`. Internal parsers handle integers, booleans, enums, and bitmask token lists. All hardware access is serialized with `hdw->big_lock`.

Control flow: setters validate type/range, mask bitmask controls, and invoke the control descriptor's `set_value` callback. Getters lock and delegate to descriptor callbacks or defaults. Symbol parsing trims whitespace, parses enum/bool names or numeric tokens, and produces mask/value pairs. Symbol formatting emits numeric, bool, enum names, or bitmask names.

State and persistence: no independent state. It operates on `struct pvr2_ctrl` and its descriptor stored in the hardware layer. Setting a control may mark dirty state or program hardware depending on the callback.

Dependencies and integration: includes pvrusb2 hardware internals for lock macros and control descriptor types; used by V4L2 ioctl glue and sysfs/debug interfaces.

Risks: lock macros rely on `hdw->big_lock` and held-state fields; callbacks must not recurse incorrectly. Bitmask string generation has a suspicious branch that prints `+0x...` for bits in `um & ~val` where a minus marker might be expected. Some helpers return neutral values for NULL controls, which can hide caller bugs. Symbol parsing accepts numeric fallbacks, so invalid names that parse as numbers can pass range checks.

Test signals: sysfs/V4L2 get/set for int, bool, enum, and bitmask controls; range-boundary tests; custom symbol conversions; lockdep under concurrent control access; invalid-token tests returning `-EINVAL` or `-ERANGE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ctrl.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ctrl.h

Purpose: public internal API for pvrusb2 control access and symbolic conversion.

Important APIs/types/functions: defines `enum pvr2_ctl_type` (`int`, `enum`, `bitmask`, `bool`) and declares setters/getters, metadata accessors, V4L mapping helpers, custom symbol helpers, generic symbol parse/format functions, and the internal no-lock formatter.

Control flow: interface layers include this header to translate user-visible controls into pvrusb2 hardware-control operations.

State and persistence: no state; it forward-declares `struct pvr2_ctrl` and describes operations on hardware-owned controls.

Dependencies and integration: used across pvrusb2 V4L2/sysfs/control code. The internal formatter is intended for callers already inside the hardware critical region.

Risks: callers must distinguish `pvr2_ctrl_value_to_sym_internal()` from the locking wrapper or risk missing synchronization. V4L IDs are optional and may be zero.

Test signals: compile all control users; static analysis for internal formatter calls; V4L2 control enumeration and sysfs symbolic control tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cx2584x-v4l.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cx2584x-v4l.c

Purpose: routing bridge between pvrusb2 input selections and the CX25840/CX2584x audio/video decoder subdevice.

Important APIs/types/functions: `struct routing_scheme_item` pairs video and audio route values. Multiple routing tables cover Hauppauge, GotView, AV400, and HVR-160xxx schemes. `pvr2_cx25840_subdev_update()` validates the scheme/input and calls video and audio `s_routing()`.

Control flow: when input state is dirty or forced, the update function chooses the route table from `hdw->hdw_desc->signal_routing_scheme`, validates `hdw->input_val`, logs selected routes, and programs both video and audio routes on the decoder subdevice.

State and persistence: no local state. It programs persistent subdevice routing state and reads `struct pvr2_hdw` device descriptor/current input flags.

Dependencies and integration: depends on `cx25840` driver interface constants, V4L2 subdev audio/video ops, and pvrusb2 hardware internals. Called by the hardware layer during control commits.

Risks: direct `sd->ops->video/audio->s_routing` calls assume ops exist. Routing tables are hardware-specific and stale values can break audio/video capture silently. Invalid routes only log and skip updates.

Test signals: switch all inputs on 24xxx, GotView, AV400, and HVR-16xxxx devices; verify decoder status logs and actual captured video/audio source; enable chip trace logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cx2584x-v4l.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cx2584x-v4l.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cx2584x-v4l.h

Purpose: private declaration for the CX25840/CX2584x routing update bridge.

Important APIs/types/functions: declares `pvr2_cx25840_subdev_update(struct pvr2_hdw *, struct v4l2_subdev *)`.

Control flow: hardware subdevice management includes this header and invokes the helper during dirty input commits.

State and persistence: no state.

Dependencies and integration: includes pvrusb2 hardware internals and V4L2 subdev type usage.

Risks: tight coupling to internal hardware state and direct subdevice update conventions.

Test signals: compile with CX25840 selected and verify routing helper linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cx2584x-v4l.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debug.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debug.h

Purpose: central trace-mask definitions for pvrusb2.

Important APIs/types/functions: `pvrusb2_debug` is the module-level trace mask. `pvr2_trace(msk, fmt, ...)` emits `pr_info()` when a mask bit is enabled. Mask definitions cover info/errors/tolerance/trap/std/init/start-stop/control/state/eeprom/context/sysfs/firmware/chips/I2C/encoder/buffer/data/debug/GPIO/DVB feed.

Control flow: all pvrusb2 files include this header and guard debug output by mask bits. Users enable bits through the module parameter defined elsewhere.

State and persistence: only the external integer trace mask. No persistent storage.

Dependencies and integration: integrates all pvrusb2 source files around a shared tracing vocabulary.

Risks: `pr_info()` can be noisy for high-volume data paths. The closing include-guard comment names a different header, which is harmless but confusing.

Test signals: set `pvrusb2_debug` to individual bits and confirm expected logs without flooding critical paths excessively.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debugifc.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debugifc.c

Purpose: sysfs-hosted debug command and status implementation for pvrusb2.

Important APIs/types/functions: `pvr2_debugifc_print_info()` emits hardware description and state report. `pvr2_debugifc_print_status()` reports USB speed, GPIO state, streaming state, and stream buffer stats. `pvr2_debugifc_docmd()` parses newline-separated commands. Internal helpers tokenize whitespace, parse unsigned numbers in decimal/octal/hex, and match keywords. Supported commands include reset variants, CPU firmware fetch/done, GPIO direction/output changes, stream stats reset, firmware reload, decoder reset, and worker untrip.

Control flow: sysfs/debug code passes user text to `pvr2_debugifc_docmd()`, which splits lines and executes each command with `pvr2_debugifc_do1cmd()`. Commands call into the hardware layer for resets, GPIO changes, firmware upload, and stream statistic reset. Print functions query hardware and stream state into caller-provided buffers.

State and persistence: no private state. Commands can mutate persistent hardware state: reset lines, GPIO direction/output, firmware capture mode, powerup/deep reset, and worker/stream stats.

Dependencies and integration: depends on pvrusb2 hardware API, stream stats, debug masks, and Linux hex parsing. It is compiled only when the debug interface option is selected through Kconfig/Makefile.

Risks: debug commands are intentionally intrusive and can reset hardware or alter GPIOs. Number parsing manually handles radix and overflow is not explicitly checked. `print_info()` can synchronize with hardware and comments warn it may hang if the driver is wedged. Command grammar is minimal and returns `-EINVAL` on many partial inputs.

Test signals: with `VIDEO_PVRUSB2_DEBUGIFC`, read info/status sysfs files; issue safe commands like `reset usbstats`; validate GPIO command parsing with mask/value forms; verify restricted/debug-only exposure; test invalid commands returning errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debugifc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debugifc.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debugifc.h

Purpose: declarations for the pvrusb2 debug interface.

Important APIs/types/functions: declares `pvr2_debugifc_print_info()`, `pvr2_debugifc_print_status()`, and `pvr2_debugifc_docmd()`.

Control flow: sysfs/debug frontend code calls these functions to render state and execute commands against a `struct pvr2_hdw`.

State and persistence: no state; commands may mutate hardware through the implementation.

Dependencies and integration: forward-declares `struct pvr2_hdw` and keeps the debug frontend decoupled from full hardware internals.

Risks: comments distinguish synchronized and nonintrusive status paths; callers should choose the right printer for wedged hardware.

Test signals: compile debug interface users and exercise sysfs read/write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debugifc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-devattr.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-devattr.c

Purpose: static per-device attribute database for pvrusb2. It maps USB IDs to hardware descriptions, firmware file names, I2C client sets, analog/digital capabilities, routing schemes, IR/LED schemes, default tuner/std values, and DVB frontend/tuner attach callbacks.

Important APIs/types/functions: `pvr2_device_table[]` is the USB match table and stores `driver_info` pointers to `struct pvr2_device_desc`. Static descriptors cover Hauppauge 29xxx/24xxx/73xxx/750xx/751xx/160000/160111, GotView variants, Terratec AV400, and OnAir devices. DVB helper callbacks attach LGDT330x, S5H1409/S5H1411, TDA10048/TDA18271/TDA829x, LGDT3306A, SI2168, SI2157, and simple tuner components when enabled. `MODULE_FIRMWARE()` advertises required FX2 firmware.

Control flow: USB probe matches an entry in `pvr2_device_table`, then the hardware layer consumes the descriptor to load firmware, instantiate subdevices, choose routing logic, expose inputs, handle IR/LED/digital control schemes, and optionally create DVB frontends. DVB attach callbacks are referenced through `struct pvr2_dvb_props`.

State and persistence: the file defines static read-only descriptors and config structs. Runtime state is created elsewhere based on these descriptors. Firmware file names refer to persistent files in the system firmware path but this file does not write them.

Dependencies and integration: depends on USB IDs, tuner type IDs, pvrusb2 device descriptor types, and optional DVB frontend/tuner driver APIs. It is the central integration point between product variants and the generic pvrusb2 hardware logic.

Risks: descriptor accuracy is critical; wrong routing, tuner type, firmware name, or digital scheme can make a product partially unusable. Conditional DVB code changes descriptor contents by build config. Some newer devices use I2C client module probing and must release demod/tuner clients on failures. `MODULE_FIRMWARE(PVR2_FIRMWARE_75xxx)` advertises the same filename as 73xxx through a separate macro, which is intentional but easy to misread.

Test signals: enumerate every USB ID; verify firmware request names; analog input availability and routing per product; IR scheme behavior; DVB frontend attach for each digital-capable model; module autoload aliases; build with and without DVB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-devattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-devattr.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-devattr.h

Purpose: type definitions and constants for pvrusb2 per-device descriptions.

Important APIs/types/functions: defines client IDs, routing/digital/LED/IR scheme IDs, `struct pvr2_device_client_desc`, `struct pvr2_device_client_table`, `struct pvr2_string_table`, and `struct pvr2_device_desc`. Declares `pvr2_device_table[]`.

Control flow: `pvrusb2-devattr.c` populates descriptors with these structures; the hardware layer reads the matched descriptor to choose firmware, clients, capabilities, and control schemes.

State and persistence: descriptors are static metadata. Fields include default std/tuner, firmware lists, client tables, DVB props, and numerous one-bit capability flags.

Dependencies and integration: includes USB mod_devicetable and V4L2 standard definitions; includes DVB declarations when DVB support is compiled.

Risks: bitfield flags are compact and easy to mis-set. `i2c_address_list` is documented as null-terminated bytes, requiring care because address zero is used as terminator. Routing scheme IDs are arbitrary internal integers and must match routing helper tables.

Test signals: compile descriptor users; static validation that each USB table entry points to a complete descriptor; runtime capability exposure for each product family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-devattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-dvb.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-dvb.c

Purpose: Linux DVB API bridge for pvrusb2 digital-capable devices. It registers DVB adapters, demux/net devices, attaches frontends/tuners, claims the shared pvrusb2 video stream for DTV, and feeds transport packets into the DVB demux.

Important APIs/types/functions: `pvr2_dvb_create()` allocates and initializes the adapter. `pvr2_dvb_adapter_init()/exit()` register/unregister DVB core objects. `pvr2_dvb_frontend_init()/exit()` attach and register frontends/tuners from device descriptor callbacks. `pvr2_dvb_stream_start()`, `pvr2_dvb_stream_end()`, and `pvr2_dvb_feed_thread()` manage streaming. `pvr2_dvb_start_feed()` and `pvr2_dvb_stop_feed()` are demux feed callbacks. `pvr2_dvb_bus_ctrl()` uses pvrusb2 input limits to acquire/release DTV ownership.

Control flow: setup creates a pvrusb2 channel, registers DVB adapter/demux/dmxdev/net, temporarily limits input to DTV, attaches frontends, registers them, installs `ts_bus_ctrl`, and releases the input limit. When the first demux feed starts, it claims the shared video stream, allocates 32 16KiB buffers, assigns them to pvr2 stream buffers, enables hardware streaming, queues idle buffers, and starts a kernel feed thread. The thread drains ready buffers, pushes payload into `dvb_dmx_swfilter()`, and requeues buffers. Last feed stop tears all streaming state down.

State and persistence: `struct pvr2_dvb_adapter` stores the pvr2 channel, DVB core objects, frontend pointers, dynamically probed I2C clients, feed count, thread pointer, stream-run flag, waitqueue, and buffer storage. State is runtime-only.

Dependencies and integration: depends on DVB core/demux/net APIs, pvrusb2 context/channel/stream/hardware APIs, optional frontend/tuner attach callbacks in device descriptors, kthreads, freezer support, and media I2C module probing.

Risks: several failure paths in `pvr2_dvb_stream_do_start()` return after partial buffer allocation or stream claiming; wrapper cleanup helps but review is needed for every early return. `pvr2_dvb_frontend_init()` returns immediately on no frontend without releasing the DTV input limit in one branch. Dual-frontend setup copies tuner ops/private data from frontend 0 to 1, which depends on frontend implementation expectations. Feed count and stream-run state are protected by `adap->lock`; frontend bus-control callbacks use channel limits separately.

Test signals: digital device probe creates `/dev/dvb/adapter*`; start/stop PID filters repeatedly; stream TS data through demux; freeze/thaw feed thread; disconnect while feeds are active; dual-frontend HVR-1955/1975 attach; fault-inject frontend/tuner attach failures and buffer allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-dvb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-dvb.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-dvb.h

Purpose: data model and prototypes for pvrusb2 DVB integration.

Important APIs/types/functions: defines `PVR2_DVB_BUFFER_COUNT` and `PVR2_DVB_BUFFER_SIZE`, `struct pvr2_dvb_adapter`, `struct pvr2_dvb_props`, and `pvr2_dvb_create()`.

Control flow: device descriptors provide `pvr2_dvb_props` attach callbacks; setup code calls `pvr2_dvb_create()` to register and manage the DVB side using the embedded channel and buffer arrays.

State and persistence: declares persistent runtime DVB adapter state: pvr2 channel, DVB adapter/demux/dmxdev/net, up to two frontends, I2C client handles, feed count, stream thread, lock, waitqueue, and 32 packet buffers.

Dependencies and integration: includes DVB frontend/demux/net/dmxdev headers and pvrusb2 context definitions.

Risks: fixed buffer count/size must match stream throughput expectations. The struct exposes multiple ownership domains whose teardown ordering is enforced only by implementation discipline.

Test signals: compile with DVB enabled; inspect adapter creation and stream buffer allocation under live DTV feeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-dvb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-eeprom.c

Purpose: reads and interprets Hauppauge EEPROM metadata for pvrusb2 devices, using the common `tveeprom` parser to determine tuner type, serial number, and supported standards.

Important APIs/types/functions: `pvr2_eeprom_analyze()` is the exported entry point. `pvr2_eeprom_fetch()` reads the last 128 bytes of the EEPROM through the pvrusb2 I2C adapter, handling 8-bit or 16-bit addressing based on the controller-reported EEPROM address.

Control flow: analysis allocates a 128-byte buffer, normalizes the EEPROM I2C address, selects address width and total size, reads 16-byte chunks from the end of the EEPROM through a two-message I2C transfer, then calls `tveeprom_hauppauge_analog()`. Parsed fields are copied into `hdw->tuner_type`, `tuner_updated`, `serial_number`, and `std_mask_eeprom`.

State and persistence: temporary EEPROM data is heap allocated and freed. Persistent runtime results are stored in `struct pvr2_hdw`; EEPROM contents are read-only hardware persistence.

Dependencies and integration: depends on pvrusb2 hardware internals, Linux I2C, trace flags, and `media/tveeprom.h`.

Risks: only the last 128 bytes are read, assuming Hauppauge layout compatibility. I2C transfer failure aborts parsing. Address normalization for high-bit-set addresses and odd-address 16-bit mode is based on observed FX2 behavior and could mis-handle unusual EEPROMs.

Test signals: devices with Hauppauge ROM; trace EEPROM output; tuner type/std mask/serial propagation; fault injection of I2C transfer failures; compare parsed values with known labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-eeprom.h

Purpose: declaration for pvrusb2 EEPROM analysis.

Important APIs/types/functions: forward-declares `struct pvr2_hdw` and declares `pvr2_eeprom_analyze()`.

Control flow: hardware initialization calls this helper when the device descriptor indicates a Hauppauge ROM.

State and persistence: no state; implementation stores parsed EEPROM results in hardware state.

Dependencies and integration: private pvrusb2 hardware initialization API.

Risks: callers must ensure I2C adapter and EEPROM address are initialized before calling.

Test signals: compile hardware initialization path and run on EEPROM-equipped devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-encoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-encoder.c

Purpose: CX23416 MPEG encoder mailbox support for pvrusb2. It sends memory read/write requests through the FX2 firmware, wraps cx2341x control updates, and starts/stops/configures MPEG/VBI capture.

Important APIs/types/functions: `pvr2_encoder_write_words()` and `pvr2_encoder_read_words()` access encoder mailbox/memory through FX2 commands. `pvr2_encoder_cmd()` implements the cx2341x mailbox callback. `pvr2_encoder_vcmd()` is a vararg helper. `pvr2_encoder_prep_config()` sends hardware-specific `CX2341X_ENC_MISC` setup. Public functions are `pvr2_encoder_adjust()`, `pvr2_encoder_configure()`, `pvr2_encoder_start()`, and `pvr2_encoder_stop()`.

Control flow: configuration sets cx2341x port, width, height, 50/60 Hz state, sends prep commands, programs vsync/event/VBI settings, applies cx2341x control state, then initializes input. The mailbox command path writes command words with driver flags clear, writes a busy/done flag, polls for firmware done, copies return args, and clears the mailbox. Start unmasks interrupts, optionally mutes video for radio input, and sends `START_CAPTURE` with MPEG or VBI parameters. Stop masks interrupts and sends `STOP_CAPTURE`.

State and persistence: encoder state is tracked in `struct pvr2_hdw`: command buffer, encoder health/run flags, current/control cx2341x state, active stream type, resolution, standard mask, timers, and locks. Hardware mailbox and encoder firmware state persist until reset/reload.

Dependencies and integration: depends on Linux firmware/cx2341x controls, pvrusb2 hardware internals, FX2 command constants, utility endian macros, and trace flags. The cx2341x module calls back into `pvr2_encoder_cmd()` through `cx2341x_update()`.

Risks: mailbox polling has retry and timeout heuristics; repeated failures mark encoder state bad and rely on firmware reload/reinitialization. Read/write chunk formats are limited by FX2 firmware and must stay in sync. Some `ENC_MISC` commands are reverse-engineered and comments document harmful variants. `pvr2_encoder_vcmd()` uses varargs with `u32` expectations; callers must pass correct types.

Test signals: encoder firmware load/configure; V4L2 MPEG control updates; start/stop MPEG and VBI streams; channel change/no-signal recovery without video corruption; forced mailbox timeout; trace encoder commands and state-bit changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-encoder.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-encoder.h

Purpose: public internal prototypes for pvrusb2 CX23416 encoder operations.

Important APIs/types/functions: declares `pvr2_encoder_adjust()`, `pvr2_encoder_configure()`, `pvr2_encoder_start()`, and `pvr2_encoder_stop()`.

Control flow: hardware state-machine code calls configure after firmware/subdevice setup, adjust after control changes, and start/stop around stream transitions.

State and persistence: no state in the header; functions operate on `struct pvr2_hdw`.

Dependencies and integration: forward-declares `struct pvr2_hdw`, keeping callers independent of implementation details.

Risks: callers must ensure encoder firmware is loaded and hardware locks/state permit commands.

Test signals: compile hardware users and run stream lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-fx2-cmd.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-fx2-cmd.h

Purpose: shared FX2 firmware command code definitions for pvrusb2 USB control transactions.

Important APIs/types/functions: defines command bytes for memory/register reads and writes, I2C read/write, USB speed query, streaming on/off, firmware post, Zilog/demod reset pins, power/deep reset, EEPROM address, IR code, and model-specific digital streaming/power commands.

Control flow: hardware, encoder, I2C, IR, firmware, and digital-control code include this header and pass these command values to the lower USB request helper.

State and persistence: no software state. Commands mutate FX2, encoder, I2C, GPIO, power, IR, or digital streaming state in hardware/firmware.

Dependencies and integration: command namespace is shared across pvrusb2 source files and must match FX2 firmware implementations for multiple product generations.

Risks: numeric command drift breaks hardware communication. Some commands exist only on Model 160xxx; using them on other devices requires descriptor gating. Similar analog and DTV streaming commands must not be confused.

Test signals: firmware upload, register/memory access, I2C transfers, analog and DTV stream on/off, IR polling, power/reset commands on supported models.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-fx2-cmd.h -->
