# sources/control-plane/mayastor/io-engine/src/core/fault_injection/mod.rs

## Purpose
Defines and re-exports the feature-gated fault-injection subsystem. It supplies common enums, errors, and public API shims used by test endpoints and hot I/O paths.

## Important APIs, Types, and Functions
- Re-exports `FaultMethod`, `InjectIoCtx`, `InjectIoDevice`, `Injection`, `InjectionBuilder`, `InjectionState`, and API functions.
- `FaultDomain` selects `NexusChild`, `BlockDevice`, or `BdevIo`.
- `FaultIoOperation` selects read, write, or both.
- `FaultIoStage` selects submission or completion.
- `FaultInjectionError` reports disabled injections, URI/parameter errors, missing devices, invalid injection combinations, and bad durations.

## Control Flow and State
This module has no runtime flow beyond type definitions and feature gating. The module tree compiles only with `fault-injection`, so any unconditional imports outside matching cfg must be guarded by build configuration.

## Dependencies and Integration Points
Depends on `snafu`, `url::ParseError`, and standard display/debug traits. The public API is re-exported through `core/mod.rs` as `pub mod fault_injection`, and consumers include bdev/nexus I/O code and test gRPC.

## Risks and Test Signals
Because the module is feature gated, CI needs coverage for builds with and without `fault-injection`. Error variants are part of user-visible test API behavior, so URI validation should remain stable. Tests should cover display strings for domains/stages/ops and Snafu messages consumed by gRPC conversion.
