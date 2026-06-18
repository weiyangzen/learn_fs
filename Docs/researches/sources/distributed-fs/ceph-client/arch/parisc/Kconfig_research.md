<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/Kconfig -->
# sources/distributed-fs/ceph-client/arch/parisc/Kconfig

## Purpose
Defines the PA-RISC architecture configuration surface, selected generic capabilities, CPU families, page sizes, SMP, compatibility mode, and kexec support.

## Important APIs, Types, And Functions
Top-level `config PARISC` selects architecture features such as cache aliasing, DMA ops, strict RWX, perf, PCI, seccomp filter, eBPF JIT, stack walking, clockevents, kgdb, kprobes, dynamic ftrace, and endian/MMU defaults. CPU choices include `PA7000`, `PA7100LC`, `PA7200`, `PA7300LC`, and `PA8X00`; derived configs include `PA11`, `PA20`, `64BIT`, page-size choices, `SMP`, `IRQSTACKS`, `COMPAT`, and `NR_CPUS`.

## Control Flow
Kconfig dependency resolution selects architecture capabilities and exposes user choices. Build files and C code compile conditionally from these symbols.

## State And Persistence
No runtime state, but `.config` output persists build-time architecture behavior including ABI width, page size, CPU count, and enabled mitigations/features.

## Dependencies And Integration Points
Integrated with generic kernel subsystems for MM, DMA, tracing, BPF, PCI, RTC, kexec, modules, and scheduler topology.

## Risks
Selects must match actual architecture implementations. Some page-size options are marked `BROKEN`; enabling them would risk memory-management failures. 64-bit notes state there is no 64-bit userland, so compat handling is important.

## Test Signals
Kconfig olddefconfig for 32-bit and 64-bit PA-RISC, SMP builds, BPF JIT/tracing builds, page-size option gating, and kexec configuration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/Kconfig -->
