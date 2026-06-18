# sources/control-plane/csi-driver-nfs/release-tools/.github/workflows/trivy.yaml

Purpose: scans the configured Go toolchain image for vulnerabilities with Trivy.

Important configuration: triggers on pushes to `master` and daily midnight UTC schedule. It checks out code, extracts `CSI_PROW_GO_VERSION_BUILD` from `prow.sh`, then scans `golang:<version>` with `aquasecurity/trivy-action`.

Control flow: the `Get Go version` shell step greps the release-tools `prow.sh` config line and writes the version to GitHub step output. The Trivy step scans the corresponding Golang image, outputs a table, ignores unfixed vulnerabilities, and fails on all severities including unknown.

State and persistence behavior: no repo mutation. Results are GitHub Actions logs/status.

Dependencies and integration points: integrates with `prow.sh` as the source of the supported Go version, GitHub Actions, actions/checkout, and Trivy.

Risks: parsing `prow.sh` with `grep|awk|sed` is brittle if the config line format changes. Scanning the base Golang image may fail for vulnerabilities unrelated to project code.

Test signals: CI failure signals vulnerable Go base image or parsing/action problems.
