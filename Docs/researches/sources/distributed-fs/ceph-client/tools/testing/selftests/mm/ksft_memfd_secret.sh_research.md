# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_memfd_secret.sh

## Purpose
Wrapper entry point for the MM selftest `memfd_secret` category.

## Important APIs, types, and functions
The script invokes `./run_vmtests.sh -t memfd_secret`.

## Control flow
All secret-memory test setup and execution is delegated.

## State and persistence behavior
The wrapper has no state. Underlying tests may create secretmem file descriptors and mappings.

## Dependencies and integration points
Requires kernel `memfd_secret` support and runner-managed binaries.

## Risks and edge cases
Feature absence should be represented by delegated skips or failures.

## Test signals
The wrapper passes when `run_vmtests.sh -t memfd_secret` passes.
