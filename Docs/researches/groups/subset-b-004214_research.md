# subset-b-004214 research

Grouped research report for the requested GSPCA USB webcam driver files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/spca561.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/spca561.c

Purpose: implements the Sunplus SPCA561 GSPCA subdriver for several SPCA561 revision 012a and 072a webcams. It exposes Bayer/SPCA561 video modes, revision-specific bridge and sensor initialization, V4L2 image controls, input snapshot-button events, packet parsing, and 072a autogain.

Important APIs and functions: module entry is `module_usb_driver(sd_driver)`, with USB IDs dispatching through `sd_probe` to either `sd_desc_12a` or `sd_desc_72a`. Core hooks are `sd_config`, `sd_init_12a`, `sd_init_72a`, `sd_start_12a`, `sd_start_72a`, `sd_stopN`, `sd_pkt_scan`, `do_autogain`, and revision-specific control initialization. Low-level helpers include `reg_w_val`, `reg_r`, `reg_w_buf`, `i2c_write`, `i2c_read`, `sensor_mapwrite`, and `write_sensor_72a`. Controls include hue, brightness, exposure, gain, contrast, and autogain depending on chip revision.

Control flow: probe reads vendor/product registers to verify communication, marks full-bandwidth needs, selects a mode table by `id->driver_info`, and initializes defaults. The 012a path writes PB100-style maps and starts compression only for 320x240 and above; the 072a path resets the bridge, writes bridge tables, programs sensor I2C tables, sets clock by mode, applies hue/contrast/autogain, and enables streaming. `sd_pkt_scan` treats packet sequence 0 as frame start, emits input `KEY_CAMERA` when the header snapshot bit is set, skips raw Bayer headers, and forwards compressed/raw payloads to GSPCA. `do_autogain` periodically reads color averages on 072a, estimates luma, adjusts sensor gain and exposure, and writes the results over the bridge I2C path.

State and persistence: `struct sd` embeds `gspca_dev`, stores control pointers, 012a exposure byte, chip revision, and an autogain countdown. State is volatile per open device; hardware registers and sensor values are reprogrammed on init/start/resume. No persistent storage is used.

Dependencies and integration points: depends on `gspca.h`, Linux USB control transfers, V4L2 controls, optional input support, GSPCA frame assembly, and SPCA561 private pixel format support. It integrates through `struct sd_desc` callbacks and the GSPCA USB probe/disconnect/PM helpers.

Risks: register scripts are mostly reverse-engineered magic constants and differ by revision. `i2c_write` times out silently without setting `usb_err`, so later code may continue after failed sensor writes. Autogain is only implemented for 072a and depends on fragile average registers. Packet parsing assumes minimum header lengths and manually skips headers; malformed short packets can discard frames. Controls no-op while not streaming, so values may not be applied until start paths explicitly reapply them.

Test signals: build with `CONFIG_USB_GSPCA_SPCA561`, probe all listed USB IDs, verify both 012a and 072a mode tables, stream raw and compressed modes, exercise brightness/hue/exposure/gain/autogain controls, check snapshot-button input events, suspend/resume, and validate frame integrity across short or empty packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/spca561.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/sq905.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/sq905.c

Purpose: implements a GSPCA subdriver for SQ905 still/video cameras that stream raw Bayer frames over bulk endpoint 0x81 using synchronous USB reads from a private workqueue.

Important APIs and functions: driver hooks are `sd_config`, `sd_init`, `sd_start`, and `sd_stop0`; there is no packet-scan hook because `sq905_dostream` directly reads and submits frames. USB helpers are `sq905_command`, `sq905_ack_frame`, and `sq905_read_data`. The mode table offers 160x120, 320x240, and conditional 640x480 `V4L2_PIX_FMT_SBGGR8` modes.

Control flow: `sd_config` marks the device as bulk and initializes the work item. `sd_init` sends clear, reads the big-endian model ID, clears again, chooses whether the high-resolution mode is available, and sets static flip flags based on ID bits. `sd_start` sends the capture command matching current mode, creates a single-thread workqueue, and queues `sq905_dostream`. The worker allocates a 32 KiB transfer buffer, reads a fixed-size frame consisting of a 64-byte header plus image data, strips the first header, emits GSPCA packet types, acknowledges each frame, and clears the camera on exit. `sd_stop0` drops `usb_lock`, destroys the workqueue, and reacquires the lock.

State and persistence: `struct sd` contains the work item and workqueue pointer. The camera mode/orientation discovered at init lives in `gspca_dev->cam`; frame state is local to the worker. No persistent configuration exists.

Dependencies and integration points: depends on `gspca.h`, workqueues, slab allocation, synchronous USB control and bulk messages, and GSPCA bulk-mode plumbing. It integrates with GSPCA through a minimal `sd_desc` because the worker performs its own frame acquisition.

Risks: synchronous streaming must finish an entire frame even after streamoff to keep the camera aligned, making stop latency dependent on USB reads. Workqueue teardown intentionally releases `usb_lock`, so races with disconnect/present checks are important. Bulk short reads are fatal. Header content is mostly ignored, and no controls exist for recovery or tuning. The 640x480 capability and orientation logic are reverse-engineered from ID bits.

Test signals: probe USB ID `2770:9120`, verify ID parsing with and without high-resolution capability, stream each available size, stop while a frame is in progress, disconnect during streaming, suspend/resume, and confirm Bayer orientation flags match real output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/sq905.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/sq905c.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/sq905c.c

Purpose: implements the SQ905C GSPCA driver for cameras that stream `V4L2_PIX_FMT_SQ905C` frames over a bulk endpoint, using a workqueue to issue synchronous reads.

Important APIs and functions: hooks are `sd_config`, `sd_init`, `sd_start`, and `sd_stop0`. USB helpers are `sq905c_command` and `sq905c_read`; streaming is handled by `sq905c_dostream`. USB IDs cover `2770:905c`, `9050`, `9051`, `9052`, and `913d`.

Control flow: probe-time config reads a version string with `SQ905C_GET_ID`, logs identifying bytes, chooses one or two modes depending on the version buffer, marks the camera as bulk, and initializes the worker. Init clears the camera. Start chooses medium or high capture command by requested width, stores the selected capability mode pointer, creates a workqueue, and queues the worker. The worker reads an 0x50-byte header, extracts payload length from bytes 0x40-0x43 in little-endian order, keeps the header as the first packet, then reads frame payload in chunks up to 0x8000 bytes and emits inter/last packets. On failure or exit, it sends `SQ905C_CLEAR`.

State and persistence: `struct sd` stores selected capture mode and workqueue state. Runtime state is volatile and rebuilt on each start; no configuration is persisted across opens or resumes.

Dependencies and integration points: depends on GSPCA bulk mode, Linux workqueues/slab, synchronous USB control and bulk transfers, and the SQ905C userspace pixel decoder for the private pixel format.

Risks: header length and size offsets are trusted after only a minimum header-length check, so corrupt size fields can stall or over-read until timeout. The worker shares the same lock-release teardown pattern as `sq905.c`. The comment for `SQ905C_CAPTURE_HI` says 320x240 despite being used for 640x480, reflecting reverse-engineering uncertainty. Control support is absent, and low-resolution capture is intentionally unsupported.

Test signals: build and probe all listed IDs, verify one-mode versus two-mode detection, stream 320x240 and 640x480, test stop/disconnect during long bulk reads, validate frame headers consumed by userspace, and exercise resume after `SQ905C_CLEAR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/sq905c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/sq930x.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/sq930x.c

Purpose: implements SQ930x webcam support for multiple sensor variants, exposing raw Bayer VGA/QVGA modes, sensor/bridge startup scripts, GPIO power/reset handling, exposure/gain controls, and bulk frame delivery.

Important APIs and functions: GSPCA hooks include `sd_config`, `sd_init`, `sd_isoc_init`, `sd_start`, `sd_stopN`, `sd_pkt_scan`, `sd_dq_callback`, and `sd_init_controls`. Hardware helpers include `reg_r`, `reg_w`, `reg_wb`, `i2c_write`, `ucbus_write`, `gpio_set`, `gpio_init`, `bridge_init`, `cmos_probe`, `global_init`, `send_start`, `send_stop`, and `setexposure`. Static tables describe sensor GPIO sequences, UCBUS writes, I2C writes, and capture payload configs.

Control flow: config decodes sensor/type from `driver_info`, installs two Bayer modes, and marks bulk transport. Init reads device info, initializes power GPIO, optionally probes CMOS sensors when an MI0360-like ID may really be a different sensor, rejects untreated OV sensors, and runs first-time global sensor init. Start repeats bridge/global init, then runs sensor-specific scripts for ICX098BQ, LZ24BP, MI0360, or MT9V111, sometimes doing a dummy start/stop cycle before the real capture start. Bulk setup forces one URB sized to frame plus 8 bytes. Packet scan wraps each bulk frame as a complete GSPCA frame and can temporarily stop URB submission so `sd_dq_callback` can program exposure/gain between frames.

State and persistence: `struct sd` stores control pointers, pending-control flag, cached two-bank GPIO values, sensor enum, and subtype. All state is runtime-only; hardware is reprogrammed on init/start and capture is stopped on stop.

Dependencies and integration points: depends on GSPCA bulk streaming, V4L2 control clustering, Linux USB control transfers, and raw Bayer formats. USB IDs encode initial sensor assumptions and Creative Live Motion subtype behavior.

Risks: most configuration is opaque reverse-engineered data. `ucbus_write` has a buffer-size guard, but the many script lengths and batch sizes must remain correct. Some sensors are probed but explicitly unsupported. Exposure updates manipulate `bulk_nurbs` and resubmit URBs manually, which is sensitive to GSPCA internals. There are deliberate long sleeps to avoid camera crashes. GPIO cache uses inverted writes, so mask mistakes can power-cycle or hold reset lines unexpectedly.

Test signals: build `CONFIG_USB_GSPCA_SQ930X`, probe each ID, verify sensor detection logs, stream both modes on each supported sensor, test exposure/gain changes during streaming, observe URB resubmission after dequeue callbacks, and validate stop/start cycles with LEDs/GPIO behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/sq930x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stk014.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stk014.c

Purpose: implements the Syntek DV4000/STK014 GSPCA driver, producing JPEG frames by adding a software JPEG header around camera payloads and exposing basic image controls.

Important APIs and functions: hooks are `sd_config`, `sd_init`, `sd_start`, `sd_stopN`, `sd_pkt_scan`, `sd_s_ctrl`, and `sd_init_controls`. USB helpers are `reg_r`, `reg_w`, `rcv_val`, `snd_val`, and `set_par`; control helpers set brightness, contrast, saturation, and power-line frequency.

Control flow: config installs 320x240 and 640x480 JPEG modes. Init switches to alternate setting 1 and verifies register `0x0740` returns `0xff`. Start creates a JPEG 4:1:1 header with quality 50, sends a sequence of parameter writes to select size and initialize color/gamma values, switches to the active alternate setting, clears bulk-like bridge status registers, and starts video flow. Stop sends stop parameters, returns to interface alt 1, clears status registers, and logs stop. Packet scan detects a frame header beginning `ff fe`, closes the previous JPEG with `ff d9`, emits the software JPEG header as `FIRST_PACKET`, skips the STK header, and appends payload as inter packets.

State and persistence: `struct sd` only adds a cached JPEG header. Control state is managed by V4L2 and applied only while streaming. Hardware state is volatile and reinitialized on start/resume.

Dependencies and integration points: depends on `gspca.h`, `jpeg.h`, V4L2 controls, and USB vendor control plus bulk endpoint operations. It integrates as USB ID `05e1:0893`.

Risks: command/register meanings are mostly magic constants. JPEG correctness depends on detecting headers and manually appending EOI markers because camera data lacks a complete standard JPEG wrapper. The code assumes enough bytes for `data[0]` and `data[1]` in packet scan. `rcv_val`/`snd_val` use hard-coded endpoints and address sequencing, including special handling for `0x003f08`.

Test signals: probe `05e1:0893`, stream both JPEG sizes, validate generated JPEGs with strict decoders, exercise brightness/contrast/saturation/frequency controls during streaming, and verify stop/start after USB altsetting changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stk014.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stk1135.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stk1135.c

Purpose: implements the Syntek STK1135 GSPCA driver for an MT9M112-based ASUS laptop camera, including variable-size Bayer capture, serial sensor access, flip-sensor debounce, and hflip/vflip controls.

Important APIs and functions: hooks are `sd_config`, `sd_init`, `sd_start`, `sd_stopN`, `sd_pkt_scan`, `stk1135_dq_callback`, `sd_init_controls`, `stk1135_try_fmt`, and `stk1135_enum_framesizes`. Register helpers include `reg_r`, `reg_w`, `reg_w_mask`, serial bus helpers, `sensor_read/write`, `sensor_set_page`, `sensor_write_mask`, `stk1135_configure_mt9m112`, `stk1135_configure_clock`, and `stk1135_camera_disable`.

Control flow: config exposes a default 640x480 SBGGR8 mode but supplies stepwise 32..1280 by 32..1024 formatting. Init configures GPIOs, interrupts, remote wakeup, serial interface, sensor clock, reads the sensor ID, and powers the camera down. Start re-enables GPIO power, configures clock and capture start/end positions from current format, programs 8-bit capture, writes a long MT9M112 configuration including AWB/AE/color/gamma/lens shading/PLL/windowing, enables capture, and resets packet sequence. Packet scan parses `struct stk1135_pkt_header`, debounces GPIO8 flip state, validates 6-bit packet sequence except on frame starts, closes prior frame on frame-start packets, skips the correct header size, and appends payload.

State and persistence: `struct sd` tracks packet sequence, current sensor page, flip status/debounce counter, and flip controls. Sensor page caching avoids redundant page writes. State is per-device and volatile; no persistent settings are saved.

Dependencies and integration points: depends on `stk1135.h` register definitions, GSPCA frame/control/format hooks, USB vendor transfers, V4L2 controls, little-endian header decoding, and the MT9M112 sensor programming sequence.

Risks: `stk1135_serial_wait_ready` returns `-1` rather than a specific errno and does not always update `usb_err`. Only MT9M112 is recognized; unknown sensor IDs are logged but initialization still proceeds to disable the camera. Packet loss causes frame discard and sequence resync. Flip debounce threshold is frame-callback based, so behavior depends on frame rate. Variable format support relies on sensor settings accepting broad dimensions.

Test signals: probe `174f:6a31`, enumerate stepwise sizes, stream minimum/maximum/even rounded sizes, verify packet sequence handling under dropped packets, test GPIO flip-sensor behavior and hflip/vflip controls, and validate suspend/resume sensor reprogramming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stk1135.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stk1135.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stk1135.h

Purpose: defines STK1135 bridge register offsets and the packet-header layout shared by `stk1135.c`.

Important APIs and types: exported definitions include GPIO/interrupt/remote-wakeup/power strap registers, sensor clock and PLL registers, capture window registers, serial bus access registers, timing generator registers, `struct stk1135_pkt_header`, frame-start/odd/I2C-vblank flag bits, and `STK1135_HDR_SEQ_MASK`.

Control flow: `stk1135.c` uses these constants to configure GPIO, serial sensor access, timing, capture window positions, and packet parsing. The packed header maps the first four bytes of each isochronous packet into flags, sequence, and GPIO status.

State and persistence: the header has no runtime state. It documents hardware register addresses and packet-bit contracts used by the driver.

Dependencies and integration points: relies on Linux fixed-width types and `__packed` conventions available through including kernel headers. It is private to the STK1135 GSPCA driver.

Risks: no include guard is present, so repeated inclusion would redefine the struct and macros. Register offsets are untyped macros, making accidental use with wrong register width easy. Packet header interpretation must remain byte-for-byte compatible with device firmware.

Test signals: compile coverage through `stk1135.c`, packet capture inspection matching header fields, and register access tests that confirm the constants still map to expected hardware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stk1135.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv0680.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv0680.c

Purpose: implements a GSPCA driver for STV0680 cameras, translating vendor control commands into a single bulk frame mode and restoring the camera's original video mode on close.

Important APIs and functions: hooks are `sd_config`, `sd_init`, `sd_start`, `sd_stopN`, `sd_stop0`, and `sd_pkt_scan`. USB helpers include `stv_sndctrl`, `stv0680_handle_error`, `stv0680_get_video_mode`, and `stv0680_set_video_mode`.

Control flow: config waits one second for hotplug settle, pings the camera, reads descriptors and capability bytes, selects CIF or QVGA, saves the original mode, temporarily programs the selected video mode to read frame size details, sets one bulk URB of the device-reported frame size, then restores the original mode. Start switches to the chosen mode, refreshes status, and sends the stream command. Stop sends a high-priority stop command; `stop0` restores the original mode if the device is still present. Packet scan accepts only full-size frame packets, discards prior frames when strange 16-byte packets appear, and completes a frame only when the next valid packet arrives.

State and persistence: `struct sd` stores the derived single `v4l2_pix_format`, original/current/video mode bytes, and no controls. The driver intentionally restores device mode state on final stop but otherwise keeps no persistent state.

Dependencies and integration points: depends on GSPCA bulk mode, STV0680 vendor commands, USB descriptor reads, and private `V4L2_PIX_FMT_STV0680` decoding.

Risks: protocol commands use magic request/set values and require exact transfer sizes. Unsupported mode combinations fail probe. The full-frame packet assumption means any short packet discards data. `sd_pkt_scan` delays `LAST_PACKET` until a following packet to catch corruption, which can look unusual to frame timing tests. Hotplug requires a full second sleep.

Test signals: probe IDs `0553:0202` and `041e:4007`, validate descriptor/capability parsing, stream CIF or QVGA depending on hardware support, inject short packets, stop and confirm original camera mode restoration, and test suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv0680.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/Kconfig

Purpose: defines the `USB_STV06XX` kernel configuration option for ST STV06XX-based GSPCA cameras.

Important APIs and symbols: declares `config USB_STV06XX` as a tristate depending on `USB_GSPCA`; help text names the resulting module `gspca_stv06xx`.

Control flow: selecting this symbol enables the Makefile rule that builds the composite STV06xx module from bridge core and sensor backend objects.

State and persistence: no runtime state; the selected tristate persists in the kernel build configuration.

Dependencies and integration points: integrates with the GSPCA USB media Kconfig tree and requires the GSPCA core to be available.

Risks: help text only mentions STV06XX generically, while the implementation covers several bridge/sensor combinations including ST6422-like hardware. Missing dependencies would surface as compile/link failures in the module.

Test signals: menuconfig visibility, `allyesconfig`/`allmodconfig` build coverage, and ensuring `CONFIG_USB_STV06XX=m` produces `gspca_stv06xx.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/Makefile

Purpose: maps `CONFIG_USB_STV06XX` to the composite `gspca_stv06xx` module and lists its bridge and sensor backend objects.

Important APIs and entries: `obj-$(CONFIG_USB_STV06XX) += gspca_stv06xx.o`; `gspca_stv06xx-objs` includes `stv06xx.o`, `stv06xx_vv6410.o`, `stv06xx_hdcs.o`, `stv06xx_pb0100.o`, and `stv06xx_st6422.o`; `ccflags-y` adds the parent GSPCA include path.

Control flow: kbuild compiles separate backend objects and links them into one module, letting the bridge core probe and dispatch among statically linked sensor descriptors.

State and persistence: no runtime state. It defines build composition only.

Dependencies and integration points: depends on Kconfig symbol `USB_STV06XX`, local headers under `stv06xx/`, and parent `drivers/media/usb/gspca` headers.

Risks: adding or removing a backend requires updating this list. The headers define some `const struct stv06xx_sensor` objects, so the single composite module include pattern matters for avoiding duplicate definitions.

Test signals: module build with `CONFIG_USB_STV06XX=y/m`, link checks for all sensor descriptor references, and include-path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx.c

Purpose: implements the common STV06xx GSPCA bridge driver that probes sensor backends, provides bridge/sensor I2C helpers, starts/stops isochronous streaming, parses chunked USB packets, and handles optional camera-button input.

Important APIs and functions: exported-in-module helpers are `stv06xx_write_bridge`, `stv06xx_read_bridge`, `stv06xx_write_sensor`, `stv06xx_write_sensor_bytes`, `stv06xx_write_sensor_words`, and `stv06xx_read_sensor`. GSPCA hooks include `stv06xx_config`, `stv06xx_init`, `stv06xx_init_controls`, `stv06xx_start`, `stv06xx_stopN`, `stv06xx_pkt_scan`, `stv06xx_isoc_init`, `stv06xx_isoc_nego`, `sd_int_pkt_scan`, `stv06xx_probe_error`, and custom disconnect cleanup.

Control flow: config records bridge type from USB `driver_info`, optionally dumps bridge registers, and probes sensors in order: ST6422, VV6410, HDCS1x00, HDCS1020, PB0100. Init delays for USB settle and delegates to the selected sensor. Control init delegates to the sensor. Start finds the selected altsetting endpoint size, writes it to bridge registers, starts the sensor, and enables ISO streaming. Iso negotiation reduces packet size by 100 down to the sensor minimum and retries altsetting selection. Packet scan walks chunked packets with id/length headers, maps SOF/EOF/data chunks to GSPCA packets, skips first corrupt ST6422 lines, and discards malformed chunks.

State and persistence: `struct sd` in `stv06xx.h` stores selected sensor, sensor-private pointer, ST6422 skip counter, and bridge type. Sensor-private memory is freed on probe error and disconnect. All state is volatile per device.

Dependencies and integration points: depends on GSPCA, USB vendor control transfers, optional input support, `stv06xx_sensor.h`, and all sensor backend descriptors linked into the module. USB IDs identify STV600, STV610, STV602, and ST6422 bridge variants.

Risks: sensor probing relies on ordered fallbacks and shared `sensor_priv` ownership. I2C command batching depends on fixed buffer layout and sensor `i2c_len`. Packet parsing trusts chunk length after bounds checks but unknown chunks are skipped silently. Iso negotiation mutates endpoint descriptor packet size in the active config cache. Debug dump mode writes test values to bridge registers and restores them, which is risky on hardware.

Test signals: build `gspca_stv06xx`, probe each USB ID/bridge generation, verify sensor detection order, stream each backend, exercise bandwidth fallback, test input interrupt packets, malformed chunk handling, suspend/resume, and disconnect memory cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx.h

Purpose: defines the common STV06xx bridge register map, I2C command-buffer constants, LED constants, bridge enum values, shared `struct sd`, and helper prototypes used by all STV06xx sensor backends.

Important APIs and types: `struct sd` embeds `gspca_dev`, selected `struct stv06xx_sensor`, backend `sensor_priv`, `to_skip`, and bridge type. Macros define ISO, I2C, scan-rate, LED, reset, and axis-control registers plus bridge IDs `BRIDGE_STV600`, `BRIDGE_STV602`, `BRIDGE_STV610`, and `BRIDGE_ST6422`. Prototypes expose bridge and sensor read/write helpers.

Control flow: sensor backends include this header through `stv06xx_sensor.h` and use the helper prototypes to program bridge and sensor registers. The core uses the bridge enum to select protocol quirks and packet skipping.

State and persistence: declares runtime state layout but performs no allocation itself. Values are per-device and freed by `stv06xx.c`.

Dependencies and integration points: depends on `gspca.h`, Linux slab header, and the STV06xx backend contract. It is the central ABI between bridge core and sensor files inside the module.

Risks: `MODULE_NAME` is uppercase `"STV06xx"` while the built module is `gspca_stv06xx`, which can confuse log filtering. Shared `struct sd` changes affect every backend. Fixed I2C buffer sizes limit batching assumptions.

Test signals: compile all backends, validate bridge register constants against USB traces, and run streaming tests for each bridge enum path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_hdcs.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_hdcs.c

Purpose: implements HDCS-1000/1100 and HDCS-1020 sensor backends for STV06xx bridges, including probe, mode selection, power state transitions, window programming, exposure/gain controls, and register dumps.

Important APIs and functions: sensor operations are `hdcs_probe_1x00`, `hdcs_probe_1020`, `hdcs_init`, `hdcs_start`, `hdcs_stop`, `hdcs_init_controls`, and `hdcs_dump`. Internal helpers include `hdcs_reg_write_seq`, `hdcs_set_state`, `hdcs_reset`, `hdcs_set_exposure`, `hdcs_set_gains`, `hdcs_set_gain`, and `hdcs_set_size`.

Control flow: probe reads `HDCS_IDENT`, selects mode table and sensor-private geometry/timing parameters, and stores `struct hdcs` in `sensor_priv`. Init optionally enables STV0600 emulation on STV602, writes bridge init registers, resets the sensor, writes common sensor init registers, enables continuous capture config, programs ADC/PGA timing, and centers the default window. Start transitions the sensor to RUN; stop transitions to SLEEP. Exposure control converts user exposure into row and sub-row exposure using sensor timing constants, stops streaming, writes exposure registers, clears error flags, and restarts streaming.

State and persistence: `struct hdcs` tracks power state, active width/height, visible array geometry, exposure timing constants, and sample period. This private state is volatile and freed by the STV06xx core cleanup paths.

Dependencies and integration points: depends on STV06xx shared I2C helpers, `stv06xx_hdcs.h` register constants and descriptor objects, V4L2 exposure/gain controls, and bridge-specific quirks.

Risks: comments note no locking around private state. Exposure math is integer-heavy and sensor-specific; invalid timing assumptions can produce bad sub-row values. Probe allocates private state only after ID match; cleanup must free it. Packet-size values in the descriptors are fixed with FIXME comments about bandwidth testing.

Test signals: probe both HDCS ID values, stream HDCS1x00 and HDCS1020 hardware, vary exposure/gain while streaming, verify centered crop and dimensions, test STV602 emulation, and enable `dump_sensor` for register-read diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_hdcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_hdcs.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_hdcs.h

Purpose: defines HDCS sensor register constants, defaults, static init tables, function prototypes, and the two STV06xx sensor descriptors for HDCS-1000/1100 and HDCS-1020.

Important APIs and types: key macros include HDCS register selectors, `HDCS_REG_CONFIG`, `HDCS_REG_CONTROL`, default dimensions, clock/exposure constants, run/sleep bits, and default exposure/gain. It defines `stv06xx_sensor_hdcs1x00` and `stv06xx_sensor_hdcs1020` with I2C address, byte length, packet sizes, and operation callbacks.

Control flow: `stv06xx.c` references the descriptor symbols during sensor probing. `stv06xx_hdcs.c` consumes the register definitions and init arrays to reset, configure, start, stop, and dump sensors.

State and persistence: no runtime state is allocated here; descriptor objects and init arrays are static module data.

Dependencies and integration points: depends on `stv06xx_sensor.h` and the shared `IS_1020(sd)` macro. The descriptor objects are defined in the header as part of the local single-inclusion backend pattern.

Risks: defining `const` objects in a header would cause duplicate definitions if included from multiple translation units. Fixed packet-size descriptors have FIXME comments about bandwidth and framerate testing. Register addresses are left-shifted because low bit encodes read/write, which is easy to misuse.

Test signals: compile/link of the composite module, probe ID-specific descriptors, verify packet size negotiation, and compare sensor register dump output with expected HDCS datasheets/traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_hdcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_pb0100.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_pb0100.c

Purpose: implements the Photobit PB-0100 sensor backend for STV06xx bridges, including mode windows, start/stop, auto/manual gain and exposure controls, red/blue balance, and autogain target programming.

Important APIs and functions: sensor callbacks are `pb0100_probe`, `pb0100_init`, `pb0100_start`, `pb0100_stop`, `pb0100_init_controls`, and `pb0100_dump`. Control helpers include `pb0100_set_gain`, `pb0100_set_red_balance`, `pb0100_set_blue_balance`, `pb0100_set_exposure`, `pb0100_set_autogain`, and `pb0100_set_autogain_target`.

Control flow: probe reads `PB_IDENT`, checks the high byte for `0x64`, and installs 320x240 cropped or 352x288 modes. Control init allocates `struct pb0100_ctrls`, builds an autogain cluster containing gain/exposure/red/blue/natural-light controls plus a target control, and stores it in `sensor_priv`. Init resets and programs bridge/sensor registers for gain, auto-exposure limits, black level, row timing, and bridge scan registers. Start inspects negotiated endpoint packet size to choose row speed, programs crop/window registers by mode, sets STV bridge X/Y/scan controls, and enables streaming. Stop aborts frame and clears the run bit.

State and persistence: `sensor_priv` holds V4L2 control pointers for the PB0100 cluster. Hardware values are volatile and re-applied on init/start or when controls change.

Dependencies and integration points: depends on STV06xx I2C/bridge helpers, `stv06xx_pb0100.h` register definitions and descriptor, V4L2 auto clusters, and GSPCA current format state for autogain target pixel calculations.

Risks: init explicitly lacks full error handling per comments, so failed writes can be ignored. Control IDs include custom user-class offsets, and the names appear swapped in dispatch: ID `+0x1001` triggers autogain target although the config labels `+0x1000` as target. Private control allocation must be freed by STV06xx cleanup. Subsample mode is flagged but disabled/commented as wrong.

Test signals: PB0100 probe, both modes, low-bandwidth packet-size fallback, autogain/manual cluster transitions, red/blue balance clamping, exposure/gain writes, and unload/reprobe leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_pb0100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_pb0100.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_pb0100.h

Purpose: declares PB-0100 sensor register constants, mode flag bits, local backend prototypes, control helper prototypes, and the `stv06xx_sensor_pb0100` descriptor.

Important APIs and types: macros cover chip ID, windowing, blanking, control, exposure, gain, DAC, thresholds, ADC, and chip-enable registers. Mode flags are `PB0100_CROP_TO_VGA` and `PB0100_SUBSAMPLE`. The descriptor sets I2C flush/address/word length, packet sizes, and callbacks.

Control flow: included by `stv06xx_pb0100.c`, this header supplies constants for all register writes and gives `stv06xx.c` access to the sensor descriptor via `stv06xx_sensor.h` extern declarations.

State and persistence: contains static descriptor data and compile-time constants only; runtime control state is allocated in the C file.

Dependencies and integration points: depends on `stv06xx_sensor.h` and the single composite module build pattern.

Risks: the descriptor object is defined in the header, so multiple inclusion outside the current pattern would duplicate symbols. Many registers are reserved or lightly documented, making misuse easy. Packet-size arrays cover only the advertised modes.

Test signals: compile/link of the PB0100 backend, probe matching ID, check descriptor packet sizes during iso negotiation, and verify register writes from controls against expected PB0100 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_pb0100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_sensor.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_sensor.h

Purpose: defines the common sensor-backend interface used by the STV06xx bridge core and declares the linked sensor descriptor objects.

Important APIs and types: `struct stv06xx_sensor` contains sensor name, I2C address/flush/word length, per-mode min/max packet sizes, and callbacks for probe, init, controls, direct read/write hooks, start, stop, and dump. Extern descriptors include VV6410, HDCS1x00, HDCS1020, PB0100, and ST6422. `IS_1020(sd)` distinguishes the HDCS1020 descriptor.

Control flow: `stv06xx.c` iterates descriptor objects and calls their callbacks through this interface. Backends fill mode tables and private state during probe, then use callbacks for lifecycle and controls.

State and persistence: the header defines no mutable state itself. It describes static descriptors and callback contracts.

Dependencies and integration points: includes `stv06xx.h`, creating a circular-looking but guarded contract between shared device state and sensor descriptors.

Risks: callback semantics are convention-based; not all backends implement optional direct read/write hooks. Packet-size arrays have fixed length four and must match backend mode counts. `IS_1020` compares descriptor addresses, so duplicate descriptor definitions would break identity tests.

Test signals: compile all backends, verify each descriptor probe path, exercise core delegation for init/control/start/stop/dump, and check packet-size arrays against mode tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_sensor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_st6422.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_st6422.c

Purpose: implements support for the integrated ST6422 sensor/bridge variant inside the STV06xx module using direct bridge-register writes rather than external I2C.

Important APIs and functions: callbacks are `st6422_probe`, `st6422_init`, `st6422_init_controls`, `st6422_start`, and `st6422_stop`. Control dispatch `st6422_s_ctrl` writes brightness, contrast, gain, and exposure through `setbrightness`, `setcontrast`, `setgain`, and `setexposure`, then commits settings by writing `0x143f`.

Control flow: probe accepts only `BRIDGE_ST6422` and installs two SGRBG8 modes: 162x120 and 324x240 with extra skipped/ignored lines noted in comments. Init writes a table of bridge registers for disabled capture, brightness/contrast, RGB gain, exposure, timing, and commit. Start writes mode-dependent size register `0x1505` and commits. Stop only logs; common core disables ISO streaming. Packet-level first-line skipping is handled in `stv06xx_pkt_scan` through `sd->to_skip`.

State and persistence: no backend-private allocation is used. Control state is held by V4L2; hardware state is bridge register state reinitialized on probe/resume.

Dependencies and integration points: depends on `stv06xx_st6422.h`, STV06xx bridge helpers, V4L2 controls, and the core packet parser's ST6422 special cases.

Risks: register meanings are largely unknown comments. Stop does not explicitly power down sensor registers. The 324x240 mode reports `sizeimage` for 324x244 while logical height is 240, relying on userspace/GSPCA handling of ignored lines. No bandwidth reduction is known for this backend.

Test signals: probe ST6422 USB IDs, stream both modes, verify first four corrupt lines are skipped, change controls and confirm commit behavior, test stop/start, and inspect frame dimensions consumed by userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_st6422.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_st6422.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_st6422.h

Purpose: declares the ST6422 backend callbacks and defines the `stv06xx_sensor_st6422` descriptor for the integrated sensor variant.

Important APIs and types: prototypes include `st6422_probe`, `st6422_start`, `st6422_init`, `st6422_init_controls`, and `st6422_stop`. The descriptor names the sensor, supplies fixed min/max packet sizes `{300, 847}`, and assigns lifecycle callbacks.

Control flow: the STV06xx core tries this descriptor first; its probe succeeds only for `BRIDGE_ST6422`, avoiding I2C probing for integrated hardware.

State and persistence: no runtime state in the header; static descriptor data only.

Dependencies and integration points: depends on `stv06xx_sensor.h` and the composite-module single-definition pattern.

Risks: descriptor definition in a header is fragile if included by more than one translation unit. Packet-size comments say no known framerate lowering exists, so bandwidth fallback is limited.

Test signals: compile/link, ST6422 probe success/failure by bridge type, and iso negotiation using fixed packet sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_st6422.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_vv6410.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_vv6410.c

Purpose: implements the ST VV6410 sensor backend for STV06xx bridges, with one CIF-like raw Bayer mode, exposure/gain controls, optional disabled flip support, LED control, and sensor register dump.

Important APIs and functions: callbacks are `vv6410_probe`, `vv6410_init`, `vv6410_init_controls`, `vv6410_start`, `vv6410_stop`, and `vv6410_dump`. Control helpers include `vv6410_set_hflip`, `vv6410_set_vflip`, `vv6410_set_analog_gain`, and `vv6410_set_exposure`.

Control flow: probe reads `VV6410_DEVICEH` and expects `0x19`, then installs a 356x292 SGRBG8 mode. Init writes bridge init entries and sensor init table. Start configures bridge crop/subsample scan registers by mode flags, turns on LED, clears low-power mode via `VV6410_SETUP0`, and leaves streaming enabled by the common core. Stop turns LED off and sets low-power mode. Exposure maps a nonlinear user value to fine and coarse exposure registers using line length; gain writes low 4 bits into `VV6410_ANALOGGAIN`.

State and persistence: no backend-private allocation. Runtime state is V4L2 control values and hardware register state, reloaded on init/start.

Dependencies and integration points: depends on STV06xx bridge/sensor helpers, `stv06xx_vv6410.h` constants and descriptor, V4L2 controls, and core ISO streaming.

Risks: hflip/vflip controls are commented out because offset renegotiation is unresolved, but helper code remains. Packet size is fixed at 1023 with FIXME comments. Exposure conversion clamps coarse exposure to 512 and may not map linearly to real brightness.

Test signals: probe VV6410 hardware, stream 356x292, verify LED on/off, adjust exposure/gain, run `dump_sensor`, and test stop/resume low-power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_vv6410.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_vv6410.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_vv6410.h

Purpose: defines VV6410 register constants, control bits, default exposure/gain values, backend prototypes, descriptor data, and bridge/sensor initialization tables.

Important APIs and types: macros cover identity, status, image end coordinates, setup, data format, exposure, clock, offset, timing, and analog registers. The descriptor `stv06xx_sensor_vv6410` sets I2C address `0x20`, byte-length accesses, packet size 1023, and lifecycle callbacks. Init tables define bridge resets and sensor low-power/setup writes.

Control flow: `stv06xx_vv6410.c` consumes these definitions to probe ID, initialize bridge/sensor registers, start/stop streaming, and apply controls. The core references the descriptor during ordered probing.

State and persistence: static constants and descriptor only; no mutable state.

Dependencies and integration points: depends on `stv06xx_sensor.h` and core STV06xx helper contracts.

Risks: descriptor definition in a header requires the current one-translation-unit inclusion pattern. Many mode flags are defined but only one active mode exists. Fixed packet-size values have FIXME comments.

Test signals: compile/link, sensor probe identity read, init-table USB traces, packet-size negotiation, and exposure/gain register writes on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_vv6410.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/sunplus.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/sunplus.c

Purpose: implements a broad Sunplus SPCA504/SPCA504B/SPCA504C/SPCA533/SPCA536 GSPCA JPEG driver with many USB IDs, subtype-specific initialization scripts, JPEG header synthesis, quantization tables, and basic image controls.

Important APIs and functions: hooks are `sd_config`, `sd_init`, `sd_start`, `sd_stopN`, `sd_pkt_scan`, `sd_s_ctrl`, and `sd_init_controls`. Helpers include `reg_r`, `reg_w_1`, `reg_w_riv`, `write_vector`, `setup_qtable`, acknowledged-command variants, SPCA504B polling/status helpers, `spca504B_SetSizeType`, `spca504_wait_status`, `spca504B_setQtable`, `init_ctl_reg`, and brightness/contrast/saturation setters.

Control flow: config decodes bridge/subtype from USB `driver_info`, probes Aiptek firmware to distinguish SPCA504A from SPCA504B, and selects mode tables. Init performs bridge-specific resets, firmware/status reads, open scripts, and JPEG quantization setup. Start creates a JPEG header, sets qtables/size/type, issues bridge/subtype-specific capture start sequences, initializes control registers, and leaves packet scan to wrap raw camera JPEG fragments. Stop sends bridge-specific stop/ack commands. Packet scan recognizes bridge-specific SOF/drop/header formats, injects EOI and a software JPEG header on SOF, skips per-bridge headers, and inserts `0x00` after in-stream `0xff` bytes for JPEG escaping.

State and persistence: `struct sd` stores autogain flag, bridge/subtype, and cached JPEG header. Hardware configuration is reissued at init/start. Autogain is a runtime flag applied to SPCA504C start logic.

Dependencies and integration points: depends on `gspca.h`, `jpeg.h`, V4L2 controls, GSPCA frame assembly, USB vendor transfers, and a large USB ID table covering many vendors.

Risks: high reverse-engineering density with many magic values and subtype exceptions. Packet scan mutates packet data when inserting JPEG escape bytes, which assumes the buffer is writable. Some discard paths intentionally do not mark `DISCARD_PACKET`. Control values are only written while streaming. The huge USB table increases risk of wrong bridge/subtype mapping.

Test signals: build Sunplus support, probe representative devices for each bridge, stream all advertised modes, validate JPEG output with strict decoders, exercise qtable setup, controls, autogain start behavior, stop/start loops, and Aiptek firmware fallback detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/sunplus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/t613.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/t613.c

Purpose: implements the T613 JPEG-compliant GSPCA driver for `17a1:0128` cameras with several possible sensors, many image controls, sensor-specific init tables, button input handling, and JPEG packet classification.

Important APIs and functions: hooks are `sd_config`, `sd_init`, `sd_start`, `sd_stopN`, `sd_pkt_scan`, `sd_g_volatile_ctrl`, `sd_s_ctrl`, and `sd_init_controls`. Low-level helpers include `reg_r`, `reg_w`, `reg_w_buf`, `reg_w_ixbuf`, `om6802_sensor_init`, `setbrightness`, `setcontrast`, `setcolors`, `setgamma`, `setawb_n_RGB`, `setsharpness`, `setfreq`, `setmirror`, `seteffect`, and `poll_sensor`.

Control flow: config exposes 160x120, 320x240, and 640x480 JPEG modes. Init reads sensor ID registers, maps them to OM6802/OTHER/TAS5130A/LT168G, performs OM6802 reset validation when needed, dumps selected debug registers, writes sensor-specific setup arrays, gamma/color/gain defaults, and stream templates. Start chooses a mode code, performs sensor-specific startup for OM6802 or TAS5130A, applies power-line frequency, writes stream registers twice, and optionally polls OM6802. Packet scan ignores control packets beginning `0x5a` while updating `KEY_CAMERA` state from byte 20, strips a two-byte packet prefix from image packets, and classifies packets by JPEG SOI/EOI markers. Stop rewrites stream toggles and releases any pressed input key.

State and persistence: `struct sd` stores frequency control pointer, AWB/gain/red/blue clustered control pointers, detected sensor enum, and button state. Sensor state is reprogrammed on init/start; no persistent storage is used.

Dependencies and integration points: depends on GSPCA, optional input support, V4L2 controls and auto white-balance clusters, slab allocation for large control buffers, and private sensor script tables.

Risks: register I/O helpers mostly ignore USB return values, so failures may be silent. Several modes are compiled out as broken. Some comments say gamma/effects/polling behavior is uncertain. Control packet parsing reads byte 20 only after a length guard but image packet parsing assumes at least two bytes and JPEG marker space. Sensor ID matching masks with `0xff0f`, which may conflate variants.

Test signals: probe `17a1:0128`, test each detected sensor variant if available, stream all enabled modes, validate JPEG SOI/EOI framing, exercise every V4L2 control including AWB volatile reads and color effects, press/release camera button, and run stop while the button is pressed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/t613.c -->
