# sources/distributed-fs/ceph-client/include/trace/events/percpu.h

Purpose: Provides tracepoints for percpu allocator success, failure, chunk creation, chunk destruction, and frees. It helps diagnose allocation size/alignment, atom size, group choice, and fragmentation.

Important APIs/types/functions: Events include `percpu_alloc_percpu`, `percpu_free_percpu`, `percpu_alloc_percpu_fail`, `percpu_create_chunk`, and `percpu_destroy_chunk`. Fields capture reserved/dynamic flag, allocation size, alignment, base/offset, group, bits, unit size, atom size, allocated/free population, and failure reason.

Control flow: The percpu allocator emits events when requests are satisfied, fail, or cause backing chunks to be created/destroyed. Free events record address and allocation characteristics.

State and persistence: No state is owned by the header. It observes in-memory percpu allocator metadata and allocated areas, which live until freed or allocator teardown.

Dependencies and integration points: Depends on tracepoints and MM flag formatting. It integrates with core allocator diagnostics, module loading, networking, scheduler, and any subsystem using per-CPU storage.

Risks and test signals: Risks include hot-path overhead, leaking sensitive addresses in traces, mismatched unit/group interpretation, and missing failure context. Test percpu allocator selftests, module load/unload churn, large alignment requests, fragmentation pressure, NUMA configs, and allocation-failure injection.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/percpu.h` completely for this pass (137 lines, 3186 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/percpu.h_research.md`.
