# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core.h

## Purpose
`core.h` is the public internal contract for the `mlxsw` core module. It declares the central opaque types, bus and driver callback tables, devlink/trap/listener interfaces, register access APIs, port lifecycle helpers, resource helpers, work scheduling helpers, linecard structures, and optional hwmon/thermal hooks consumed across the Mellanox switch driver family.

## Important APIs, Types, And Functions
- Opaque handles include `struct mlxsw_core`, `struct mlxsw_core_port`, `struct mlxsw_driver`, `struct mlxsw_bus`, `struct mlxsw_bus_info`, and `struct mlxsw_fw_rev`.
- `struct mlxsw_driver` describes a device-kind driver: identity, private size, firmware requirements, init/fini callbacks, port split/unsplit, shared-buffer callbacks, devlink trap/policer callbacks, resource/KVD callbacks, PTP transmitted callback, config profile, and SDQ CQE-v2 support flag.
- `struct mlxsw_bus` abstracts the transport. It supplies `init`, `fini`, optional TX/RX, command execution, hardware clock reads, lag/flood mode reads, and feature flags `MLXSW_BUS_F_TXRX` and `MLXSW_BUS_F_RESET`.
- `struct mlxsw_config_profile` is a large driver-to-bus/hardware configuration request with `used_*` flags controlling LAG, flood tables, KVD sizing, CQE timestamp type, and SWID configuration.
- Listener declarations (`struct mlxsw_rx_listener`, `struct mlxsw_event_listener`, `struct mlxsw_listener`) and macros (`MLXSW_RXL`, `MLXSW_RXL_DIS`, `MLXSW_RXL_MIRROR`, `MLXSW_EVENTL`, `MLXSW_CORE_EVENTL`) standardize trap IDs, enabled/disabled actions, trap groups, control-buffer routing, and event-vs-packet dispatch.
- Register APIs provide synchronous query/write and asynchronous/bulk EMAD transaction helpers using `mlxsw_reg_trans_cb_t`.
- Port and devlink helpers expose physical/CPU port registration, netdev linking, devlink port lookup, linecard lookup, and selected-port removal.
- `struct mlxsw_rx_md_info`, `struct mlxsw_tx_info`, `struct mlxsw_txhdr_info`, and `struct mlxsw_skb_cb` define metadata carried in `skb->cb`; the inline `mlxsw_skb_cb()` asserts it fits.
- Linecard declarations define linecard status events, device info, `struct mlxsw_linecard`, `struct mlxsw_linecards`, event operations, devlink info/flash hooks, block-device hooks, and linecard driver registration.

## Control Flow
The header establishes a layering model. Bus implementations register devices through `mlxsw_core_bus_device_register()`, protocol drivers register themselves through `mlxsw_core_driver_register()`, and protocol code uses the exported core helpers to program registers, register traps, create devlink ports, query resources, and schedule work. Packet/event delivery enters through the trap listener API, while administrative operations enter through devlink callbacks routed to `struct mlxsw_driver`.

## State And Persistence Behavior
This header mostly declares state layout rather than implementing it. The notable persistence contracts are in-memory ownership: driver private memory is trailing storage behind `struct mlxsw_core`, SKB metadata reuses `skb->cb`, bus info carries immutable device facts such as PSID/VSD/FW revision, and linecard objects are owned by `struct mlxsw_linecards` with per-linecard mutexes and delayed work.

## Dependencies And Integration Points
The header includes Linux device, module, SKB, workqueue, net namespace, auxiliary bus, and devlink headers, plus local `trap.h`, `reg.h`, `cmd.h`, `resources.h`, and `mlxfw.h`. It is the common integration point used by bus drivers, Spectrum protocol drivers, linecard support, environment support, trap code, hwmon/thermal optional modules, and firmware flashing.

## Risks And Edge Cases
- `struct mlxsw_driver` has many optional callbacks. Callers must check for hook availability before use, as `core.c` does for devlink operations.
- `mlxsw_skb_cb()` relies on compile-time size compatibility with `skb->cb`; extending metadata can break this invariant.
- Config-profile `used_*` flags must match initialized values. Adding a field without a corresponding flag or bus handling can silently misconfigure hardware.
- Linecard indexing uses one-based slot indices in `mlxsw_linecard_get()` by subtracting one; callers must not pass zero.
- Trap macros bake in actions and trap groups. Incorrect macro selection can enable traps unexpectedly or route packets to the wrong group.

## Test Signals
Compile coverage is important because this file defines cross-module ABI-like structures. Runtime signals include successful driver/bus registration, devlink port operations, trap listener registration through macro-generated definitions, register transaction callbacks, resource query/get behavior, linecard event operations, and optional hwmon/thermal builds both enabled and disabled.
