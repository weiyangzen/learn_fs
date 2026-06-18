## sources/control-plane/csi-driver-iscsi/cloudbuild.yaml

Purpose: repo-local Cloud Build configuration, equivalent to the shared release-tools template, for publishing csi-driver-iscsi images.

Control flow uses a two-hour timeout, loose substitutions, a single builder step executing `./.cloudbuild.sh`, and environment variables for git tag, base ref, staging registry, and HOME. Placeholder substitutions define `_GIT_TAG`, `_PULL_BASE_REF`, and `_STAGING_PROJECT`.

State is Cloud Build job state and pushed images. Dependencies include `.cloudbuild.sh`, shared release-tools, Docker buildx, Makefile image targets, and staging project configuration. Risks mirror the shared template: stale builder image pin, loose substitutions hiding misconfiguration, and central coupling to `gcr_cloud_build`. Test signal is Cloud Build success.
