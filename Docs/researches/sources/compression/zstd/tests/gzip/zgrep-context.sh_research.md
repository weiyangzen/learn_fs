<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zgrep-context.sh -->
## sources/compression/zstd/tests/gzip/zgrep-context.sh

Purpose: Ensures `zgrep -15` context option handling works on compressed stdin.

Important APIs and functions: Sources `init.sh`, defines a small `seq` replacement, uses `${GREP:-grep}` to probe host grep support, runs `zgrep`, and compares output.

Control flow: It creates numbers `1..40`, compresses them, and expects `2..32` when searching for `17` with 15 lines of context. If host grep lacks the context option, it skips with exit `77`. Otherwise it requires `zgrep -15 17 - < in.gz` to match expected output.

State and persistence: Creates `in`, `in.gz`, `exp`, and `out`.

Dependencies and integration points: Tests option forwarding/parsing in `zgrep`, including compressed stdin through `-`.

Risks: Relies on host grep supporting the compact numeric context form. The local `seq` uses awk and assumes basic awk availability.

Test signals: Either SKIP due to unsupported grep context options or PASS with exact `2..32` output.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zgrep-context.sh -->
