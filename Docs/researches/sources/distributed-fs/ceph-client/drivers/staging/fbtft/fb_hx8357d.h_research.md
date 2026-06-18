<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8357d.h -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8357d.h

Purpose: contains HX8357B/HX8357D command constants, geometry constants, and RGB565 color definitions used by the HX8357D FBTFT driver.

Important APIs/types/functions: defines command IDs such as `HX8357D_SETC`, `HX8357_SETRGB`, `HX8357D_SETCOM`, `HX8357_SETPWR1`, `HX8357D_SETSTBA`, `HX8357D_SETCYC`, and `HX8357D_SETGAMMA`.

Control flow: no executable code; inclusion lets `fb_hx8357d.c` use named constants instead of literal command bytes.

State and persistence: no state.

Dependencies and integration: private to the HX8357D driver but based on an Adafruit header with MIT license text.

Risks: contains constants for both B and D variants; using the wrong variant command in driver code can silently misconfigure hardware. Color constants are unused by the driver.

Test signals: compile the HX8357D driver and compare command values with the target controller datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8357d.h -->
