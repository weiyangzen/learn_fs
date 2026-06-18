# sources/control-plane/csi-lib-utils/release-tools/update-vendor.sh

## Purpose

This helper updates dependency vendoring for repositories using either legacy `dep` or Go modules.

## Important Behavior

If `Gopkg.toml` exists, it prints that the repo uses dep and runs `dep ensure`. If `go.mod` exists, it verifies the Go version through `release-tools/verify-go-version.sh "go"`, then runs `GO111MODULE=on go mod tidy` and `GO111MODULE=on go mod vendor`.

## State, Dependencies, and Integration

The script mutates dependency lock/module/vendor files. It depends on `dep` for legacy repos, Go modules for modern repos, and `release-tools/verify-go-version.sh`. It integrates with Makefile or manual maintenance flows that want a single vendoring command.

## Risks and Test Signals

It has no explicit `set -e`, but failing commands in simple scripts may still need caller handling. It silently does nothing when neither `Gopkg.toml` nor `go.mod` exists. Test signals are command exit status and resulting git diffs for module/vendor files.
