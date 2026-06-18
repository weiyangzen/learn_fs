# Research Report: subset-b-004199

This grouped report covers the requested cx231xx analog capture files and AF9015 DVB USB v2 files. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-reg.h

## Purpose

`cx231xx-reg.h` is the symbolic hardware register map for Conexant Cx23100/Cx23101/Cx23102 USB video capture devices. It contains no executable code; its role is to centralize register addresses, bit masks, video stream marker constants, and enumerated numeric values used by the rest of the `cx231xx` driver. The register definitions cover VBI and active video SAV/EAV codes, host/chip control, AFE controls, analog video decoder/scaler/VBI slicer, audio demodulation, I2S/AC97 routing, DirectIF-related blocks, and video format/input/output constants.

## Important APIs, Types, and Constants

The most integration-sensitive constants are the SAV/EAV byte codes at the top of the file. `SAV_ACTIVE_VIDEO_FIELD1`, `SAV_ACTIVE_VIDEO_FIELD2`, `SAV_VBI_FIELD1`, and `SAV_VBI_FIELD2` are consumed directly by `cx231xx-video.c` and `cx231xx-vbi.c` to detect field boundaries and decide where bytes belong in vb2 buffers.

Register address groups include `HOST_REG*`, `CHIP_CTRL`, `AFE_CTRL`, `PIN_CTRL`, `AUD_IO_CTRL`, `MODE_CTRL`, `OUT_CTRL*`, `GEN_STAT`, `INT_STAT_MASK`, luma/chroma/scaler registers, VBI configuration registers, DFE/PLL/comb/crush/reset controls, firmware download registers such as `DL_CTL`, and audio-demodulator registers under the `0x800` range. Each register is paired with `FLD_*` bit masks used by helper functions such as `cx231xx_reg_mask_write()` and direct I2C register accessors declared in `cx231xx.h`.

The bottom of the file defines semantic constants such as `VID_FMT_NTSC_M`, `VID_FMT_PAL_BDGHI`, `INPUT_MODE_CVBS_0`, `INPUT_MODE_YC_1`, luma/UV filter values, output modes, audio source selectors, and PLL phase increments. These values allow higher-level driver code to express board and standard setup without scattering magic numbers.

## Control Flow

There is no control flow in this header. The functional control flow appears in implementation files that include it. The header shapes control flow indirectly by giving parser functions stable marker values and by giving hardware programming paths stable register masks for read/modify/write operations.

## State and Persistence Behavior

The file itself has no mutable state. It defines the persistent contract between source code and device firmware/register layout. Runtime state lives in `struct cx231xx`, `struct cx231xx_video_mode`, and block-specific helpers that write these registers over USB control or internal I2C transactions. Any register definition error here can persist across multiple driver paths because the same mask may be reused by initialization, mode switching, tuner frequency changes, VBI setup, and debug register access.

## Dependencies and Integration Points

`cx231xx.h` includes this header and exposes the definitions to most driver modules. `cx231xx-video.c` uses `GEN_STAT`, `FLD_VPRES`, `FLD_HLOCK`, and the SAV/EAV constants. VBI capture uses `SAV_VBI_FIELD*`. Board setup, AV core, DIF, audio, GPIO, and core transfer setup files rely on the register addresses and field masks to program chip sub-blocks through `cx231xx_read_i2c_data()`, `cx231xx_write_i2c_data()`, and `cx231xx_reg_mask_write()`.

## Risks

The primary risk is silent hardware misconfiguration. A wrong mask width, register address, or overlapping field value can compile cleanly but alter unrelated bits in the device. The SAV/EAV constants are also parser-critical; incorrect values would cause dropped frames, incorrectly interleaved fields, or VBI/video buffer corruption. Many masks use raw hexadecimal values without typed wrappers, so call sites depend on accurate register width and endian assumptions. Because the header spans multiple hardware blocks, changes should be treated as ABI-like changes for the driver.

## Test Signals

Useful signals include successful analog video streaming in PAL and NTSC, correct VBI capture line counts, stable tuner input detection through `GEN_STAT`, no USB/URB overrun noise while streaming, and no regressions in `CONFIG_VIDEO_ADV_DEBUG` register reads/writes. Hardware smoke tests should cover composite, S-video, tuner, VBI, and audio paths because this header feeds all of them. Build coverage should include configurations with and without VBI, DVB, radio, and advanced debug support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-vbi.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-vbi.c

## Purpose

`cx231xx-vbi.c` implements raw VBI capture for the cx231xx V4L2 driver. It owns the VBI vb2 queue operations, bulk URB allocation and teardown for the VANC endpoint, URB completion handling, SAV/EAV parsing for VBI fields, and copying of VBI samples into userspace-visible videobuf2 buffers. The implementation mirrors the main analog video parser but only accepts VBI SAV markers and lays field 1 and field 2 data into a two-field raw VBI frame.

## Important APIs, Types, and Functions

The exported queue operations are `cx231xx_vbi_qops`, with `vbi_queue_setup()`, `vbi_buf_prepare()`, `vbi_buf_queue()`, `vbi_start_streaming()`, and `vbi_stop_streaming()`. These are installed on `dev->vbiq` by `cx231xx_register_analog_devices()` in `cx231xx-video.c`.

The URB lifecycle is exposed through `cx231xx_init_vbi_isoc()` and `cx231xx_uninit_vbi_isoc()`, both exported with `EXPORT_SYMBOL_GPL`. Despite the name, VBI uses bulk URBs through `usb_fill_bulk_urb()` on `dev->vbi_mode.end_point_addr`. The copy callback passed into initialization is normally `cx231xx_isoc_vbi_copy()`.

The parser and copy path is split across `cx231xx_isoc_vbi_copy()`, `cx231xx_get_vbi_line()`, `cx231xx_copy_vbi_line()`, `cx231xx_reset_vbi_buffer()`, `cx231xx_do_vbi_copy()`, and `cx231xx_is_vbi_buffer_done()`. It reuses shared SAV/EAV scanning helpers declared in `cx231xx.h` and implemented in `cx231xx-video.c`.

## Control Flow

When userspace starts VBI streaming, vb2 calls `vbi_start_streaming()`. The function resets the VBI DMA sequence and calls `cx231xx_init_vbi_isoc()` with `CX231XX_NUM_VBI_PACKETS`, `CX231XX_NUM_VBI_BUFS`, the VBI alternate packet size, and the VBI copy callback. Initialization first calls `cx231xx_uninit_vbi_isoc()` to clear previous URBs, clears endpoint halt, initializes parser counters in `dev->vbi_mode.vidq`, allocates arrays of URB pointers and transfer buffers, fills bulk URBs, submits them, and finally calls `cx231xx_capture_start(dev, 1, Vbi)`.

Each URB completion enters `cx231xx_irq_vbi_callback()`. Nonfatal statuses are logged, fatal unlink/shutdown statuses return, and successful completions take `dev->vbi_mode.slock`, invoke the configured bulk copy callback, release the lock, reset the URB status, and resubmit with `GFP_ATOMIC`.

`cx231xx_isoc_vbi_copy()` scans the transfer buffer for SAV/EAV sequences, including markers split over URB boundaries via `dma_q->partial_buf`. For VBI field markers, `cx231xx_get_vbi_line()` maps `SAV_VBI_FIELD1` and `SAV_VBI_FIELD2` to field numbers and delegates to `cx231xx_copy_vbi_line()`. Copying advances `bytes_left_in_line`, `lines_completed`, `current_field`, and `pos`; once all lines for field 2 are complete, `vbi_buffer_filled()` timestamps and completes the vb2 buffer.

## State and Persistence Behavior

Runtime state is held in `dev->vbi_mode`, particularly `bulk_ctl` and `vidq`. `bulk_ctl` persists URB arrays, transfer buffers, the active vb2 buffer pointer, packet size, and callback. `vidq` persists parser state across URBs: partial SAV bytes, current field, bytes left in line, completed lines, sequence number, and active buffer list. Device-level state such as `dev->norm` and `dev->width` determines VBI line count and buffer size. No on-disk persistence is used.

## Dependencies and Integration Points

This file depends on the cx231xx core for USB endpoint setup, `cx231xx_capture_start()`, and shared parser helpers. It depends on the V4L2/vb2 framework for buffer ownership and on `cx231xx-video.c` for VBI ioctl exposure and registration. It uses constants from `cx231xx-vbi.h` and `cx231xx-reg.h`, including PAL/NTSC VBI line ranges and VBI SAV marker values.

## Risks

Several paths assume nonzero URB payload length before copying the last four bytes into `partial_buf`; short or malformed URBs are a boundary-risk area. Parser state is protected by a spinlock in the URB callback, but open/close and stream teardown interact with URB killing and buffer completion, so regressions can produce use-after-free, double completion, or resubmission after disconnect. VBI size calculations use `dev->width` and norm-derived height; inconsistencies with the V4L2 VBI format constants can expose payload-size mismatches to userspace.

## Test Signals

Expected signals include successful `/dev/vbi*` registration, `VIDIOC_G_FMT` reporting correct PAL or NTSC line ranges, `v4l2-ctl --stream-mmap` or read streaming returning monotonically timestamped buffers, clean streamoff/open-close cycles, no URB resubmit errors after disconnect, and correct operation for both 525-line and 625-line norms. Tests should also exercise VBI capture after analog video streaming because both paths share device power, alternate settings, and parser helper code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-vbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-vbi.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-vbi.h

## Purpose

`cx231xx-vbi.h` is the public internal header for cx231xx raw VBI capture. It declares the VBI vb2 queue operations, PAL/NTSC VBI geometry constants, VBI URB sizing constants, and parser/copy functions implemented by `cx231xx-vbi.c`.

## Important APIs, Types, and Constants

`extern struct vb2_ops cx231xx_vbi_qops` is the main object consumed by analog device registration. The VBI geometry constants define NTSC lines 10-21 and PAL lines 6-23, with `NTSC_VBI_LINES` and `PAL_VBI_LINES` computed from the start/end pairs. `VBI_STRIDE` and `VBI_SAMPLES_PER_LINE` are fixed at 1440, while `CX231XX_NUM_VBI_PACKETS` and `CX231XX_NUM_VBI_BUFS` size the VBI USB transfer ring.

The function declarations expose the stream lifecycle (`cx231xx_init_vbi_isoc()`, `cx231xx_uninit_vbi_isoc()`), line parser (`cx231xx_get_vbi_line()`), copy helpers (`cx231xx_copy_vbi_line()`, `cx231xx_do_vbi_copy()`), parser reset (`cx231xx_reset_vbi_buffer()`), and completion predicate (`cx231xx_is_vbi_buffer_done()`).

## Control Flow

The header has no control flow, but it defines the call graph boundary. `cx231xx-video.c` registers `cx231xx_vbi_qops`; vb2 then calls into `cx231xx-vbi.c`. The URB callback path invokes the parser functions declared here to reconstruct VBI buffers.

## State and Persistence Behavior

No state is stored in the header. The constants encode the driver's expected VBI layout and therefore act as a stable contract among V4L2 format reporting, vb2 queue sizing, and the byte-copy path. State lives in `struct cx231xx_video_mode`, `struct cx231xx_dmaqueue`, and `struct cx231xx_bulk_ctl` from `cx231xx.h`.

## Dependencies and Integration Points

The prototypes require `struct cx231xx`, `struct cx231xx_dmaqueue`, and `struct urb` definitions from included kernel and driver headers. It is included by both VBI implementation and analog video registration. It depends on V4L2/vb2 semantics because `cx231xx_vbi_qops` is installed directly into a `struct vb2_queue`.

## Risks

Mismatch between `VBI_LINE_LENGTH` in `cx231xx.h`, `VBI_STRIDE`/`VBI_SAMPLES_PER_LINE` here, and the copy logic in `cx231xx-vbi.c` would produce incorrect payload sizes or line placement. The header exposes implementation functions broadly inside the driver, so callers must respect the locking and parser-state assumptions used by the URB callback.

## Test Signals

Build coverage should catch missing declarations and type drift. Runtime signals include correct VBI device registration, buffer sizes matching the reported V4L2 raw VBI format, and successful PAL/NTSC VBI streaming without queue errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-vbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-video.c

## Purpose

`cx231xx-video.c` is the main analog V4L2 implementation for cx231xx USB capture devices. It registers and operates video, VBI, and radio devices; manages vb2 queues for analog video; parses incoming BT.656-style active video from isochronous or bulk URBs; exposes V4L2 ioctl handlers; coordinates tuner, decoder, media-controller links, frequency changes, and device power/alternate settings.

## Important APIs, Types, and Functions

The module exposes parameters for card selection and device numbering (`card`, `video_nr`, `vbi_nr`, `radio_nr`) plus debug flags. The supported video format table currently exposes YUYV only.

The parser path includes `cx231xx_find_boundary_SAV_EAV()`, `cx231xx_find_next_SAV_EAV()`, `cx231xx_get_video_line()`, `cx231xx_copy_video_line()`, `cx231xx_reset_video_buffer()`, `cx231xx_do_copy()`, `cx231xx_swab()`, and `cx231xx_is_buffer_done()`. `cx231xx_isoc_copy()` and `cx231xx_bulk_copy()` are URB copy callbacks installed by `start_streaming()`.

The vb2 operations are `queue_setup()`, `buffer_queue()`, `start_streaming()`, and `stop_streaming()`. The V4L2 ioctl surface includes format, standard, input, tuner, frequency, debug register, pixel aspect, selection, and querycap handlers. Shared exported-like driver functions include `video_mux()`, `cx231xx_v4l2_create_entities()`, `cx231xx_enum_input()`, `cx231xx_g_input()`, `cx231xx_s_input()`, `cx231xx_g_tuner()`, `cx231xx_s_tuner()`, `cx231xx_g_frequency()`, `cx231xx_s_frequency()`, `cx231xx_querycap()`, `cx231xx_release_analog_resources()`, and `cx231xx_register_analog_devices()`.

## Control Flow

Analog registration starts in `cx231xx_register_analog_devices()`. It sets default PAL norm and dimensions, selects the initial input via `video_mux()`, propagates the standard to subdevices, initializes V4L2 control handlers, creates and registers the video device, creates and registers the VBI device using `cx231xx_vbi_qops`, and optionally registers radio. Media-controller pads are initialized when enabled.

Open goes through `cx231xx_v4l2_open()`, which locks `dev->lock`, opens the V4L2 file handle, powers the device for analog TV or external AV on the first user, sets video alternate settings, configures I2C, and applies radio or VBI-specific setup. Close goes through `cx231xx_v4l2_close()` and `cx231xx_close()`, releases vb2 state, decrements users, puts tuners into standby on last close, tears down analog URBs, suspends mode, and resets relevant alternate settings.

Video streaming starts when vb2 calls `start_streaming()`. It resets sequence, enables the analog tuner media link if needed, initializes either isochronous or bulk transfers depending on `dev->USE_ISO`, calls subdevices with `s_stream(1)`, and completes queued buffers back to userspace if transfer setup fails. Stop calls `s_stream(0)` and returns active buffers with error state.

The URB copy path searches for SAV/EAV byte sequences, handles markers crossing packet boundaries, maps active field markers to field 1/2, and copies line data into alternating lines of the destination buffer. `cx231xx_swab()` converts UYVY-like incoming words into the YUYV byte order expected by the advertised pixel format. A frame is complete only after field 2 has enough lines and field 1 was completed.

## State and Persistence Behavior

State is centered on `struct cx231xx`: current norm, width, height, format, input, audio input, tuner frequency, user count, V4L2 devices, vb2 queues, control handlers, and transfer mode. Per-stream parser state lives in `dev->video_mode.vidq`, while active URB and buffer pointers live in either `dev->video_mode.isoc_ctl` or `dev->video_mode.bulk_ctl`. No state is persisted across module unload; board EEPROM and hardware state are read or initialized elsewhere.

## Dependencies and Integration Points

This file integrates with V4L2 core, videobuf2 vmalloc memory, media-controller entities, tuner and cx25840 subdevices, DVB frontend headers for hybrid devices, cx231xx USB core transfer helpers, VBI code, board tables, I2C/register helpers, power/mode functions, and optional advanced debug register access. It is the analog side of a hybrid media driver and must coordinate with DVB streaming because the DMA engine cannot serve both paths simultaneously.

## Risks

The parser is sensitive to malformed or short URB data, field loss, and packet-boundary marker handling. `memcpy(dma_q->partial_buf, p_buffer + buffer_size - 4, 4)` assumes enough payload after earlier length checks; isochronous packet checks guard actual length but bulk behavior depends on positive lengths. Buffer completion and stream teardown must avoid racing URB callbacks. Frequency changes contain board-specific IF programming and ignore some intermediate return values, so tuner regressions may be board-specific. The V4L2 format path supports only YUYV and interlaced capture; userspace assumptions outside that format are rejected.

## Test Signals

Strong signals include successful video, VBI, and radio node registration; `v4l2-compliance` for capture and radio ioctls; PAL and NTSC standard switching when not streaming; input switching across composite, S-video, and tuner; streaming by read, mmap, userptr, and dmabuf; clean streamoff/disconnect; tuner frequency changes on board models with both subdevice tuners and direct analog-frequency callbacks; and media-controller link validation on hybrid analog/DVB boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx.h

## Purpose

`cx231xx.h` is the central internal interface for the Conexant cx231xx USB media driver. It collects board IDs, buffer and URB sizing, enums, common data structures, call macros, and function prototypes shared by analog video, VBI, audio, DVB, I2C, GPIO, AFE, DIF, core USB, board setup, and optional IR/MPEG extension code.

## Important APIs, Types, and Functions

Important constants include board IDs from `CX231XX_BOARD_UNKNOWN` through `CX231XX_BOARD_HAUPPAUGE_975`, queue defaults such as `CX231XX_MIN_BUF`, `CX231XX_NUM_BUFS`, `CX231XX_NUM_PACKETS`, VBI sizing, I2C addresses for internal blocks, and audio/stream bit flags.

Core enums describe mode (`CX231XX_SUSPEND`, `CX231XX_ANALOG_MODE`, `CX231XX_DIGITAL_MODE`), stream state, input type, video mux pins, audio mux, decoder presence, I2C master ports, device state, AFE mode, audio input, transfer type, and MPEG packet-header behavior.

Key structures include `cx231xx_isoc_ctl` and `cx231xx_bulk_ctl` for URB rings, `cx231xx_buffer` for vb2 buffers, `cx231xx_dmaqueue` for parser progress, `cx231xx_input` and `cx231xx_board` for board capabilities and routing, `cx231xx_audio`, `cx231xx_i2c`, `cx231xx_i2c_xfer_data`, `VENDOR_REQUEST_IN`, `cx231xx_tvnorm`, `cx231xx_video_mode`, `cx231xx_tsport`, and the main `struct cx231xx`.

Function prototypes cover every subsystem: I2C registration and data transfer, GPIO, AFE/I2S/DIF setup, video parsing, core USB control, URB initialization/teardown, mode and power control, stream start/stop, analog V4L2 registration/ioctls, board setup, extension registration, cx23417 MPEG support, and optional remote-control init/exit.

## Control Flow

The header defines cross-file call paths rather than executing them. Probe/board setup code fills `struct cx231xx`, registers I2C and V4L2 subdevices, and calls `cx231xx_register_analog_devices()` or DVB extension code depending on board capabilities. V4L2 streaming and DVB streaming then use the transfer structures and function pointers declared here. Subdevice calls are routed through `cx25840_call()`, `tuner_call()`, and `call_all()`.

## State and Persistence Behavior

`struct cx231xx` is the persistent in-kernel state for a device instance. It tracks model, board copy, USB device, V4L2 devices, subdevices, controls, tuner identity, current norm/frequency/input, dimensions, audio state, I2C buses and muxes, GPIO values, power mode, AFE state, active mode, VBI/sliced CC mode, transport stream ports, MPEG state, and work items. Parser state persists while streams run in `cx231xx_dmaqueue`. Hardware-derived EEPROM data is cached in `eedata[256]`.

## Dependencies and Integration Points

The header depends on Linux USB, I2C, V4L2, videobuf2, rc-core, cx2341x, and local register/config headers. It is included throughout the `cx231xx` driver and forms the dependency bridge between analog video files, VBI, audio, DVB, board tables, core USB, and AV/DIF configuration files. Because it declares optional inline stubs for IR, it also controls build behavior when `CONFIG_VIDEO_CX231XX_RC` is disabled.

## Risks

This is a high-blast-radius header: changes can rebuild or alter behavior across the entire driver. Layout changes to `struct cx231xx`, transfer controls, or parser queues can break assumptions in URB callbacks and teardown paths. Board flag semantics affect device registration and power/routing behavior. The main structure mixes lifetime domains including USB device, V4L2 objects, I2C clients, work items, and streaming buffers, so locking and ownership must be checked carefully for every field addition or user.

## Test Signals

Signals include all `cx231xx` translation units compiling under analog-only, DVB, audio, RC, media-controller, and advanced-debug configurations; successful probe/disconnect of supported board IDs; analog video, VBI, radio, DVB, audio, and IR smoke tests where available; and no sparse/coccinelle warnings around pointer ownership, missing prototypes, or structure-field type drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/Kconfig

## Purpose

This `Kconfig` file defines the build-time configuration menu for the second-generation DVB USB driver framework and the individual USB receiver drivers that sit on top of it. It lets kernel builders enable the shared `DVB_USB_V2` core and then select device-specific drivers such as AF9015, AF9035, Anysee, RTL28xxU, MxL111SF, and others.

## Important APIs, Types, and Symbols

`config DVB_USB_V2` is the umbrella tristate. It depends on `DVB_CORE`, `USB`, `I2C`, and either `RC_CORE` or no RC support. Its help text points users to firmware requirements and supported-device documentation.

Inside `if DVB_USB_V2`, each device driver gets a tristate symbol. `DVB_USB_AF9015` depends on `DVB_USB_V2 && I2C_MUX`, selects `REGMAP` and `DVB_AF9013`, and conditionally selects tuner/front-end helpers under `MEDIA_SUBDRV_AUTOSELECT`. Other symbols express similar dependencies, including hard dependencies such as `RC_CORE` for `DVB_USB_LME2510` and conditional SDR support for `DVB_USB_RTL28XXU`.

## Control Flow

Kconfig has declarative dependency flow. Enabling `DVB_USB_V2` makes the child choices visible. Enabling a child symbol controls which object targets the Makefile builds and which frontend/tuner modules are selected automatically. Conditional `select` clauses reduce manual configuration burden when `MEDIA_SUBDRV_AUTOSELECT` is enabled.

## State and Persistence Behavior

The file persists configuration state through kernel `.config` symbols. At runtime it has no state, but selected symbols determine which modules exist, which firmware names are requested, and which probe tables can bind to USB devices.

## Dependencies and Integration Points

This file integrates with `drivers/media/usb/dvb-usb-v2/Makefile`, the DVB core, USB core, I2C, rc-core, regmap, DVB frontend drivers, tuner drivers, and media-subdriver autoselection. For AF9015 specifically, its Kconfig entry enables the code in `af9015.c` and ensures the AF9013 demodulator and relevant tuner drivers can be built.

## Risks

Incorrect dependencies can produce link failures, missing symbols, or unusable drivers that compile without required subdrivers. Overbroad `select` usage can force in dependencies unexpectedly, while missing conditional selects can leave common hardware unsupported unless users know which tuner module to enable manually. Device support is firmware-dependent, so enabling the symbol does not guarantee runtime success.

## Test Signals

Useful checks include `make olddefconfig` and build tests for `DVB_USB_V2=m/y`, each child driver as module and built-in, `MEDIA_SUBDRV_AUTOSELECT` both enabled and disabled, and RC support enabled/disabled where allowed. Runtime smoke testing should confirm enabled USB IDs bind to expected modules and request expected firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/Makefile

## Purpose

This Makefile maps DVB USB v2 Kconfig symbols to kernel objects. It builds the shared `dvb_usb_v2` core and each selected device-specific module, and it adds include paths for DVB frontend, tuner, and common media headers.

## Important APIs, Types, and Targets

`dvb_usb_v2-objs` is composed of `dvb_usb_core.o`, `dvb_usb_urb.o`, and `usb_urb.o`; `obj-$(CONFIG_DVB_USB_V2)` emits the shared module or built-in object. Each device driver has an object list such as `dvb-usb-af9015-objs := af9015.o` and an `obj-$(CONFIG_DVB_USB_AF9015)` assignment. MxL111SF is split into multiple objects and also builds `mxl111sf-demod.o` and `mxl111sf-tuner.o` as separate targets under the same config.

The `ccflags-y` entries add include directories for `drivers/media/dvb-frontends`, `drivers/media/tuners`, and `drivers/media/common`, allowing device drivers such as `af9015.c` to include frontend/tuner headers directly.

## Control Flow

The build flow is controlled entirely by Kconfig-expanded `obj-*` variables. When a config symbol is `m`, the corresponding module object is built as a module; when `y`, it is linked into the kernel image. The source-to-object mapping is one-to-one for most device drivers, while shared core objects are grouped into the `dvb_usb_v2` composite.

## State and Persistence Behavior

There is no runtime state. Build state is persisted in generated object files and modules according to the active kernel configuration. The Makefile also encodes the stable module names, such as `dvb-usb-af9015`.

## Dependencies and Integration Points

This file integrates with the Kbuild system and the `Kconfig` file in the same directory. It also indirectly enforces source layout expectations: `af9015.c` becomes the only object in `dvb-usb-af9015`, while shared code remains in `dvb_usb_v2`. Include path choices couple this directory to frontend and tuner header locations.

## Risks

Misaligned object names and Kconfig symbols can result in drivers never being built. Missing include paths can break compile coverage for tuners/frontends. Composite module changes must preserve expected module names because userspace, documentation, initramfs module lists, and alias handling may refer to existing names.

## Test Signals

Build tests should verify module and built-in configurations for `DVB_USB_V2` and each child driver. `modinfo dvb-usb-af9015` should show USB aliases emitted from `af9015.c`, and dependency generation should include selected tuner/frontend modules when autoselection is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/af9015.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/af9015.c

## Purpose

`af9015.c` is the DVB USB v2 device driver for Afatech AF9015 DVB-T USB2.0 receivers and compatible products. It implements AF9015 USB command framing, firmware download/boot, EEPROM-based hardware configuration, an I2C adapter for demodulator/tuner access, AF9013 frontend attachment, tuner attachment for several tuner chips, dual-tuner stream setup, PID filtering, remote-control polling, regmap access, USB probe/disconnect, and the USB ID table.

## Important APIs, Types, and Functions

The lowest layer is `af9015_ctrl_msg()`, which serializes `struct req_t` commands into the device bulk control endpoint, assigns sequence numbers, switches high-level read/write I2C commands to the hardware `READ_WRITE_I2C` command, handles virtual memory writes, bounds payload length against `BUF_LEN`, and validates the two-byte ACK/status response.

The I2C layer consists of `af9015_i2c_xfer()`, `af9015_i2c_func()`, and `af9015_i2c_algo`. It supports plain writes, write-then-read register reads, and reads to non-demod addresses, with special address-length behavior for AF9013 demodulators.

Device setup includes `af9015_identify_state()`, `af9015_download_firmware()`, `af9015_eeprom_hash()`, `af9015_read_config()`, `af9015_probe()`, and `af9015_disconnect()`. Frontend/tuner setup includes `af9015_af9013_frontend_attach()`, `af9015_frontend_detach()`, `af9015_tuner_attach()`, and the callback wrappers that serialize demod/tuner init, sleep, tuning, and status through `state->fe_mutex`.

Streaming is controlled by `af9015_get_stream_config()`, `af9015_streaming_ctrl()`, and `af9015_get_adapter_count()`. PID filtering delegates to AF9013 platform callbacks under the same mutex. Remote control support is compiled under `CONFIG_RC_CORE` through `af9015_rc_query()` and `af9015_get_rc_config()`.

## Control Flow

USB binding uses `af9015_usb_driver`, whose probe is the DVB USB v2 generic probe. The generic layer consumes `af9015_props`, calls `af9015_probe()` to reject known conflicting TerraTec IT9135 hardware and initialize regmap, identifies warm/cold firmware state, downloads firmware if needed, reads EEPROM configuration, attaches frontends and tuners, initializes RC state, and configures stream properties.

Firmware download chunks the firmware to the device memory window at `0x5100`, records firmware size and checksum for possible slave-demod copy, and sends `BOOT`. Dual-mode devices attach adapter 0 as USB TS mode and adapter 1 as serial TS mode. For adapter 1, `af9015_copy_firmware()` copies the downloaded firmware image from the master demodulator to the second demodulator, boots it, and polls firmware status.

Streaming control lazily configures USB endpoint and transport-stream registers once per adapter. Adapter 0 uses EP4 and adapter 1 uses EP5; on stream-on it clears NAK, enables endpoint output, and clears reset bits, while stream-off reverses the sequence. Bulk stream descriptors in `af9015_props` expose endpoint `0x84` and `0x85` with six buffers sized at `87 * 188` bytes, adjusted for full-speed USB.

## State and Persistence Behavior

Driver state lives in `struct af9015_state`: regmap, shared command buffer, IR mode and last RC data, dual-mode flag, USB command sequence, MT2060 IF values, firmware size/checksum, EEPROM hash, AF9013 platform data, demod I2C clients, demod addresses, per-adapter USB TS configuration flags, saved demod/tuner callbacks, and frontend mutex. EEPROM values persist in device hardware and are read at probe to populate clock, IF, tuner, spectral inversion, IR, dual-mode, and second-demod address fields. Runtime state is not persisted after disconnect.

## Dependencies and Integration Points

The file depends on `dvb_usb.h`, AF9013 demodulator support, regmap, Linux firmware loading, USB core, I2C core, rc-core, and tuner drivers for MT2060, QT1010, TDA18271, MXL5005S, MC44S803, TDA18218, MXL5007T, and DVB PLL. Kconfig selects the common dependencies for typical builds. The USB ID table binds many vendor/product IDs to `af9015_props` and optional RC maps.

## Risks

The command buffer is shared and protected by `d->usb_mutex`; any bypass could corrupt in-flight USB messages. I2C transaction length limits are hardware-specific, so frontend/tuner code must respect 21-byte write and 61-byte read maxima. EEPROM parsing has board-specific overrides for bad AVerMedia data, indicating real-world devices may ship invalid descriptors. Dual-mode firmware copy is timing-sensitive and can disable the second frontend on failure. Remote polling intentionally masks intermittent errors once to prevent the DVB USB core from stopping RC polling, which can hide noisy hardware conditions. The TerraTec ID conflict depends on manufacturer string matching.

## Test Signals

Build signals include `CONFIG_DVB_USB_AF9015=m/y` with `MEDIA_SUBDRV_AUTOSELECT` on and off, plus RC enabled/disabled. Runtime signals include successful firmware request for `dvb-usb-af9015.fw`, warm/cold identification, EEPROM dump/hash, frontend attach for one- and two-adapter devices, tuner attach for each supported tuner ID, lock/tune/status operations without I2C contention, stream-on/off for EP4 and EP5, PID filter enable and PID programming, RC key decoding for NEC/NECX/NEC32, correct rejection of TerraTec IT9135 devices sharing `0ccd:0099`, and clean regmap teardown on disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/af9015.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/af9015.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/af9015.h

## Purpose

`af9015.h` defines the private driver contract for the AF9015 DVB USB v2 driver. It includes required DVB USB, AF9013, regmap, frontend, and tuner headers; names the firmware; defines EEPROM offsets and I2C addresses; describes the USB command packet; enumerates AF9015 command and IR modes; and stores per-device private state.

## Important APIs, Types, and Constants

`AF9015_FIRMWARE` is `dvb-usb-af9015.fw`, the firmware requested by the DVB USB core. `AF9015_I2C_EEPROM` and `AF9015_I2C_DEMOD` define hardware I2C addresses. EEPROM offsets cover IR mode, remote type, TS mode, second demod address, per-adapter SAW bandwidth, crystal type, spectral inversion, IF frequency, MT2060 IF, and tuner ID. `AF9015_EEPROM_OFFSET` maps the adapter-1 EEPROM block from the adapter-0 base offsets.

`struct req_t` is the in-driver representation of an AF9015 control message: command, I2C address, register address, mailbox byte, address length, data length, and data pointer. `enum af9015_cmd` lists device commands including configuration, firmware download/boot, memory read/write, I2C read/write, firmware copy, reconnect, virtual memory write, and IR code read. `enum af9015_ir_mode` names firmware IR transport modes.

`struct af9015_state` is the private state allocated by `af9015_props`. It holds regmap, a 63-byte USB command buffer, IR tracking fields, dual-mode flag, USB sequence number, firmware metadata, EEPROM hash, AF9013 platform data for two frontends, demod I2C clients and addresses, per-adapter TS configuration flags, saved callback pointers, and a frontend mutex. `enum af9015_remote` maps module-parameter values to known remote profiles.

## Control Flow

The header does not execute control flow, but it defines data consumed throughout `af9015.c`. Probe allocates `struct af9015_state`, initializes regmap and mutexes, then EEPROM parsing fills `af9013_pdata`, tuner attach uses the tuner IDs and platform data, streaming uses `usb_ts_if_configured`, and RC setup uses IR and remote fields.

## State and Persistence Behavior

All mutable state is per USB device instance. EEPROM-derived data is copied into memory at probe. Firmware size and checksum are saved only to support copying firmware to a second demodulator during the same device lifetime. The command sequence byte increments per control message and is not persisted across disconnect.

## Dependencies and Integration Points

This header couples the AF9015 driver to the DVB USB v2 core, AF9013 demodulator, regmap, `linux/hash.h`, and every tuner frontend it may attach. It is included by `af9015.c` only in this subset, but its included tuner headers require Kconfig/Makefile include paths and selected subdrivers to remain aligned.

## Risks

Changing `BUF_LEN` or `struct req_t` semantics affects every USB command. Changes to EEPROM offsets can mis-detect tuner, clock, IF, IR, or dual-mode hardware. `struct af9015_state` stores callback pointers that wrap frontend/tuner operations; incorrect indexing or missing initialization can crash on dual-adapter paths. Adding tuner support requires coordinated enum handling in AF9013 data, Kconfig selects, includes, and `af9015_tuner_attach()`.

## Test Signals

Compile tests should verify all included tuner/frontend headers are available under AF9015 configurations. Runtime tests should confirm EEPROM-derived fields match hardware, both `af9013_pdata[0]` and `[1]` are correct on dual devices, remote module parameter mapping works, and firmware copy state is valid for adapter 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/af9015.h -->
