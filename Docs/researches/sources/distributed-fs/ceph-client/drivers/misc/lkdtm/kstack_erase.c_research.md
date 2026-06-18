# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/kstack_erase.c

## Purpose
`kstack_erase.c` verifies that stackleak/kstack erasure poisoned the unused portion of the current task stack with `KSTACK_ERASE_POISON`.

## Important APIs, Types, and Functions
The main implementation is `check_stackleak_irqoff()` under `CONFIG_KSTACK_ERASE`, wrapped by `lkdtm_KSTACK_ERASE()`. It uses `task_stack_page()`, `stackleak_task_low_bound()`, `stackleak_task_high_bound()`, `current_stack_pointer`, `current->lowest_stack`, `stackleak_find_top_of_poison()`, `instrumentation_begin/end()`, and IRQ save/restore.

## Control Flow
The test disables local IRQs to stabilize stack usage and calls a `noinstr` checker. The checker validates current and lowest stack pointers against task stack bounds, computes the untracked range, finds the top of poison, scans downward to the low bound for non-poison words, and prints either failure details or stack usage offsets. If stack erasure is not built, the crashtype reports an expected failure based on architecture support.

## State and Persistence
No persistent state is owned. It reads per-task stack metadata, especially `current->lowest_stack`, and stack memory contents.

## Dependencies and Integration Points
Depends on `CONFIG_KSTACK_ERASE`, `CONFIG_HAVE_ARCH_KSTACK_ERASE`, `<linux/kstack_erase.h>`, architecture stack bounds, and LKDTM crashtype registration through `stackleak_crashtypes`.

## Risks
Any function call, interrupt, or compiler-generated stack behavior can alter the measured area. The file avoids printing until after instrumentation is re-enabled to reduce false positives.

## Test Signals
Signals include bounds validation, reported poison coverage, `OK` when the rest of the stack is erased, `FAIL` on non-poison values below the poison boundary, and `XFAIL` when support is absent.
