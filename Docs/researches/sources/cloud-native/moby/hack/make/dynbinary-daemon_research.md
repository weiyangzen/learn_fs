# sources/cloud-native/moby/hack/make/dynbinary-daemon

## Purpose
Builds a dynamically linked `dockerd` daemon binary.

## Important APIs and Types
Daemon-specific wrapper for `.binary`/dynamic build settings.

## Control Flow, State, and Persistence
Compiles `dockerd` into a dynamic daemon bundle, preserving version metadata from `make.sh`.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on system libraries such as libsystemd when journald tags are enabled. Risks include missing runtime libraries in target images and mismatch with static daemon behavior. Daemon startup in test bundles is the validation signal.
