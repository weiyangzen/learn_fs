<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/.github/workflows/trivy.yaml -->
# sources/control-plane/csi-driver-smb/release-tools/.github/workflows/trivy.yaml

Purpose: GitHub Actions workflow that scans the configured Go toolchain image for vulnerabilities with Trivy.

Important configuration: Runs on pushes to `master` and daily schedule. It reads `CSI_PROW_GO_VERSION_BUILD` from `prow.sh`, emits it as a step output, then scans `golang:<version>` with pinned `aquasecurity/trivy-action`. It fails on any vulnerability severity from UNKNOWN through CRITICAL when unfixed issues are ignored.

Control flow: Checkout, parse Go version with shell pipeline, run Trivy action.

State and persistence behavior: No local persistence. Results live in the workflow run and may fail CI.

Dependencies and integration points: Couples directly to `prow.sh` config syntax. Supports release-tools maintenance by detecting vulnerable Go base images.

Risks: The `grep|awk|sed` parser is brittle if `prow.sh` changes formatting. Scanning `golang:<version>` may not exactly match all CI images or build environments.

Test signals: CI vulnerability signal for the Go version used by release-tools.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/.github/workflows/trivy.yaml -->
