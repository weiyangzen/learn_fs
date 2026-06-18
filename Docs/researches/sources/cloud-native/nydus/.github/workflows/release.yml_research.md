# sources/cloud-native/nydus/.github/workflows/release.yml

## Purpose
This workflow builds release artifacts for tagged Nydus releases and daily sanity checks, covering Linux, macOS, Go contrib binaries, tarballs, GitHub releases, GoReleaser packaging, and SLSA provenance.

## Important APIs, Types, and Functions
Jobs include multi-arch `nydus-linux`, multi-arch `nydus-macos`, multi-arch `contrib-linux`, `prepare-tarball-linux`, `prepare-tarball-darwin`, `create-release`, `goreleaser`, and `provenance`. It uses `cross`, Docker Buildx for riscv64, a custom cross Dockerfile, `make static-release`, `make contrib-release`, `actions/upload-artifact`, `softprops/action-gh-release`, `goreleaser/goreleaser-action`, and SLSA generator.

## Control Flow
On tag push, schedule, or manual dispatch, Linux and macOS jobs build static binaries per arch and upload artifacts. Contrib jobs build Go tools. Tarball jobs download/merge artifacts, produce `nydus-static-<tag>-<os>-<arch>.tgz` and sha256sum files, and upload them. `create-release` downloads tarballs and creates a GitHub release only for push events. `goreleaser` runs only for tag pushes, prepares context from artifacts, runs checks and release, and emits base64-encoded subject hashes. `provenance` runs SLSA generation for tag pushes.

## State and Persistence
Persistent outputs are GitHub Actions artifacts, release assets, GoReleaser artifacts, checksums, and provenance attestations. Runtime state includes cross containers, cargo/go caches, and copied `misc/configs`.

## Dependencies and Integration Points
The workflow depends on the workspace Makefile, rust-toolchain, `Cross.toml`, Go workspace, `goreleaser.sh`, GoReleaser config, GitHub release permissions, and SLSA workflow interface.

## Risks and Edge Cases
The provenance job references `${{ needs.release.outputs.tag_name }}`, but there is no `release` job in `needs`; the tag output is defined by `goreleaser`, so this expression appears incorrect. The `provenance` job depends only on `goreleaser`; if draft upload tag is miswired, attestation upload may fail. Multi-arch builds rely on cross image/toolchain compatibility. Scheduled runs have no tag, so tarball naming from `GITHUB_REF` may produce branch-like names and release steps are skipped by event conditions.

## Test Signals
Signals include successful multi-arch binary builds, uploaded artifacts/tarballs/checksums, release asset creation on tag push, GoReleaser check/release success, and SLSA provenance completion.
