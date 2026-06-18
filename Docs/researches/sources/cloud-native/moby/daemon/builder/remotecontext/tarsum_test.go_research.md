# sources/cloud-native/moby/daemon/builder/remotecontext/tarsum_test.go

## Purpose
Tests the archive-backed remotecontext source created by `FromArchive`, including root cleanup, path hashing, subdirectory hashing, and removal of files/directories from the unpacked context.

## Important APIs, Types, And Functions
Defines constants `filename` and `contents`, `TestMain` for `reexec.Init`, tests `TestCloseRootDirectory`, `TestHashFile`, `TestHashSubdir`, `TestRemoveDirectory`, and helper `makeTestArchiveContext`.

## Control Flow
Tests build temporary filesystem content, tar it with `archive.Tar`, pass the stream to `FromArchive`, and then call `Close`, `Hash`, or `Remove`. Hash tests compare fixed SHA256 strings. Removal tests cast to `modifiableContext` and assert the path disappears from the extracted root.

## State And Persistence
`FromArchive` extracts into a temporary root owned by the source; `Close` removes it. Tests require root and skip otherwise, reflecting archive ownership/permission semantics.

## Dependencies And Integration Points
Depends on `github.com/moby/go-archive`, `compression.None`, builder source interfaces, and `reexec`. It validates code in adjacent `archive.go` and file-hash behavior.

## Risks And Test Signals
Root-only requirement limits coverage in unprivileged CI. Fixed hashes make metadata changes visible. Failures indicate extraction lifecycle leaks, path normalization issues, or hash compatibility drift.
