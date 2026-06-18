<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-arm64.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-arm64.c

## Purpose

`kvm-stat-arm64.c` provides ARM64-specific tracepoint names, exit-key extraction, and registration tables for `perf kvm stat`.

## Important APIs, Types, and Functions

It defines `arm64_exit_reasons` and `arm64_trap_exit_reasons`, event tracepoints `kvm:kvm_entry` and `kvm:kvm_exit`, `event_get_key()`, begin/end predicates, `exit_events`, `__kvm_reg_events_ops`, skip-event list, and exported functions `__cpu_isa_init_arm64()`, `__kvm_events_tp_arm64()`, `__kvm_reg_events_ops_arm64()`, and `__kvm_skip_events_arm64()`.

## Control Flow

Begin events match ARM64 KVM entry. End events match ARM64 KVM exit and call `event_get_key()`. Basic exits decode the `ret` trace field against exception types; TRAP exits switch to the `esr_ec` trace field and ESR exception-class table.

## State and Persistence Behavior

The module stores static tables only. Runtime state is written into `struct event_key` and `perf_kvm_stat.exit_reasons_isa`.

## Dependencies and Integration Points

It depends on common KVM stat APIs, `evsel__intval()`, ARM64 exception macros, and `EM_AARCH64` dispatch from `kvm-stat.c`.

## Risks and Edge Cases

Tracepoint field names must match kernel tracing. TRAP handling depends on `esr_ec` being present. Unknown exception classes fall through common decode as `UNKNOWN`.

## Test Signals

Tracepoint sample tests should cover entry/exit pairing, IRQ/SERROR exits, TRAP ESR decoding, and missing/unknown field behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-arm64.c -->
