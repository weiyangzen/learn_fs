# subset-b-004210 Research

Grouped research for Linux GSPCA USB camera bridge and sensor source files under `sources/distributed-fs/ceph-client/drivers/media/usb/gspca`. Each section preserves the original source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_core.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_core.c

## Purpose
`m5602_core.c` is the USB/GSPCA bridge driver core for ALi M5602 webcams. It binds USB ID `0402:5602`, abstracts bridge register and sensor I2C access, probes one of several supported sensors, dispatches sensor-specific lifecycle hooks, and converts M5602 isochronous packets into GSPCA frame boundaries.

## Important APIs, Types, And Functions
The exported bridge helpers are `m5602_read_bridge()`, `m5602_write_bridge()`, `m5602_read_sensor()`, and `m5602_write_sensor()`. `sensor_urb_skeleton` and `bridge_urb_skeleton` define the vendor-control payload templates. `m5602_probe_sensor()` selects a `struct m5602_sensor` implementation from PO1030, MT9M111, S5K4AA, OV9650, OV7660, or S5K83A. GSPCA callbacks are wired through `sd_desc`: `m5602_configure()`, `m5602_init()`, `m5602_init_controls()`, `m5602_start_transfer()`, `m5602_stop_transfer()`, and `m5602_urb_complete()`.

## Control Flow
USB probe calls `gspca_dev_probe()` with `sd_desc`, then `m5602_configure()` optionally dumps bridge registers and tries each sensor probe. Sensor probes write bridge GPIO/clock/I2C preinit sequences and read sensor IDs; the selected sensor populates `cam_mode`/`nmodes`. On init and control setup the core delegates to sensor callbacks. Streaming start calls the sensor `start()` hook first, then sends a bridge start command `{0x13, 0xf9, 0x0f, 0x01}`. Packet scanning treats `ff xx id xx ff ff` with a changed frame id as a frame delimiter, strips six bytes for first packets and four bytes for continuation packets, caps copies at `pixfmt.sizeimage`, and feeds `gspca_frame_add()`.

## State, Persistence, And Dependencies
State is in `struct sd` embedded in `struct gspca_dev`: selected sensor pointer, frame id/count, V4L2 control pointers, and any sensor-specific thread/control state declared in the bridge header. Hardware state persists only in volatile bridge/sensor registers. Dependencies include USB control messages, GSPCA core, M5602 bridge register definitions, V4L2 controls, and all sensor headers.

## Integration Points
The file is the integration layer between the Linux USB driver model, GSPCA video-device callbacks, and per-sensor modules. Module parameters `force_sensor`, `dump_bridge`, and `dump_sensor` steer probe diagnostics and sensor selection. Power-management callbacks are inherited from GSPCA when `CONFIG_PM` is enabled.

## Risks
`m5602_wait_for_i2c()` polls without an explicit retry limit and depends on USB errors to break a busy sensor. `m5602_read_sensor()` documents known PO1030 issues for one-byte register reads. Several init callbacks return success even if their loop accumulated an error, so bad register scripts can be partially hidden. Disconnect assumes `sd->sensor` is valid. Bridge dumping is intentionally disruptive and warns that a power cycle may be required.

## Test Signals
Probe each supported sensor with and without `force_sensor`; verify bridge/sensor I2C reads and writes; stream across frame-id wrap; test short packets, over-size frames, suspend/resume, disconnect during streaming, and control changes while streaming; confirm `dump_sensor` and `dump_bridge` do not corrupt normal non-debug paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_mt9m111.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_mt9m111.c

## Purpose
`m5602_mt9m111.c` implements the Micron MT9M111 sensor backend for the ALi M5602 bridge. It probes the two-byte chip version, programs sensor-core/color-pipeline/camera-control pages, exposes VGA Bayer capture, and provides V4L2 gain, white-balance, and flip controls.

## Important APIs, Types, And Functions
Static register scripts `preinit_mt9m111`, `init_mt9m111`, and `start_mt9m111` mix bridge writes and two-byte sensor writes. Public callbacks are `mt9m111_probe()`, `mt9m111_init()`, `mt9m111_init_controls()`, `mt9m111_start()`, and `mt9m111_disconnect()`. Control helpers include `mt9m111_set_hvflip()`, `mt9m111_set_auto_white_balance()`, `mt9m111_set_gain()`, and RGB/green balance setters. `mt9m111_dump_registers()` walks all three sensor pages.

## Control Flow
Probe honors `force_sensor`, otherwise runs the preinit script and reads `MT9M111_SC_CHIPVER`, expecting bytes `0x14 0x3a`. Init replays a larger bridge/sensor script that resets the sensor, configures color-pipeline output, defect correction, auto-exposure/AWB parameters, context B, frame window, blanking, row mode, and shutter width. Start writes bridge timing setup, then synthesizes VSYNC and HSYNC parameters from the selected mode. V4L2 controls are ignored until streaming; white-balance auto mode optionally writes manual color gains, and H/V flip rewrites row-mode bits according to current width.

## State, Persistence, And Dependencies
The driver uses `sd` control pointers for auto white balance, color gains, gain, and flip clusters. It depends on M5602 sensor I2C helpers, MT9M111 register constants, GSPCA debug, V4L2 clustered controls, and camera mode state. Sensor page selection is persistent hardware state and must be explicitly set before page-relative register writes.

## Integration Points
The matching header registers this backend as `mt9m111` with slave ID `0xba` and two-byte register width. The M5602 core calls these callbacks through `struct m5602_sensor`. The sensor emits `V4L2_PIX_FMT_SBGGR8` at 640x480.

## Risks
`mt9m111_init()` returns `0` even when the register-script loop recorded an error. Control dispatch handles `V4L2_CID_HFLIP` but relies on clustering for VFLIP changes, which is subtle. Page-map assumptions are important: `mt9m111_set_auto_white_balance()` reads color-pipeline registers without setting `MT9M111_PAGE_MAP`, so prior page state can matter. Gain bit composition is hand-coded and should be validated against hardware.

## Test Signals
Validate chip ID detection, page-dump readability, VGA stream timing, H/V flip in both row-skip configurations, manual and auto white balance transitions, high gain boundary rejection, resume init, and injected USB/I2C failures in the init script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_mt9m111.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_mt9m111.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_mt9m111.h

## Purpose
`m5602_mt9m111.h` defines the MT9M111 register map, bit masks, default control values, exported callbacks, and static `struct m5602_sensor` descriptor used by the M5602 core.

## Important APIs, Types, And Functions
The header names sensor-core registers such as chip version, window, shutter, row mode, color gains, and page map; color-pipeline and camera-control registers; page constants `MT9M111_SENSOR_CORE`, `MT9M111_COLORPIPE`, and `MT9M111_CAMERA_CONTROL`; reset/standby/output flags; row-skip/flip flags; and default gain/white-balance values. It declares the MT9M111 probe/init/control/start/disconnect callbacks and instantiates `mt9m111`.

## Control Flow
There is no executable control flow. The constants drive the C file's register scripts and control handlers, while the static descriptor tells the core to use slave ID `0xba`, two-byte sensor registers, and the MT9M111 callback set.

## State, Persistence, And Dependencies
The header has no mutable state, but its page and bit definitions describe persistent sensor register state. It depends on `m5602_sensor.h`, which supplies `struct m5602_sensor`, instruction enums, and shared private control IDs.

## Integration Points
Included by `m5602_core.c` for sensor probing and by `m5602_mt9m111.c` for register programming. The descriptor is a compile-time registration mechanism rather than a dynamic module table.

## Risks
Because the descriptor is `static const` in a header, every translation unit that includes it gets a private copy; this is intentional in this driver but unusual. Incorrect page constants or two-byte register-width assumptions would corrupt all MT9M111 I2C transactions. Several bit names overlap numerically and must be used only with their documented registers.

## Test Signals
Build coverage, successful sensor callback linking, correct slave ID on USB/I2C traces, validated chip-version reads, and control defaults matching created V4L2 ranges are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_mt9m111.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_ov7660.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_ov7660.c

## Purpose
`m5602_ov7660.c` implements the OmniVision OV7660 backend for M5602 webcams. It probes OV7660 product/version IDs, initializes one-byte sensor registers and bridge timing for 640x480 Bayer output, and exposes auto white-balance, exposure-auto, autogain/gain, and flip controls.

## Important APIs, Types, And Functions
Core scripts are `preinit_ov7660` and `init_ov7660`. Public callbacks are `ov7660_probe()`, `ov7660_init()`, `ov7660_init_controls()`, `ov7660_start()`, `ov7660_stop()`, and `ov7660_disconnect()`. Control helpers are `ov7660_set_gain()`, `ov7660_set_auto_white_balance()`, `ov7660_set_auto_gain()`, `ov7660_set_auto_exposure()`, and `ov7660_set_hvflip()`. `ov7660_dump_registers()` can dump and destructively test writable registers.

## Control Flow
Probe optionally honors `force_sensor`, otherwise sends a bridge/sensor preinit sequence and reads `OV7660_PID`/`OV7660_VER`, expecting `0x76 0x60`. Init runs a long sequence covering reset, clocking, H/V window, biases, COM registers, Bayer output, and bridge VSYNC/HSYNC setup. The explicit start/stop callbacks are no-ops because the init sequence already programs streaming-related bridge state. Controls short-circuit until streaming and then read-modify-write `OV7660_COM8` for auto algorithms or write `OV7660_MVFP` for flips.

## State, Persistence, And Dependencies
Runtime state is limited to V4L2 control pointers in `sd`; persistent behavior lives in OV7660 and M5602 registers. The backend depends on one-byte `m5602_read_sensor()`/`write_sensor()` transactions, the M5602 bridge register map, V4L2 clustering, and the core's frame scanner.

## Integration Points
The header descriptor exposes this sensor as slave ID `0x42` and register width `1`. The mode table contributes one 640x480 `V4L2_PIX_FMT_SBGGR8` mode to `gspca_dev->cam`.

## Risks
Start and stop are no-ops, so all stream setup depends on init ordering and the core's bridge start command. The debug writable-register probe writes `0xff` across the register space and must stay diagnostic-only. Auto-exposure is exposed as a menu with only automatic/manual limit values, and manual exposure itself is not implemented in this file. Repeated bridge/GPIO script fragments make accidental ordering changes risky.

## Test Signals
Probe ID reads, VGA Bayer frame delivery, COM8 auto bit toggles, gain writes after disabling autogain, H/V flip visual orientation, resume behavior after init-only timing setup, and `dump_sensor` register restore behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_ov7660.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_ov7660.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_ov7660.h

## Purpose
`m5602_ov7660.h` supplies OV7660 register addresses, default image-control values, callback declarations, and the static M5602 sensor descriptor.

## Important APIs, Types, And Functions
The header defines gain, color-gain, ID, clock, COM, window, bias, output-format, lens-correction, and flip-related registers including `OV7660_PID`, `OV7660_VER`, `OV7660_COM8`, and `OV7660_MVFP`. Defaults cover gain, red/blue gain, saturation, and exposure. It declares OV7660 callbacks and instantiates `ov7660`.

## Control Flow
There is no runtime logic. The constants are consumed by `m5602_ov7660.c`, and the descriptor advertises slave ID `0x42`, one-byte register width, and all lifecycle hooks including no-op start/stop.

## State, Persistence, And Dependencies
No local state exists. The definitions describe hardware register state and depend on `m5602_sensor.h` for the shared sensor interface and `force_sensor`/`dump_sensor` externs.

## Integration Points
Included by both the core sensor-probe list and the OV7660 implementation. Its `struct m5602_sensor` object is the only binding metadata the core needs to call into this backend.

## Risks
One-byte register-width metadata must match the core I2C access path; a wrong value changes read/write command construction. Several reserved registers are named and used in scripts, so datasheet uncertainty remains part of the maintenance risk.

## Test Signals
Compile-time inclusion, correct slave ID in traces, OV7660 ID readback, mode registration, and successful callback dispatch for init/start/stop/disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_ov7660.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_ov9650.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_ov9650.c

## Purpose
`m5602_ov9650.c` implements the OmniVision OV9650 sensor backend for the M5602 bridge. It supports multiple Bayer modes from QCIF to VGA, DMI-based orientation quirks, bridge timing synthesis, sensor sleep on stop, and V4L2 auto/manual exposure, gain, white balance, and flip controls.

## Important APIs, Types, And Functions
Register scripts include `preinit_ov9650`, `init_ov9650`, and `res_init_ov9650`. `ov9650_flip_dmi_table` lists machines whose physical camera orientation needs compensation. Public callbacks are `ov9650_probe()`, `ov9650_init()`, `ov9650_init_controls()`, `ov9650_start()`, `ov9650_stop()`, and `ov9650_disconnect()`. Control helpers program split exposure bits, gain MSBs/LSBs, red/blue balance, COM8 auto bits, and `OV9650_MVFP`.

## Control Flow
Probe optionally honors `force_sensor`, runs preinit, and validates `OV9650_PID == 0x96` plus `OV9650_VER == 0x52`. Init optionally dumps registers, then performs reset, clock, black-level, color, window, denoise, variopixel, and soft-sleep setup. Start wakes output drive, writes bridge line/pixel setup, calculates vertical offset adjustments based on DMI and VFLIP, writes VSYNC/HSYNC windows, and selects the OV9650 mode bits for 176x144, 320x240, 352x288, or 640x480. Flip changes may re-run `ov9650_start()` while streaming to realign bridge timing.

## State, Persistence, And Dependencies
Mode and control state is stored in GSPCA/V4L2 structures; orientation policy also depends on DMI system matching. Hardware state is persistent until rewritten in OV9650 and bridge registers. The file depends on one-byte M5602 sensor access, V4L2 auto clusters, DMI, and GSPCA stream state.

## Integration Points
The descriptor in the header binds slave ID `0x60` and one-byte register width. The core calls this backend during sensor probing and stream lifecycle. The raw Bayer format is `V4L2_PIX_FMT_SBGGR8`.

## Risks
`ov9650_init()` returns success even if a register write fails. DMI orientation compensation affects both sensor flip bits and bridge VSYNC offsets, making regressions platform-specific. Exposure and gain are split across multiple registers, so partial write failures leave inconsistent values. The diagnostic writable-register scan is destructive if used outside controlled debugging.

## Test Signals
ID probe, all four modes, DMI-listed and non-DMI orientation behavior, stream restart after flip, manual exposure/gain after disabling auto modes, stop sleep command, resume double-reset behavior, and fault injection on multi-register control writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_ov9650.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_ov9650.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_ov9650.h

## Purpose
`m5602_ov9650.h` defines the OV9650 register map, bit masks, mode-selection flags, default controls, orientation offset, callbacks, and static sensor descriptor.

## Important APIs, Types, And Functions
Definitions cover core OV9650 registers, COM register bits for reset, resolution, RGB/raw output, AGC/AEC/AWB, variopixel, flip, sleep, denoise, and default gain/color/exposure values. It declares OV9650 callbacks and instantiates `ov9650`.

## Control Flow
There is no executable flow. The descriptor advertises slave ID `0x60`, register width `1`, and all lifecycle hooks. The constants feed the C file's probe, init, start, stop, and control code.

## State, Persistence, And Dependencies
The header has no mutable state. It depends on Linux DMI declarations and `m5602_sensor.h`. Its bit definitions describe volatile but persistent-in-hardware sensor state.

## Integration Points
The M5602 core includes this header to get the `ov9650` descriptor; the OV9650 implementation includes it for register programming and DMI support.

## Risks
Resolution flags share `COM7`, so using a wrong combination can select the wrong sensor output format. `OV9650_LEFT_OFFSET` is baked into bridge timing synthesis and is hardware/platform sensitive. As a header-level `static const` object, duplicate descriptor copies are intentional but non-obvious.

## Test Signals
Build, probe ID readback, mode-specific `COM7` writes in USB traces, sleep/wake control writes, and DMI orientation tests across listed systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_ov9650.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_po1030.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_po1030.c

## Purpose
`m5602_po1030.c` implements the PixelPlus PO1030 sensor backend for M5602 webcams. It initializes PO1030 raw Bayer output, probes by device ID, programs 640x480 timing, and exposes white balance, exposure, gain, and flip controls.

## Important APIs, Types, And Functions
Important scripts are `preinit_po1030` and `init_po1030`; `po1030_modes` defines 640x480 Bayer with a vertical offset in `priv`. Public callbacks are `po1030_probe()`, `po1030_init()`, `po1030_init_controls()`, `po1030_start()`, and `po1030_disconnect()`. Helpers program exposure high/middle bytes, global and color gains, `PO1030_CONTROL2` flip bits, and `PO1030_AUTOCTRL1` auto white-balance/exposure bits.

## Control Flow
Probe runs bridge GPIO/clock setup and sensor reset, then reads `PO1030_DEVID_H` and accepts `0x30`. Init programs reset, raw Bayer output, HREF, gamma, frame/window dimensions, gains, and bridge GPIO. Start adjusts sensor window registers for 320 or 640 width, then writes bridge sensor type, line/pixel framing, VSYNC offsets/height, HSYNC width, and signal initialization. Controls are active only while streaming and use auto clusters to apply manual color or exposure values when auto mode is disabled.

## State, Persistence, And Dependencies
The backend uses `sd` pointers for auto white balance, RGB/green balances, exposure, gain, and flips. Sensor register state persists until rewritten. Dependencies include one-byte M5602 sensor access, V4L2 custom green-balance control, and bridge timing registers.

## Integration Points
The header descriptor identifies the sensor as slave ID `0xdc`, one-byte registers, and no stop callback. The M5602 core calls `po1030_start()` before enabling the bridge transfer.

## Risks
The M5602 core comments that one-byte sensor reads have PO1030 issues, and this backend relies on read-modify-write for auto controls and flips. `po1030_start()` has 320-width logic despite only a 640x480 mode in the local mode table, suggesting leftover or future path risk. No stop hook means the sensor is not explicitly put into standby on stream stop. Duplicate macro definitions exist in the header.

## Test Signals
Probe ID, raw 640x480 frame alignment, bridge VSYNC/HSYNC values from `priv`, manual exposure and gain writes, auto/manual white balance transitions, flip read-modify-write correctness, and stream stop/restart stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_po1030.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_po1030.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_po1030.h

## Purpose
`m5602_po1030.h` defines PO1030 register addresses, output/control bits, defaults, callback declarations, and the static M5602 sensor descriptor.

## Important APIs, Types, And Functions
The register definitions cover device ID, frame/window geometry, gains, integration lines, control registers, flicker periods, gamma coefficients, color matrix, auto controls, output format, edge enhancement, and saturation/contrast. Bit masks include H/V flip, HREF enable, raw Bayer output, shutter/auto-subsampling/frame-equal, reset, and subsampling. Defaults cover global gain, exposure, and RGB/green gains.

## Control Flow
No executable logic exists. The descriptor binds name `PO1030`, slave ID `0xdc`, register width `1`, and the probe/init/control/start/disconnect callbacks used by the core.

## State, Persistence, And Dependencies
No local mutable state. It depends on `m5602_sensor.h` for the shared interface and exports the shared module parameters. The constants describe persistent PO1030 register programming state.

## Integration Points
Included by the M5602 core and PO1030 implementation. The custom green-balance control ID comes from the shared sensor header.

## Risks
`PO1030_AUTO_SUBSAMPLING` and `PO1030_FRAME_EQUAL` are defined twice with identical values, which is harmless but noisy. Geometry register definitions must match the one-byte write path and start-time bridge timing calculations. Missing stop callback in the descriptor is an intentional behavioral contract to notice in lifecycle tests.

## Test Signals
Build, descriptor callback coverage, correct slave ID, PO1030 ID readback, and sensor register traces for output format, window, exposure, gain, and flip writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_po1030.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_s5k4aa.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_s5k4aa.c

## Purpose
`m5602_s5k4aa.c` implements the Samsung S5K4AA sensor backend for the M5602 bridge. It supports VGA and SXGA Bayer modes, page-based sensor initialization, DMI-based flip compensation, and V4L2 controls for brightness, exposure, gain, sharpness/noise suppression, and flip.

## Important APIs, Types, And Functions
Scripts include `preinit_s5k4aa`, `init_s5k4aa`, `VGA_s5k4aa`, and `SXGA_s5k4aa`, using `BRIDGE`, `SENSOR`, and `SENSOR_LONG` commands. `s5k4aa_vflip_dmi_table` lists systems needing physical orientation compensation. Public callbacks are `s5k4aa_probe()`, `s5k4aa_start()`, `s5k4aa_init()`, `s5k4aa_init_controls()`, and `s5k4aa_disconnect()`. Control helpers write page 2 exposure, read-mode flip bits, gain, brightness, and noise suppression.

## Control Flow
Probe optionally honors `force_sensor`, runs preinit, then reads three two-byte register pairs and compares them with an expected six-byte ID. Init performs bridge/GPIO/clock setup and several page-map sensor writes, then optionally dumps all pages. Start chooses the SXGA or VGA script based on current width, programming bridge frame timing and sensor crop/skip/window/blanking values. Flip control sets page 2, updates read-mode H/V flip bits with DMI inversion if needed, and adjusts row/column start low bits to keep alignment.

## State, Persistence, And Dependencies
State is held in GSPCA mode/control structures and DMI match results. Sensor page map and page-2 registers persist in hardware. Dependencies include two-byte M5602 sensor writes for some commands, one-byte writes for many page registers, DMI, V4L2 controls, and M5602 bridge timing registers.

## Integration Points
The header descriptor uses slave ID `0x5a`, register width `2`, and no stop callback. The mode table registers 640x480 and 1280x1024 `V4L2_PIX_FMT_SBGGR8` formats.

## Risks
The script executor sometimes ignores intermediate errors until after full mode script completion, so later writes may run after a failure. The descriptor declares two-byte register width while many helper paths deliberately write length 1, so core validation and command construction must be preserved. DMI flip compensation changes both flip bits and row/column offsets. The register dump scans 16 pages and writes test values, which is dangerous outside diagnostics.

## Test Signals
Six-byte ID detection, both VGA and SXGA stream alignment, DMI and non-DMI flip behavior, page-map restoration after dumps, brightness/exposure/gain/noise controls, stream restart after mode changes, and injected failures in `SENSOR_LONG` writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_s5k4aa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_s5k4aa.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_s5k4aa.h

## Purpose
`m5602_s5k4aa.h` defines S5K4AA page/register constants, read-mode bit masks, defaults, callback prototypes, and the static M5602 sensor descriptor.

## Important APIs, Types, And Functions
The header names `S5K4AA_PAGE_MAP`, page constants 0-2, page-2 geometry/exposure/gain/brightness/noise registers, row/column skip bits, H/V flip bits, and default gain/brightness values. It declares S5K4AA callbacks and instantiates `s5k4aa`.

## Control Flow
No runtime flow exists. The descriptor registers the backend with slave ID `0x5a`, register width `2`, and probe/init/control/start/disconnect callbacks.

## State, Persistence, And Dependencies
No mutable state. It depends on Linux DMI declarations and `m5602_sensor.h`. Page-map constants and read-mode flags represent persistent sensor register state.

## Integration Points
Included by the core sensor list and the S5K4AA implementation. The DMI include supports the implementation's orientation quirk table.

## Risks
The two-byte register-width descriptor must remain compatible with one-byte helper writes in the C file. Some register names carry uncertainty comments, so controls such as brightness and gain may map to empirically identified hardware behavior rather than fully documented semantics.

## Test Signals
Build/link callback coverage, correct slave ID and register-width behavior in traces, page 2 writes for controls, and mode script validation for VGA/SXGA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_s5k4aa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_s5k83a.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_s5k83a.c

## Purpose
`m5602_s5k83a.c` implements the Samsung S5K83A sensor backend for M5602 webcams. It configures a VGA Bayer stream, controls LED indication, polls a GPIO-based rotation sensor in a kernel thread, and exposes brightness, exposure, gain, and flip controls.

## Important APIs, Types, And Functions
Register scripts are `preinit_s5k83a`, `init_s5k83a`, and `start_s5k83a`. Public callbacks are `s5k83a_probe()`, `s5k83a_init()`, `s5k83a_init_controls()`, `s5k83a_start()`, `s5k83a_stop()`, and `s5k83a_disconnect()`. `rotation_thread_function()` polls `M5602_XB_GPIO_DAT`; helpers include `s5k83a_set_led_indication()`, `s5k83a_get_rotation()`, `s5k83a_set_flip_real()`, and setters for gain, brightness, exposure, and clustered flip.

## Control Flow
Probe runs preinit unless forced, reads registers `0x00` and `0x01`, and accepts any pair not equal to `0xff`. Init runs bridge and page-map writes required especially after resume. Start creates the rotation polling thread, writes bridge timing for 640x480, and turns the LED on. The thread sleeps in 100 ms intervals, takes `usb_lock`, reads the rotation GPIO, and rewrites flip registers when orientation changes; on exit it restores the user-requested front orientation. Stop halts the thread and turns the LED off. Controls no-op until streaming.

## State, Persistence, And Dependencies
State includes V4L2 control pointers and `sd->rotation_thread`; hardware state includes GPIO data, LED bit, page-map, flip/tune registers, exposure, brightness, and gain. Dependencies include Linux kthreads, `usb_lock`, M5602 bridge reads/writes, two-byte sensor access, and GSPCA streaming state.

## Integration Points
The header descriptor uses slave ID `0x5a`, two-byte register width, and supplies both start and stop hooks. The core's stop path calls `s5k83a_stop()` before the generic bridge stream is shut down.

## Risks
If `s5k83a_start()` starts the rotation thread and then a later register write fails, the error path returns without stopping the thread. Probe identification is weak because it only rejects `0xff` bytes. The rotation thread sets `sd->rotation_thread = NULL` itself while stop/disconnect can race conceptually around kthread lifetime. Gain programming is marked FIXME and empirically derived.

## Test Signals
Probe on real S5K83A hardware, start failure injection after thread creation, LED on/off writes, rotation GPIO transitions while streaming, stop/disconnect with active thread, clustered H/V flip behavior, and suspend/resume init sequence coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_s5k83a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_s5k83a.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_s5k83a.h

## Purpose
`m5602_s5k83a.h` defines S5K83A register addresses, default controls, GPIO masks, callback prototypes, and the static M5602 sensor descriptor.

## Important APIs, Types, And Functions
The header names flip/tuning, brightness, exposure, gain, and page-map registers; default gain/brightness/exposure and maximum exposure; flip, LED, and rotation GPIO masks. It declares probe/init/control/start/stop/disconnect callbacks and instantiates `s5k83a`.

## Control Flow
There is no executable flow. The descriptor binds name `S5K83A`, slave ID `0x5a`, register width `2`, and all lifecycle callbacks including stop.

## State, Persistence, And Dependencies
No local mutable state. It depends on `m5602_sensor.h`. The GPIO masks describe persistent bridge GPIO bits used by LED and rotation handling.

## Integration Points
Included by `m5602_core.c` and `m5602_s5k83a.c`. The descriptor makes this backend available to the core probe sequence.

## Risks
The same I2C slave ID as S5K4AA means probe order and ID strength matter. The register-width descriptor must match two-byte writes in probe/start/control sequences. GPIO masks are bridge-specific and wrong values would invert LED or rotation behavior.

## Test Signals
Build, descriptor callback dispatch, LED/rotation GPIO bit validation, S5K83A probe after other sensors fail, and correct stop callback invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_s5k83a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_sensor.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_sensor.h

## Purpose
`m5602_sensor.h` defines the common sensor interface used by all ALi M5602 sensor backends. It centralizes private V4L2 control IDs, sensor enum values used by `force_sensor`, register-script instruction types, and the callback vtable.

## Important APIs, Types, And Functions
Private controls are `M5602_V4L2_CID_GREEN_BALANCE` and `M5602_V4L2_CID_NOISE_SUPPRESION`. `enum sensors` assigns force IDs for OV9650, S5K83A, S5K4AA, MT9M111, PO1030, and OV7660. `enum instruction` defines `BRIDGE`, `SENSOR`, and `SENSOR_LONG` script entries. `struct m5602_sensor` contains name, I2C slave ID, register width, and optional lifecycle callbacks.

## Control Flow
No executable logic exists. `m5602_core.c` stores a pointer to one `struct m5602_sensor`, calls `probe()` candidates until one succeeds, then delegates init, control setup, start, stop, and disconnect through this vtable.

## State, Persistence, And Dependencies
The header has no mutable state. It depends on `m5602_bridge.h`, which defines `struct sd`, bridge registers, and the M5602 USB/I2C helper prototypes. The `i2c_regW` field directly controls core sensor read/write validation and protocol construction.

## Integration Points
Every sensor-specific header includes this file and then defines a static descriptor. V4L2 controls in sensor implementations store pointers in `struct sd` and share private control IDs from here.

## Risks
The enum values are user-facing through the `force_sensor` module parameter, so renumbering would break diagnostics and scripts. Callback pointers can be NULL for optional operations, so the core must guard them. `SENSOR_LONG` support is implemented only in some sensor script loops, not in the generic core.

## Test Signals
Compile all sensor backends, verify `force_sensor` values documented by the module match enum values, exercise NULL optional callbacks, and validate one-byte versus two-byte register-width enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_sensor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/mars.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/mars.c

## Purpose
`mars.c` is a standalone GSPCA subdriver for Mars-Semi MR97311A JPEG webcams, binding USB ID `093a:050f`. It configures the bridge and MI sensor, builds JPEG headers, exposes image and illuminator controls, and detects frame starts in the device's JPEG payload stream.

## Important APIs, Types, And Functions
`struct sd` extends `gspca_dev` with brightness, saturation, sharpness, gamma, two illuminator controls, and a cached JPEG header. USB helpers are `reg_w()` for bulk endpoint 4 writes and `mi_w()` for MI sensor writes. Control setters write bridge registers for brightness, color, gamma, sharpness, and illuminators. GSPCA callbacks are `sd_config()`, `sd_init()`, `sd_init_controls()`, `sd_start()`, `sd_stopN()`, and `sd_pkt_scan()`.

## Control Flow
Probe registers two JPEG modes, 320x240 and 640x480. Start generates a JPEG 4:2:2 header at fixed quality, writes bridge dimensions and compression/frame-size registers, applies current gamma/saturation/brightness/sharpness, initializes 32 MI sensor registers, enables isochronous transfer, and applies illuminator state. Control changes are ignored while stopped except the clustered illuminator values are kept mutually exclusive. Packet scanning searches for `ff ff 00 ff 96 64..67`, ends the previous frame, inserts the cached JPEG header as the first packet, skips a 16-byte device header, and appends the remaining data.

## State, Persistence, And Dependencies
State is in V4L2 controls and `jpeg_hdr`. Hardware state is volatile bridge/sensor register programming. Dependencies include GSPCA, `jpeg.h`, USB bulk endpoint 4, V4L2 illuminator controls, and the device's marker format.

## Integration Points
The `sd_desc` hooks integrate with GSPCA and standard PM helpers. The output format is `V4L2_PIX_FMT_JPEG`, and the driver supplies JPEG headers because the device stream carries frame data without a complete standard header at each SOF.

## Risks
`reg_w()` records only the first USB error in `usb_err`, so later writes are skipped until the caller resets it. Packet scanning always appends an `INTER_PACKET` even if no SOF was found, relying on GSPCA frame state. Illuminator mutual exclusion mutates peer control values manually and depends on cluster/update semantics. The start script is mostly trace-derived magic constants.

## Test Signals
USB probe on `093a:050f`, both JPEG modes, JPEG header validity, SOF detection with split/offset markers, controls during active streaming, illuminator exclusivity and stop-time off command, and bulk-write failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/mars.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/mr97310a.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/mr97310a.c

## Purpose
`mr97310a.c` is a standalone GSPCA subdriver for Mars-Semi MR97310A CIF and VGA still/video cameras. It detects camera and sensor variants sharing USB IDs, initializes variant-specific register tables, exposes only applicable controls, and frames the proprietary `V4L2_PIX_FMT_MR97310A` stream.

## Important APIs, Types, And Functions
`struct sd` tracks exposure/min-clockdiv controls, SOF detection state, camera type, sensor type, LCD-stop requirement, and color-adjustment quirk. USB helpers are `mr_write()`, `mr_read()`, `sensor_write_reg()`, `sensor_write_regs()`, `sensor_write1()`, `cam_get_response16()`, `zero_the_pointer()`, `stream_start()`, `stream_stop()`, `lcd_stop()`, and `isoc_enable()`. Variant setup is split between `start_cif_cam()` and `start_vga_cam()`. Controls are implemented by `setbrightness()`, `setexposure()`, `setgain()`, and `setcontrast()`.

## Control Flow
Probe sets all modes, zeros the device memory pointer, temporarily starts streaming, reads register `0x07` to classify CIF/VGA and sensor subtype, adjusts mode count for CIF devices, handles quirks such as Sakar color adjustment and Argus LCD stop, then stops streaming. Start repeats pointer reset, starts streaming, runs CIF or VGA startup tables based on `cam_type`/`sensor_type` and selected resolution, then enables isochronous transfer. Stop stops streaming, zeros the pointer again, and optionally sends LCD stop. Packet scanning uses `pac_find_sof()`, closes the previous frame before the PAC marker, starts the next frame with `pac_sof_marker`, and appends remaining data.

## State, Persistence, And Dependencies
State lives in `struct sd` and in V4L2 controls chosen dynamically by camera subtype. Hardware state includes a memory pointer, bridge stream bit, sensor registers, LCD state, exposure/gain/color settings, and isochronous enable. Dependencies include GSPCA, `pac_common.h`, USB bulk endpoints 3 and 4, and the MR97310A variant ID behavior.

## Integration Points
The USB table covers Trust, Aiptek, Pixart/Mars, and other MR97310A IDs. `sd_init_controls()` creates different control sets for CIF sensor 0/1, VGA sensor 0/1/2, Argus QuickClix, and Sakar CyberPix. The custom `MR97310A_CID_CLOCKDIV` clusters with exposure on devices needing minimum frame clock control.

## Risks
Probe performs real stream start/stop and can leave hardware in a partial state on failure. `force_sensor_type` coerces only boolean sensor types and cannot represent VGA sensor type 2 cleanly. Many register tables are empirical and variant-specific; wrong classification may produce no stream or bad colors. `sd_s_ctrl()` has no default error for unknown controls, relying on V4L2 to send only created controls. Pointer-zeroing loops can take many USB transactions and report status without failing if final status is unexpected.

## Test Signals
Probe all listed USB IDs and subtypes, forced sensor parameter behavior, CIF/VGA mode availability, start/stop pointer reset, PAC SOF framing across packet boundaries, exposure/min-clockdiv cluster math, Argus brightness lookup, Sakar color adjustment, LCD stop quirk, and USB bulk error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/mr97310a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/nw80x.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/nw80x.c

## Purpose
`nw80x.c` is a standalone GSPCA subdriver for DivIO NW800/NW801/NW802 and related ET31x110 webcams. It autodetects bridge generation, selects one of many webcam-specific register scripts, supports a module parameter for webcam type, handles optional auto-exposure/gain, and frames JPGL-like compressed packets.

## Important APIs, Types, And Functions
`struct sd` tracks auto-exposure window size, autogain countdown, exposure high/low counters, bridge generation, and webcam subtype. `enum bridges` and `enum webcams` classify supported hardware; `webcam_chip[]` maps subtypes to bridge generations; `webcam_start[]` selects large register scripts. USB helpers are `reg_w()`, `reg_r()`, `i2c_w()`, `reg_w_buf()`, `nw802_test_reg()`, and `swap_bits()`. Controls use `setgain()`, `setexposure()`, `setautogain()`, `do_autogain()`, and `sd_s_ctrl()`.

## Control Flow
Probe clamps the `webcam` module parameter, marks full bandwidth, initializes autogain off, and detects bridge generation by probing register writability: missing `0x0500` implies NW802, missing `0x109b` implies NW801, otherwise NW800/ET31x110. For `06a5:d800`, GPIO bits refine ET31x110 sensor subtype. The selected subtype must match the detected bridge. Config then chooses CIF or VGA mode tables and available mode count. Init runs any bridge-specific init script. Start runs the base subtype script plus resolution-specific additions for P35u, Kr651us, or Proscope. Packet scan treats an eight-byte `00 00 hh ww ss xx ff ff` header as a new frame and strips it.

## State, Persistence, And Dependencies
State is in `struct sd`, GSPCA controls, and volatile bridge/sensor registers. `reg_w_buf()` interprets script records as big-endian register plus length plus data, with special `I2C0` records routed through bridge I2C. Autogain persists across dequeued frames through `ag_cnt` and `ae_res`. Dependencies include GSPCA, USB vendor control messages, V4L2 auto clusters, and GSPCA exposure/autogain helper algorithms.

## Integration Points
The USB table covers Logitech, DVC, EZCam, Mustek, DivIO, Trust, and AVerMedia-style IDs. Module parameter `webcam` can override subtype selection. `sd_desc` includes `.dq_callback = do_autogain`, so exposure/gain adjustment is tied to frame dequeue rather than packet receipt.

## Risks
The register scripts are large opaque hardware traces; small edits can break specific models. Bridge detection writes test values to hardware registers during probe. Several USB IDs map to many possible webcams, so `webcam` override may be required and mismatches return `-ENODEV`. `sd_pkt_scan()` assumes `len >= 8` before reading header bytes and relies on GSPCA packet sizing. Autogain reads luma registers and divides by `ae_res`; fallback protects zero window size, but wrong AE window registers skew control feedback.

## Test Signals
Probe NW800/NW801/NW802 hardware, subtype overrides, ET31x110 GPIO detection, CIF/VGA mode selection, start scripts for P35u/Kr651us/Proscope at both resolutions, LED-off stop writes, packet header framing with short packets, autogain convergence from `dq_callback`, and USB control error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/nw80x.c -->
