# Research: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy.go

Purpose: implements parsing and defaulting for daemon garbage-collection thresholds and policy rules. It translates human TOML values into durations and byte/percentage disk-space controls.

Important APIs and flow: `Duration.UnmarshalText` accepts Go duration strings or integer seconds. `DiskSpace.UnmarshalText` accepts percentages or Docker unit strings. `DefaultGCPolicy` preserves deprecated `gckeepstorage` compatibility, detects default caps when unset, and returns four ordered policies: quick cleanup of reproducible sources/cache mounts, old-data cleanup, unshared cache cap, and all-data cap. `DetectDefaultGCCap` computes reserve/max/free settings from platform constants. `DiskSpace.AsBytes` converts bytes or percentages against disk stats, with `defaultCap` fallback when disk total is unknown. `GCConfig.IsUnset` checks modern threshold fields.

State and dependencies: no persistence, but outputs feed worker GC policies that later delete cache. Depends on docker/go-units, disk stats, platform constants from OS-specific files, and TOML text unmarshaling.

Risks and test signals: percentage rounding and deprecated field fallback affect data-retention behavior. `gcpolicy_test.go` verifies the first default policy filter matches only intended cache record types, but threshold parsing itself is mostly covered through config load tests.
