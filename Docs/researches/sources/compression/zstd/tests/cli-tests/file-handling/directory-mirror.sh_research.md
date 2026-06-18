# sources/compression/zstd/tests/cli-tests/file-handling/directory-mirror.sh

## Purpose
This test validates `--output-dir-mirror` path reconstruction across relative, cwd-relative, absolute, and dotted paths, including hidden files and directories.

## APIs, control flow, and integration
It creates `src` with visible/hidden files, `mid`, and `dst`. It compresses recursively with `zstd -q -r --output-dir-mirror`, decompresses recursively with the same option, and compares source/destination trees with `diff --brief --recursive --new-file`. The sequence is repeated from inside `src`, with absolute `$BASE_PATH`, and with paths containing `./` components.

## State, dependencies, risks, and test signals
State is the `src`, `mid`, and `dst` directory trees, reset between cases. Dependencies are recursive CLI mode and POSIX `diff`. Risks are platform path normalization differences, absolute path handling on non-Unix systems, and hidden-file traversal regressions. Pass means compressed and decompressed mirrored trees preserve structure and content.
