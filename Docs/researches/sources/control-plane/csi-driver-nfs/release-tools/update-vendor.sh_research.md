# sources/control-plane/csi-driver-nfs/release-tools/update-vendor.sh

Purpose: refreshes dependency vendoring for repositories using either dep or Go modules.

Important commands: checks for `Gopkg.toml` and runs `dep ensure`; otherwise checks for `go.mod`, runs `release-tools/verify-go-version.sh go`, then `go mod tidy` and `go mod vendor` with `GO111MODULE=on`.

Control flow: simple conditional selection based on dependency management files in the current directory.

State and persistence behavior: mutates dependency lock/vendor state through `dep ensure` or Go module tidy/vendor output. It does not commit changes.

Dependencies and integration points: used by release and maintenance workflows. Depends on dep for legacy repos, Go tooling for module repos, and the local `verify-go-version.sh` helper.

Risks: no `set -e` is present, so failures rely on command exit propagation from the last executed command in each branch. Repositories with both files prefer dep. Repositories with neither file silently do nothing.

Test signals: no direct tests; resulting `go mod tidy`, `go mod vendor`, or `dep ensure` output plus downstream build/test are validation.
