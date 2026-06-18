<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/walker.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/walker.go

## Purpose

This file implements the local filesystem walker used by nydusify's external snapshotter metadata path. It scans a root directory, asks a backend handler to describe each regular file as external chunks, and aggregates chunk metadata, file attributes, and backend configuration into a `backend.Result`.

## Important APIs, Types, and Functions

`Walker` is a stateless facade constructed by `NewWalker`. `bfsWalk` recursively walks directories by first handling regular files in the current directory and then descending into child directories. `(*Walker).Walk` accepts a `context.Context`, root path, and `Handler`; it builds a delayed list of per-file closures, invokes `handler.Handle` with `File{RelativePath, Size}`, and finally calls `handler.Backend`.

## Control Flow

The walk starts with `os.Lstat`, ignores a root that is itself a non-directory, and processes only entries whose `DirEntry.Type().IsRegular()` returns true. For every handled source file, returned chunks are appended to the result. File attributes are emitted once per consecutive chunk file path by comparing each chunk's `FilePath()` with the last seen path.

## State and Persistence Behavior

The walker does not write persistent state. It accumulates slices in memory and returns them to the caller. Relative paths are derived with `filepath.Rel(root, path)`, so output paths depend on the supplied root and host path separator behavior.

## Dependencies and Integration Points

It integrates with the external backend interfaces in the same package: `Handler`, `File`, `Chunk`, `FileAttribute`, `Backend`, and `Result`. It is called by `external.Handle` before metadata generation and backend/attributes file emission.

## Risks and Test Signals

The function skips symlinks, special files, and regular files whose type is not reported in `DirEntry.Type`, and it groups file attributes only for consecutive chunks with the same `FilePath`, not globally. Handler work is deliberately postponed until after walking, so file changes between walk and handle can make sizes stale. Tests cover invalid paths, empty directories, traversal order, handler/backend errors, and attribute aggregation.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/walker.go -->
