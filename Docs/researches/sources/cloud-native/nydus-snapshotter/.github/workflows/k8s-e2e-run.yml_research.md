# sources/cloud-native/nydus-snapshotter/.github/workflows/k8s-e2e-run.yml

Purpose: orchestrates Kubernetes E2E scenarios through a reusable workflow.

Flow: on main pushes, semver tags, and PRs to main, it invokes `.github/workflows/k8s-e2e.yml` three times: CRI auth, kubeconfig auth, and kubeconfig with index detection.

State/dependencies: no direct commands; delegates all state to called workflow jobs.

Integration points: keeps scenario matrix small while reusing the Kubernetes test template.

Risks/tests: failures are surfaced from the reusable workflow. Any new auth mode must be added here to enter the k8s E2E matrix.
