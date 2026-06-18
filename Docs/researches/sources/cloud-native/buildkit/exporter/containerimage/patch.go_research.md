# Research: sources/cloud-native/buildkit/exporter/containerimage/patch.go

## Purpose
Default image layer patch hook.

## Important APIs, Types, and Functions
Non-Nydus `patchImageLayers` no-op.

## Control Flow
Writer calls it before config/manifest commit and receives unchanged remote/history.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on cache/session/solver/OCI types. Build-tag extension point for Nydus.

## Risks and Edge Cases
Low default risk; behavior changes under Nydus tags.

## Test Signals
Build-tag coverage.
