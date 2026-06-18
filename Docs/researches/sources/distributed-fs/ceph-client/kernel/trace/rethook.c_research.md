# sources/distributed-fs/ceph-client/kernel/trace/rethook.c

## Purpose
`rethook.c` implements the generic return-hook infrastructure used by facilities such as kretprobes. It manages per-task shadow stacks of hooked return addresses, preallocated hook nodes, trampoline handling, handler invocation, and cleanup when hooked tasks exit before returning.

## Important APIs, types, and functions
Public APIs include `rethook_alloc()`, `rethook_stop()`, `rethook_free()`, `rethook_try_get()`, `rethook_hook()`, `rethook_recycle()`, `rethook_flush_task()`, `rethook_find_ret_addr()`, and `rethook_trampoline_handler()`. Important types are `struct rethook`, `struct rethook_node`, `rethook_handler_t`, task `rethooks` llist storage, and the `objpool` used to preallocate nodes.

## Control flow
Clients allocate a `struct rethook` with a non-NULL handler and a fixed node pool. At function entry, with preemption disabled, a client obtains a node with `rethook_try_get()`, architecture code rewrites the return path through `rethook_hook()`, and the node is pushed onto `current->rethooks`. When the architecture trampoline fires, `rethook_trampoline_handler()` finds the original return address, restores the instruction pointer, runs handlers for nodes on the matching frame, applies optional architecture return-address fixup, unlinks the used shadow-stack nodes, and recycles them. If a task exits with unreached return hooks, `rethook_flush_task()` recycles all leftover nodes.

## State and persistence
State is runtime-only and split between the rethook object, its RCU-protected handler pointer, the object pool, and each task's lockless list of active nodes. `rethook_stop()` publishes a NULL handler to prevent new gets and to switch recycling into delayed RCU pool dropping. `rethook_free()` is asynchronous; callers must not touch the object afterward.

## Dependencies and integration points
The file depends on architecture-specific return-hook support (`arch_rethook_prepare`, `arch_rethook_trampoline`, optional `arch_rethook_fixup_return`), task lifetime cleanup, RCU, preemption control, lockless lists, objpool, kallsyms/kprobes headers, and `NOKPROBE_SYMBOL` annotations to keep core paths from being probed recursively.

## Risks and test signals
Risks include handler lifetime misuse after `rethook_free()`, node pool exhaustion, missing preemption disable around node acquisition, RCU-unavailable contexts rejected by validation builds, incorrect frame matching causing wrong return-address recovery, and fatal BUG if a trampoline cannot find the real return address. Test signals include nested return hooks on the same task, task exit with pending hooks, handler unregister under load, pool exhaustion behavior, stack traces using `rethook_find_ret_addr()`, and architecture-specific trampoline/fixup correctness.
