# sources/cloud-native/moby/hack/make/binary-proxy

## Purpose
Bundle target for building `docker-proxy`.

## Important APIs and Types
Thin wrapper setting proxy binary/package variables and sourcing `.binary`.

## Control Flow, State, and Persistence
Compiles the userland proxy binary into the active bundle destination.

## Dependencies, Integration Points, Risks, and Test Signals
Used when integration or libnetwork tests require `docker-proxy`. Risks include missing binary in PATH for bridge/network tests and build tag mismatches. `hack/test/unit` triggers proxy build/install for libnetwork bridge packages when needed.
