# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/global.c

## Purpose
`global.c` defines the VIA framebuffer driver's cross-file global configuration and object pointers.

## Important APIs, Types, And Data
It defines display layout and feature globals such as `viafb_platform_epia_dvi`, `viafb_device_lcd_dualedge`, `viafb_bus_width`, `viafb_display_hardware_layout`, `viafb_DeviceStatus`, hotplug mode fields, refresh rates, LCD method/mode, output enable flags, SAMM/dual-fb flags, primary device selection, LCD panel ID, and global `fb_info`/`viafb_par` pointers for primary and secondary framebuffers.

## Control Flow
There is no executable control flow. Other VIA files read and mutate these globals during option parsing, chip initialization, mode setting, hotplug handling, DVI/LCD setup, and framebuffer registration.

## State And Persistence
These globals are process/kernel lifetime state for the VIA fbdev driver. They provide defaults before probe and become shared mutable runtime state after initialization. No external persistence is performed.

## Dependencies And Integration Points
The file includes `global.h`, so the definitions match declarations consumed across `hw.c`, `dvi.c`, `lcd.c`, `viafbdev.c`, `ioctl.c`, and related helpers.

## Risks
Global mutable state makes ordering important and complicates multi-device support. Many fields are plain `int` flags with implicit enum domains. Hotplug and modeset code must coordinate updates carefully because settings such as `viafb_DVI_ON`, `viafb_LCD_ON`, `viafb_SAMM_ON`, and `viafb_primary_dev` drive hardware routing.

## Test Signals
Signals include default startup configuration, option parsing changing expected globals, modeset paths updating hotplug fields, dual framebuffer scenarios using `viafbinfo1`/`viaparinfo1`, and absence of stale globals across module unload/reload.
