# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/dvi.h

## Purpose
`dvi.h` defines DVI/TMDS constants and declares the DVI helper functions used by the VIA framebuffer driver.

## Important APIs, Types, And Data
Constants include VT1632 device ID register/value, panel-size source constants, DVI panel ID values, EDID version markers, and connection type flags for DVI/HDMI. Function declarations cover sensing, enable/disable, TMDS transmitter identification, panel-size initialization, and DVI mode programming.

## Control Flow
There is no executable control flow. `dvi.c` implements the declared functions and consumes the constants during transmitter detection and EDID parsing.

## State And Persistence
No state is stored here. The header defines stable constants that shape runtime state in `tmds_chip_information` and `tmds_setting_information`.

## Dependencies And Integration Points
The prototypes rely on structures declared in `chip.h`/`global.h` and on `struct fb_var_screeninfo` from fbdev headers included through the VIA global include chain. It integrates `dvi.c` with `hw.c` and other VIA display selection code.

## Risks
The typo `GET_DVI_SZIE_BY_HW_STRAPPING` is part of the local API spelling and can be propagated. Panel ID constants are narrow and do not describe arbitrary EDID modes. Any mismatch between this header and `dvi.c` would break the composite `viafb.o` build.

## Test Signals
Signals include clean compilation of all callers, correct VT1632 detection using the defined ID, and runtime paths that call each declared public function during DVI probe/sense/modeset.
