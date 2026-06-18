# sources/cloud-native/moby/hack/make/dynbinary

## Purpose
Bundle target for dynamically linked Docker binary artifacts.

## Important APIs and Types
Wrapper around shared binary logic with dynamic-build flags rather than static ldflags.

## Control Flow, State, and Persistence
Builds into the `dynbinary` bundle destination, relying on upstream environment to select dynamic linking behavior.

## Dependencies, Integration Points, Risks, and Test Signals
Used by default `hack/make.sh` bundles. Risks include runtime library availability and divergence from static binary behavior. CI build and integration runs using `dynbinary` validate it.
