# sources/cloud-native/containerd/defaults/defaults.go

## Purpose
This file defines platform-independent default constants for containerd.

## Important APIs, Types, and Functions
Constants include default gRPC send/receive message sizes, namespace label keys for runtime/snapshotter/sandboxer defaults, and `DefaultSandboxer`.

## Control Flow
There is no executable control flow.

## State and Persistence
No state is persisted. Constants guide client/server configuration and namespace-label lookup.

## Dependencies and Integration Points
Used by client startup, integration tests, namespace default selection, and server configuration.

## Risks
Changing label keys or message limits is API/configuration visible and can break existing deployments.

## Test Signals
Integration client tests use default snapshotter/runtime labels and message behavior indirectly.
