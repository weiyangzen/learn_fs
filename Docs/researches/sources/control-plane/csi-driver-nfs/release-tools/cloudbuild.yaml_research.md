# sources/control-plane/csi-driver-nfs/release-tools/cloudbuild.yaml

Purpose: Google Cloud Build configuration for Kubernetes CSI multi-architecture image publishing.

Important configuration: sets a 7200-second timeout, allows loose substitutions, runs one step using `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud:v20260205-38cfa9523f`, invokes `./.cloudbuild.sh`, and passes `GIT_TAG`, `PULL_BASE_REF`, `REGISTRY_NAME`, and `HOME`.

Control flow: Cloud Build fills substitutions, starts the Docker/gcloud image, executes the repository's `.cloudbuild.sh`, and relies on that script to call `gcr_cloud_build`.

State and persistence behavior: Cloud Build produces container images in the configured staging registry; the repository checkout is not committed back.

Dependencies and integration points: integrates with Kubernetes test-infra image-pushing jobs, the staging project `k8s-staging-sig-storage`, `cloudbuild.sh`, and consuming repos' Makefile/Dockerfile conventions.

Risks: assumes Dockerfiles accept a `binary` build argument and the repo supports `make push-multiarch`. Pinned builder images and substitutions need periodic maintenance.

Test signals: Cloud Build status and pushed image artifacts are the practical validation.
