## sources/control-plane/csi-driver-iscsi/hack/verify-govet.sh

Purpose: runs `go vet` over all non-vendor packages.

Control flow executes `go vet $(go list ./... | grep -v vendor)` under strict bash. State is read-only except module cache.

Dependencies are Go tooling and successful package listing. Risks include shell word splitting, grep-based vendor exclusion, and failure if `go list` includes packages requiring platform-specific host tools. Test signal is `verify-all.sh`.
