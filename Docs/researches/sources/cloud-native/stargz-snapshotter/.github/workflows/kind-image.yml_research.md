# sources/cloud-native/stargz-snapshotter/.github/workflows/kind-image.yml

## Purpose
The kind-image workflow builds and optionally pushes multi-arch KinD node images tagged for releases.

## Important APIs, Types, and Functions
It triggers on version tags and pull requests. Steps checkout, compute Docker metadata, login to GHCR except on PRs, set up QEMU and Buildx, and run `docker/build-push-action` for linux/amd64 and linux/arm64.

## Control Flow, State, and Persistence
For PRs, the image is built but not pushed. For tag pushes, credentials from `GITHUB_TOKEN` push images to `ghcr.io/<repository>` with semver `{{version}}-kind` tags.

## Dependencies and Integration Points
It depends on Docker metadata/login/setup-qemu/setup-buildx/build-push GitHub Actions and the repository Dockerfile kind target.

## Risks and Test Signals
Tag patterns only match `v*`; nonstandard release tags will not run. Multi-arch builds rely on QEMU/binfmt. The workflow does not upload local artifacts for PR inspection.
