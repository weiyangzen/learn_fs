<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_unsupported.go -->
# sources/cloud-native/cri-o/server/container_create_unsupported.go

## Purpose

This build-tagged file handles platforms that are neither Linux nor FreeBSD by making sandbox container creation explicitly unsupported.

## Important APIs, Types, and Functions

`createSandboxContainer(ctx, ctr, sb)` returns `(nil, fmt.Errorf("not implemented yet"))` for `!linux && !freebsd` builds.

## Control Flow

The shared `CreateContainer` path will reach this method after early validation and name reservation. The method immediately fails, causing the outer cleanup chain to run.

## State and Persistence Behavior

No direct state is written here. Any state already staged by the caller should be cleaned by `CreateContainer` resource cleaners.

## Dependencies and Integration Points

It keeps the server package buildable on unsupported platforms by satisfying the method required by the common create path.

## Risks and Edge Cases

The generic error is intentionally blunt and not CRI-typed. If unsupported platforms should expose more precise API behavior, this would need better error mapping.

## Test Signals

No direct tests are included; build-tag compilation is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_unsupported.go -->
