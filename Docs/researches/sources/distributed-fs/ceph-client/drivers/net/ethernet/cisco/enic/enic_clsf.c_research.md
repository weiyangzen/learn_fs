<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_clsf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_clsf.c

## Purpose

`enic_clsf.c` implements ENIC classifier support, primarily IPv4 TCP/UDP 5-tuple filters used by accelerated RFS and exposed through ethtool RX classification reporting.

## Important APIs, Types, and Functions

`enic_addfltr_5t` converts `flow_keys` into a firmware `struct filter` and calls `vnic_dev_classifier(..., CLSF_ADD, ...)`. `enic_delfltr` deletes a firmware classifier filter. `enic_rfs_flw_tbl_init` initializes the ENIC RFS hash table, free count, and cleanup cursor; `enic_rfs_flw_tbl_free` stops the expiry timer, deletes hardware filters, removes nodes, and restores free count. `htbl_fltr_search` scans all buckets for a filter ID.

With `CONFIG_RFS_ACCEL`, `enic_flow_may_expire` periodically asks `rps_may_expire_flow` whether filters can be removed, and `enic_rx_flow_steer` adds or retargets filters for skb flows and RX queues.

## Control Flow

RX flow steering dissects the SKB, rejects non-IPv4 or non-TCP/UDP flows, hashes to a bucket, and locks `rfs_h.lock`. Existing flows on the same queue return `-EEXIST`; existing flows moving queues either add the new hardware filter before deleting the old one or, when table space is exhausted, delete first. New flows decrement the free count, allocate a node, add the hardware filter, and insert it in the hash bucket. The expiry timer processes `ENIC_CLSF_EXPIRE_COUNT` buckets per tick and reschedules itself every quarter second.

## State and Persistence Behavior

Classifier state is split between firmware hardware filters and the in-memory `enic->rfs_h` hash table. It persists while the netdev/device is active and is fully deleted during stop/free. It is not disk-persistent and is rebuilt by RFS traffic.

## Dependencies and Integration Points

The file depends on flow dissector keys, RPS/RFS APIs, ENIC vNIC classifier devcmds, `enic_res.h`, and the `devcmd_lock`. Ettool reads these nodes through helpers in `enic_ethtool.c`.

## Risks and Edge Cases

Free-count handling is delicate, especially when retargeting a flow and delete/add operations partially fail. If deleting an old filter fails after adding a new one, a minimal cleanup node is inserted so later expiry can retry, but it does not contain full key data. `htbl_fltr_search` is O(number of buckets plus entries). Timer shutdown must run before freeing nodes.

## Test Signals

Test RFS with TCP/UDP IPv4 flows, unsupported protocols, queue retargeting, table-full conditions, firmware add/delete failures, expiry via `rps_may_expire_flow`, ethtool rule listing/lookup, and stop/remove cleanup with outstanding filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_clsf.c -->
