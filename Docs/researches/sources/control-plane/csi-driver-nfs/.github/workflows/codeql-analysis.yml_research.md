# sources/control-plane/csi-driver-nfs/.github/workflows/codeql-analysis.yml

Purpose: runs CodeQL security analysis for Go code in the NFS driver.

Important APIs and types: workflow triggers on pushes and PRs to `master` and `release-**`, plus daily schedule. Job grants `security-events: write`, sets up Go `^1.18`, checks out code, initializes CodeQL for language `go`, runs `make all`, then analyzes.

Control flow: CodeQL database initialization precedes build so compiled Go code is captured, then CodeQL uploads analysis results.

State and persistence: security alerts/results in GitHub code scanning.

Dependencies and integration: depends on GitHub CodeQL action, setup-go, checkout, and the Makefile build target.

Risks: setup Go version is older than the Makefile and Trivy workflow versions, which can expose version skew. Autobuild is replaced with explicit `make all` but still assumes Linux build defaults are valid.

Test signals: CodeQL job status and code scanning alerts.
