# sources/cloud-native/composefs-rs/crates/composefs-ctl/src/mkcomposefs.rs

## Purpose
This module implements a Rust `mkcomposefs` compatibility tool. It creates composefs EROFS images from source directories or composefs dumpfiles, optionally writes regular file content into a digest store, supports C-compatible format versions, and can print the fs-verity digest of the generated image.

## Important APIs, types, and functions
`Args` defines CLI flags for dumpfile input, digest printing, epoch mtimes, device and xattr filtering, min/max format version, digest store, hardlink behavior, thread count, source, and output image. `run` parses standalone args; `run_from_args` supports hidden `cfsctl mkcomposefs` dispatch.

`run_with_args` validates arguments, maps version flags to `FormatVersion`, opens an optional `FlatDigestStore`, reads input, applies transformations, builds an EROFS image with `mkfs_erofs_versioned`, writes it unless digest-only mode is selected, and prints digest if requested. `read_dumpfile`, `read_directory`, `write_image`, `compute_fsverity_digest`, `apply_transformations`, `set_all_mtimes_to_epoch`, and `remove_device_nodes` implement the steps.

## Control flow
Argument validation rejects digest-only with an image, missing image without digest-only, invalid version ranges, and unsupported `--min-version > 1`. Directory input opens a current-directory fd, creates a Tokio runtime based on `--threads`, optionally bounds verity work with a semaphore, and calls `read_filesystem_with_opts`. Dumpfile input reads from a file or stdin and parses text. Output to `-` refuses to write binary data to a terminal.

## State and persistence behavior
The module reads source directories or dumpfiles, may populate a digest store using the C-compatible `XX/DIGEST` layout, writes an image file or stdout, and prints digests. In-memory transformations can remove xattrs, keep only `user.*`, zero mtimes, remove block/character devices, and compact the filesystem after device removal.

## Dependencies and integration points
It depends on composefs dumpfile parsing, filesystem reading, object-store APIs, EROFS writer validation, fs-verity computation, and tree mutation. It is exposed through `main.rs` argv0 dispatch and hidden `cfsctl` forwarding. It uses `tokio` for async filesystem reading and `rustix` for fd-relative access.

## Risks
`--max-version` is validated only as a range input; actual selection is driven by `--min-version`, matching the current compatibility comments but potentially surprising. `--digest-store` is ignored with `--from-file` after warning. The generated image is fully materialized in memory before writing. `remove_device_nodes` recursively mutates directories and depends on a final `compact` to avoid orphan leaves. Without `--hardlinks`, host hardlinks are deliberately broken for C-compatible output.

## Test signals
There are no local tests in this file, though comments claim byte-for-byte compatibility is tested elsewhere. Important coverage includes C fixture comparisons for directory and dumpfile input, digest output modes, stdout terminal refusal, digest-store layout, hardlink behavior, xattr/device/mtime flags, version selection, thread counts, and stdin dumpfile parsing.
