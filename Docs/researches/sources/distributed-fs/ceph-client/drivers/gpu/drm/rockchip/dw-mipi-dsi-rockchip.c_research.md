# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw-mipi-dsi-rockchip.c

## Purpose
Provides Rockchip glue for Synopsys DesignWare MIPI DSI host controllers and also exposes some controllers as MIPI DPHY providers. It configures SoC GRF lane/mux registers, internal/external PHY timing, dual-DSI operation, DRM encoder state, and component binding.

## Important APIs, Types, And Functions
Key structs are `rockchip_dw_dsi_chip_data`, `dw_mipi_dsi_rockchip`, `dphy_pll_parameter_map`, and `hstt`. Major flows include `dw_mipi_dsi_get_lane_mbps()`, `dw_mipi_dsi_phy_init()`, `dw_mipi_dsi_rockchip_bind()`, host attach/detach, exported DPHY ops, resume reconfiguration, and the SoC chip-data tables for PX30, RK3128, RK3288, RK3368, RK3399, RK3506, RK3568, and RV1126.

## Control Flow
Probe maps registers, selects chip data by MMIO base, gets clocks, optional external DPHY, GRF, creates a PHY provider, and probes the DW DSI core. Host attach claims usage mode and registers one or two components. Bind resolves dual-DSI clock master/slave, enables runtime PM and PLL reference clock, writes static GRF lane config, creates encoder, sets endpoint ID, and binds the DW DSI core. Atomic check translates DSI pixel format into Rockchip output mode and marks dual DSI when a slave is present.

## State And Persistence
Persistent state includes usage mode under `usage_mutex`, dual-channel pointers, lane Mbps, PLL divisors, pixel format, PHY config, bound state, and chip data. GRF and PHY test-interface writes persist until reset or resume reprogramming.

## Dependencies And Integration Points
Integrates with `drm/bridge/dw_mipi_dsi`, MIPI DSI host attach, generic PHY/DPHY framework, runtime PM, syscon GRF, DRM OF graph, and Rockchip VOP output state.

## Risks
Dual-DSI discovery peeks at peer driver data and forces synchronous probe. Usage-mode arbitration must prevent simultaneous DSI-host and DPHY-provider use. PLL parameter calculations are sensitive to reference clock and lane rate. Several GRF constants come from BSP or undocumented registers.

## Test Signals
Single and dual DSI panels, clock-master validation, external versus internal DPHY paths, exported DPHY receiver mode on RK3399, suspend/resume before panel enable, RGB565/666/888 output modes, and probe ordering with peer DSI nodes.
