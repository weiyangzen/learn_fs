# sources/cloud-native/ostree/tests/test-basic-c.c

Purpose: GLib C unit tests for low-level libostree repository, content stream, xattr, hardlink, and validation APIs.

Important APIs/types/functions: uses `OstreeRepo`, `OstreeRepoDevInoCache`, `OstreeRepoCommitModifier`, `OstreeMutableTree`, `ostree_raw_file_to_archive_z2_stream`, `ostree_content_stream_parse`, `ostree_repo_write_content`, `ostree_repo_write_regfile_inline`, `ostree_break_hardlink`, `ostree_validate_remote_name`, `ostree_fs_get_all_xattrs`, and `ostree_validate_structureof_dirmeta`.

Control flow: sets up a test repo, registers GLib tests for repo-not-system, archive stream roundtrip, object writes and checksum failures, devino-cache xattr callbacks, hardlink breaking, remote-name validation, large metadata commits, xattr reading, and invalid dirmeta xattrs.

State/persistence: creates temporary repos/checkouts, writes content objects, metadata objects, hardlinks, symlinks, and xattrs. Dependencies include GLib/GIO, libglnx, `libostreetest`, xattr support, and shell harness invocation from C.

Integration/risk/test signals: covers core library contracts beneath CLI tests. Risks are feature-dependent skips and direct use of internal object encodings. GLib test paths and assertions signal success.
