# sources/compression/xz/tests/test_compress.sh

Purpose: shell round-trip test driver for generated or prepared compression inputs using `xz` and optionally `xzdec`.

Important functions and variables: resolves `XZ` and `XZDEC`, validates build/feature availability, defines `test_xz()` for compress/decompress/compare cycles, sets conservative memlimits and `--threads=1`, and derives temporary names from the input fixture.

Control flow: skips if `xz` is missing, if required encoder/decoder support is disabled, or if the shell lacks functions. For `compress_generated_*`, invokes `create_compress_files`; for `compress_prepared_*`, reads from `$srcdir`. It then tests presets `-1` through `-4` and selected filters when both encoder and decoder macros are present: delta distances, x86, powerpc, ia64, arm, armthumb, arm64, sparc, and riscv. Each compression is decompressed with `xz -cd`, and also `xzdec` if built.

State and persistence: creates temporary compressed/uncompressed outputs and removes them via trap. Generated fixtures may persist in the build directory.

Dependencies and integration: integrates generated fixture wrappers, `xz`, `xzdec`, `config.h`, shell `cmp`, and Automake parallel tests.

Risks: filter availability detection is macro-based and acknowledged as imperfect when partial support is configured. Ancient shell behavior around empty `"$@"` is avoided by always passing arguments.

Test signals: any compression failure, decompression failure, or byte mismatch exits 1; unsupported configuration exits 77.
