
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/disposal.go

- Purpose: implements `entry dispose-unused` for cleaning unlinked-but-open disposal files.
- Important APIs: `entryDisposalCfg`, `newEntryDisposalCmd`, and `runEntryDisposalCmd`.
- Control flow/state: calls `entry.CleanupDisposals`, consumes result and error channels, prints optional per-entry rows, and summarizes disposed versus total files.
- Dependencies/integration: uses `types.MultiError`, `beegfs.OpsErr_SUCCESS`, and backend disposal cleanup.
- Risks/tests: concurrent result/error channels require draining buffered results after errors; disposal mutates filesystem state only with `--dispose`, otherwise dry runs. No local tests found.
