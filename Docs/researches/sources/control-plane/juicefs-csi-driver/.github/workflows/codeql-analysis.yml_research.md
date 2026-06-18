# sources/control-plane/juicefs-csi-driver/.github/workflows/codeql-analysis.yml

## Purpose
This workflow runs GitHub CodeQL static analysis for Go code on pushes, pull requests, and a weekly schedule.

## Important Jobs and Steps
The `analyze` job requests `actions:read`, `contents:read`, and `security-events:write` permissions. It checks out code, initializes CodeQL for `go`, uses CodeQL autobuild, and runs `github/codeql-action/analyze`.

## Control Flow
Pushes to `master` run when Go files change while excluding docs and markdown-related files. Pull requests to `master` run on Go changes. A scheduled weekly run catches issues independent of recent PR path filters.

## State and Persistence Behavior
The workflow uploads CodeQL security results to GitHub code scanning. It does not change repository files.

## Dependencies and Integration Points
It depends on GitHub's CodeQL actions and the Go build being discoverable by autobuild. It complements `go.yaml` tests and `golangci` linting by providing security-oriented static analysis.

## Risks
The action versions are older major versions (`checkout@v3`, CodeQL `@v2`). Autobuild may miss custom build flags or generated assets. Path filters may skip relevant security changes outside `**.go` on PRs.

## Test Signals
The workflow emits code scanning alerts and pass/fail status for CodeQL analysis. It does not run runtime tests or E2E suites.
