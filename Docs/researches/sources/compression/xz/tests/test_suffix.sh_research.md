# sources/compression/xz/tests/test_suffix.sh

Purpose: shell regression test for `xz` suffix handling, especially raw-format compression/decompression where a suffix is required to derive output file names. It also covers stdin/stdout behavior and `--files`/`--files0` filename-list paths that previously regressed.

Important APIs/functions: uses the `xz` command-line interface with `-z`, `-d`, `-f`, `-k`, `--suffix`, `-Fraw`, `--lzma1=preset=0`, `--lzma2=preset=0`, `--files`, `--files0`, and `-c`. Exit code `77` is the skip signal expected by Automake/CMake.

Control flow: resolves the `xz` executable from argument `$1` or `../src/xz/xz`, skips if unavailable, and skips if an Autotools `config.h` says encoder or decoder support is missing. It creates a temporary input file, validates raw compression with an explicit suffix, asserts raw compression/decompression without suffix fails, validates `.xz` compression with an explicit custom suffix, checks stdin raw mode writes to stdout implicitly, exercises newline- and NUL-delimited file lists, then checks unknown file-type decompression copies to stdout only with `-c`.

State and persistence: creates and removes `suffix_temp`, `suffix_temp.foo`, `suffix_temp_files`, and `suffix_temp_files0` in the current working directory. The test assumes a scratch working directory and removes leftovers before and after the run.

Dependencies and integration: integrated by `tests.cmake` as `test_suffix.sh` on Unix builds with encoder and decoder support. It depends on a built `xz` binary, shell utilities, and optional `../config.h` feature probes.

Risks: cleanup has one duplicate entry in the early `rm -f` list and relies on no unrelated files sharing the temporary names. The CMake build has no `config.h`, so the script assumes full feature availability when invoked there; `tests.cmake` compensates by gating on CMake feature variables.

Test signals: failure messages identify the exact suffix scenario. Passing protects raw suffix errors, file-list suffix renaming, stdin raw mode, and unknown-file passthrough semantics.
