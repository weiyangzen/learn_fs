# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx8394.c

## Purpose

This driver supports several Himax HX8394 or closely related HX8399 MIPI DSI panels: HannStar HSD060BHW4, Huiling HL055FHAV028C, Powkiddy X55, and Microchip AC40T08A. It provides descriptor-driven DSI mode setup, fixed modes, orientation handling, and vendor initialization sequences.

## Important APIs, Types, And Functions

`struct hx8394` stores the device, DRM panel, reset GPIO, `vcc` and `iovcc` regulators, orientation, and descriptor. `struct hx8394_panel_desc` stores one mode, lane count, mode flags, pixel format, and an init sequence callback.

`hx8394_prepare()` controls reset and regulators. `hx8394_enable()` sends the descriptor init sequence, exits sleep, waits 120 ms, and turns display on. `hx8394_disable()` enters sleep mode. `hx8394_unprepare()` asserts reset and disables regulators. `hx8394_get_modes()` duplicates the descriptor mode and fills display info. `hx8394_probe()` reads orientation, supplies, optional backlight, descriptor data, and attaches the DSI device.

## Control Flow

Probe configures the DSI device from the matched descriptor before panel add and DSI attach. At runtime, prepare only establishes hardware power/reset state and waits 180 ms. Enable performs the command-table programming and display-on sequence. If display-on fails after sleep-out, the error path attempts to enter sleep mode. Disable and unprepare reverse those steps across DCS sleep and regulator shutdown.

## State And Persistence

There is no persistence. State is limited to descriptor data, regulator/reset state, panel orientation, and DSI host attachment. Backlight, when present in DT, is owned by the DRM panel framework rather than this file.

## Dependencies And Integration Points

The driver depends on DRM panel, MIPI DSI helpers, regulators, GPIO, OF match data, panel orientation, and optional panel backlight binding. Compatibles are `hannstar,hsd060bhw4`, `huiling,hl055fhav028c`, `powkiddy,x55-panel`, and `microchip,ac40t08a-mipi-panel`.

## Risks

Initialization is split across prepare and enable; hosts or bridges that expect panel programming during prepare may expose ordering issues. The HL055FHAV028C sequence is for an HX8399-related panel despite sharing this driver, so command meanings differ from HX8394 comments. The init tables include many undocumented commands and bank switches. `devm_gpiod_get_optional()` may return NULL, but reset operations call `gpiod_set_value_cansleep()` which tolerates NULL in gpiod APIs; this relies on that API contract.

## Test Signals

Confirm each compatible reports the expected fixed resolution, physical size, lane count, and DSI flags. Hardware tests should verify prepare/enable ordering, panel orientation, optional backlight discovery, visible image after sleep-out/display-on, and reliable suspend/resume with DCS sleep before regulators are disabled.
