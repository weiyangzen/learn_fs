# sources/compression/lz4/tests/test-lz4-basic.sh

## Purpose
This shell test is broad CLI smoke coverage for `lz4`, `lz4cat`, and `unlz4`. It validates core compression/decompression, frame options, pass-through behavior, `--rm`, filename edge cases, multi-threading options, directory rejection, block checksum handling, and fast-compression parser edge cases.

## Important Control Flow
The script uses `set -e`, `set -x`, a `tmp-tlb` prefix, and an EXIT trap that removes temporary files. It streams `datagen` output through different `lz4` options, uses `diff`/`grep`/`test` for assertions, and intentionally expects some commands to fail with `&& exit 1`.

## State, Dependencies, and Integration
It relies on test binaries in PATH (`datagen`, `lz4`, `lz4cat`, `unlz4`) and a POSIX-like shell environment. Runtime state is entirely temporary files prefixed with `tmp-tlb`, including files whose names begin with `-` to exercise `--` option termination. It integrates with the LZ4 CLI regression suite rather than library APIs.

## Risks and Test Signals
The script catches high-value command-line regressions such as deleting inputs only when intended, refusing directories, rejecting invalid trailing data, preserving pass-through mode, and avoiding an out-of-bounds issue for very high `--fast` values. It is not isolated from PATH issues and contains a case-sensitive reference to `$FPREFIX-dg20K` while the generated file is `dg20k`, so behavior may depend on the intended failure path.
