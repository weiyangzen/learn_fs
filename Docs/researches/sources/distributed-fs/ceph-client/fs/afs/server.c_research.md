<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/server.c -->
# sources/distributed-fs/ceph-client/fs/afs/server.c

## Purpose
Creates, indexes, updates, references, expires, and destroys active fileserver records for a cell.

## Important APIs, Types, And Functions
Exports `afs_find_server()`, `afs_lookup_server()`, `afs_get_server()`, `afs_use_server()`, `afs_unuse_server()`, `afs_unuse_server_notime()`, `afs_put_server()`, `afs_purge_servers()`, `afs_wait_for_servers()`, and `afs_check_server_record()`. Internal helpers allocate/install UUID-indexed servers, query VLDB addresses, update address records, expire idle servers, and give up callbacks on teardown.

## Control Flow
Lookup first searches the cell UUID rb-tree under read lock. Missing records are allocated as `UNCREATED`, installed under write lock, marked `CREATING`, populated with VLDB addresses, and immediately probed. Other waiters sleep on the creating bit. Active uses cancel the idle timer; unuse schedules GC or destroy work. Address-version mismatch marks a server for update, which is serialized with `AFS_SERVER_FL_UPDATING`.

## State And Persistence
Server state includes UUID, active/ref counts, endpoint state, address version, service ID, probe lists, timers, callback-token data, volume attachments, proc/probe links, flags, and cell ref. All state is in memory and RCU-freed.

## Dependencies And Integration Points
Integrates with VL rotation/client lookup, fileserver probing, RxRPC peer appdata, callback give-up RPC, procfs server listing, volume server lists, and namespace outstanding-server waiters.

## Risks And Edge Cases
Creation failure must wake waiters with the right error. Expiration logic appears sensitive to `net->live`/cell removal conditions. Address update waits can return stale failure after retries. Peer appdata must be unbound before RCU free.

## Test Signals
Concurrent volume lookups for the same UUID, VLDB address changes, server GC after inactivity, cell purge/netns exit, callback give-up on destroy, and probe-triggered service updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/server.c -->
