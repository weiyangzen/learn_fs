# sources/distributed-fs/ceph-client/drivers/base/map.c

## Purpose
`map.c` implements `kobj_map`, a dev_t-to-kobject lookup table used by character/block device infrastructure to find the kobject that owns a device number.

## Important APIs, Types, And Functions
`struct kobj_map` holds 255 hash buckets of `struct probe` lists and an external mutex. Public APIs are `kobj_map()`, `kobj_unmap()`, `kobj_lookup()`, and `kobj_map_init()`. Each probe records base dev_t, range, module owner, lookup callback, optional lock callback, and data.

## Control Flow, State, And Persistence
Mapping allocates one probe entry per covered major bucket, caps bucket span at 255, initializes identical metadata, and inserts entries sorted by ascending range so narrower mappings win. Unmap removes matching range entries from every bucket and frees the allocated block once. Lookup scans the bucket for mappings covering the dev_t, pins the module, optionally calls a lock callback, drops the map mutex, invokes the probe callback, releases the module, and retries if the callback returns NULL.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include dev_t major/minor encoding, module refs, kobjects, mutexes, and callbacks from block/char device registries. Risks include poor scaling for large dev_t spaces, sorted range ordering correctness, retry behavior after callbacks mutate mappings, owner protection covering only the probe call, and freeing shared allocation from any bucket removal. Test signals include overlapping ranges preferring smaller range, lookup retry after failed probe, module ref failure, lock callback denial, unmap across multiple majors, and base probe fallback.
