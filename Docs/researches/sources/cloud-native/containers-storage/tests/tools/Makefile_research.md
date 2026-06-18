# sources/cloud-native/containers-storage/tests/tools/Makefile

Purpose: builds and vendors auxiliary tools used by the `containers-storage` test and verification workflows.

Important APIs and control flow: `vendor` runs `go mod tidy`, `go mod vendor`, and `go mod verify`. `all` builds the `build` directory targets. `go-build` is a make macro that builds a vendored package into `build/<basename>`. Targets build `git-validation`, `go-md2man`, and `golangci-lint`; the linter target downloads the version specified by `GOLANGCI_LINT_VERSION`.

State and persistence: writes binaries under `build/` and vendored dependencies under `vendor/`. `clean` removes `build/`.

Dependencies and integration: depends on Go modules, vendored tool packages, curl, and the upstream golangci-lint install script. It complements `tools.go`, which pins Go tool dependencies for vendoring.

Risks: `go-build` uses `$(shell ...)` during recipe expansion, which can make failures less obvious than normal recipe commands. The linter target downloads network code at build time and requires `GOLANGCI_LINT_VERSION`.

Test signals: successful target completion confirms tool binaries exist; `go mod verify` validates vendored module integrity.
