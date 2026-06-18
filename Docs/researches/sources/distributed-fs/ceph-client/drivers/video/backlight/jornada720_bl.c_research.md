# sources/distributed-fs/ceph-client/drivers/video/backlight/jornada720_bl.c

## Purpose
This platform driver controls HP Jornada 710/720/728 backlight brightness through the Jornada SSP microcontroller protocol and a PPC GPIO enable bit.

## Important APIs, Types, and Functions
`jornada_bl_get_brightness()` checks the PPC backlight enable bit, sends `GETBRIGHTNESS`, validates `TXDUMMY`, reads the value, and returns an inverted brightness. `jornada_bl_update_status()` turns hardware off when blanked, enables the PPC bit otherwise, sends `SETBRIGHTNESS`, and writes the inverted 0-255 value. `jornada_bl_ops` exposes get/update callbacks with `BL_CORE_SUSPENDRESUME`.

## Control Flow
Probe registers a raw backlight named `S1D_DEVICENAME`, sets power on and default brightness 25, applies the setting, and logs the driver banner. Runtime updates serialize SSP transactions with `jornada_ssp_start()`/`jornada_ssp_end()` and use timeout errors when the microcontroller handshake is not `TXDUMMY`.

## State and Persistence
There is no private state. Brightness lives in the microcontroller and backlight core properties. The PPC GPIO bit records whether the backlight is physically enabled.

## Dependencies and Integration Points
The driver depends on Jornada platform headers, direct PPC port macros, `video/s1d13xxxfb.h` for the device name, and the backlight core. It is paired with `jornada720_lcd.c` for LCD power/contrast.

## Risks
The inverted brightness mapping is hardware-specific and easy to misinterpret. Backlight-off handshake failure still clears the PPC bit and reports timeout. Direct global register manipulation assumes no competing owner.

## Test Signals
Test SSP success and timeout cases, blanking to off, brightness inversion, get when PPC bit is off, default probe update, and suspend/resume core calls.
