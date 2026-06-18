<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/cpu-features.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/cpu-features.h

Purpose: publishes SH CPU feature bit positions.

Important APIs/types/functions: `CPU_HAS_FPU`, `P2_FLUSH_BUG`, `MMU_PAGE_ASSOC`, `DSP`, `PERF_COUNTER`, `PTEA`, `LLSC`, `L2_CACHE`, `OP32`, `PTEAEX`, `CAS_L`.

Control flow: kernel CPU detection sets these bits and proc/ELF code interprets them.

State and persistence: state is in `current_cpu_data.flags` and exposed indirectly to procfs/userspace.

Dependencies/integration: must stay in sync with proc flag strings and CPU probe code.

Risks: bit renumbering silently changes feature meaning.

Test signals: compare `/proc/cpuinfo` flags against detected CPU subtype capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/cpu-features.h -->
