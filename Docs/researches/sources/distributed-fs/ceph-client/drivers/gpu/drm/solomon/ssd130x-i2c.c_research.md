# sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x-i2c.c

Purpose: I2C transport for the shared SSD130x/SSD132x/SSD133x DRM OLED core.

Important APIs and types: `ssd130x_i2c_regmap_config` uses 8-bit reg/value fields; the core treats command/data control bytes as regmap registers. `ssd130x_i2c_probe()` creates an I2C regmap and calls `ssd130x_probe()`. remove and shutdown delegate to the core. The OF table covers SH1106, SSD1305/1306/1307/1309, deprecated `*fb-i2c` compatibles, and SSD1322/1325/1327.

Control flow: probe is thin: regmap init, core probe, clientdata storage. shutdown and remove retrieve the core device pointer and call core shutdown/remove.

State and persistence: no transport state beyond clientdata and devm regmap.

Dependencies and integration: depends on I2C regmap and core symbols in `DRM_SSD130X` namespace.

Risks: I2C table lacks SSD1331 while SPI supports it; this may reflect bus support, but adding an I2C SSD1331 board would require updating this file. Returning raw `PTR_ERR()` from regmap/core probe gives less context than `dev_err_probe()`.

Test signals: OF match data must select the correct variant, deprecated compatibles should still bind, and remove/shutdown should blank/power down through the core.
