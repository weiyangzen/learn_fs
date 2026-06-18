# sources/control-plane/beegfs-csi-driver/release-tools/cloudbuild.yaml

Purpose: Google Cloud Build configuration for Kubernetes CSI multi-architecture image builds.

Important APIs/types/functions: Sets `timeout: 7200s`, `substitution_option: ALLOW_LOOSE`, and one build step using `gcr.io/k8s-testimages/gcb-docker-gcloud:v20230623-56e06d7c18` with entrypoint `./.cloudbuild.sh`. Passes `GIT_TAG`, `PULL_BASE_REF`, `REGISTRY_NAME`, and `HOME` via environment. Defines default substitutions for `_GIT_TAG`, `_PULL_BASE_REF`, and `_STAGING_PROJECT`.

Control flow: Cloud Build expands substitutions, runs `.cloudbuild.sh`, and that script calls `gcr_cloud_build` from `prow.sh`. Repos importing this file are expected to symlink or copy it and provide compatible Dockerfiles and Makefile targets.

State and persistence: Produces pushed container images in the configured staging registry. No repository file writes are specified by the YAML itself.

Dependencies and integration points: Integrates Kubernetes test-infra image-pushing conventions, GCR staging projects, Docker buildx, and `make push-multiarch`.

Risks: Image builder version and staging project defaults can become stale. `ALLOW_LOOSE` avoids missing substitution failures but can hide misconfigured variables. Build timeout must remain high enough for multiple architectures.

Test signals: Operational signal comes from Cloud Build/Prow image-pushing jobs, not unit tests.
