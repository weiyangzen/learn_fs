# sources/distributed-fs/beegfs-go/.github/workflows/checks.yml

## Purpose
This GitHub Actions workflow runs the BeeGFS Go repository's standard checks and unit tests.

## Control Flow
It triggers on pull requests except Markdown-only path changes and can also be invoked by `workflow_call`. The single `checks` job runs on Ubuntu, grants read-only contents permission, checks out the repository, installs Go using `go.mod`, and runs `make test`.

## Dependencies and Integration
The workflow depends on `actions/checkout@v4`, `actions/setup-go@v5`, and the repository `Makefile`. `make test` fans out to Go version, formatting, static analysis, tidy, unit tests, vulnerabilities, and license checks.

## Risks and Test Signals
Markdown-only PRs skip this workflow, so code embedded in docs would not be checked here. The workflow is concise and delegates risk to `Makefile` targets, which may modify `go.mod`, `go.sum`, and NOTICE files during validation.
