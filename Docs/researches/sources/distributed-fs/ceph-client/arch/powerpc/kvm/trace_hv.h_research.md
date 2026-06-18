
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_hv.h

## Purpose
Defines tracepoints for Book3S HV KVM guest entry/exit, page faults, hypercalls, vcore scheduling/blocking, vCPU run loop entry/exit, and nested/pseries vCPU timing counters.

## Important APIs, Types, And Functions
Defines large symbolic maps `kvm_trace_symbol_hcall`, `kvm_trace_symbol_kvmret`, and `kvm_trace_symbol_hcall_rc`, then events `kvm_guest_enter`, `kvm_guest_exit`, `kvm_page_fault_enter`, `kvm_page_fault_exit`, `kvm_hcall_enter`, `kvm_hcall_exit`, `kvmppc_run_core`, `kvmppc_vcore_blocked`, `kvmppc_vcore_wakeup`, `kvmppc_run_vcpu_enter`, `kvmppc_run_vcpu_exit`, and conditional `kvmppc_vcpu_stats`.

## Control Flow
HV code emits tracepoints at guest transitions, hash/radix page fault handling, hcall dispatch, and scheduling paths. The tracepoint callbacks snapshot vCPU IDs, PC/MSR/trap state, HPTE/GPTE fields, memslot metadata, hcall arguments/return values, runnable counts, wait duration, and nested transition timing. `kvmppc_vcpu_stats` is conditionally emitted only when counters are nonzero and uses registration callbacks.

## State And Persistence
No owned state. The header defines trace metadata and event snapshots consumed by ftrace/perf/BPF.

## Dependencies And Integration Points
Depends on `trace_book3s.h`, `asm/hvcall.h`, `asm/kvm_asm.h`, optional `CONFIG_PPC_PSERIES`, and HV KVM structures such as `struct kvmppc_vcore`. It is part of the Book3S HV observability surface.

## Risks
The hcall symbolic table is extensive and must track firmware ABI additions. Some trace entries dereference memslots or HPTE arrays, so call sites must provide valid pointers. Trace output exposes low-level addresses and guest state, so it is powerful but sensitive in production diagnostics.

## Test Signals
Enable `kvm_hv:*` tracepoints under Book3S HV guests. Expected signals include enter/exit pairs, hcall enter/exit pairs with symbolic names, page fault records, and vcore scheduling events during multi-vCPU workloads.
