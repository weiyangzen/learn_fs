# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lag.h

## Purpose
Defines LAG roles, constants, state structures, work-item layout, and public LAG entry points for the `ice` driver.

## Important APIs, types, and functions
- `enum ice_lag_role` models none, primary, backup, and unset roles.
- Constants define invalid lport, primary/secondary indexes and masks, reset retry count, default switch profile, metadata protocol ID, and lport extract offset.
- `struct ice_lag` stores PF/netdev linkage, upper bond netdev, notifier, bond mode, SWID, active lport, state flags, active-port bitmap, primary/secondary lports, queue-home matrix, secondary placeholder VF VSIs, recipe/rule IDs, and role.
- `struct ice_lag_work` stores deferred notifier work, a copied netdev list, event type, event netdev, and copied notifier payload.
- Declares initialization, teardown, rebuild, switchdev query, VF movement, reset prepare/complete, and active-active failover functions.

## Control flow
No executable flow is present. The struct layout directly drives the event work and queue-migration logic in `ice_lag.c`.

## State and persistence behavior
All state is per-PF runtime state. Hardware-persistent effects are managed by the implementation through recipe/rule/SWID IDs stored in `struct ice_lag`.

## Dependencies and integration points
Includes `linux/netdevice.h` and forward-declares `ice_pf` and `ice_vf`. The header is shared with PF lifecycle, reset, VF, and switchdev paths that need LAG state or helper calls.

## Risks
Bitfield state must remain large enough for encoded values such as `port_bitmap`. Arrays are sized by SR-IOV limits; changes to VF or queue maxima affect memory footprint. Public helper comments in the implementation impose locking requirements that callers must follow.

## Test signals
Build coverage plus runtime bond join/leave, VF reset, PF reset, and active-active failover exercise the exported interface and state layout.
