## sources/control-plane/csi-driver-iscsi/hack/update-dependencies.sh

Purpose: regenerates Go module pinning and vendor contents with explicit `require` and `replace` directives for all dependencies.

Control flow forces module mode, clears GOPATH/GOFLAGS, changes to repo root, creates temp workspace, defines optional vendor pruning, captures current require/replace JSON with `go mod edit -json` and jq, adds replace directives for versioned requirements, adds explicit indirect requires from `go list -m -json all`, pins unpinned modules, groups replace directives in go.mod with awk, runs `go mod tidy`, repeats pinning, and runs `go mod vendor`.

State is go.mod, go.sum, and vendor. Dependencies are Go modules, jq, awk, xargs, git, and network/module proxy. Risks include large invasive go.mod rewrites, xargs behavior with empty input, fragile awk regrouping, temp dir accumulation, and no tests before success. Test signal is subsequent `verify-gomod`, `verify-update`, and CI builds.
