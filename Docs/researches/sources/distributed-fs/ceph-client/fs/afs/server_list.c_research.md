<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/server_list.c -->
# sources/distributed-fs/ceph-client/fs/afs/server_list.c

## Purpose
Builds and manages replaceable per-volume fileserver lists derived from VLDB records.

## Important APIs, Types, And Functions
Exports `afs_put_serverlist()`, `afs_alloc_server_list()`, `afs_annotate_server_list()`, `afs_attach_volume_to_servers()`, `afs_reattach_volume_to_servers()`, and `afs_detach_volume_from_servers()`. It works with `afs_server_list`, `afs_server_entry`, VLDB masks/flags, and volume/server attachment lists.

## Control Flow
Allocation filters VLDB server entries by requested volume type, applies `DONTUSE` exclusions, handles RO replication `NEWREPSITE` cutover when at least half usable sites are updated, looks up each fileserver, and insertion-sorts by UUID while deduplicating. Attach/reattach/detach maintain each server’s sorted `volumes` list under the cell volume-server lock.

## State And Persistence
Server lists are refcounted and RCU-freed. Entries retain active server uses while the list lives and carry per-volume flags and callback expiry. Attach state records whether list entries are linked into server volume lists.

## Dependencies And Integration Points
Depends on VLDB entry parsing, `afs_lookup_server()`, cell `vs_lock`, volume replacement in volume management, rotation server selection, and validation callback expiry state.

## Risks And Edge Cases
RO replication cutover policy directly affects consistency during `vos release`. Duplicate server UUIDs, empty usable lists, server lookup failures, and reattach diff logic can break failover or callback propagation.

## Test Signals
VLDB records with RW/RO/BK masks, `DONTUSE`, `NEWREPSITE`, duplicate servers, no servers, server-list replacement, and callback expiry preservation during reattach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/server_list.c -->
