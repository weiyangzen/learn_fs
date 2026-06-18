# sources/cloud-native/composefs/tools/mkcomposefs.c

## Purpose
`mkcomposefs.c` builds composefs EROFS images from either a source directory or a textual dump file. It computes content digests, can stage payloads into a digest store, supports reproducibility and filtering flags, and can print the resulting image digest.

## Important APIs, Types, And Functions
Parsing helpers include `split_at`, `unescape_string`, `unescape_optional_string`, `parse_int_field`, `parse_mtime`, and `parse_xattr`. Dump import is represented by `dump_info`, `hardlink_fixup`, and `field_info`, with `tree_from_dump_line`, `tree_add_node`, `tree_add_hardlink_fixup`, `tree_resolve_hardlinks`, and `tree_from_dump`.

Filesystem copy and digest work includes `ensure_dir`, `mkdir_parents`, `write_to_fd`, `copy_file_data_range`, `copy_file_data_classic`, `copy_file_data`, `copy_file_with_dirs_if_needed`, `construct_copy_data`, `construct_compute_data`, `process_copy`, `process_compute`, `execute_in_threads`, `compute_digest`, and `fill_store`.

The CLI supports `--digest-store`, `--use-epoch`, `--skip-devices`, `--skip-xattrs`, `--user-xattrs`, `--print-digest`, `--print-digest-only`, `--from-file`, `--min-version`, `--max-version`, and `--threads`.

## Control Flow
`main` starts with digest-by-content build flags, parses options and version/thread constraints, validates positional source/output arguments, opens an output file unless digest-only mode is used, and then builds a node tree. In `--from-file` mode it parses a dump stream into `lcfs_node_s` objects, including deferred hardlink resolution. In directory mode it calls `lcfs_build` with digest calculation disabled/no inline, then computes digests in parallel and optionally fills the digest store in parallel.

After the tree is ready, `main` configures `lcfs_write_options_s`, writes EROFS output with `lcfs_write_to`, optionally prints the digest, closes the output, and unrefs the tree. The fuzzer build replaces the normal CLI with a `LLVMFuzzerTestOneInput` harness that parses a dump, writes an image to memory, and verifies it can be reloaded.

## State And Persistence
Persistent outputs are the image file and optional digest-store object files. Digest-store writes are staged through temporary files, fsynced, optionally fs-verity-enabled, then renamed. In-memory mutable state includes node trees, hardlink fixups, dynamic read buffers, work collections, and a shared iterator protected by `mutex_thread_access`.

## Dependencies And Integration Points
The tool depends on libcomposefs writer/build APIs, Linux fs-verity and reflink/copy syscalls, pthreads, CPU affinity/sysinfo, and standard POSIX filesystem calls. It interoperates with `composefs-info dump` through the dump grammar, with `mount.composefs` and kernel composefs through generated images, and with object stores through digest payload paths.

## Risks
Dump parsing is security-sensitive: field splitting, escaping, xattrs, hardlinks, and strict mode all affect accepted input. Some error checks after parsing `gid` and `rdev` accidentally test `uid == 0 && err`, which can obscure the field associated with an error. `copy_file_range` behavior varies across kernels/filesystems, so fallback logic is critical. Threaded digest/copy processing shares a single mutex for iteration and copy-file-range state. Output to an image file is not atomic unless the caller writes to a temporary destination.

## Test Signals
Coverage should include directory builds, `--from-file` round trips, strict and non-strict dump parsing, malformed escapes/NULs/xattrs, hardlink cycles and missing targets, inline content size limits, symlink size validation, digest-only mode, version min/max handling, multi-threaded digest/store paths, copy-file-range fallback, fs-verity best-effort enabling, and the existing fuzz harness.
