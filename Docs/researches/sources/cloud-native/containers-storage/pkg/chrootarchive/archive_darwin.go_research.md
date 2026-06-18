<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_darwin.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/archive_darwin.go

Purpose: macOS fallback implementation for chrootarchive pack/unpack hooks.

Important APIs/types/functions: `unpackDestination`, `Close`, `newUnpackDestination`, `invokeUnpack`, and `invokePack`.

Control flow: `newUnpackDestination` records only `dest`. `invokeUnpack` calls `archive.Unpack` directly. `invokePack` ignores `root` and calls `archive.TarWithOptions`.

State/persistence: extraction and tar creation happen inline in the current process without chroot sandboxing.

Dependencies/integration: satisfies platform hook interfaces for `archive.go` on Darwin.

Risks: root restriction is explicitly not implemented for pack, and unpack is not sandboxed through chroot/pivot. Security properties differ from Linux/Unix reexec implementations.

Test signals: generic chroot tests may run where applicable, but malicious symlink root tests are Unix-not-Windows and most meaningful on platforms with real chroot support.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_darwin.go -->
