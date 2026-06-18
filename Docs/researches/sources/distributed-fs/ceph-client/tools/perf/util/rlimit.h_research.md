# sources/distributed-fs/ceph-client/tools/perf/util/rlimit.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/rlimit.h` declares perf resource-limit helper APIs.

## Important APIs, Types, and Functions

`enum rlimit_action` has states `NO_CHANGE`, `SET_TO_MAX`, and `INCREASED_MAX` used by `rlimit__increase_nofile`. Declared functions are `rlimit__bump_memlock` and `rlimit__increase_nofile`.

## Control Flow

No runtime flow exists in the header. Callers maintain an `enum rlimit_action` value across retry attempts.

## State and Persistence Behavior

The only modeled state is the caller-owned nofile action enum. Actual process rlimit changes are performed by the implementation.

## Dependencies and Integration Points

The header is lightweight but uses `bool`, relying on include order or transitive includes to provide it in consumers.

## Risks and Edge Cases

Consumers should include a boolean definition before this header if not already present. The state enum represents a progression and should not be reset accidentally between retries.

## Test Signals

Compile coverage and `rlimit.c` behavioral tests validate this contract.
