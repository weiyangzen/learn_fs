# sources/control-plane/rook/.github/workflows/daily-nightly-jobs.yml

## Purpose

Runs scheduled and manually dispatched nightly Rook tests against ARM64 and development Ceph images.

## Important APIs, Types, and Functions

Jobs include `canary-arm64`, smoke suites for `squid-devel`, `tentacle-devel`, and Ceph `main`, object suites with and without TLS for Ceph `main`, upgrade suites from stable to development Ceph versions, and `canary-tests` which calls the reusable canary workflow with five Ceph images. `GOFLAGS=-tags=ceph_preview` is set globally.

## Control Flow

The workflow runs daily at midnight or on manual dispatch. Every job is gated to `github.repository == 'rook/rook'`, checks out full history, can enable tmate, provisions cluster resources at Kubernetes `v1.35.5`, runs a targeted `go test` or canary workflow, collects logs, and uploads failure artifacts.

## State and Persistence Behavior

Cluster and test state is ephemeral. Logs under the integration output directory and canary `test` directory are persisted only when uploaded. The reusable canary receives secrets by inheritance.

## Dependencies and Integration Points

It integrates with the reusable canary, setup and debug composite actions, Go integration tests, `tests/scripts/github-action-helper.sh`, `tests/scripts/collect-logs.sh`, GitHub secrets, and ARM runners.

## Risks and Edge Cases

Nightlies are sensitive to external Ceph development image availability and behavior. ARM64 jobs disable liveness probes due to slow environment assumptions. The workflow exercises more images than PR CI, so check names and runtime cost are substantial.

## Test Signals

Passing nightlies indicate current Rook works against latest/development Ceph images and ARM64 canary coverage. Failure artifacts are the key diagnostic signal.
