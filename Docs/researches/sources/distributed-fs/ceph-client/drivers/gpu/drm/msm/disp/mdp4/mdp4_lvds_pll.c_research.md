# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_lvds_pll.c

Purpose: registers a simple LVDS PLL clock provider for MDP4 LCDC/LVDS output.

Important APIs and functions: `mdp4_get_lcdc_clock()` initializes the PLL and returns the platform `lcdc_clk` if present, otherwise returns the PLL clock directly. `mdp4_lvds_pll_init()` allocates/registers `clk_hw` and OF clock provider. Clock ops implement enable, disable, recalc, determine_rate, and set_rate. `find_rate()` selects an entry from a static frequency table.

Control flow: set_rate stores requested pixel clock. enable selects the nearest configured table entry, resets the LVDS PHY, writes PLL control registers, enables PLL control, then busy-waits for the lock bit. disable clears PHY and PLL control registers.

State and persistence: `struct mdp4_lvds_pll` stores DRM device and selected pixel clock. Hardware PLL state persists only while powered/enabled.

Dependencies and integration: used by LCDC encoder init. Depends on clock provider APIs, OF clock registration, MDP4 MMIO helpers, and generated LVDS PHY registers.

Risks: the frequency table contains only one configured rate, so clock selection is very limited. The lock wait has no timeout and can spin forever on broken hardware. `find_rate()` assumes a non-empty sorted table.

Test signals: clock registration, fallback when `lcdc_clk` is missing, rate determination, PLL lock on hardware, and disable clearing PHY/PLL state.
