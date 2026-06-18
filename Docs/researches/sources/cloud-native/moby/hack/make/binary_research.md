# sources/cloud-native/moby/hack/make/binary

## Purpose
Bundle target for building the primary Docker CLI/static binary set through shared helpers.

## Important APIs and Types
Thin wrapper around `.binary` with `BINARY_NAME`/package settings.

## Control Flow, State, and Persistence
Delegates common build setup to `.binary`, producing a bundle under `bundles/binary` or the active destination.

## Dependencies, Integration Points, Risks, and Test Signals
Called by `hack/make.sh binary` and developer loops. Risks are inherited from `.binary`: wrong package path, missing version generation, and stale output. Successful CLI binary execution and install bundle tests validate it.
