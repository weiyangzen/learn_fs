<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/gzip-env.sh -->
## sources/compression/zstd/tests/gzip/gzip-env.sh

Purpose: Tests the obsolete `GZIP` environment variable handling for gzip-compatible invocation.

Important APIs and functions: Sources `init.sh`, calls `path_prepend_ .`, uses `gzip`, `compare`, and `Exit`. It creates a compressed stdin fixture from `exp`, then runs decompression with environment-supplied options.

Control flow: First validates that `GZIP=-qv` does not break `gzip -d` decompression. It then iterates over options that must be rejected when supplied through `GZIP`, including mode-changing, output-changing, suffix, recursive, help/version, and force/keep flags. Finally it iterates over allowed options such as name/no-name, quiet/verbose, and compression levels.

State and persistence: Creates temporary files under the `init.sh` test directory: `exp`, `in`, `out`, and `err`. State is local to the spawned test process and removed by the harness trap.

Dependencies and integration points: Depends on zstd's gzip-compatible CLI honoring the imported GNU gzip policy for `GZIP`. It also depends on the shared `compare` helper and shell variable assignment syntax immediately before a command.

Risks: This test is commented out in the Makefile default target, likely because zstd may intentionally limit or differ in `GZIP` envvar support. Any implementation accepting dangerous options from `GZIP` can alter files or test process behavior unexpectedly.

Test signals: Allowed options must exit successfully and reproduce `exp` in `out`; disallowed options must fail. Any mismatch sets `fail=1`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/gzip-env.sh -->
