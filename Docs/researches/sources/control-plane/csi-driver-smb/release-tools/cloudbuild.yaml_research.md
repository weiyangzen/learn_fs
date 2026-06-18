<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/cloudbuild.yaml -->
# sources/control-plane/csi-driver-smb/release-tools/cloudbuild.yaml

Purpose: Reusable Google Cloud Build configuration for multi-arch Kubernetes CSI image builds.

Important configuration: Sets a two-hour timeout, allows loose substitutions, runs a pinned `gcb-docker-gcloud` image with `./.cloudbuild.sh` as entrypoint, and passes `GIT_TAG`, `PULL_BASE_REF`, `REGISTRY_NAME`, and `HOME`. Default substitutions include `_GIT_TAG`, `_PULL_BASE_REF`, and `_STAGING_PROJECT`.

Control flow: Cloud Build executes one step; `.cloudbuild.sh` is expected to call `release-tools/cloudbuild.sh` or equivalent.

State and persistence behavior: Produces and pushes multi-arch images through delegated make targets.

Dependencies and integration points: Tied to Kubernetes image-pushing infrastructure, staging projects, Docker buildx behavior, and Dockerfiles accepting a `binary` build argument.

Risks: Assumes importing repos follow symlink and build-argument conventions. The builder image SHA/tag must be maintained. Registry and tag derivation depend on Prow substitutions.

Test signals: Validated by real Cloud Build image-push jobs rather than local tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/cloudbuild.yaml -->
