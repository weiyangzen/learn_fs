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
