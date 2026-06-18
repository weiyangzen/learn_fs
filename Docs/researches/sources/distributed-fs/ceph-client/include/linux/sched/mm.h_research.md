# sources/distributed-fs/ceph-client/include/linux/sched/mm.h

Purpose: declares scheduler-facing MM lifetime helpers, current allocation-context scopes, mmap layout hooks, memcg active charging, and membarrier MM callbacks.

Important APIs and types: `mm_alloc()`, `mmgrab()`, `mmdrop()`, `mmdrop_sched()`, lazy-TLB refcount helpers, `mmget()`, `mmget_not_zero()`, `mmput()`, `mmput_async()`, `get_task_mm()`, `mm_access()`, exit/exec MM release helpers, mmap area selectors, `in_vfork()`, `current_gfp_context()`, `memalloc_*_save/restore()`, `might_alloc()`, `set_active_memcg()`, and membarrier state/flags are central.

Control flow: task lifetime code pins `mm_struct` either by structural count or active users count, drops references with barriers needed by membarrier, and uses RT-delayed drops where necessary. Allocation paths consult current PF_MEMALLOC flags to mask GFP bits, while scoped helpers temporarily impose NOIO/NOFS/noreclaim/pinning contexts.

State and persistence: state lives in `mm_struct` refcounts/flags/membarrier state, current task PF flags, active memcg pointers, and mmap layout. It persists for task/address-space lifetime and affects allocation behavior while scopes are active.

Dependencies and integration points: integrates scheduler task lifetime with MM, memcg, coredump dumpability, GFP reclaim, vfork, membarrier, architecture mmap layout, lazy TLB, and futex/private hash configs.

Risks and test signals: risks include confusing `mm_count` with `mm_users`, missing full barriers on mm drop, leaking memalloc scopes, incorrect GFP masking precedence, unsafe `real_parent` access in vfork checks, and membarrier sync-core omissions. Test fork/exec/exit, vfork, ptrace mm access, memcg charging, reclaim recursion scenarios, PREEMPT_RT, lazy TLB configs, and membarrier selftests.
