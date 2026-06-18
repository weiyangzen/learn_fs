# sources/distributed-fs/ceph-client/arch/x86/xen/multicalls.c

Purpose: Implements per-CPU batching for Xen hypercalls through the multicall interface, amortizing trap overhead for MMU, descriptor, and CPU lazy-mode operations.

Important APIs/types/functions: `struct mc_buffer` stores pending multicall entries, argument bytes, and post-flush callbacks. Optional `struct mc_debug_data` records callers and arguments. Public helpers are `xen_mc_flush()`, `__xen_mc_entry()`, `xen_mc_extend_args()`, and `xen_mc_callback()`. Early params/init include `xen_mc_debug` and `mc_debug_enable()`.

Control flow and state: Callers allocate a slot and argument storage in the current CPU buffer. If the buffer or argument area is full, it flushes. Flush disables interrupts, directly invokes single calls or `HYPERVISOR_multicall()` for batches, reports failed entries, resets indices, and runs callbacks such as deferred lock release or CR3 state updates. Debug mode copies entries before executing so failures can print original arguments and callers.

Dependencies and integration points: It depends on Xen hypercall wrappers, per-CPU state, static keys, debugfs-related config, tracepoints, and all PV MMU/CPU code that enters lazy modes.

Risks and test signals: Multicall code assumes non-preemptible callers and per-CPU ordering. Failure reporting is diagnostic only; many failures still WARN/BUG higher up. Callback ordering is part of MMU correctness. Test signals include PV boot under `xen_mc_debug`, lazy MMU batching, descriptor/TLB update stress, no preemptible caller BUGs, and useful logs for injected multicall failures.
