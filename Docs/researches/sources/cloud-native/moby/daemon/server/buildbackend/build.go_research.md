# sources/cloud-native/moby/daemon/server/buildbackend/build.go

## Purpose
Defines build-backend option and data contracts for build execution, build cache disk usage/prune, image resolution, progress streaming, and build outputs.

## Important APIs, Types, And Functions
Important definitions include `DiskUsageOptions`, `CachePruneOptions`, `PullOption` constants, `ProgressWriter`, `AuxEmitter`, `BuildConfig`, `BuildOptions`, `BuildOutput`, and `GetImageAndLayerOptions`.

## Control Flow
Type definitions and enum constants only. Routers and build manager implementations supply execution flow.

## State And Persistence
These structs carry request state such as build context streams, tags, auth configs, resource limits, cache settings, BuildKit outputs, session IDs, and platform selection. Persistence occurs in builder/image layers, not here.

## Dependencies And Integration Points
Imports Docker API build/container/registry types, daemon filters, and OCI platform specs. It bridges API build routes, legacy builder, BuildKit, image pull policy, cache prune, and progress output.

## Risks And Edge Cases
`BuildArgs` uses `map[string]*string` to distinguish omitted from empty values. Pull policy controls network access. Resource fields mirror container host config and need version-compatible parsing upstream.

## Test Signals
Build route and builder integration tests validate these contracts; this file has no direct tests.
