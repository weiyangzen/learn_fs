# sources/cloud-native/containerd/internal/cri/server/runtime_config.go

## Purpose

This file implements the CRI `RuntimeConfig` RPC wrapper.

## Important APIs, Types, and Functions

`(*criService).RuntimeConfig` returns a `runtime.RuntimeConfigResponse` whose `Linux` field is supplied by the platform-specific `getLinuxRuntimeConfig`.

## Control Flow

The function allocates the response and delegates all platform logic. It ignores the request fields because the CRI request has no options used here.

## State and Persistence Behavior

No state is mutated. It reads service configuration indirectly through the platform helper.

## Dependencies and Integration Points

It integrates with kubelet's CRI runtime config query and Linux/non-Linux build-tag implementations.

## Risks and Test Signals

The wrapper is simple; meaningful risk lies in platform helper accuracy. Linux tests call this API to verify cgroup driver selection.
