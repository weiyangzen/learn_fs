# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/csi.c

## Purpose
Implements the Tegra CSI host1x client and V4L2 subdevice layer, including endpoint parsing, TPG pad operations, runtime power, MIPI calibration sequencing, CSI stream-on/off, and channel lifecycle.

## Important APIs, Types, And Functions
TPG-only pad ops include `csi_enum_bus_code()`, `csi_enum_framesizes()`, `csi_enum_frameintervals()`, `csi_get_format()`, `csi_set_format()`, and `tegra_csi_get_frame_interval()`. `tegra_csi_calc_settle_time()` derives D-PHY settle timings from CIL clock and source pixel rate. `tegra_csi_enable_stream()` powers CSI, enables/calibrates MIPI pads, starts CSI hardware, then starts the source subdev for real sensors. `tegra_csi_disable_stream()` reverses source, hardware, MIPI, and runtime PM. Channel allocation/init functions parse DT graph channels and lane counts or synthesize TPG channels. Probe maps registers, gets clocks/regulator, adds optional MIPI provider ops, enables PM runtime, and registers as host1x client.

## Control Flow
Platform probe prepares resources and host1x registration. Host1x init allocates CSI channels, initializes subdevices, and stores `vid->csi`. On stream-on, VI calls the CSI subdev `s_stream`; CSI resumes PM, handles MIPI calibration around sensor stream-on, delegates hardware programming to SoC ops, and unwinds on error. Error recovery stops CSI, calls SoC recovery, and restarts.

## State And Persistence
Runtime state lives in `struct tegra_csi` and per-channel `struct tegra_csi_channel`: active format, blanking/framerate, pixel rate, MIPI handle, lane/gang-port mapping, and list membership. No persistent storage.

## Dependencies And Integration Points
Depends on host1x, runtime PM, clock bulk APIs, regulator `avdd-dsi-csi`, Tegra MIPI calibration, V4L2 fwnode/async/media, and SoC ops from `tegra20.c` or `tegra210.c`. Integrates with VI via subdev hostdata and `tegra_channel_get_remote_*` helpers.

## Risks And Test Signals
Lane validation, ganged-port mapping, PM unwind, and MIPI calibration ordering are high-risk. `csi_set_format()` uses nearest-size logic for TPG and should be checked for width/height argument correctness. Test signals include DT graph parsing, 2-lane/4-lane/ganged stream start, TPG format/framerate enumeration, MIPI calibration success/failure, runtime PM refcount balance, and recovery after CSI errors.
