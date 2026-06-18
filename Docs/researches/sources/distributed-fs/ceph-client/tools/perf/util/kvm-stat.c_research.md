<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat.c

## Purpose

`kvm-stat.c` is the common architecture-dispatch and default event helper layer for `perf kvm stat`.

## Important APIs, Types, and Functions

It implements common helpers `kvm_exit_event()`, `kvm_entry_event()`, `exit_event_get_key()`, `exit_event_begin()`, `exit_event_end()`, and `exit_event_decode_key()`. Dispatch functions include `setup_kvm_events_tp()`, `cpu_isa_init()`, `vcpu_id_str()`, `kvm_exit_reason()`, `kvm_entry_trace()`, `kvm_exit_trace()`, `kvm_events_tp()`, `kvm_reg_events_ops()`, `kvm_skip_events()`, and `kvm_add_default_arch_event()`.

## Control Flow

Common begin/end logic reads the evsel ELF machine, compares evsel names against architecture-specific entry/exit tracepoint names, and fills an `event_key` with the architecture-specific exit reason field. Dispatch switches on `e_machine` to call ARM64, LoongArch, PowerPC, RISC-V, s390, or x86 providers. Unsupported machines print errors and return failure/null.

## State and Persistence Behavior

No persistent state is owned here. It reads architecture tables and mutates `perf_kvm_stat` during ISA init and setup.

## Dependencies and Integration Points

It depends on evsel machine detection, tracepoint field extraction, common debug logging, and arch providers declared in `kvm-stat.h`. It is the central integration point between generic KVM stat code and per-architecture modules.

## Risks and Edge Cases

Unsupported `e_machine` values must fail clearly. `exit_event_decode_key()` assumes `key->exit_reasons` is set; architectures that rely on `kvm->exit_reasons` must ensure keys point to a valid table before decoding. Field-name dispatch must match kernel tracepoint definitions.

## Test Signals

Tests should exercise every architecture dispatch branch, unsupported machine handling, vCPU field-name selection, entry/exit trace names, skip-event tables, and default event injection for x86/PowerPC only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat.c -->
