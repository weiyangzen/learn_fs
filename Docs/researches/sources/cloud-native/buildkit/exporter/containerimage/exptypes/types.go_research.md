# Research: sources/cloud-native/buildkit/exporter/containerimage/exptypes/types.go

## Purpose
Container image exporter internal data types.

## Important APIs, Types, and Functions
Known metadata keys, `Platforms`, `Platform`, `InlineCacheEntry`, `InlineCache`.

## Control Flow
Frontends/solver populate these and writer/exporter consume them.

## State and Persistence
Data contract only.

## Dependencies and Integration Points
Depends on context, solver result generics, OCI platforms. Connects frontend metadata to image export internals.

## Risks and Edge Cases
Changes affect cache/config/base-image and platform compatibility.

## Test Signals
Integration coverage.
