# sources/cloud-native/moby/hack/make/install-proxy

## Purpose
Installs `docker-proxy` from bundle output.

## Important APIs and Types
Thin wrapper around `.install` for the proxy artifact.

## Control Flow, State, and Persistence
Copies the built proxy binary into the configured install prefix.

## Dependencies, Integration Points, Risks, and Test Signals
Used by unit/integration tests that require userland proxy availability. Risks are missing or stale proxy binaries and insufficient install permissions. Network and libnetwork tests validate it.
