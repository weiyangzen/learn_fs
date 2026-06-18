<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-riscv.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-riscv.c

## Purpose

`kvm-stat-riscv.c` supplies RISC-V KVM stat tracepoint and trap-cause decoding.

## Important APIs, Types, and Functions

It defines `riscv_exit_reasons`, tracepoints `kvm:kvm_entry` and `kvm:kvm_exit`, `event_get_key()`, begin/end predicates, `exit_events`, registration ops, skip events, and exported RISC-V hook functions.

## Control Flow

Begin matches RISC-V KVM entry. End matches RISC-V KVM exit, reads the `scause` field, masks off the interrupt high bit with `CAUSE_IRQ_FLAG(64)`, and decodes the remaining cause through the RISC-V trap table.

## State and Persistence Behavior

Static tables are immutable. Runtime state is limited to event keys and `exit_reasons_isa = "riscv64"`.

## Dependencies and Integration Points

It depends on common KVM stat, evsel field extraction, `riscv_trap_types.h`, and `EM_RISCV` dispatch.

## Risks and Edge Cases

The code currently hardcodes `xlen = 64` with a TODO for 32-bit support. Masking interrupt causes means interrupt and exception numeric namespaces share the same decode table after removing the high bit. Kernel tracepoint field-name changes would break decoding.

## Test Signals

Tests should cover exception and interrupt `scause` values, high-bit masking, unknown traps, and future 32-bit RISC-V behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-riscv.c -->
