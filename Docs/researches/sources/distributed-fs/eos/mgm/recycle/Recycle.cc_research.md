<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/Recycle.cc -->
# sources/distributed-fs/eos/mgm/recycle/Recycle.cc

## Purpose
`Recycle.cc` implements EOS MGM recycle-bin management: background retention cleanup, listing, restore, purge, configuration commands, recycle-project id setup, path demangling, and utility handling for symlink-like directory listings. It is a master-only subsystem started by `QdbMaster::SlaveToMaster()`.

## Important APIs and functions
- Static configuration/state: `gRecyclingPrefix` (`/recycle/` before MGM proc prefix adjustment), `gRecyclingAttribute` (`sys.recycle`), directory postfix `.d`, version key `sys.recycle.version.key`, project recycle-id key `sys.forced.recycleid`, root identity `mRootVid`, and `mLastRemoveTs`.
- Local helper `AllHierarchyHasXattr()` verifies every directory in a subtree has a given xattr/value, excluding version directories via `_find` options.
- `CollectEntries()` periodically scans the recycle prefix, selects old date shards and empty upper directories based on `GetCutOffDate()`, and populates `mPendingDeletions` by container id/path.
- `RemoveEntries()` spreads deletion across remove intervals using `cid % total_slots`, honors dry-run, and stops early if quota watermarks are back within limits.
- `RemoveSubtree()` recursively finds and permanently deletes files and directories under a recycle subtree, deepest first, with guards against deleting `/` or paths outside the recycle prefix.
- `GetCutOffDate()` computes a date string from the current clock minus keep time minus one extra day.
- `Recycler()` is the assisted background thread: waits for namespace boot, applies recycle config, sleeps on config update or timeout, checks master/enabled state, refreshes ratio watermarks, and runs collection/removal when keep-time is configured and watermarks require cleanup.
- `Print()` lists recycle contents or summary quota data. It supports all/admin listing, per-user listing, recycle-id listing, project-path filtering, date filtering, monitoring output, optional details, max entries, id translation, and dtrace display.
- `IsAllowedToRestore()` allows user recycle restores only for the owning uid and otherwise checks parent directory ACL read permission.
- `GetPathFromRestoreKey()` resolves `fxid:<hex>` or `pxid:<hex>` keys to file/container paths and verifies the object is under the recycle prefix.
- `DemanglePath()` converts flattened `#:#` names plus `.hexid`/`.d` suffix back to original paths.
- `Restore()` resolves a recycle key, checks permissions, reconstructs original path, optionally creates missing parents, handles conflicts by renaming existing targets when forced, renames the recycled object back, and optionally restores versions through the stored version key.
- `Purge()` permanently deletes one recycle key or a dated subtree, restricted to root/sudo/admin roles.
- `Config()` handles root-only recycle commands for adding/removing recycle xattrs, lifetime, ratio, collect/remove intervals, dry-run, enforce, and enable flags. It delegates policy storage to `RecyclePolicy::Config()` and wakes the recycler.
- `RecycleIdSetup()` creates a project recycle directory, applies optional ACLs, and propagates `sys.forced.recycleid` recursively across a project subtree with verification retries.
- `HandlePotentialSymlink()` strips `" -> target"` suffixes only when the full displayed name does not stat, allowing recycle operations to target symlink entries.

## Control flow
The background recycler starts via `Start()` in the header and enters `Recycler()`. After namespace boot and initial config application, it sleeps until a config update or calculated timeout. Only the master runs cleanup. When enabled, ratio configuration first refreshes watermarks from quota statistics. If keep time is nonzero and current usage is not within ratio limits, the thread collects candidates and removes a bounded slot of them.

Interactive flows use static methods. Listing builds a `printmap` of `uid:<id>` or `rid:<id>` top-level directories based on caller privileges and arguments, then either walks detailed entries to reconstruct restore metadata or prints recycle quota summary from `Quota::GetGroupStatistics()`. Restore and purge both first resolve safe recycle paths, reject paths outside the recycle prefix, and then delegate to MGM filesystem operations using `mRootVid`.

Project setup starts from a real namespace container, rejects proc hierarchy paths, chooses an existing or container-id-based recycle id, creates `/recycle/rid:<id>`, applies ACLs through `AclCmd`, recursively sets the xattr, and verifies propagation with repeated `_find` scans.

## State and persistence
Recycle entries are persisted as renamed namespace objects under the recycle prefix with path layout `<prefix>/<uid:...|rid:...>/<year>/<month>/<day>/<shard>/<mangled-original>.<16hex>[.d]`. Directory entries use `.d`. The recycle path itself is returned through `XrdOucErrInfo` by `RecycleEntry::ToGarbage`.

Policy state is persisted through `RecyclePolicy::StoreConfig()` in FsView global config. Recycle configuration by subtree uses recursive xattrs with key `sys.recycle`; recycle projects use `sys.forced.recycleid`. Version restoration links use `sys.recycle.version.key`. Cleanup candidate state `mPendingDeletions` is in-memory only and recomputed by collection.

## Dependencies and integration points
The file depends on `XrdMgmOfs` filesystem operations, `FsView`, ACL parsing/commands, quota statistics, QDB master role checks, MGM proc commands, namespace prefetchers, container iterators, common path/string utilities, and `BackOffInvoker`. Callers include `proc/user/RecycleCmd.cc` and gRPC namespace recycle methods. `proc/user/Rm.cc` and `RmCmd.cc` use `RecycleEntry::ToGarbage()` for moving deleted objects into the structure this file manages.

## Risks and edge cases
- Destructive cleanup uses root identity and recursive deletion. The prefix guard in `RemoveSubtree()` is critical; any change to prefix normalization must preserve it.
- `Print()` summary divides by quota maximums without local zero guards in the formatting branch; empty or zero quota maps need careful handling.
- `GetPathFromRestoreKey()` declares an outer `fmd` but shadows it with `auto fmd` inside the file lookup block, so the later `if (!force_file && !fmd)` tests the still-null outer pointer. That means container lookup is attempted even after file lookup succeeded unless `force_file` is true; normally the already-filled `recycle_path` still saves behavior, but this is a concrete code smell.
- Date filters only validate digits and `/`, not semantic date shape. This avoids injection but may still produce broad or empty scans.
- Cleanup scheduling by `cid % total_slots` spreads load but can leave items pending if collection/removal intervals are misconfigured or ids cluster.
- `RecycleIdSetup()` retries xattr propagation but concurrent namespace mutations can still race with verification.
- Restore conflict handling renames existing targets with their inode suffix; failure leaves the recycled object untouched but may already have created parent paths.

## Test signals
`sources/distributed-fs/eos/unit_tests/mgm/RecycleTests.cc` covers `GetCutOffDate()` with a fake clock and `DemanglePath()` for invalid paths and encoded file names. More coverage is warranted for restore-key resolution, forced restore conflict behavior, purge permission checks, project recycle-id propagation, symlink display handling, and recycler cleanup slot/watermark behavior. Integration signals include user recycle commands, gRPC recycle methods, and rm command paths that send objects to garbage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/Recycle.cc -->
