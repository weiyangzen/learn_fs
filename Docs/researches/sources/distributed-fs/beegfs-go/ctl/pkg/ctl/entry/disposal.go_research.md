# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/disposal.go

Purpose: lists or unlinks metadata disposal entries across metadata nodes, including mirrored disposal directories.

Important APIs/types/functions: `DisposalCfg`; `DisposalResult`; `CleanupDisposals`; `disposalCleaner.run`; `disposalCleaner.walkNode`; constants `disposal`, `mdisposal`, and `disposalMaxOutNames`.

Control flow: initialization gets logger, node store, buddy groups, and a meta buddy-group-to-primary-node map, then starts a goroutine. The cleaner iterates metadata nodes, walks non-mirrored disposal entries on each, and walks mirrored entries only on primary nodes. `walkNode` pages with `ListDirFromOffsetRequest` up to 50 names at a time, optionally sends `UnlinkFileRequest` for each entry, emits results, and stops when fewer than max names are returned.

State and persistence: read-only by default; with `Dispose` true it unlinks disposal entries on metadata servers.

Dependencies and integration points: uses BeeMsg node store requests, buddygroup listing, util mapping, logger, and BeeGFS metadata node IDs.

Risks: disposal cleanup is destructive when enabled. Fatal RPC errors stop all processing. Delete response operation errors are returned as per-entry results rather than fatal. Paging assumes the server offset remains valid while entries may be deleted. Mirrored walking relies on primary mapping to avoid duplicate deletion.

Test signals: no direct tests. Useful tests would mock node store pages, dispose vs list behavior, mirrored primary filtering, delete result handling, and fatal list/unlink request errors.
