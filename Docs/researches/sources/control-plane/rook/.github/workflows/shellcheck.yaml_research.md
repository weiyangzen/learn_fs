# sources/control-plane/rook/.github/workflows/shellcheck.yaml

## Purpose

Runs ShellCheck over shell scripts on pushes and pull requests.

## Important APIs, Types, and Functions

The `shellcheck` job checks out the repo and runs `make lint.shell`.

## Control Flow

Standard push/PR triggers with PR concurrency cancellation execute the job. The Makefile locates shell scripts and invokes the pinned ShellCheck binary/tool target.

## State and Persistence Behavior

No state is persisted; results are check logs/annotations.

## Dependencies and Integration Points

It integrates with the Makefile `lint.shell` target, `build/reset`, `build/sed-in-place`, and Mergify-required `Shellcheck`.

## Risks and Edge Cases

Only files found by the Makefile are checked. ShellCheck version is controlled by Makefile variables, not the workflow.

## Test Signals

Passing means shell scripts meet the configured ShellCheck warning threshold.
