## sources/control-plane/csi-driver-iscsi/.github/workflows/codeql-analysis.yml

Purpose: runs CodeQL analysis for the Go codebase on master/release pushes, matching pull requests, and daily schedule.

Control flow sets up Go `^1.18`, checks out code, initializes CodeQL for Go, runs `make all` as autobuild, then performs analysis. Permissions allow security event upload.

State is GitHub Actions build and CodeQL database/upload state. Dependencies include pinned setup-go/checkout/codeql actions and Makefile compatibility with the chosen Go. Risks include old Go setup relative to newer lint/trivy workflows, CodeQL build failures when vendor/toolchain changes, and only Go language coverage. Test signal is CodeQL alerts or workflow failure.
