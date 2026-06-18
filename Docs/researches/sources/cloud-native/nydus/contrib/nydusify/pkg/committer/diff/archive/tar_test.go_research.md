# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar_test.go

Purpose: tests tar change writer behavior for copying, whiteouts, parent directories, skipped unmodified files, directories, and archive entry names.

Important APIs and flow: helper `tarEntryNames` reads generated tar bytes and sorts names. Tests cover `copyBuffered` success and canceled context, delete-to-whiteout output, added regular files with parent directory entries, unmodified file omission, and directory handling. Additional tests in the file exercise symlinks, hardlinks, special cases, and close behavior where available.

State and persistence: uses temporary source directories and in-memory tar buffers.

Dependencies and integration: validates output consumed by the Nydus commit diff path and OCI layer semantics.

Risks and test signals: good signal for common tar entry behavior. Full device/xattr behavior depends on platform privileges and is partly delegated to Unix-specific tests/helpers.
