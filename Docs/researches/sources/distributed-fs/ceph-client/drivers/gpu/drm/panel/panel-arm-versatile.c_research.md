# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-arm-versatile.c

Purpose: Platform DRM panel driver for ARM Versatile reference-design TFT panels detected through syscon CLCD identification registers.

Important APIs/types/functions: Defines SYS_CLCD and IB2 control bits, `struct versatile_panel_type`, `struct versatile_panel`, `versatile_panels[]`, DRM panel funcs, and platform probe.

Control flow: Probe obtains parent syscon regmap, reads `SYS_CLCD`, masks the panel ID, selects a matching panel descriptor, optionally finds the IB2 syscon for panels mounted on that board, and registers a DPI panel. Enable/disable update IB2 control bits when present. `get_modes` duplicates the detected panel mode and sets physical size and bus flags.

State and persistence: State stores detected panel type plus syscon regmaps. Hardware detection is performed at probe; no persistent storage is written beyond IB2 enable bits.

Dependencies and integration: Depends on OF platform device, MFD syscon/regmap, videomode helpers, and DRM panel. Integrates with ARM Versatile/RealView display controllers through a DPI panel abstraction.

Risks: Unknown IDs return `-ENODEV`, including the VGA/no-panel case. IB2 lookup failure is tolerated by treating it as absent. Register definitions are board-specific.

Test signals: Boot on Versatile AB/PB variants, syscon read failure paths, each supported ID mode, IB2 enable/disable bit updates, and connector mode dimensions/bus flags.
