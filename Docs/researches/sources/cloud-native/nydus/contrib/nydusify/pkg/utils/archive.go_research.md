<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/archive.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/archive.go

## Purpose

This utility file provides tar/tar.gz packing and unpacking helpers used by nydusify for layer, bootstrap, and file extraction workflows.

## Important APIs, Types, and Functions

`PackTargz` streams a single source file into a tar or tar.gz archive under a requested name. `PackTargzInfo` computes the digest and size of that generated stream. `UnpackTargz` decompresses an archive stream and applies it into a destination directory with optional overlay whiteout conversion.

## Control Flow

`PackTargz` returns an `io.PipeReader` immediately and writes archive data in a goroutine, closing the pipe with the first encountered error. `PackTargzInfo` tees the generated stream through a pipe so digest calculation and size counting proceed concurrently. `UnpackTargz` uses containerd compression detection, temporarily sets umask to zero, creates the destination, and calls `archive.Apply`.

## State and Persistence Behavior

Packing only reads the source file and streams bytes. Unpacking writes files under `dst` and temporarily mutates process umask, restoring it with `defer`. Overlay mode controls whether whiteouts are converted or skipped.

## Dependencies and Integration Points

It depends on Go tar/gzip, containerd archive/compression, OCI digest, and `unix.Umask`. `viewer` and other nydusify utilities use neighboring unpack helpers for bootstrap extraction.

## Risks and Test Signals

`PackTargz` uses `0666` archive mode and a directory header from `filepath.Dir(name)`, which can produce `"."` entries. `PackTargzInfo` uses unbuffered channels that assume the digest reader drains correctly. `UnpackTargz` delegates path handling to containerd archive logic. Tests cover deterministic digest/size, compressed/uncompressed streams, invalid streams, and unpacked content.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/archive.go -->
