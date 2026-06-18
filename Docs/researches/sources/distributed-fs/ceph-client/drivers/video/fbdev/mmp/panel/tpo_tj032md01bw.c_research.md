# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/panel/tpo_tj032md01bw.c

## Purpose
Implements an SPI-controlled TPO TJ032MD01BW HVGA active panel driver for the MMP display subsystem. It registers a panel, provides one 320x480 mode, and sends power-on/off command sequences over SPI.

## Important APIs, Types, and Functions
- `init[]` and `poweroff[]` are 16-bit command sequences sent to the panel.
- `struct tpohvga_plat_data` stores platform power callback and SPI device pointer.
- `tpohvga_onoff()` toggles platform power and writes init or poweroff SPI commands.
- `mmp_modes_tpohvga[]` defines a 320x480 60 Hz RGB565 output mode with 10.3944 MHz pixel clock.
- `tpohvga_get_modelist()` returns the static mode list.
- `panel_tpohvga` is the `struct mmp_panel` registered with the MMP core.
- `tpohvga_probe()` validates platform data, sets SPI word size to 16, allocates panel private data, fills panel fields, and calls `mmp_register_panel()`.

## Control Flow
SPI core probes devices named `tpo-hvga`. The driver requires `struct mmp_mach_panel_info` platform data containing path name and platform on/off callback. It configures 16-bit SPI words, stores the SPI device and callback, binds the panel to the platform path name, and registers it. When a display path powers on the panel, `tpohvga_onoff()` calls platform power on then sends the init array. Power off sends the poweroff command then calls platform power off.

## State and Persistence
The driver uses one static `panel_tpohvga` object and allocates one `tpohvga_plat_data` in probe. Panel mode and command arrays are static. There is no remove callback, so allocated panel data and registration are not released on device removal.

## Dependencies and Integration Points
Depends on Linux SPI, platform data from `<video/mmp_disp.h>`, and MMP core panel registration. It can use the LCD-controller SPI master from `mmp_spi.c` or another SPI host with matching platform device setup.

## Risks
The static panel object and no remove path make multiple panel instances or hot-unplug unsafe. `tpohvga_onoff()` assumes `plat_onoff` is valid. Power-on sequencing has no delay between platform power and SPI init besides what lower layers may provide. SPI write failures are warnings only, so path power state may proceed despite panel init failure.

## Test Signals
Validate SPI probe with missing and valid platform data, 16-bit `spi_setup()`, panel registration and path name matching, mode list retrieval, power-on command sequence, power-off command, and warning logs on SPI transfer failures.
