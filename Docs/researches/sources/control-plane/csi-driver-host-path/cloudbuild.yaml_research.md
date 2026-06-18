<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/cloudbuild.yaml -->
## sources/control-plane/csi-driver-host-path/cloudbuild.yaml

Purpose: Google Cloud Build configuration for multi-arch staging image builds.

Behavior: sets 7200s timeout, allows loose substitutions, runs `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud:v20260205-38cfa9523f` with entrypoint `./.cloudbuild.sh`, and passes git tag, base ref, registry, and HOME environment. Defines default substitutions for tag, base ref, and staging project.

State and dependencies: produces container images in Kubernetes staging registry via release-tools and Cloud Build.

Integration points: Kubernetes image promotion workflow and Prow-triggered Cloud Build.

Risks: builder image tag and release-tools behavior are external dependencies. Default substitutions are placeholders and must be overridden by real jobs.

Test signals: Cloud Build success/failure.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/cloudbuild.yaml -->
