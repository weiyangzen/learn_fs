<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/tar.go -->
# sources/cloud-native/stargz-snapshotter/util/testutil/tar.go

## Purpose
Provides utilities for constructing synthetic tar archives for tests, including files, directories, symlinks, hardlinks, device metadata, xattrs, and whiteouts.

## Important APIs, Types, And Functions
- `TarEntry` describes path, body, mode, link target, type, xattrs, uid/gid, and times.
- Build options configure tar behavior and entry transforms.
- `BuildTar` writes tar headers and content to a pipe/reader for callers.
- Helpers normalize directory paths, create whiteout entries, and fill tar headers.

## Control Flow
The builder iterates entries, prepares a tar header according to type and options, writes headers, writes file bodies for regular files, and closes the tar writer/pipe with any error.

## State And Persistence
Archives are generated as streams/in-memory data. No persistent files are written unless callers consume the stream into files.

## Dependencies And Integration Points
Used by eStargz and metadata tests to create controlled layer blobs. Depends on Go `archive/tar` and filesystem metadata constants.

## Risks And Edge Cases
Malformed entries can create invalid tar headers. Streaming through pipes means callers must read to observe writer errors. Platform-specific metadata such as devices and xattrs can behave differently across consumers.

## Test Signals
Expected signals include tar readers seeing the requested entries, modes, links, xattrs, uid/gid, times, whiteouts, and file payload bytes.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/tar.go -->
