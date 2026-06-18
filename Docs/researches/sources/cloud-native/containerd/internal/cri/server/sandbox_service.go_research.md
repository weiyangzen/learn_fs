# sources/cloud-native/containerd/internal/cri/server/sandbox_service.go

## Purpose

This file defines a small CRI-facing sandbox service facade over containerd sandbox controllers.

## Important APIs, Types, and Functions

`criSandboxService` stores sandbox controllers by sandboxer name and CRI config. Methods include `SandboxController`, `CreateSandbox`, `StartSandbox`, `WaitSandbox`, `SandboxStatus`, `SandboxPlatform`, `ShutdownSandbox`, `UpdateSandbox`, and `StopSandbox`.

## Control Flow

Each operation resolves the requested sandbox controller and delegates to it. `WaitSandbox` wraps a blocking controller `Wait` call in a goroutine and returns a buffered channel containing a containerd `ExitStatus`.

## State and Persistence Behavior

The facade itself persists no sandbox state. It delegates all mutations to controllers and returns wait results through channels.

## Dependencies and Integration Points

It integrates CRI service code with the generic `core/sandbox.Controller` interface and containerd exit status type.

## Risks and Test Signals

Risks include missing sandboxer names and goroutine lifetime tied to wait context. Sandbox run/recovery tests exercise the facade indirectly.
