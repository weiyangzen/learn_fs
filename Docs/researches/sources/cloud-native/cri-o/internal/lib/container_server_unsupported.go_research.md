# sources/cloud-native/cri-o/internal/lib/container_server_unsupported.go

## Purpose
Provides non-Linux no-op platform hooks for sandbox add/remove bookkeeping.

## Important APIs, Types, And Functions
- `addSandboxPlatform(sb *sandbox.Sandbox) error` returns nil.
- `removeSandboxPlatform(sb *sandbox.Sandbox) error` returns nil.

## Control Flow
Build-tagged with `//go:build !linux`. Both functions ignore input and succeed.

## State And Persistence
No state is changed. There is no SELinux process-level reference counting on these platforms.

## Dependencies And Integration Points
Keeps `ContainerServer.AddSandbox` and `RemoveSandbox` buildable off Linux. FreeBSD still has its own `configNsPath` but uses these no-op platform hooks.

## Risks And Edge Cases
Non-Linux platforms do not get SELinux label accounting through this path. This is intentional but differs from Linux cleanup semantics.

## Test Signals
No direct tests in this subset; build-tag compilation is the signal.
