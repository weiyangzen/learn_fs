<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-golint -->
# sources/control-plane/juicefs-csi-driver/hack/verify-golint

## Purpose
Go lint verifier that ensures `golangci-lint` exists and runs it across the repository.

## Important APIs, Types, and Resources
Checks `which golangci-lint`; if absent, installs `github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.11.4` into `$(go env GOPATH)/bin` using current `GOTOOLCHAIN`, then executes `golangci-lint run`.

## Control Flow
The script bootstraps the linter if needed, prepends GOPATH/bin to PATH, and runs the configured lint suite. It exits nonzero on lint findings or install failures.

## State and Persistence
May persist a downloaded linter binary in GOPATH/bin and module/cache downloads. It does not modify repository source.

## Dependencies and Integration Points
Depends on Bash, Go, network/module proxy access for install, golangci-lint configuration, and PATH. Integrated into `verify-all`.

## Risks
Risks include network-dependent CI, tool version changes relative to config, GOTOOLCHAIN compatibility, and installing tools during verification rather than using pinned CI images.

## Test Signals
Run in a clean environment, verify install path and lint results, and pin/cache the linter in CI for reproducibility.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-golint -->
