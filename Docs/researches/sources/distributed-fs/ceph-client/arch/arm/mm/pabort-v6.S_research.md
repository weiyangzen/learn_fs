# sources/distributed-fs/ceph-client/arch/arm/mm/pabort-v6.S

## Purpose
This file implements the ARMv6 prefetch-abort adapter. It reports the aborted instruction address from the exception glue and reads the architected instruction fault status register.

## Important APIs, Types, and Functions
The entry point is `v6_pabort`. It uses `mrc p15, 0, r1, c5, c0, 1` to read IFSR, leaves `r0` as the aborted instruction address from `r4`, and branches to `do_PrefetchAbort`.

## Control Flow
Abort entry code calls `v6_pabort`. The handler copies `r4` to `r0`, reads IFSR into `r1`, and tail-branches into the generic C prefetch-abort handler. It does not read IFAR, so the faulting address is still the instruction address supplied by the common abort frame.

## State and Persistence Behavior
No state is stored by this file. It consumes CP15 fault-state at abort time and transfers it to generic exception handling. Persistent effects are limited to the generic fault path.

## Dependencies and Integration Points
It is selected from `proc-v6.S` through the processor-function table as `pabort=v6_pabort`. It depends on CP15 availability and on the common ARM abort ABI used by `do_PrefetchAbort`.

## Risks
The risk is CPU mismatch. Using this handler on cores without the expected IFSR register semantics would provide an invalid status. Since IFAR is not read, fault-address precision depends on the exception entry path's instruction address.

## Test Signals
Build ARMv6 MMU configurations and exercise execute faults: user execute on unmapped pages, permission faults, and kernel prefetch faults. Confirm IFSR-derived codes are visible to the generic abort handler and that fault reporting matches ARMv6 expectations.
