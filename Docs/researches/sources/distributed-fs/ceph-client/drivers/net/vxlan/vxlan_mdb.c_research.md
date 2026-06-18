<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_mdb.c -->
# sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_mdb.c

## Purpose
`vxlan_mdb.c` implements VXLAN multicast database support. It lets user space program bridge-style MDB entries that map multicast IP groups, optional sources, and source VNIs to one or more VXLAN remote tunnel destinations. The datapath uses these entries to replicate eligible multicast traffic to selected remotes instead of using the generic all-zero/default FDB flooding path.

## Important APIs, Types, and Functions
- Core data types: `struct vxlan_mdb_entry_key` (`src`, `dst`, `vni`), `struct vxlan_mdb_entry` (rhashtable/list node plus remotes list), `struct vxlan_mdb_remote` (RCU `vxlan_rdst`, flags, filter mode, route protocol, source list), `struct vxlan_mdb_src_entry`, `struct vxlan_mdb_config`, and `struct vxlan_mdb_flush_desc`.
- Rhashtable configuration: `vxlan_mdb_rht_params` indexes entries by `(source address, group address, source VNI)`.
- Netlink dump/fill: `vxlan_mdb_dump()`, `vxlan_mdb_fill()`, `vxlan_mdb_entry_fill()`, `vxlan_mdb_entry_info_fill()`, and source-list helpers format RTM_NEWMDB bridge MDB payloads.
- Config parsing/validation: `vxlan_mdb_config_init()`, `vxlan_mdb_config_attrs_init()`, `vxlan_mdb_group_set()`, `vxlan_mdb_is_valid_source()`, `vxlan_mdb_config_src_list_init()`, and policy tables for set/delete/get attributes.
- Mutators: public `vxlan_mdb_add()`, `vxlan_mdb_del()`, `vxlan_mdb_del_bulk()` call internal `__vxlan_mdb_add()`, `__vxlan_mdb_del()`, `vxlan_mdb_remote_add()`, `vxlan_mdb_remote_replace()`, `vxlan_mdb_remote_del()`, and `vxlan_mdb_flush()`.
- Datapath APIs: `vxlan_mdb_entry_skb_get()` selects an MDB entry for an outgoing skb; `vxlan_mdb_xmit()` clones and sends to eligible remote destinations via `vxlan_xmit_one()`.
- Lifecycle: `vxlan_mdb_init()` initializes per-device table/list; `vxlan_mdb_fini()` flushes entries and destroys the table.

## Control Flow
MDB add/delete requests arrive through `ndo_mdb_add`/`ndo_mdb_del` registered in `vxlan_core.c`. `vxlan_mdb_config_init()` validates that the bridge MDB port is the VXLAN netdevice, entries are permanent for create/replace, VID is absent, the group is IPv4 or IPv6, and required entry attributes exist. Attribute parsing requires a remote destination IP and validates optional source, filter mode, source list, route protocol, remote port/VNI/ifindex, and source VNI.

`__vxlan_mdb_add()` gets or creates the group entry in the rhashtable/list, then adds or replaces a remote. Replacing swaps in a fresh `vxlan_rdst`, updates source filtering state, notifies RTNLGRP_MDB, then RCU-frees the old destination. For `(*,G)` entries with source lists, source forwarding entries are represented by corresponding `(S,G)` entries; INCLUDE/EXCLUDE controls whether generated source entries are blocked or active. Delete removes a remote, recursively deletes associated source-forwarding entries, sends delete notification, and drops the parent entry when no remotes remain.

Transmit lookup in `vxlan_mdb_entry_skb_get()` only considers multicast, non-broadcast Ethernet frames carrying IPv4 or IPv6. It builds an `(S,G,VNI)` key from inner IP source/destination, tries exact `(S,G)`, then `(*,G)`, then an all-zero group fallback for non-link-local multicast. `vxlan_mdb_xmit()` iterates remotes under RCU, skips blocked remotes and `(*,G)` INCLUDE remotes, clones the skb for all but one remote, and calls `vxlan_xmit_one()` with the MDB entry source VNI.

## State and Persistence Behavior
MDB state is runtime per-VXLAN-device state: `vxlan->mdb_tbl`, `vxlan->mdb_list`, `vxlan->mdb_seq`, and `VXLAN_F_MDB` in `vxlan->cfg.flags`. Entries and remotes are RCU-freed. Remote destinations own `dst_cache` objects and hold remote IP/port/VNI/ifindex. Source lists are normal hlist allocations tied to a remote. The state is not persisted across reloads; user space is expected to reprogram MDB entries.

`VXLAN_F_MDB` is enabled when the first MDB entry is inserted and disabled when the last entry is removed. `mdb_seq` changes on add/delete and is used by dump consistency checks.

## Dependencies and Integration Points
This file uses bridge MDB netlink ABI (`br_mdb_entry`, `MDBA_*`, `MDBE_*`, RTM_NEWMDB/RTM_DELMDB), rtnetlink, rhashtable, RCU lists, VXLAN address helpers from `vxlan_private.h`, and transmit support in `vxlan_core.c`. It integrates into the VXLAN netdevice operations through `ndo_mdb_*` and into the datapath through `vxlan_xmit()` checking `VXLAN_F_MDB`.

## Risks and Edge Cases
- MDB source-filter semantics are nontrivial: `(*,G)` INCLUDE entries are not directly transmitted by `vxlan_mdb_xmit()`; source-list generated `(S,G)` entries carry forwarding state. Changes must preserve this relationship.
- Remote lookup currently keys remotes by remote IP only. Remote port/VNI/ifindex are part of the stored `vxlan_rdst` and notification output, but not the remote lookup discriminator.
- Recursive source-entry add/delete can partially fail; rollback paths must remove generated source entries and not leave blocked/active state inconsistent.
- RCU pointer replacement in `vxlan_mdb_remote_replace()` must not free old destinations before readers finish.
- All-zero fallback intentionally avoids IPv4 local multicast and IPv6 link-local multicast to leave those on the default flooding path.
- Bulk delete filters only a subset of attributes and permanent state; unsupported state/protocol combinations must remain rejected.

## Test Signals
- Add, replace, get, dump, delete, and bulk-delete MDB entries for IPv4 and IPv6 groups, with and without source VNI, remote VNI, remote port, ifindex, and route protocol.
- Validate rejection of non-permanent creates, VID, non-multicast group addresses, multicast source addresses, source on all-zero group, source lists without filter mode, and empty `(*,G)` INCLUDE lists.
- Send multicast traffic through exact `(S,G)`, `(*,G)`, all-zero fallback, link-local multicast, blocked remote, INCLUDE, and EXCLUDE configurations; verify replication count and remote selection.
- Exercise replace while traffic is active to catch RCU destination lifetime issues.
- Confirm `ip mdb show`/netlink dumps remain consistent across partial dumps using `mdb_seq`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_mdb.c -->
