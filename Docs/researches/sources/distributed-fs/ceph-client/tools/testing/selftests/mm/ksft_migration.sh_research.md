# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_migration.sh

## Purpose
Wrapper entry point for the MM selftest `migration` category.

## Important APIs, types, and functions
It delegates with `./run_vmtests.sh -t migration`.

## Control flow
No local logic beyond runner invocation.

## State and persistence behavior
No wrapper state; underlying migration tests may move pages across nodes or memory types.

## Dependencies and integration points
Requires runner and migration-related test binaries/configuration.

## Risks and edge cases
NUMA and memory-hotplug capabilities can influence delegated behavior.

## Test signals
Pass/fail follows the `migration` target.
