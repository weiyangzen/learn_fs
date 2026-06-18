## sources/control-plane/csi-driver-iscsi/.github/workflows/golangci-lint.yml

Purpose: runs golangci-lint as a static check on pushes and pull requests.

Control flow sets up Go `^1.22`, checks out the repository, and runs the pinned `golangci/golangci-lint-action` with default configuration. State is workflow output and linter cache managed by the action.

Dependencies are GitHub Actions, setup-go, checkout, and golangci-lint. Risks include different Go version than build workflows, default linter config drift through action version, and possible vendor/module behavior mismatch. Test signal is linter findings.
