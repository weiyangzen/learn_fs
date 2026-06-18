<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/Makefile -->
# sources/control-plane/beegfs-csi-driver/operator/Makefile

Purpose: development, build, deployment, bundle, and catalog automation for the BeeGFS CSI operator.

Important APIs and flow: key targets include `manifests`, `generate`, `fmt`, `vet`, `test`, `build`, `run`, `docker-build`, `install`, `deploy`, `bundle`, `bundle-build`, `catalog-build`, and `docker-buildx`. The build loop compiles `main.go` for tuples in `BUILD_PLATFORMS`; `test` uses envtest assets; `bundle` regenerates OLM manifests and applies a custom OpenShift minimum version script; `docker-buildx` is intentionally disabled.

State and persistence: writes binaries and tools under `bin`, CRD/bundle manifests under config/bundle paths, local cover profiles, and may mutate Kustomize image references.

Dependencies and integration points: uses Go, controller-gen, kustomize, setup-envtest, operator-sdk, opm, Docker, kubectl, and GitHub-hosted tool downloads.

Risks and test signals: network/tool version drift affects reproducibility; `docker-buildx` exits intentionally. Test with `make test`, `make bundle`, and operator-sdk bundle validation.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/Makefile -->
