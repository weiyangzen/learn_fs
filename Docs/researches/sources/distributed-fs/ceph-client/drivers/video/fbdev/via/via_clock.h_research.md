<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_clock.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_clock.h

Purpose: Public clock/PLL function-table interface for the VIA framebuffer driver.

Important APIs/types/functions: Defines `enum via_clksrc`, `struct via_pll_config`, `struct via_clock`, inline helpers `get_pll_internal_frequency()` and `get_pll_output_frequency()`, and `via_clock_init()`.

Control flow and state: No standalone flow beyond inline frequency calculations. A `via_clock` instance becomes a chip-specific dispatch table after `via_clock_init()` and is then used by modeset code to program clocks and PLLs.

Dependencies and integration points: Uses Linux fixed-width types and is implemented by `via_clock.c`. Risks include integer division/overflow if reference frequencies or PLL values are invalid, function pointers needing initialization before use, and no explicit error channel for unsupported operations. Test signals are compile coverage, PLL frequency calculations for known configurations, and function-table initialization for each supported `gfx_chip` value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_clock.h -->
