<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_config.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_config.c

## Purpose
`rmnet_config.c` implements RMNET's rtnetlink configuration engine. It registers the `"rmnet"` link kind, associates real devices with RMNET ports, creates/deletes muxed virtual devices, changes mux IDs and data-format flags, handles bridge mode, and cleans up when underlying devices unregister.

## Important APIs, Types, and Functions
- `rmnet_policy[]` validates `IFLA_RMNET_MUX_ID` and `IFLA_RMNET_FLAGS`.
- Real-device helpers register/unregister `rmnet_rx_handler` and allocate/free `struct rmnet_port`.
- `rmnet_newlink()` creates a mux endpoint and virtual rmnet netdev on a real device.
- `rmnet_dellink()` removes a virtual endpoint, bridge state, upper links, and real-device registration when no endpoints remain.
- `rmnet_changelink()` changes mux ID and data-format flags with MTU validation/rollback.
- `rmnet_fill_info()` reports mux ID and flags to rtnetlink.
- Exported helpers: `rmnet_get_port_rcu()`, `rmnet_get_endpoint()`, `rmnet_add_bridge()`, `rmnet_del_bridge()`, and `rmnet_get_port_rtnl()`.
- Module init/exit register the netdevice notifier and rtnl link ops.

## Control Flow
Creating a link requires `IFLA_LINK` and a valid mux ID, finds the real device, allocates an endpoint, registers the real device rx handler if needed, creates the virtual rmnet device through `rmnet_vnd_newlink()`, links it as an upper device, inserts the endpoint into the mux hash bucket, and applies flags. Deletion removes bridge state first, deletes the endpoint from RCU hlist, unlinks uppers, unregisters the real device if empty, and queues virtual netdev unregister. Netdevice notifier force-cleans RMNET state on real device unregister and rejects MTU changes that invalidate attached rmnet devices.

## State and Persistence
Per-real-device `struct rmnet_port` is stored as `rx_handler_data`. Per-mux `struct rmnet_endpoint` objects live in RCU hlist buckets. Data-format flags, bridge endpoints, aggregation state, and rmnet device counts persist until link deletion or forced cleanup.

## Dependencies and Integration Points
Depends on rtnetlink, netdevice rx handlers, upper/lower device links, RCU hlist traversal, rmnet MAP handlers, virtual netdev helpers, and aggregation helpers. Userspace integrates through `ip link add/change ... type rmnet`.

## Risks and Edge Cases
- Mux ID range is 0-254 because `RMNET_MAX_LOGICAL_EP` is 255.
- Bridge mode is mutually constrained with multiplexed rmnet devices; more than one rmnet dev prevents bridging.
- Error paths must free endpoints, unregister real devices, and undo virtual device creation in the right order.
- Data-format changes roll back if resulting MTU is invalid.
- Forced unassociation must handle both real-device and bridge-device roles.
- RCU endpoint lookup requires callers to hold appropriate RCU or rtnl protection.

## Test Signals
Rtnetlink tests should cover newlink without link/mux, duplicate mux IDs, changelink mux moves, flag changes with MTU rollback, deleting endpoints, real-device unregister cleanup, bridge add/delete, and module init/exit registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_config.c -->
