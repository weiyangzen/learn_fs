# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_arfs.c

## Purpose
`ice_arfs.c` implements accelerated Receive Flow Steering for the PF VSI when `CONFIG_RFS_ACCEL` is enabled. It converts Linux RFS flow-steer requests into ICE Flow Director perfect filters and periodically syncs pending filter additions/deletions to hardware.

## Important APIs, Types, And Functions
`ice_is_arfs_active()` checks whether the PF VSI has an ARFS hash table. `ice_rx_flow_steer()` is the netdev callback that validates an skb, extracts 4-tuple flow keys, checks Flow Director perfect-filter availability, finds or creates an `ice_arfs_entry`, updates queue selection, and schedules the service task. `ice_sync_arfs_fltrs()` scans all hash buckets, builds temporary add/delete lists under `arfs_lock`, then performs hardware programming outside the spinlock.

Hardware add/delete is performed by `ice_arfs_add_flow_rules()` and `ice_arfs_del_flow_rules()` through `ice_fdir_write_fltr()`. Active counters are maintained by `ice_arfs_update_active_fltr_cntrs()` and queried by `ice_is_arfs_using_perfect_flow()` so Flow Director can avoid conflicts. `ice_arfs_is_flow_expired()` uses `rps_may_expire_flow()` and a five-second UDP activation window. Initialization and teardown are handled by `ice_init_arfs()`, `ice_clear_arfs()`, `ice_remove_arfs()`, and `ice_rebuild_arfs()`.

## Control Flow
On initialization, the PF VSI allocates a 1024-bucket hlist table, active counters, last-filter-id atomic, and spinlock. When the networking stack asks to steer a flow, the driver rejects encapsulated, unsupported, fragmented IPv4, non-TCP/UDP, or unavailable perfect-flow cases. Existing active entries with a changed queue are marked inactive and their active counter is decremented. New entries are inserted as inactive. The service task later transitions inactive entries to active and programs Flow Director rules; expired active entries move to delete lists and are removed from hardware and memory.

## State And Persistence
State is runtime-only in the PF VSI: `arfs_fltr_list`, `arfs_fltr_cntrs`, `arfs_lock`, and `arfs_last_fltr_id`. Each entry stores Flow Director filter info, hlist node, optional UDP activation time, Linux flow id, and state (`INACTIVE`, `ACTIVE`, `TODEL`). Filter IDs wrap modulo `RPS_NO_FILTER`.

## Dependencies And Integration Points
The file depends on Linux RFS/RPS, skb flow dissector, IP/IPv6/TCP/UDP parsing, netdev CPU rmap support, ICE Flow Director programming, service task scheduling, and PF/VSI definitions from `ice.h`.

## Risks And Test Signals
Risks include active counter imbalance on update/delete failures, stale entries after reset, memory allocation under `GFP_ATOMIC`, races around hash-table mutation, UDP expiration timing, and conflicts with user-programmed Flow Director perfect filters. Test signals include `CONFIG_RFS_ACCEL` builds, `ndo_rx_flow_steer` behavior, RFS CPU rmap setup, Flow Director add/delete success, reset rebuild cleanup, and traffic steering moving flows to expected Rx queues.
