# sources/distributed-fs/ceph-client/arch/microblaze/kernel/traps.c

Purpose: initializes hardware exceptions and prints kernel stack/call traces for trap diagnostics.

Important APIs and state: `trap_init()` calls `__enable_hw_exceptions()`. `show_stack()` prints stack words and delegates call-trace decoding to `microblaze_unwind()`. Boot parameter `kstack=` limits stack words printed through `kstack_depth_to_print`.

Control flow: show_stack selects an SP from an explicit argument, sleeping task context, or current stack, computes remaining words in `THREAD_SIZE`, aligns the first hex dump line, prints stack bytes, then prints call trace and held locks.

State and persistence: only boot parameter state persists. Diagnostic output reads kernel stack memory.

Dependencies and integration: used by generic dump_stack/oops paths; depends on exception enable helper and unwinder.

Risks and test signals: invalid SP can dump bad memory; depth limiting is useful for noisy logs. Test oops output, `kstack=` parameter, current and non-current task stack dumps, and trap initialization.
