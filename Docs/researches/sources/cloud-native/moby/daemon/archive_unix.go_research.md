# sources/cloud-native/moby/daemon/archive_unix.go

## Purpose
Implements Unix container filesystem stat, archive, and extraction helpers for Docker copy APIs.

## APIs, Types, And Functions
Key functions are `containerStatPath`, `containerArchivePath`, `containerExtractToDir`, and `checkWritablePath`. Dependencies include `openContainerFS`, `go-archive`, compression helpers, `ioutils.NewReadCloserWrapper`, container mount parsing, event logging, and Moby errdefs.

## Control Flow, State, And Integration
Stat locks the container, opens its filesystem, and stats the target path. Archive locks the container for the lifetime of the returned reader, rebases tar paths, runs tarball creation inside the container filesystem, and logs an archive event. Extraction decompresses before entering the container filesystem, resolves symlinks, verifies a directory and writability, selects tar options, untars content, and logs an extract event.

## Risks And Test Signals
Risks include lock lifetime tied to stream closure, symlink/path traversal mistakes, executing decompression helpers inside container context, read-only volume/rootfs checks, and archive overwrite semantics. Integration is with Docker `cp`, volume mount metadata, container events, and Unix filesystem isolation.
