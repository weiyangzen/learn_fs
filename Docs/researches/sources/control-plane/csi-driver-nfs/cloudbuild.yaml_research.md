# sources/control-plane/csi-driver-nfs/cloudbuild.yaml

## Purpose
Google Cloud Build configuration for multi-architecture CSI NFS image builds and staging publication.

## Important APIs, Types, And Functions
Uses Cloud Build `timeout`, `options.substitution_option: ALLOW_LOOSE`, one build step image `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud:v20260205-38cfa9523f`, entrypoint `./.cloudbuild.sh`, and substitutions `_GIT_TAG`, `_PULL_BASE_REF`, and `_STAGING_PROJECT`.

## Control Flow
Cloud Build runs `.cloudbuild.sh` with environment values for the git tag, base ref, registry name, and home directory. Comments state the repository must import csi-release-tools, provide `.cloudbuild.sh`, and accept a `binary` Dockerfile build argument.

## State And Persistence
Build outputs are container images pushed to the configured staging registry. The YAML itself has no runtime storage, but substitutions and Cloud Build logs preserve build metadata.

## Dependencies And Integration Points
Integrates with Kubernetes test-infra image-pushing workflows, csi-release-tools, `.cloudbuild.sh`, Dockerfiles that consume prebuilt binaries, and the `k8s-staging-sig-storage` registry.

## Risks And Edge Cases
The build image tag and release-tools expectations can drift. A too-short timeout would fail slow multi-arch builds, so this uses 7200 seconds. Loose substitutions prevent failures when optional refs are absent but can hide missing expected values.

## Test Signals
Run or dry-run Cloud Build configuration in the staging project, verify `.cloudbuild.sh` exists and is executable, and confirm images are published with the expected `_GIT_TAG`.
