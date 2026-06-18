# sources/cloud-native/containers-storage/pkg/archive/archive_linux_test.go

## Purpose
This Linux test file validates overlay whiteout and opaque-directory conversion across tar and untar operations.

## Important Tests and Helpers
`setupOverlayTestDir` creates opaque directories and a character-device whiteout. `setupOverlayLowerDir` creates a lower-layer directory used to decide whether an opaque directory needs an AUFS opaque marker. `TestOverlayTarUntar` tars and untars using overlay whiteout format and checks modes, opaque xattrs, and device whiteouts. `TestOverlayTarAUFSUntar` tars overlay input but extracts as AUFS, checking `.wh..wh..opq` and `.wh.<file>` entries. `TestNestedOverlayWhiteouts` ensures nested whiteouts do not fail when a parent path has already become a whiteout device.

## Control Flow and State
The tests manipulate real xattrs and device nodes using `system.Lsetxattr` and `system.Mknod`, set umask to zero for deterministic modes, stream archives through `TarWithOptions`, and inspect the extracted filesystem state.

## Dependencies and Integration Points
The file depends on Linux-specific `system`, `unix`, `syscall`, and archive whiteout APIs. It validates `archive_linux.go` plus the shared tar/extraction machinery in `archive.go`.

## Risks and Edge Cases
These tests require privileges/filesystem support for xattrs and mknod-like behavior. They focus on a small overlay tree, not all lower-layer combinations. The nested test specifically protects the ENOTDIR case documented in the converter.

## Test Signals
The tests provide strong Linux-specific confidence that overlay whiteouts survive archive round trips and that conversions to AUFS tar markers preserve the expected deletion/opaque semantics.
