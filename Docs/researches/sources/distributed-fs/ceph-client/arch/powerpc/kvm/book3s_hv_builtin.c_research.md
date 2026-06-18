# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_builtin.c

## Purpose

`book3s_hv_builtin.c` contains Book3S HV support that must be built into the kernel or callable from real-mode/low-level contexts. It handles CMA reservation for hash page tables, real-mode hypercall helpers, HV VM activity tracking, real-mode IPI and exit coordination, XICS passthrough interrupt triage, interrupt injection support, guest MSR sanitization, and per-CPU TLB flush checks.

## Important APIs, Types, And Functions

`early_parse_kvm_cma_resv()` parses the `kvm_cma_resv_ratio=` boot parameter. `kvm_cma_reserve()` reserves a contiguous CMA area for KVM HPT allocation when the host is in HV mode. `kvm_alloc_hpt_cma()` and `kvm_free_hpt_cma()` allocate and release HPT pages from that CMA area and are GPL-exported.

`kvmppc_rm_h_confer()` implements the real-mode part of `H_CONFER` by watching vcore running, ceded, and conferring bitmaps for a short timebase window and returning `H_TOO_HARD` when the virtual-mode scheduler should yield.

`hv_vm_count`, `kvm_hv_vm_activated()`, `kvm_hv_vm_deactivated()`, and `kvm_hv_mode_active()` track whether HV VMs exist, using CPU hotplug read locking around count changes. `kvmppc_hcall_impl_hv_realmode()` checks the real-mode hcall table. `kvmppc_hwrng_present()` and `kvmppc_rm_h_random()` expose platform random seed support to real-mode hcalls.

`kvmhv_rm_send_ipi()`, `kvmhv_interrupt_vcore()`, and `kvmhv_commence_exit()` send doorbells/IPIs and coordinate all threads in a vcore or split-core group to leave the guest. `kvmppc_read_intr()` and `kvmppc_read_one_intr()` read XICS/OPAL interrupt state in real mode, distinguish host IPIs, guest wakeup IPIs, passthrough interrupts, and host-handled interrupts, and save XIRR state in PACA.

`get_irqmap()` and `kvmppc_check_passthru()` support lockless lookup of mapped passthrough IRQs when `CONFIG_KVM_XICS` is enabled. `kvmppc_set_msr_hv()`, `inject_interrupt()`, `kvmppc_inject_interrupt_hv()`, and `kvmppc_guest_entry_inject_int()` sanitize guest MSR, synthesize interrupt entry state, and inject pending external/decrementer/doorbell events. `flush_guest_tlb()` and `kvmppc_check_need_tlb_flush()` perform per-CPU guest TLB flushes requested by shared masks.

## Control Flow

Early boot calls `kvm_cma_reserve()` after memblock setup. If HV mode is unavailable it returns; otherwise it computes a percentage of physical memory, aligns to HPT requirements, and declares the `kvm_cma` area. Later HPT allocation uses `cma_alloc()` with HPT alignment and releases with `cma_release()`.

Real-mode exit coordination begins when one guest thread calls `kvmhv_commence_exit()`. It atomically sets that thread's exit-request bit in `entry_exit_map`; the first exiting thread interrupts other active vcore threads, and if split-core mode is active it also marks other subcores for exit and interrupts them.

Interrupt polling reads host IPI state first, then XICS/OPAL XIRR when XIVE is not active. XICS IPIs are cleared and EOIed; if a host IPI raced in, it is resent and the host handles it. Otherwise guest wakeup IPIs are consumed in real mode. Non-IPI interrupts are checked against passthrough mappings; mapped interrupts can be delivered directly to the target virtual interrupt controller, while unmapped or failed delivery returns control to host interrupt handling.

Interrupt injection writes SRR0/SRR1, PC, and MSR according to Book3S rules, including transactional suspend conversion and LPCR AIL=3 alternate interrupt location when legal. `kvmppc_set_msr_hv()` forces ME on, HV off, rejects illegal TS=11, updates the shadow MSR, and clears cede state.

## State And Persistence Behavior

Persistent-in-kernel state includes the CMA reservation pointer, the boot-time reservation ratio, `hv_vm_count`, and exported `kvmppc_host_rm_ops_hv`. Runtime per-vCPU/vcore state includes `conferring_threads`, `entry_exit_map`, PACA `kvm_hstate` fields, saved XIRR, cede/timer flags, doorbell state, and per-VM `need_tlb_flush` masks. No filesystem persistence is used.

## Dependencies And Integration Points

The file depends on memblock/CMA, CPU hotplug locks, OPAL interrupt services, XICS/XIVE interfaces, PACA `kvm_hstate`, Book3S interrupt constants, hcall real-mode tables, platform random seed hooks, and the HV private header. It exports functions used by KVM-HV modules, real-mode assembly handlers, and host interrupt paths.

## Risks

Real-mode code has strict constraints: it cannot rely on normal sleeping locks and must carefully order MMIO, OPAL, and shared-memory updates. The passthrough IRQ map uses lockless readers, so writer store ordering and the reader `smp_rmb()` are correctness-critical. Exit coordination uses bitmaps shared with assembly; incorrect bit placement can leave sibling threads running. Interrupt injection must preserve Book3S MSR/SRR semantics, especially around TM and AIL. CMA reservation sizing can fail HPT allocation if the ratio or alignment is wrong.

## Test Signals

Signals include successful HPT allocation from CMA, correct `kvm_cma_resv_ratio` parsing, CPU hotplug blocked while pre-POWER9 HV VMs exist, `H_CONFER` yield behavior, real-mode `H_RANDOM`, guest exits pulling all vcore/split-core threads out, XICS guest wakeup IPIs not leaking to the host, passthrough IRQs delivered or completed correctly, decrementer/external/doorbell injection, and per-CPU TLB flush masks clearing after guest TLB invalidation.
