# sources/distributed-fs/ceph/src/osd/PGTransaction.h

## Purpose
`PGTransaction.h` defines `PGTransaction`, the PG-backend-level transaction description consumed by replicated and erasure-coded backends. It records object creation/removal/clone/rename intent, data writes, zeros, clone ranges, truncates, attr and omap mutations, snap updates, allocation hints, and object-context references in a normalized form that backends can traverse safely.

## Important APIs and Types
- `PGTransaction::obc_map` maps `hobject_t` to `ObjectContextRef` for object contexts touched by the transaction.
- `ObjectOperation::InitType` is a variant over `None`, `Create`, `Clone{source}`, and `Rename{source}` describing how an object is initialized.
- `delete_first` distinguishes deletion of an existing object before recreation from creation of a new object.
- Object-operation predicates `deletes_first()`, `is_delete()`, `is_none()`, `is_fresh_object()`, `is_rename()`, and `has_source()` expose transaction topology to backends.
- Mutation fields include `clear_omap`, `truncate`, `attr_updates`, `omap_updates`, `omap_header`, `updated_snaps`, `alloc_hint`, and interval-mapped `buffer_updates`.
- `BufferUpdateType` is a variant over `Write{buffer,fadvise_flags}`, `Zero{len}`, and `CloneRange{from,offset,len}`.
- Public mutation methods include `create`, `clone`, `rename`, `remove`, `update_snaps`, `omap_clear`, `truncate`, `setattrs`, `setattr`, `rmattr`, `set_alloc_hint`, `write`, `clone_range`, `zero`, `omap_setkeys`, `omap_rmkeys`, `omap_rmkeyrange`, `omap_setheader`, `nop`, `empty`, `get_bytes_written`, and `safe_create_traverse`.

## Control Flow
Callers build a `PGTransaction` by requesting an `ObjectOperation` for each modified object. Creation methods assert the target is empty or delete-first, then set the initialization variant. `rename()` requires a temp source and non-temp target; if the source already has an operation, it moves that operation to the target while preserving whether the target must be deleted first. `remove()` either converts an existing-object operation to delete-first or erases a fresh non-rename object operation as a no-op.

Data writes are stored in an `interval_map` so overlapping and adjacent updates are split and merged deterministically. `SplitMerger::split()` slices writes, zeros, or clone ranges; `can_merge()` allows adjacent writes with matching fadvise flags and adjacent zeros; `merge()` concatenates buffers or zero lengths and refuses clone-range merging. `truncate()` erases buffer updates beyond the truncation offset and tracks both the lowest and final truncate offsets.

`safe_create_traverse()` builds a source-to-destination graph from clone and rename edges, seeds roots from operations without sources plus external sources referenced by operations, then performs post-order traversal so sinks are visited before sources. This ordering lets backends create clone/rename targets before operations that could mutate their sources.

## State and Persistence Behavior
`PGTransaction` is an in-memory planning structure; it does not persist itself. Backends translate its operations into `ObjectStore::Transaction` or EC-specific subtransactions. The state model is designed to preserve enough intent for EC rollback/stash decisions: delete-before-create, clone/rename source identity, snap-only updates, truncation history, and exact byte ranges are all kept separate until backend generation.

Buffer and omap payloads are stored as `ceph::buffer::list` values. Some methods copy and rebuild buffers (`setattrs`, `setattr`) to avoid pinned larger buffers; omap set/remove/range methods encode key maps or sets into bufferlists for backend consumption. `get_bytes_written()` sums only buffer update lengths, not omap/attr/header sizes.

## Dependencies and Integration Points
- Depends on `hobject_t`, `ObjectContextRef`, `interval_map`, `inline_variant::match`, Ceph bufferlists, snap IDs, and OSD internal types or Crimson object contexts depending on `WITH_CRIMSON`.
- Used by `ECTransaction`, `ECCommon`, `ECSwitch`, and backend code to generate concrete object-store work from PG-level operations.
- The file's constraints are tuned for `PrimaryLogPG` and ECBackend workflows such as copy-from rename, make-writeable clone, rollback clone-to-head, and combined clone/rollback sequences.

## Risks and Edge Cases
- The transaction graph must be acyclic and each source can have at most one sink. Violations can lead to traversal errors or assertions.
- `clone_range` sources must not be modified by the same transaction; the class documents this but relies on callers/backends to respect it.
- `remove()` on a fresh object erases the operation as a no-op, but removing a rename target is asserted against; callers must sequence rename/remove carefully.
- `update_snaps()` asserts there are no buffer updates or truncate, so combining snap-only and data mutations on the same operation is invalid.
- `truncate()` stores both lowest and final truncate offsets; backends must interpret the pair correctly when multiple truncates occur.
- `setattrs()`/`setattr()` assign optional bufferlists and call `rebuild()`, which is important for memory pinning; future methods adding buffers should follow the same pattern.
- `omap_rmkeyrange()` takes non-const string references even though it only encodes them, which can surprise callers expecting const inputs.

## Test Signals
Focused tests should cover overlapping writes/zeros/clone ranges in the interval map, truncate interaction with prior writes, rename moving source operations to target, remove-after-create no-op behavior, snap-update assertions, byte-count accounting, and `safe_create_traverse()` ordering for copy-from, make-writeable, rollback, and combined clone/rollback graphs. Integration tests should validate EC transaction generation from this structure through `ECTransaction` and `ECCommon`.
