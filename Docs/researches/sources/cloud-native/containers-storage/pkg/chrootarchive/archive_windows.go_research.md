<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_windows.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/archive_windows.go

Purpose: Windows implementation of chrootarchive hooks without chroot/reexec sandboxing.

Important APIs/types/functions: `unpackDestination`, `Close`, `newUnpackDestination`, `chroot`, `invokeUnpack`, and `invokePack`.

Control flow: records destination directly, no-ops `chroot`, invokes `archive.Unpack` inline with `longpath.AddPrefix(dest.dest)`, and invokes `archive.TarWithOptions` inline for packing.

State/persistence: extraction and tar creation happen in the current process.

Dependencies/integration: integrates with `archive` and `longpath` for Windows path length handling.

Risks: no chroot isolation exists on Windows, so safety relies on archive path sanitization rather than process root confinement. `applyLayerHandler` in `diff_windows.go` also passes nil options to `UnpackLayer`, ignoring its `options` parameter.

Test signals: Windows-specific archive tests outside this subset cover some canonical naming and invalid destination cases; many chroot tests skip Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_windows.go -->
