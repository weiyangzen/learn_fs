<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rseq.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rseq.h

Purpose: defines the restartable sequences syscall ABI shared between the kernel and C libraries for per-thread, userspace-managed critical sections that abort on migration, signal, or preemption.

Important APIs, types, and functions: enums define special CPU ID states, `RSEQ_FLAG_UNREGISTER`, and critical-section feature/status bits. `struct rseq_cs` describes a critical section by version, flags, start IP, post-commit offset, and abort IP with cacheline alignment. `struct rseq` is the per-thread registered area containing CPU IDs, active `rseq_cs` pointer, feature flags, NUMA node ID, memory-map concurrency ID, `rseq_slice_ctrl`, reserved feature byte, and flexible end marker.

Control flow: userspace allocates an aligned `struct rseq`, registers it with the `rseq` syscall, updates `rseq_cs` before entering assembly critical sections, verifies CPU ID fields before commit, and unregisters when a thread exits or disables rseq. The kernel updates CPU, node, mm_cid, flags, and slice-control state, and clears/redirects active critical sections on abort events.

State and persistence behavior: state is per-thread userspace memory registered with the kernel. It is not persistent across process lifetime, and a thread may have only one active registration. The extensible area size and alignment are advertised by auxv but remain backward-compatible with the original 32-byte allocation.

Dependencies and integration points: depends on Linux types and byteorder headers. It integrates with the `rseq` syscall, libc TLS setup, sched/migration paths, signal delivery, restartable sequence assembly, and userspace allocators or per-CPU data structures.

Risks and edge cases: alignment and feature-size handling are critical. Userspace must not reclaim active `rseq_cs` memory without clearing the pointer. Unsupported historical no-restart flags must remain false. 32-bit architectures must write the low bits of `rseq_cs` consistently. Feature growth must preserve old 32-byte behavior.

Test signals: libc registration tests, migration/preemption/signal abort tests, auxv size/alignment handling, unregister paths, 32-bit compat builds, mm_cid/node_id correctness, and stress tests with per-CPU counters under CPU hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rseq.h -->
