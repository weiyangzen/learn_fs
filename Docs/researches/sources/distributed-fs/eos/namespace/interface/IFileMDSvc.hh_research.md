## sources/distributed-fs/eos/namespace/interface/IFileMDSvc.hh

Purpose: Defines the service interface for file metadata storage, id allocation, cache management, listener notification, quota/accounting integration, and file enumeration.

Important APIs and types: `TreeInfos` accumulates tree-size/file/container deltas and supports negation/addition. `IFileMDChangeListener` reports file changes, reads, checks, and tree add/remove. `IFileVisitor` supports full scans. `IFileMDSvc` exposes lifecycle, async/sync fetch, existence check, cache drop, create/update/remove, counts, listeners, quota stats, container service wiring, visits, first-free-id, cache stats, and id blacklist.

Control flow: concrete implementations fetch or create `IFileMD`, persist updates/removals, notify listeners with `Event`, and support scans/blacklisting during startup or migration.

State and persistence: service implementations own file metadata persistence and cache state. Tree delta events propagate to container accounting/quota.

Dependencies and integration: depends on file/container metadata, identifiers, misc cache statistics, `MDException`, `MDLocking`, and folly futures. Used by `IView`, filesystem view, quota stats, and prefetcher.

Risks: `removeFile` comment requires callers to write-lock before removal, but the type system does not enforce it. Listener callbacks can be order-sensitive and may observe partially updated state if implementations are careless.

Test signals: async/sync fetch, `hasFileMD`, create/update/remove persistence, listener event contents, tree delta math, visitor scans, cache drop/stats, blacklist behavior, and write-lock precondition tests.
