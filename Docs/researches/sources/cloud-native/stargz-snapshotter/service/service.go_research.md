<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/service.go -->
# sources/cloud-native/stargz-snapshotter/service/service.go

## Purpose
Wires registry resolution, source-label parsing, filesystem construction, and snapshotter construction into reusable service constructors.

## Important APIs, Types, And Functions
- Options: `WithCredsFuncs`, `WithCustomRegistryHosts`, and `WithFilesystemOptions`.
- `NewStargzSnapshotterService` builds the filesystem and `snapshot.NewSnapshotter` with async removal and optional invalid-mount tolerance.
- `NewFileSystem` selects registry hosts, detects overlay opaque mode, and creates `stargzfs.NewFilesystem`.
- `snapshotterRoot`, `fsRoot`, `sources`, and `Supported` are helper APIs.

## Control Flow
Options are applied, registry hosts come from explicit override or resolver config plus credentials, `NeedsUserXAttr` selects trusted vs user overlay opaque semantics, source providers are chained CRI-first then default-label, external TOC decompressor support is added, and filesystem/snapshotter roots are derived under the service root.

## State And Persistence
Filesystem state is under `<root>/stargz`; snapshot metadata and overlay dirs are under `<root>/snapshotter`. Async removal defers directory cleanup to snapshotter cleanup.

## Dependencies And Integration Points
Integrates containerd snapshot interfaces, overlay utilities, stargz filesystem, layer metadata, resolver credentials, source labels, and external TOC decompression.

## Risks And Edge Cases
Failure to detect `userxattr` only logs a warning and assumes the zero value. Source provider ordering can hide default-label errors behind CRI-label errors only after CRI fails. Async removal changes when disk space is reclaimed.

## Test Signals
Signals include successful filesystem creation with configured registry hosts, correct root paths, overlay support checks, source fallback behavior, and snapshotter startup with remote snapshot restore.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/service.go -->
