# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/update.c

Shared data update engine used by move-path consumers such as copygc, reconcile, promote, self-heal, and scrub.

Key entry points:
- `bch2_data_update_in_flight()` checks the update rhashtable to avoid unsafe overlapping updates at the same `bbpos`.
- `ptr_mask_remap()` remaps pointer masks from an original extent to a split/reassembled extent.
- `bch2_data_update_index_update()` merges newly written replicas back into the live extent key after IO completes.
- `bch2_data_update_read_done()` transitions a completed read into write submission, scrub completion, or no-write repair.
- `bch2_can_do_data_update()` predicts whether a requested move can allocate enough durability and, for mandatory EC, whether stripe allocation is feasible.
- `bch2_data_update_init()` initializes a `struct data_update`, computes replicas needed, takes device refs, locks nocow buckets, and prepares read/write bios.
- `bch2_data_update_exit()`, `bch2_fs_data_update_init()`, and `bch2_fs_data_update_exit()` clean up individual updates and the global in-flight table.

Core behavior:
- Index updates compare the current extent with the saved old extent, cut both old/new keys to the overlapping range, drop killed/conflicting pointers, append newly written pointers, and re-run reconcile tagging before committing.
- IO-error handling can rewrite from remaining replicas, drop failed pointers without a write, or record scrub journal repairs for no-repair scrub mode.
- Unwritten extents are converted by allocating replacement unwritten pointers and updating the index without data IO.
- Durability checks distinguish user data from btree data, target-constrained writes from whole-filesystem fallback, copygc from other updates, and cached pointers from durable replicas.
- Mixed checksummed/non-checksummed extents use checksum paranoia: reads prefer the specific replica being rewritten and may rewrite only one non-cached pointer at a time.

Important invariants:
- Non-copygc updates are excluded by any in-flight update at the same position; copygc only excludes other copygc.
- Device refs are stored in `cas[]` and must not be re-derived from `c->devs[]` during cleanup because device removal may clear lookup slots while refs still pin devices.
- Updates must not replace non-cached durable data with cached data.
- During option-change windows, an update that would reduce durability can force emergency read-only.
- Nocow locks are acquired after btree locks are dropped and released on all error paths.

Dependencies and interactions:
- Uses btree transactions, extent mutation helpers, write path, read bios, foreground allocator capacity checks, EC stripe-head checks, copygc wakeups, reconcile pending marking, nocow locking, scrub repair journal, and debug trace events.
