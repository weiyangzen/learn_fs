# sources/control-plane/csi-lib-utils/release-tools/cloudbuild.yaml

## Purpose

This Google Cloud Build configuration runs multi-architecture image publishing for CSI repositories that import release tools. It is intended to be symlinked or copied by component repositories.

## Important Behavior

The build timeout is two hours. `substitution_option: ALLOW_LOOSE` tolerates unused substitutions. A single build step runs `./.cloudbuild.sh` in the `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud` image and passes `GIT_TAG`, `PULL_BASE_REF`, `REGISTRY_NAME`, and `HOME=/root`. Default substitutions provide placeholder `_GIT_TAG`, `_PULL_BASE_REF`, and `_STAGING_PROJECT`.

## State, Dependencies, and Integration

State is external: built images and registry pushes. Dependencies include the Cloud Build service, staging project permissions, Docker, gcloud, and a repo-provided `.cloudbuild.sh` wrapper. It integrates with Kubernetes image-pushing jobs and k8s staging registries.

## Risks and Test Signals

The step image pin is a major supply-chain and reproducibility anchor. Repos must accept `binary` build arguments and implement `make push-multiarch` behavior expected by `prow.sh`. Cloud Build success, registry artifacts, and downstream promotion are the operational test signals.
