# Research: sources/cloud-native/buildkit/executor/oci/spec_darwin.go

## Purpose
Darwin stubs for OCI spec helpers.

## Important APIs, Types, and Functions
No-op/unsupported implementations for mount/security/process/idmap/resource/CDI/tracing helpers.

## Control Flow
Allows common package compilation on Darwin while Linux-only features are absent.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on build tags and shared OCI types. Portability layer.

## Risks and Edge Cases
No-op behavior must not be mistaken for full runtime support.

## Test Signals
Cross-platform build signal.
