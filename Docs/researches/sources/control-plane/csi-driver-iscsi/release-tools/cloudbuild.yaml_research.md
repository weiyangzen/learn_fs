# sources/control-plane/csi-driver-iscsi/release-tools/cloudbuild.yaml

Purpose: reusable Google Cloud Build configuration for Kubernetes CSI multi-architecture image publishing.

Important APIs and types: sets `timeout: 7200s`, allows loose substitutions, runs one step in `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud:v20260205-38cfa9523f`, uses `./.cloudbuild.sh` as entrypoint, and passes `GIT_TAG`, `PULL_BASE_REF`, `REGISTRY_NAME`, and `HOME`.

Control flow: Cloud Build resolves substitutions, launches the builder image, executes `.cloudbuild.sh`, and delegates actual image build/push behavior to release-tools.

State and persistence: produces pushed images in the staging registry; the YAML itself is declarative.

Dependencies and integration: integrates with Kubernetes image-pushing jobs, repo symlink conventions, Dockerfiles that accept `binary`, and `release-tools/cloudbuild.sh`.

Risks: the builder image tag is pinned and must be maintained. Repositories without expected Makefile/Dockerfile contracts will fail at runtime. Default substitution values are placeholders and rely on Prow/Cloud Build overrides.

Test signals: Cloud Build logs, resulting image manifests, and promotion readiness.
