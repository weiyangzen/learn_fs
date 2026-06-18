# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht.c

## Purpose
Defines the exported xlator API for the standard DHT "distribute" translator. It binds GlusterFS FOP vectors, dump callbacks, callbacks, options, lifecycle hooks, and pass-through behavior into `xlator_api`.

## Important APIs and Types
- `dht_pt_fops`: reduced pass-through FOP set used when DHT is effectively pass-through, preserving mkdir layout creation, xattr access, and rename changelog tracing.
- `fops`: main DHT operation table covering lookup, create/mknod, directory ops, rename, locks, inode read/write ops, xattrs, allocation, discard, and zerofill.
- `dumpops`: maps private and inode-context statedump callbacks to shared DHT dump functions.
- `cbks`: registers `dht_release` and `dht_forget`; `releasedir` is intentionally commented.
- `xlator_api`: exported translator descriptor with `dht_init`, `dht_fini`, `dht_notify`, `dht_reconfigure`, `mem_acct_init`, options, identifier `"distribute"`, and maintained category.

## Control Flow
There is no algorithmic runtime logic here beyond dispatch registration. GlusterFS loads this module, reads `xlator_api`, invokes lifecycle hooks, and routes FOPs through the function pointers. The pass-through table is available for the single-child/shrunk-volume case where only a small subset of DHT-specific behavior should remain active.

## State and Persistence
The file owns no mutable state. Persistent behavior is indirect through the selected FOP implementations in other DHT files. The table selection determines which functions can mutate layouts, linkfiles, locks, xattrs, and backend data.

## Dependencies and Integration Points
Includes `dht-common.h` and references nearly every DHT FOP implementation. It integrates with the translator loader ABI via `xlator_api_t`, with shared options from `dht_options`, and with pass-through logic used after remove-brick/shrink workflows.

## Risks
- Missing or mismatched FOP assignments silently change translator behavior.
- The commented lookup/readdir pass-through entries document a known dangling-linkto tradeoff for 1x volumes.
- Pass-through rename is deliberately retained for changelog tracing; removing it would affect changelog consumers.

## Test Signals
Coverage is mostly integration-level: mounting a distribute volume and exercising each FOP verifies the dispatch table. Specific tests should confirm pass-through mode still creates layouts on mkdir, exposes xattrs, and traces rename while not unexpectedly handling lookup/readdir in the reduced table.
