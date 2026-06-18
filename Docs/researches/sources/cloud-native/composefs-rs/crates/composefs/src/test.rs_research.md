# sources/cloud-native/composefs-rs/crates/composefs/src/test.rs

Purpose: provides reusable test utilities for composefs and internal proptest strategies that generate complex `tree::FileSystem` values across hash algorithms.

Important APIs/types/functions: `tempdir`, crate-test-only `tempfile`, `TestRepo`, `TestRepo::new/path/dir`, and the `proptest_strategies` module with `filename`, `stat`, xattr generators, `LeafContentSpec`, `LeafSpec`, `DirSpec`, `FsSpec`, `UnusualFsSpec`, `filesystem_spec`, `unusual_filesystem_spec`, `build_filesystem`, and `build_unusual_filesystem`.

Control flow: temp directories are allocated under `$CFS_TEST_TMPDIR` or `~/.var/tmp` to avoid tmpfs/overlayfs fs-verity limitations. `TestRepo::new` initializes an insecure repository for tests. Proptest strategies generate Linux-valid filenames, xattr namespaces, symlink targets, regular inline/external files, devices, sockets, fifos, whiteouts, directories, and hardlinks, then builders convert specs into concrete composefs trees.

State/persistence: temp repo paths are retained by `TempDir` lifetimes and cleaned on drop. Generated filesystem specs are in-memory only, but they deliberately model persistent metadata such as uid/gid/mode, mtimes, xattrs, external object hashes/sizes, and hardlink identity via shared `LeafId`s.

Dependencies/integration: depends on `once_cell`, `tempfile`, `rustix::fs::CWD`, `proptest`, `hex`, and composefs tree/fsverity/repository modules. It is used by crate unit tests and downstream crate tests needing stable test repos or generated trees.

Risks/test signals: the generators intentionally stress EROFS/composefs boundaries: 255-byte names, xattr prefix indexes, overlay xattr escaping, ACL bits, V1 lustre fallback behavior, large directories, 30 GB external sizes, whiteouts, and hardlinks. Risks are mainly generator drift from production invariants and environmental failures if the selected temp filesystem cannot support required operations.
