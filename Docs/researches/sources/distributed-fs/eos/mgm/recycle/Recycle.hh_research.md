<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/Recycle.hh -->
# sources/distributed-fs/eos/mgm/recycle/Recycle.hh

## Purpose
`Recycle.hh` declares the recycle-bin subsystem interface and its background cleanup object. It exposes static command-style operations for configuration, listing, restoring, purging, project setup, restore-key lookup, and path demangling, plus instance methods for running the recycler thread and reading policy state.

## Important APIs and types
- `Recycle::RecycleListing` is a vector of string maps used by listing callers needing structured results.
- Static strings define recycle namespace layout and xattr keys: prefix, recycle attribute, directory postfix, version key, recycle-id xattr key.
- `Config()`, `RecycleIdSetup()`, `Print()`, `Restore()`, `GetPathFromRestoreKey()`, `DemanglePath()`, and `Purge()` are the command-facing static API.
- `InRecycleBin()` and `IsTopRecycleBin()` are lightweight path predicates.
- Constructor accepts `fake_clock` for testable time behavior; destructor calls `Stop()`.
- `Start()` and `Stop()` manage an `AssistedThread` running `Recycler()`.
- `NotifyConfigUpdate()`, `GetCollectInterval()`, `Dump()`, `IsEnforced()`, and `IsEnabled()` expose policy/runtime state.
- Private helpers include restore authorization, subtree removal, symlink handling, candidate collection/removal, and cutoff-date calculation.

## Control flow and state model
The header shows a hybrid design: most user operations are static and operate through MGM globals, while one `Recycle` instance owns the background thread, `RecyclePolicy`, pending deletion map, fakeable clock, and config-update condition variable. `Stop()` notifies the condition variable before joining, which prevents shutdown from waiting for a long remove interval.

`mPendingDeletions` maps container ids to full paths, allowing removal to be distributed by id. `mPolicy` stores atomics for enable/enforce/keep/ratio/dry-run/interval/watermark settings. Test harness builds can access internals through the `IN_TEST_HARNESS` public section.

## Persistence behavior
The header identifies persistence via namespace xattrs and recycle directory paths rather than an external database. The instance state is transient; on restart, pending deletions are discovered again by scanning the recycle tree. Policy persistence is delegated to `RecyclePolicy`.

## Dependencies and integration points
The declaration depends on `Namespace.hh`, `RecyclePolicy`, `AssistedThread`, `SystemClock`, generated `Recycle.pb.h`, XRootD strings, and virtual identity types. It is integrated with MGM master lifecycle, user/gRPC recycle commands, rm command recycling, quota policy, ACLs, and namespace filesystem operations.

## Risks and test signals
The static API makes permission and prefix validation central: callers can invoke powerful restore/purge/config operations without constructing a `Recycle` object. Unit tests already use `fake_clock` and `IN_TEST_HARNESS` for cutoff-date and demangle behavior. Further tests should target `Stop()` wakeup, `IsTopRecycleBin()` trailing slash normalization, `InRecycleBin()` prefix pitfalls, and config update notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/Recycle.hh -->
