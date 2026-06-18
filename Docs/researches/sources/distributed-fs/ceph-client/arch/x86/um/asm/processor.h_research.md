<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/processor.h

## Purpose
`processor.h` defines UML/x86 processor-facing helpers and thread register access conventions.

## Important APIs, types, and functions
Important macros/functions are `KSTK_EIP`, `KSTK_ESP`, `KSTK_EBP`, `ARCH_IS_STACKGROW`, `native_pause()`, `cpu_relax()`, `task_pt_regs()`, and inclusion of bitness-specific `arch_thread` definitions.

## Control flow
Scheduler and memory-management code use these helpers to inspect saved host register arrays and decide stack growth. Busy-wait loops call `cpu_relax()`, which advances time-travel modes instead of only executing `pause`.

## State and persistence behavior
State lives in each task's `thread.regs` and `thread.arch`; this header only defines accessors.

## Dependencies and integration points
It depends on `sysdep/faultinfo.h`, `processor_32.h`/`processor_64.h`, time-travel internals, and generic processor definitions.

## Risks and edge cases
Stack-growth decisions depend on a correct saved SP. Time-travel modes require `cpu_relax()` to avoid infinite simulated CPU loops.

## Test signals
Signals are UML scheduler tests, stack-growth fault handling, and time-travel mode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/processor.h -->
