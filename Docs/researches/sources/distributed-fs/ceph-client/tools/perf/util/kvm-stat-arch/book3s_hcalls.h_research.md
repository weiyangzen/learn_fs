<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/book3s_hcalls.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/book3s_hcalls.h

## Purpose

`book3s_hcalls.h` is the PowerPC Book3S HV hypercall code-to-name mapping for `perf kvm stat hcall`.

## Important APIs, Types, and Functions

The single `kvm_trace_symbol_hcall` macro expands many `{code, "H_*"}` entries such as `H_REMOVE`, `H_ENTER`, `H_CEDE`, `H_REGISTER_VPA`, `H_GET_PERF_COUNT`, `H_RANDOM`, and `H_RTAS`.

## Control Flow

There is no local flow. `kvm-stat-powerpc.c` expands the macro into an `exit_reasons_table` and uses it when hcall enter events provide a `req` code.

## State and Persistence Behavior

The table is static decode metadata aligned with PowerPC hypervisor ABI codes. It stores no runtime data.

## Dependencies and Integration Points

It integrates with `kvm_hv:kvm_hcall_enter`/`kvm_hcall_exit` tracepoints and `hcall_event_decode_key()`.

## Risks and Edge Cases

Unknown or newly added hypercalls decode as `UNKNOWN`. Incorrect codes would corrupt reports without causing runtime failures.

## Test Signals

Sample-driven tests should cover common HCALLs and an unknown code, ensuring the hcall report key displays the expected name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/book3s_hcalls.h -->
