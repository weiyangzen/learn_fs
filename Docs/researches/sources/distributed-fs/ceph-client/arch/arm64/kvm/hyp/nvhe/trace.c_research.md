<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/trace.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/trace.c

## Purpose
`trace.c` implements hyp-side tracing buffer management for nVHE. It loads a host-provided descriptor, admits backing pages into hyp or pins shared pages depending on protected mode, initializes per-CPU simple ring buffers, enables/disables tracing, swaps reader pages, updates the trace clock, and resets buffers.

## Important APIs, Types, and Functions
`trace_buffer` holds per-CPU `simple_rb_per_cpu` state, donated backing pages, and a lock. `tracing_reserve_entry()` and `tracing_commit_entry()` are the hyp event write path. `__tracing_load()` admits the host descriptor, validates it, and calls `hyp_trace_buffer_load()`. `hyp_trace_desc_validate()` bounds-checks descriptor entries, CPU ordering, and backing page counts. `__tracing_unload()`, `__tracing_enable()`, `__tracing_swap_reader()`, `__tracing_update_clock()`, and `__tracing_reset()` expose host hypercall operations.

## Control Flow, State, and Persistence
The trace buffer is globally loaded or unloaded under `trace_buffer.lock`; loaded state is indicated by nonzero backing size. In protected mode, descriptor/backing memory is donated to hyp and per-buffer page VAs are pinned as shared pages; unload reverses these operations after zeroing backing memory. Clock updates wait until all per-CPU buffers are not in `SIMPLE_RB_WRITING`, then update the shared clock bank.

## Dependencies and Integration Points
It depends on `simple_ring_buffer.c`, hyp clock helpers, pKVM memory donation/pinning from `mem_protect.c`, address translation helpers, `hyp_nr_cpus`, tracing hypercalls in `hyp-main.c`, and generated hyp event IDs.

## Risks and Test Signals
Risks include trusting malformed descriptors, CPU/order mismatches, leaked donated backing pages on partial load failure, busy-wait clock updates, tracing while unloaded, and protected/non-protected memory admission differences. Test signals are load/unload success and failure paths, descriptor fuzzing, per-CPU swap/reset, enable without load returning error, trace event write/read integrity, and memory ownership after unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/trace.c -->
