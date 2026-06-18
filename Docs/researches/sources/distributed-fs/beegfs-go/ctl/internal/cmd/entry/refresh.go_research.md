
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/refresh.go

- Purpose: implements `entry refresh` to synchronize BeeGFS metadata with backing filesystem state after repair or delays.
- Important APIs: local `frontendCfg`, `newRefreshEntryInfoCmd`, and `runRefreshEntryInfoCmd`.
- Control flow/state: validates paths, supports stdin delimiter and recursive `--yes`, determines path input method, calls `entry.RefreshEntriesInfo`, prints path/status/entry ID rows, and returns backend wait errors.
- Dependencies/integration: uses BeeGFS op status, path input utility, `cmdfmt`, and entry backend refresh stream.
- Risks/tests: recursive refresh can touch many entries and is gated; status output is per-entry but no partial-success wrapping is visible here. No direct tests found.
