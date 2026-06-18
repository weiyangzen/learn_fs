# sources/distributed-fs/ceph-client/drivers/md/dm-snap-transient.c

## Purpose
Implements the volatile snapshot exception store. It allocates COW chunks linearly in memory and performs no metadata IO, so exceptions are lost at teardown or reboot.

## Important APIs, Types, And Functions
`struct transient_c` stores only `next_free`. Store methods are `transient_ctr()`, `transient_dtr()`, `transient_read_metadata()`, `transient_prepare_exception()`, `transient_commit_exception()`, `transient_usage()`, and `transient_status()`. It registers names `transient` and `N`.

## Control Flow
Constructor allocates context and sets `next_free` to zero. Metadata read returns success without loading exceptions. Prepare checks COW capacity, converts `next_free` to `e->new_chunk`, and advances by chunk size. Commit immediately invokes the snapshot callback with the supplied validity result.

## State And Persistence
State is in-memory only. `transient_usage()` reports allocated sectors from `next_free`, total COW sectors, and zero metadata sectors. There is no merge support and no recovery.

## Dependencies And Integration Points
Depends on `dm-exception-store.h`, `dm_snap_cow()`, and the exception-store registry. `dm-snap.c` uses it for normal snapshot COW but rejects it for snapshot-merge because merge hooks are absent.

## Risks
COW exhaustion returns a nonzero failure rather than preserving detailed errno. Users must not expect persistence. Capacity accounting relies on chunk-aligned sector increments.

## Test Signals
Create `N` and `transient` snapshots, perform origin and snapshot writes, verify status allocation and zero metadata sectors, reload to confirm exceptions are not preserved, and check snapshot-merge rejection.
