# sources/cloud-native/moby/daemon/pkg/oci/caps/utils.go

## Purpose
This file normalizes, validates, enumerates, and tweaks Linux capabilities for container OCI specs.

## Important APIs, Types, And Functions
`GetAllCapabilities` returns current-environment capabilities. `NormalizeLegacyCapabilities` uppercases names, adds `CAP_`, validates against known/current capabilities, and accepts magic `ALL`. `TweakCapabilities` computes the final capability set from defaults, additions, drops, and privileged mode. `knownCapabilities` and globals `allCaps`/`knownCaps` are initialized by platform-specific `initCaps`.

## Control Flow
Normalization loops over requested capabilities, handles `ALL`, prefixes missing `CAP_`, rejects unknown names, and rejects known but unavailable names. Tweaking returns all capabilities for privileged containers, returns defaults when no changes are requested, otherwise normalizes add/drop lists and applies one of three rules: add all except drops, drop all and use adds, or remove drops from defaults then append adds.

## State, Persistence, And Dependencies
State is cached in package-level `allCaps` and `knownCaps`, initialized once by platform code. There is no persistence. Dependencies include slices/string helpers and errdefs invalid-parameter errors.

## Integration Points
Linux OCI spec generation calls `TweakCapabilities` before applying capabilities with containerd OCI helpers. API `CapAdd`/`CapDrop` compatibility relies on legacy normalization.

## Risks And Edge Cases
Duplicate capabilities are not de-duplicated in the default add-after-drop path. The `ALL` magic value in `CapDrop` causes output to be exactly normalized `CapAdd`, so callers must not pass `ALL` through to OCI. Environment-restricted capabilities produce invalid-parameter errors before runtime invocation.

## Test Signals
No direct tests in this subset; behavior depends on capability utility tests elsewhere and OCI integration.
