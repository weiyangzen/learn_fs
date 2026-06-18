# sources/control-plane/csi-lib-utils/release-tools/go-get-kubernetes.sh

## Purpose

This script updates Kubernetes-related Go module dependencies in CSI repositories to a target Kubernetes version or branch. It is used directly and by batch update scripts.

## Important Behavior

The script accepts `-p` to prune unused Kubernetes staging module replacements and `-h` for help, then requires one positional Kubernetes version such as `1.34.0`. It downloads the target Kubernetes `go.mod` from GitHub, extracts `k8s.io/* => ./staging/src/k8s.io/*` replacements, and for each staging module resolves the corresponding `kubernetes-<version>` module version. It writes `go mod edit -replace=<module>=<module>@<resolved-version>` entries, optionally dropping unused replacements when `-p` is enabled. It then obtains imported Kubernetes packages with `go list all`, falling back to dependency listing for `./...`, filters packages whose modules are covered by the replacements, and runs one `go get` over those packages with `@kubernetes-<version>` or `@v<version>` for `k8s.io/kubernetes/...`.

## State, Dependencies, and Integration

It mutates `go.mod` and `go.sum`; vendoring is handled by callers such as `go-modules-update.sh`. It depends on bash, curl, sed, Go modules, network access to `raw.githubusercontent.com` and Go module download endpoints, and a local Go module checkout. It integrates with manual and scripted CSI dependency update workflows.

## Risks and Test Signals

Dependency updates can introduce API incompatibilities that the script cannot resolve. The initial staging-module extraction is tied to Kubernetes `go.mod` formatting. The `go list all` fallback can still fail if the repository cannot load packages before dependency updates. Test signals are successful replacement edits, successful final `go get`, resulting module diffs, and downstream tidy/vendor/test runs in caller scripts.
