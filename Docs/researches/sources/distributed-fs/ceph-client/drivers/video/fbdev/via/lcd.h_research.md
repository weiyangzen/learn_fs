<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/lcd.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/lcd.h

Purpose: LCD/LVDS interface header for viafb. It defines LVDS/TMDS chip ID constants, panel ID constants, external LCD state globals, and function prototypes implemented by `lcd.c` and `vt1636.c`.

Important APIs/types/functions: Constants include VT1631/VT3271 device-ID registers and named LCD panel IDs from 640x480 through OLPC 1200x900. Prototypes cover VT1636 power/init helpers, `viafb_lcd_enable()`, `viafb_lcd_disable()`, `viafb_init_lcd_size()`, `viafb_lcd_set_mode()`, `viafb_lvds_trasmitter_identify()`, `viafb_init_lvds_output_interface()`, and `viafb_lcd_get_mobile_state()`.

Control flow and state: There is no runtime flow in this header. It provides the compile-time contract for the LCD path that mutates `lvds_setting_information`, `lvds_chip_information`, and global active-output flags.

Dependencies and integration points: Depends on LVDS and framebuffer types supplied through the broader viafb include chain. It is consumed by `global.h` users, `lcd.c`, `vt1636.c`, and modeset code. Risks include duplicate declaration of `viafb_init_lvds_output_interface`, panel ID names that do not directly match the `fp_id_to_vindex()` switch numbering for every entry, and reliance on global `viafb_LCD*_ON`/`viafb_DVI_ON`. Test signals are compile coverage, panel-ID to geometry validation, and ensuring all prototypes match implementation signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/lcd.h -->
