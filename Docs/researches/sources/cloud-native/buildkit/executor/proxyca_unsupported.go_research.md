# Research: sources/cloud-native/buildkit/executor/proxyca_unsupported.go

## Purpose
Unsupported-platform proxy CA stub.

## Important APIs, Types, and Functions
Build-tagged `InjectProxyCA` fallback.

## Control Flow
Compiles non-Linux executors without Linux bundle mutation.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on build tags. Portability for proxy-aware executor code.

## Risks and Edge Cases
Non-Linux proxy trust behavior may differ.

## Test Signals
Cross-platform compilation.
