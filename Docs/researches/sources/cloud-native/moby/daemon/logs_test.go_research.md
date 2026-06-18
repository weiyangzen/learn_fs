# sources/cloud-native/moby/daemon/logs_test.go

## Purpose
This file tests one regression path in daemon log configuration merging.

## Important APIs, Types, And Functions
`TestMergeAndVerifyLogConfigNilConfig` constructs a daemon with default `json-file` log config and calls `mergeAndVerifyLogConfig`.

## Control Flow
The test passes a `LogConfig` with the default type but nil `Config` map, expecting the method to allocate/merge defaults and validate successfully.

## State, Persistence, And Dependencies
No persistent state. It mutates the local `cfg` and uses Docker container API types.

## Integration Points
This protects container create/update paths where the caller supplies a log driver type but omits an option map.

## Risks And Edge Cases
The test is narrow; it does not inspect the final map contents or cover non-default drivers, invalid options, or logcache-specific defaults.

## Test Signals
Passing the test proves `mergeAndVerifyLogConfig` no longer panics or errors for nil `Config` when daemon defaults contain options.
