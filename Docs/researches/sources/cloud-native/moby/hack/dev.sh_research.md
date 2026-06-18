# sources/cloud-native/moby/hack/dev.sh

## Purpose
Developer loop that repeatedly builds, installs, and runs `dockerd` in debug mode.

## Important APIs and Types
No functions. It invokes `./hack/make.sh binary`, `KEEPBUNDLE=1 ./hack/make.sh install-binary`, and `dockerd --debug`.

## Control Flow, State, and Persistence
An infinite loop rebuilds the daemon binary. Build failures sleep for five seconds and retry. Install failures skip to the next loop. `dockerd` exits are ignored, followed by a short sleep.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on the repository build container/tooling and a runnable daemon environment. It persists installed binaries through `hack/make.sh install-binary`. Risks include accidental long-running daemon loops, stale bundles with `KEEPBUNDLE`, and masking daemon crash exits. Validation is manual developer use rather than automated tests.
