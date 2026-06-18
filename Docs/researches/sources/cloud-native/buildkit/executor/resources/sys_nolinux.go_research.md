# Research: sources/cloud-native/buildkit/executor/resources/sys_nolinux.go

## Purpose
Non-Linux system sampler stub.

## Important APIs, Types, and Functions
Build-tagged `newSysSampler` fallback.

## Control Flow
No system sampling occurs.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on build tags. Portability for resource package.

## Risks and Edge Cases
Consumers must tolerate absent host samples.

## Test Signals
Cross-platform compilation.
