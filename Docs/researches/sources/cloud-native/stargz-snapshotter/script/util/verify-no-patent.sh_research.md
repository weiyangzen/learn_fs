<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/util/verify-no-patent.sh -->
# sources/cloud-native/stargz-snapshotter/script/util/verify-no-patent.sh

## Purpose
Verifies release binaries do not include HashiCorp `golang-lru`'s patented `NewARC` symbol. It is a licensing/supply-chain guard copied and adapted from nerdctl.

## Important APIs, Types, And Functions
- Computes `CONTEXT` and `REPO` relative to the script location.
- Runs `make` with `GO_BUILD_LDFLAGS=""` so symbols remain visible.
- Iterates over `containerd-stargz-grpc`, `ctr-remote`, and `stargz-store`.
- Uses `go tool nm`, `grep -w -F main.main`, and `grep -w NewARC`.

## Control Flow
The script enables `set -eux -o pipefail`, builds the repository, emits one `.sym` file per binary, validates the symbol dump by requiring `main.main`, and fails if `NewARC` is present.

## State And Persistence
Writes symbol dump files under `out/*.sym` and rebuilds binaries under `out/` via the project `Makefile`. It does not remove these artifacts.

## Dependencies And Integration Points
Depends on Go tooling, `make`, shell utilities, and the project binary names. It is intended for CI or release verification after dependency changes.

## Risks And Edge Cases
The guard only checks linked symbols in the selected binaries. Build failures, stripped symbols, renamed outputs, or non-main artifacts can make the check fail or miss an affected path. Emptying `GO_BUILD_LDFLAGS` intentionally changes build flags for observability.

## Test Signals
Passing output includes `main.main` in each symbol file, no `NewARC` match, and a final `OK`. Failure signals include corrupt symbol dumps or any matching `NewARC` symbol.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/script/util/verify-no-patent.sh -->
