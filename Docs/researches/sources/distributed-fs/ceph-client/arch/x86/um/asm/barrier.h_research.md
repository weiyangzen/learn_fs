<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/barrier.h

## Purpose
`barrier.h` defines UML/x86 memory barrier primitives using x86 instructions suitable for device and shared-memory ordering.

## Important APIs, types, and functions
APIs are `mb()`, `rmb()`, and `wmb()`. On 32-bit they use alternatives between locked stack ops and SSE fences; on 64-bit they directly emit `mfence`, `lfence`, and `sfence`.

## Control flow
Callers expand the macros inline, then generic barrier definitions fill in the rest of the Linux barrier API.

## State and persistence behavior
No state exists except alternative patching metadata on 32-bit builds.

## Dependencies and integration points
It depends on `cpufeatures.h`, `alternative.h`, and generic barrier fallbacks.

## Risks and edge cases
Instruction selection must be valid for the configured CPU feature set; barriers are required even on UP because UML can interact with devices/shared host state.

## Test signals
Signals are build coverage, lock/barrier tests, and runtime stability under SMP/time-travel/device I/O workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/barrier.h -->
