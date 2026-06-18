# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-core.h

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-core.h

## Purpose

This header defines the shared data model for the Cadence DSI core and its platform wrappers. It is the contract between the generic DSI host/bridge implementation and SoC-specific glue such as TI J721E.

## Important APIs, Types, And Functions

`struct cdns_dsi_output` records the attached `mipi_dsi_device`, downstream `drm_bridge`, and cached PHY options. `enum cdns_dsi_input_id` names SDI, DPI, and DSC inputs, though the core currently forces `CDNS_DPI_INPUT`. `struct cdns_dsi_cfg` stores horizontal DSI byte counts. `struct cdns_dsi_input` embeds the upstream DRM bridge. `struct cdns_dsi_platform_ops` provides `init`, `deinit`, `enable`, and `disable` wrapper hooks. `struct cdns_dsi` contains all runtime state.

## Control Flow

The header has no executable flow, but it shapes probe and atomic paths. The core fills clock/reset/PHY/MMIO fields at probe, stores attached output device information during DSI host attach, uses platform ops during probe and atomic enable/disable, and gates optional J721E wrapper MMIO through `CONFIG_DRM_CDNS_DSI_J721E`.

## State And Persistence Behavior

All state is in memory and device-managed where possible. The two booleans `link_initialized` and `phy_initialized` prevent redundant link/PHY bring-up across command transfers and modesets until post-disable clears them. The completion coordinates direct-command IRQs.

## Dependencies And Integration Points

The header depends on DRM bridge, DRM MIPI DSI, Linux completions, and generic PHY configuration types. Platform wrapper headers include this file to declare wrapper ops against the full `struct cdns_dsi`.

## Risks And Test Signals

Changing field layout or optional members can break wrapper builds or core assumptions. The core assumes one `input` and one `output`; extending to multiple DSI devices would require bridge-chain reconfiguration beyond this header. Build coverage with and without `CONFIG_DRM_CDNS_DSI_J721E` is the primary signal.
