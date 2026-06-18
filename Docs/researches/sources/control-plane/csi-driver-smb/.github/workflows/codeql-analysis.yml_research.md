## sources/control-plane/csi-driver-smb/.github/workflows/codeql-analysis.yml

Purpose: runs CodeQL analysis for Go on pushes, pull requests, and a daily schedule. It grants read permissions for actions/contents and write permission for security events.

Important flow: it sets up Go `^1.18`, checks out code with pinned actions, initializes CodeQL for language `go`, runs `make all` as the autobuild step, then invokes CodeQL analysis. The matrix is single-language but keeps `fail-fast: false`.

State is GitHub Actions workspace plus uploaded SARIF/security results. Dependencies include `make all`, vendored Go dependencies, CodeQL action v4, and setup-go. Risks include old Go version relative to current module needs, build failures blocking analysis, and analysis only covering Go. Test signal is GitHub security analysis completion and alerts.
