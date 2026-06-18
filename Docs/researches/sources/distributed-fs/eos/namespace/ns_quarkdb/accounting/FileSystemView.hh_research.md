## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemView.hh

Purpose: Declares the filesystem-view API and helper iterators for QuarkDB-backed namespace accounting. The header documents the Redis/QuarkDB set layout: `fsview:<fsid>:files`, `fsview:<fsid>:unlinked`, and the no-replica set.

Important APIs and types: `QdbFileSystemIterator` wraps a moved `std::set` of filesystem IDs discovered from backend scans. `ListFileSystemIterator` snapshots filesystem IDs from the in-memory handler map. `QuarkFileSystemView` implements `IFsView` with methods for file change notifications, consistency repair, regular/unlinked/no-replica file iterators, streaming variants, count queries, random file selection, unlinked-list cleanup, filesystem iteration, and membership checks.

State and persistence: the class owns one no-replica `FileSystemHandler`, two maps of regular and unlinked handlers keyed by filesystem ID, a folly executor shared by handlers, and an assisted cache-cleaner thread. It stores non-owning pointers to `qclient::QClient` and `MetadataFlusher`; callers must ensure their lifetime exceeds the view. Map mutex protection is explicitly scoped to map membership, not handler contents.

Dependencies and integration: depends on EOS namespace interfaces, `FileSystemHandler`, QuarkDB constants, `QClient`, `AssistedThread`, and `MetadataFlusher`. The exposed `parseFsId()` helper is part of backend-key discovery and repair tooling.

Risks and test signals: the header includes itself, which is harmless due to guards but unusual and worth watching during include cleanup. API consumers must handle `nullptr` iterators for unknown filesystems. Tests should validate iterator validity, snapshot behavior, initialization/fetch semantics, streaming list behavior, and that `finalize()`, `shrink()`, `AddTree()`, and `RemoveTree()` are intentionally no-ops for this view.
