# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/atomisp-gc2235.c

## Purpose
Implements a V4L2 subdevice driver for the GalaxyCore GC2235 2MP raw camera sensor used with Intel AtomISP. It handles I2C register programming, power sequencing through AtomISP platform callbacks, exposure control, format/resolution selection, streaming, and sensor registration.

## Important APIs, Types, and Functions
Low-level I2C helpers include `gc2235_read_reg()`, `gc2235_i2c_write()`, `gc2235_write_reg()`, and buffered register-array helpers that coalesce consecutive writes and honor delay tokens. Exposure paths are `__gc2235_set_exposure()`, `gc2235_set_exposure()`, `gc2235_s_exposure()`, and `gc2235_q_exposure()`. Power helpers `power_ctrl()`, `gpio_ctrl()`, `power_up()`, and `power_down()` call platform callbacks. V4L2 operations include `gc2235_s_power()`, `gc2235_set_fmt()`, `gc2235_get_fmt()`, `gc2235_s_stream()`, frame size/code enumeration, frame interval, skip frames, volatile exposure control, and AtomISP private ioctl handling. Probe allocates `struct gc2235_device`, fetches GMIN platform data, configures/detects the sensor, initializes controls and media entity pads, then registers with AtomISP.

## Control Flow and State
Device state includes the selected resolution, media pad/format, control handler, platform data, and `input_lock`. A file-scope `is_init` flag controls whether startup power-cycles and reinitializes before resolution changes. `gc2235_s_config()` powers down, powers up, enables CSI, detects the sensor ID, then powers down after probe. `gc2235_set_fmt()` chooses the nearest preview resolution, stores it, and for active formats writes init/resolution registers. Streaming writes static stream-on/off register arrays.

## Dependencies and Integration Points
Depends on I2C, V4L2 subdev/media entity/control APIs, ACPI match `INT33F8`, AtomISP GMIN platform data, sensor-specific `gc2235.h` register tables, and AtomISP private exposure ioctl `ATOMISP_IOC_S_EXPOSURE`.

## Risks and Test Signals
Risks include global `is_init` across devices, inconsistent media bus code between set/get and enum paths, register write return values overwritten in exposure programming, platform callback failure handling, and tight coupling to AtomISP private APIs. Test signals include ACPI probe, power sequencing timing, sensor ID detection, register-array coalescing with delay tokens, exposure/gain boundary behavior, format negotiation for try and active states, stream on/off register writes, CSI cleanup on remove, volatile exposure readback, and skip-frame values per selected resolution.
