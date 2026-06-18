# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ucall.S

## Purpose
Provides the minimal assembly helper for issuing a PowerPC ultravisor call and returning the status in `r3`.

## Important APIs, Types, And Functions
Exports GPL symbol `ucall_norets`. The body executes `sc 2`, the ultravisor system-call variant, and then returns with `blr`.

## Control Flow
Callers load ultravisor arguments according to the platform ABI and branch to `ucall_norets`. The ultravisor handles the secure call and returns to the helper, which immediately returns to the caller with `r3` carrying the status.

## State And Persistence
The helper has no private state and touches no memory. Its effects are entirely those of the ultravisor operation invoked by `sc 2`.

## Dependencies And Integration Points
Depends on `<asm/ppc_asm.h>` for `_GLOBAL` and on the ultravisor ABI implemented by secure PowerPC platforms. Kernel secure-VM code can link to the exported symbol.

## Risks And Edge Cases
Correctness depends on the caller setting registers exactly as the ultravisor ABI expects. The helper has no local validation, no register save frame, and no fallback for systems without an ultravisor.

## Test Signals
Build/link coverage with ultravisor users and secure guest runtime tests are the main signals. Functional testing should exercise successful and failing ultravisor calls and validate returned status propagation.
