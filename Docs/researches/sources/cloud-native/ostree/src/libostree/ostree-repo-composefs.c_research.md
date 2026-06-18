# sources/cloud-native/ostree/src/libostree/ostree-repo-composefs.c

## Purpose
This file implements composefs support for libostree. It parses repo configuration, manages an in-memory `OstreeComposefsTarget`, checks out an `OstreeRepoFile` tree into libcomposefs nodes, writes composefs images, optionally computes fsverity digests, and can insert composefs digest metadata into commit metadata.

## Important APIs, Types, And Functions
The exported or repo-internal surface includes `_ostree_repo_parse_composefs_config()`, `ostree_composefs_target_new()`, `ostree_composefs_target_ref()`, `ostree_composefs_target_unref()`, the boxed `OstreeComposefsTarget` type, `ostree_composefs_target_write()`, `_ostree_repo_checkout_composefs()`, and `ostree_repo_commit_add_composefs_metadata()`. Important static helpers under `HAVE_COMPOSEFS` are `_composefs_read_cb()`, `_composefs_write_cb()`, `_ostree_composefs_set_xattrs()`, `checkout_one_composefs_file_at()`, `checkout_composefs_recurse()`, `checkout_composefs_tree()`, and `ensure_lcfs_dir()`.

## Control Flow
Configuration parsing reads `integrity.composefs` as an `OtTristate`, stores wanted and supported state on `OstreeRepo`, and errors when composefs is required but the build lacks libcomposefs. Target creation initializes a root libcomposefs directory node when support is compiled in. Checkout starts by querying the source `OstreeRepoFile` root as a directory, then recursively loads OSTree dirtree and dirmeta variants. For each file, it validates the destination name, loads file content/info/xattrs with `ostree_repo_load_file()`, creates a composefs node, fills mode, uid, gid, size, symlink payload or loose-object payload path, attaches xattrs, and optionally attaches fsverity digest data. For each directory, it validates child names, sets directory metadata, and recurses into subtrees.

Image writing chooses the `root` child if present, otherwise an empty directory, configures libcomposefs write options, writes to an fd if provided, and optionally returns a 32-byte fsverity digest. `_ostree_repo_checkout_composefs()` also ensures rootfs bind-mount anchor directories such as `usr`, `etc`, `boot`, `var`, and `sysroot`. Commit metadata generation builds a composefs target from a repo root, writes it without an output fd to compute the digest, and inserts `OSTREE_COMPOSEFS_DIGEST_KEY_V0` into a metadata dictionary.

## State And Persistence
`OstreeComposefsTarget` is refcounted and owns a libcomposefs node tree until written or unreffed. The checkout process does not materialize a traditional filesystem checkout; it records paths, metadata, xattrs, symlink targets, object payload paths, and fsverity digest hints in the composefs node graph. Persistence happens only when `ostree_composefs_target_write()` writes the image fd or when commit metadata receives the computed digest.

## Dependencies And Integration Points
This file depends on optional `libcomposefs`, optional Linux fsverity headers, GIO Unix streams, OSTree core loose object path helpers, `OstreeRepoFile`, repo-private memory cache helpers, and xattr/dirmeta variant formats. It integrates with checkout/deploy paths through `_ostree_repo_checkout_composefs()`, with commit metadata through `ostree_repo_commit_add_composefs_metadata()`, and with repo config through `_ostree_repo_parse_composefs_config()`.

## Risks And Edge Cases
The code is compiled into support and non-support paths; unsupported builds must consistently return `composefs_not_supported()`. Name validation is critical because file and subdirectory names become composefs paths. Duplicate file or directory targets are rejected. fsverity handling has several branches: it prefers kernel-measured digest from bare repo file fds, falls back to user-space content hashing only when verity is explicitly required, and otherwise may omit a digest. Large trees can be expensive when fsverity digest computation falls back to reading all content. Root checkout must be a directory, and root bind-mount directories are added even if absent from the original tree.

## Test Signals
Tests should cover config tristate behavior with and without compile-time support, empty target image writing, recursive checkout preserving uid/gid/mode/xattrs/symlinks, invalid path names, duplicate target names, fsverity digest selection and fallback, rootfs anchor directory creation, commit metadata digest insertion, and graceful unsupported-build errors for all public composefs entry points.
