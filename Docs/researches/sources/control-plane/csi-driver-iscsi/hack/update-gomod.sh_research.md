## sources/control-plane/csi-driver-iscsi/hack/update-gomod.sh

Purpose: updates Kubernetes staging module replace directives to match a supplied Kubernetes version.

Control flow strips a leading `v` from the argument, fetches the target Kubernetes `go.mod`, extracts staging `k8s.io/*` modules, downloads each `@kubernetes-$VERSION` module, parses its resolved version, and writes a `replace` directive to go.mod.

State is go.mod and module cache. Dependencies are curl, sed, Go modules, and Kubernetes release conventions. Risks include no `go mod tidy/vendor`, brittle parsing, unquoted echo/variables, and partial updates after a network failure. Test signal is follow-up module verification and build.
