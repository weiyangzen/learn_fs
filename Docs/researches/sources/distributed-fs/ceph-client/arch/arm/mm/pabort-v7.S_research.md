# sources/distributed-fs/ceph-client/arch/arm/mm/pabort-v7.S

## Purpose
This file implements the ARMv7 prefetch-abort adapter, using both IFAR and IFSR so the generic fault path gets the architected instruction-fault address and status.

## Important APIs, Types, and Functions
The single entry is `v7_pabort`. It reads IFAR with `mrc p15, 0, r0, c6, c0, 2`, reads IFSR with `mrc p15, 0, r1, c5, c0, 1`, and tail-branches to `do_PrefetchAbort`.

## Control Flow
The abort vector enters `v7_pabort`; the handler collects CP15 fault registers and immediately branches to the C handler. Unlike the legacy and ARMv6 handlers, `r0` is not the saved `r4` instruction address but the architected IFAR value.

## State and Persistence Behavior
No local state is kept. The handler consumes transient CP15 exception registers. Downstream persistent effects are managed by `do_PrefetchAbort`.

## Dependencies and Integration Points
This handler is referenced by ARMv7 processor-function tables, including `proc-v7.S` outside this work item. It integrates with the ARM exception path and generic memory-fault logic.

## Risks
Using the handler on CPUs with incompatible IFAR/IFSR behavior would misreport faults. Correct ordering matters because exception state must be read before any later handler path could disturb it. It also depends on the common abort ABI preserving the registers mentioned in the file comment.

## Test Signals
Build ARMv7 configurations and trigger instruction fetch faults across unmapped, no-execute, and permission-denied pages. Check that reported fault addresses come from IFAR and that status decoding routes to the expected signal or oops path.
