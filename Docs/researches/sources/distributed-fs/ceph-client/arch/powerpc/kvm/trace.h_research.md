
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace.h

## Purpose
Defines generic PowerPC KVM tracepoints for instruction emulation, shadow/guest TLB writes, shadow TLB invalidation, and request checks. `powerpc.c` defines `CREATE_TRACE_POINTS` before including this header, making it the tracepoint definition source.

## Important APIs, Types, And Functions
Trace events are `kvm_ppc_instr`, `kvm_stlb_inval`, `kvm_stlb_write`, `kvm_gtlb_write`, and `kvm_check_requests`. Each declares its argument list, trace entry fields, assignment block, and printk format.

## Control Flow
Callers invoke generated `trace_kvm_*` functions at emulation, TLB, and request-processing sites. The trace subsystem records event fields only when tracing is enabled. The bottom of the header sets `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace`, then includes `trace/define_trace.h` outside the guard.

## State And Persistence
No runtime state is owned by the header beyond generated static tracepoint definitions. Trace records are emitted into the kernel tracing infrastructure.

## Dependencies And Integration Points
Depends on `linux/tracepoint.h` and KVM vCPU definitions for request tracing. Export of `kvm_ppc_instr` from `powerpc.c` allows module users to attach to that tracepoint.

## Risks
Tracepoint field formats become observability ABI for tooling; changing field names or units can break scripts. Tracepoints that dereference vCPU fields must be called with valid vCPU lifetime. The header must maintain the trace include pattern exactly to avoid duplicate or missing definitions.

## Test Signals
Build and ftrace/perf availability are the main signals. Enabling `kvm:kvm_ppc_instr` and TLB events during guest execution should show decoded instruction and TLB writes/invalidation data.
