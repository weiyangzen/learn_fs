# sources/cloud-native/moby/hack/validate/golangci-lint

## Purpose
Runs golangci-lint across all Go modules except `man`.

## Important APIs and Types
Uses `GOLANGCI_LINT_OPTS`, `DOCKER_BUILDTAGS`, `pkg-config libsystemd`, module discovery by `find go.mod`, and `.golangci.yml`.

## Control Flow, State, and Persistence
The script sets a default timeout, adds `journald` build tag when libsystemd is available, discovers module directories, then runs `golangci-lint run` in each module with shared config and build tags.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on golangci-lint, Go module layout, pkg-config, and shell arrays. Risks include platform-dependent tags, long runtime, lint config drift, and missing modules filtered by path. CI lint results validate it.
