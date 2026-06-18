# sources/distributed-fs/ceph-client/arch/x86/kvm/trace.h

## Purpose
`trace.h` defines the x86 KVM tracepoint API for VM entry/exit, hypercalls, port I/O, MMIO, CPUID, interrupt/APIC delivery, nested virtualization, instruction emulation, TSC/timekeeping, SMM, posted interrupts/APICv/AVIC, Hyper-V features, SEV VMGEXIT, and SNP RMP faults. It is shared by VMX, SVM, Hyper-V, Xen, MMU, LAPIC, and SEV code.

For the SVM subset, this file is the observability surface used by `svm.c` for entry/exit, page faults, CR/MSR access, interrupt injection, nested SVM VMRUN/VMEXIT, INVLPGA/SKINIT, PLE window updates, AVIC events, Hyper-V TLB flushes, VMGEXIT, and RMP faults.

## Important APIs, Types, and Functions
Trace infrastructure:

- `TRACE_SYSTEM kvm` groups all events under KVM.
- `tracing_kvm_rip_read(vcpu)` returns RIP unless guest state is protected, in which case it reports zero to avoid reading inaccessible SEV-protected state.
- `KVM_ISA_VMX` and `KVM_ISA_SVM` distinguish exit reason formatting.
- `kvm_print_exit_reason(exit_reason, isa)` formats VMX and SVM exit reasons differently.
- `TRACE_EVENT_KVM_EXIT(name)` generates VM-exit-style tracepoints using the active `kvm_x86_ops.get_exit_info()` callback.

Major event families:

- Entry/exit: `kvm_entry`, `kvm_exit`, `kvm_nested_vmexit`.
- Hypercalls: `kvm_hypercall`, `kvm_hv_hypercall`, `kvm_hv_hypercall_done`, `kvm_xen_hypercall`.
- I/O and emulation: `kvm_pio`, `kvm_fast_mmio`, `kvm_cpuid`, `kvm_msr`, `kvm_cr`, `kvm_emulate_insn`, `vcpu_match_mmio`.
- IRQ/APIC: `kvm_ioapic_set_irq`, `kvm_ioapic_delayed_eoi_inj`, `kvm_msi_set_irq`, `kvm_apic`, `kvm_apic_ipi`, `kvm_apic_accept_irq`, `kvm_eoi`, `kvm_pv_eoi`, `kvm_inj_virq`, `kvm_inj_exception`, `kvm_pi_irte_update`.
- Nested virtualization: `kvm_nested_vmenter`, `kvm_nested_intercepts`, `kvm_nested_vmexit_inject`, `kvm_nested_intr_vmexit`, `kvm_nested_vmenter_failed`.
- SVM-specific or SVM-relevant: `kvm_invlpga`, `kvm_skinit`, `kvm_ple_window_update`, `kvm_avic_incomplete_ipi`, `kvm_avic_unaccelerated_access`, `kvm_avic_ga_log`, `kvm_avic_kick_vcpu_slowpath`, `kvm_avic_doorbell`, `kvm_vmgexit_enter`, `kvm_vmgexit_exit`, `kvm_vmgexit_msr_protocol_enter`, `kvm_vmgexit_msr_protocol_exit`, `kvm_rmp_fault`.
- Timekeeping: `kvm_write_tsc_offset`, `kvm_update_master_clock`, `kvm_track_tsc`, `kvm_pvclock_update`, `kvm_wait_lapic_expire`.
- SMM and APICv: `kvm_smm_transition`, `kvm_apicv_inhibit_changed`, `kvm_apicv_accept_irq`.
- Hyper-V synthetic interrupt/timer/TLB/IPI/debug: `kvm_hv_notify_acked_sint`, `kvm_hv_synic_set_irq`, `kvm_hv_synic_send_eoi`, `kvm_hv_synic_set_msr`, `kvm_hv_stimer_*`, `kvm_hv_timer_state`, `kvm_hv_flush_tlb`, `kvm_hv_flush_tlb_ex`, `kvm_hv_send_ipi`, `kvm_hv_send_ipi_ex`, `kvm_pv_tlb_flush`, `kvm_hv_syndbg_set_msr`, and `kvm_hv_syndbg_get_msr`.

Convenience wrappers:

- `trace_kvm_apic_read/write`, `trace_kvm_msr_read/write/read_ex/write_ex`, `trace_kvm_cr_read/write`, and `trace_kvm_emulate_insn_start/failed` normalize common read/write trace uses.

## Control Flow
This file is compile-time tracepoint definition, not executable control logic by itself. Callers invoke generated `trace_kvm_*()` functions at runtime. `TP_fast_assign` blocks capture fields from caller arguments into per-event records, and `TP_printk` defines human-readable formatting.

For entry/exit events, control flows through generic x86 KVM callbacks: `kvm_entry` uses `kvm_x86_call(get_entry_info)` and `kvm_exit`/`kvm_nested_vmexit` use `kvm_x86_call(get_exit_info)`. On SVM, those callbacks are supplied by `svm_get_entry_info()` and `svm_get_exit_info()` in `svm.c`, which read VMCB `event_inj`, `exit_code`, `exit_info_*`, and interrupt info fields.

The header ends by setting `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE`, then includes `<trace/define_trace.h>` outside include guards as required by Linux tracepoint generation.

## State and Persistence Behavior
Tracepoints do not own persistent VM state. They snapshot runtime state into the kernel tracing ring buffer when enabled. Fields include vCPU ID, RIP, exit reason, interrupt info, error code, requests bitmap, GPA/GVA, MSR/CR values, APIC vectors, nested VMCB/VMCS identifiers, TSC offsets, Hyper-V masks, GHCB data, and RMP fault metadata.

Protected guest state behavior is explicit: `tracing_kvm_rip_read()` avoids reading RIP for protected guests and emits zero, preventing tracepoints from depending on inaccessible SEV-ES/SNP register state.

## Dependencies and Integration Points
The header depends on Linux tracepoint macros and x86 architecture headers for VMX/SVM exit symbols, clocksource IDs, and pvclock structures. It also references KVM structures such as `struct kvm_vcpu`, `struct kvm_lapic`, `struct ghcb`, and `struct pvclock_vcpu_time_info`.

Integration points with this subset:

- `svm.c` emits `trace_kvm_entry`, `trace_kvm_exit`, `trace_kvm_page_fault`, `trace_kvm_fast_mmio`, `trace_kvm_cr_read/write`, `trace_kvm_invlpga`, `trace_kvm_skinit`, `trace_kvm_inj_virq`, `trace_kvm_apicv_accept_irq`, and `trace_kvm_ple_window_update`.
- Nested SVM code uses nested VMRUN/VMEXIT/intercept events.
- AVIC code uses the `kvm_avic_*` events.
- SEV code uses VMGEXIT and RMP fault tracepoints.
- Hyper-V paths use TLB, IPI, SynIC, timer, and synthetic debug tracepoints.

## Risks and Edge Cases
Risks:

- Tracepoints must not access protected guest state directly; the RIP helper mitigates that for entry/exit and page-fault style events.
- Tracepoint field widths must match architecture values; truncating exit codes, addresses, or masks would mislead debugging.
- Events called from hot paths must keep assignment logic cheap when tracing is disabled and safe when enabled.
- Format strings and symbolic tables must stay aligned with SVM/VMX architectural constants.
- `TRACE_EVENT_KVM_EXIT` depends on runtime x86 ops; backends must provide valid `get_exit_info()` and `get_entry_info()` semantics.

## Test Signals
Validation signals include successful kernel tracepoint generation, ability to enable events under `/sys/kernel/tracing/events/kvm/`, correct SVM exit reason formatting with `SVM_EXIT_REASONS`, and useful traces under workloads that exercise VM entry/exit, NPF, nested SVM, AVIC, Hyper-V TLB/IPI, VMGEXIT, and SNP RMP faults.
