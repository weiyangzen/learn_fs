<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/file.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/file.go

## Purpose

Provides a small helper to extract the next file argument from command multipart/stdin input.

## Important APIs, Types, and Functions

`GetFileArg(it files.DirIterator) (files.File, error)` advances the iterator, checks iterator errors, and converts the current entry to a `files.File`.

## Control Flow

If no entry is available, it returns the iterator error or an explicit "expected a file argument" error. If the entry is not a file, it returns "file argument was nil". Otherwise it returns the file handle for the caller to read or close.

## State and Persistence Behavior

No persistent state. It consumes one entry from the provided iterator, so callers control file lifetime.

## Dependencies and Integration Points

Depends on boxo `files`. Used by config replacement and MFS write paths to avoid duplicating multipart validation.

## Risks and Edge Cases

The helper only returns one file and does not enforce that no extra files remain. Callers must close returned files when appropriate.

## Test Signals

No direct tests in this subset. Coverage should include empty iterator, iterator error propagation, directory/non-file entries, and normal file extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/file.go -->
