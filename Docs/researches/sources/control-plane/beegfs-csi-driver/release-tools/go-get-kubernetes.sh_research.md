# sources/control-plane/beegfs-csi-driver/release-tools/go-get-kubernetes.sh

Purpose: Updates Go module dependencies that originate from `kubernetes/kubernetes` staging modules to a specific Kubernetes release version, adding necessary replace statements to avoid fake `v0.0.0` module revisions.

Important APIs/types/functions: Supports `-p` to prune unused replace statements and `-h` for help. Fetches Kubernetes `go.mod` for a supplied `x.y.z` version, extracts staging module names, applies `go mod edit -replace`, enumerates imported `k8s.io` packages, and runs `go get` with `@kubernetes-<version>` or `@v<version>` for `k8s.io/kubernetes/...`.

Control flow: Validates exactly one version argument, downloads upstream Kubernetes `go.mod`, builds the staging module list, optionally prunes unused replacements based on `go mod graph`, determines actual module versions via `go mod download -json`, edits replacements, gathers package imports with `go list all` or fallback dependency listing, filters packages whose modules have replace entries, and runs `go get` for those packages.

State and persistence: Mutates `go.mod` and potentially `go.sum` in the current repository. Downloads module metadata and upstream files. No commits.

Dependencies and integration points: Used by `go-modules-update.sh` and manually during dependency updates. Requires curl, sed, grep, Go modules, network access to GitHub and module proxy/source, and a Go module repository.

Risks: Parsing upstream `go.mod` with sed is sensitive to format changes. `go list all` can fail before replacements are complete, hence fallback logic. The script modifies module replacements broadly unless pruned. It does not update non-Kubernetes-staging `k8s.io` modules such as `klog` or `utils`.

Test signals: Success is indicated by `SUCCESS` after `go get`. Downstream validation usually requires `go mod tidy`, vendoring, and project tests.
