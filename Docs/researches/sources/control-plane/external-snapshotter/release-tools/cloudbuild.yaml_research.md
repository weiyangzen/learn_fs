# sources/control-plane/external-snapshotter/release-tools/cloudbuild.yaml

Purpose: reusable Google Cloud Build configuration for Kubernetes CSI multi-architecture image builds.

Important keys: timeout `7200s`, loose substitutions, one build step using `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud:v20260205-38cfa9523f`, entrypoint `./.cloudbuild.sh`, environment variables for tag, branch/ref, staging registry, and home, plus default substitutions for `_GIT_TAG`, `_PULL_BASE_REF`, and `_STAGING_PROJECT`.

Control flow: Cloud Build runs the configured image and invokes repository-specific `.cloudbuild.sh`, which usually delegates into release-tools image build helpers.

State and persistence: persists built container images to the configured staging registry; Cloud Build logs retain build evidence.

Dependencies and integration: integrates Kubernetes image-pushing infrastructure, csi-release-tools, repository Dockerfiles accepting `binary` build args, and staging projects.

Risks and test signals: risks include floating expectations around build image tooling, long timeout masking hangs, loose substitutions hiding missing values, and repo-specific Dockerfile incompatibility. Signal is successful Cloud Build and promoted staging image artifacts.
