# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/set.go

## Purpose
Applies entry metadata updates such as directory stripe pattern, chunksize, pool, remote storage target settings, remote cooldown, and file access/data state. It centralizes validation and dispatches to directory, file, or file-state update paths.

## Important APIs, Types, And Functions
Exports `SetEntryCfg`, `SetEntryResult`, and `SetEntries`. Internal helpers include `setEntry`, `handleDirectory`, `handleFile`, and `handleFileStateUpdate`. `setFileStateIoctl` is a `probecache` used to avoid repeatedly trying unsupported client ioctls.

## Control Flow
`SetEntries` validates effective-user permissions once, fetches mappings while tolerating missing RST mappings, and streams paths through `util.ProcessPaths`. `setEntry` loads entry metadata and a node store. File state changes (`AccessFlags`/`DataState`) are routed separately and only allowed for regular files. Directories are updated with `SetDirPatternRequest` after merging requested changes into current pattern/RST config and validating pool/pattern compatibility unless forced. Non-directories can currently update only RST fields using `SetFilePatternRequest`.

`handleFileStateUpdate` computes the desired combined file state, returns success with no updates if unchanged, tries `ioctl.SetFileState` when the cached probe permits it, then falls back to `SetFileStateRequest` RPC and marks the ioctl unavailable after failures.

## State And Persistence
Persistent effects occur on metadata servers: directory pattern/pool/RST fields, file RST fields, and regular-file state. Local state includes `actorEUID` embedded into the config after validation and the global `setFileStateIoctl` availability cache with a five-minute reprobe window.

## Dependencies And Integration Points
Uses entry lookup helpers, `config.NodeStore`, `config.BeeGFSClient`, `util.Mappings`, management-derived pool config, BeeMsg metadata update requests, `common/ioctl`, `common/filesystem`, and `probecache`.

## Risks And Edge Cases
`SetEntryCfg` contains an internal `actorEUID` pointer and is unsafe to call through `setEntry` directly without `setAndValidateEUID`. Non-root local validation blocks root-only updates before server-side policy, while chunksize/pattern permissions are partly delegated to metadata server behavior. Directory pool/pattern compatibility uses mappings that may be stale. Ioctl fallback caches unavailability globally, so a transient mount/config error can force RPC use for up to five minutes. `handleDirectory` accepts `OpsErr_NOTADIR` as a non-error response even though the path was previously classified as a directory, which may reflect race handling.

## Test Signals
No direct tests in this file. Strong tests would mock metadata entry details, pool eligibility, non-root validation, unchanged file-state short-circuit, ioctl success/failure, and RPC fallback.
