# sources/distributed-fs/ceph-client/scripts/kconfig/tests/no_write_if_dep_unmet/config

## Purpose
This initial config enables `A` for the no-write-if-dependency-unmet test.

## Important APIs, Types, and Functions
It contains `CONFIG_A=y`.

## Control Flow
The paired test starts from this state and then answers `n` in oldaskconfig.

## State and Persistence
Copied as temporary `.config` by the test runner.

## Dependencies and Integration Points
Used by the local pytest module only.

## Risks and Edge Cases
Minimal fixture; any added choice member state would change the test intent.

## Test Signals
Pass depends on this fragment making the choice initially visible.
