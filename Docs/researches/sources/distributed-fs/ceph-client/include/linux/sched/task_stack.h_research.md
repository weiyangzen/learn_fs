# sources/distributed-fs/ceph-client/include/linux/sched/task_stack.h

Purpose: declares kernel stack access, reference, end-marker, stack-cache, and debug helpers for tasks.

Important APIs and types: `task_stack_page()`, `setup_thread_stack()`, `end_of_stack()`, `try_get_task_stack()`, `put_task_stack()`, `exit_task_stack_account()`, `task_stack_end_corrupted()`, `object_is_on_stack()`, `thread_stack_cache_init()`, `stack_not_used()`, `set_task_stack_end_magic()`, and `kstack_end()` are key.

Control flow: fork/setup code initializes thread stack metadata, stack readers pin non-current task stacks where refcounted, debug code checks magic/end corruption and unused stack, and object-on-stack tests compare against current stack bounds after KASAN tag reset.

State and persistence: state is each task’s kernel stack pointer, optional stack refcount, VMAP stack area, and stack-end magic. It lasts for task lifetime and stack RCU/freeing rules.

Dependencies and integration points: depends on `sched.h`, thread-info layout, magic constants, refcounts, KASAN, VMAP stack, and architecture stack growth direction.

Risks and test signals: risks include reading an exiting task stack without pinning, stack-growth boundary mistakes, missing magic initialization, and KASAN tag comparison errors. Test stack debugging, VMAP_STACK, THREAD_INFO_IN_TASK and legacy layouts, task exit races, and stack-usage diagnostics.
