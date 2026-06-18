# sources/cloud-native/containerd/.github/workflows/release.yml

## Purpose
This workflow builds release binaries and publishes full containerd GitHub releases for tags matching `v*`; it also builds release artifacts on pushes/PRs to main and release branches.

## Important APIs, Types, And Functions
Jobs are `check`, `build`, and `release`. It verifies signed tags, extracts release notes, builds platform release tarballs through Docker Buildx using `.github/workflows/release/Dockerfile`, uploads artifacts, creates build provenance attestations, and publishes via `softprops/action-gh-release`.

## Control Flow
`check` runs only for tag pushes and validates tag signatures, including SSH allowed-signers config setup. `build` runs a platform matrix for Linux amd64/arm64/ppc64le/s390x/riscv64 and Windows amd64, setting `RELEASE_VER` for tags, invoking Docker Buildx, and uploading release tarballs. `release` runs only for tag pushes, downloads artifacts, attests `.tar.gz` files, renames the attestation bundle, and creates the latest GitHub release.

## State And Persistence
Persistent outputs are release artifacts, checksums from Makefile release targets, a GitHub Release, and provenance attestation JSONL. Intermediate Actions artifacts are also stored.

## Dependencies And Integration Points
It depends on signed tags, Docker Buildx, `tonistiigi/xx`, Go release image, the release Dockerfile, Makefile `release static-release`, GitHub artifact and attestation actions, and `GITHUB_TOKEN`.

## Risks
Release correctness depends on the build Dockerfile and Makefile staying in sync. The build job runs for PRs too but release publication is tag-only. Windows build args for CNI networking are hard-coded from previously generated packages. Tag signature shell logic is subtle and security-critical.

## Test Signals
Successful matrix artifact builds on PRs/branches, signed tag release runs, attestation creation, and uploaded release assets validate this workflow.
