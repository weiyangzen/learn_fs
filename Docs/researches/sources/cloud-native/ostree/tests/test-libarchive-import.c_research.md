<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-libarchive-import.c -->
# sources/cloud-native/ostree/tests/test-libarchive-import.c

## Purpose
`test-libarchive-import.c` is a C unit/integration test for importing archives into an OSTree repo through the libarchive importer. It covers parent creation, device-file rejection or ignoring, OSTree filesystem conventions, xattrs, callback path semantics, and SELinux relabeling.

## Important APIs, Types, And Functions
Key helpers include `TestData`, `test_data_init`, `spawn_cmdline`, `test_archive_setup`, `import_write_and_ref`, `skip_if_no_xattr`, and `check_ostree_convention`. It uses `OstreeRepoImportArchiveOptions`, `archive_read_new`, `ostree_repo_commit_modifier_new`, `ostree_repo_commit_modifier_set_xattr_callback`, `ostree_repo_commit_modifier_set_sepolicy`, `ostree_sepolicy_new`, and xattr syscalls.

## Control Flow
The fixture creates a temporary repo and archive payload. Tests import archives with and without `autocreate_parents`, expect device-file errors unless `ignore_unsupported_content` is enabled, validate `/usr/etc` convention remapping, import xattrs from archive data, inject xattrs through callbacks, skip xattrs through commit modifiers, test callback paths with or without original archive entry names, and optionally verify SELinux labels outside containers.

## State And Persistence
State includes a temporary repo, archive fd, imported refs such as `bar`, `baz`, and `bob`, and checkout directories used to inspect contents and xattrs. SELinux checks consult host policy but do not persist policy changes.

## Dependencies And Integration Points
It integrates libarchive, `ostree_repo_import_archive_to_mtree` style import behavior, commit modifiers, xattr storage, SELinux policy, command-line checkout/ls, and the common C test helpers in `libostreetest`.

## Risks And Test Signals
The test has environment-dependent skips for xattrs, libarchive support, containers, and SELinux availability. Passing signals include correct import failures, parent auto-creation behavior, xattr round trips including embedded NULs, callback-selected xattrs, skipped xattrs, and SELinux context assignment on `/etc`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-libarchive-import.c -->
