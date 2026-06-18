# sources/compression/zstd/tests/cli-tests/file-stat/compress-stdin-to-file.sh

## Purpose
This test covers stdin-input to named file-output compression with file-stat tracing.

## APIs, control flow, and integration
It generates `file`, pipes it into `zstd < file -q --trace-file-stat -o file.zst`, and validates with `zstd -tq`. This exercises the code path where input stat information is unavailable or stream-based while output stat tracing remains relevant.

## State, dependencies, risks, and test signals
State is `file` and `file.zst`. Risks include trace code assuming file-backed input. Pass confirms stdin compression with trace instrumentation produces a valid file.
