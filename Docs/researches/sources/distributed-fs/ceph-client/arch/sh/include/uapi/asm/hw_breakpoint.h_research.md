<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/hw_breakpoint.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/hw_breakpoint.h

Purpose: marks SH hardware-breakpoint UAPI as empty/unsupported in this tree.

Important APIs/types/functions: no structs or ioctls are declared.

Control flow: ptrace/perf breakpoint features cannot rely on arch-specific UAPI from this header.

State and persistence: no state.

Dependencies/integration: included by generic perf/ptrace headers to satisfy architecture layout.

Risks: adding fields later is ABI-sensitive and must align with perf_event expectations.

Test signals: build perf/ptrace headers and confirm unsupported breakpoint paths fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/hw_breakpoint.h -->
