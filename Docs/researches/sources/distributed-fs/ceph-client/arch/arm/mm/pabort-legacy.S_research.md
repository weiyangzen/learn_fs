# sources/distributed-fs/ceph-client/arch/arm/mm/pabort-legacy.S

## Purpose
This small assembly file implements the legacy ARM prefetch-abort adapter for CPUs that do not provide a useful instruction fault status register in the newer ARMv6/v7 form.

## Important APIs, Types, and Functions
The only exported entry is `legacy_pabort`. It receives the common abort-entry register convention: `r2` points at `pt_regs`, `r4` contains the aborted instruction address, and `r5` contains the parent context PSR. It passes `r0 = r4` and a fixed `r1 = 5` fault status to `do_PrefetchAbort`.

## Control Flow
The vector/abort glue enters `legacy_pabort`, which does no local decoding. It preserves the caller-required register set and tail-branches to the C abort handler. The fixed status value stands in for a legacy prefetch-abort reason.

## State and Persistence Behavior
There is no stored state. The handler only transfers register values to `do_PrefetchAbort`; lasting effects are whatever the generic abort path does, such as signal delivery, fault accounting, or kernel oops handling.

## Dependencies and Integration Points
The file depends on `linux/linkage.h` and `asm/assembler.h` for `ENTRY`/`ENDPROC`. It is wired into CPU processor-function tables by older `proc-*.S` files through `define_processor_functions ... pabort=legacy_pabort`.

## Risks
The fixed status code has less diagnostic precision than IFSR/IFAR-aware handlers. Incorrectly assigning this handler to a CPU that expects architected fault-status handling can degrade fault classification and debugging. Since it tail-branches into C with the abort ABI, any register convention drift would be severe.

## Test Signals
Build CPU configurations whose proc tables reference `legacy_pabort`, then run instruction-prefetch fault tests from user mode and kernel fault-injection paths. Useful signals are correct SIGSEGV/SIGBUS behavior, expected kernel oops reporting, and no register corruption across abort entry.
