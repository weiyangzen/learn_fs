<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-feixin-k101-im2ba02.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-feixin-k101-im2ba02.c

### Purpose

`panel-feixin-k101-im2ba02.c` drives the Feixin K101 IM2BA02 MIPI-DSI LCD panel. It is a command-table based four-lane RGB888 video panel driver with three bulk regulators, reset GPIO control, a long page-based initialization table, a delayed display-on/TE enable step, and one fixed 800x1280 preferred mode.

### Important APIs, types, and functions

`struct k101_im2ba02` stores the DRM panel, DSI device, three bulk supplies (`dvdd`, `avdd`, `cvdd`), and reset GPIO. `struct k101_im2ba02_init_cmd` wraps two-byte command/data pairs. `k101_im2ba02_init_cmds` contains the long vendor sequence covering command pages, password/unlock values, lane count, VCOM, gamma power, gate power, panel/BGR configuration, TCON parameters, gamma tables, GIP configuration, and sleep-out. `timed_cmds` holds display-on and tear-on commands, though enable uses only the second entry after an explicit DCS display-on helper. DRM callbacks are `k101_im2ba02_prepare()`, `k101_im2ba02_enable()`, `k101_im2ba02_disable()`, `k101_im2ba02_unprepare()`, and `k101_im2ba02_get_modes()`.

### Control flow

Probe allocates state, assigns regulator bulk names, obtains regulators and reset GPIO, binds optional backlight, adds the panel, sets DSI video mode/RGB888/four lanes, and attaches. `prepare()` bulk-enables supplies, waits, toggles reset high-low-high with long settling delays, then iterates the complete two-byte init table using `mipi_dsi_dcs_write_buffer()`. If a command fails, it drives reset low, waits, and disables supplies. `enable()` waits 150 ms after prepare, sends DCS display-on, waits 50 ms, then sends the second timed command (`0x35, 0x00`) to enable tearing effect. `disable()` sends display-off. `unprepare()` sends display-off and sleep-in, waits 200 ms, drives reset low, waits, and disables all supplies.

### State and persistence behavior

There is no explicit software power state; the regulator bulk and reset GPIO encode hardware state. Vendor command state is volatile and rebuilt on each prepare. The fixed mode and init arrays are static. Backlight state is delegated to the DRM panel backlight helper. DSI errors in prepare stop the init loop and power down, while unprepare logs but ignores display-off/sleep-in failures before disabling rails.

### Dependencies

The driver depends on DRM panel/mode helpers, MIPI DSI DCS write helpers, Linux regulator bulk and GPIO APIs, OF match data, and `drm_panel_of_backlight()`. It expects a four-lane DSI host with RGB888 video mode support.

### Integration points

The compatible is `feixin,k101-im2ba02`. DTS must provide `dvdd`, `avdd`, `cvdd`, `reset`, and optional backlight. The connector gets one preferred 800x1280 mode at 70 MHz with 136 mm by 217 mm dimensions. Runtime integration follows the standard panel prepare/enable/disable/unprepare path.

### Risks

The initialization table is long and largely magic-number driven; accidental edits can change power, gamma, GIP, or lane behavior. `timed_cmds[0]` duplicates display-on but is unused, which can confuse maintenance. `prepare()` returns the result of regulator disable on the powerdown path rather than preserving the original DSI write error if disable succeeds, potentially hiding the real failure. Reset polarity and the 200 ms settling delay are critical. Any mismatch between the table lane command and DSI host lane count can cause link failure.

### Test signals

Validate probe and DSI attach, bulk regulator sequencing, reset waveform, failure unwinding from an injected DSI write error, mode enumeration, backlight binding, display-on plus tear-on behavior, repeated suspend/resume, and visual checks for gamma/GIP correctness across the whole panel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-feixin-k101-im2ba02.c -->
