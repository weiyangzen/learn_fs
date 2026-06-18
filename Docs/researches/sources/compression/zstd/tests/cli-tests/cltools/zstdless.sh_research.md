# sources/compression/zstd/tests/cli-tests/cltools/zstdless.sh

## Purpose

This CLI test checks `zstdless` invocation, option forwarding to `less`, and bad-path behavior.

## Important APIs, Types, and Functions

It runs `zstdless file.zst`, `zstdless -N file.zst`, and `zstdless bad.zst >&2`, labeling each step.

## Control Flow, State, and Persistence

`set -e` fails on unexpected nonzero status. No files are created; it depends on the cltools setup output.

## Dependencies and Integration Points

It depends on `zstdless`, `less`, `println`, and the compressed test file.

## Risks and Test Signals

The `-N` check ensures flags are interpreted by `less`, not zstd. Test behavior can vary if `less` is unavailable or configured differently in the harness.
