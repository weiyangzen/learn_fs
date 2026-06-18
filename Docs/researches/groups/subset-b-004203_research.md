# subset-b-004203 Research

Grouped research for the requested DVB USB driver files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cxusb-analog.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cxusb-analog.c

## Purpose
Implements the optional analog/V4L2 half of the Conexant CXUSB Medion MD95700 hybrid DVB-T/analog capture driver. It registers `/dev/video*` and `/dev/radio*` devices, configures the CX25840 video decoder plus analog tuner/IF demodulator, receives BT.656 video over isochronous USB endpoint 2, converts that byte stream into UYVY vb2 capture buffers, and coordinates analog opens with the digital path through the shared `cxusb_medion_get()`/`cxusb_medion_put()` arbitration implemented in `cxusb.c`.

## Important APIs, Types, And Functions
The file consumes the shared `struct cxusb_medion_dev`, `struct cxusb_medion_auxbuf`, `struct cxusb_bt656_params`, and `struct cxusb_medion_vbuffer` declarations from `cxusb.h`. The main external entry points are `cxusb_medion_analog_init()`, `cxusb_medion_register_analog()`, and `cxusb_medion_unregister_analog()`. V4L2/vb2 integration is provided by `cxdev_video_qops`, `cxusb_video_ioctl`, `cxusb_radio_ioctl`, `cxusb_video_fops`, and `cxusb_radio_fops`.

Important internal groups are:

- Buffer setup: `cxusb_medion_v_queue_setup()`, `cxusb_medion_v_buf_init()`, and `cxusub_medion_v_buf_queue()` validate UYVY buffer sizing and maintain `cxdev->buflist`.
- Auxiliary stream buffering: `cxusb_auxbuf_*()` tracks the concatenated isochronous payload and trims old bytes when a new URB would exceed the auxiliary buffer.
- BT.656 parsing: `cxusb_medion_cf_refc_*()`, `cxusb_medion_copy_samples()`, `cxusb_medion_copy_field()`, and `cxusb_medion_v_process_auxbuf()` search SAV/EAV preambles, handle field changes, pad missing line samples, skip VBI data, and complete vb2 frames.
- URB lifecycle: `cxusb_medion_v_start_streaming()`, `cxusb_medion_v_complete()`, `cxusb_medion_v_complete_work()`, `cxusb_medion_v_complete_handle_urb()`, `cxusb_medion_v_stop_streaming()`, and `cxusb_medion_urbs_free()` allocate isochronous URBs, resubmit them from workqueue context, and tear them down.
- Analog controls: format, input, tuner, frequency, standard, and status ioctls are implemented by `cxusb_medion_*fmt*`, `cxusb_medion_*input*`, `cxusb_medion_*tuner*`, `cxusb_medion_*frequency*`, `cxusb_medion_*std*`, and `cxusb_medion_log_status()`.

## Control Flow
Registration starts in `cxusb_medion_register_analog()`: initialize `dev_lock`, a V4L2 release completion, register `v4l2_device`, attach subdevices with `cxusb_medion_register_analog_subdevs()`, initialize URB work and the queued-buffer list, set a conservative 320x240 default capture size, then register the video and radio devices. Subdevice registration attaches the CX25840 at `0x44`, the tuner at `0x61`, and the TDA9887-compatible IF demod at `0x43`, then configures the tuner type and CX25840 BT.656 output mode.

Open flow is deliberately routed through the shared Medion mode gate. `cxusb_videoradio_open()` calls `cxusb_medion_get(dvbdev, CXUSB_OPEN_ANALOG)` before `v4l2_fh_open()`, causing the core driver to power the device, switch USB alternate setting/mode to analog, and run `cxusb_medion_analog_init()` if analog was not already active. Release calls `vb2_fop_release()` for video or `v4l2_fh_release()` for radio, then decrements the shared open counter with `cxusb_medion_put()`.

Streaming starts through vb2. `cxusb_medion_v_start_streaming()` determines field order, starts CX25840 streaming, sends `CMD_STREAMING_ON`, allocates an auxiliary buffer sized around one frame plus one URB, allocates up to five isochronous URBs, and submits them. USB completion only records which URB completed and schedules work. The work handler runs under the video-device lock, appends completed URB payloads into the auxiliary buffer, parses enough BT.656 data to complete frames, resubmits URBs, and reschedules itself while buffered data can produce more frames. Stop flow sends `CMD_STREAMING_OFF`, stops the CX25840, temporarily drops the video lock so completions can drain, kills all URBs, flushes the work item, frees buffers, returns outstanding vb2 buffers with error state, and clears `stop_streaming`.

## State And Persistence
Persistent in-kernel state lives in `struct cxusb_medion_dev`: current V4L2 input, norm, width/height, field order, stop flag, auxiliary stream bytes, URB pointers/completion bitmap, current BT.656 parser position, active vb2 buffer, frame sequence, queued buffer list, V4L2 subdevice pointers, and video/radio device pointers. There is no disk persistence. Device-visible state is changed through USB vendor commands, USB alternate-interface selection done by `cxusb.c`, I2C writes to the tuner, and V4L2 subdevice operations on CX25840/tuner/TDA9887.

## Dependencies And Integration Points
The file depends on the media core, V4L2 subdev API, videobuf2-vmalloc, CX25840 driver interface definitions, tuner framework, and the DVB USB CXUSB core. It is compiled only when `CONFIG_DVB_USB_CXUSB_ANALOG` enables the declarations in `cxusb.h`; otherwise the public analog hooks become stubs. It integrates tightly with `cxusb.c`: `cxusb_probe()` registers analog support only for the Medion device, `cxusb_medion_get()` calls `cxusb_medion_analog_init()` during analog mode acquisition, and disconnect calls `cxusb_medion_unregister_analog()`.

## Risks
The largest risk area is concurrency between vb2 stop, URB completions, and workqueue parsing; the code explicitly drops/reacquires the video lock and uses `usb_kill_urb()` plus `flush_work()` to manage this. Auxiliary buffer overwrite resets the current frame parser, so high USB jitter or slow workqueue processing can skip frames. The BT.656 parser pads malformed or early field/line transitions with zeroes, which is robust for frame completion but can hide signal timing problems. Mode switching shares hardware with the DVB frontend, so any missed `cxusb_medion_put()` or failed acquisition can block analog or digital users. Radio support is intentionally incomplete because audio support is still TODO.

## Test Signals
Useful test signals are successful creation/removal of video and radio nodes on Medion MD95700 probe/disconnect, analog open returning `-EBUSY` while digital streaming owns the device, `VIDIOC_QUERYCAP`/format/input/std/frequency operations succeeding through V4L2 compliance tools, stable `vb2` streaming with queued buffers receiving monotonically increasing UYVY frames, clean stream stop without URB resubmit errors or leaked buffers, and kernel logs from `CXUSB_DBG_BT656`, `CXUSB_DBG_URB`, `CXUSB_DBG_OPS`, and `CXUSB_DBG_AUXB` when diagnosing malformed BT.656 streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cxusb-analog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cxusb.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cxusb.c

## Purpose
Implements the main DVB USB driver for Conexant CXUSB/Bluebird-style USB TV devices. It provides bridge control messaging, I2C master access, GPIO helpers, power and streaming callbacks, remote-control polling, frontend/tuner attachment for many board variants, Medion analog/digital mode arbitration, firmware state/download quirks, USB probe/disconnect, and the `dvb_usb_device_properties` tables consumed by the DVB USB framework.

## Important APIs, Types, And Functions
The exported/shared APIs are `cxusb_ctrl_msg()`, `cxusb_medion_get()`, and `cxusb_medion_put()`. `cxusb_ctrl_msg()` is the bridge command primitive: it bounds commands by `MAX_XFER_SIZE`, serializes through `d->data_mutex`, prepends the command byte, calls `dvb_usb_generic_rw()`, and copies the optional response.

Key internal APIs include:

- I2C and GPIO: `cxusb_i2c_xfer()`, `cxusb_i2c_algo`, `cxusb_gpio_tuner()`, `cxusb_bluebird_gpio_rw()`, `cxusb_bluebird_gpio_pulse()`, `cxusb_nano2_led()`, and `cxusb_d680_dmb_gpio_tuner()`.
- Power/streaming: `_cxusb_power_ctrl()`, `cxusb_power_ctrl()`, `cxusb_aver_power_ctrl()`, `cxusb_bluebird_power_ctrl()`, `cxusb_nano2_power_ctrl()`, `cxusb_d680_dmb_power_ctrl()`, `cxusb_streaming_ctrl()`, `cxusb_aver_streaming_ctrl()`, and `cxusb_d680_dmb_streaming_ctrl()`.
- Remote control: `cxusb_rc_query()`, `cxusb_bluebird2_rc_query()`, and `cxusb_d680_dmb_rc_query()`.
- Attachment callbacks: board-specific `*_frontend_attach()` and `*_tuner_attach()` functions for CX22702, LGDT3303, MT352, ZL10353, XC2028/XC3028, MXL5005S, DiB7000P/DiB0070, LGS8GXX, ATBM8830, and MAX2165 devices.
- Probe/lifetime: `cxusb_probe()`, `cxusb_disconnect()`, `bluebird_fx2_identify_state()`, `bluebird_patch_dvico_firmware_download()`, `cxusb_medion_priv_init()`, and `cxusb_medion_priv_destroy()`.

## Control Flow
The USB driver registers as `dvb_usb_cxusb` with `cxusb_table`. Probe tries Medion first because it has hybrid analog handling, then tries each Bluebird/Aver/Conexant property table until `dvb_usb_device_init()` accepts the device. For Medion, probe validates the analog isochronous alternate setting, powers the hardware, switches to analog, registers V4L2 analog devices through `cxusb_medion_register_analog()`, switches back to digital, powers down, then releases the initial `CXUSB_OPEN_INIT` state through `cxusb_medion_put()`.

Digital streaming generally enters `cxusb_streaming_ctrl()`. On Medion, starting digital streaming first acquires `CXUSB_OPEN_DIGITAL`; failure returns immediately if analog owns the device. It then sends `CMD_STREAMING_ON`; stopping sends `CMD_STREAMING_OFF` and releases the Medion open reference. Other boards use simpler bridge-specific streaming commands or drain USB pipes before enabling.

Frontend attachment selects USB alternate settings, sends `CMD_DIGITAL`, performs board-specific GPIO resets, and calls `dvb_attach()` for the expected demodulator. Tuner attach callbacks then attach or configure the matching tuner. Device property tables bind these callbacks to USB IDs, stream endpoint/buffer settings, firmware requirements, RC maps, and power callbacks.

Medion mode arbitration is centralized in `cxusb_medion_get()`/`cxusb_medion_put()`. The open lock protects `open_type` and `open_ctr`. First acquisition for a different mode powers the device, calls `cxusb_medion_set_mode()` to select USB altsetting 6 for digital or 1 for analog, clears bulk pipe halts, sends `CMD_DIGITAL` or `CMD_ANALOG`, marks GPIO state stale, and, for analog, calls `cxusb_medion_analog_init()`. Additional users of the same mode increment the count; opposite-mode acquisition returns `-EBUSY`.

## State And Persistence
`struct cxusb_state` holds cached GPIO write state/refresh flags, optional I2C client handles, a command buffer, a stream mutex, and saved frontend status hooks. Medion extends this through `struct cxusb_medion_dev` in `cxusb.h`. The driver persists no data to disk. Runtime state is held in kernel objects owned by the DVB USB framework, the I2C adapter, attached frontend/tuner modules, RC core, V4L2 analog devices, and USB device/interface settings. Firmware download patching creates a temporary in-memory firmware copy for some DViCO devices.

## Dependencies And Integration Points
This file sits at the intersection of USB core, DVB USB framework, Linux media frontend/tuner modules, I2C core, RC core, and optional V4L2 analog support. It includes many demod/tuner headers and uses `dvb_attach()` so module availability matters. `cxusb.h` provides shared state and debug definitions; `cxusb-analog.c` supplies analog hooks when configured. Firmware names include `dvb-usb-bluebird-01.fw`, `dvb-usb-bluebird-02.fw`, and Cypress FX2 paths via the DVB USB framework.

## Risks
Several board paths rely on reverse-engineered command values and magic register sequences, so regressions can be hardware-specific. `cxusb_i2c_xfer()` must keep transfer lengths within `MAX_XFER_SIZE`; unsupported transaction shapes or oversized messages return errors. Medion mode switching is sensitive because comments note switching during I2C transactions can crash the device, hence `cxusb_medion_set_mode()` serializes with `i2c_mutex`. Power-off is deliberately blocked while analog owns the device; mistakes there can reset active V4L2 capture. Firmware patching depends on hard-coded offsets. Probe tries many property tables in sequence, making USB-ID overlap and cold/warm identification important.

## Test Signals
Test signals include successful `dvb_usb_device_init()` for each supported USB ID, firmware download and cold/warm transition behavior for Bluebird devices, I2C scan/attach success for each demod/tuner pair, TS streaming start/stop on the expected endpoint, remote-control key events matching the configured RC map, Medion analog/digital mutual exclusion returning `-EBUSY` when expected, and clean disconnect that unregisters analog V4L2 devices and any I2C client devices without leaks or use-after-free reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cxusb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cxusb.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cxusb.h

## Purpose
Defines the shared private state, constants, debug helpers, bridge command IDs, Medion analog data structures, and cross-file function prototypes for the CXUSB DVB USB driver. It is the contract between `cxusb.c` and the optional `cxusb-analog.c` implementation.

## Important APIs, Types, And Functions
The header defines USB bridge commands such as `CMD_I2C_WRITE`, `CMD_I2C_READ`, `CMD_POWER_ON`, `CMD_STREAMING_ON`, `CMD_ANALOG`, and `CMD_DIGITAL`, plus GPIO and BT.656 bit masks used by the C files. Video constants include five URBs, a 512 KiB maximum URB transfer, 3030-byte isochronous packets, and frame sizing limits.

Core types:

- `struct cxusb_state`: base private state used by all CXUSB devices, including GPIO cache, optional I2C clients, bounded command buffer, stream mutex, and saved frontend status callback.
- `enum cxusb_open_type`: Medion ownership states for initialization, idle, analog, and digital access.
- `struct cxusb_medion_auxbuf`: rolling byte buffer for analog isochronous payloads.
- `enum cxusb_bt656_mode`, `enum cxusb_bt656_fmode`, and `struct cxusb_bt656_params`: state machine for frame/field and line/VBI parsing.
- `struct cxusb_medion_dev`: Medion-specific private state. It deliberately begins with `struct cxusb_state` so the same `dvbdev->priv` pointer can be used as base CXUSB state or Medion extended state.
- `struct cxusb_medion_vbuffer`: vb2 buffer wrapper with a queue list node.

The public prototypes are `cxusb_ctrl_msg()`, `cxusb_medion_get()`, and `cxusb_medion_put()`. When analog support is enabled, the header also declares `cxusb_medion_analog_init()`, `cxusb_medion_register_analog()`, and `cxusb_medion_unregister_analog()`; otherwise it provides stubs that fail or no-op as appropriate.

## Control Flow
The header has no runtime control flow, but it shapes the driver flow. `cxusb.c` allocates private storage based on property tables and treats `dvbdev->priv` as `struct cxusb_state` for generic devices or `struct cxusb_medion_dev` for Medion. Analog registration and open flows compile to real calls only under `CONFIG_DVB_USB_CXUSB_ANALOG`; without that option, Medion analog initialization fails with `-EINVAL` and registration/unregistration become harmless no-ops.

## State And Persistence
All state described here is transient kernel driver state. `gpio_write_state` and `gpio_write_refresh` cache bridge GPIO state across mode switches. `open_type`/`open_ctr` protect hardware ownership for Medion analog versus digital users. V4L2 state includes subdevice pointers, video/radio devices, current input/norm/format, queued capture buffers, URB completion bits, active parser state, and completion used for release synchronization. No persistent storage or userspace-visible configuration file is defined.

## Dependencies And Integration Points
The header pulls in Linux completion, I2C, list, mutex, USB, workqueue, V4L2, and videobuf2 headers, then includes `dvb-usb.h` under the CXUSB log prefix. It is included by both CXUSB source files and provides their shared debug macro `cxusb_vprintk()`, which assumes the device private pointer is a `struct cxusb_medion_dev` when analog debug output is used.

## Risks
The leading-member layout requirement in `struct cxusb_medion_dev` is important; changing it would break casts in `cxusb.c` that expect `struct cxusb_state` at offset zero. The analog fields are compiled only under a Kconfig guard, so any unguarded access from generic code would break non-analog builds. `MAX_XFER_SIZE` bounds bridge command payloads and must stay in sync with actual command buffer usage. The debug macro is Medion/V4L2-specific and should not be used on generic devices without confirming `priv` layout.

## Test Signals
Build coverage should include both `CONFIG_DVB_USB_CXUSB_ANALOG=y/m` and disabled configurations to exercise real analog prototypes and stub paths. Runtime signals include correct private-size setup for generic versus Medion devices, stable analog/digital open counting, and no compiler warnings when media/V4L2 or DVB USB APIs change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cxusb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dib0700.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dib0700.h

## Purpose
Defines the shared interface for drivers of DiBcom DiB0700 USB bridge devices. It declares vendor request IDs, debug categories, private bridge state, exported bridge helper functions, the I2C algorithm, and the device/USB-ID tables implemented by the DiB0700 driver family.

## Important APIs, Types, And Functions
The request constants encode the bridge firmware protocol: version query, old/new I2C read/write, GPIO, clock, USB transfer length, remote-control mode, video enable, firmware jump-to-RAM, and I2C speed parameters. `struct dib0700_state` is the private runtime state: streaming channel bitmap, tuner IF values, RC toggle/counter, firmware capability flags, firmware version, TS packet buffer size, saved frontend hooks, a 255-byte command buffer, and optional demod/tuner I2C client handles.

Declared functions include `dib0700_get_version()`, `dib0700_set_gpio()`, `dib0700_ctrl_clock()`, `dib0700_ctrl_rd()`, `dib0700_download_firmware()`, `dib0700_rc_setup()`, `dib0700_streaming_ctrl()`, `dib0700_identify_state()`, `dib0700_change_protocol()`, and `dib0700_set_i2c_speed()`. It also exports `dib0700_i2c_algo`, `dib0700_device_count`, `dib0700_devices[]`, and `dib0700_usb_id_table[]`.

## Control Flow
The header itself is declarative. It enables `dib0700_core.c` to provide common bridge behavior while board-specific DiB0700 files can reference the same state and helper API. The DVB USB framework consumes the exported device property and USB ID tables, while I2C, RC, firmware, and streaming callbacks call back into the helpers declared here.

## State And Persistence
All state is in-memory driver state attached to a `struct dvb_usb_device`. Firmware version and capability fields are discovered at probe/download time and then guide I2C, RC, and streaming behavior. `channel_state` persists active adapter streaming bits across streaming-control calls so multi-adapter devices can enable/disable channels without clobbering peers. No disk state is represented.

## Dependencies And Integration Points
The header includes `dvb-usb.h` with the DiB0700 log prefix and `dib07x0.h` for GPIO enumeration. It integrates with the DVB USB framework, USB control/bulk firmware protocol, Linux I2C core, and RC core. Board-specific files are expected to define `dib0700_devices[]`, `dib0700_usb_id_table[]`, and `dib0700_device_count`.

## Risks
The request IDs and buffer layout are firmware ABI. Changes must be coordinated with the firmware versions handled in `dib0700_core.c`. `struct dib0700_state::buf` is shared by many commands and must be protected by the appropriate USB/I2C mutexes. Feature flags such as `fw_use_new_i2c_api` and `disable_streaming_master_mode` must be initialized consistently by board/probe code or callbacks may use the wrong command format.

## Test Signals
Compile tests should cover all DiB0700 board objects that include this header. Runtime signals are correct firmware version decoding, successful I2C transactions through `dib0700_i2c_algo`, GPIO/clock setup success, RC protocol switching, and streaming-control behavior on single- and dual-adapter devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dib0700.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dib0700_core.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dib0700_core.c

## Purpose
Provides the common USB bridge implementation for DiBcom DiB0700-based DVB USB devices. It handles firmware download and startup, firmware version detection, vendor control reads/writes, legacy and new firmware I2C master protocols, GPIO/clock/I2C-speed configuration, MPEG-TS streaming enable/disable, RC protocol and bulk/interrupt URB handling, USB probe/disconnect, and module registration.

## Important APIs, Types, And Functions
The exported bridge helpers are `dib0700_get_version()`, `dib0700_ctrl_rd()`, `dib0700_set_gpio()`, `dib0700_ctrl_clock()`, `dib0700_set_i2c_speed()`, `dib0700_download_firmware()`, `dib0700_streaming_ctrl()`, `dib0700_change_protocol()`, `dib0700_rc_setup()`, `dib0700_identify_state()`, and `dib0700_i2c_algo`.

Important internal functions include `dib0700_ctrl_wr()` for vendor writes, `dib0700_set_usb_xfer_len()` for firmware 1.20.1+ transfer sizing, `dib0700_i2c_xfer_new()` and `dib0700_i2c_xfer_legacy()` for firmware-specific I2C transactions, `dib0700_set_clock()`, `dib0700_jumpram()` for firmware start, `dib0700_rc_urb_completion()` for RC packet decoding/resubmission, `dib0700_probe()`, and `dib0700_disconnect()`. The module exposes debug and `nb_packet_buffer_size` parameters plus adapter numbering.

## Control Flow
Cold detection in `dib0700_identify_state()` sends `REQUEST_GET_VERSION`; a failed or empty response means cold firmware state. Firmware download parses Intel HEX records using `dvb_usb_get_hexline()`, writes each record over bulk endpoint 1, jumps to RAM address `0x70000000`, sleeps for firmware startup, queries the firmware version, and updates every DiB0700 property table's bulk buffer size based on the requested number of TS packets and firmware constraints.

Probe loops over `dib0700_devices[]` and calls `dvb_usb_device_init()` until a property table claims the interface. It then reads and stores firmware version, copies the TS packet buffer module parameter into private state, selects bulk RC mode for firmware 1.20+, starts RC setup, and returns success. Disconnect unregisters optional tuner/demod I2C clients, drops module references, and exits the DVB USB device.

I2C transfer control branches on `st->fw_use_new_i2c_api`. The new API serializes through `i2c_mutex`, emits individual start/stop flags per message, supports read messages without a preceding write, and uses `REQUEST_NEW_I2C_READ/WRITE`. The legacy API locks both I2C and USB mutexes, supports write-only and write-then-read patterns via `REQUEST_I2C_WRITE/READ`, and returns the number of consumed messages or an error.

Streaming control optionally programs USB transfer length on firmware 1.20.1+, builds `REQUEST_ENABLE_VIDEO`, computes adapter number from endpoint 2/3 or adapter ID fallback, updates `channel_state`, ORs it into the command payload, and sends the vendor write under `usb_mutex`.

RC setup uses firmware version to decide whether bulk/interrupt URB mode is available. `dib0700_rc_setup()` allocates one URB and a six-byte buffer on endpoint 1, accepting either bulk or interrupt IN endpoints. Completion validates packet length, decodes NEC, NECX, NEC32, RC5, and repeat packets depending on selected protocol, reports events through rc-core, clears the buffer, and resubmits the URB.

## State And Persistence
Private state is `struct dib0700_state` from `dib0700.h`. `fw_version`, `fw_use_new_i2c_api`, `nb_packet_buffer_size`, `disable_streaming_master_mode`, and `channel_state` directly influence control paths. The shared `st->buf` command buffer is protected by USB and/or I2C mutexes in most paths. RC state is split between `d->props.rc.core.protocol`, the rc-core device, and the live URB. No data is persisted beyond the running kernel driver, though firmware bytes are loaded from the kernel firmware mechanism.

## Dependencies And Integration Points
This file depends on the DVB USB framework for property tables, firmware parsing, logging, adapter setup, and device exit. It integrates with USB control and bulk APIs, Linux I2C algorithm registration, rc-core scancode helpers, firmware loader declarations via `MODULE_FIRMWARE("dvb-usb-dib0700-1.20.fw")`, and board-specific `dib0700_devices[]`/`dib0700_usb_id_table[]` definitions.

## Risks
`dib0700_get_version()` copies 16 bytes from `st->buf` after `usb_control_msg()` without checking that exactly 16 bytes were returned, so short successful transfers would produce stale/partial version fields. The new I2C read path performs the USB read before checking whether `msg[i].len` fits in `st->buf`; a too-large length asks USB to write past the command buffer, making caller-side I2C length validation important. RC completion resubmits without checking `usb_submit_urb()` return status. Firmware download mutates global device property buffer sizes after firmware version detection, which affects later allocation and should be considered shared module state. Disconnect assumes I2C clients' driver owners are valid when unregistering.

## Test Signals
Useful signals are cold/warm detection for devices with and without firmware, successful firmware load and version print, I2C transfers against demod/tuner chips on both legacy and new firmware, buffer-size behavior when `nb_packet_buffer_size` is varied, TS streaming on/off for endpoint 2 and 3 devices without disrupting the other adapter's `channel_state`, RC key reporting for NEC/RC5/RC6-MCE-capable firmware, and clean disconnect with tuner/demod I2C client cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dib0700_core.c -->
