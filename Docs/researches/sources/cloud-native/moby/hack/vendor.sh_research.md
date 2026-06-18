# sources/cloud-native/moby/hack/vendor.sh

## Purpose
Wrapper for tidying, vendoring, and managing local replace rules across Moby modules.

## Important APIs and Types
Defines `tidy`, `vendor`, `replace`, `dropreplace`, and `help`. Module sets are `api`, `client`, root, and `man` for vendoring.

## Control Flow, State, and Persistence
`tidy` runs `go mod tidy` in all modules. `vendor` runs `go mod vendor` in selected modules. `replace` adds root and client replace rules for local `api` and `client`. `dropreplace` resolves a git ref, drops replace rules, requires api/client modules at that ref, tidies, and vendors. The case statement dispatches subcommands, defaulting to tidy plus vendor.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Go modules, git remotes, and module layout. It mutates `go.mod`, `go.sum`, and `vendor/`. Risks include missing `$2` under `set -u`-like assumptions if changed, ref resolution surprises, and large vendored diffs. Validation scripts and clean module builds are the signals.
