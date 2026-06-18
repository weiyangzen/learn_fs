# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch.h

## Purpose
`ice_eswitch.h` declares the public switchdev/e-switch interface used by the rest of the ice driver. It exposes representor attach/detach, devlink eswitch mode operations, packet-path helpers, representor update, queue control, and VSI switchdev configuration helpers, with compile-time stubs when `CONFIG_ICE_SWITCHDEV` is disabled.

## Important APIs, Types, and Functions
- VF/SF lifecycle: `ice_eswitch_attach_vf()`, `ice_eswitch_detach_vf()`, `ice_eswitch_attach_sf()`, and `ice_eswitch_detach_sf()`.
- Devlink mode: `ice_eswitch_mode_get()`, `ice_eswitch_mode_set()`, and `ice_is_eswitch_mode_switchdev()`.
- Representor maintenance: `ice_eswitch_update_repr()` and `ice_eswitch_stop_all_tx_queues()`.
- Packet path: `ice_eswitch_set_target_vsi()`, `ice_eswitch_port_start_xmit()`, and `ice_eswitch_get_target()`.
- VSI setup/restore: `ice_eswitch_cfg_vsi()` and `ice_eswitch_decfg_vsi()`.
- Disabled-build stubs return no-op behavior, `-EOPNOTSUPP`, `NETDEV_TX_BUSY`, legacy mode semantics, or original Rx netdev fallback depending on call role.

## Control Flow
The header is a compile-time dispatch layer. When `CONFIG_ICE_SWITCHDEV` is enabled, call sites bind to the implementations in `ice_eswitch.c`. When disabled, the inline stubs keep non-switchdev builds linkable and force callers into legacy/no-op behavior. The notable disabled-build `ice_eswitch_mode_get()` stub returns `DEVLINK_ESWITCH_MODE_LEGACY` directly rather than writing through its `mode` pointer, which means call sites must match expected usage carefully.

## State and Persistence Behavior
The header owns no runtime state. It constrains possible state transitions by making switchdev operations unavailable in non-switchdev builds. Runtime state lives in PF/eswitch/representor structures managed by the implementation.

## Dependencies and Integration Points
It includes `<net/devlink.h>` and `devlink/port.h`, and relies on declarations for `struct ice_pf`, `struct ice_vf`, `struct ice_dynamic_port`, `struct ice_vsi`, `struct ice_tx_offload_params`, `struct ice_rx_ring`, `struct sk_buff`, `struct net_device`, and ice Rx descriptor types from surrounding headers. It is included by PF, VF, SF, Tx, Rx, devlink, and representor code that needs to remain buildable without switchdev.

## Risks and Edge Cases
- Disabled-build stubs must preserve caller expectations. Any caller expecting `ice_eswitch_mode_get(devlink, &mode)` to write `mode` in all builds would be wrong for the current stub.
- Stub return values intentionally differ by operation; attach returns unsupported, detach is no-op, representor Tx reports busy, and Rx target returns the physical netdev.
- New switchdev APIs must add matching stubs or non-switchdev builds will fail.

## Test Signals
- Compile with `CONFIG_ICE_SWITCHDEV=y` and disabled to validate both declaration and stub paths.
- Static checks should ensure callers handle `-EOPNOTSUPP` from attach/config helpers and do not depend on side effects from disabled stubs.
- Packet-path build tests should verify non-switchdev Rx fallback and Tx busy behavior do not break callers.
