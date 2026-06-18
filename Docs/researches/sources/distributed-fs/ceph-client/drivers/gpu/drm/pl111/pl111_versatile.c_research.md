# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_versatile.c

Purpose: This file provides platform-specific setup for ARM Integrator, Versatile, RealView, and Versatile Express boards using PL110/PL111 CLCD blocks. It maps syscon compatibles to variant metadata, register callbacks, connector mux programming, and DVI mux decisions.

Important APIs, types, and functions: `pl111_versatile_init()` is the exported entry point. Internal callbacks include `pl111_integrator_enable()`, `pl111_impd1_enable()/disable()`, `pl111_versatile_enable()/disable()`, and `pl111_realview_clcd_enable()/disable()`. `pl111_vexpress_clcd_init()` handles VExpress-specific motherboard/core-tile DVI muxing through `devm_regmap_init_vexpress_config()`. Static `pl111_variant_data` instances override formats, fbdev depth, broken clockdivider/vblank flags, and register selection.

Control flow: The init path finds a matching syscon node from `versatile_clcd_of_match`; non-reference designs return success without changes. VExpress uses a special path that scans root child nodes for core-tile PL111/HDLCD, decides whether motherboard or daughterboard should own DVI, writes the FPGA mux, and selects the VExpress variant. Integrator systems can be redirected to an IM-PD1 syscon if present. Other platforms convert the syscon node to a regmap and install variant callbacks and metadata based on the matched enum.

State and persistence: A file-static `versatile_syscon_map` is used by enable/disable callbacks to write platform control registers. `priv->variant`, `priv->variant_display_enable`, `priv->variant_display_disable`, `priv->ienb`, and `priv->ctrl` are persistent driver state for the probed device. The actual connector/mux settings persist in platform syscon registers until changed by firmware or another driver.

Dependencies and integration points: Integrates OF matching, syscon/regmap, platform devices, VExpress config APIs, DRM format definitions, and `pl111_drm_dev_private`. The display pipeline later calls the installed enable/disable callbacks when programming the CLCD.

Risks: `versatile_syscon_map` is global, so multiple matching CLCD instances would share callback backing state. VExpress probe can intentionally return `-ENODEV` to deactivate the motherboard CLCD when core-tile graphics owns DVI; that needs to be interpreted as platform selection, not a generic failure. Format-to-mux programming is limited to known DRM formats and logs errors for unhandled formats.

Test signals: Boot each supported ARM reference design; validate syscon bits for RGB/BGR/555/888 modes; test VExpress configurations with motherboard-only CLCD, core-tile CLCD, and core-tile HDLCD; confirm broken-vblank and clock-divider flags change behavior in the core driver.
