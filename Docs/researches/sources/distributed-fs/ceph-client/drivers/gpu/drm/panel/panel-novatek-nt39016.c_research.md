# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-novatek-nt39016.c

Purpose: SPI-controlled DRM DPI panel driver for Novatek NT39016 TFT LCD controllers, currently matched to Kingdisplay KD035G6-54NT 320x240 panels with 50 Hz and 60 Hz modes.

Important APIs, types, and functions: `enum nt39016_regs` names controller registers. `struct nt39016_panel_info` carries mode table, dimensions, bus format, and bus flags. `struct nt39016` stores `drm_panel`, regmap, regulator, panel info, and reset GPIO. Key functions are `nt39016_probe()`, `nt39016_prepare()`, `nt39016_enable()`, `nt39016_disable()`, `nt39016_unprepare()`, and `nt39016_get_modes()`.

Control flow: probe allocates a DPI panel, reads OF match data, gets `power` regulator and reset GPIO, configures SPI as 8-bit mode 3 3-wire, initializes a regmap with 6-bit register and 8-bit value fields, binds optional backlight, and adds the panel. Prepare enables power, pulses reset, then writes the initialization register table through `regmap_multi_reg_write()`. Enable writes `NT39016_REG_SYSTEM` with reset-not and standby bits, and waits before backlight use. Disable clears standby, while unprepare asserts reset and disables power.

State and persistence: no durable state. Regmap uses `REGCACHE_FLAT`, so register values are cached in memory; hardware is reinitialized on prepare.

Dependencies and integration points: DRM panel over DPI, SPI, regmap, regulator, GPIO, media bus formats, and optional OF backlight. Compatible string is `kingdisplay,kd035g6-54nt`.

Risks and test signals: regmap access restrictions must align with the controller protocol. Remove calls disable/unprepare after panel removal, which can report errors if hardware is already off. SPI mode and 3-wire support are host-dependent. Test SPI setup, regmap writes, reset pulse timing, both display modes, bus format `MEDIA_BUS_FMT_RGB888_1X24`, backlight delay, and remove after failed/partial prepare.
