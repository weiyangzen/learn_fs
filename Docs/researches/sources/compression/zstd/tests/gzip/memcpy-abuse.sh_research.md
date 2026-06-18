<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/memcpy-abuse.sh -->
## sources/compression/zstd/tests/gzip/memcpy-abuse.sh

Purpose: Regression test for historical gzip inflate code using `memcpy` on overlapping regions.

Important APIs and functions: Sources `init.sh`, generates a slightly non-uniform input larger than 32 KiB with `printf` and `tee`, compresses with `gzip`, decompresses with `gzip -dc`, and compares.

Control flow: It creates `in` and `in.gz` from the same generated stream. Decompression must succeed and produce byte-identical output.

State and persistence: Creates `in`, `in.gz`, and `out` in the temporary test directory.

Dependencies and integration points: Exercises deflate match copying behavior in the gzip-compatible decompressor. The generated size targets internal gzip buffer edges.

Risks: The `printf %032767d` format is deliberate; changing it can stop hitting the overlap-sensitive path. This test checks correctness, not memory sanitizer diagnostics.

Test signals: `gzip -dc in.gz` exits zero and `out` equals `in`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/memcpy-abuse.sh -->
