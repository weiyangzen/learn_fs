# sources/control-plane/external-snapshotter/release-tools/go-get-kubernetes.sh

Purpose: updates Go module dependencies that come from `kubernetes/kubernetes` staging modules to a target Kubernetes version, adding necessary `replace` directives to avoid fake `v0.0.0` module revisions.

Important variables/functions: option `-p` for pruning unused replaces, `help`, `die`, target version argument, fetched Kubernetes `go.mod`, staging module extraction, `go mod edit -replace/-dropreplace`, package discovery via `go list`, and final `go get`.

Control flow: fetches upstream Kubernetes go.mod for `v<version>`, extracts staging modules, downloads each `kubernetes-<version>` module to discover concrete versions, writes replace directives, optionally prunes unused modules, lists k8s.io packages in the current module, maps packages to staging modules with replaces, and runs `go get` for the selected package versions.

State and persistence: mutates the current repo's `go.mod` and indirectly `go.sum`; network downloads populate module cache.

Dependencies and integration: depends on curl, sed, grep, Go modules, network access to GitHub/module proxy, and Kubernetes staging version conventions. Used by broader release-tools update scripts.

Risks and test signals: risks include remote go.mod parsing drift, command failure under partially broken modules, package-vs-module mapping edge cases, and unquoted dependency expansion. Success signal is `SUCCESS` plus clean `go mod tidy`/build in the caller.
