# sources/compression/zstd/doc/educational_decoder/Makefile

Purpose: builds and tests the educational zstd decoder harness. It is documentation-adjacent but executable, compiling all local C files into `harness` and comparing decoder output with files produced by a system `zstd`.

Important variables/targets: `ZSTD ?= zstd`, platform-specific `DIFF`, `HARNESS_FILES=*.c`, `MULTITHREAD_LDFLAGS=-pthread`, `DEBUGFLAGS=-g -DZSTD_DEBUG=1`, include paths into the real zstd tree, strict `CFLAGS`, `harness`, `clean`, and `test`.

Control flow: `harness` compiles local C files with debug/warning flags. `test` compresses `README.md`, decodes it through the educational decoder, diffs output, then trains a dictionary from repeated local files, compresses with that dictionary, decodes with `./harness tmp.zst tmp dictionary`, and diffs again.

State and persistence: produces `harness`, optional object/debug folders, temporary `tmp*` files, and a temporary `dictionary`. Clean removes local harness outputs and macOS debug folders.

Dependencies/integration: depends on an installed `zstd` CLI for tests, `diff` or `gdiff`, pthread linkage, and source-tree variables such as `ZSTDDIR` and `PRGDIR` supplied by the caller/environment.

Risks: tests are tied to `README.md` in the working directory and an installed CLI. `HARNESS_FILES=*.c` means any added C file in the directory becomes part of the harness build. The educational decoder intentionally exits on errors and is not production hardened.

Test signals: `make harness`, `make test`, dictionary and non-dictionary round trips, invalid input behavior through the harness, and compile with `ZDEC_NO_DICTIONARY` to verify conditional dictionary handling.
