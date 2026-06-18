# sources/cloud-native/stargz-snapshotter/script/k3s-argo-workflow/run.sh

Purpose: Benchmarks Argo workflow runtime on custom k3s images with overlayfs versus stargz snapshotter.
Important APIs/types/functions: helpers `argo_yaml`, `replace_image`, `go_ci_yaml`, and `run`; constants for k3s, containerd, Argo versions.
Control flow: downloads Argo manifest, clones k3s, vendors current stargz snapshotter via git archive, patches go.mod, builds a local k3s node image, then repeatedly creates k3d clusters, installs Argo, submits a Go workflow, records elapsed time, and deletes the cluster.
State and persistence: creates temp cloned repos, generated YAMLs, k3d clusters, local k3s images, and an output JSON-lines result file.
Dependencies and integration points: depends on git, Go, k3s build tooling, k3d, kubectl, argo CLI, envsubst, jq, and current repo commit state.
Risks: very heavyweight and tracks `main` branches by default; local uncommitted changes are excluded because it uses `git archive HEAD`.
Test signals: result file contains elapsed comparisons for overlayfs and stargz workflow runs.
