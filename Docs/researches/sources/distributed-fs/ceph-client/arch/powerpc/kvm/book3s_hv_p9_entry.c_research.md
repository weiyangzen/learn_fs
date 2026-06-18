# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_p9_entry.c

## Purpose

`book3s_hv_p9_entry.c` is the C implementation of the POWER9 and later KVM-HV vcpu entry/exit path. It switches host CPU state into guest state, enters the low-level assembly guest transition, captures exit state, restores host state, and accounts time, MMU context, PMU state, decrementers, transactional memory, and security-sensitive registers.

## Important APIs, Types, And Functions

The exported functions are `load_vcpu_state()`, `store_vcpu_state()`, `save_p9_host_os_sprs()`, `restore_p9_host_os_sprs()`, optional `accumulate_time()`, `kvmppc_msr_hard_disable_set_facilities()`, and `kvmhv_vcpu_entry_p9()`. Important local helpers include `load_spr_state()`, `store_spr_state()`, SLB accessors, `radix_clear_slb()`, `switch_mmu_to_guest_radix()`, `switch_mmu_to_guest_hpt()`, `switch_mmu_to_host()`, `save_clear_host_mmu()`, `save_clear_guest_mmu()`, `flush_guest_tlb()`, and `check_need_tlb_flush()`.

`struct p9_host_os_sprs` carries host SPRs that must be restored after guest execution. The file manipulates `vcpu->arch` state, `vcpu->arch.vcore`, `local_paca->kvm_hstate`, and host thread state in `current->thread`.

## Control Flow

`kvmhv_vcpu_entry_p9()` starts by computing HDEC from `time_limit` and the current timebase, rejecting already expired runs. It saves host MSR and host SPRs such as HFSCR, CIABR, PSSCR, PID, DAWRs, PURR/SPURR, IAMR, and AMR. It hard-disables interrupts while enabling any guest-required facilities, aborts if a lazy interrupt is pending, then loads vcpu state including TM, scalar SPRs, FP, and vector state.

Before guest entry it applies any guest timebase offset, writes VTB/PURR/SPURR/PCR/DPDES, installs guest DAWR/CIABR/PSSCR/HFSCR, sets HSRR0/HSRR1 for guest HRFID, writes a canary to HDSISR on affected POWER9 revisions, loads SPRGs, marks `local_paca->kvm_hstate.in_guest`, optionally disables translation to avoid radix prefetch or hash-context hazards, switches MMU context to guest radix or HPT, flushes pending per-core TLB state, writes HDEC and DEC, loads DAR/DSISR/SRR0/SRR1, switches PMU to guest, and calls `kvmppc_p9_enter_guest()`.

On return it accumulates timing, switches PMU back, saves SRR/DAR/DSISR and trap state, reconstructs volatile GPRs and special registers from PACA exception save areas, handles machine check and HMI in real mode, records HEIR/ASDR/HFSCR for relevant traps, and may immediately re-enter the guest for early POWER9 TM softpatch emulation. It then updates host PURR/SPURR accounting, saves guest IC/PID/PSSCR/SPRG/doorbell/VTB/DEC state, unapplies any timebase offset, saves/clears guest MMU state, switches back to host LPID/PID/LPCR, reenables MSR facilities only after host MMU is restored, stores vcpu FP/vector/TM state, restores host PURR/SPURR/PSSCR/HFSCR/CIABR/DAWR/DPDES/PCR/HDEC/DEC and OS SPRs, clears `in_guest`, and aborts copy-paste buffers on ARCH_31 CPUs.

## State And Persistence Behavior

The function persists guest-modified CPU state back into `vcpu->arch`, including general trap/fault fields, SPRs, PMU, TM, FP/vector state, decrementer expiry, timebase offset application, doorbell state, and performance counters. Host state is kept in stack locals and `p9_host_os_sprs` and is restored before exit. `vc->tb_offset_applied` records whether the hardware timebase has been shifted and must be reset before host return. `need_tlb_flush` cpumasks are cleared per CPU after guest TLB flush synchronization.

## Dependencies And Integration Points

The C entry path wraps the lower-level `kvmppc_p9_enter_guest()` assembly helper and is selected by `book3s_hv.c` for P9 bare-metal and nested v1 runs. It calls PMU helpers from `book3s_hv_p9_perf.c`, RAS handlers from `book3s_hv_ras.c`, TM helpers from `book3s_hv_rmhandlers.S` and `book3s_hv_tm_builtin.c`, MMU/TLB helpers from Book3S radix/HPT code, and host decrementer/timer helpers. Nested v1 is supported by choosing `nested->shadow_lpid` in radix guest MMU switching.

## Risks

This is a high-risk context switch path. Ordering around `in_guest`, MSR[RI], MMU switches, and exception save areas is critical for recoverability from SRESET/MCE/HMI. Incorrect host SPR restoration can corrupt host thread state after scheduling. Timebase offset application must be symmetric on all exits. TLB flush cpumask races can leave stale guest translations on sibling threads. POWER9 errata handling for HDSISR, TM assist, PSSCR fake suspend, and copy-paste must remain feature-gated. Any failure before host state restoration can be fatal.

## Test Signals

Signals include repeated guest entry/exit under external interrupts, HDEC/DEC expiry, radix and HPT guests, nested v1 L2 runs, PMU enabled and disabled guests, DAWR/CIABR debug registers, doorbell delivery, TM active/suspended paths, POWER9 radix prefetch bug configurations, machine-check/HMI injection, and stress tests that combine host scheduling with guest FP/vector/PMU use.
