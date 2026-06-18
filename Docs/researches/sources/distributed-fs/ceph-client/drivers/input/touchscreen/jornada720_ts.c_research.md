<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/jornada720_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/jornada720_ts.c

Purpose: platform input driver for HP Jornada 710/720/728 touchscreens. It uses Jornada-specific SSP helper routines and a pen-up GPIO interrupt to sample three X and Y readings, average them, and report a resistive single-touch input device.

Important APIs/types/functions: `struct jornada_ts` stores the input device, pen GPIO, and sample buffers. `jornada720_ts_collect_data()` reads the low and packed high bits for three X and three Y samples from `jornada_ssp_byte()`. `jornada720_ts_average()` reconstructs and averages three 10-bit samples. `jornada720_ts_interrupt()` handles pen-up/down detection and sampling. `jornada720_ts_probe()` sets up GPIO, IRQ, absolute ranges, and input registration.

Control flow: probe obtains the `penup` GPIO, maps it to an IRQ, allocates the input device, requests a rising-edge IRQ, and registers the device. On interrupt, a high GPIO means pen up and emits `BTN_TOUCH=0`. Otherwise the driver starts SSP, sends `GETTOUCHSAMPLES`, verifies the dummy reply, collects and averages samples, reports touch coordinates, then ends SSP.

State and persistence: state is only current sample arrays and GPIO/input handles. There is no saved calibration or firmware state; fixed min/max ranges encode expected board calibration.

Dependencies/integration: depends on `mach/jornada720.h` board APIs (`jornada_ssp_start`, `jornada_ssp_inout`, `jornada_ssp_byte`, `jornada_ssp_end`), GPIO consumer API, platform binding `jornada_ts`, and Linux input core.

Risks and test signals: this is tightly board-specific and assumes SSP serialization is handled by the Jornada helpers. Test pen-up GPIO polarity, rising-edge-only release IRQ behavior, SSP failure/dummy response mismatch, high-bit reconstruction, fixed axis ranges against calibration, repeated pen-down samples if no falling-edge IRQ is present, and module coldplug aliasing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/jornada720_ts.c -->
