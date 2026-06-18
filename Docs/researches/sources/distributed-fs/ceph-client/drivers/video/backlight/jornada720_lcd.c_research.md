# sources/distributed-fs/ceph-client/drivers/video/backlight/jornada720_lcd.c

## Purpose
This platform driver controls LCD power and contrast for HP Jornada 700-series devices through PPC GPIO bits and the Jornada SSP microcontroller.

## Important APIs, Types, and Functions
`jornada_lcd_get_power()` reads PPC bit `PPC_LDD2`. `jornada_lcd_get_contrast()` and `jornada_lcd_set_contrast()` issue `GETCONTRAST`/`SETCONTRAST` SSP commands and validate `TXDUMMY`. `jornada_lcd_set_power()` toggles `PPC_LDD2`. The `lcd_ops` table supplies power and contrast callbacks.

## Control Flow
Probe registers an LCD device named `S1D_DEVICENAME`, stores it as platform data, sets default contrast `0x80`, powers the LCD on, and waits 100 ms. Sysfs operations through the LCD class call the contrast and power callbacks directly.

## State and Persistence
No private state is kept. Power state is the PPC output bit; contrast is held by the microcontroller. There is no software cache.

## Dependencies and Integration Points
The driver depends on Jornada platform register macros, SSP helpers, the LCD class, and the S1D framebuffer device name. It complements the separate Jornada backlight driver.

## Risks
SSP errors surface as `-ETIMEDOUT`, but direct power bit writes always return success. Contrast reads return zero when the LCD is off, which is a policy choice rather than a hardware contrast value. Direct PPC register access assumes board exclusivity.

## Test Signals
Test probe defaults, sysfs `lcd_power`, sysfs `contrast`, SSP timeout handling, power off returning contrast zero, and coexistence with the Jornada backlight driver.
