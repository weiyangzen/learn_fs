
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/set.go

- Purpose: implements `entry set` for directory stripe defaults, storage pools, RSTs, and hidden file state updates.
- Important APIs: `entrySetCfg`, `newEntrySetCmd`, `runEntrySetCmd`, and `sprintfNewEntryConfig`.
- Control flow/state: validates path args, disallows mixing `--access-flags`/`--data-state` with ordinary config flags in `PreRunE`, gates recursion with `--yes`, streams `entry.SetEntries`, and prints summary/optional per-entry updates.
- Dependencies/integration: uses custom flag types, remote target flags, filesystem filters, backend `SetEntryCfg`, reflection for summary formatting, and path input utility.
- Risks/tests: reflection output depends on backend struct field names; hidden state flags mutate regular file access/data state and have stricter allowed flag combinations. No direct tests observed.
