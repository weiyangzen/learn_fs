# sources/distributed-fs/juicefs/pkg/meta/utils_test.go

## Purpose
`utils_test.go` tests metadata utility behavior for atime update policy and transaction method-name discovery.

## Important APIs, Types, and Functions
Tests are `TestRelatimeNeedUpdate`, `TestAtimeNeedsUpdate`, and `Test_getCallerName`.

## Control Flow and State
`TestRelatimeNeedUpdate` checks that relatime updates when atime is older than 24 hours, older than ctime, older than mtime, and not when timestamps match. `TestAtimeNeedsUpdate` exercises `NoAtime`, `RelAtime`, and `StrictAtime`, including strict mode's greater-than-one-second threshold. `Test_getCallerName` verifies explicit context override and stack-derived caller name.

## State and Persistence Behavior
The tests use in-memory `Attr` and `baseMeta` structs only. No metadata backend is touched.

## Dependencies and Integration Points
They cover utility functions consumed by readlink/atime update paths, transaction logging/metrics, and user-facing metadata behavior.

## Risks and Test Signals
Passing tests signal correct core time-policy logic, but they do not cover nanosecond boundary combinations, timezone irrelevance, or caller-name behavior under deeper anonymous stack frames beyond the simple closure case.
