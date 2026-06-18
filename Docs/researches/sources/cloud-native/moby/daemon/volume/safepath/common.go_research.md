# sources/cloud-native/moby/daemon/volume/safepath/common.go

## Purpose
Shared path-resolution helpers for safe volume/image subpath mounting.

## Important APIs, Types, And Functions
`evaluatePath(path, subpath)` resolves symlinks in the base and combined path, returns resolved base and a relative resolved subpath, and errors if the result escapes. `isLocalTo(path, basepath)` lexically checks subtree membership via `filepath.Rel` and `filepath.IsLocal`.

## Control Flow
`evaluatePath` resolves the base, maps missing/inaccessible paths to `ErrNotAccessible`, resolves the combined path, computes the relative path from base to combined target, and rejects non-local relative paths as `ErrEscapesBase`.

## State And Persistence
No state is persisted. It reads filesystem metadata through `EvalSymlinks`.

## Dependencies And Integration Points
Called by Linux and Windows `Join` implementations before platform-specific fd/handle locking. Errors integrate with Moby errdefs through marker methods.

## Risks
The initial symlink resolution is not sufficient alone for TOCTOU safety; callers must continue with platform-specific safe open/locking. `filepath.IsLocal` behavior differs by OS and is central to containment.

## Test Signals
`common_test.go` covers lexical locality cases including backtracking, absolute escapes, relative paths, and dot-containing filenames.
