# sources/control-plane/csi-driver-iscsi/release-tools/.github/workflows/trivy.yaml

Purpose: scans the configured Go build image for vulnerabilities using Trivy.

Important APIs and types: workflow runs on pushes to `master` and daily schedule. It extracts `CSI_PROW_GO_VERSION_BUILD` from `prow.sh`, emits it as a step output, then scans `golang:<version>` with a pinned Trivy action and all severities enabled.

Control flow: checkout, shell extraction of the Go version, Trivy image scan, and fail on vulnerability finding because `exit-code: 1`.

State and persistence: no repo state is written; scan results live in workflow logs/checks.

Dependencies and integration: depends on the exact text shape of `prow.sh`, GitHub Actions, Docker image availability, and Trivy vulnerability DB.

Risks: the `grep|awk|sed` parser is brittle if `prow.sh` formatting changes. `ignore-unfixed: true` reduces noise but can hide unresolved base image exposure until a fixed package exists.

Test signals: scheduled and push workflow status show current Go image vulnerability health.
