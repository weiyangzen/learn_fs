<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pkeys.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pkeys.h

## Purpose
This header declares PowerPC memory protection key support, including key allocation policy, execute-only pkey handling, AMR/IAMR/UAMOR helpers, and VMA permission integration.

## Important APIs, Types, And Functions
It defines pkey limits and special key values when supported, helpers for checking pkey availability, converting key/protection into PTE bits, initializing thread/user AMR/IAMR state, reserving/freeing pkeys, assigning execute-only pkeys, and arch hooks used by `mprotect_pkey()` and fault handling. Unsupported configurations provide no-op or default stubs.

## Control Flow
On supported CPUs, process setup initializes pkey registers and allocation bitmaps. VMA creation and mprotect paths assign pkeys and encode access rights. Fault paths and context switch code restore AMR/IAMR/UAMOR-derived state.

## State And Persistence Behavior
Pkey state persists per mm/thread in allocation maps and access-control registers. Execute-only mappings may reserve a dedicated key until released.

## Dependencies And Integration Points
It integrates with generic Linux pkeys, PowerPC radix/Book3S support, thread context, page-table protection bits, and signal/fault paths.

## Risks And Edge Cases
Unsupported configurations must preserve generic API expectations. Register state must be context-switched correctly. Execute-only pkey reuse can accidentally widen access if allocation state is mishandled.

## Test Signals
Run Linux pkeys selftests on supported POWER systems, mprotect_pkey permutations, fork/exec/context-switch tests, signal delivery, and unsupported-config build checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pkeys.h -->
