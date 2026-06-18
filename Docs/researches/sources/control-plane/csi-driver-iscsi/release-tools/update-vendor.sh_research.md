# sources/control-plane/csi-driver-iscsi/release-tools/update-vendor.sh

Purpose: updates vendored dependencies for repos using either dep or Go modules.

Important APIs and types: no functions; top-level shell checks for `Gopkg.toml` or `go.mod`.

Control flow: if `Gopkg.toml` exists, runs `dep ensure`. If `go.mod` exists, runs `release-tools/verify-go-version.sh go`, then `go mod tidy` and `go mod vendor` with `GO111MODULE=on`.

State and persistence: mutates dependency metadata and `vendor` contents.

Dependencies and integration: depends on dep, Go modules, and release-tools Go-version policy.

Risks: no strict shell options are set, so failures can be less controlled than verifier scripts. It assumes `release-tools/verify-go-version.sh` is reachable from repo root.

Test signals: clean git diff after expected dependency changes and passing `verify-vendor.sh`.
