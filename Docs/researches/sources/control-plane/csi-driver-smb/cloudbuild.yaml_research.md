<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/cloudbuild.yaml -->
# Research: sources/control-plane/csi-driver-smb/cloudbuild.yaml

- Purpose: Google Cloud Build configuration for multi-architecture CSI SMB image building in Kubernetes staging infrastructure.
- Important APIs/types/functions: uses Cloud Build `timeout: 7200s`, `ALLOW_LOOSE` substitutions, a `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud` builder, and runs `./.cloudbuild.sh` with `GIT_TAG`, `PULL_BASE_REF`, `REGISTRY_NAME`, and `HOME` environment variables.
- Control flow: Cloud Build injects substitutions, starts the builder image, and delegates all repo-specific build/push behavior to `.cloudbuild.sh`; this file mainly wires the release-tools contract to Kubernetes image promotion staging.
- State and persistence behavior: no repo runtime state; build outputs are container images pushed to the configured staging registry, with tags derived from `_GIT_TAG`/branch context.
- Dependencies/integration points: Kubernetes test-infra image-pushing jobs, csi-release-tools conventions, `.cloudbuild.sh`, Dockerfiles accepting a `binary` build argument, and `k8s-staging-sig-storage` registry permissions.
- Risks: loose substitutions can mask unset variables, builder image drift can break builds, and incorrect staging project or tag values push images to the wrong location.
- Test signals: Cloud Build status, image presence in staging registry, and successful downstream promotion jobs.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/cloudbuild.yaml -->
