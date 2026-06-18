# sources/cloud-native/ostree/src/libostree/ostree-repo-libarchive.c

Purpose: bridges libarchive archives and OSTree mutable trees/repo objects, supporting archive import into an `OstreeMutableTree` and export of an `OstreeRepoFile` tree back to a libarchive writer.

Important APIs/types/functions: public functions are `ostree_repo_import_archive_to_mtree`, `ostree_repo_write_archive_to_mtree`, `ostree_repo_write_archive_to_mtree_from_fd`, and `ostree_repo_export_tree_to_archive`. Internal import context `OstreeRepoArchiveImportContext`, `DeferredHardlink`, path normalization helpers, xattr/SELinux helpers, hardlink deferral, and recursive export helpers do most work.

Control flow: import reads archive headers, accepting `ARCHIVE_WARN` while validating UTF-8 path and symlink data itself. Paths are made relative, optionally translated or converted with the OSTree `/etc -> /usr/etc` convention, parent directories are created when requested, commit modifiers can skip/modify entries and xattrs, file content is written as OSTree content objects, directory metadata is written separately, and hardlinks are resolved after all entries are seen. Export recursively enumerates an `OstreeRepoFile` tree, writes directory/file/symlink archive entries, emits xattrs unless disabled, streams regular content from the repo, and uses checksum tracking to emit hardlinks for duplicate content.

State and persistence: import persists new OSTree content and directory metadata objects and mutates the provided mutable tree. Export is read-only against repo objects and stores only per-export checksum state. Builds without libarchive return not-supported errors.

Dependencies/integration: depends on libarchive, `ostree-libarchive-input-stream`, repo content APIs, mutable-tree APIs, commit modifiers, SELinux policy lookup, xattr callbacks, GLib file info, and core object serialization. Tests in `tests/test-libarchive-import.c` exercise import behavior.

Risks: path handling is security-sensitive; `path_relative` rejects `.`/`..` after normalizing absolute paths. UTF-8 handling was explicitly hardened to avoid locale conversion failures. Hardlink reconstruction is subtle because archive formats differ in ordering and size semantics. Unsupported file types either fail or are ignored depending on options. There is a duplicated `archive_read_close()` call in `write_archive_to_mtree`, which appears harmless but is worth regression testing.

Test signals: `tests/test-libarchive-import.c` covers import paths and options. Export should be tested for xattrs, symlinks, hardlinks by checksum, path prefixes, and content streaming errors.
