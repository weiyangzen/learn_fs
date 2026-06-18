# Research: sources/cloud-native/buildkit/executor/resources/monitor_nolinux.go

## Purpose
Non-Linux resource monitor stub.

## Important APIs, Types, and Functions
Build-tag fallback returning unsupported/no-op monitor behavior.

## Control Flow
No real sampling occurs.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on build tags and shared resource API. Keeps package portable.

## Risks and Edge Cases
Consumers must tolerate missing resource samples.

## Test Signals
Cross-platform compilation.
