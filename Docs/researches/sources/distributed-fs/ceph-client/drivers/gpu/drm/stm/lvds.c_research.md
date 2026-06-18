# sources/distributed-fs/ceph-client/drivers/gpu/drm/stm/lvds.c

## Purpose
`lvds.c` implements the STM32MP25 LVDS display interface transmitter as a DRM bridge. It discovers single- or dual-link topology from OF graph, configures host data mapping and lane distribution, registers an LVDS pixel clock backed by the internal PHY PLL, controls PHY power, and optionally creates a panel connector.

## Important APIs, Types, and Functions
- `struct stm_lvds`: persistent bridge state with registers, clocks, pixel clock rate, PHY descriptors, connector/panel/next bridge pointers, hardware version, and link type.
- `enum lvds_link_type`, `enum lvds_pixel`, `struct lvds_phy_info`: describe topology and PHY register mapping.
- PLL/clock helpers: `lvds_pll_get_params`, `lvds_pll_config`, `lvds_pixel_clk_*`, and clock provider registration/unregistration.
- Host helpers: `lvds_config_data_mapping` and `lvds_config_mode`.
- DRM bridge/connector callbacks: attach, atomic enable/disable, get modes, and connector atomic check.
- `lvds_probe/remove`: platform lifecycle and bridge registration.

## Control Flow, State, and Persistence
Probe locates downstream panel/bridge on port 1, maps registers, enables `pclk`, resets the block, inspects graph ports 1 and 2 for dual-link or single-link routing, gets the reference clock, registers `clk_pix_lvds`, records hardware version, adds the bridge, and disables `pclk`. During atomic enable it enables `pclk`, configures link mode/polarity/channel distribution, writes JEIDA/VESA data mapping from connector bus format, enables LVDS, and prepares/enables the panel. Pixel clock enable powers the selected PHY/PHYs, computes PLL divisors from target pixel clock times seven bits per pixel lane, waits for lock, and enables clock outputs.

Persistent state includes link type, selected PHY pointers, registered clock provider, pixel clock rate, connector/panel relationships, and hardware register programming while enabled.

## Dependencies and Integration Points
The file depends on DRM bridge/panel/OF LVDS helpers, common clock provider APIs, reset, MMIO, iopoll, and media bus formats. It integrates as a downstream bridge for the STM LTDC encoder and may provide the `lvds` clock consumed by LTDC mode validation.

## Risks and Test Signals
Risks include fragile OF graph interpretation, possible resource leaks on some enable error paths, limited data mapping support, integer-only PLL configuration, dual-link phase defaults, and clock-provider lifetime ordering. Tests should cover single primary, single secondary, dual odd-even/even-odd, JEIDA/VESA RGB888 panels, unsupported bus formats, PLL rate rounding, bridge attach with and without next bridge, panel prepare/enable ordering, and repeated enable/disable cycles.
