# sources/cloud-native/containerd/.github/workflows/fuzz.yml

## Purpose
This workflow runs fuzzing checks on pull requests for containerd.

## Important APIs, Types, And Functions
It has `ci_fuzz` using Google OSS-Fuzz CIFuzz build/run actions for project `containerd`, and `go_test_fuzz` using the repository `script/go-test-fuzz.sh`. Crash artifacts are uploaded on failure.

## Control Flow
For upstream PRs, CIFuzz builds fuzzers, runs them for 300 seconds with `continue-on-error: true`, and uploads crash artifacts when appropriate. The Go test fuzz job checks out code, installs Go, runs Go-native fuzz targets, and uploads fuzz testdata artifacts if it fails.

## State And Persistence
Workflow artifacts may persist crash reproducers. No source state is changed.

## Dependencies And Integration Points
It depends on OSS-Fuzz project configuration, Go fuzz tests in the repository, and the local Go setup action.

## Risks
`continue-on-error` on CIFuzz run can hide runtime fuzz failures unless artifact/status handling is monitored. The workflow is upstream-only and PR-only.

## Test Signals
Fuzzer build success, Go fuzz script success, and absence of uploaded crash artifacts are the main signals.
