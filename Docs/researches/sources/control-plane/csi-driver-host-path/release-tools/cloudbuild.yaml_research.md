## sources/control-plane/csi-driver-host-path/release-tools/cloudbuild.yaml

Purpose: shared Google Cloud Build configuration for multi-architecture CSI image builds. It documents the required symlink/import pattern for consuming repos.

Control flow is declarative: a two-hour timeout, loose substitutions, one `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud` step executing `./.cloudbuild.sh`, and env values for git tag, base ref, staging registry, and HOME. Substitutions define placeholder `_GIT_TAG`, `_PULL_BASE_REF`, and `_STAGING_PROJECT`.

State is Cloud Build execution state and pushed images. Dependencies include the image builder container, `.cloudbuild.sh`, release-tools `gcr_cloud_build`, Docker buildx, and repo Makefile targets. Risks include stale builder image pin, loose substitutions masking missing inputs, and a single entrypoint coupling all repos to shared release-tools behavior. Test signal is image-pushing job result.
