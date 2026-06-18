<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-powerpc.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-powerpc.c

## Purpose

`kvm-stat-powerpc.c` provides PowerPC Book3S HV KVM stat support for VM exits and hypercalls, plus a default guest-profiling event choice.

## Important APIs, Types, and Functions

It defines `hv_exit_reasons`, `hcall_reasons`, Book3S HV tracepoint list, hcall key/decode functions, `hcall_events`, `exit_events`, registered event ops for `vmexit` and `hcall`, `is_tracepoint_available()`, `ppc__setup_book3s_hv()`, `ppc__setup_kvm_tp()`, `__setup_kvm_events_tp_powerpc()`, `__cpu_isa_init_powerpc()`, and `__kvm_add_default_arch_event_powerpc()`.

## Control Flow

Setup creates a temporary evlist and verifies all Book3S HV tracepoints can be parsed. On success it publishes them in `__kvm_events_tp`, sets HV exit reasons, and labels the ISA `HV`. VM-exit events use common begin/end logic. HCALL events begin on `kvm_hcall_enter`, read the `req` field, and end on `kvm_hcall_exit`. Default event augmentation adds `trace_imc/trace_cycles/` when the user did not specify `-e` and the PMU event is available.

## State and Persistence Behavior

The module has a static mutable tracepoint pointer array populated at setup. Runtime KVM state receives exit-reason table and ISA label. Default event injection duplicates strings into argv.

## Dependencies and Integration Points

It depends on Book3S HV tracepoints, parse-events, PMU event discovery, parse-options, common KVM stat, and PowerPC hcall/exit mapping headers.

## Risks and Edge Cases

Only Book3S HV is supported; missing tracepoints cause setup failure. The temporary evlist allocated in setup is not visibly deleted in this file, so leak checks should inspect caller/build behavior. Default event injection returns `-EINVAL` if `trace_imc/trace_cycles` is unavailable. HCALL unknown codes log debug and decode as `UNKNOWN`.

## Test Signals

Tests should cover tracepoint availability success/failure, VM-exit and hcall reports, default event insertion with and without user `-e`, unavailable trace_imc fallback, and unknown hcall codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-powerpc.c -->
