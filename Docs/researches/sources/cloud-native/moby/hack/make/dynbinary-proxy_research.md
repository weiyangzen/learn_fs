# sources/cloud-native/moby/hack/make/dynbinary-proxy

## Purpose
Builds a dynamically linked `docker-proxy` binary.

## Important APIs and Types
Proxy-specific dynamic wrapper around shared binary helpers.

## Control Flow, State, and Persistence
Compiles proxy output into the dynamic proxy bundle destination.

## Dependencies, Integration Points, Risks, and Test Signals
Used by networking tests when dynamic artifacts are preferred. Risks include missing runtime libraries and proxy not found by daemon/test PATH. Libnetwork and integration networking tests validate it.
