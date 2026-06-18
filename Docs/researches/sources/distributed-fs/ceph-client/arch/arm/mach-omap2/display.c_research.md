<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/display.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/display.c

## Purpose
`display.c` wires OMAP2+ display subsystem devices into the platform and provides a custom DSS reset sequence. It handles legacy `omapdss`, framebuffer, VRFB, VOUT helper device registration, OMAP4 DSI pad muxing, OF DSS submodule population, and safe DISPC output shutdown before reset.

## Important APIs, Types, and Functions
The externally used API is `omap_dss_reset(struct omap_hwmod *oh)`. Important internals include `omap4_dsi_mux_pads()`, `omap_dsi_enable_pads()`, `omap_dsi_disable_pads()`, `omap_display_get_version()`, `omapdss_init_fbdev()`, `omapdss_find_dss_of_node()`, `omapdss_init_of()`, and `dispc_disable_outputs()`. It uses `struct omap_dss_board_info` callbacks and `struct omap_dss_dispc_dev_attr`.

## Control Flow
At `omap_device_initcall`, OF initialization finds an enabled DSS node, populates its child devices, then registers legacy fbdev helpers. OMAP4 DSI pad setup locates `omap4_padconf_global` syscon and updates lane-enable/PIPD masks. During DSS reset, optional clocks are enabled, active LCD/TV managers are detected, relevant framedone IRQs are cleared, managers are disabled, and the code waits up to `FRAMEDONE_IRQ_TIMEOUT` before clearing DSS control/SDI/PLL registers and checking reset-done status.

## State and Persistence Behavior
State includes the registered `omapdss` platform device, `omap4_dsi_mux_syscon`, OF-populated subdevices, and transient DISPC/DSS register programming. The reset path mutates display output enable bits and control registers but writes no persistent storage.

## Dependencies and Integration Points
It depends on OF platform population, syscon/regmap, platform data `linux/platform_data/omapdss.h`, OMAP hwmod accessors, clock APIs, SoC revision checks, `display.h`, `control.h`, and `prm.h`. It integrates with framebuffer, VRFB, VOUT, DSS child drivers, and hwmod reset hooks.

## Risks
Resetting DSS while outputs are active can hang or corrupt display state if framedone IRQ selection is wrong. OMAP4 DSI pad muxing depends on syscon availability and correct lane masks. Version detection by SoC revision affects downstream driver feature selection. Timeout paths continue with warnings and may leave displays partially disabled.

## Test Signals
Boot with enabled DSS DT nodes and verify child devices populate. Exercise framebuffer, VOUT, DSI lane enable/disable, and DSS reset while displays are active. Check for framedone timeout warnings, missing syscon errors, and correct `omapdss_version` selection on OMAP2/3/4/5/AM43xx/DRA7 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/display.c -->
