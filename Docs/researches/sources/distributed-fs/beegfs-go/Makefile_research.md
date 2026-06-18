# sources/distributed-fs/beegfs-go/Makefile

## Purpose
The Makefile centralizes local install, uninstall, package, notice generation, and validation targets for the BeeGFS Go repository.

## APIs and Control Flow
Generated install/uninstall rules cover `beegfs`, `beegfs-remote`, `beegfs-sync`, and `beegfs-watch`, installing to `$(HOME)/go/bin`. `package-all` runs local snapshot GoReleaser packaging. `generate-notices` uses `go tool go-licenses report` for ctl, remote, sync, and watch notices. `test` chains `check-go-version`, `check-gofmt`, `check-linters`, `check-go-tidy`, `test-unit`, `check-vulnerabilities`, and `check-licenses`. `tidy` runs `go mod tidy`.

## Dependencies and Integration
The file depends on Bash, Go toolchain/tool directives, staticcheck, govulncheck, go-licenses, GoReleaser for packaging, Git status checks, and repository notice templates.

## Risks and Test Signals
`make test` can modify local files through tidy and notice generation, then fails if changes appear. Go version checking requires exact `go version` match with `go.mod`. License checking intentionally ignores selected private or manually reviewed dependencies. The Makefile is the core CI signal invoked by `.github/workflows/checks.yml`.
