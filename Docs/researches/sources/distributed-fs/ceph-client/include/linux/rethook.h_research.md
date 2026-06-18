# sources/distributed-fs/ceph-client/include/linux/rethook.h

Purpose: this header declares the generic return-hook framework, which uses a per-task list-based shadow stack to intercept function returns for tracing/probing infrastructure.

Important APIs/types/functions: `rethook_handler_t` is the callback type. `struct rethook` stores user data, RCU-protected handler pointer, object pool, and RCU head. `struct rethook_node` stores RCU/list linkage, owning rethook, real return address, and frame pointer. APIs include `rethook_alloc()`, `rethook_stop()`, `rethook_free()`, `rethook_try_get()`, `rethook_recycle()`, `rethook_hook()`, `rethook_find_ret_addr()`, architecture hooks `arch_rethook_prepare()`, `arch_rethook_trampoline()`, `arch_rethook_fixup_return()`, generic `rethook_trampoline_handler()`, `is_rethook_trampoline()`, and `rethook_flush_task()`.

Control flow: clients allocate a rethook pool, obtain nodes, install a hook by replacing a return address via architecture preparation, and the trampoline calls the generic handler on function return. Nodes are recycled to the pool. Stop/free uses RCU/object-pool lifetime rules; task exit flushes pending nodes when enabled.

State and persistence: rethook state persists across active hooked calls; nodes are shadow-stack entries linked from task state and hold original return address/frame. Handler pointer is RCU-protected for safe stop/free.

Dependencies and integration points: depends on objpool, kallsyms symbol descriptors, lockless lists, RCU, `pt_regs`, and architecture-specific trampoline/return-address manipulation. It integrates with kretprobes/fprobe-style return instrumentation.

Risks: architecture implementations must preserve calling convention and frame/return-address correctness. Pool exhaustion can drop hooks. Incorrect RCU/free sequencing can call stale handlers. Test signals include kretprobe/fprobe return-hook tests, nested returns, task exit flush, trampoline address detection, pool exhaustion, and architecture unwinder correctness.
