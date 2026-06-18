# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_userfaultfd.sh

## Purpose
Wrapper entry point for the MM selftest `userfaultfd` category.

## Important APIs, types, and functions
The script invokes `./run_vmtests.sh -t userfaultfd`.

## Control flow
Delegates unit and stress tests for userfaultfd anon, hugetlb, and shmem modes to the runner.

## State and persistence behavior
No wrapper state. Delegated tests create mappings and userfaultfd descriptors.

## Dependencies and integration points
Requires userfaultfd kernel support, permission/sysctl configuration, and runner-built binaries.

## Risks and edge cases
Userfaultfd is often restricted for unprivileged users, causing skips or failures in delegated tests.

## Test signals
Successful completion of the `userfaultfd` runner target.
