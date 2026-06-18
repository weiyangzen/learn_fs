# sources/distributed-fs/ceph-client/drivers/video/backlight/corgi_lcd.c

## Purpose
This SPI driver controls the LCD timing generator and backlight on Sharp Zaurus Corgi-family handhelds. It registers both an `lcd_device` for panel power and mode switching and a `backlight_device` for brightness.

## Important APIs, Types, and Functions
`struct corgi_lcd` holds the SPI device, LCD/backlight devices, current mode/power/intensity, optional `BL_ON` and `BL_CONT` GPIOs, and a platform battery callback. `corgi_ssp_lcdtg_send()` writes compact register/data values over SPI. `lcdtg_*` helpers bit-bang a write-only pseudo-I2C path through LCD timing generator registers to program common voltage. `corgi_lcd_power_on()` and `corgi_lcd_power_off()` implement the panel sequencing. `corgi_lcd_set_mode()` switches QVGA/VGA. `corgi_bl_update_status()` enforces suspend and low-battery limits before calling `corgi_bl_set_intensity()`. `corgi_lcd_limit_intensity()` is exported for battery policy code.

## Control Flow
Probe requires `struct corgi_lcd_platform_data`, allocates state, registers `corgi_lcd` and `corgi_bl`, obtains optional GPIOs, stores `kick_battery`, powers the LCD on, applies default brightness, then publishes the singleton `the_corgi_lcd`. LCD power transitions only execute when crossing the `POWER_IS_ON()` boundary. Mode changes update phase adjustment and resolution control. Suspend sets `CORGIBL_SUSPENDED`, forces intensity zero, and powers the panel off; resume reverses those steps.

## State and Persistence
State is volatile and partly global. `the_corgi_lcd` and `corgibl_flags` are file-scope globals, while per-device state records current intensity, mode, power, and limit mask. Hardware state is spread across the timing generator, GPIO lines, and the common-voltage DAC. There is no persistent storage.

## Dependencies and Integration Points
The driver depends on SPI, GPIO descriptors, the LCD/backlight core, Corgi platform data, and `sharpsl_param` for `comadj` and phase-adjust defaults. It integrates with external power management via `corgi_lcd_limit_intensity()` and optional `kick_battery()`.

## Risks
The singleton design assumes one device and makes `corgi_lcd_limit_intensity()` unsafe before successful probe. The pseudo-I2C path assumes writes are acknowledged because the bus is write-only. Register sequences are delay-sensitive and platform-data dependent. Brightness encoding mutates values above `0x10`, uses a GPIO for bit 5, and stores the translated intensity rather than the original user-visible value.

## Test Signals
Test probe without platform data, optional GPIO acquisition, QVGA/VGA mode changes, power on/off ordering, low-battery limiting, suspend/resume, exported intensity limiting after probe, and removal forcing brightness zero and panel power off.
