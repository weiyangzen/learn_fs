# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_cow.sh

## Purpose
Wrapper entry point for the MM selftest `cow` category.

## Important APIs, types, and functions
The entire script is a POSIX shell wrapper with `set -e` semantics through `#!/bin/sh -e`, calling `./run_vmtests.sh -t cow`.

## Control flow
Execution immediately delegates to the VM test runner's copy-on-write category.

## State and persistence behavior
No wrapper-owned state exists.

## Dependencies and integration points
Requires `run_vmtests.sh` and the COW test binaries/configuration it selects.

## Risks and edge cases
No local cleanup exists; failures or skips are governed by the underlying runner.

## Test signals
The wrapper's exit status mirrors the `cow` target.
