# sources/distributed-fs/ceph-client/fs/nfs/pnfs_dev.c

## Purpose
`pnfs_dev.c` implements the generic pNFS device-id cache. A device ID is unique per NFS client and layout type; this file hashes, looks up, fetches, inserts, removes, invalidates, temporarily marks unavailable, and purges decoded device-id nodes. Layout drivers provide the actual opaque `GETDEVICEINFO` decode via `alloc_deviceid_node()` and final free via `free_deviceid_node()`.

## Important APIs, types, and functions
`nfs4_find_get_deviceid()` is the primary lookup API: it returns a referenced `struct nfs4_deviceid_node`, fetching device info from the MDS on cache miss. `nfs4_delete_deviceid()` unhashes one node. `nfs4_init_deviceid_node()` initializes driver-allocated nodes. `nfs4_put_deviceid_node()` drops references and frees nodes when no longer cached or used. `nfs4_mark_deviceid_available()`, `nfs4_mark_deviceid_unavailable()`, and `nfs4_test_deviceid_unavailable()` implement temporary backoff after device failures. `nfs4_deviceid_purge_client()` removes all cached nodes for a client, and `nfs4_deviceid_mark_client_invalid()` marks all client nodes invalid after MDS clientid recall. Debug builds also export `nfs4_print_deviceid()`.

## Control flow
`nfs4_find_get_deviceid()` hashes the 16-byte device ID, performs an RCU lookup for the current layout driver and client, and uses `atomic_inc_not_zero()` to pin a live node. On miss, `nfs4_get_device_info()` allocates a `pnfs_device`, page vector, and reply pages sized from the NFSv4.1 session max response, calls `nfs4_proc_getdeviceinfo()`, and hands the result to the layout driver to allocate/decode a node. If the server marks the device non-cacheable, the node gets `NFS_DEVICEID_NOCACHE`.

After fetching, insertion is serialized by `nfs4_deviceid_lock`. The code rechecks the cache to avoid duplicate nodes, frees the unused new node if another thread won, or adds the new node to the RCU hlist with an extra cache reference. Deletion removes the node from the hlist under the spinlock, clears the non-cache bit, and drops the cache reference. Purge walks each hash bucket, unhashes all matching client nodes into a temporary list, then drops references outside the global lock.

Unavailable marking stores `jiffies` then sets `NFS_DEVICEID_UNAVAILABLE`; tests suppress use until `PNFS_DEVICE_RETRY_TIMEOUT` expires, after which the flag is cleared. Client invalidation is weaker: it sets `NFS_DEVICEID_INVALID` under RCU so data paths can stop trusting affected nodes.

## State and persistence behavior
The cache is a static 32-bucket RCU hash table protected by `nfs4_deviceid_lock` for mutation. Node lifetime is atomic-reference based, with one reference for cache membership and additional references for users. `NFS_DEVICEID_NOCACHE` changes put behavior so a non-cacheable node is deleted when the last non-cache user drops it. Device unavailable timestamps are volatile; no device information is persisted locally.

## Dependencies and integration points
This file depends on NFSv4 sessions for `max_resp_sz`, `nfs4_proc_getdeviceinfo()` for server fetches, layout driver decode/free callbacks, RCU hlist primitives, `pnfs.h` state flags, and `nfs4trace.h` tracepoints (`trace_nfs4_find_deviceid`, `trace_nfs4_deviceid_free`). It is invoked by layout drivers when mapping layout segments to storage devices or data servers, and by pNFS teardown/recovery in `pnfs.c`.

## Risks and test signals
Risks include duplicate insertion races, freeing a node still visible to RCU readers, incorrect handling of non-cacheable devices, leaked reply pages on partial allocation failure, stale invalid/unavailable flags, and purging while layout segments still hold references. Tests should cover concurrent lookup of the same device ID, GETDEVICEINFO failure, driver decode failure, `nocache` nodes, delete while referenced, client purge, client invalidation after lease recovery, unavailable timeout behavior, and layout-driver free callback invocation under fault injection.
