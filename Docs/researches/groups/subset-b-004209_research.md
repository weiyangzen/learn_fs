# subset-b-004209 research

Grouped research for the requested GSPCA-related Linux USB camera files. Each section preserves the source path in its title and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/dtcs033.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/dtcs033.c

Purpose: `dtcs033.c` is a compact GSPCA subdriver for the Scopium DTCS033 astro camera (`0547:7303`). It exposes two 640x480 modes from the same bulk stream: `V4L2_PIX_FMT_GREY` for raw monochrome-looking Bayer bytes and `V4L2_PIX_FMT_SRGGB8` for consumers that want the Bayer pattern declared. The driver uses one bulk URB sized as `640 * 512`, then strips the first and last sixteen sensor lines to deliver a 640x480 frame.

Important APIs, types, and functions: `struct dtcs033_usb_requests` encodes vendor control requests used by `reg_reqs()`. `reg_rw()` sends a vendor control message through `usb_rcvctrlpipe()` even for request types that include `USB_DIR_OUT`; this follows the local source but is a point to inspect if control writes fail on hardware. `sd_config()` sets bulk transport fields in `struct cam`; `dtcs033_pkt_scan()` is the frame parser; `dtcs033_setexposure()` maps V4L2 exposure and gain controls into two vendor request writes; `dtcs033_init_controls()` creates an exposure/gain cluster.

Control flow: probe calls `gspca_dev_probe()`, which calls `sd_config()`, `sd_init()`, and control initialization. Stream start replays the large `dtcs033_start_reqs` table. Each full-size bulk packet is treated as a complete sensor readout: `FIRST_PACKET`, one `INTER_PACKET` with cropped data, then `LAST_PACKET`. Stream stop replays `dtcs033_stop_reqs`.

State and persistence: only V4L2 control values are retained in `struct sd`; the hardware state is rewritten on stream start and when controls change during streaming. `gspca_dev->usb_err` short-circuits subsequent control requests.

Dependencies and integration points: depends on `gspca.h`, V4L2 controls, USB bulk transfer setup in `gspca.c`, and the shared GSPCA frame assembly contract.

Risks: strict packet length checking discards any short transfer; all capture correctness depends on fixed 512-line bulk packets. Gain/exposure conversions use integer arithmetic and assume the UI ranges enforced by V4L2. The control helper does not validate returned byte counts. Test signals include successful probe, start request completion, stable 640x480 payload size, no `frame overflow`, and observable exposure/gain changes while streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/dtcs033.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/etoms.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/etoms.c

Purpose: `etoms.c` supports Etoms ET61x151 USB cameras with either PAS106 or TAS5130CXX sensors. It outputs Bayer `V4L2_PIX_FMT_SBGGR8` frames in SIF or VGA-class modes, configures bridge registers and sensor I2C windows, and includes simple automatic gain based on luma samples read after frames are dequeued.

Important APIs, types, and functions: `struct sd` extends `gspca_dev` with `sensor`, `autogain`, and an autogain countdown. `reg_r()`, `reg_w_val()`, and `reg_w()` wrap vendor control transfers to bridge registers. `i2c_w()` and `i2c_r()` program PAS106 sensor registers through ETOMS I2C staging registers. `Et_init1()` initializes PAS106 paths; `Et_init2()` initializes TAS5130CXX paths. `sd_pkt_scan()` parses isochronous packet headers and emits GSPCA frame packets. `do_autogain()` is wired as `dq_callback`.

Control flow: USB IDs choose the sensor through `driver_info`. Probe sets mode tables and initializes controls. `sd_init()` performs a full bridge/sensor setup and turns video off. `sd_start()` repeats setup, arms autogain, resets the bridge, and enables video. Packets with `seqframe == 0x3f` begin a new frame after closing the prior one; nonzero data packets append after an 8-byte header; zero-length logical payloads discard the frame.

State and persistence: most hardware state is volatile and replayed on init/start. User controls are not cached as V4L2 pointers, except autogain state in `sd->autogain`; brightness, contrast, and saturation writes go directly to bridge/sensor registers when streaming. Autogain persists a countdown and periodically adjusts PAS106 global gain.

Dependencies and integration points: integrates with the GSPCA V4L2 control path, frame assembly, and optional `dq_callback`. It depends on ETOMS-specific register semantics and PAS106 I2C register layouts.

Risks: many USB helpers ignore return values and do not set `usb_err`, so partial hardware failures can be silent. `sd_pkt_scan()` trusts `data[0]` and `data[1]`; the GSPCA core normally avoids zero-length packets, but malformed short packets would be hazardous. Autogain reads bridge luma registers without locking beyond the callback context. Test signals include stable frame boundaries, no discarded packets under normal light, working PAS106 saturation/gain controls, and luma-driven gain convergence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/etoms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/finepix.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/finepix.c

Purpose: `finepix.c` is a GSPCA subdriver for Fujifilm FinePix still cameras that expose a simple live JPEG capture mode over USB bulk transfers. It advertises one 320x240 JPEG capture format and reads frames synchronously from a workqueue instead of relying on URB completion callbacks.

Important APIs, types, and functions: `struct usb_fpix` adds a `work_struct` to `gspca_dev`. `command()` sends 12-byte class-interface control messages for reset and frame request. `dostream()` runs in process context and loops while the device is present and streaming. `sd_start()` initializes the device, drains the reset response, requests the first frame, clears halt, then schedules the worker. `sd_stop0()` releases `usb_lock` around `flush_work()` to avoid deadlock.

Control flow: `sd_config()` sets `cam->bulk = 1`, `bulk_size = 0x2000`, and initializes work. The GSPCA core creates a bulk URB, but because `cam.bulk_nurbs` remains zero, the core lets the subdriver drive bulk reads itself. The worker sends a frame request, then repeatedly calls `usb_bulk_msg()` until a short read or JPEG EOI marker marks end-of-frame. It uses `FIRST_PACKET` for the first chunk after the previous `LAST_PACKET`, `INTER_PACKET` for middle chunks, and `LAST_PACKET` for the terminal chunk. A fixed delay prevents camera disconnects caused by requesting frames too quickly.

State and persistence: no user controls are exposed. Runtime state is the scheduled work item plus `present`, `streaming`, and PM `frozen` checks inherited from GSPCA. No persistent hardware state is maintained across stream stops beyond the camera's own firmware behavior.

Dependencies and integration points: depends on GSPCA bulk mode, V4L2 JPEG format reporting, `usb_bulk_msg()`, `usb_control_msg()`, and the core stop path calling `stop0`.

Risks: synchronous worker streaming depends on careful lock release in `sd_stop0()`. JPEG completeness is best-effort; comments note incomplete JPEGs can occur. A timeout restarts the request loop, which may mask intermittent transport problems. Test signals include repeated stream on/off without workqueue hangs, valid JPEG EOI under normal capture, no disconnects with the 35 ms delay, and successful suspend/resume behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/finepix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/Kconfig

Purpose: this Kconfig fragment defines `CONFIG_USB_GL860`, the build-time switch for the Genesys Logic GL860 GSPCA camera driver.

Important APIs, types, and functions: it declares a `tristate` option named "GL860 USB Camera Driver" and depends on both `VIDEO_DEV` and `USB_GSPCA`. Its help text documents that the module name is `gspca_gl860`.

Control flow: there is no runtime control flow. In Kbuild configuration, selecting `Y` links the driver into the kernel image, `M` builds the module, and unset excludes the GL860 sources from compilation.

State and persistence: the option persists through the kernel `.config`. It gates compilation only; runtime state is held by `gl860.c` and sensor files.

Dependencies and integration points: integrates with the media USB GSPCA Kconfig hierarchy. The `USB_GSPCA` dependency is important because GL860 sources include and call the shared GSPCA core.

Risks: if dependencies are relaxed incorrectly, the module could compile without required V4L2/GSPCA symbols. Test signals are Kconfig visibility under the GSPCA menu, successful `M` builds producing `gspca_gl860.ko`, and absence of unresolved GSPCA/V4L2 symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/Makefile -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/Makefile

Purpose: this Makefile builds the GL860 subdriver module and composes it from the bridge core plus four sensor-specific source files.

Important APIs, types, and functions: `obj-$(CONFIG_USB_GL860) += gspca_gl860.o` binds the object to the Kconfig option. `gspca_gl860-objs` lists `gl860.o`, `gl860-mi1320.o`, `gl860-ov2640.o`, `gl860-ov9655.o`, and `gl860-mi2020.o`. `ccflags-y` adds the parent GSPCA include directory so `gspca.h` is found.

Control flow: Kbuild compiles each listed source into constituent objects and links them into `gspca_gl860.o`, then into a module or built-in object depending on `CONFIG_USB_GL860`.

State and persistence: no runtime state. The source list is the authoritative link boundary for sensor helpers referenced by `gl860.c`.

Dependencies and integration points: must stay synchronized with declarations in `gl860.h` and calls from `gl860.c` to `mi1320_init_settings()`, `mi2020_init_settings()`, `ov2640_init_settings()`, and `ov9655_init_settings()`.

Risks: omitting a sensor object causes link failures; adding a source without updating this file leaves code unreachable. Test signals are successful incremental and clean Kbuilds with `CONFIG_USB_GL860=m` and expected module symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860-mi1320.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860-mi1320.c

Purpose: `gl860-mi1320.c` provides GL860 bridge initialization, resolution setup, and camera controls for the Micron MI1320 sensor. It is linked into `gspca_gl860` and selected after `gl860.c` identifies the sensor.

Important APIs, types, and functions: `mi1320_init_settings()` fills `struct sd` current/default/max control ranges and installs function pointers for startup, alt configuration, pre-alt initialization, stop cleanup, and camera settings. `common()` replays shared GL860/MI1320 register scripts. `mi1320_sensor_settings()` chooses 640, 800, or 1280 register tables. `mi1320_camera_settings()` maps V4L2 controls to bridge/sensor register writes and tracks old values in `sd->vold`.

Control flow: GL860 core calls `mi1320_init_settings()` during probe. `sd_init()` reaches `mi1320_init_at_startup()`, which runs startup and common tables. Before streaming, `mi1320_configure_alt()` selects alt 3 for 640 and alt 1 for larger modes, then `mi1320_init_pre_alt()` resets cached controls, runs common setup, applies resolution settings, and applies camera settings. Stop sends a shutdown sequence through `mi1320_post_unset_alt()`.

State and persistence: the file uses `vcur`, `vold`, and `vmax` from `struct sd_gl860`. `mirrorMask` is reset at stream start and later influenced by orientation monitoring in `gl860.c`. `swapRB` is set when hue selects the special channel-swap mode, which affects packet scan line skipping in the core.

Dependencies and integration points: depends on `gl860_RTx()`, `fetch_validx()`, `keep_on_fetching_validx()`, V4L2 control values managed by `gl860.c`, and GSPCA mode `.priv` values (`IMAGE_640`, `IMAGE_800`, `IMAGE_1280`).

Risks: register scripts are opaque and hardware-log derived; small ordering changes can break capture. `mi1320_camera_settings()` contains repeated hue handling and disabled contrast max, so UI expectations may not match hardware. Test signals include sensor detection as MI1320, correct altsetting per resolution, visible control effects, correct orientation flips, and no dropped first frames after startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860-mi1320.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860-mi2020.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860-mi2020.c

Purpose: `gl860-mi2020.c` implements the GL860 path for the Micron MI2020 2MP sensor. It provides large register scripts for startup, per-resolution programming, white balance, AC frequency, flip/mirror, brightness, contrast/gamma, backlight, sharpness, and hue channel swapping.

Important APIs, types, and functions: `mi2020_init_settings()` sets defaults and function pointers in the shared GL860 `struct sd`. `common()` sends a mix of `validx` and `idxdata` scripts. `mi2020_init_at_startup()` performs probe reads and startup scripts. `mi2020_init_post_alt()` is the main resolution and sensor sequencing path. `mi2020_camera_settings()` applies deferred controls after enough images have arrived. `fetch_idxdata()` is heavily used for 3-byte indexed writes with embedded sleeps.

Control flow: probe installs MI2020 operations, then startup reads probe state and runs `tbl_init_at_startup` plus common scripts. Stream start resets selected `vold` entries, calls `mi2020_init_post_alt()`, programs resolution-specific data for 640, 800, 1280, or 1600 modes, then applies frequency, white balance, flip/mirror, and long post-alt tables. `mi2020_camera_settings()` refuses to apply most controls until `sd->nbIm >= 4`, causing the core callback to retry later.

State and persistence: `sd->nbIm` counts early frames, `waitSet` defers settings, `vold` avoids redundant writes, and `swapRB` is toggled by hue. Hardware state is otherwise replayed on stream transitions.

Dependencies and integration points: depends on `gl860.c` callback increments and orientation logic, GL860 control transfer helpers, GSPCA mode `.priv` values, and V4L2 controls registered from `vmax`.

Risks: this is timing-sensitive, with sleeps up to 1850 ms and many undocumented tables. Deferred settings can hide control changes until enough frames have completed. Several controls are advertised with comments saying the hardware path is incomplete or not done. Test signals include all four modes streaming, controls taking effect after initial frames, no frame corruption when flip/mirror changes, and no USB short-control-transfer logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860-mi2020.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860-ov2640.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860-ov2640.c

Purpose: `gl860-ov2640.c` supports OV2640 sensors behind the GL860 bridge, including 640x480, 800x600, 1280x960, and 1600x1200 Bayer modes. It programs OV sensor registers through GL860 vendor control sequences and exposes a broad set of V4L2 image controls.

Important APIs, types, and functions: `ov2640_init_settings()` installs sensor callbacks and control ranges. `ov2640_init_at_startup()` runs bridge reset/probe sequences, common OV2640 register setup, and expected read checks. `ov2640_init_post_alt()` selects per-resolution scripts and then calls `ov2640_camera_settings()`. `ov2640_camera_settings()` handles backlight, brightness, white balance, contrast, saturation, sharpness, hue, gamma, and mirror/flip.

Control flow: GL860 core selects this file after sensor probing or module parameter override. Startup replays `tbl_init_at_startup`, `dat_init1`, and `tbl_common`. Stream preparation chooses alt 3 for 640 and alt 1 for larger modes. Post-alt setup sends common sensor settings, resolution-specific tables, and image dimension bytes (`dat_640`, `dat_800`, `dat_1280`, `dat_1600`). Stop sends a bridge reset and `tbl_post_unset_alt`.

State and persistence: `vcur/vold/vmax` track control state. `mirrorMask` starts at zero and may be changed by core orientation polling. Hue values at or above the special limit set `swapRB`, which changes frame data skipping in the shared GL860 packet scanner.

Dependencies and integration points: uses `ctrl_out`, `ctrl_in`, `fetch_validx`, and shared mode constants from `gl860.h`. It depends on the core `dq_callback` for delayed orientation-driven settings and on GSPCA frame assembly for Bayer payloads.

Risks: `ov2640_camera_settings()` intentionally writes backlight twice and only updates `vold.backlight` after the second block, so refactoring can alter behavior. Some expected read buffers are initialized with expected values but not checked by this file. Test signals include correct mode dimensions, visible controls, stable mirror/flip, successful 1600 mode start, and clean stop/restart without stale sensor state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860-ov2640.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860-ov9655.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860-ov9655.c

Purpose: `gl860-ov9655.c` supports OV9655 sensors on GL860 devices. It is narrower than the other GL860 sensor files, exposing 640x480 and 1280x960 Bayer modes plus brightness and a hue-driven red/blue swap.

Important APIs, types, and functions: `ov9655_init_settings()` installs operation callbacks and only enables controls whose `vmax` entries are nonzero. `ov9655_init_at_startup()` replays startup and common tables. `ov9655_init_post_alt()` selects `tbl_640` or `tbl_1280`, sends each table with length metadata, then performs a repeated post-alt handshake around reads from `0x801e`. `ov9655_camera_settings()` writes brightness and toggles `swapRB` through hue.

Control flow: the GL860 core calls this file after sensor detection. Stream setup chooses alt 1 for all modes. Pre-alt resets cached brightness and hue, replays common bridge setup, then post-alt loads the resolution table and repeated sensor wake/config sequences. Stop sends a bridge stop command and writes `0x0061` to index zero.

State and persistence: control state is minimal: `vcur.brightness`, `vcur.hue`, `vold` cache, and `swapRB`. Mirror, flip, gamma, contrast, saturation, white balance, backlight, and frequency are effectively unavailable because max values are zero.

Dependencies and integration points: uses shared GL860 control transfer helpers, `fetch_validx()`/`keep_on_fetching_validx()`, GSPCA mode selection, and core packet scan behavior for `swapRB`.

Risks: post-alt sequencing is highly repetitive and likely timing-sensitive. `tbl_commmon` is misspelled but internally consistent. Brightness writes mutate a local byte string before sending. Test signals include both modes producing valid Bayer frames, brightness changes affecting image intensity, hue swap behavior, and no failures in the repeated `0x801e` read/write handshake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860-ov9655.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860.c

Purpose: `gl860.c` is the bridge/core module for Genesys Logic GL860 webcams. It detects one of several sensors, installs the appropriate sensor-specific operations, registers controls, selects transfer modes, parses GL860 isochronous packets, and provides common USB control helpers.

Important APIs, types, and functions: `sd_config()` handles module parameter overrides and sensor probing. Four `sd_desc` instances share callbacks but are assigned after sensor detection. `sd_s_ctrl()` updates `sd->vcur` and defers hardware writes with `waitSet`. `sd_pkt_scan()` recognizes `0x0202` frame-start markers and strips two-byte packet headers. `sd_callback()` polls orientation and applies pending camera settings. `gl860_RTx()`, `fetch_validx()`, `keep_on_fetching_validx()`, and `fetch_idxdata()` are exported within the module to sensor files.

Control flow: USB probe enters with the MI1320 descriptor, but `sd_config()` may replace `gspca_dev->sd_desc` after `gl860_guess_sensor()`. Sensor choice controls mode table and function pointer installation. On stream start, GSPCA calls `isoc_init`, `start`, packet scan callbacks, and dequeue callbacks. Sensor code programs bridge/sensor registers through the helper functions.

State and persistence: `struct sd` stores current, old, and maximum control values, sensor ID, orientation state, `swapRB`, `mirrorMask`, image counters, and `waitSet`. Static `nSkipped` in `sd_pkt_scan()` persists across calls and is reset only at frame markers.

Dependencies and integration points: integrates tightly with all `gl860-*.c` files, the GSPCA core, V4L2 controls, USB vendor control requests, and the Linux USB driver table for `05e3:0503` and `05e3:f191`.

Risks: sensor detection is heuristic and can be overridden by a module parameter. Descriptor replacement during config is unusual and must happen before later GSPCA callbacks. Static packet-scan state assumes a single active device stream. Test signals include correct sensor logs, controls appearing according to `vmax`, frame boundaries at `0x0202`, orientation-triggered flip changes, and successful suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860.h

Purpose: `gl860.h` is the private interface between the GL860 bridge core and its sensor-specific implementation files.

Important APIs, types, and functions: it defines module naming/version constants, aliases `ctrl_in` and `ctrl_out` to `gl860_RTx`, sensor IDs (`ID_MI1320`, `ID_OV2640`, `ID_OV9655`, `ID_MI2020`), mode IDs (`IMAGE_640`, `IMAGE_800`, `IMAGE_1280`, `IMAGE_1600`), `struct sd_gl860` for image controls, and `struct sd` for GL860 device state and function pointers. `struct validx` and `struct idxdata` represent compact register-script entries. It declares helper functions and each sensor's `*_init_settings()`.

Control flow: the header has no runtime flow, but its function pointer fields define how `gl860.c` dispatches startup, altsetting, stream setup, stop, and camera settings into selected sensor code.

State and persistence: `struct sd` persists control snapshots, sensor ID, orientation/mirror state, frame counters, and deferred setting flags across stream callbacks. This struct embeds `struct gspca_dev` first, satisfying the GSPCA casting contract.

Dependencies and integration points: includes `gspca.h` and is included by every GL860 source. It must match the object list in the GL860 Makefile so all declared sensor initializers are linked.

Risks: macros like `_MI1320_` cast arbitrary `gspca_dev` pointers to `struct sd`, so they are valid only inside this module. Function pointer fields must be initialized by each sensor file before GSPCA invokes callbacks. Test signals are clean compilation, no missing sensor initializer symbols, and correct struct layout for `gspca_dev_probe()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/gl860.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gspca.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gspca.c

Purpose: `gspca.c` is the shared GSPCA USB camera core. It registers V4L2 video devices, owns vb2 queue integration, manages USB isochronous/bulk URBs, dispatches subdriver callbacks, assembles frames, supports optional input buttons, and handles disconnect and power management.

Important APIs, types, and functions: exported entry points are `gspca_dev_probe()`, `gspca_dev_probe2()`, `gspca_disconnect()`, `gspca_frame_add()`, `gspca_suspend()`, and `gspca_resume()`. URB callbacks include `isoc_irq()`, `bulk_irq()`, and optional `int_irq()`. Streaming setup runs through `gspca_init_transfer()`, `build_isoc_ep_tb()`, `create_urbs()`, and `gspca_stream_off()`. V4L2 operations cover format enumeration, try/set format, frame sizes/intervals, stream parameters, JPEG compression, and vb2 buffer lifecycle.

Control flow: subdrivers call `gspca_dev_probe()`, which allocates `gspca_dev`, initializes V4L2/vb2 state, calls subdriver `config/init/init_controls`, sets a default mode, registers the video device, and starts optional interrupt input. On `STREAMON`, vb2 calls `gspca_start_streaming()`, which chooses endpoints/altsettings, creates URBs, calls subdriver `start`, submits URBs, and resubmits them in completion handlers. Subdriver packet scanners call `gspca_frame_add()` to complete buffers.

State and persistence: `gspca_dev` stores mode, queue, buffer list, URBs, current image pointer/length, sequence, USB error, locks, streaming/present flags, endpoint/altsetting, and PM frozen state. State is per device and freed through V4L2 release.

Dependencies and integration points: depends on Linux USB, V4L2, videobuf2-vmalloc, optional input, and subdriver `sd_desc` contracts.

Risks: frame correctness depends on subdrivers emitting a sane FIRST/INTER/LAST sequence. `gspca_frame_add()` protects buffer list selection but image pointer/length are interrupt-context state. Bandwidth negotiation can fail on crowded USB buses. Test signals include v4l2-compliance basics, repeated stream on/off, no buffer leaks on disconnect, suspend/resume with active streams, and absence of frame overflow logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gspca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gspca.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gspca.h

Purpose: `gspca.h` defines the public contract between the GSPCA core and individual USB camera subdrivers.

Important APIs, types, and functions: debug levels and `gspca_dbg/gspca_err` wrap V4L2 logging. `struct cam` describes mode tables, bulk/isoc transport, endpoint constraints, bandwidth behavior, and framerate tables. `struct sd_desc` lists mandatory and optional subdriver callbacks. `enum gspca_packet_type` defines frame assembly events. `struct gspca_buffer` wraps vb2 buffers, while `struct gspca_dev` holds the complete per-device core state. The header declares probe/disconnect, frame assembly, PM, and autogain helper APIs.

Control flow: subdrivers embed `struct gspca_dev` as their first field, fill an `sd_desc`, and pass both to `gspca_dev_probe()`. During streaming, subdriver `pkt_scan` callbacks translate USB payloads into `gspca_frame_add()` calls using the packet type enum.

State and persistence: all persistent runtime state is in `struct gspca_dev`: USB device, V4L2 device, controls, URBs, current image assembly fields, queue/list locks, mode, sequence, endpoint, altsetting, present/streaming flags, and optional input state.

Dependencies and integration points: includes Linux module/kernel/USB, V4L2, videobuf2, controls, and mutex APIs. It is included by every researched subdriver.

Risks: struct layout comments are contractual; `struct gspca_dev` must be first in subdriver structs because casts rely on it. Callback omissions are handled selectively, so mandatory operations must be present. Test signals are compile-time type compatibility and runtime probe/streaming through representative subdrivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gspca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jeilinj.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jeilinj.c

Purpose: `jeilinj.c` supports Jeilin dual-mode bulk cameras that deliver raw JPEG payload blocks. It covers Sakar 57379 and Sportscam DV15 variants, with extra V4L2 controls and JPEG quality handling for the Sportscam path.

Important APIs, types, and functions: `struct sd` stores block count, device type, control pointers, JPEG quality, and a generated JPEG header. `jlj_write2()` and `jlj_read1()` use fixed bulk endpoints for command and acknowledgement. `jlj_start()` sends variant-dependent startup command sequences. `sd_pkt_scan()` detects frame starts by `FRAME_START`, prepends a generated JPEG header, tracks `blocks_left`, and marks the final block as `LAST_PACKET`. `sd_stopN()` drains remaining blocks until JPEG EOI before sending stop commands.

Control flow: probe chooses an `sd_desc` by `driver_info`; Sportscam gets controls and JPEG compression callbacks, Sakar gets a simpler descriptor. GSPCA bulk URB callbacks feed fixed 0x200-byte blocks into `sd_pkt_scan()`. On frame start, byte `0x0a` gives total block count; following blocks decrement until completion.

State and persistence: `blocks_left` persists across packets to frame completion. `jpeg_hdr` is regenerated at stream start using current dimensions and quality. Control values are held by V4L2 controls; command writes occur only when streaming.

Dependencies and integration points: uses `jpeg.h` for standard JPEG header and quantization updates, GSPCA bulk transfer, V4L2 JPEG compression compatibility callbacks, and fixed vendor endpoint conventions.

Risks: `((u32 *)data)[0]` may be unaligned on some architectures, and block count is trusted from device data. `sd_stopN()` can loop while draining if EOI is not observed. Test signals include valid JPEG decode with inserted DHT/DQT, correct 320/640 mode startup, Sportscam controls affecting hardware, and clean streamoff after partial frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jeilinj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jl2005bcd.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jl2005bcd.c

Purpose: `jl2005bcd.c` supports JL2005B/C/D USB cameras using command bulk endpoint `0x03`, response endpoint `0x84`, and data endpoint `0x82`. It advertises a custom `V4L2_PIX_FMT_JL2005BCD` format for CIF or VGA camera families detected from firmware ID.

Important APIs, types, and functions: `struct sd` stores firmware ID, workqueue, frame brightness, block size, and selected mode family. Command helpers include `jl2005c_write2()`, `jl2005c_read1()`, `jl2005c_read_reg()`, and `jl2005c_write_reg()`. `jl2005c_get_firmware_id()` reads six identifying registers. Four stream-start helpers program large/small VGA/CIF modes. `jl2005c_dostream()` is the synchronous bulk capture worker.

Control flow: `sd_config()` enables bulk mode with a small core buffer, reads firmware ID, chooses CIF modes with 0x80-byte blocks when the first ID nibble is `0x4`, otherwise VGA modes with 0x200-byte blocks, and initializes work. `sd_start()` selects a register script by requested width and schedules the worker. The worker requests a new frame, validates the `JL` header, computes remaining bytes from header byte 7 times block size, then reads chunks until `LAST_PACKET`.

State and persistence: firmware ID and block size persist for the device lifetime. Frame-local state (`bytes_left`, `header_read`) lives in the worker. No V4L2 controls are provided.

Dependencies and integration points: depends on process-context USB bulk I/O, GSPCA stop0 flushing, and a custom userspace pixel format decoder.

Risks: capture stops on short reads or bad first block signature, with no recovery loop inside the worker. `sd_start()` returns success after scheduling even if later worker setup fails. Test signals include correct CIF/VGA detection, valid frame sizes, repeated stream restart without stuck work, and graceful handling of unplug during worker reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jl2005bcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jpeg.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jpeg.h

Purpose: `jpeg.h` provides a static baseline JPEG header and small helper functions for GSPCA subdrivers that receive entropy-coded JPEG payloads without complete headers.

Important APIs, types, and functions: `jpeg_head[]` contains SOI, DQT, DHT, SOF0, and SOS segments unless `CONEX_CAM` is defined. `JPEG_QT0_OFFSET`, `JPEG_QT1_OFFSET`, `JPEG_HEIGHT_OFFSET`, and `JPEG_HDR_SZ` describe patch points. `jpeg_define()` copies the template and patches height, width, and Y sampling. `jpeg_set_qual()` scales luminance and chrominance quantization tables from a V4L2-style quality value.

Control flow: no runtime registration. Subdrivers allocate a header buffer of `JPEG_HDR_SZ`, call `jpeg_define()` at stream start or mode change, call `jpeg_set_qual()` when quality changes, and prepend the buffer to frame data.

State and persistence: `jpeg_head` is read-only. Mutable state lives in each subdriver's copied header buffer.

Dependencies and integration points: requires kernel `u8` and `memcpy()` availability through includers. It is used by `jeilinj.c` in this subset and by other GSPCA JPEG subdrivers.

Risks: quantization scaling does not clamp values to JPEG's usual 1..255 range, so extreme quality values can produce zero or oversized table entries if callers bypass expected ranges. Header constants must stay consistent with the byte template. Test signals include generated JPEGs decoding in userspace, correct dimensions in SOF0, and quality controls visibly changing compression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jpeg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/kinect.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/kinect.c

Purpose: `kinect.c` is a GSPCA driver for Microsoft Kinect camera interfaces, supporting either video or depth operation selected by the `depth_mode` module parameter. It programs the device through vendor control commands and parses Kinect stream packet headers.

Important APIs, types, and functions: `struct sd` stores command tag, stream flag, and command buffers. `struct pkt_hdr` describes stream packets; `struct cam_hdr` describes control command/reply framing. `send_cmd()` builds tagged control messages, validates replies, and increments `cam_tag`. `write_register()` wraps command `0x03`. `sd_config_video()` and `sd_config_depth()` choose mode tables, endpoint `0x81` or `0x82`, and stream flags. `sd_pkt_scan()` validates `RB` packet magic and maps flags to FIRST/INTER/LAST.

Control flow: probe chooses video or depth descriptor based on `depth_mode`. Start functions write register sequences for video or depth stream configuration. Video mode supports Bayer, UYVY, and Y10B variants; depth mode exposes 640x480 Y10B-packed. Packets carry a header whose flag identifies start, middle, or end using `stream_flag | {1,2,5}`.

State and persistence: `cam_tag` persists across control commands for reply matching. `stream_flag` identifies the active stream type. No V4L2 controls are exposed.

Dependencies and integration points: depends on GSPCA isochronous endpoint selection, V4L2 custom pixel formats, USB vendor control transfers, and Kinect firmware command protocol.

Risks: `send_cmd()` loops while reads return zero with no explicit retry limit. It returns `-1` for several protocol errors rather than specific errno values. `sd_pkt_scan()` silently ignores packets shorter than the header. Test signals include successful command/reply tag matching, valid video and depth frames, correct endpoint selection, and reliable stream reset on stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/kinect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/konica.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/konica.c

Purpose: `konica.c` supports Konica-chipset USB webcams such as Intel YC76. It is notable for using two isochronous endpoints in tandem: one data endpoint and one status endpoint used to frame and filter data packets.

Important APIs, types, and functions: `struct sd` stores the last data URB and snapshot-button state. `reg_w()` and `reg_r()` perform vendor register access. `sd_start()` manually creates four URBs because `cam.no_urb_create` is set. `sd_isoc_irq()` pairs data/status URBs by `start_frame`, interprets one-byte status packets, reports optional input events, and emits frame data. `sd_s_ctrl()` writes brightness, contrast, saturation, white balance, and sharpness, briefly stopping the stream around each register write.

Control flow: probe configures three `V4L2_PIX_FMT_KONICA420` modes and disables core URB creation. Init waits roughly six seconds for firmware boot and polls register `0x10` for readiness. Start writes mode value from `.priv`, turns streaming on, allocates alternating endpoint URBs, and lets the GSPCA core submit them. Status bytes with bit 7 start a new frame; bit 0 drops padding data; bit 6 reports the camera button.

State and persistence: `last_data_urb` pairs asynchronous completions. `snapshot_pressed` prevents duplicate input events and is cleared on stop. Control values are not cached beyond V4L2 core state.

Dependencies and integration points: depends on GSPCA custom URB support (`no_urb_create`), Linux input when enabled, and fixed endpoint addresses `0x81/0x82`.

Risks: synchronization assumes status URB arrives after its matching data URB; lost ordering discards/resubmits. Manual URB allocation must match core destruction expectations. Test signals include paired URB start frames, button press/release events, no stuck pressed state after stop, and control writes without stream loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/konica.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/Kconfig

Purpose: this Kconfig fragment defines `CONFIG_USB_M5602`, the build option for ALi m5602 GSPCA webcam support.

Important APIs, types, and functions: it declares a `tristate` option named "ALi USB m5602 Camera Driver", depends on `VIDEO_DEV` and `USB_GSPCA`, and documents the output module name `gspca_m5602`.

Control flow: no runtime behavior. The setting controls whether the m5602 bridge core and supported sensor files are built in, modular, or omitted.

State and persistence: persists in kernel `.config`; runtime state is defined in m5602 C sources and `m5602_bridge.h`.

Dependencies and integration points: integrates with the parent GSPCA media driver menu and Kbuild files. It must remain aligned with the Makefile's `obj-$(CONFIG_USB_M5602)` binding.

Risks: missing `USB_GSPCA` dependency would expose unresolved core symbols. Test signals include menu visibility, successful `CONFIG_USB_M5602=m` build, and generated `gspca_m5602.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/Makefile -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/Makefile

Purpose: this Makefile composes the ALi m5602 GSPCA module from its bridge core and sensor-specific implementation files.

Important APIs, types, and functions: `obj-$(CONFIG_USB_M5602) += gspca_m5602.o` binds build output to Kconfig. `gspca_m5602-objs` lists `m5602_core.o`, `m5602_ov9650.o`, `m5602_ov7660.o`, `m5602_mt9m111.o`, `m5602_po1030.o`, `m5602_s5k83a.o`, and `m5602_s5k4aa.o`. `ccflags-y` adds the parent GSPCA include path.

Control flow: Kbuild compiles and links the listed objects into `gspca_m5602.o` for either built-in or module output.

State and persistence: no runtime state. The object list defines which sensor backends are available to the bridge core.

Dependencies and integration points: must match declarations and sensor tables used by the m5602 core and `m5602_bridge.h`; the include flag is required for `gspca.h`.

Risks: object list drift causes link failures or missing sensor support. Test signals are clean Kbuild with `CONFIG_USB_M5602=m`, expected module name, and no missing sensor symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_bridge.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_bridge.h

Purpose: `m5602_bridge.h` is the shared private bridge header for ALi m5602 GSPCA webcam drivers. It defines bridge register addresses, endpoint constants, driver metadata, per-device state, and bridge/sensor I/O prototypes.

Important APIs, types, and functions: the header maps many `M5602_XB_*` and `M5602_OB_*` register constants for sensor geometry, clocks, endpoint control, I2C, GPIO, power, and scratch registers. It defines `I2C_BUSY`, module description strings, endpoint addresses `0x81` and `0x82`, and `M5602_URB_MSG_TIMEOUT`. `struct sd` embeds `gspca_dev`, stores the active `struct m5602_sensor *`, frame ID/count, optional rotation thread, and several V4L2 control clusters. Function prototypes cover bridge reads/writes and sensor reads/writes.

Control flow: no implementation lives here, but m5602 core/sensor files use these constants and prototypes to reset the bridge, configure the active image sensor, poll I2C state, stream isochronous data, and expose controls.

State and persistence: `struct sd` defines persistent per-device runtime state, including frame boundary tracking, active sensor dispatch, rotation polling, and clustered controls for white balance, exposure, gain, and flips.

Dependencies and integration points: includes `gspca.h` and Linux slab support. It depends on an external `struct m5602_sensor` definition from other m5602 headers/sources in the module and is built through the m5602 Makefile.

Risks: register constants are low-level hardware ABI; mistakes can break sensor setup or bus access. Control cluster pointers must be initialized consistently by the core. Test signals include successful sensor detection, I2C operations clearing `I2C_BUSY`, correct frame ID transitions, rotation handling on flip-capable cameras, and no unresolved references to bridge I/O helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_bridge.h -->
