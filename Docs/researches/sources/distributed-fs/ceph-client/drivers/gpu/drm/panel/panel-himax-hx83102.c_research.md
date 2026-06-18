# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx83102.c

## Purpose

This driver supports several Himax HX83102 based MIPI DSI panels, mainly 1200x1920 tablet-class panels plus a 720x1600 Holitech panel. It maps each device-tree compatible string to an `hx83102_panel_desc` containing a fixed DRM mode, physical size, optional DCS backlight support, and a panel-specific initialization callback.

## Important APIs, Types, And Functions

`struct hx83102` owns the `drm_panel`, `mipi_dsi_device`, panel descriptor, orientation, regulators (`pp1800`, `avdd`, `avee`), and enable GPIO. `struct hx83102_panel_desc` describes mode/size/backlight/init data.

Panel lifecycle is implemented by `hx83102_prepare()`, `hx83102_enable()`, `hx83102_disable()`, and `hx83102_unprepare()`. `hx83102_get_modes()` duplicates the descriptor mode and fills connector display info. `hx83102_get_orientation()` returns the DT panel orientation. `hx83102_probe()` allocates the panel, configures 4-lane RGB888 video DSI with sync pulse and low-power command mode, registers the panel, and attaches to the DSI host.

The file contains vendor command definitions and several init callbacks: `starry_himax83102_j02_init()`, `boe_nv110wum_init()`, `csot_pna957qt1_1_init()`, `ivo_t109nw41_init()`, `kingdisplay_kd110n11_51ie_init()`, `starry_2082109qfh040022_50e_init()`, and `holitech_htf065h045_init()`. These callbacks use `mipi_dsi_multi_context` and `mipi_dsi_dcs_write_seq_multi()` to send long manufacturer command tables.

## Control Flow

Probe obtains match data, sets DSI bus parameters, calls `hx83102_panel_add()`, stores driver data, then calls `mipi_dsi_attach()`. `hx83102_panel_add()` obtains regulators and GPIO, reads orientation, binds a DT backlight if present, and creates a DCS backlight fallback only for descriptors with `has_backlight`.

Prepare holds the enable GPIO low, powers `pp1800`, then `avdd` and `avee`, sends a DCS NOP, toggles the enable GPIO through the panel reset sequence, calls the descriptor init callback, exits sleep, waits 120 ms, and turns the display on. Error paths disable supplies in reverse order. Disable clears LPM, sends display-off and sleep-in, restores LPM, and waits 150 ms. Unprepare disables the GPIO and supplies.

## State And Persistence

There is no persistent storage. Runtime state is the panel descriptor selected from OF match data, the current orientation, DSI mode flags, backlight brightness through DCS, regulator enable state, and enable GPIO level. Brightness state is held by the DRM backlight core and read/written with 12-bit DCS large brightness helpers.

## Dependencies And Integration Points

The driver depends on DRM panel, DRM connector modes, MIPI DSI helpers, `video/mipi_display.h`, regulator, GPIO, OF match data, and backlight APIs. It integrates with device tree compatibles for BOE, CSOT, IVO, Kingdisplay, Starry, and Holitech panels. It expects supplies named `avdd`, `avee`, and `pp1800`, an `enable` GPIO, and optional backlight/orientation properties.

## Risks

The largest risk is panel-specific command-table fragility: small byte changes can prevent bring-up or alter voltage, GIP, gamma, or MIPI timing behavior. `ctx->desc->init(ctx)` returns only the accumulated DSI write status, so semantic failures in a table are not detected. The fallback DCS backlight temporarily clears LPM, which must stay compatible with the host. Regulator sequencing and GPIO timing are tightly coupled to hardware. The generic init path assumes all descriptors work with the same 4-lane RGB888 sync-pulse video configuration.

## Test Signals

Useful validation includes successful module bind and `mipi_dsi_attach()`, absence of regulator/GPIO probe errors, a connector with the expected fixed mode and physical size, correct orientation from DT, visible image after prepare/enable, reliable suspend/resume through disable/unprepare/prepare, and working DCS brightness reads/writes on Holitech or other DCS-backlight variants.
