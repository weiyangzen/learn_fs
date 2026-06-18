# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efclib.c

## Purpose
`efclib.c` initializes and destroys shared libefc runtime resources and documents the broad locking model for discovery state transitions.

## Important APIs, Types, And Functions
`efcport_init` initializes `efc->lock`, vport and pending-frame lists, pending-frame lock, node mempool, node DMA pool, and ELS I/O mempool. `efcport_destroy` purges pending domain-level frames and destroys pools. `efc_purge_pending` frees held hardware sequences through `efc->tt.hw_seq_free`.

## Control Flow And State
Initialization is sequential: core locks/lists first, then node object pool, node DMA pool, then ELS I/O pool. Destroy purges held receive frames before releasing pools. The top comment explains that libefc uses broad locking around base-driver entry points because discovery state is not on the hot I/O path.

## Dependencies And Integration Points
The file depends on Linux mempool and DMA pool APIs, base-driver sequence-free callbacks, and constants from `efc.h`/`efclib.h`. It must run before any domain/node/ELS allocation and after all live objects have been shut down.

## Risks And Test Signals
Risks include cleanup gaps on partial init failure: if ELS I/O pool creation fails, the node pool and DMA pool are not both unwound in the visible path. Destroy assumes pools were initialized and no active objects remain. Test signals include init fault injection for each allocation step, destroy after pending-frame accumulation, and lockdep checks around libefc entry points.
