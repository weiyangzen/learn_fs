<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/book3s_hv_exits.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/book3s_hv_exits.h

## Purpose

`book3s_hv_exits.h` maps PowerPC Book3S HV interrupt/vector exit codes to display names for KVM VM-exit reports.

## Important APIs, Types, and Functions

The `kvm_trace_symbol_exit` macro lists vector codes such as `RETURN_TO_HOST`, `SYSTEM_RESET`, `MACHINE_CHECK`, storage and segment exceptions, `EXTERNAL`, `DECREMENTER`, hypervisor storage exits, `PERFMON`, `ALTIVEC`, and `VSX`.

## Control Flow

No executable flow exists. PowerPC KVM stat expands the macro into `hv_exit_reasons` and uses common exit-event begin/end logic.

## State and Persistence Behavior

The file is static decode metadata tied to PowerPC exception-vector values.

## Dependencies and Integration Points

It integrates with `kvm_hv:kvm_guest_exit` tracepoint `trap` fields and common KVM stat decoding.

## Risks and Edge Cases

Stale or missing vector codes lead to `UNKNOWN` or wrong display names. Values are architecture-specific and should not be reused for non-Book3S KVM.

## Test Signals

Tests should decode representative trap values, especially external/decrementer/storage exits and unknown values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/book3s_hv_exits.h -->
