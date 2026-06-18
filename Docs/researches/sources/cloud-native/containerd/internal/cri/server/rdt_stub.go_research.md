# sources/cloud-native/containerd/internal/cri/server/rdt_stub.go

## Purpose

This `no_rdt` build-tag file disables RDT class selection while preserving the CRI service method set.

## Important APIs, Types, and Functions

`(*criService).rdtClassFromAnnotations` ignores all inputs and returns an empty class with nil error.

## Control Flow

The method is a direct no-op.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It integrates through build tags with container creation code that always calls the method regardless of RDT build support.

## Risks and Test Signals

The risk is silent loss of requested RDT annotations in `no_rdt` builds. Compile tests and build-tag-specific container creation tests are the relevant signals.
