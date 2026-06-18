# sources/cloud-native/buildkit/.github/workflows/buildkit.yml

## Purpose
Main BuildKit CI, image, binary, vulnerability, scout, and release workflow. It runs on schedule, manual dispatch, pushes to master/release branches/tags, and PRs except docs-only paths.

## APIs, Flow, And State
Jobs prepare bake platform matrices, build signed/SBOM release binaries via reusable `docker/github-builder`, finalize artifacts, invoke `.test.yml`, run `govulncheck`, compute image tag matrices, build/push BuildKit images, run Docker Scout on master images, and draft GitHub releases for version tags. Control flow is mostly `needs`: binaries feed tests/finalization; tests gate images and releases; images gate scout.

## Dependencies And Integration
Depends on Buildx, bake targets (`release`, `integration-tests`, `govulncheck`, `image-cross`), DockerHub secrets, Codecov, GitHub OIDC signing, SARIF upload, Docker Scout, and `softprops/action-gh-release`. It integrates with Docker image tagging conventions for latest, nightly, master, semver, rootless, and ubuntu variants.

## Risks And Test Signals
Risks include tag-generation mistakes, accidental image pushes, secret availability, cache poisoning/misses, and release artifact renaming assumptions. Test signals are matrix test results, artifact presence, SARIF uploads, Scout SARIF, SBOM/provenance outputs, and draft release creation.
