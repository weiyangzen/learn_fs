# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/sdi.c

## Purpose
`sdi.c` implements the OMAP DSS Serial Display Interface output driver. It registers an SDI output, calculates clocks, configures the LCD manager for SDI, controls the SDI regulator and DISPC runtime state, handles DT datapair parsing, and exposes SDI ops to display devices.

## Important APIs, types, and functions
The file centers on the global `sdi` state. Important functions are `sdi_calc_clock_div`, `sdi_config_lcd_manager`, `sdi_display_enable`, `sdi_display_disable`, timing get/set/check, `sdi_set_datapairs`, `sdi_connect`, `sdi_disconnect`, output init/uninit, component bind/unbind, platform driver init/uninit, `sdi_init_port`, and `sdi_uninit_port`.

## Control Flow
Enable validates a connected manager, enables the SDI regulator and DISPC runtime, forces SDI signal edges, searches DSS/DISPC divisors with gradually widened pixel-clock tolerance, updates the requested pixel clock if only an approximate value is found, sets manager timings and DSS fclk, writes LCD manager config and divisors early for pck-free, initializes/enables the SDI block, delays 2 ms, then enables the manager. Disable reverses manager, SDI block, DISPC runtime, and regulator. Connect obtains regulator and binds manager/output to the destination display.

## State and Persistence
Runtime state includes platform device, regulator pointer, LCD manager config, timings, datapairs, output object, and `port_initialized`. Hardware state is in DSS SDI, DISPC manager, clock, and regulator state. Nothing persists across driver unload.

## Dependencies and Integration Points
It depends on component framework, OF graph endpoints, regulator APIs, DSS clock/divider helpers, DISPC runtime and manager APIs, and output registration.

## Risks
Global singleton state assumes one SDI output. Clock calculation may alter `timings->pixelclock`, which callers must tolerate. Error paths must balance regulator and DISPC runtime. `sdi_uninit_port` does not clear `port_initialized`. DT endpoint parsing requires `datapairs`.

## Test Signals
Test OMAP3 SDI output registration, DT datapairs parsing, exact and approximate pixel clocks, regulator/runtime failure unwinds, pck-free divider programming, enable/disable cycles, invalid timings, connect/disconnect while display enabled, and datapair changes.
