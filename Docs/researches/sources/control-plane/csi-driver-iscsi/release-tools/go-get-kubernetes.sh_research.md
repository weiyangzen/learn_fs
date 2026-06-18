# sources/control-plane/csi-driver-iscsi/release-tools/go-get-kubernetes.sh

Purpose: updates Kubernetes staging-module dependencies in a Go module to a target Kubernetes version while maintaining necessary replace directives.

Important APIs and types: CLI accepts optional `-p` prune and a required Kubernetes version `x.y.z`. Internal helpers are `help` and `die`.

Control flow: downloads the target `kubernetes/kubernetes` `go.mod`, extracts staging module replaces, optionally prunes unused replaces, resolves each staging module version via `go mod download <mod>@kubernetes-<version>`, writes `go mod edit -replace`, obtains imported packages through `go list`, maps packages to replaced modules, and runs `go get` on package-level dependencies at the target version.

State and persistence: mutates `go.mod` and later `go.sum` via Go tooling. It reads module graph and package dependency state from the current repository.

Dependencies and integration: depends on curl, sed, grep, Go modules, network access to GitHub and module proxies, and Kubernetes staging module versioning conventions.

Risks: package discovery fallback still may fail for broken repos. It intentionally expands shell word splitting for package lists. Network or proxy flakiness can leave partial `go.mod` edits. The help text says optional `-p`, but usage line is confusing.

Test signals: `SUCCESS`, clean `go mod tidy`, and downstream build/test/vendor checks.
