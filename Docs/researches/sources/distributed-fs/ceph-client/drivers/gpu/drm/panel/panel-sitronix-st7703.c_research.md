# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sitronix-st7703.c

## Purpose
This is a DRM MIPI DSI panel driver for panels based on the Sitronix ST7703 controller and close clones. It provides fixed modes and panel-specific vendor initialization sequences for Rocktech, Xingbangda, Anbernic, Powkiddy, and GameForce panels.

## Important APIs, Types, And Functions
`struct st7703` stores the DRM panel, reset GPIO, `vcc` and `iovcc` regulators, debugfs root, descriptor, and orientation. `struct st7703_panel_desc` provides mode, lanes, mode flags, pixel format, and an `init_sequence()` callback. Each panel has a static init function such as `jh057n_init_sequence()`, `xbd599_init_sequence()`, `rg353v2_init_sequence()`, `rgb30panel_init_sequence()`, `rgb10max3_panel_init_sequence()`, and `gameforcechi_init_sequence()`.

The panel ops are `st7703_prepare()`, `st7703_enable()`, `st7703_disable()`, `st7703_unprepare()`, `st7703_get_modes()`, and `st7703_get_orientation()`. Debug support is exposed through `allpixelson_set()` and `st7703_debugfs_init()`.

## Control Flow
Probe allocates the panel, acquires reset GPIO, stores match descriptor data, configures the DSI device from the descriptor, fetches `vcc` and `iovcc`, reads orientation, binds an optional OF backlight, adds the panel, attaches to the DSI host, logs the resolved mode, and creates debugfs. Prepare asserts reset, enables `iovcc` then `vcc`, waits for stabilization, deasserts reset, and waits again. Enable executes the descriptor init sequence through `mipi_dsi_multi_context`, exits sleep, waits 120 ms, and turns the display on. Disable turns display off, enters sleep, and waits 120 ms. Unprepare asserts reset and disables regulators.

## State And Persistence
No persistent state is written. The descriptor and debugfs pointer are retained for the device lifetime. The debugfs `allpixelson` file temporarily drives all pixels on, sleeps for a caller-provided number of seconds, and then cycles the panel through disable/unprepare/prepare/enable to restore video.

## Dependencies And Integration Points
The driver uses DRM panel APIs, MIPI DSI multi-context helpers, regulator and GPIO frameworks, OF match data, media bus format reporting, orientation helpers, OF backlight binding, and debugfs. It is registered with `module_mipi_dsi_driver()`.

## Risks
Many command sequences are vendor-provided or for clone controllers, so parameter meanings are partly undocumented. The debugfs all-pixels-on operation assumes the panel was already on and intentionally power-cycles it, making it unsuitable as a general userspace interface. Get-modes reports a single RGB888 bus format for all descriptors, which should match host expectations. Failure paths around DSI attach remove the panel, while later managed resources are released by device core.

## Test Signals
Validation should confirm DSI attach, regulator sequencing, orientation, backlight binding, debugfs creation/removal, and a working fixed mode for each compatible. Hardware tests should include suspend-like disable/unprepare cycles and the debugfs all-pixels-on recovery path on a non-production setup.
