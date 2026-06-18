# sources/control-plane/csi-driver-iscsi/release-tools/cloudbuild.sh

Purpose: generic Cloud Build entrypoint for repositories importing CSI release-tools.

Important APIs and types: sources `release-tools/prow.sh` and calls `gcr_cloud_build`.

Control flow: when Google Cloud Build invokes this script, `prow.sh` defines configuration and helper functions, then `gcr_cloud_build` authenticates Docker with gcloud, prepares the build environment, optionally registers QEMU, and runs `make push-multiarch`.

State and persistence: pushes container images to the configured registry through `REGISTRY_NAME` and `GIT_TAG` environment values.

Dependencies and integration: depends on Cloud Build, gcloud, Docker buildx, Go, repository Makefile targets, and `release-tools/prow.sh`.

Risks: assumes caller has a top-level `release-tools` import and Makefile support for `push-multiarch`. Missing environment variables are handled mostly by downstream make/prow logic.

Test signals: Cloud Build success and pushed multi-architecture images.
