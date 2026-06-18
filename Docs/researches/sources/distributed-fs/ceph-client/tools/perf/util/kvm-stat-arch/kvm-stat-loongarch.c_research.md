<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-loongarch.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-loongarch.c

## Purpose

`kvm-stat-loongarch.c` implements LoongArch KVM stat exit decoding, including special handling for guest privileged instruction traps.

## Important APIs, Types, and Functions

It defines LoongArch exception constants and `loongarch_exit_reasons`, tracepoints `kvm_enter`, `kvm_reenter`, `kvm_exit`, and `kvm_exit_gspr`, begin/end predicates, `event_gspr_get_key()`, child event table for `kvm_exit_gspr`, and exported arch hooks for ISA initialization, tracepoints, registered events, and skip events.

## Control Flow

Begin uses common `exit_event_begin()` on `kvm_exit`. End is either `kvm_enter` or `kvm_reenter`, reflecting LoongArch's adjacent reentry/entry behavior after exits. The child `kvm_exit_gspr` event decodes the trapped instruction word to classify CPUCFG, CSR, IOCSR, IDLE, or other privileged traps.

## State and Persistence Behavior

Static tables define names. `__cpu_isa_init_loongarch()` sets `exit_reasons_isa` to `loongarch64` and assigns the exit-reason table into the runtime KVM stat object.

## Dependencies and Integration Points

It depends on common KVM stat, tracepoint parsing, PMU headers, evsel field reads, and `EM_LOONGARCH` dispatch.

## Risks and Edge Cases

Instruction decoding in `event_gspr_get_key()` is pattern-based and must match kernel trace semantics. Begin/end pairing differs from other architectures, so regressions can invert measured durations. Unknown privileged traps collapse to `Others`.

## Test Signals

Tests should cover `kvm_reenter` and `kvm_enter` as end events, ordinary exit reasons, GSPR instruction classification for CPUCFG/CSR/IOCSR/IDLE, and unknown instruction fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-loongarch.c -->
