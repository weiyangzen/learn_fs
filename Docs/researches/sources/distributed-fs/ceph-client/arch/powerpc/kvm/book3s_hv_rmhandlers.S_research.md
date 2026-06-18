# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_rmhandlers.S

## Purpose

`book3s_hv_rmhandlers.S` is the real-mode assembly core for Book3S HV KVM on POWER7/POWER8 style entry paths and for shared real-mode helpers. It provides the trampoline from relocated host code into real-mode KVM, coordinates hardware threads across a vcore, switches partition/MMU/timebase state, enters and exits guests, handles selected interrupts and hcalls without returning to virtual mode, manages cede/nap states, and provides low-level FP/vector/PMU/TM save/restore helpers.

## Important APIs, Labels, And Tables

Externally visible symbols include `kvmppc_hv_entry_trampoline`, `idle_kvm_start_guest`, `kvmppc_interrupt_hv`, `kvm_flush_link_stack`, `hcall_real_table`, `hcall_real_table_end`, `kvmppc_h_set_xdabr`, `kvmppc_h_set_dabr`, `kvmppc_h_cede`, `kvmppc_save_tm_hv`, and `kvmppc_restore_tm_hv`. Important local labels include `kvmppc_hv_entry`, `kvmppc_got_guest`, `fast_guest_return`, `guest_exit_cont`, `guest_bypass`, `kvmhv_switch_to_host`, `kvmppc_guest_external`, `kvmppc_hdsi`, `kvmppc_hisi`, `hcall_try_real_mode`, `kvm_do_nap`, `kvm_end_cede`, `machine_check_realmode`, `hmi_realmode`, `kvmppc_check_wake_reason`, `kvmppc_save_fp`, `kvmppc_load_fp`, `kvmhv_load_guest_pmu`, `kvmhv_load_host_pmu`, and `kvmhv_save_guest_pmu`.

`hcall_real_table` maps real-mode hcall numbers to handlers such as HPT MMU functions from `book3s_hv_rm_mmu.c`, XICS handlers from `book3s_hv_rm_xics.c`, `kvmppc_h_cede`, `kvmppc_rm_h_confer`, DABR/XDABR setup, and random/page-init helpers.

## Control Flow

`kvmppc_hv_entry_trampoline` saves host MSR, clears RI, disables relocation through SRR0/SRR1, and calls `kvmppc_hv_entry`. On return it restores host DABR/SPRG/PMU/DEC, clears hwthread requests, and RFIs back to high memory or external interrupt handling.

`kvmppc_hv_entry` sets PACA `in_guest` to host-HV mode, joins the vcore entry map, lets the primary thread switch LPID/SDR1 to the guest partition, applies timebase offset and PCR/DPDES/VTB, marks subcore guest state, and releases secondaries. Each thread with a vcpu saves host/loads guest SPRs, PMU, FP/vector, TM, nonvolatile GPRs, SLB, decrementer, interrupt state, SRR/HSRR, and then reaches `fast_guest_return`, which loads guest volatile GPRs and performs `HRFI_TO_GUEST`.

Guest exits enter `kvmppc_interrupt_hv`, which saves volatile GPRs, CR, LR, CTR, XER, SRR/HSRR, DAR/DSISR, CFAR/PPR, and trap state into the vcpu, enables RI after critical state is safe, and dispatches special cases. HDSI/HISI paths call `kvmppc_hpte_hv_fault()` to decide retry, guest reflection, MMIO instruction fetch, or host exit. External interrupts call `kvmppc_read_intr()` and may re-enter the guest. Hcalls go through `hcall_try_real_mode`, checking privilege, enabled hcall bitmaps, and the real-mode table; `H_TOO_HARD` falls back to virtual mode.

The common exit path saves guest SLB, DEC expiry, PURR/SPURR deltas, POWER8-specific SPRs, AMR/UAMOR/DSCR/SPRGs, FP/vector/TM state, VPA yield count, and guest PMU state. `kvmhv_switch_to_host` then coordinates secondaries, has the primary switch LPID/SDR1 back to host, saves DPDES/VTB, unapplies timebase offset, clears subcore guest state, resets PCR/HDEC/LPCR, clears `in_guest`, and returns the trap.

Cede and nap flow is handled by `kvmppc_h_cede`, `kvm_do_nap`, and `kvm_end_cede`. A ceded vcpu saves enough state, sets napping bitmaps, programs DEC to wake no later than HDEC, enters a platform nap instruction, restores state on wake, checks wake reason, and either re-enters or exits.

## State And Persistence Behavior

The file persists guest state in `struct kvm_vcpu` offsets, vcore coordination state in `VCORE_ENTRY_EXIT`, `VCORE_IN_GUEST`, `VCORE_NAPPING_THREADS`, timebase offset fields, and PACA `kvm_hstate` fields. It relies on PACA scratch registers and exception save areas for reentrant interrupt state. `HSTATE_NAPPING`, `HSTATE_HWTHREAD_REQ`, and `HSTATE_HWTHREAD_STATE` persist per-thread sleep/ownership state. PMU, FP/vector, and TM helpers persist architectural state into vcpu fields.

## Dependencies And Integration Points

The assembly calls C helpers from the MMU, XICS, RAS, timing, interrupt, and platform layers, including `kvmppc_check_need_tlb_flush()`, `kvmppc_guest_entry_inject_int()`, `kvmppc_hpte_hv_fault()`, `kvmppc_read_intr()`, `kvmhv_commence_exit()`, `kvmppc_realmode_machine_check()`, `kvmppc_realmode_hmi_handler()`, and OPAL/HMI routines. It consumes offset definitions from `asm-offsets.h`, feature fixup macros, and CPU feature sections for POWER7/8/9 behavior.

## Risks

This file is extremely sensitive to register conventions, feature fixups, memory ordering, and real-mode constraints. A missed save/restore corrupts guest or host state. Incorrect vcore entry/exit coordination can let threads switch LPID or timebase while siblings are still in guest context. HDSI/HISI fast reflection must preserve MSR transactional state. Real-mode hcall handlers must not sleep or touch unsafe virtual addresses. The bad-host-interrupt path intentionally stops after saving state, indicating how unrecoverable exceptions can be in this window.

## Test Signals

Signals include POWER7/POWER8 HV guests, whole-core and split-core runs, secondary idle wakeups through `idle_kvm_start_guest`, cede/doorbell/decrementer wakeups, real-mode HPT hcalls, real-mode XICS hcalls, HDSI/HISI faults for paged-out and MMIO HPTEs, external interrupt pass-through, machine check and HMI exits, PMU/FP/vector/TM state preservation, and stress with simultaneous vcore exits across hardware threads.
