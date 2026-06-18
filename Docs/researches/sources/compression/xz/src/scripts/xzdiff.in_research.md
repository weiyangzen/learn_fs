# sources/compression/xz/src/scripts/xzdiff.in

## Purpose
Template for `xzdiff`/`xzcmp`, comparing uncompressed contents of compressed files or a compressed file against its uncompressed counterpart.

## Important APIs, Types, And Functions
Shell variables:
- `xz='@xz@ --format=auto'` with `XZ_OPT` preserved for limits/threads.
- `prog` and `cmp` selected by executable name and environment (`DIFF`/`CMP`).
- `escape` sed script quotes user options for later `eval`.
- `xz1`, `xz2` choose decompressor commands by suffix.
- `xz_status` captures decompressor exit statuses through extra file descriptors.

## Control Flow
The script parses `--help`, `--version`, `--`, and cmp/diff options, validating input files. For one operand, it derives the uncompressed filename from recognized suffixes and compares decompressed input to that file. For two operands, it chooses decompressor commands based on each suffix and handles compressed-compressed, stdin-stdin, `/dev/fd` capable systems, and fallback temporary directory comparison. It then reconciles decompressor statuses, ignoring successful decompression and SIGPIPE, and exits with the diff/cmp status or 2 on decompression/setup errors.

## State And Persistence
May create a temporary directory in fallback two-compressed-file mode and removes it via traps. No persistent state otherwise.

## Dependencies And Integration Points
Configured by Autotools placeholders for shell, xz path, package metadata, and optional path setup. Integrates with gzip, bzip2, lzop, zstd, lz4 when suffixes indicate those formats. Installed via `scripts/Makefile.am`.

## Risks
Uses `eval` to run user-selected diff/cmp and quoted options; escaping is central to safety. Suffix inference is broad and can misclassify names. `/dev/fd` probing handles old shell bugs. Temporary directory fallback must be secure and cleaned on signals. Preserving `XZ_OPT` is intentional but changes resource behavior.

## Test Signals
Tests for one/two operands, stdin, xz/gz/bz2/lzo/zstd/lz4 suffixes, files with quotes/spaces/newlines where possible, diff and cmp modes, decompressor failures, SIGPIPE from early cmp/diff exit, mktemp fallback, and `--help`/`--version`.
