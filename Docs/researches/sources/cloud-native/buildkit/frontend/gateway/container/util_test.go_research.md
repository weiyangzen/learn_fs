# sources/cloud-native/buildkit/frontend/gateway/container/util_test.go

## Purpose

This file tests detection of `os.Root` path escape errors for container stat fallback behavior.

## Important APIs, Types, And Functions

- `TestIsPathEscapesRootError` creates a temp root, symlinks `sh` to `/bin/sh`, opens the root with `os.OpenRoot`, stats the symlink through `fs.Stat`, and checks `isPathEscapesRootError`.

## Control Flow

The test constructs the escaping symlink, opens the restricted root filesystem, expects `fs.Stat(fsys.FS(), "sh")` to error, and requires the helper to classify it as a path escape.

## State And Persistence Behavior

Only a temporary directory and symlink are created. The opened root is closed with `defer`.

## Dependencies And Integration Points

The test uses Go `io/fs`, `os.OpenRoot`, filesystem symlinks, and `testify/require`. It protects the fallback path in `gatewayContainer.StatFile`.

## Risks And Edge Cases

The test depends on platform support for `os.OpenRoot` and symlink semantics. It verifies only positive detection; negative cases for non-`PathError` or unrelated `PathError` are not covered.

## Test Signals

This is a focused regression signal for safely statting symlinks that would otherwise escape the mounted root.
