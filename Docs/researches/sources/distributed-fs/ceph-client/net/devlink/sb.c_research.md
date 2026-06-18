
# sources/distributed-fs/ceph-client/net/devlink/sb.c

## Purpose
This file implements devlink shared-buffer support. Shared buffers describe packet buffer pools and traffic-class bindings, expose pool and per-port thresholds, allow userspace to trigger occupancy snapshots or clear maxima, and delegate all hardware reads/writes to driver callbacks.

## Important APIs, Types, And Functions
`struct devlink_sb` stores list linkage, shared-buffer index, total size, ingress/egress pool counts, and ingress/egress traffic-class counts. Lookup and validation helpers include `devlink_sb_get_by_index()`, `devlink_sb_get_from_attrs()`, `devlink_sb_pool_index_get_from_attrs()`, `devlink_sb_pool_type_get_from_attrs()`, `devlink_sb_th_type_get_from_attrs()`, and `devlink_sb_tc_index_get_from_attrs()`.

Command handlers cover shared-buffer metadata (`devlink_nl_sb_get_doit()`, dump), pools (`devlink_nl_sb_pool_get_doit()`, dump, `devlink_nl_sb_pool_set_doit()`), port-pool thresholds (`devlink_nl_sb_port_pool_get_doit()`, dump, set), traffic-class pool bindings (`devlink_nl_sb_tc_pool_bind_get_doit()`, dump, set), occupancy snapshot (`devlink_nl_sb_occ_snapshot_doit()`), and max clear (`devlink_nl_sb_occ_max_clear_doit()`).

Driver-facing lifecycle APIs are `devl_sb_register()`, `devlink_sb_register()`, `devl_sb_unregister()`, and `devlink_sb_unregister()`.

## Control Flow
Drivers register each shared buffer with static counts and size. Get/dump commands enumerate registered SBs and call driver callbacks to fetch pool, port-pool, and TC binding state. Set commands validate indexes/types/required attributes, then call the corresponding driver setter.

Pool dumps iterate each registered shared buffer and every pool index. Port-pool dumps iterate every registered port for every pool. TC binding dumps iterate every port, all ingress TCs, and all egress TCs. Dump state uses a flat index so generic netlink can resume after message-size limits.

Occupancy information is optional. If `sb_occ_port_pool_get` or `sb_occ_tc_port_bind_get` exists, fill paths append current and max occupancy values unless the callback returns `-EOPNOTSUPP`. Snapshot and max-clear commands directly call `sb_occ_snapshot` and `sb_occ_max_clear` when provided.

## State And Persistence
The file stores only SB descriptors in `devlink->sb_list`. Pool sizes, thresholds, bindings, and occupancy values are owned by hardware/driver state and retrieved or changed through callbacks. No persistent storage is written here; persistence depends on device firmware/driver behavior.

## Dependencies And Integration Points
The implementation depends on `devl_internal.h`, devlink port iteration, generic netlink helpers, and a broad set of `struct devlink_ops` shared-buffer callbacks. Drivers such as Ocelot/Felix and NFP in this repository provide concrete shared-buffer behavior.

## Risks And Edge Cases
The set paths validate index ranges against registered counts but do not enforce semantic consistency between pool type and pool index beyond what drivers do. A pool index spans ingress and egress pool counts as a flat range, while TC validation uses the supplied pool type.

In `devlink_nl_sb_tc_pool_bind_fill()`, an occupancy callback error other than `-EOPNOTSUPP` returns immediately without cancelling the in-progress generic-netlink message. That differs from the nearby port-pool fill path and is worth focused review because it can leave partially built skb state on error.

Dump loops can become large because they multiply SBs, ports, pools, and TCs. Correct flat-index resume behavior is important for devices with many ports or traffic classes.

## Test Signals
Driver-specific tests and reports for Ocelot/Felix and NFP shared buffers are relevant integration signals. Useful tests cover invalid SB/pool/TC indexes, pool get/set, port-pool thresholds, ingress and egress TC binding, optional occupancy unsupported paths, occupancy snapshot/max clear, and multi-part dumps on devices with enough ports/pools to exceed one skb.
