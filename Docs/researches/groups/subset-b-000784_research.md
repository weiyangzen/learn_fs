# subset-b-000784 Research

Grouped research for the PowerPC Book3S HV KVM files under `sources/distributed-fs/ceph-client/arch/powerpc/kvm`. Each section preserves the source path and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_nested.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_nested.c

## Purpose

`book3s_hv_nested.c` implements nested virtualization support for Book3S HV KVM on POWER9 and later, mainly the nested v1 path plus shared nested partition-table and shadow radix-MMU management. It lets an L1 guest run an L2 guest through `H_ENTER_NESTED`, translates L1 LPIDs into L0 shadow LPIDs, mirrors L1 partition/process table state into L0-visible partition table entries, handles nested TLB invalidation hcalls, and services nested radix page faults by installing mappings in per-nested-guest shadow page tables.

## Important APIs, Types, And Functions

Key exported or externally used entry points are `kvmhv_enter_nested_guest()`, `kvmhv_nested_init()`, `kvmhv_nested_exit()`, `kvmhv_flush_lpid()`, `kvmhv_set_ptbl_entry()`, `kvmhv_set_partition_table()`, `kvmhv_copy_tofrom_guest_nested()`, `kvmhv_vm_nested_init()`, `kvmhv_release_all_nested()`, `kvmhv_get_nested()`, `kvmhv_put_nested()`, `kvmhv_insert_nest_rmap()`, `kvmhv_update_nest_rmap_rc_list()`, `kvmhv_remove_nest_rmap_range()`, `kvmhv_do_nested_tlbie()`, `do_h_rpt_invalidate_pat()`, `kvmhv_nested_page_fault()`, and `kvmhv_nested_next_lpid()`.

Important data structures are `struct hv_guest_state` for the L2 HV register block passed by L1, `struct pt_regs` for L2 GPR/control state, `struct kvm_nested_guest` for L1 LPID to shadow LPID state, and `struct rmap_nested` for reverse mappings from host memslots back to nested shadow PTEs. The file also owns the pseries nested v1 partition table allocation through `pseries_partition_tb` and the global `nested_capabilities` negotiated with a parent hypervisor.

## Control Flow

`kvmhv_enter_nested_guest()` is the central L2 run path. It rejects missing L1 partition-table setup and transactional-mode misuse, reads `hv_guest_state` and `pt_regs` from L1 guest memory, performs endian conversion when needed, validates the state version and vcpu token, and checks that L1 and L2 transactional-state combinations are legal. It then obtains or creates a `struct kvm_nested_guest` for the L1 LPID, refreshes the cached L1 partition table entry when needed, saves L1 register/HV state, converts L2 timebase/decrementer values into host-relative values, installs L2 state into the current vcpu, filters LPCR and HFSCR, masks hypervisor DAWR/CIABR settings, and runs `kvmhv_run_single_vcpu()`. On exit it saves L2 return state, restores L1 state, accumulates PURR/SPURR/IC/VTB deltas into L1 accounting, writes the L2 state back to L1 memory, and maps MMIO completion state to nested GPR storage when needed.

Initialization has two modes. On pseries with radix enabled, `kvmhv_nested_init()` first probes `plpar_guest_get_capabilities()`. If nested v2 capability negotiation succeeds it enables the static branch `__kvmhv_is_nestedv2` and avoids the v1 partition table. Otherwise it allocates a nested v1 partition table, registers it with `H_SET_PARTITION_TABLE`, and uses `kvmhv_set_ptbl_entry()` to update pseries entries. On bare metal it writes the hardware partition table directly.

Nested guest lifecycle flows through the per-VM IDR. `kvmhv_get_nested()` validates the L1 LPID against L1's PTCR size, finds or allocates a `kvm_nested_guest`, allocates a shadow radix pgtable and shadow LPID, preallocates the IDR slot, installs with refcounts under `kvm->mmu_lock`, and releases unused races. `kvmhv_flush_nested()` frees shadow PTEs, flushes the shadow LPID, reloads L1 partition table state, and removes the nested guest if L1 no longer has a usable table entry. `kvmhv_release_all_nested()` removes all IDR entries and frees memslot nested rmaps when a VM is destroyed or switched away from radix nested mode.

The nested fault path is `kvmhv_nested_page_fault()` -> `__kvmhv_nested_page_fault()`. It refreshes L1 partition-table cache, translates the nested GPA through L1's partition-scoped radix tree with `kvmppc_mmu_walk_radix_tree()`, forwards missing/protection/table faults back to L1 when appropriate, handles DSISR_SET_RC by setting reference/change bits in both L0 and shadow page tables, locates the L1 GPA memslot, emulates MMIO when no memslot backs the target, finds or instantiates the L0 host PTE, combines L0 and L1 permissions, chooses a page size not larger than either mapping, allocates a nested rmap entry, and inserts the shadow PTE with `kvmppc_create_pte()`.

TLB invalidation comes through `kvmhv_do_nested_tlbie()` and `do_h_rpt_invalidate_pat()`. The file decodes private radix `tlbie` fields, rejects invalid encodings, invalidates individual nested addresses, one LPID, or all LPIDs, and uses whole-LPID flushes for large ranges above `tlb_range_flush_page_ceiling`.

## State And Persistence Behavior

Persistent VM state includes `kvm->arch.l1_ptcr`, the nested guest IDR, each nested guest's `l1_lpid`, `shadow_lpid`, `shadow_pgtable`, cached L1 guest-real-to-host-real root `l1_gr_to_hr`, process table, `need_tlb_flush`, and refcount. Memslot `arch.rmap` entries persist nested reverse mappings so host page invalidations and dirty/reference changes can propagate into nested shadow page tables. L2 run state is persisted by writing the updated `hv_guest_state` and `pt_regs` back into L1 memory.

The file is careful about lock domains: IDR/refcounts and shadow PTE lookup require `kvm->mmu_lock`, while per-nested-guest page-table and partition-cache operations use `gp->tlb_lock`. SRCU protects reads and writes into guest memory and memslot traversal. Shadow LPID flushing is explicit because stale nested translations can otherwise outlive L1 table changes.

## Dependencies And Integration Points

This file integrates with `book3s_hv.c` for nested fault dispatch, nested vcpu entry, LPCR/HFSCR filtering, and VM teardown; `book3s_64_mmu_radix.c` for radix PTE creation, teardown, and host PTE lookup; pseries firmware hcalls through `plpar_wrappers.h`; nested v2 helpers in `book3s_hv_nestedv2.c`; and KVM memslot/mmu notifier infrastructure through rmap and `mmu_invalidate_seq`. It also depends on POWER radix MMU helpers such as `radix__flush_all_lpid()`, `kvmppc_radix_tlbie_page()`, `__find_linux_pte()`, and `kvmppc_book3s_instantiate_page()`.

## Risks

The highest-risk areas are state filtering on L2 entry, nested rmap lifetime, stale shadow PTE invalidation, and timebase/decrementer conversion. Incorrect LPCR/HFSCR/DAWR/CIABR filtering can expose host or L1-only facilities to L2. Missing rmap cleanup can leave dangling `rmap_nested` entries in memslots; over-aggressive cleanup can lose reference/dirty propagation. The fault path must recheck `mmu_invalidate_seq` and PFN identity to avoid installing stale mappings. The nested MMIO path rewrites `io_gpr` to `KVM_MMIO_REG_NESTED_GPR`, so regressions there can corrupt L1's saved L2 register image.

## Test Signals

Useful signals include booting an L1 KVM guest that can run L2 guests with radix enabled, exercising `H_ENTER_NESTED` with big and little endian L1s, nested MMIO loads and stores, L2 migration-like state save/restore, L1 `H_SET_PARTITION_TABLE` changes, L2 page faults across 4K/PMD/PUD backed mappings, memslot deletion while nested mappings exist, `H_TLB_INVALIDATE` and `H_RPT_INVALIDATE` range/all flushes, and dirty-log/reference-bit tests that confirm updates propagate through nested rmap entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_nested.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_nestedv2.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_nestedv2.c

## Purpose

`book3s_hv_nestedv2.c` implements the Book3S HV nested v2 guest-state-buffer interface used when this KVM instance itself runs as a nested guest under a parent hypervisor that supports `H_GUEST_*` hcalls. Instead of directly running L2 through the local real-mode path, it serializes selected vcpu and vcore state into guest state buffers, sends modified guest-wide state to L0, receives lazy state back from L0, and parses `H_GUEST_RUN_VCPU` output.

## Important APIs, Types, And Functions

The file exports the static key `__kvmhv_is_nestedv2`, plus `__kvmhv_nestedv2_mark_dirty()`, `__kvmhv_nestedv2_cached_reload()`, `kvmhv_nestedv2_flush_vcpu()`, `kvmhv_nestedv2_set_ptbl_entry()`, `kvmhv_nestedv2_set_vpa()`, `kvmhv_nestedv2_parse_output()`, `__kvmhv_nestedv2_reload_ptregs()`, `__kvmhv_nestedv2_mark_dirty_ptregs()`, `kvmhv_nestedv2_vcpu_create()`, and `kvmhv_nestedv2_vcpu_free()`.

Important local abstractions are `struct kvmppc_gs_msg_ops`, `struct kvmppc_gs_msg`, `struct kvmppc_gs_buff`, `struct kvmppc_gs_bitmap`, and `struct kvmhv_nestedv2_io`. `config_msg_ops` handles run input/output buffer configuration. `vcpu_message_ops` maps many `KVMPPC_GSID_*` identifiers to and from fields in `struct kvm_vcpu`, `struct pt_regs`, `vcpu->arch.shregs`, vector/floating state, performance counters, and `vcpu->arch.vcore`.

## Control Flow

`kvmhv_nestedv2_vcpu_create()` calls `plpar_guest_create_vcpu()` for the parent hypervisor and then `kvmhv_nestedv2_host_create()` to allocate and register nested v2 buffers. Host creation first queries `KVMPPC_GSID_RUN_OUTPUT_MIN_SIZE`, allocates an output buffer, sends its physical address and size to L0, builds a thread-wide `vcpu_message`, allocates a run input buffer sized from the serialized message, sends that input buffer to L0, then builds a guest-wide `vcore_message`. On success it fills `io->valids`, treating all state as initially cached locally.

Dirty and reload control is bitmap driven. `__kvmhv_nestedv2_mark_dirty()` includes a GSID in both vcpu and vcore messages and marks it valid locally. `__kvmhv_nestedv2_cached_reload()` only issues a receive hcall when the GSID is not valid in `io->valids`, using flags from `kvmppc_gsid_flags()` to request the correct scope. `kvmhv_nestedv2_flush_vcpu()` sends guest-wide dirty elements first, resets and fills the run input buffer with thread-wide dirty state, and always appends `KVMPPC_GSID_HDEC_EXPIRY_TB` for the requested run time limit.

`gs_msg_ops_vcpu_fill_info()` is the outbound serializer. It iterates requested GSIDs, skips entries whose requested wide/non-wide flag does not match the element scope, and writes scalar, GPR, SPR, vector, PMU, DEC expiry, TB offset, LPCR, VTB, DPDES, and logical PVR values. `gs_msg_ops_vcpu_refresh_info()` is the inbound parser. It parses a GSB into elements, writes recognized values into vcpu/vcore fields, and sets validity bits for each refreshed GSID. `kvmhv_nestedv2_parse_output()` clears fault/emulation defaults before parsing the output buffer so absent output fields do not preserve stale fault state.

Partition table updates use `kvmhv_nestedv2_set_ptbl_entry()`, which converts raw PATE doublewords into `kvmppc_gs_part_table` and `kvmppc_gs_proc_table` records and sends them wide to L0. VPA registration uses `kvmhv_nestedv2_set_vpa()` to send a `KVMPPC_GSID_VPA` datum through the run input buffer.

## State And Persistence Behavior

Persistent per-vcpu state lives in `vcpu->arch.nestedv2_io`: configuration records, input and output guest-state buffers, vcpu and vcore messages, and validity bits. The validity bitmap is a local cache contract: a set bit means local `vcpu->arch` has the current value; a clear bit lets accessors lazily fetch from L0. Dirty messages persist across changes until flushed. Buffer physical addresses and sizes are registered with L0 and must remain valid until `kvmhv_nestedv2_vcpu_free()`.

## Dependencies And Integration Points

This file is enabled by `kvmhv_nested_init()` after successful pseries capability negotiation. It integrates with inline accessors in `book3s_hv.h`, the nested vcpu run path in `book3s_hv.c`, VPA registration in the Book3S HV core, and partition-table updates from `book3s_hv_nested.c`. It depends heavily on `asm/guest-state-buffer.h` helpers for sizing, parsing, and sending GSB data, and on pseries `plpar_guest_create_vcpu()` and related GSB hcalls.

## Risks

The main risks are GSID coverage gaps, scope mismatches between thread-wide and guest-wide state, stale validity bits, and buffer lifetime errors. Missing a GSID in fill or refresh can produce state loss only under nested v2, which is hard to detect on bare metal. `gs_msg_ops_vcpu_get_size()` excludes host-wide and configuration elements; mistakes there can under-size buffers. Logical PVR defaults are synthesized from CPU features when `arch_compat` is zero, so compatibility tests should cover POWER9, POWER10, and POWER11 feature combinations. Error paths in host creation must free partially allocated messages and buffers without leaving L0 configured with freed addresses.

## Test Signals

Useful tests include nested v2 boot on pseries, vcpu create/free failure injection, dirty/reload accessors for GPRs, MSR, LPCR, PMU, vector, and DEC expiry GSIDs, VPA register/unregister, L2 exits that return HDAR/HDSISR/ASDR/HEIR, logical PVR propagation, partition/process table changes, and repeated vcpu run loops that verify no stale fault fields survive an output buffer that omits them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_nestedv2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_p9_entry.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_p9_entry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_p9_perf.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_p9_perf.c

## Purpose

`book3s_hv_p9_perf.c` isolates POWER9 and later performance monitor state across KVM-HV guest entry and exit. It freezes PMU counters before switching ownership, saves host counters when the host is using the PMU, loads guest counters only when requested or demand-enabled, and restores host counters after guest exit.

## Important APIs, Types, And Functions

The file exports `switch_pmu_to_guest()` and `switch_pmu_to_host()`. The local helper `freeze_pmu()` forces MMCR0/MMCRA into a frozen, non-sampling state, with ARCH_31 handling for `MMCR0_PMCCEXT` and `MMCRA_BHRB_DISABLE`. State is stored in `struct p9_host_os_sprs`, `vcpu->arch.pmc[]`, `vcpu->arch.mmcr[]`, `vcpu->arch.mmcra`, `vcpu->arch.siar`, `vcpu->arch.sdar`, and `vcpu->arch.sier[]`.

## Control Flow

On guest entry, `switch_pmu_to_guest()` checks the pinned VPA/lppaca `pmcregs_in_use` flag to decide whether the guest requested PMU preservation. If the host currently uses the PMU (`ppc_get_pmu_inuse()`), it saves host MMCR0/MMCRA, freezes the PMU, and then saves all PMCs, MMCR1/MMCR2, SDAR, SIAR, SIER, and ARCH_31 MMCR3/SIER2/SIER3. On pseries it mirrors the selected PMU ownership into the host lppaca `pmcregs_in_use`. It loads guest PMU registers when `load_pmu` is true or HFSCR[PM] is already enabled from a previous PMU facility fault, writing MMCRA before MMCR0 last. For non-nested guests it sets HFSCR[PM] when the PM facility is permitted.

On guest exit, `switch_pmu_to_host()` again checks guest VPA `pmcregs_in_use`, with an optional nested PMU workaround that forces saving for nesting-capable guests. If saving is required, it captures guest MMCR0/MMCRA, freezes counters, and saves the full PMU state into `vcpu->arch`. If saving is not requested but HFSCR[PM] is set, it freezes whatever the guest touched and clears HFSCR[PM] for non-nested guests to demand-fault future access. It then restores pseries host lppaca PMU ownership and, if the host uses PMU, reloads host PMC/MMCR/SIAR/SDAR/SIER state and finally MMCRA/MMCR0.

## State And Persistence Behavior

Guest PMU state persists only when the guest declares PMU use or the nested workaround requires it. Otherwise KVM uses HFSCR[PM] demand faulting to avoid saving every counter on every exit. Host PMU state is transiently stored in `p9_host_os_sprs` across the entry call. The pseries lppaca PMU-use flag is updated on both sides so the parent environment sees accurate PMU ownership.

## Dependencies And Integration Points

This file is called directly by `kvmhv_vcpu_entry_p9()` before and after `kvmppc_p9_enter_guest()`. It depends on `asm/pmc.h`, SPR accessors, CPU feature bits, lppaca/VPA state, HFSCR[PM], pseries detection through `kvmhv_on_pseries()`, and the optional `CONFIG_KVM_BOOK3S_HV_NESTED_PMU_WORKAROUND`.

## Risks

Risk centers on counter leakage, lost PMU alerts, and nested guest accounting. Loading guest PMU state when not needed wastes time, but failing to save when needed loses guest-visible counter values. Freezing must happen before reading counters to avoid races. The nested workaround exists because older L1s may mishandle `pmcregs_in_use`; removing or changing it can regress nested PMU correctness. ARCH_31 BHRB and extended counter controls must stay aligned with hardware behavior.

## Test Signals

Useful tests include guests that never use PMU, guests that set lppaca `pmcregs_in_use`, guests that touch PMU registers without declaring use and fault through HFSCR[PM], host perf running while a guest runs, nested PMU workloads, and POWER10/POWER11 systems covering MMCR3 and SIER2/SIER3 save/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_p9_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_ras.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_ras.c

## Purpose

`book3s_hv_ras.c` contains real-mode reliability, availability, and serviceability handlers for Book3S HV KVM. It handles guest machine checks and hypervisor maintenance interrupts, especially SLB/TLB recovery on POWER7-era systems and timebase/HMI coordination across split subcores. It also provides POWER9-specific HMI handling for the C P9 entry path.

## Important APIs, Types, And Functions

Important functions are `kvmppc_realmode_machine_check()`, `kvmppc_p9_realmode_hmi_handler()`, `kvmppc_subcore_enter_guest()`, `kvmppc_subcore_exit_guest()`, and `kvmppc_realmode_hmi_handler()`. Local helpers include `reload_slb()`, `kvmppc_realmode_mc_power7()`, `kvmppc_cur_subcore_size()`, `kvmppc_tb_resync_required()`, and `kvmppc_tb_resync_done()`. The file uses `struct machine_check_event`, PACA sibling subcore state, OPAL HMI/timebase hooks, and the vcore timebase offset fields.

## Control Flow

For machine checks, `kvmppc_realmode_machine_check()` either lets FWNMI guests handle recovery or calls `kvmppc_realmode_mc_power7()` to recover known SLB parity/multihit, DERAT multihit, and TLB multihit conditions. It then retrieves the machine-check event with `get_mce_event(MCE_EVENT_RELEASE)`, marks it recovered when appropriate, and stores it in `vcpu->arch.mce_evt` for virtual-mode completion.

`kvmppc_p9_realmode_hmi_handler()` is used by the P9 C entry path. It first unapplies any guest timebase offset so OPAL/debug handling observes host-relative time. It counts the HMI, lets `hmi_handle_debugtrig()` consume debug-trigger HMIs, calls `ppc_md.hmi_exception_early()` when available, and reapplies the guest timebase offset before returning.

The older `kvmppc_realmode_hmi_handler()` coordinates HMI handling across subcores. The primary thread sets a shared resync-required bit, clears its subcore guest state, waits for all sibling subcores to leave guest context, calls OPAL's early HMI handler, has one elected thread perform `opal_resync_timebase()`, and makes all others wait until resync is complete. It clears `tb_offset_applied` so the guest exit path does not subtract an already-resynchronized guest offset.

## State And Persistence Behavior

Persistent outputs are the stored machine check event in `vcpu->arch.mce_evt`, PACA `hmi_irqs`, sibling subcore `in_guest[]` and `flags`, and vcore `tb_offset_applied`. `kvmppc_subcore_enter_guest()` and `_exit_guest()` update shared subcore state that the HMI handler uses to decide when it is safe to resynchronize a whole core. SLB reload uses a pinned guest SLB shadow buffer when present, but only after bounds checks against `pinned_end`.

## Dependencies And Integration Points

This file is called from both `book3s_hv_p9_entry.c` and `book3s_hv_rmhandlers.S` for machine check and HMI exits. It integrates with OPAL (`opal_resync_timebase()`), platform HMI callbacks (`ppc_md.hmi_exception_early`), machine-check event retrieval, PACA sibling subcore state, and KVM's vcore timebase-offset machinery.

## Risks

Timebase resynchronization is the main risk: resync is core-wide, so doing it while a sibling subcore is still in guest context can corrupt guest time. Conversely, failing to clear `tb_offset_applied` can double-subtract offsets. Machine-check recovery must only report recoverable conditions when all remaining status bits are understood. Real-mode execution limits available services, so event queuing is deferred through vcpu state rather than normal host queues.

## Test Signals

Signals include injected machine checks for SLB/TLB multihit and unrecoverable cases, FWNMI guest behavior, HMI debug-trigger handling, OPAL HMI callbacks, split-core/subcore guest runs with concurrent HMI, timebase offset guests, and verifying that `vcpu->arch.mce_evt` reaches virtual-mode handling with the expected disposition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_ras.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_rm_mmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_rm_mmu.c

## Purpose

`book3s_hv_rm_mmu.c` implements real-mode and low-level hash page table MMU support for Book3S HV KVM. It services HPT hypercalls, maintains reverse mappings between guest HPTEs and memslots, performs TLB invalidation with POWER9 errata workarounds, initializes pages in real mode, and triages HPTE faults into guest reflection, retry, MMIO emulation, or virtual-mode handling.

## Important APIs, Types, And Functions

Exported functions include `kvmppc_add_revmap_chain()`, `kvmppc_update_dirty_map()`, `kvmppc_do_h_enter()`, `kvmppc_h_enter()`, `kvmppc_do_h_remove()`, `kvmppc_h_remove()`, `kvmppc_h_bulk_remove()`, `kvmppc_h_protect()`, `kvmppc_h_read()`, `kvmppc_h_clear_ref()`, `kvmppc_h_clear_mod()`, `kvmppc_rm_h_page_init()`, `kvmppc_invalidate_hpte()`, `kvmppc_clear_ref_hpte()`, `kvmppc_hv_find_lock_hpte()`, and `kvmppc_hpte_hv_fault()`.

Important local helpers are `real_vmalloc_addr()`, `global_invalidates()`, `kvmppc_set_dirty_from_hpte()`, `revmap_for_hpte()`, `remove_revmap_chain()`, `is_mmio_hpte()`, `fixup_tlbie_lpid()`, `do_tlbies()`, `kvmppc_get_hpa()`, page-zero/copy helpers, and the MMIO HPTE cache helpers. Core state lives in `kvm->arch.hpt`, `struct revmap_entry`, memslot `arch.rmap`, `vcpu->arch.mmio_cache`, and `vcpu->arch.pgfault_*`.

## Control Flow

`kvmppc_do_h_enter()` validates HPT mode, page-size encoding, storage size bits, and target HPTE slot. It locates the backing memslot, obtains a host PTE under the raw MMU lock, computes the real HPTE from host PA and guest-requested protection, marks emulated MMIO as absent with storage key 31, finds or locks an HPTEG slot, records the guest RPTE in the revmap entry, links the HPTE into the memslot rmap unless an invalidation raced, converts HPTE format on POWER9, writes the second HPTE word, then unlocks by writing the first word.

Remove/protect/read/clear hypercalls operate directly on locked HPTEs. `kvmppc_do_h_remove()` invalidates valid HPTEs, performs TLB invalidation, rereads R/C bits, removes the revmap chain, returns guest-format HPTE values, and bumps `mmio_update` for MMIO HPTEs. `kvmppc_h_bulk_remove()` batches up to four removals before issuing TLB invalidations. `kvmppc_h_protect()` updates guest-visible protection and invalidates before changing a valid HPTE. `kvmppc_h_clear_ref()` and `kvmppc_h_clear_mod()` clear R/C bits while preserving dirty logging and rmap reference state.

`kvmppc_hpte_hv_fault()` is called from real-mode HDSI/HISI handlers. It searches the HPT, optionally using the per-vcpu MMIO HPTE cache, checks whether a not-found fault should retry because the HPTE became valid, validates read/write/execute and storage-key permissions against the guest RPTE and SLB key, saves HPTE metadata for virtual-mode handling, caches MMIO HPTEs, returns `-2` when instruction fetch is needed for MMIO data emulation, returns `-1` for host handling, `0` for retry, or a modified DSISR/SRR1 value to reflect to the guest.

## State And Persistence Behavior

The HPT and revmap structures persist guest translations. `rev->guest_rpte` stores the guest's view of the HPTE low word independent of host-enforced read-only or absent bits. Memslot rmap entries store the head of HPTE reverse chains plus accumulated R/C/reference state. Dirty logging is persisted in memslot dirty bitmaps. `kvm->arch.mmio_update` invalidates cached MMIO HPTE entries when MMIO HPTEs are changed. `kvm->arch.need_tlb_flush` records CPUs that need local flushes when `tlbiel` is used instead of global `tlbie`.

## Dependencies And Integration Points

This file backs the real-mode hcall table in `book3s_hv_rmhandlers.S` and virtual-mode paths in `book3s_hv.c`. It depends on HPT helpers from `asm/book3s/64/mmu-hash.h`, KVM memslot APIs, host PTE lookup, raw MMU locks, POWER tlbie/tlbiel instructions, HPTE old/new format conversion for POWER9, and guest fault reflection code in the assembly handlers.

## Risks

Risks include real-mode access to vmalloc-backed arrays, HPTE locking races, lost R/C bits, dirty-log omissions, stale local TLB entries, MMIO cache staleness, and incorrect HPTE format conversion on POWER9. `global_invalidates()` trades global flushes for per-core flush debt only when a single vcore is running; mistakes there can leave stale translations. `kvmppc_get_hpa()` and page-init helpers run under raw locks and must not fault or sleep.

## Test Signals

Signals include HPT guests issuing `H_ENTER`, `H_REMOVE`, `H_BULK_REMOVE`, `H_PROTECT`, `H_READ`, `H_CLEAR_REF`, `H_CLEAR_MOD`, and `H_PAGE_INIT`, dirty logging with HPT mappings, MMIO through absent key-31 HPTEs, hugepage and base-page combinations, concurrent memslot invalidation, local versus global TLB invalidation, POWER9 HPTE format systems, and guest storage-key faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_rm_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_rm_xics.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_rm_xics.c

## Purpose

`book3s_hv_rm_xics.c` implements real-mode XICS interrupt-controller handling for Book3S HV KVM. It lets common interrupt hcalls and pass-through MSI delivery complete without exiting to virtual mode when state is simple, while flagging `H_TOO_HARD` when host work, debugging, notifier callbacks, or vcpu kicking cannot safely be handled in real mode.

## Important APIs, Types, And Functions

Global tunables are `h_ipi_redirect` and `kvm_irq_bypass`. Key functions are `xics_rm_h_xirr_x()`, `xics_rm_h_xirr()`, `xics_rm_h_ipi()`, `xics_rm_h_cppr()`, `xics_rm_h_eoi()`, `kvmppc_deliver_irq_passthru()`, and `kvmppc_xics_ipi_action()`. Local helpers include `ics_rm_check_resend()`, `icp_send_hcore_msg()`, `grab_next_hostcore()`, `find_available_hostcore()`, `icp_rm_set_vcpu_irq()`, `icp_rm_clr_vcpu_irq()`, `icp_rm_try_update()`, `icp_rm_try_to_deliver()`, `icp_rm_deliver_irq()`, `icp_rm_down_cppr()`, `ics_rm_eoi()`, `icp_eoi()`, and real-mode per-CPU IRQ stat updating.

The main types are `struct kvmppc_xics`, `struct kvmppc_icp`, `union kvmppc_icp_state`, `struct kvmppc_ics`, `struct ics_irq_state`, `struct kvmppc_irq_map`, and `struct kvmppc_passthru_irqmap`.

## Control Flow

Interrupt delivery starts in `icp_rm_deliver_irq()`. It finds the ICS and IRQ source, locks the ICS, resolves the target ICP if the interrupt moved servers, handles resend filtering, marks masked interrupts as `masked_pending`, tries to deliver by atomically replacing ICP `xisr` and `pending_pri`, and handles rejected interrupts by recursively retrying delivery. Failed delivery marks source `resend`, updates the ICP resend bitmap, and retries if the ICP `need_resend` flag was cleared in the race window.

`xics_rm_h_xirr()` clears the vcpu external interrupt indication, atomically accepts the current pending interrupt by returning XISR|CPPR in GPR4, sets CPPR to the pending priority, and clears `xisr`. `xics_rm_h_ipi()` updates MFRR, may replace the pending interrupt with XICS_IPI, handles rejected interrupts and resend checks, and returns `H_TOO_HARD` if real-mode deferred work accumulated. `xics_rm_h_cppr()` raises or lowers CPPR, clearing local interrupt output when raising priority and invoking `icp_rm_down_cppr()` when lowering priority may expose resends or IPIs. `xics_rm_h_eoi()` lowers CPPR based on XIRR, skips ICS EOI for IPIs, and for real IRQs advances LSI/MSI PQ state, redelivers if needed, records EOI notifiers as deferred actions, and adjusts pass-through affinity through OPAL if host IRQ affinity no longer matches the guest core.

Pass-through delivery in `kvmppc_deliver_irq_passthru()` updates IRQ stats in real mode, converts the real interrupt to a virtual hwirq, atomically updates MSI PQ state, delivers to the ICP when P transitions to presented, EOIs the real interrupt through OPAL or XICS MMIO, and returns either direct-delivery status or a host-completion request.

## State And Persistence Behavior

ICP state is a 64-bit atomic state machine containing CPPR, MFRR, XISR, pending priority, output EE, and need-resend. ICS state persists per-source priority, server, resend, masked-pending, LSI/MSI PQ state, host IRQ, and interrupt CPU. Vcpu state records pending external exceptions, stats, and deferred real-mode actions in `icp->rm_action`, `rm_kick_target`, and `rm_eoied_irq`. Host-core redirection uses `kvmppc_host_rm_ops_hv->rm_core[]` state and data until `kvmppc_xics_ipi_action()` runs in host context.

## Dependencies And Integration Points

The real-mode hcall table in `book3s_hv_rmhandlers.S` calls the XICS hcall handlers. Completion of deferred operations is handled by virtual-mode XICS code in `book3s_xics.c`. The file integrates with OPAL interrupt calls, PowerNV PCI MSI EOI, host IPI machinery, KVM vcpu kick callbacks, irq descriptors/statistics, and the Book3S XICS data structures declared in `book3s_xics.h`.

## Risks

The atomic ICP transitions are race-sensitive. Incorrect ordering around `resend`, `resend_map`, and `need_resend` can lose interrupts. Real-mode cannot safely perform all host actions, so missing an `H_TOO_HARD` condition can execute unsafe work in real mode, while excessive `H_TOO_HARD` harms latency. Pass-through EOI and affinity adjustment can misroute interrupts if `intr_cpu` or OPAL server updates are wrong. Per-CPU stat increments handle vmalloc per-CPU storage manually, which is architecture-sensitive.

## Test Signals

Signals include XICS guests issuing `H_XIRR`, `H_XIRR_X`, `H_IPI`, `H_CPPR`, and `H_EOI` in real mode, interrupt rejection/resend storms, masked MSI and LSI sources, vcpu kick redirection when a target vcpu is not loaded, irq ack notifier fallback, pass-through MSI delivery and EOI, host IPI completion through `kvmppc_xics_ipi_action()`, and real-mode debug forcing `H_TOO_HARD`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_rm_xics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_rmhandlers.S -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_rmhandlers.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_tm.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_tm.c

## Purpose

`book3s_hv_tm.c` emulates selected transactional memory instructions for POWER9 DD2.2 softpatch interrupts. It handles cases where hardware TM behavior requires KVM to synthesize state transitions, facility-unavailable exceptions, illegal-instruction exceptions, transaction failure state, checkpoint copying, and rollback-like effects in vcpu state.

## Important APIs, Types, And Functions

The exported function is `kvmhv_p9_tm_emulation()`. The local helper `emulate_tx_failure()` synthesizes TEXASR and TFIAR failure state. The function uses instruction opcode constants for `rfid`, `rfebb`, `mtmsrd`, `tsr`, `treclaim`, and `trechkpt`, plus helpers such as `sanitize_msr()`, `kvmppc_get_gpr()`, `kvmppc_core_queue_program()`, `kvmppc_book3s_queue_irqprio()`, `copy_from_checkpoint()`, and `copy_to_checkpoint()`.

## Control Flow

`kvmhv_p9_tm_emulation()` receives the faulting instruction in `vcpu->arch.emul_inst`. Because the softpatch interrupt advances NIP past the instruction, it first subtracts four to reconstruct normal synchronous-interrupt semantics. It masks instructions with `PO_XOP_OPCODE_MASK`, intentionally ignoring bit 31 for TM instructions whose invalid forms can also produce the softpatch.

For `rfid` and `mtmsrd`, it checks for suspended-to-transactional transitions, sanitizes the target MSR, updates guest MSR and NIP/CFAR as appropriate, and resumes the guest. For `rfebb`, it enforces PR/PCR and EBB facility availability, queues illegal or facility-unavailable interrupts when needed, updates BESCR[GE], transitions TM state from suspended to transactional, and branches to EBBRR.

For `tsr`, it checks privilege/architecture and TM facility availability, records previous transactional state in CR0, and performs suspend or resume depending on the L bit. For `treclaim`, it verifies TM availability and active transaction state, optionally synthesizes failure state from RA, copies checkpointed state back into active state, records prior state in CR0, clears MSR TS bits, and advances NIP. For `trechkpt`, it requires TM enabled, no active transaction, and TEXASR[FS] set, copies active state to checkpoint, records CR0 state, sets suspended state, and advances NIP. Unknown instructions queue a program illegal interrupt and emit a rate-limited warning.

## State And Persistence Behavior

The function updates `vcpu->arch.shregs.msr`, `vcpu->arch.regs.nip`, `vcpu->arch.cfar`, `vcpu->arch.regs.ccr`, `vcpu->arch.texasr`, `vcpu->arch.tfiar`, `vcpu->arch.tfhar` indirectly through checkpoint helpers, `vcpu->arch.fscr`, `vcpu->arch.hfscr`, and `vcpu->arch.trap`. It preserves TEXASR ROT/TL bits when synthesizing failure state. It returns either `RESUME_GUEST` for fully handled emulation or `-1` to rerun host interrupt handling for hypervisor facility unavailable cases.

## Dependencies And Integration Points

This file is called from the POWER9 entry/exit handling in `book3s_hv_p9_entry.c` and virtual-mode exit handling in `book3s_hv.c`. It complements the TM save/restore assembly in `book3s_hv_rmhandlers.S` and the early TM softpatch handling in `book3s_hv_tm_builtin.c`. It depends on Book3S interrupt queuing, MSR sanitization, TM checkpoint copy helpers, and HFSCR/FSCR facility cause encodings.

## Risks

TM state transitions are subtle. Incorrect NIP rewind/advance can re-execute or skip an instruction. Wrong MSR TS transitions can produce TM bad-thing behavior or fail to emulate hardware. Facility checks must distinguish hypervisor facility unavailable from guest facility unavailable. `treclaim` and `trechkpt` must copy checkpoint state in the correct direction and preserve CR0/TEXASR semantics. The bit-31 masking behavior is intentional and should not be simplified without hardware validation.

## Test Signals

Signals include POWER9 DD2.2 TM softpatch tests for `rfid`, `rfebb`, `mtmsrd`, `tsr`, `treclaim`, and `trechkpt`; PR and HV privilege combinations; HFSCR/FSCR TM and EBB disabled cases; active, suspended, and non-transactional MSR states; TEXASR[FS] set and clear; RA failure-cause generation; and unknown TM-related instruction warning paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_tm.c -->
