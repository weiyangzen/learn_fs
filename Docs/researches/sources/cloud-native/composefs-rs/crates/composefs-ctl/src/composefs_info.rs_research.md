# sources/cloud-native/composefs-rs/crates/composefs-ctl/src/composefs_info.rs

## Purpose
This module implements a Rust `composefs-info` compatibility tool for inspecting composefs EROFS images. It supports listing entries, dumping composefs dumpfile text, listing referenced object paths, finding missing objects in a base directory, and measuring fs-verity digests for files.

## Important APIs, types, and functions
`Cli` and `Command` define clap parsing for `ls`, `dump`, `objects`, `missing-objects`, and `measure-file`. `run` parses process args for standalone or argv0 dispatch. `run_from_args` supports hidden `cfsctl composefs-info` dispatch by prepending a synthetic program name.

`print_escaped` emits C-compatible escaped path bytes. `ls_print` recursively walks sorted filesystem entries, prints directories with trailing slash, prints symlink targets, and prints external object paths for first-seen regular leaves. `collect_objects_from_fs` collects unique external object IDs from the leaves table. `cmd_*` functions implement each subcommand, and `read_image` reads the entire EROFS image into memory before parsing.

## Control flow
Every image-oriented command reads each image into a byte vector, converts it with `erofs_to_filesystem::<Sha256HashValue>`, and then performs its inspection. `ls` recurses from root and applies root-level filters only at the first level. `dump` serializes the tree using `write_dumpfile`. `objects` sorts object IDs by hex. `missing-objects` unions object IDs across all images and filters by `basedir/<object path>`. `measure-file` bypasses image parsing and uses fs-verity measurement with fallback.

## State and persistence behavior
The module is read-only except for stdout/stderr output. It does not mutate repositories or images. It tracks in-memory `seen_leaf_ids` to suppress repeated object path output for hardlinks in `ls`.

## Dependencies and integration points
It depends on composefs EROFS reader, dumpfile writer, tree types, and fs-verity measurement. It is integrated into `cfsctl` through hidden subcommand forwarding and argv0 multi-call dispatch in `main.rs`.

## Risks
Images are read fully into memory, which is simple but can be expensive for very large metadata images. The code assumes SHA-256 images, so it is compatibility-oriented rather than dynamically matching repository hash metadata. `cmd_dump` accepts a filter argument but ignores it. Root-level filtering in `ls` may differ from users expecting recursive name filtering. Output compatibility depends on `print_escaped` matching the C tool exactly.

## Test signals
There are no local tests in this file. Useful coverage would compare output against C `composefs-info` fixtures for listing, dump output, object ordering, hardlinks, whiteouts, escaping, missing object detection, and kernel/fs fallback behavior in `measure-file`.
