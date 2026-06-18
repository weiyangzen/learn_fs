# sources/control-plane/external-snapshotter/release-tools/.github/workflows/trivy.yaml

Purpose: scheduled and master-branch GitHub Actions workflow that scans the configured Go builder image for vulnerabilities with Trivy.

Important keys/steps: workflow name, push-to-master and daily cron triggers, checkout, shell step extracting `CSI_PROW_GO_VERSION_BUILD` from `prow.sh`, and pinned `aquasecurity/trivy-action` scanning `golang:<version>` with exit code `1` for all severities and `ignore-unfixed: true`.

Control flow: checkout repo, parse Go version into `$GITHUB_OUTPUT`, then run Trivy against the corresponding official Golang image.

State and persistence: no repo mutation; vulnerability findings persist in workflow logs and check status.

Dependencies and integration: integrates GitHub Actions, Trivy, `prow.sh` config conventions, and container image vulnerability feeds.

Risks and test signals: parsing `prow.sh` with grep/awk/sed is fragile, scanning only the base Go image may miss repo-built image layers, and all severities can cause frequent failures. Signal is scheduled workflow failure when the selected Go image has unfixed or fixed vulnerabilities matching policy.
