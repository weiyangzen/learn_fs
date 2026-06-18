# sources/distributed-fs/ceph-client/include/linux/scs.h

Purpose: `scs.h` declares Shadow Call Stack support used to protect return addresses by keeping a separate per-task shadow stack. It provides allocation, task preparation/release, runtime enablement queries, and corruption checks around a sentinel value.

Important APIs/types/functions: With `CONFIG_SHADOW_CALL_STACK`, the header defines `SCS_ORDER`, `SCS_SIZE`, `GFP_SCS`, `SCS_END_MAGIC`, `task_scs()`, `task_scs_sp()`, and functions `scs_alloc()`, `scs_free()`, `scs_init()`, `scs_prepare()`, and `scs_release()`. Inline helpers include `scs_task_reset()`, `__scs_magic()`, `task_scs_end_corrupted()`, `scs_is_dynamic()`, and `scs_is_enabled()`. Disabled builds stub these to no-ops or false.

Control flow: Task setup allocates and initializes an SCS area, stores base/SP in thread info, and resets SP when tasks are reused. On release, the area is freed. Runtime checks compare the magic word at the end of the allocation and verify the shadow stack pointer remains inside bounds.

State and persistence behavior: State is per-task in `thread_info` fields and per-allocation in the sentinel word. `dynamic_scs_enabled` provides a static key for runtime dynamic SCS mode. No persistent disk state exists.

Dependencies and integration points: It depends on task/thread-info layout, page allocation, poison pointer constants, static keys, scheduler lifecycle, and architecture compiler support for shadow call stacks. It is tightly integrated with fork/exit and low-level call/return instrumentation.

Risks: Bad stack bounds or missed reset can corrupt future task state. Dynamic SCS checks must match architecture enablement. The sentinel check uses `READ_ONCE_NOCHECK()` to avoid sanitizer false positives; changing this can create noisy or unsafe instrumentation.

Test signals: Test `CONFIG_SHADOW_CALL_STACK` and disabled builds, fork/exit stress, task reuse, deliberate sentinel corruption, dynamic SCS toggling, and architecture context-switch paths that save/restore the SCS pointer.
