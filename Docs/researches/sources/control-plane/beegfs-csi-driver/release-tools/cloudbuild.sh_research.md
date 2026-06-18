# sources/control-plane/beegfs-csi-driver/release-tools/cloudbuild.sh

Purpose: Thin Cloud Build entrypoint that sources release-tools Prow/build helpers and runs the Google Container Registry multi-architecture build flow.

Important APIs/types/functions: Sources `release-tools/prow.sh` and calls `gcr_cloud_build`.

Control flow: The script is expected to be invoked as `.cloudbuild.sh` from a repository that imports release-tools. `gcr_cloud_build` performs Docker credential setup, optional QEMU registration, derives revision metadata from `GIT_TAG`, and invokes `make push-multiarch`.

State and persistence: Effects are delegated to `gcr_cloud_build`: Docker auth config, buildx/QEMU setup, container builds, and pushed images.

Dependencies and integration points: Used by `cloudbuild.yaml` as the build step entrypoint. Depends on `release-tools/prow.sh`, `gcloud`, Docker, Go, and Makefile targets in the importing repository.

Risks: Because it sources the large `prow.sh`, all default config variables are evaluated in the Cloud Build environment. It assumes the working tree has a `release-tools/prow.sh` path and suitable Makefile.

Test signals: Covered by Cloud Build jobs using `cloudbuild.yaml`; no local unit tests.
