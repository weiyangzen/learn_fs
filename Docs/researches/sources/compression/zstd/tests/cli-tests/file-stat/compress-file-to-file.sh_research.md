# sources/compression/zstd/tests/cli-tests/file-stat/compress-file-to-file.sh

## Purpose
This file-stat test covers normal file-to-file compression with trace instrumentation enabled.

## APIs, control flow, and integration
It generates `file`, sets mode `642`, runs `zstd file -q --trace-file-stat -o file.zst`, and validates the output with `zstd -tq file.zst`.

## State, dependencies, risks, and test signals
State is `file` and `file.zst`. The chmod checks stat propagation paths without making the file unreadable. Risks are platform permission differences and diagnostic expectation churn. Pass confirms traced file input/output compression still creates a valid frame.
