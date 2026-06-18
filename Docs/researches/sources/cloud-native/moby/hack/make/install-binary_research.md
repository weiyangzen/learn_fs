# sources/cloud-native/moby/hack/make/install-binary

## Purpose
Installs built Docker binaries from bundle output into the configured destination.

## Important APIs and Types
Sources `.install` and uses binary bundle paths plus install prefix variables.

## Control Flow, State, and Persistence
Ensures the binary bundle is present or built, creates install directories, and installs binaries. It mutates the local/container filesystem.

## Dependencies, Integration Points, Risks, and Test Signals
Used by `hack/dev.sh` and CI images. Risks include stale binary installation, permission errors, and PATH confusion when multiple bundles exist. Post-install `dockerd`/`docker` invocation validates it.
