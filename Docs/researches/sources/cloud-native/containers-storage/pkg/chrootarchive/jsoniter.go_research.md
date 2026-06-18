<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/jsoniter.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/jsoniter.go

Purpose: shared JSON implementation variable for Unix chrootarchive IPC.

Important APIs/types/functions: package variable `json`.

Control flow: binds `jsoniter.ConfigCompatibleWithStandardLibrary` to a package-level variable used by reexec parent/child code for options and responses.

State/persistence: none beyond process-local configuration.

Dependencies/integration: used in `archive_unix.go` and `diff_unix.go` to encode/decode `archive.TarOptions` and apply-layer responses.

Risks/test signal: keeping JSON behavior compatible with the standard library matters because options structs are shared with code that may expect standard encoding semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/jsoniter.go -->
