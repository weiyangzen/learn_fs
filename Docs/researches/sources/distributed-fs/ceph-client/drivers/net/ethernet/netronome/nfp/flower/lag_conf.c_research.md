# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/lag_conf.c

## Purpose
This file synchronizes Linux bonding/LAG state to NFP Flower firmware and provides LAG action metadata to the action compiler and tunnel neighbor code. It tracks offloadable bond groups, assigns firmware group IDs/instances, batches configuration control messages, handles firmware retransmission/sync requests, and reacts to netdev LAG events.

## Important APIs, types, and functions
- `struct nfp_flower_cmsg_lag_config` is the firmware control payload containing flags, packet number, batch version, group ID/instance, and active member port IDs.
- `struct nfp_fl_lag_group` tracks one bond master, group ID/instance, dirty/offloaded/remove/destroy flags, and slave count.
- `nfp_flower_lag_populate_pre_action()`, `nfp_flower_lag_get_info_from_netdev()`, and `nfp_flower_lag_get_output_id()` expose group metadata to action/tunnel code.
- `nfp_fl_lag_do_work()` builds batched config/delete messages from dirty groups.
- `nfp_flower_lag_unprocessed_msg()` handles firmware DATA/XON/SYNC retransmission protocol.
- `nfp_flower_lag_netdev_event()` dispatches `NETDEV_CHANGEUPPER`, `NETDEV_CHANGELOWERSTATE`, and `NETDEV_UNREGISTER`.
- `nfp_flower_lag_reset()`, `_init()`, and `_cleanup()` manage LAG subsystem lifecycle.

## Control flow
Change-upper events verify the upper is a LAG master, all slaves are NFP representors from the same app, and firmware-supported bond mode/hash is used. They create or update a group, mark it dirty, and schedule delayed work. Lower-state events update per-representor link/tx flags and mark the group dirty. The work item walks groups under lock, sends delete messages for removals, computes active members for dirty valid groups, sends one message per group, then sends a batch-end sync message if any group was configured. Firmware can ask the host to store unprocessed DATA messages, flush them with XON, or perform a full SYNC reset/resend.

## State and persistence
State is volatile in `struct nfp_fl_lag`: delayed work, group list, mutex, IDA allocator, retransmission skb queue, packet number, batch version, global instance, and reset flag. Group IDs 1-31 are allocated with IDA; group 0 is reserved for sync. Batch version skips zero and increments by two because firmware ignores the LSB.

## Dependencies and integration points
The file depends on Flower cmsg allocation/transmit, representor port IDs, Linux bonding/LAG notifier data, delayed work, IDA, skb queues, and action structs from `cmsg.h`. `action.c` uses pre-LAG data for LAG output actions, while `main.c` calls LAG init/reset/event/cleanup based on firmware feature negotiation.

## Risks
LAG correctness depends on netdev notifier ordering and deferred work. If slave count changes while work runs, the group is skipped until later notifications. Retransmission storage is capped at 100 skbs and drops excess, relying on firmware to request a full resync. Group removal/destroy must not free IDs while firmware still references stale groups. Unsupported bond modes must fall back cleanly.

## Test signals
Test active-backup and supported hash modes, unsupported tx/hash rejection, adding/removing representor slaves, mixed-device bonds, lower-state link/tx changes, group ID exhaustion, delete and unregister paths, firmware DATA/XON/SYNC messages, reset on app start, and LAG action compilation requiring an existing group.
