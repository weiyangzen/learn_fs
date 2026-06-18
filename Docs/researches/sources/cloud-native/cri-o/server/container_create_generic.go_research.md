<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_generic.go -->
# sources/cloud-native/cri-o/server/container_create_generic.go

## Purpose

This build-tagged file provides `createContainerPlatform` for `windows`, `darwin`, and `freebsd`, delegating directly to the configured runtime without Linux-specific bundle ownership preparation.

## Important APIs, Types, and Functions

The only function is `createContainerPlatform(ctx, container, cgroupParent, idMappings) error`. It accepts the same parameters as the Linux implementation but ignores ID mappings and simply calls `s.ContainerServer.Runtime().CreateContainer(ctx, container, cgroupParent, false)`.

## Control Flow

There is no local branching. The common `CreateContainer` path calls this after storage and in-memory container state are prepared; this platform implementation forwards the call to the runtime.

## State and Persistence Behavior

This file does not persist anything directly. Runtime-side state is created by the runtime implementation. Unlike Linux, it does not call `makeAccessible` on bundle or mount paths for user namespace root mappings.

## Dependencies and Integration Points

It integrates with the shared creation pipeline through the same method signature and depends on internal `oci.Container`, containers/storage `idtools` for API compatibility, and the CRI-O runtime abstraction.

## Risks and Edge Cases

The broad build tag includes FreeBSD even though `container_create_freebsd.go` supplies many other FreeBSD helpers. Any platform needing pre-runtime filesystem preparation must implement it here or split the build tags.

## Test Signals

No direct tests are present. Coverage comes only through platform builds and runtime integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_generic.go -->
