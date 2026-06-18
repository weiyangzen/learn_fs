# sources/cloud-native/containerd/internal/cri/server/blockio_linux.go

## Purpose

This Linux server helper resolves the effective block I/O class for a container from CRI annotations and validates that blockio support is enabled before applying the class.

## Important APIs, Types, and Functions

`blockIOClassFromAnnotations(containerName, containerAnnotations, podAnnotations)` calls `blockio.ContainerClassFromAnnotations`, checks `blockio.IsEnabled`, optionally ignores disabled errors based on config, and returns the class name or error.

## Control Flow

If annotation parsing returns an error, it is propagated. If a class is requested while blockio is disabled, the method either clears the class and logs debug when configured to ignore, or returns an error refusing container creation. Empty class returns empty success.

## State and Persistence Behavior

It reads CRI service config and blockio global state. It does not mutate persisted state; the returned class is later converted to OCI Linux block IO settings.

## Dependencies and Integration Points

It depends on `pkg/blockio` and containerd logging. Linux container spec creation calls it before appending `oci.WithBlockIO`.

## Risks and Edge Cases

Ignoring disabled blockio can silently drop requested QoS. Refusing disabled blockio fails container creation based on annotations. Annotation precedence is delegated to the blockio package.

## Test Signals

Tests should cover no class, valid class with blockio enabled, parse errors, disabled blockio with ignore true, and disabled blockio with ignore false.
