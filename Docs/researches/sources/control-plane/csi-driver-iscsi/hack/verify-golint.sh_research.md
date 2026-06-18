## sources/control-plane/csi-driver-iscsi/hack/verify-golint.sh

Purpose: legacy lint verifier using golangci-lint with only the deprecated `golint` linter enabled.

Control flow installs golangci-lint v1.31.0 via remote install script if missing, updates PATH, then runs `golangci-lint run --no-config --enable=golint --disable=typecheck --deadline=10m`. State is a binary installed under GOPATH/bin when absent.

Dependencies are curl, Go env, golangci-lint, and network access. Risks include remote shell install, old linter version, deprecated flags/linter, typecheck disabled, and this script not being called by `verify-all.sh`. Test signal is manual invocation.
