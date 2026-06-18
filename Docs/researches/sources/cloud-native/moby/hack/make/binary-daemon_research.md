# sources/cloud-native/moby/hack/make/binary-daemon

## Purpose
Bundle target for building the `dockerd` daemon binary.

## Important APIs and Types
Sets daemon-specific binary name/package variables and sources shared binary generation helpers.

## Control Flow, State, and Persistence
Builds `dockerd` with static build tags/ldflags from `make.sh`, writing to the daemon binary bundle destination.

## Dependencies, Integration Points, Risks, and Test Signals
Required by integration daemon startup, install-binary, and release artifacts. Risks include missing daemon build tags such as journald/static settings, incorrect embedded version data, and cross-platform incompatibility. Integration suites that start `dockerd` validate the output.
