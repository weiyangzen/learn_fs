# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_mock_selftests.h

## Purpose
This header is the ordered mock selftest registry for i915. It lists unit-style selftests that can run against mock hardware before or without normal live device operation.

## Important APIs, Types, And Functions
The file exposes a macro list only. Entries include sanity check, shmem utilities, software fence, scatterlist, syncmap, uncore, ring, engine, timelines, requests, objects, physical GEM, dmabuf, VMA, eviction, GTT, hugepages, and memory-region mock suites.

## Control Flow
`i915_selftest.c` repeatedly includes this header with macro definitions that generate enum constants, the `mock_selftests[]` dispatch table, and module parameters. The textual ordering controls execution order through `run_selftests(mock, NULL)`.

## State And Persistence
No state is stored in the header. Expanded entries become `struct selftest` records with mutable `enabled` flags in the compiled runner.

## Dependencies And Integration Points
Each listed function must have signature `int function(void)`. The file is part of the selftest macro contract and therefore cannot include normal include guards around the list expansion beyond the fallback `selftest` definition.

## Risks
Name collisions break enum/table generation. Reordering can hide dependencies between mock setup and later tests. Adding live-only behavior here would violate the no-hardware mock execution path.

## Test Signals
The generated mock runner prints the selected test name and stops on the first nonzero error. Build failures or absent module parameters are the primary signals of registry misuse.
