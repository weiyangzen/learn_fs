# sources/control-plane/rook/.github/workflows/checkmake.yaml

## Purpose

Runs CheckMake against the repository `Makefile` for pull requests to `master` and release branches.

## Important APIs, Types, and Functions

The workflow has one `checkmake` job using pinned `actions/checkout` and `Uno-Takashi/checkmake-action` with `Makefile: Makefile` and `debug: true`.

## Control Flow

Pull request events trigger the job, concurrency cancels older runs for the same PR, checkout fetches the repository, and the action parses the Makefile using the local `checkmake.ini` configuration.

## State and Persistence Behavior

The workflow writes no repository state. Its only durable state is the GitHub check result and logs.

## Dependencies and Integration Points

It integrates with `checkmake.ini`, the root `Makefile`, branch protection, and Mergify check names. It requires only read access to contents.

## Risks and Edge Cases

The external action and CheckMake parser may lag Makefile syntax. With `debug: true`, logs are more verbose but still do not modify files.

## Test Signals

A passing `CheckMake` check indicates Makefile linting passed for the PR.
