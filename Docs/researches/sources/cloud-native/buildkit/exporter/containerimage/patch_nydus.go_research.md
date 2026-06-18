# Research: sources/cloud-native/buildkit/exporter/containerimage/patch_nydus.go

## Purpose
Nydus-specific image layer patch hook.

## Important APIs, Types, and Functions
Build-tagged `patchImageLayers` for Nydus compression/export.

## Control Flow
Validates Nydus options and adjusts remote descriptors/history before manifest commit.

## State and Persistence
Returned remote/history carry state; content mutations are delegated.

## Dependencies and Integration Points
Depends on BuildKit Nydus compression, cache refs, solver remotes, sessions, OCI history. Integrates Nydus export into generic writer.

## Risks and Edge Cases
Wrong descriptor/history patching breaks pull/runtime behavior.

## Test Signals
Nydus integration tests needed.
