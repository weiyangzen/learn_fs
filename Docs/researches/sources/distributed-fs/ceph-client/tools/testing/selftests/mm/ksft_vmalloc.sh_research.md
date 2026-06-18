# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_vmalloc.sh

## Purpose
Wrapper entry point for the MM selftest `vmalloc` category.

## Important APIs, types, and functions
The script invokes `./run_vmtests.sh -t vmalloc`.

## Control flow
Delegates vmalloc smoke testing to the runner, which runs `test_vmalloc.sh smoke` for this category.

## State and persistence behavior
No wrapper state; delegated tests exercise kernel vmalloc behavior.

## Dependencies and integration points
Requires runner and vmalloc test script/binaries.

## Risks and edge cases
Kernel module/configuration requirements belong to the underlying vmalloc tests.

## Test signals
The wrapper passes when the `vmalloc` category passes.
