<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/riscv_trap_types.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/riscv_trap_types.h

## Purpose

`riscv_trap_types.h` defines RISC-V interrupt and exception cause constants and a macro table for KVM stat trap decoding.

## Important APIs, Types, and Functions

It defines `CAUSE_IRQ_FLAG(xlen)`, interrupt cause constants such as supervisor/VS/machine software, timer, external, guest external, and PMU overflow, exception causes such as illegal instruction, breakpoints, load/store/inst access and page faults, hypervisor/supervisor syscalls, guest page faults, and virtual instruction fault, plus `TRAP(x)` and `kvm_riscv_trap_class`.

## Control Flow

No executable flow exists. RISC-V KVM stat masks the interrupt flag from `scause` and decodes the remaining value with the macro-expanded table.

## State and Persistence Behavior

The file is static architecture decode metadata aligned with RISC-V cause numbers.

## Dependencies and Integration Points

It uses `_AC` from kernel-style constant macros and integrates with `kvm-stat-riscv.c`.

## Risks and Edge Cases

Interrupt and exception causes can share low numeric values after masking; the combined table must be interpreted in context. New RISC-V causes require updates. Current consumer assumes 64-bit xlen.

## Test Signals

Tests should validate interrupt-flag masking, each guest page fault cause, virtual instruction fault, PMU overflow, and unknown cause fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/riscv_trap_types.h -->
