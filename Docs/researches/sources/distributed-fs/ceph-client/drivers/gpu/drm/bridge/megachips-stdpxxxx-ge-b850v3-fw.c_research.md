# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/megachips-stdpxxxx-ge-b850v3-fw.c

## Purpose

This board-specific driver models the GE B850v3 display pipeline containing two MegaChips devices with GE firmware: STDP4028 LVDS-to-DP and STDP2690 DP-to-DP++. The chips self-configure video; the driver exists to expose one DRM bridge/connector, read EDID through the STDP2690 I2C device, and handle HPD/link interrupts from the STDP4028 I2C device.

## Important APIs, Types, And Functions

`struct ge_b850v3_lvds` contains a DRM connector, DRM bridge, and two I2C client pointers. A global `ge_b850v3_lvds_ptr` plus `ge_b850v3_lvds_dev_mutex` coordinates the two independent I2C drivers until both physical devices are probed.

EDID functions are `stdp2690_read_block()`, `ge_b850v3_lvds_edid_read()`, and `ge_b850v3_lvds_get_modes()`. Detection is `ge_b850v3_lvds_bridge_detect()` using STDP4028 status. Connector creation is `ge_b850v3_lvds_create_connector()`. Registration is delayed until both `stdp4028_ge_b850v3_fw_probe()` and `stdp2690_ge_b850v3_fw_probe()` have run.

## Control Flow

Module init registers two I2C drivers. Each probe initializes or reuses the global bridge object, stores its I2C client, and returns early if the other half is not present. Once both are present, `ge_b850v3_register()` sets bridge ops/type/of_node, adds the bridge, clears pending STDP4028 interrupts, and requests the HPD IRQ if provided. Attach enables STDP4028 interrupt output and hotplug/link-change interrupts, then creates a DisplayPort connector unless connectorless attach was requested.

## State And Persistence

The singleton global object persists while both I2C devices are bound. Removal only tears down the DRM bridge when both client pointers are populated, avoiding double removal but also making global lifetime/order important. HPD interrupt enablement and pending status are stored in STDP4028 registers. EDID is read directly from STDP2690 on demand.

## Dependencies And Integration Points

The driver depends on I2C SMBus/transfer operations, DRM bridge/connector/EDID helpers, IRQ threading, and OF matching for both physical chips. It integrates with KMS as one DisplayPort bridge/connector despite the two-chip hardware pipeline.

## Risks And Edge Cases

The global singleton design is fragile for multiple boards/devices. Remove ordering leaves client pointers intact and depends on devm allocation, so late callbacks must not occur after one device disappears. I2C transfer errors in EDID read return `-1` rather than a normal errno. Detect uses exact link-state equality and returns unknown for partial states. Bridge `of_node` is taken from STDP4028 only. Connector creation is legacy and skipped for connectorless attach.

## Test Signals

Test both probe orders, one-chip-missing behavior, IRQ absent/present, HPD connect/disconnect, EDID reads through STDP2690, connectorless and connector-owning attach, removal in both orders, duplicate device instances, and SMBus error handling.
