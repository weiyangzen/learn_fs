<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/helin-segv.sh -->
## sources/compression/zstd/tests/gzip/helin-segv.sh

Purpose: Regression test for a historical gzip decompression segfault on a short `.Z`/compress-style input provided by Aki Helin.

Important APIs and functions: Sources `init.sh`, uses `printf` to create byte-exact `helin.gz` and expected output, invokes `gzip -dc`, compares with `compare`, and exits through `Exit`.

Control flow: The script writes a seven-byte compressed fixture, writes two NUL bytes as the expected decoded stream, then decompresses to `out` and requires success plus byte-identical output.

State and persistence: Creates `helin.gz`, `exp`, and `out` in the temporary test directory. No external state persists beyond harness cleanup.

Dependencies and integration points: Exercises gzip-format compatibility in the zstd CLI when invoked through the `gzip` symlink. It specifically reaches legacy decompress paths that must not crash on tiny crafted input.

Risks: The fixture is byte-oriented; shell or platform `printf` differences would be risky, but POSIX octal escapes are used. The test only checks stdout content, not stderr silence.

Test signals: `gzip -dc helin.gz` must exit zero and produce exactly two NUL bytes.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/helin-segv.sh -->
