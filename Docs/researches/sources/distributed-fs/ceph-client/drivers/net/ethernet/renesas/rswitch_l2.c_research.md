# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch_l2.c

## Purpose
This file implements switchdev and netdevice notifier support for R-Switch bridge offload. It tracks which R-Switch ports belong to a Linux bridge, decides whether a bridge has enough open R-Switch ports for hardware L2 offload, programs forwarding-engine registers for MAC learning and L2 forwarding, handles bridge STP state changes, applies bridge ageing time, and registers/unregisters notifier blocks for the module.

## Important APIs, Types, And Functions
- Offload eligibility: `rdev_for_l2_offload()` requires a selected `priv->offload_brdev`, matching `rdev->brdev`, and an opened port bit.
- Hardware programming: `rswitch_change_l2_hw_offloading()`, `rswitch_update_l2_hw_learning()`, `rswitch_update_l2_hw_forwarding()`, and exported `rswitch_update_l2_offload()`.
- Bridge tracking: `rswitch_update_offload_brdev()`, `rswitch_port_update_brdev()`, and `rswitch_netdevice_event()` handle `NETDEV_CHANGEUPPER` bridge link/unlink notifications.
- Switchdev attributes: `rswitch_port_update_stp_state()`, `rswitch_update_ageing_time()`, `rswitch_port_attr_set()`, `rswitch_switchdev_event()`, and `rswitch_switchdev_blocking_event()`.
- Notifier lifecycle: `rswitch_register_notifiers()` and `rswitch_unregister_notifiers()` register netdevice, switchdev atomic, and switchdev blocking notifier blocks.

## Control Flow
When a netdevice upper changes, the netdevice notifier filters for R-Switch netdevs using `is_rdev()` and for bridge masters using `netif_is_bridge_master()`. It updates the port's `brdev`, scans all R-Switch ports for the first bridge with at least two member ports, stores that bridge as `priv->offload_brdev`, and recalculates L2 offload. Open and stop in `rswitch_main.c` also call `rswitch_update_l2_offload()` when a port has a bridge master so offload follows port runtime state.

STP changes arrive through switchdev `SWITCHDEV_ATTR_ID_PORT_STP_STATE`. The driver marks learning requested for LEARNING or FORWARDING states, forwarding requested only for FORWARDING, and updates hardware. Learning offload toggles `FWPC0_MACSSA`, `FWPC0_MACHLA`, and `FWPC0_MACHMA`; forwarding offload toggles `FWPC0_MACDSA`. Forwarding also computes a destination mask where participating hardware-forwarded ports are cleared, writes `FWPC2(port)` with a mask that prevents self-forwarding, and starts/stops hardware forwarding per port. Bridge ageing time writes `FWMACAGC` after validating the value fits the hardware field.

## State And Persistence
State is runtime-only in `struct rswitch_device` and `struct rswitch_private`: each port tracks `brdev`, `learning_requested`, `learning_offloaded`, `forwarding_requested`, and `forwarding_offloaded`; the private structure tracks the currently selected `offload_brdev` and opened-port bitmap. Hardware forwarding state persists in MFWD registers until changed or reset. No disk persistence exists.

## Dependencies And Integration Points
The file depends on Linux netdevice notifier APIs, bridge helpers, switchdev notifier APIs, FIELD_PREP/FIELD_FIT bitfield helpers, `rswitch.h` register/state definitions, and `rswitch_l2.h` prototypes. It integrates with `rswitch_main.c` through `is_rdev()`, `rswitch_modify()`, port list state, open/stop notifications, module probe notifier registration, and remove notifier unregistration.

## Risks And Edge Cases
- Only one bridge is selected for offload (`priv->offload_brdev`), chosen as the first bridge found with two R-Switch ports; additional bridges or later ordering changes are not offloaded.
- The debug message in `rswitch_update_offload_brdev()` appears inverted: it logs "changing" when the new bridge equals the old bridge, and "starting" otherwise.
- Notifier callbacks update shared port/offload state without an explicit private lock; this relies on notifier and RTNL/switchdev serialization.
- Ageing time is a `clock_t` written directly into the hardware field, so unit conversion expectations must match switchdev's ageing-time units and the hardware's configured ageing clock.
- Unsupported switchdev port object add/delete operations return `-EOPNOTSUPP`; bridge features beyond STP state and ageing time are not offloaded.

## Test Signals
Create Linux bridges with two or more R-Switch ports, join and leave ports, open/close bridge member interfaces, change STP states through bridge operation, verify `FWPC0` learning/forwarding bits and `FWPC2` destination masks, set bridge ageing time and validate field limits, test unsupported FDB/VLAN/MDB operations fail gracefully, and remove the driver while notifiers are registered without callbacks touching freed state.
