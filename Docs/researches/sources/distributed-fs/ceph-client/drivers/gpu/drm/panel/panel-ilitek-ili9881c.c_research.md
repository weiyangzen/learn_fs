# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9881c.c

## Purpose

This is a DRM panel driver for MIPI DSI panels built around the Ilitek ILI9881C controller. It supports several board and panel compatibles through descriptor records that select a fixed display mode, DSI mode flags, lane count, an optional default address mode, and a panel-specific vendor initialization table. The driver is not a generic runtime-configurable panel stack; almost all panel variance is encoded in static command arrays and OF match data.

## Important APIs, Types, And Functions

- `struct ili9881c_instr` models the panel init script as either `ILI9881C_SWITCH_PAGE` or `ILI9881C_COMMAND`.
- `struct ili9881c_desc` binds an init script, default mode, DSI flags, address mode, and lane count to one compatible.
- `struct ili9881c` stores the `drm_panel`, attached `mipi_dsi_device`, descriptor, `power` regulator, optional reset GPIO, orientation, and computed DCS address mode.
- `ili9881c_prepare()` enables power, resets the panel, replays the descriptor init table, returns to page 0, programs optional address mode, enables tearing, exits sleep, and turns the display on.
- `ili9881c_unprepare()` sends display off and sleep mode, disables power, and asserts reset.
- `ili9881c_get_modes()` duplicates the descriptor mode, marks it preferred, fills size/subpixel order, and propagates panel orientation.
- `ili9881c_dsi_probe()` allocates and registers the panel, gets regulator/reset/backlight resources, reads orientation, configures DSI settings, and attaches to the host.

## Control Flow

Probe is driven by the MIPI DSI bus and `ili9881c_of_match`. The match data selects descriptors for compatibles such as `bananapi,lhr050h41`, `bestar,bsd1218-a101kl68`, `feixin,k101-im2byl02`, `startek,kd050hdfia020`, `tdo,tl050hdv35`, `wanchanglong,w552946aaa`, `wanchanglong,w552946aba`, `ampire,am8001280g`, `raspberrypi,dsi-5inch`, and `raspberrypi,dsi-7inch`. Prepare powers and resets the panel, iterates the selected static init array, and sends common DCS startup commands. Mode enumeration is fixed and does not read hardware.

## State And Persistence

There is no persistent storage, runtime calibration, EDID, or NVM handling. Driver state is in memory only and rebuilt on probe. The panel controller's volatile register state is reprogrammed on each prepare. `orientation` comes from device tree, while `address_mode` is descriptor-derived and adjusted for bottom-up orientation.

## Dependencies And Integration Points

The driver integrates with DRM panel, MIPI DSI helpers, OF match data, regulators, GPIO descriptors, and optional DRM backlight lookup. Connector integration occurs through `get_modes()` and `get_orientation()`. `prepare_prev_first = true` affects bridge sequencing.

## Risks

Descriptor accuracy is the main risk: register values, lane count, DSI flags, and delays are panel-specific. Several descriptors omit `.lanes`, which should be checked before modifying those entries. Prepare error unwinding disables power but does not assert reset. Unprepare ignores accumulated DSI errors. Orientation handling rewrites bottom-up to normal by flipping address-mode bits, so rotation changes need hardware verification.

## Test Signals

Validate DSI attach, regulator/reset sequencing, one preferred mode with expected resolution and size, correct subpixel order/orientation, backlight binding, and repeated enable/disable and suspend/resume cycles on each compatible.
