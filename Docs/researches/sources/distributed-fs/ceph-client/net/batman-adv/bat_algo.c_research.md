# sources/distributed-fs/ceph-client/net/batman-adv/bat_algo.c

## Purpose
`bat_algo.c` manages routing algorithm registration, selection, module parameter validation, and generic netlink dumping of supported algorithms.

## Important APIs and Functions
- Global `batadv_routing_algo[20] = "BATMAN_IV"`: module parameter backing store and default algorithm name.
- `batadv_algo_init`: initializes the algorithm hlist.
- `batadv_algo_get`: searches registered `struct batadv_algo_ops` by name.
- `batadv_algo_register`: rejects duplicate names and validates required callbacks before inserting an algorithm.
- `batadv_algo_select`: assigns a registered algorithm to a mesh interface; intended only during mesh creation.
- `batadv_param_set_ra`: validates module parameter writes against registered algorithms.
- `batadv_algo_dump`: emits registered algorithm names through generic netlink.

## Control Flow
Subsystem init initializes the list, then algorithm implementations register themselves (`BATMAN_IV`, optionally `BATMAN_V`). Module parameter writes strip a trailing newline, verify the algorithm exists, and update `batadv_routing_algo`. Mesh creation calls `batadv_algo_select` to set `bat_priv->algo_ops`. Netlink dump walks the hlist using `cb->args[0]` as the skip cursor.

## State and Persistence
State persists in the global algorithm list and the routing algorithm module parameter. Per-mesh state is a pointer to selected `algo_ops`; this file explicitly does not deinitialize an old algorithm when selecting a new one.

## Dependencies and Integration
Depends on `struct batadv_algo_ops` from `main.h`, netlink family definitions, and algorithm providers in `bat_iv_ogm.c` and `bat_v.c`.

## Risks and Test Signals
Risks include registering incomplete algorithm ops, changing selection after mesh initialization, module parameter ordering before optional algorithm registration, and netlink dump truncation/cursor handling. Test signals include module parameter validation for `BATMAN_IV`/`BATMAN_V`/invalid names, duplicate registration failure, netlink algorithm dump with small skb, and mesh creation selecting configured algorithms.
