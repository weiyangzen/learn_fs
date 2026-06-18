# sources/cloud-native/containerd/.github/workflows/buf-breaking.yml

## Purpose
This workflow detects breaking changes in protobuf API files during pull requests.

## Important APIs, Types, And Functions
It triggers on PR changes to `api/**/*.proto` or `api/buf.yaml`, uses `bufbuild/buf-action@v1` with Buf `1.63.0`, and disables breaking checks when the PR has label `breaking-api-change`.

## Control Flow
For target branches `main` and `release/**`, the workflow checks out code and runs Buf against input `api` with lint/format/commenting disabled and breaking detection controlled by labels.

## State And Persistence
No repository state is persisted. The workflow reports check status on PRs.

## Dependencies And Integration Points
It integrates with Buf's breaking-change engine, GitHub PR labels, and API proto files.

## Risks
Maintainers can bypass detection with a label, which is intentional but should be controlled. Only proto and `buf.yaml` path changes trigger the workflow; generator config changes in `buf.gen.yaml` are not included.

## Test Signals
PRs changing `api/**/*.proto` should show Buf status, and labeled breaking-change PRs should bypass only the breaking gate.
