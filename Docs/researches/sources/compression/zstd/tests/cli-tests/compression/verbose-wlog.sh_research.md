# sources/compression/zstd/tests/cli-tests/compression/verbose-wlog.sh

## Purpose
This test checks verbose compression/listing output around high compression levels and long-distance mode, especially window-log reporting.

## APIs, control flow, and integration
It sources `COMMON/platform.sh`, then compresses stdin from `file` with `-vv -19` into `file.19.zst` and lists it with `zstd -vv -l`. It repeats with `--long` into `file.19.long.zst`. Expected stderr/stdout matching is handled by the CLI test harness.

## State, dependencies, risks, and test signals
State is two `.zst` outputs. The test depends on verbose output stability and a large enough setup input to produce meaningful frame metadata. Risks are mostly diagnostic-output churn and platform-specific line endings or terminal behavior. Pass confirms both operations succeed and expected verbose metadata appears.
