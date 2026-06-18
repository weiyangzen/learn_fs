<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tartest/tar.go -->
# sources/cloud-native/containerd/pkg/archive/tartest/tar.go

Purpose: test helper package for programmatically constructing tar streams with controlled entries, ownership, mtimes, links, symlinks, and xattrs.

Important APIs and types: `WriterToTar`, `TarAll`, `TarFromWriterTo`, `TarContext`, `WithUIDGID`, `WithModTime`, `WithXattrs`, `File`, `Dir`, `Symlink`, `Link`, and `writeHeaderAndContent`.

Control flow and state: `TarFromWriterTo` uses an `io.Pipe` and goroutine to stream tar records. `TarContext` is immutable-by-copy for UID/GID/mtime, but `WithXattrs` mutates or shares the map on the copied context, so callers should treat returned contexts as the owner of the xattr map.

Dependencies and integration: used heavily by `archive/tar_test.go` to manufacture edge-case tar entries that system `tar` would not easily produce.

Risks and test signals: panics on impossible `tar.FileInfoHeader` errors, which is acceptable for test fixtures. It validates content length before writing to catch inconsistent test setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tartest/tar.go -->
