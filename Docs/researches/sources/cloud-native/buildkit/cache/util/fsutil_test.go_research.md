# sources/cloud-native/buildkit/cache/util/fsutil_test.go

## Purpose

This file tests the error-path rewriting helper used by cache filesystem utilities.

## Important APIs, Types, and Functions

- `TestSetErrorPath` calls `fsutil.Stat` on a missing path, invokes `replaceErrorPath`, and asserts the error string reflects the new path.

## Control Flow and State

The test creates a temporary directory, constructs a guaranteed-missing nested path, and confirms the original error mentions that path. It then mutates the path error to `/my/new/path` and checks the original path disappears from `err.Error()` while the replacement appears.

## Dependencies and Integration Points

The test depends on `tonistiigi/fsutil` returning an error chain containing a mutable `*os.PathError`. It protects `StatFile` and `ReadFile` user-facing error reporting.

## Risks and Edge Cases

The test documents a dependency on a specific fsutil error implementation detail. If fsutil changes wrapping behavior or formats error strings eagerly, this method may stop working.

## Test Signals

The test gives focused coverage for `replaceErrorPath` only. It does not cover successful stat/read/list behavior.
