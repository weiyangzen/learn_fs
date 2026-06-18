# sources/compression/zstd/tests/cli-tests/dict-builder/no-inputs.sh

## Purpose
This negative CLI test exercises dictionary training with no inputs.

## APIs, control flow, and integration
It turns on shell tracing and runs `zstd --train`. There is no `set -e`, so the expected result is controlled by the harness `.exit`/stderr expectation files rather than shell abort behavior.

## State, dependencies, risks, and test signals
The test writes no inputs. It depends on the CLI emitting stable diagnostics and returning the expected nonzero status. It catches regressions where `--train` without samples silently succeeds or crashes.
