# sources/control-plane/csi-driver-nfs/.github/workflows/static.yaml

Purpose: runs Go static analysis and Helm chart verification for the NFS driver.

Important APIs and types: `go_lint` job uses setup-go `^1.19`, pinned checkout, and pinned `golangci-lint-action` v2.10 with explicit enabled linters and 30-minute timeout. `verify-helm` installs `yq` via snap and runs `sudo hack/verify-helm-chart.sh`.

Control flow: the lint job analyzes Go code; the Helm job checks chart rendering/consistency through repository hack script.

State and persistence: no intended repo writes; verification may render temp artifacts.

Dependencies and integration: depends on `.golangci.yml`, golangci-lint, yq, Helm verification script, and sudo availability.

Risks: workflow args enable many linters beyond `.golangci.yml` default staticcheck, so local and CI lint surfaces may differ. Installing yq from snap can be slow or version-sensitive.

Test signals: lint annotations, Helm verification output, and job status.
