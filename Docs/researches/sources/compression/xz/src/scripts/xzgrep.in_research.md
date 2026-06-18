# sources/compression/xz/src/scripts/xzgrep.in

## Purpose
Template for `xzgrep`, `xzegrep`, and `xzfgrep`, running grep variants over decompressed input.

## Important APIs, Types, And Functions
Shell variables:
- `xz='@xz@ --format=auto'`.
- `prog`/`grep` selected from executable name and `GREP`.
- `escape` quotes options/patterns for `eval`.
- Flags track pattern presence and filename/list modes.
- `grep_supports_label` detects support for `grep -H --label`.
- Per-file `uncompress`, `xz_status`, and result accumulator `res`.

## Control Flow
The script parses grep options, rejects recursive/directory/null-data options that cannot be supported, handles `--help`/`--version`, identifies options requiring arguments, and ensures a pattern via `-e` if needed. It defaults files to stdin. For each input, it chooses a decompressor by suffix or xz autodetection, pipes decompressed data into grep, handles `-l`/`-L`, filename prefixing via `--label` or a sed fallback, captures decompressor status separately, ignores SIGPIPE when grep exits early, and accumulates grep-like exit status semantics.

## State And Persistence
No persistent filesystem state. Result state is process-local across file loop.

## Dependencies And Integration Points
Autotools placeholders configure shell/xz/package/path. Depends on grep, sed, expr, gzip/bzip2/lzop/zstd/lz4 as needed. Installed by scripts Automake rules and invoked through symlink aliases.

## Risks
Complex POSIX shell parsing and `eval` require careful escaping. Option support intentionally excludes recursive/directory/null-data behavior. Filename prefix sed fallback must escape metacharacters and newlines. Different grep implementations have different `--label` support and binary-file behavior. Exit status handling around signals differs across shells.

## Test Signals
Pattern with/without `-e`, option clusters, grep modes (`-H`, `-h`, `-l`, `-L`), unsupported options, stdin, all supported suffixes, decompressor errors, SIGPIPE from `grep -q`, filenames with special characters, and grep implementations without `--label`.
