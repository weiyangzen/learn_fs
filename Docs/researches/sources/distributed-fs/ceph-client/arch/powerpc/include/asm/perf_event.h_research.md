<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event.h

## Purpose
This is the top-level PowerPC perf-event architecture header. It selects server or Freescale embedded PMU definitions and supplies generic register-capture helpers for perf.

## Important APIs, Types, And Functions
It conditionally includes `perf_event_server.h` for `CONFIG_PPC_PERF_CTRS` or provides stub `is_sier_available()` and `get_pmcs_ext_regs()`. It includes `perf_event_fsl_emb.h` for embedded PMU support. Under `CONFIG_PERF_EVENTS`, it defines `perf_arch_bpf_user_pt_regs()`, `perf_arch_fetch_caller_regs()`, declares `is_sier_available()`, `get_pmcs_ext_regs()`, and `PERF_REG_EXTENDED_MASK`.

## Control Flow
Perf sampling uses the fetch macro to populate caller registers with instruction pointer, stack pointer, MSR, and current task. PMU-specific code comes from the selected backend.

## State And Persistence Behavior
The header owns no state. `PERF_REG_EXTENDED_MASK` and backend PMU registration state are defined elsewhere.

## Dependencies And Integration Points
It integrates with Linux perf, BPF perf register access, ptrace register layout, and server/embedded PMU drivers.

## Risks And Edge Cases
Stub SIER functions must match unavailable hardware behavior. Caller register capture must produce valid pt_regs enough for perf unwinding. Backend selection depends on mutually correct Kconfig.

## Test Signals
Run `perf stat`, `perf record`, BPF perf programs, extended-register sampling on supported POWER CPUs, and embedded PMU builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event.h -->
