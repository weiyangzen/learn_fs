## sources/control-plane/csi-driver-iscsi/.github/workflows/pluto.yaml

Purpose: checks Kubernetes manifests for deprecated API versions using Pluto.

Control flow runs on push and pull_request, checks out code, downloads Pluto through `FairwindsOps/pluto/github-action`, and runs `pluto detect-files -d deploy`. State is workflow output only.

Dependencies are GitHub Actions and Pluto's API deprecation database. Risks include scanning only `deploy`, not `examples`, and action database drift. Test signal is failure when deploy manifests use deprecated or removed Kubernetes APIs.
