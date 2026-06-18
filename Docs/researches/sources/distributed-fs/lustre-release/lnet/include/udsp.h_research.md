# sources/distributed-fs/lustre-release/lnet/include/udsp.h

## Purpose
This internal header declares User Defined Selection Policy management APIs for LNet. UDSP policies influence route, peer, network, and NI selection by applying priorities or preferred lists to matching constructs.

## Important APIs, Types, And Functions
Policy list management uses `lnet_udsp_add_policy()`, `lnet_udsp_get_policy()`, and `lnet_udsp_del_policy()`. Application hooks are `lnet_udsp_apply_policies()`, `lnet_udsp_apply_policies_on_lpni()`, `lnet_udsp_apply_policies_on_lpn()`, `lnet_udsp_apply_policies_on_ni()`, and `lnet_udsp_apply_policies_on_net()`. Lifecycle helpers are `lnet_udsp_alloc()`, `lnet_udsp_free()`, and `lnet_udsp_destroy()`. User/kernel conversion is represented by `lnet_get_udsp_size()`, `lnet_udsp_marshal()`, `lnet_udsp_demarshal_add()`, and `lnet_udsp_get_construct_info()`.

## Control Flow
Management functions require the LNet API mutex. Applying all policies may target all stored policies or a single passed policy and can also revert effects. Object-specific application functions require both the API mutex and exclusive LNet network lock. Marshal/demarshal paths convert between internal `struct lnet_udsp` and ioctl bulk payloads.

## State, Persistence, And Dependencies
The header declares APIs over a global policy set owned by LNet implementation files. Policy state persists in kernel memory until deletion or `lnet_udsp_destroy()`. It depends on `lib-lnet.h`, LNet peer/net/NI structures, and ioctl UDSP payload definitions.

## Integration Points
LNet configuration ioctls and netlink/control paths create policies; route/peer/NI management invokes the apply helpers when constructs are added, removed, refreshed, or queried.

## Risks
The locking preconditions are critical. Calling apply helpers while holding `lnet_net_lock` where forbidden, or without `LNET_LOCK_EX` where required, can deadlock or race policy state. Marshal size mismatches can corrupt user/kernel exchange. Revert behavior must mirror apply behavior exactly.

## Test Signals
Tests should add/delete/reorder policies, apply to existing and newly added peers/NIs/nets, revert policies, marshal/demarshal round trip complex descriptors, query construct info, and run lockdep-enabled policy churn.
