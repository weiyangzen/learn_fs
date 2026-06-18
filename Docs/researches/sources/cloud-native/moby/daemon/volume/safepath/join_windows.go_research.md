# sources/cloud-native/moby/daemon/volume/safepath/join_windows.go

## Purpose
Windows implementation of safe subpath joining through component handle locking.

## Important APIs, Types, And Functions
`Join(ctx, path, subpath)` resolves and locks a path. `lockFile` opens each component with backup semantics and reparse-point flags.

## Control Flow
After shared symlink evaluation, `Join` splits the relative subpath and walks each component. For each path it opens a handle, registers cleanup, re-evaluates symlinks, rejects escapes, checks file information by handle, and rejects reparse points. On success it returns a `SafePath` pointing to the real full path with cleanup handles released to the `SafePath`.

## State And Persistence
No files are created. The `SafePath` owns open Windows handles that keep components stable until closed.

## Dependencies And Integration Points
Used by mount setup for subpaths on Windows. Depends on Windows syscall handles, `cleanups.Composite`, and shared safepath errors.

## Risks
Handle lifetime is the core safety boundary; cleanup bugs can leak handles. Reparse-point rejection is important for symlink/junction safety. Capturing `fullPath` in cleanup closures must remain correct if modified.

## Test Signals
Cross-platform safepath tests cover escape rejection, valid internal symlinks, replacement behavior, and close invalidation.
