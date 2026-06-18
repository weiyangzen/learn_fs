# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_lvds.c

## Purpose

`rockchip_lvds.c` implements the Rockchip LVDS component driver for RK3288 and PX30 style LVDS blocks. It binds a DRM encoder to a panel or downstream bridge, parses output/data-mapping properties, programs LVDS/RGB/dual-LVDS hardware and GRF muxes, manages panel sequencing, runtime PM, clocks, PHY setup, and lifecycle.

## Important APIs, Types, and Functions

- `struct rockchip_lvds_soc_data` selects SoC-specific probe and encoder helper functions.
- `struct rockchip_lvds` stores MMIO, GRF regmap, pclk, optional PHY, output/format selections, panel/bridge, Rockchip encoder, and pinctrl info.
- `rockchip_lvds_encoder_atomic_check` writes P888 LVDS output into `rockchip_crtc_state`.
- RK3288 helpers power lanes, program PLL/lane registers, configure GRF format/dual-channel/source, and handle panel enable/disable.
- PX30 helpers enable LVDS/P2S mode in GRF, configure format/source, and initialize/power the PHY.
- `rockchip_lvds_bind` resolves graph endpoints, creates encoder/bridge connector, and enables runtime PM.

## Control Flow

Probe allocates state, reads match data, obtains GRF, performs SoC initialization, and adds the component. Bind locates port 1 endpoints, finds a panel or bridge, derives output type and LVDS mapping, initializes a DRM LVDS encoder, attaches helper funcs, wraps panels in a bridge, attaches a bridge connector, and enables runtime PM. Encoder enable prepares the panel, powers/configures LVDS hardware and VOP source mux, then enables the panel. Disable reverses the sequence.

## State and Persistence Behavior

`rockchip_lvds` persists for the platform device lifetime. Parsed `output` and `format` control enable-time programming. RK3288 pclk is prepared during probe and enabled around poweron; PX30 keeps a PHY initialized and powered on after probe, while runtime PM gates register access.

## Dependencies and Integration Points

The driver depends on DRM bridge/panel/connector helpers, OF graph, syscon regmap, pinctrl, PHY, clocks, runtime PM, and Rockchip CRTC state. It integrates with VOP/VOP2 through encoder atomic state and GRF source selection.

## Risks and Edge Cases

`rockchip_lvds_unbind` unconditionally calls the SoC encoder disable helper. Some enable error paths unprepare the panel but may not fully power off after partial hardware enable. PX30 rejects RGB and dual-LVDS output. Panel bridge cleanup should be reviewed for externally supplied bridges.

## Test Signals

Test RK3288 RGB/single/dual LVDS, PX30 LVDS-only, VESA/JEIDA mappings, VOP source selection, panel sequencing, runtime suspend/resume, missing endpoints, invalid properties, and GRF writes.
