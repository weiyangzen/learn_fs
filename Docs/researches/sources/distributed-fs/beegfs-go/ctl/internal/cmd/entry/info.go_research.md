
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/info.go

- Purpose: implements `entry info` for table or retro details about BeeGFS entries.
- Important APIs: `entryInfoCfg`, `newEntryInfoCmd`, `runEntryInfoCmd`, `assembleRetroEntry`, and `assembleTableRow`.
- Control flow/state: selects path input method from args/stdin/recurse, streams `entry.GetEntries` results, handles verbose-detail errors as warnings, and renders either table rows or old-style vertical output.
- Dependencies/integration: uses filesystem filters, Viper debug/raw flags, `cmdfmt`, unit formatting, entry backend combined info, and logger warnings.
- Risks/tests: output has many conditionals for directories, files, mirrored metadata, RSTs, unavailable details, and verbose paths; TODO notes table verbose output is incomplete. No direct tests found.
