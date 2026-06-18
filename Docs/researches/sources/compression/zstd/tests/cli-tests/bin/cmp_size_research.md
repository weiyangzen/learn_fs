# sources/compression/zstd/tests/cli-tests/bin/cmp_size

## Purpose

This shell utility compares two file sizes for CLI tests without printing sizes in traced command output.

## Important APIs, Types, and Functions

It supports `-h`/`--help`, validates that argument 2 and argument 3 are files, obtains sizes with `wc -c`, and applies one comparison operator: `-eq`, `-ne`, `-lt`, `-le`, `-gt`, or `-ge`.

## Control Flow, State, and Persistence

`set -e` aborts on failed commands except the final test expression naturally becomes the process status. The script has no persistent state.

## Dependencies and Integration Points

It depends on POSIX `sh`, `test`, and `wc`, and is available on the CLI test `PATH`.

## Risks and Test Signals

Arguments are unquoted in `test -f` and redirection, so paths with spaces/globs are unsafe. Unknown operators fall through with status from an empty case arm. Tests should cover every operator, missing files, help output, and filenames without shell metacharacters.
