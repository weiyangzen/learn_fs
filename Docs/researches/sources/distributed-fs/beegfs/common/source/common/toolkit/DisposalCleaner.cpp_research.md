<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/DisposalCleaner.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/DisposalCleaner.cpp

Purpose: Walks disposal directories on metadata nodes and optionally unlinks disposal entries.

Important APIs/functions: `run` iterates nodes and invokes `walkNode`. `walkNode` pages through disposal entries with `ListDirFromOffsetMsg`, calls an `onItem` callback, and can remove entries depending on callback result. `unlinkFile` sends `UnlinkFileMsg` for a disposal entry.

Control flow/state/persistence: The cleaner communicates with metadata nodes, tracks server offsets, and uses metadata entry IDs for disposal directories. Persistent effects occur only through remote unlink requests.

Dependencies/integration: Uses `Node`, `MessagingTk`, list-dir/unlink messages, `EntryInfo`, and metadata constants. It integrates cleanup tooling with metadata disposal state.

Risks/test signals: Remote list/unlink errors and pagination loops are key. Tests should cover empty directories, multiple pages, callback stop/delete decisions, mirrored disposal entries, communication failures, and unlink result handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/DisposalCleaner.cpp -->
