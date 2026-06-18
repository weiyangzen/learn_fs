# sources/distributed-fs/ceph-client/kernel/events/callchain.c

## Purpose

`callchain.c` manages perf callchain capture buffers and callchain sysctls. It allocates per-CPU, recursion-context-aware buffers usable from NMI context, coordinates lifetime across perf events, captures kernel and user callchains through weak architecture hooks, fixes uretprobe trampoline entries, and exposes sysctl limits for maximum stack depth and context markers.

## Important APIs, Types, And Functions

- `struct callchain_cpus_entries` stores an RCU head and a flexible per-CPU array of `struct perf_callchain_entry *` buffers.
- `sysctl_perf_event_max_stack` and `sysctl_perf_event_max_contexts_per_stack` define global callchain limits.
- `perf_callchain_entry__sizeof()` computes per-entry size from the sysctl stack and context limits.
- `callchain_recursion` is a per-CPU recursion guard indexed by `PERF_NR_CONTEXTS`.
- `nr_callchain_events`, `callchain_mutex`, and `callchain_cpus_entries` manage buffer lifetime.
- Weak hooks `perf_callchain_kernel()` and `perf_callchain_user()` are implemented by architectures.
- `alloc_callchain_buffers()` and `release_callchain_buffers()` allocate and RCU-free per-CPU callchain buffers.
- `get_callchain_buffers()` and `put_callchain_buffers()` reference-count global buffers for perf events.
- `get_callchain_entry()` and `put_callchain_entry()` acquire/release a per-CPU buffer for the current recursion context.
- `fixup_uretprobe_trampoline_entries()` replaces uretprobe trampoline addresses with original return addresses.
- `get_perf_callchain()` captures a kernel and/or user callchain into a reusable entry.
- `perf_event_max_stack_handler()` updates sysctls only when no callchain events are active.
- `init_callchain_sysctls()` registers the `kernel.perf_event_max_stack` and `kernel.perf_event_max_contexts_per_stack` sysctls.

## Control Flow

Perf events call `get_callchain_buffers()` when they need callchains. Under `callchain_mutex`, the event count increments, per-event max-stack requests are rejected with `-EOVERFLOW` when above the global cap, and the first event allocates buffers. Allocation creates one top-level `callchain_cpus_entries` object sized for `nr_cpu_ids` and then one buffer per possible CPU sized for all recursion contexts. Releasing decrements the count, and the final put swaps the global pointer to NULL and frees buffers after an RCU grace period.

`get_callchain_entry()` obtains a recursion context from the per-CPU guard. If no context is available or global buffers are missing, it returns NULL after cleanup. Otherwise it returns the current CPU's buffer slice for that recursion context. `get_perf_callchain()` initializes a context wrapper, optionally stores kernel/user context markers, invokes the architecture kernel hook when requested and not already in user mode, then handles user callchain capture unless cross-task user-only capture was requested. For deferred user stacks, it stores `PERF_CONTEXT_USER_DEFERRED` and the cookie instead of walking the user stack.

After a user walk, `fixup_uretprobe_trampoline_entries()` scans newly added user IPs and replaces uretprobe trampoline addresses with pending return-instance original return addresses. Sysctl writes are staged through a temporary table; writes are accepted only while no callchain events are active, preventing buffer-size changes under active users.

## State And Persistence Behavior

Runtime state includes global sysctl variables, per-CPU recursion bytes, an atomic active-event count, mutex-protected buffer lifetime, RCU-protected buffer pointers, and per-task uprobe return instances inspected during fixup. Sysctl values persist during the kernel runtime and affect future buffer sizing; buffer allocations persist while at least one callchain event is active.

## Dependencies And Integration Points

The file depends on perf event internals, architecture callchain walkers, NMI-safe buffer access, per-CPU APIs, RCU, mutexes, sysctl registration, scheduler task stack helpers, uprobes, recursion guards, and context marker constants such as `PERF_CONTEXT_KERNEL`, `PERF_CONTEXT_USER`, and `PERF_CONTEXT_USER_DEFERRED`.

## Risks And Edge Cases

- Buffers are manually per-CPU allocated because normal percpu allocation is not suitable for NMI access; freeing must be RCU-delayed.
- Sysctl writes while events are active are rejected with `-EBUSY` to prevent buffer-size mismatch.
- `get_callchain_buffers()` increments the event count before validation and must decrement on errors.
- Cross-task user-only callchains are rejected because user stacks are not supported for that mode.
- Recursion guard exhaustion returns NULL and avoids corrupting nested callchain captures.
- Uretprobe fixup assumes pending return instances correspond to encountered trampoline addresses in order.

## Test Signals

Use perf record/report callchains for kernel-only, user-only, mixed, and deferred user stacks; stress NMI sampling; test nested perf contexts; change sysctls before and during active callchain events; validate `-EOVERFLOW` for per-event stack requests above the cap; run uretprobe return-probe callchain tests; and use KASAN/KCSAN/RCU debug builds to catch lifetime or concurrency errors.
