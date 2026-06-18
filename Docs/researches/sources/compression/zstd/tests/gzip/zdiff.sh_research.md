<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zdiff.sh -->
## sources/compression/zstd/tests/gzip/zdiff.sh

Purpose: Exercises `zdiff` with two compressed inputs and with equal inputs.

Important APIs and functions: Sources `init.sh`, uses `gzip`, `zdiff`, shell status checks, and `compare`.

Control flow: It creates files `a` and `b`, compresses both, prepares expected classic diff output, and runs `zdiff a.gz b.gz`. Status must be `1` and output must match the expected difference. It then runs `zdiff a.gz a.gz` and requires success with empty stdout and stderr.

State and persistence: Creates `a.gz`, `b.gz`, `exp`, `out`, and `err`.

Dependencies and integration points: Depends on `zdiff` being available in `PATH` and using the tested gzip-compatible decompressor for `.gz` inputs.

Risks: Exact diff output assumes default `diff` formatting. Host-specific `zdiff` implementations can vary if not the intended wrapper.

Test signals: Different compressed files yield status `1` and expected diff; identical compressed files yield zero status and no output.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zdiff.sh -->
