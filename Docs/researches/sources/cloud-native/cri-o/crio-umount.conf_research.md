# sources/cloud-native/cri-o/crio-umount.conf

## Purpose
tmpfiles/systemd-umount style configuration for unmounting CRI-O storage/run mounts during cleanup/shutdown.

## Important APIs, Types, and Functions
Contains path/action entries targeting CRI-O storage and runtime mount locations.

## Control Flow
Consumed by systemd-tmpfiles or distro packaging hook to perform unmount cleanup.

## State and Persistence
Mutates mount namespace/state by unmounting configured paths; no application state.

## Dependencies
Depends on systemd tmpfiles semantics and CRI-O path conventions.

## Integration Points
Complements crio-wipe/service packaging cleanup.

## Risks and Edge Cases
Unmounting active paths can disrupt running containers; path drift makes it ineffective.

## Test Signals
Packaging/install tests and shutdown cleanup validate it.
