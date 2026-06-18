# sources/cloud-native/containerd/.github/actions/install-go/action.yml

## Purpose
This composite GitHub Action centralizes Go installation for containerd workflows.

## Important APIs, Types, And Functions
It defines required input `go-version` with default `1.26.4` and runs `actions/setup-go` pinned to a full commit SHA corresponding to v6.4.0.

## Control Flow
Workflows call this local action, optionally overriding `go-version`; the composite step delegates to `actions/setup-go`.

## State And Persistence
It modifies the workflow runner environment by installing/selecting Go. No repository files are modified.

## Dependencies And Integration Points
It is used by CI, release, nightly, image, CodeQL, and node e2e workflows. It should stay aligned with `go.mod`, devcontainer Go feature version, and release Dockerfile `GO_VERSION`.

## Risks
If the pinned `actions/setup-go` SHA is stale or compromised upstream policy changes, every workflow using this local action is affected. The `required: true` input still has a default, so callers usually do not pass a value.

## Test Signals
Workflow runs should confirm `go version` and cache/setup behavior after version bumps.
