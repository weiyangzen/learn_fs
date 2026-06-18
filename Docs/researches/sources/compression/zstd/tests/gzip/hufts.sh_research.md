<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/hufts.sh -->
## sources/compression/zstd/tests/gzip/hufts.sh

Purpose: Regression test for invalid deflate input that historically made gzip misbehave or crash in Huffman table handling.

Important APIs and functions: Sources `init.sh`, uses `gzip -dc`, normalizes stderr with `sed`, and compares stdout/stderr through `compare`.

Control flow: It prepares expected stderr text, decompresses `$abs_srcdir/hufts-segv.gz`, requires exit status `1`, requires empty stdout, rewrites the variable filename prefix in stderr to a stable `...:` prefix, and compares against the expected diagnostic.

State and persistence: Creates `exp`, `out`, `err`, and temporary `k` in the test directory. Reads the immutable fixture `hufts-segv.gz` from the source directory.

Dependencies and integration points: Depends on `abs_srcdir` from the test environment and on gzip-compatible error wording for invalid compressed data.

Risks: Diagnostic text matching is exact after filename normalization, so wording changes can fail this test even if behavior is otherwise correct. Missing `abs_srcdir` or fixture breaks setup.

Test signals: Expected failure status `1`, empty output, and normalized stderr `invalid compressed data--format violated`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/hufts.sh -->
