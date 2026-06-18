# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-ldb-helper.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-ldb-helper.c

## Purpose

This helper library factors common LVDS Display Bridge channel handling for i.MX LDB drivers. It manages channel discovery, bridge registration, common attach behavior, bus-format capture, and shared LDB control-bit updates.

## Important APIs, Types, And Functions

Exported functions include `ldb_channel_is_single_link()`, `ldb_channel_is_split_link()`, `ldb_bridge_atomic_check_helper()`, `ldb_bridge_mode_set_helper()`, `ldb_bridge_enable_helper()`, `ldb_bridge_disable_helper()`, `ldb_bridge_attach_helper()`, `ldb_init_helper()`, `ldb_find_next_bridge_helper()`, `ldb_add_bridge_helper()`, and `ldb_remove_bridge_helper()`.

## Control Flow

Platform drivers allocate per-channel bridges, set `ldb->channel[]`, then call `ldb_init_helper()` to get the parent syscon regmap and discover available channel child nodes. They call `ldb_find_next_bridge_helper()` to resolve downstream bridges, then `ldb_add_bridge_helper()` to publish only available channels. During atomic operations the helper records negotiated bus formats, sets split/data-width/JEIDA bits in `ldb_ctrl`, writes the control register on enable, and clears channel mode bits on disable.

## State And Persistence Behavior

Shared mutable state is `ldb->ldb_ctrl`, channel availability, child node pointers, link type, and bus formats. It is volatile driver state with syscon register writes on enable/disable.

## Dependencies And Integration Points

It depends on syscon regmap, OF child nodes with `reg`, DRM bridge chaining, media bus LVDS formats, and exported GPL symbols used by i.MX8QM/QXP LDB drivers.

## Risks And Test Signals

Risks include stale bits accumulating in `ldb_ctrl` across repeated mode sets, invalid child `reg` handling, and requiring `NO_CONNECTOR` attach. Test signals are dual/single-link channel discovery, downstream bridge resolution, correct SPWG/JEIDA bit programming, and module symbol linkage.
