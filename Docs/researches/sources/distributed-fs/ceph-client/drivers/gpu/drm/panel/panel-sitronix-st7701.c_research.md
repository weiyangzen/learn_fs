# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-sitronix-st7701.c

## Purpose
This driver supports panels based on the Sitronix ST7701 controller, with both MIPI DSI and SPI/DBI transport variants. It presents the panel through `drm_panel`, advertises fixed modes for specific compatible strings, programs ST7701 command-bank registers, and sequences regulators, reset GPIO, display on/off, and sleep state.

## Important APIs, Types, And Functions
The main data model is `struct st7701`, which owns `struct drm_panel`, optional `mipi_dsi_device`, `mipi_dbi`, two supplies (`VCC`, `IOVCC`), reset GPIO, orientation, and a transport-specific `write_command` callback. `struct st7701_panel_desc` holds the fixed mode, DSI lane/format data, panel sleep delay, gamma and power tuning fields, and an optional `gip_sequence`.

Key helpers are `st7701_dsi_write()`, `st7701_dbi_write()`, `st7701_switch_cmd_bkx()`, `st7701_vgls_map()`, and `st7701_init_sequence()`. Panel operations are `st7701_prepare()`, `st7701_enable()`, `st7701_disable()`, `st7701_unprepare()`, `st7701_get_modes()`, and `st7701_get_orientation()`. Probe is shared through `st7701_probe()`, then specialized by `st7701_dsi_probe()` and `st7701_spi_probe()`.

## Control Flow
Probe allocates a managed panel, fetches descriptor data from OF match data, gets regulators and reset GPIO, reads panel orientation, derives sleep delay as 120 ms plus descriptor extra delay, wires OF backlight support, adds the panel, and registers a managed cleanup action. DSI probe selects DSI connector type, validates that the descriptor has lanes, sets video burst/LPM/non-continuous mode flags, and attaches to the DSI host. SPI probe selects DPI connector type, initializes `mipi_dbi` from SPI plus optional D/C GPIO, and disables DBI reads.

Prepare enables supplies, toggles reset, runs the generic ST7701 initialization sequence, applies optional GIP commands, and returns to command set 1. Enable and disable send `MIPI_DCS_SET_DISPLAY_ON/OFF`. Unprepare sends sleep-in, waits for the panel-specific sleep delay, asserts reset, waits again, and disables regulators.

## State And Persistence
Runtime state is in `struct st7701`; descriptor constants are immutable per compatible string. There is no persistent storage. The only retained dynamic state is transport selection, `sleep_delay`, orientation, and panel lifecycle state tracked by DRM. `prepare_prev_first` is set so bridge/pipeline ordering prepares the panel before previous components where required.

## Dependencies And Integration Points
The driver integrates with DRM panel core, MIPI DSI, MIPI DBI/SPI, regulator, GPIO, device tree OF match data, `drm_panel_of_backlight()`, and orientation helpers. It registers one DSI driver and one SPI driver in the same module init/exit path, guarded by `CONFIG_DRM_MIPI_DSI` and `CONFIG_SPI`.

## Risks
The ST7701 command data is highly panel-specific and mostly not self-validating; incorrect descriptor voltages, gamma arrays, or GIP sequences can produce blank panels or image artifacts. `ST7701_WRITE` ignores command return values, so many initialization failures are not propagated. SPI and DSI share setup but differ in command transport and connector type, so adding a panel to the wrong OF match table can fail late. Sleep/reset delays are conservative but undocumented for some panels.

## Test Signals
Useful validation is successful probe/attach, regulator and GPIO acquisition, backlight binding, correct single fixed mode from `get_modes()`, correct orientation propagation, and a hardware smoke test of prepare/enable/disable/unprepare. For new descriptors, test both boot-from-off and bootloader-left-on cases, and verify panel-specific GIP/gamma behavior visually.
