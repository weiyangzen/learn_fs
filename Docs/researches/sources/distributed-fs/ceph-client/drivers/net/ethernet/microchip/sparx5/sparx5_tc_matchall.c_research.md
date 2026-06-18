## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc_matchall.c

### Purpose
`sparx5_tc_matchall.c` implements TC matchall offload for two coarse actions: port mirroring through mirror probes and goto-chain lookup enablement through the VCAP framework.

### Important APIs, Types, And Functions
The public handler is `sparx5_tc_matchall()`. Internals include `sparx5_tc_matchall_entry_find()`, action parsing helpers, `sparx5_tc_matchall_replace()`, `sparx5_tc_matchall_destroy()`, and `sparx5_tc_matchall_stats()`. Entries are stored as `struct sparx5_mall_entry` on `sparx5->mall_entries`.

### Control Flow
Replace requires exactly one action. For `FLOW_ACTION_MIRRED`, it records source port, monitor port, direction, cookie, calls `sparx5_mirror_add()`, and initializes baseline stats. For `FLOW_ACTION_GOTO`, it calls `vcap_enable_lookups()` from the current chain to the target chain and translates common errors into extack messages. Successful entries are appended to the mall list. Destroy finds by cookie, deletes mirror state or disables VCAP lookup, removes the list entry, and returns the result. Stats are supported only for mirror entries.

### State, Persistence, And Dependencies
State is retained in allocated mall entries and hardware mirror/VCAP lookup state. Mirror stats baseline is stored per port through `sparx5_mirror_stats()`. Dependencies include TC matchall structures, flow action helpers, mirror APIs, VCAP API, and `sparx5_main.h`.

### Integration Points
`sparx5_tc.c` dispatches `TC_SETUP_CLSMATCHALL` here for ingress or egress clsact blocks. Mirror actions are implemented by `sparx5_mirror.c`; goto actions prepare VCAP chains used by flower rules.

### Risks
Error paths after allocating `mall_entry` do not free it before returning in several cases, which should be checked for leaks. The action parser does not validate that mirrored device is a Sparx5 netdev before `netdev_priv()`. Destroy removes entries but does not free the `mall_entry` allocation. Stats for goto are unsupported.

### Test Signals
Test one-action enforcement, mirror add/delete/stat paths, mirror error extacks, goto enable/disable with invalid and duplicate chains, unsupported actions, invalid mirror device handling, and memory/resource cleanup on replace failure and destroy.
