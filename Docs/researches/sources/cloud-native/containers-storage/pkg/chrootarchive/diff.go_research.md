<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/diff.go

Purpose: public chrootarchive wrappers for applying layer diffs.

Important APIs/types/functions: `ApplyLayer` and `ApplyUncompressedLayer`.

Control flow: `ApplyLayer` delegates to platform `applyLayerHandler` with decompression enabled and default empty `archive.TarOptions`; `ApplyUncompressedLayer` delegates with caller options and no decompression.

State/persistence: all filesystem mutation occurs in platform-specific handlers, typically through `archive.UnpackLayer` inside a chroot/reexec child.

Dependencies/integration: thin facade over `archive` diff semantics and per-platform `diff_*` files.

Risks/test signal: public comments say `ApplyLayer` stream can only be uncompressed, but the implementation passes `decompress=true`, matching archive package behavior. Tests in `archive_test.go` cover empty archive application and safe dot-dot names.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff.go -->
