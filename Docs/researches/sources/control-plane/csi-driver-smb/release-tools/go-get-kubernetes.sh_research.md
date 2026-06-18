<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/go-get-kubernetes.sh -->
# sources/control-plane/csi-driver-smb/release-tools/go-get-kubernetes.sh

Purpose: Updates Go module dependencies that originate from `kubernetes/kubernetes` to a specific Kubernetes release, including required staging-module replace directives.

Important behavior: Accepts `-p` to prune unused replace directives and `-h` for help, then requires one Kubernetes `x.y.z` version. It fetches Kubernetes `go.mod`, extracts staging modules, maps each module to its `kubernetes-<version>` pseudo release, writes `go mod edit -replace` directives, discovers used `k8s.io` packages with `go list`, then runs `go get` on package versions.

Control flow: The script first sets/updates replacement modules, optionally drops unused ones, then gathers packages with `go list all` or falls back to dependency listing for `./...`.

State and persistence behavior: Mutates `go.mod` and module cache, and can change `go.sum` when users run tidy afterward.

Dependencies and integration points: Used by module-update scripts and `update-vendor.sh`. Depends on curl, Go modules, Kubernetes staging module versioning, and network access to GitHub/module proxies.

Risks: Package/module parsing is shell/sed-based and can miss unusual package layouts. The script can leave `go.mod` partly edited if later `go get` fails. It warns about complex Kubernetes fake versions but does not run tidy/vendor itself.

Test signals: No direct tests; success is validated by subsequent `go mod tidy`, vendor checks, and repo test suites.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/go-get-kubernetes.sh -->
