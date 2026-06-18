# sources/distributed-fs/ceph-client/include/trace/events/rseq.h

Purpose: Defines restartable-sequence tracepoints for task rseq pointer updates and instruction-pointer fixups after aborts or signal/preemption events.

Important APIs/types/functions: `rseq_update` records task PID, old rseq pointer, and new rseq pointer. `rseq_ip_fixup` records PID, original IP, fixed IP, and abort IP.

Control flow: rseq syscall or task setup paths emit update events when a task registers/unregisters its rseq area. Architecture/core rseq abort handling emits IP fixup when execution is redirected to an abort handler.

State and persistence: No state is owned. It observes per-task rseq registration and transient instruction pointer correction. The rseq userspace area persists in the task address space while registered.

Dependencies and integration points: Depends on tracepoints and types. It integrates with scheduler preemption, signal delivery, rseq syscall handling, and userspace per-CPU fast paths.

Risks and test signals: Risks include exposing userspace addresses, arch-specific IP correction drift, and tracing during signal/preempt paths. Test rseq selftests, register/unregister, migration/preemption aborts, signal aborts, exec/clone behavior, and 32/64-bit compat paths.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rseq.h` completely for this pass (62 lines, 1482 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rseq.h_research.md`.
