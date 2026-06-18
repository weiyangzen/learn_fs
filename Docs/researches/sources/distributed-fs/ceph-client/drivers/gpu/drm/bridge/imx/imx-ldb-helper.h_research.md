# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-ldb-helper.h

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-ldb-helper.h

## Purpose

This header defines the shared i.MX LDB control bits, channel/base structures, link-type enum, and helper prototypes used by platform-specific LDB bridge drivers.

## Important APIs, Types, And Functions

It defines LDB channel enable masks, split-mode, 24-bit width, JEIDA mapping, VSYNC polarity bits, `MAX_LDB_CHAN_NUM`, `enum ldb_channel_link_type`, `struct ldb_channel`, `struct ldb`, `bridge_to_ldb_ch()`, and prototypes for all exported helper functions.

## Control Flow

There is no executable flow. The definitions establish how platform drivers allocate channels, store private bridge state, and call common attach/mode/enable helpers.

## State And Persistence Behavior

The header describes volatile state fields such as `link_type`, `in_bus_format`, `out_bus_format`, `is_available`, and aggregate `ldb_ctrl`. Register persistence is handled by C-file helpers and platform drivers.

## Dependencies And Integration Points

It includes Linux device/OF/regmap headers and DRM atomic, bridge, device, encoder, and modeset helper headers. It is shared by `imx-ldb-helper.c` and SoC LDB drivers such as `imx8qm-ldb.c`.

## Risks And Test Signals

The bit definitions encode hardware ABI. Incorrect masks affect all helper users. Build tests with each LDB consumer and runtime validation of single/split link programming are the main signals.
