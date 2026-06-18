# sources/cloud-native/nydus-snapshotter/.github/workflows/k8s-e2e.yml

Purpose: reusable Kubernetes E2E workflow template.

Flow: accepts `auth-type` and optional `index-detect`, checks out submodules, sets up Go, runs `./tests/helpers/kind.sh`, and on failure gathers pod YAML/descriptions/logs, secrets, containerd configs, journal logs, process lists, test-pod YAML, and Docker auth config into an uploaded artifact.

State/dependencies: requires kind, kubectl/docker behavior from helper scripts, and a `nydus-system` namespace.

Integration points: called by `k8s-e2e-run.yml` for auth and index detection coverage.

Risks/tests: failure log dump includes secrets YAML and Docker config, which is useful for debugging but sensitive in artifact retention contexts.
