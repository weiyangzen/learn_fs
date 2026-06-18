# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/venc.c

## Purpose
`venc.c` implements the OMAP analog TV encoder output driver for PAL/NTSC composite and S-Video. It provides VENC register tables, exported PAL/NTSC timings, output registration, power/runtime/regulator handling, WSS support, DT channel parsing, debug dumps, and platform/component driver integration.

## Important APIs, types, and functions
Important data includes `struct venc_config`, `venc_config_pal_trm`, `venc_config_ntsc_trm`, exported `omap_dss_pal_timings`, `omap_dss_ntsc_timings`, and global `venc` state. Key functions are `venc_write_config`, `venc_reset`, runtime get/put, `venc_timings_to_config`, `venc_power_on/off`, display enable/disable, timing check/set/get, WSS get/set, type/polarity setters, `venc_connect`, `venc_disconnect`, `venc_probe_of`, `venc_bind/unbind`, runtime PM callbacks, and platform driver init/uninit.

## Control Flow
Bind maps VENC memory, gets optional TV DAC clock, enables runtime PM, reads revision, parses DT channel/polarity, creates debugfs, and registers output. Display enable locks `venc_lock`, runtime-resumes hardware, resets VENC, writes PAL/NTSC table plus WSS data, selects output type, enables DAC bias, writes output control, sets manager timings, enables regulator, and enables the manager. Disable clears output control and DAC bias, disables manager, regulator, and runtime PM. WSS writes update cached data and the BSTAMP/WSS register under runtime PM.

## State and Persistence
Global runtime state includes mapped base, mutex, WSS data, regulator, optional TV DAC clock, timings, output type, polarity, platform device, and output object. Hardware state lives in VENC registers, DAC control, manager timings, and regulator/clock state.

## Dependencies and Integration Points
The file depends on DSS feature flags, DISPC runtime through VENC runtime PM, regulator and clock APIs, OF graph parsing, component framework, output/manager APIs, and debugfs.

## Risks
`venc_timings_to_config` calls `BUG()` for unsupported timings, so callers must use `venc_check_timings`. `venc_probe_of` returns 0 even on invalid DT parse in its error path, potentially masking bad channel data. Runtime suspend disables `tv_dac_clk` even if NULL, relying on clock helpers. PAL/NTSC comparisons require exact struct matches.

## Test Signals
Test PAL and NTSC enable, rejection of non-TV timings, composite versus S-Video DT channels, polarity inversion, WSS set/get across standard changes, runtime PM suspend/resume, missing regulator/clock resources, reset timeout behavior, debugfs dumps, and manager/regulator failure unwinds.
