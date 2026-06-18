# sources/cloud-native/buildkit/.github/workflows/frontend.yml

## Purpose
CI, image publishing, security scanning, and release workflow for the Dockerfile frontend images.

## APIs, Flow, And State
Triggers on manual dispatch, master/release pushes, `dockerfile/*` tags, and PRs except docs-only paths. It calls `.test.yml` for frontend packages/kinds, computes image matrix entries for `mainline` and `labs` channels, builds/pushes `docker/dockerfile-upstream` images with SBOMs and metadata, scans master tags with Docker Scout, and drafts GitHub releases for Dockerfile tags.

## Dependencies And Integration
Uses Buildx/bake target `frontend-image-cross`, DockerHub secrets, reusable `docker/github-builder`, Codecov, Scout, SARIF upload, and `softprops/action-gh-release`. Tag logic handles semver major/minor/latest tags plus channel suffixes.

## Risks And Test Signals
Channel parsing is a critical risk: malformed `dockerfile/*` tags can publish unexpected tags or releases. Persistent effects are DockerHub images, SARIF uploads, and draft releases. Test signals are frontend integration tests, image build outputs, Scout reports, and release draft metadata.
