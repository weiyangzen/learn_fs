# sources/distributed-fs/beegfs-go/.github/workflows/release.yml

## Purpose
This workflow runs GoReleaser for BeeGFS binary/package releases when version tags matching `v8.*` are pushed.

## Control Flow
The `goreleaser` job checks out full history, logs into GHCR, imports a GPG package key, sets up Go from `go.mod`, computes `GORELEASER_CURRENT_TAG` and `GORELEASER_PREVIOUS_TAG`, and runs `goreleaser release --clean`. Tag selection sorts semantic tags by temporarily replacing prerelease dashes with tildes before `sort -Vr`.

## Dependencies and Integration
The workflow needs `contents: write` for releases, `packages: write` for GHCR, Docker login action, GPG import action, `actions/setup-go`, GoReleaser action v6, secrets for GPG material, and `GITHUB_TOKEN`.

## Risks and Test Signals
Release correctness depends on tag naming and the custom previous-tag pipeline. The workflow is restricted to `v8.*`, intentionally avoiding Go module API tags. GPG and GHCR credentials are hard release blockers.
