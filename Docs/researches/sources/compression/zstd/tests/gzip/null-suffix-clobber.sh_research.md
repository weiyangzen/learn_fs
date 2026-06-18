<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/null-suffix-clobber.sh -->
## sources/compression/zstd/tests/gzip/null-suffix-clobber.sh

Purpose: Regression test ensuring an empty suffix supplied with `-S ''` is rejected without clobbering the input file.

Important APIs and functions: Sources `init.sh`, creates a gzip file, invokes `gzip ---presume-input-tty -d -S ''`, and compares stdout/stderr.

Control flow: It writes `F.gz`, prepares `yes` stdin and expected stderr `gzip: invalid suffix ''`, then runs decompression with empty suffix. The command must fail, produce no stdout, emit the expected error, and leave `F.gz` intact.

State and persistence: Creates `F.gz`, `yes`, `expected-err`, `out`, and `err` under the test temp directory.

Dependencies and integration points: Checks suffix validation and interactive prompt handling in gzip-compatible mode.

Risks: Exact stderr text is required. The triple-dash long option `---presume-input-tty` is unusual and assumes compatibility with GNU gzip's test-only option parsing.

Test signals: Failed exit, empty stdout, exact invalid-suffix diagnostic, and retained source archive.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/null-suffix-clobber.sh -->
