# sources/cloud-native/stargz-snapshotter/.github/workflows/release.yml

## Purpose
The release workflow builds static release tarballs for multiple Linux architectures and creates a draft GitHub release.

## Important APIs, Types, and Functions
It triggers on `v*` tag pushes. The build job matrix covers amd64, arm-v7, arm64, ppc64le, and s390x. It uses Docker target `release-binaries`, gzip-compresses the output tar stream, writes sha256sum files, and uploads artifacts. The release job downloads artifacts and calls `gh release create` with a draft note.

## Control Flow, State, and Persistence
Build artifacts are persisted via upload/download artifact actions. The final draft release is persisted in GitHub releases using `GITHUB_TOKEN`.

## Dependencies and Integration Points
It depends on Docker BuildKit, repository Dockerfile release target, `sha256sum`, GitHub CLI, and artifact actions.

## Risks and Test Signals
Release notes are placeholder `(TBD)`. Asset glob expansion depends on shell behavior and downloaded artifact directory names. `CGO_ENABLED=0` is forced for static binaries.
