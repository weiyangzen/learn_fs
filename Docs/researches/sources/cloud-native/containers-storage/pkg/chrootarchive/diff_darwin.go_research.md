<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff_darwin.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/diff_darwin.go

Purpose: Darwin `applyLayerHandler` implementation without chroot/reexec sandboxing.

Important APIs/types/functions: `applyLayerHandler`.

Control flow: cleans destination, optionally decompresses with `archive.DecompressStream`, creates a temp extraction directory under `os.Getenv("temp")`, calls `archive.UnpackLayer(dest, layer, options)`, removes the temp directory, and wraps errors with destination context.

State/persistence: mutates destination through `UnpackLayer`; creates/removes a temporary directory.

Dependencies/integration: used by public `ApplyLayer` wrappers on Darwin.

Risks: no chroot confinement. `os.Getenv("temp")` may be empty on Unix-like systems, so temp placement depends on `os.MkdirTemp` behavior with an empty dir. Cleanup ignores remove errors.

Test signals: generic chroot apply tests may cover this path on Darwin, but Linux-specific sandbox behavior is not present.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff_darwin.go -->
