# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/entry.go

Purpose: core backend for retrieving BeeGFS entry metadata, owner nodes, verbose storage paths, file state, access flags, and Remote target IDs.

Important APIs/types/functions: `GetEntriesCfg`; `GetEntryCombinedInfo`; `Entry`; `EntryDetails`; `patternConfig`; `remoteConfig`; `newEntry`; `Verbose`; `newVerbose`; `GetEntries`; `GetEntry`; `GetEntryAndOwnerFromPath`; ioctl/RPC helpers; `getPrimaryMetaNode`; `GetFileDataState`; `SetFileDataState`; `GetFileAccessFlags`; `SetAccessFlags`; `ClearAccessFlags`; `SetFileRstIds`; `SetDirRstIds`.

Control flow: `GetEntries` wraps path processing and calls `GetEntry`. `GetEntry` resolves entry and owner via ioctl when mounted or RPC when unmounted/no ioctl, fetches full `GetEntryInfoResponse` if needed, builds a combined entry, optionally fetches parent data for verbose paths, and returns structured details. The ioctl path first tries `GetEntryInfoV2` with a one-minute unavailable probe cache, falls back to opening files/directories and `GetEntryInfo`, handles special file types through parent `LookupIntent`, and falls back to RPC on locked regular files. The RPC path walks from root with `FindOwnerRequest` shortcuts up to 128 steps. State setters fetch current file state, compute a new bit field, send `SetFileStateRequest`, and retry once on inode-lock conflicts.

State and persistence: reads live metadata and file state. `SetFileDataState`, access flag setters, `SetFileRstIds`, and `SetDirRstIds` mutate metadata on owner nodes. Global probe cache records ioctl availability. Uses cached mappings and node store from config/util.

Dependencies and integration points: central integration point for filesystem provider, ioctls, BeeMsg TCP requests, mapping cache, BeeRemote RST protobufs, common BeeGFS types, path processing, zap logging, and Unix syscalls.

Risks: many paths require initialized global BeeGFS client and node store. Unmounted/RPC path requires root. `GetEntryInfoV2` fallback behavior must avoid triggering automatic restore on older clients, which is why probe caching matters. Special file handling opens parent directories and performs lookup; concurrent path mutation can produce depth or lookup errors. `SetAccessFlags` retry recomputes `info` but compares against the pre-retry `fs` value, so concurrent state changes deserve careful review. `SetDirRstIds` treats `NOTADIR` as non-fatal despite checking type earlier.

Test signals: no direct tests in this subset. Needed coverage includes ioctl V2 success/unavailable/error, special file lookup, RPC traversal, buddy mirrored owner resolution with mapping refresh, nil `Details` handling, state setter retry behavior, and RST setters.
