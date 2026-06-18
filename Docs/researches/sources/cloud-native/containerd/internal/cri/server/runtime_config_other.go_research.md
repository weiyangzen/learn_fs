# sources/cloud-native/containerd/internal/cri/server/runtime_config_other.go

## Purpose

This non-Linux file disables Linux runtime configuration reporting on other platforms.

## Important APIs, Types, and Functions

`getLinuxRuntimeConfig` returns nil.

## Control Flow

The method is a direct stub.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It satisfies the platform helper used by `RuntimeConfig` under `!linux`.

## Risks and Test Signals

Non-Linux clients receive no Linux runtime config, which matches the platform. Compile and platform CRI smoke tests are sufficient.
