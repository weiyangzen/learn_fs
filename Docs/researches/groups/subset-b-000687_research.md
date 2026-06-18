# subset-b-000687 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/nested.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/nested.c

Purpose: implements arm64 KVM nested virtualization support for virtual EL2. It manages shadow stage-2 MMU contexts for L1 guest hypervisors, walks guest stage-2 page tables, translates and caches L1 `VNCR_EL2` mappings, reacts to nested TLBI and MMU notifier events, limits ID register exposure for nested guests, applies RES0/RES1 masks to virtual EL2 system registers, and synchronizes nested exception/debug/PMU-related state around guest entry and exit.

Important APIs and types: `struct vncr_tlb` caches a single translated guest `VNCR_EL2` VA, stage-1 walk metadata, resulting HPA, owning CPU fixmap, and validity. `struct s2_walk_info` captures decoded VTCR/VTTBR stage-2 walk parameters. Major entry points include `kvm_init_nested()`, `kvm_vcpu_init_nested()`, `kvm_walk_nested_s2()`, `compute_tlb_inval_range()`, `kvm_s2_mmu_iterate_by_vmid()`, `lookup_s2_mmu()`, `kvm_vcpu_load_hw_mmu()`, `kvm_vcpu_put_hw_mmu()`, `kvm_s2_handle_perm_fault()`, `kvm_inject_s2_fault()`, `kvm_handle_s1e2_tlbi()`, `kvm_nested_s2_wp()`, `kvm_nested_s2_unmap()`, `kvm_arch_flush_shadow_all()`, `kvm_vcpu_allocate_vncr_tlb()`, `kvm_handle_vncr_abort()`, `limit_nv_id_reg()`, `kvm_vcpu_apply_reg_masks()`, `kvm_init_nv_sysregs()`, `check_nested_vcpu_requests()`, `kvm_nested_flush_hwstate()`, `kvm_nested_sync_hwstate()`, and `kvm_nested_setup_mdcr_el2()`.

Control flow: VM setup initializes an empty nested-MMU pool and per-VM VNCR mapping count. VCPU nested initialization validates feature combinations, allocates the per-vCPU VNCR register page, resizes the VM-wide `nested_mmus` array to `online_vcpus * S2_MMU_PER_VCPU`, and initializes new stage-2 MMUs. When a vCPU enters a nested context, `kvm_vcpu_load_hw_mmu()` either uses the canonical VM MMU for hyp context or obtains a matching/reusable nested MMU keyed by virtual VMID, VTTBR, VTCR, and whether nested stage-2 is enabled. Reused valid MMUs are marked for pending unmap before being retagged. Requests later drain pending unmaps and VNCR mappings before guest execution.

The nested stage-2 walker decodes VTCR into `s2_walk_info`, validates input/output address-size constraints, reads L1 descriptors through `kvm_read_guest()`, handles guest endianness, optionally atomically sets AF when VTCR.HA is enabled, and returns either a translated output PA plus permissions/level/block size or an ESR fault code matching the failing level. Permission faults are forwarded to L1 only when the shadow translation lacks the access requested by the L2 trap.

State and persistence: persistent VM state lives in `kvm->arch.nested_mmus`, `nested_mmus_size`, `nested_mmus_next`, `sysreg_masks`, debugfs nested ptdump dentries, and `vncr_map_count`. Persistent vCPU state includes `ctxt.vncr_array`, `arch.vncr_tlb`, `arch.hw_mmu`, nested request flags, virtual EL2 sysregs, and SError bookkeeping. Shadow MMUs hold cached `tlb_vttbr`, `tlb_vtcr`, `nested_stage2_enabled`, `pending_unmap`, and refcounts. VNCR fixmap mappings are per-CPU transient and are dropped unconditionally on vCPU put.

Dependencies and integration: depends on arm64 system register definitions, `asm/kvm_nested.h`, stage-2 MMU helpers from `mmu.c`, page-table helpers, KVM SRCU and `mmu_lock`, TLBI opcode decoding, `__kvm_translate_va()` for EL2 stage-1 walks, memslot/gmem fault-in APIs, debugfs ptdump creation, VGIC feature state, and sysreg fixed-bit helpers from `sys_regs.c`. It integrates with MMU notifiers through nested S2 invalidation, with guest entry through hardware MMU load/put, with exit handling through nested abort and request processing, and with PMU/debug routing via `MDCR_EL2` setup.

Risks: this file is concurrency-sensitive. Nested MMU lookup/reuse requires `mmu_lock` discipline and correct refcount management; stale `pending_unmap` state can expose old shadow mappings. The stage-2 descriptor walker must exactly match architectural translation fault levels, endianness, AF handling, contiguous hints, and output-size constraints. VNCR caching is deliberately a one-entry pseudo-TLB, so TLBI range decoding, ASID matching, MMU notifier invalidation, and fixmap CPU ownership are high-risk. Guest-memory-backed VNCR paths can return to userspace on gmem faults, while regular memslot paths inject to L1, so error-code handling must remain precise. ID register limiting and RES0/RES1 masks are also architectural ABI: exposing unsupported nested features can let L1 program state that KVM cannot emulate.

Test signals: useful signals include KVM selftests that create nested arm64 guests, exercise L1 stage-2 faults, permission faults, TLBI by VMID/VA/ASID/range, VNCR access under NV2, migration/reset of nested sysregs, and SError routing. Runtime diagnostics include nested stage-2 debugfs ptdumps, lockdep around `mmu_lock`, WARNs in invalid translation limits and refcount-free teardown, and gmem fault exits for VNCR pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/nested.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/pauth.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/pauth.c

Purpose: provides narrowly scoped pointer-authentication emulation for nested guest hypervisor `ERETAA` and `ERETAB` handling. It authenticates the virtual EL2 return address in `ELR_EL2` using the guest's instruction pointer authentication keys and updates the return address to either a canonical authenticated VA or an architecturally corrupted failure value.

Important APIs and functions: `kvm_auth_eretax()` is the exported entry point. Internal helpers are `compute_pac()`, which temporarily installs a guest key into `APGAKEY_EL1` and executes `PACGA`; `effective_tbi()`, which determines whether top-byte-ignore applies for the relevant TTBR half; `compute_bottom_pac()` and `compute_pac_mask()`, which derive the PAC bit mask from TCR_EL2 translation size and TBI/TBID; `to_canonical_addr()`, which sign/canonicalizes around the PAC mask; and `corrupt_addr()`, which produces the failure encoding when FEAT_PAuth2 is absent.

Control flow: `kvm_auth_eretax()` reads `SCTLR_EL2`, ESR, and `ELR_EL2`. It selects APIA or APIB based on whether ESR identifies `ERETAA` or `ERETAB`, and bypasses authentication if the relevant enable bit is clear. It computes the PAC mask from the candidate pointer, canonicalizes the address, calculates the PAC using the guest key and SP modifier, and compares masked PAC bits with the signed pointer. On success it returns `true` and stores the canonical pointer in `*elr`. On failure it either corrupts the canonical address with the ERETAA/ERETAB error code or XORs the PAC into the pointer for PAuth2, stores the failed address in `*elr`, and returns `false`.

State and persistence: this file does not own persistent VM state. It reads guest virtual EL2 sysregs and PAuth key sysregs. `compute_pac()` briefly disables preemption, saves the host APGA key, installs the guest key without synchronization, runs the PAC instruction, and restores the host key before reenabling preemption. The only durable output is the caller-provided `*elr`.

Dependencies and integration: depends on arm64 pointer-authentication helpers, KVM vCPU sysreg accessors, ESR ERETAx decoding, `vcpu_el2_e2h_is_set()`, and `kvm_has_pauth()`. It is intended for nested-virt ERETAx emulation while already running in the right EL2/KVM context; the source explicitly warns against reuse elsewhere.

Risks: the implementation relies on architectural shortcuts and host hardware PAuth behavior. Preemption and key restore ordering are critical because it writes real APGA key registers. The PAC mask assumes current translation-size limits and comments that TTST/LVA/LVA2 may require revisiting. TBI/TBID interpretation differs for E2H and VA[55], so corner cases with malformed guest pointers can be subtle. Failure address corruption must match exception behavior expected by the caller, which remains responsible for any exception injection.

Test signals: nested ERETAx tests should cover APIA/APIB enable disabled/enabled, E2H and non-E2H TBI/TBID configurations, addresses in both VA[55] halves, valid PAC success, invalid PAC failure with and without PAuth2, and preservation of host pointer-auth keys across preemption-sensitive paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/pauth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/pkvm.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/pkvm.c

Purpose: implements host-side protected KVM setup and pKVM stage-2 mediation. It reserves hypervisor-private memory during boot, finalizes host protection, creates and destroys protected or shared hypervisor VM/vCPU objects, and forwards guest stage-2 map/unmap/permission/aging/cache operations to the nVHE hypervisor while tracking host-owned mapping metadata in an interval tree.

Important APIs and types: global state includes `kvm_protected_mode_initialized`, `hyp_memory`, `hyp_memblock_nr_ptr`, `hyp_mem_base`, and `hyp_mem_size`. VM lifecycle functions include `kvm_hyp_reserve()`, `pkvm_init_host_vm()`, `pkvm_create_hyp_vm()`, `pkvm_create_hyp_vcpu()`, `pkvm_destroy_hyp_vm()`, and `finalize_pkvm()`. Page-table mediation functions include `pkvm_pgtable_stage2_init()`, `pkvm_pgtable_stage2_map()`, `pkvm_pgtable_stage2_unmap()`, `pkvm_pgtable_stage2_destroy_range()`, `pkvm_pgtable_stage2_destroy_pgd()`, `pkvm_pgtable_stage2_wrprotect()`, `pkvm_pgtable_stage2_flush()`, `pkvm_pgtable_stage2_test_clear_young()`, `pkvm_pgtable_stage2_relax_perms()`, `pkvm_pgtable_stage2_mkyoung()`, and `pkvm_force_reclaim_guest_page()`. `struct pkvm_mapping` entries are managed by an interval tree over guest frame ranges.

Control flow: early boot calls `kvm_hyp_reserve()` only when EL2 is available, the kernel is not already in hyp mode, and KVM is configured for protected mode. It records memblock regions for hyp, computes page needs for hyp S1, host S2, VM tables, vmemmap, selftests, and FFA proxy, then reserves aligned physical memory. `finalize_pkvm()` later removes hyp memory from kmemleak visibility and runs `__pkvm_prot_finalize` on every CPU, enabling the static key before host stage-2 isolation becomes immutable.

VM creation first reserves a hyp VM handle, marks protected VMs as experimental/tainted, allocates host pages for hyp VM/vCPU structures and the stage-2 PGD, donates them to hyp via `kvm_call_hyp_nvhe()`, and tracks finalized state under `config_lock` and sometimes `slots_lock`. Destruction finalizes or unreserves hyp VM state, resets handles, and frees teardown memcaches.

State and persistence: pKVM state persists in `kvm->arch.pkvm` fields such as `handle`, `is_created`, `is_protected`, `is_dying`, and teardown memcaches. `kvm_pgtable.pkvm_mappings` persists host-side metadata about pages shared/donated to the protected hypervisor; each entry records GFN, PFN, and page count. Protected VM mappings are page-granular RWX donations; unprotected pKVM mappings can be page or PMD shares. Destroy paths reclaim dirty pinned pages or unshare host mappings and remove interval entries.

Dependencies and integration: relies on nVHE hyp symbols and calls (`__pkvm_*`), memblock, kmemleak, static keys, KVM config and slots locks, stage-2 MMU operations, page pin accounting, `account_locked_vm()`, host cache maintenance, and the pKVM hyp memory cache. It plugs into generic KVM stage-2 operations by replacing software page-table manipulation with hypercalls.

Risks: ownership transitions are the central risk. A failed share/donate/reclaim path can leave pages pinned, inaccessible, dirty-accounted incorrectly, or still represented in the interval tree. Protected VM mapping is intentionally stricter than normal KVM and rejects non-page/RWX mappings. Concurrency with memslot changes and first run is guarded by locks; bypassing those locks risks changing memory layout after hyp state exists. The unimplemented split/create-unlinked/free-unlinked paths WARN, so generic stage-2 callers must not reach them under pKVM.

Test signals: boot with protected KVM should reserve hyp memory and finalize host protection without WARNs. VM tests should cover protected and unprotected pKVM creation, vCPU finalization, memslot teardown, map conflicts returning `-EAGAIN`, forced reclaim, dirty unpin on destroy, write-protect/young/cache flush operations, and rejection of unsupported split/unlinked page-table operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/pkvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/pmu-emul.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/pmu-emul.c

Purpose: emulates the ARM PMUv3 programming model for KVM guests using host perf events. It manages virtual PMU counters, event type registers, overflow state, interrupt delivery, user-visible PMU device attributes, PMU instance selection, event filtering, counter count limits, and nested virtualization interactions for counters reserved to virtual EL2.

Important APIs and functions: public entry points include `kvm_supports_guest_pmuv3()`, `kvm_pmu_evtyper_mask()`, `kvm_pmu_get_counter_value()`, `kvm_pmu_set_counter_value()`, `kvm_pmu_set_counter_value_user()`, `kvm_pmu_vcpu_init()`, `kvm_pmu_vcpu_destroy()`, `kvm_pmu_counter_is_hyp()`, `kvm_pmu_accessible_counter_mask()`, `kvm_pmu_implemented_counter_mask()`, `kvm_pmu_reprogram_counter_mask()`, `kvm_pmu_should_notify_user()`, `kvm_pmu_update_run()`, `kvm_pmu_flush_hwstate()`, `kvm_pmu_sync_hwstate()`, `kvm_pmu_software_increment()`, `kvm_pmu_handle_pmcr()`, `kvm_pmu_set_counter_event_type()`, `kvm_host_pmu_init()`, `kvm_pmu_get_pmceid()`, `kvm_vcpu_reload_pmu()`, `kvm_arm_pmu_v3_enable()`, `kvm_arm_pmu_v3_set_attr()`, `kvm_arm_pmu_v3_get_attr()`, `kvm_arm_pmu_v3_has_attr()`, `kvm_arm_pmu_get_pmuver_limit()`, `kvm_vcpu_read_pmcr()`, and `kvm_pmu_nested_transition()`. Global `arm_pmus` is protected by `arm_pmus_lock`.

Control flow: vCPU initialization assigns counter indexes; PMU device initialization validates VGIC state and IRQ ownership, initializes overflow irq_work, and marks the vCPU PMU created. Userspace can set IRQ, event filters, host PMU type, number of counters, and INIT before the PMU is created or before the VM has run as required. Counter writes release current perf events and recreate them when needed so sample periods track the virtual counter value. Event type writes mask guest-visible bits, reject software/chained events from perf backing, consult filters and host PMU event mapping, then create pinned kernel perf events with EL0/EL1/EL2 exclusion bits derived from guest registers and nested context.

Overflow handling stops the perf event, recomputes the sample period to the next architectural overflow, marks `PMOVSSET_EL0`, propagates chained overflow if possible, requests IRQ delivery, kicks the vCPU or defers through `irq_work` from NMI, and restarts the event. Software increments follow the same counter overflow and chain propagation logic in pure emulation. `kvm_pmu_update_state()` converts overflow plus interrupt-enable state into either VGIC injection or userspace `kvm_run` device IRQ level.

State and persistence: per-vCPU state lives in `vcpu->arch.pmu`, including `pmc[]`, `perf_event` pointers, IRQ number, created flag, IRQ level, and overflow work. VM-wide state includes selected `arm_pmu`, `nr_pmu_counters`, supported CPU mask, and optional `pmu_filter` bitmap. Virtual PMU sysregs store counter values, event types, enables, overflow status, and interrupt enables. Perf events are transient kernel objects that are disabled/released on counter stop, rewrite, vCPU destroy, or reload.

Dependencies and integration: depends on Linux perf, `linux/perf/arm_pmu.h`, ARM PMUv3 event constants, VGIC IRQ routing, KVM device attribute UAPI, KVM requests (`KVM_REQ_RELOAD_PMU`, `KVM_REQ_IRQ_PENDING`), nested virtualization helpers, and host PMU registration from perf drivers. It also calls `kvm_vcpu_pmu_restore_guest()` from `pmu.c` after reprogramming hardware-backed events.

Risks: counter width and overflow semantics are subtle across PMUv3 versions, cycle counter vs event counters, LP/LC bits, and nested `MDCR_EL2.HPMN/HPME/HLP`. Recreating perf events on register changes can lose counts if ordering is wrong. Filters must match PMCEID advertising and event creation. IRQ mode differs for in-kernel VGIC vs userspace IRQ delivery, and PPI/SPI constraints must be consistent across vCPUs. Heterogeneous host PMUs are partially supported but default PMU selection can still produce guest-visible behavior dependent on vCPU scheduling.

Test signals: KVM selftests for `KVM_ARM_VCPU_PMU_V3_*` attributes, vPMU counter access, overflow IRQ delivery, event filtering, PMCEID masking, PMCR reset bits, chained counters, userspace IRQ mode, GICv5 architected PMU IRQ, host PMU selection, counter count limits, and nested EL2 counter reservation provide strong coverage. Runtime signals include `pr_err_once` on perf event creation failure and WARNs on invalid VGIC injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/pmu-emul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/pmu.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/pmu.c

Purpose: handles host hardware PMU context coordination around KVM guest execution, especially VHE systems where host and guest share EL0 PMU access controls. It tracks perf events that need host/guest exclusion switching, toggles EL0 counting filters at vCPU load/put time, preserves host `PMUSERENR_EL0`, and requests resynchronization after interrupt-time PMU changes.

Important APIs and functions: `struct kvm_pmu_events` per-CPU storage is exposed by `kvm_get_pmu_events()`. `kvm_set_pmu_events()` and `kvm_clr_pmu_events()` update host/guest event bitmaps for perf events that need switching. `kvm_vcpu_pmu_restore_guest()` and `kvm_vcpu_pmu_restore_host()` program PMEVTYPER/PMCCFILTR/PMICFILTR EL0 exclusion bits for guest or host. `kvm_set_pmuserenr()` intercepts host writes to PMUSERENR while a VHE guest value is loaded. `kvm_vcpu_pmu_resync_el0()` requests a later guest EL0 restore after interrupt-time changes.

Control flow: perf event setup calls `kvm_set_pmu_events()` with event bits and attributes. `kvm_pmu_switch_needed()` ignores cases not needing different host/guest treatment, including VHE guest-kernel cases where EL0 is already excluded. Guest entry calls `kvm_vcpu_pmu_restore_guest()`, which disables preemption, snapshots per-CPU host/guest masks, enables EL0 counting for guest events, and disables it for host events. Guest exit calls `kvm_vcpu_pmu_restore_host()`, reversing the EL0 filters. If host userspace writes PMUSERENR while KVM owns the hardware register, `kvm_set_pmuserenr()` records the host value in the saved host context rather than touching active guest state.

State and persistence: state is per-CPU, not per-VM: `events_host` and `events_guest` track hardware event indexes requiring filter toggles. Host PMUSERENR persistence is in `host_ctxt` while a guest PMUSERENR is loaded. The actual hardware state is transient and rewritten around vCPU scheduling. The code exits early when PMUv3 or VHE is unavailable.

Dependencies and integration: depends on PMUv3 sysreg accessors (`read_pmevtypern`, `write_pmevtypern`, `read_pmccfiltr`, `write_pmccfiltr`, `read_pmicfiltr`, `write_pmicfiltr`), perf event attributes, `system_supports_pmuv3()`, `has_vhe()`, KVM running-vCPU lookup, host context storage, and request delivery for `KVM_REQ_RESYNC_PMU_EL0`. It complements `pmu-emul.c`, which creates guest perf events and invokes guest restore after reprogramming.

Risks: this code writes real hardware PMU filters and assumes preemption control on VHE when modifying per-CPU state. Incorrect event masks can leak host EL0 counts into guest-visible events or suppress guest counts. Interrupt-time host PMU changes require deferred resync; missing that request can leave guest EL0 filters stale. Non-VHE paths deliberately return false/no-op because full sysreg context switching covers PMUSERENR.

Test signals: perf/KVM interaction tests should monitor host and guest event exclusion across VHE guest entry/exit, PMUSERENR writes while a vCPU is running, interrupt-time PMU updates, and systems without PMUv3 or VHE. Hardware counter sanity checks can detect host/guest EL0 count leakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/psci.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/psci.c

Purpose: emulates the ARM Power State Coordination Interface for KVM guests. It handles vCPU suspend/off/on, affinity queries, PSCI feature discovery, system shutdown/reset/suspend exits to userspace, PSCI version dispatch from 0.1 through 1.3, and SMCCC register return conventions.

Important APIs and functions: `kvm_psci_call()` is the exported dispatcher. Key helpers include `kvm_psci_vcpu_suspend()`, `kvm_psci_vcpu_on()`, `kvm_psci_vcpu_affinity_info()`, `kvm_prepare_system_event()`, `kvm_psci_system_off()`, `kvm_psci_system_off2()`, `kvm_psci_system_reset()`, `kvm_psci_system_reset2()`, `kvm_psci_system_suspend()`, `kvm_psci_narrow_to_32bit()`, `kvm_psci_check_allowed_function()`, `kvm_psci_0_1_call()`, `kvm_psci_0_2_call()`, and `kvm_psci_1_x_call()`.

Control flow: `kvm_psci_call()` first rejects 64-bit PSCI function IDs from 32-bit vCPUs, then dispatches based on the VM-configured PSCI version. PSCI 0.1 supports only legacy CPU off/on. PSCI 0.2 adds version, suspend, affinity info, migrate info type, system off, and system reset. PSCI 1.x layers feature discovery, optional system suspend, reset2, and off2 based on the minor version and VM flags. Most calls write return values through `smccc_set_retval()` and return 1 to resume the guest. System off/reset/off2 and suspend prepare `KVM_EXIT_SYSTEM_EVENT` and return 0 so userspace handles the event.

CPU_ON resolves the target MPIDR, verifies the vCPU exists and is stopped, stores reset PC, endianness, and x0/r0 in `reset_state`, sets `reset = true`, issues `KVM_REQ_VCPU_RESET`, uses a write barrier before marking the vCPU runnable, and wakes it. SYSTEM_* events stop all vCPUs, request sleep, populate `run->system_event`, and preload an internal-failure return value for cases where userspace incorrectly resumes the caller.

State and persistence: persistent state touched here includes `vcpu->arch.mp_state`, `mp_state_lock`, `reset_state`, VM PSCI version/config flags, and `kvm_run.system_event`. Suspend is modeled as WFI and does not persist power-down state. CPU_OFF updates the vCPU power state through shared KVM helpers.

Dependencies and integration: depends on SMCCC argument helpers, KVM MP state, vCPU wakeup and reset requests, `kvm_mpidr_to_vcpu()`, ARM PSCI constants, hypercall dispatch, userspace KVM exits, and system suspend enable flags. Reset state written by PSCI is consumed by `reset.c` in `kvm_reset_vcpu()`.

Risks: PSCI is guest ABI. Return-code differences between PSCI 0.1 and newer versions matter, especially CPU_ON already-on handling. System event exits intentionally stop all vCPUs before userspace action; allowing vCPUs to continue can violate PSCI immediacy expectations. 32-bit narrowing must be applied to the right calls before reading affinity/entry parameters. Reset2/off2 feature reporting must track the advertised minor version and validate type arguments.

Test signals: KVM PSCI tests should cover all configured versions, CPU_ON success/already-on/invalid-affinity, 32-bit callers invoking 64-bit functions, AFFINITY_INFO levels, SYSTEM_OFF/RESET/SUSPEND exits, RESET2 warm/vendor ranges, OFF2 hibernate validation, and userspace resuming after a system event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/psci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/ptdump.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/ptdump.c

Purpose: provides debugfs page-table dumps for arm64 KVM stage-2 page tables, including canonical VM stage-2 tables and nested virtualization shadow stage-2 MMUs. It formats leaf PTE attributes through the generic ptdump machinery and exposes IPA range and level-count metadata.

Important APIs and types: `struct kvm_ptdump_guest_state` holds the target `kvm_s2_mmu`, parser state, IPA markers, and level descriptions. Public creation/removal functions are `kvm_s2_ptdump_create_debugfs()`, `kvm_nested_s2_ptdump_create_debugfs()`, and `kvm_nested_s2_ptdump_remove_debugfs()`. Internal file operations are backed by `kvm_ptdump_guest_show()`, `kvm_ptdump_guest_open()`, `kvm_ptdump_guest_close()`, `kvm_pgtable_range_show()`, `kvm_pgtable_levels_show()`, and shared open/close helpers.

Control flow: debugfs open obtains a safe KVM reference with `kvm_get_kvm_safe()`, allocates a parser state based on the target page table start level, and attaches it to a single-open seq file. The show path initializes `ptdump_pg_state`, takes `kvm->mmu_lock` for writing, and walks the page table from IPA 0 to `BIT(ia_bits)` with a leaf-only walker. Each visited leaf calls `note_page()` with the old PTE. Close frees parser state and drops the KVM reference. Nested debugfs files are named from cached VTTBR, VTCR, and whether virtual stage-2 is enabled.

State and persistence: this file persists only debugfs dentries and per-open parser allocations. `mmu->shadow_pt_debugfs_dentry` is stored for nested MMU removal. It does not modify page-table contents; it reads under `mmu_lock` to provide a stable dump.

Dependencies and integration: depends on `linux/debugfs.h`, `seq_file`, arm64 KVM page-table walkers, generic `ptdump`, stage-2 PTE bit definitions, KVM lifetime reference helpers, and nested-virt capability detection. `nested.c` creates/removes nested ptdump files when shadow MMU contexts are allocated or recycled.

Risks: debugfs lifetime must not outlive the KVM or nested MMU. The safe KVM reference and removal path reduce that risk, but stale `i_private` pointers would be serious. The dump takes a write lock over a full IPA walk, so large sparse VMs can make debugfs reads expensive and block MMU updates. Formatting masks must stay synchronized with stage-2 PTE bit definitions.

Test signals: manual debugfs reads should show `stage2_page_tables`, `ipa_range`, `stage2_levels`, and nested entries when nested virt is available. Tests can validate open/close during VM teardown, nested MMU recycling removing files, and output attribute strings for readable/writable/executable/accessed/block mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/ptdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/pvtime.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/pvtime.c

Purpose: implements arm64 KVM paravirtual stolen-time support. It lets userspace configure a guest physical address for the stolen-time structure, initializes the structure, answers SMCCC PV feature queries, and updates the guest-visible stolen-time counter from host scheduler run-delay accounting.

Important APIs and functions: `kvm_update_stolen_time()` updates the guest memory field. `kvm_hypercall_pv_features()` reports PV time feature availability to the guest. `kvm_init_stolen_time()` zeros and arms the guest structure. `kvm_arm_pvtime_supported()` checks `sched_info_on()`. `kvm_arm_pvtime_set_attr()`, `kvm_arm_pvtime_get_attr()`, and `kvm_arm_pvtime_has_attr()` implement the `KVM_ARM_VCPU_PVTIME_IPA` device attribute.

Control flow: userspace sets the stolen-time IPA through the vCPU device attribute. The setter verifies sched info support, attr ID, user copy, 64-byte alignment, one-shot configuration, and that the target GFN resolves to a valid memslot under SRCU. Initialization records current `current->sched_info.run_delay`, zeros the guest `pvclock_vcpu_stolen_time` structure, and returns the base. Runtime updates read the existing little-endian stolen-time value at `base + offsetof(stolen_time)`, compute the delta in current task run delay since the last update, store the new `last_steal`, and write the accumulated value back to guest memory.

State and persistence: per-vCPU state is `vcpu->arch.steal.base` and `last_steal`. Guest memory persists the ABI structure and accumulated stolen-time value in little-endian format. `INVALID_GPA` disables the feature. No global state is owned by this file.

Dependencies and integration: depends on scheduler `sched_info`, ARM SMCCC PV time function IDs, KVM guest memory access helpers, SRCU, memslot lookup, and the `pvclock-abi.h` layout. It integrates with hypercall handling and vCPU run/load paths that call update/init helpers.

Risks: the configured IPA is validated only at setup; later memslot changes or invalidation rely on normal KVM memory access failure handling. Stolen-time accumulation is tied to the host task's `run_delay`, so update frequency affects when the guest observes increments. Endianness is explicitly little-endian per ABI and must not follow guest CPU endianness. One-shot IPA configuration prevents accidental relocation but means userspace must set it correctly before use.

Test signals: tests should cover unsupported sched-info systems, unaligned IPA rejection, invalid memslot rejection, duplicate set returning `-EEXIST`, get/has attr behavior, feature hypercall success only after base is configured, zero initialization, and monotonic stolen-time accumulation after host scheduling delays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/pvtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/reset.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/reset.c

Purpose: centralizes arm64 KVM vCPU reset/finalization and IPA-limit initialization. It initializes SVE virtualization limits, finalizes per-vCPU SVE state, frees vCPU-owned hyp-shared resources, resets core and system registers for EL1/EL2/AArch32 entry, applies PSCI-provided reset state, resets timers, and computes the maximum physical/IPA size KVM exposes.

Important APIs and functions: `kvm_arm_init_sve()`, `kvm_arm_vcpu_finalize()`, `kvm_arm_vcpu_is_finalized()`, `kvm_arm_vcpu_destroy()`, `kvm_reset_vcpu()`, `kvm_get_pa_bits()`, `get_kvm_ipa_limit()`, and `kvm_set_ipa_limit()` are public to the KVM arm64 subsystem. Internal helpers include `kvm_vcpu_enable_sve()`, `kvm_vcpu_finalize_sve()`, and `kvm_vcpu_reset_sve()`.

Control flow: boot-time SVE initialization records the maximum virtualizable and host vector lengths, publishes the host max to nVHE, caps guest VL at `VL_ARCH_MAX`, and warns if guests are limited below host max. VCPU reset snapshots and clears pending `reset_state` under `mp_state_lock`, disables preemption, fully puts loaded vCPU state if necessary, enables or clears SVE state depending on finalization, chooses reset PSTATE based on AArch32, nested virt, or normal EL1, zeroes general/FPSIMD and legacy SPSR state, resets sysregs, then applies PSCI reset overrides for PC, Thumb bit, endianness, pending exception flags, and x0/r0. It resets the virtual timer and reloads hardware state if the vCPU was loaded.

State and persistence: VM-wide immutable state includes `kvm_ipa_limit`, `kvm_sve_max_vl`, and `kvm_host_sve_max_vl`. Per-vCPU persistent state includes `sve_max_vl`, `sve_state`, finalized flags, `reset_state`, core registers, sysregs, FPSIMD context, VNCR allocations, CCSIDR cache, and timer state. SVE buffers are shared with hyp on finalize and unshared/freed on destroy.

Dependencies and integration: depends on SVE/FPSIMD helpers, KVM hyp sharing APIs, nested virtualization helpers, sysreg reset, arch timer reset, PSCI reset state from `psci.c`, CPU feature registers, LPA2 and stage-2 granule support checks, and VM physical address-size policy. It is called from vCPU init ioctls and from PSCI CPU_ON reset requests.

Risks: reset can run while a vCPU is loaded, so preemption and put/load ordering are critical. SVE finalization is a userspace ABI boundary: once finalized, vector lengths and buffer size are fixed. Failing to unshare SVE or vCPU memory from hyp leaks protected mappings. Reset-state application must happen after sysreg reset or PSCI PC/endianness/x0 values would be overwritten. IPA limit setup must reject unsupported stage-2 granules and cap address sizes correctly without LPA2.

Test signals: coverage should include vCPU init reset, PSCI CPU_ON reset while loaded, AArch32 Thumb entry, nested EL2 reset PSTATE, SVE enable/finalize/destroy, vector length caps, timer reset, clearing pending exception/PC increment flags, and boot on systems with unsupported TGRAN_2 or PARange above 48 bits without LPA2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/stacktrace.c

Purpose: provides host-side printing of nVHE hypervisor stack traces for arm64 KVM. It supports direct unwinding of non-protected nVHE stacks that remain host-accessible and shared-buffer printing for protected KVM where hyp memory is inaccessible to the host.

Important APIs and functions: the public entry point is `kvm_nvhe_dump_backtrace()`. Internal helpers define stack ranges (`stackinfo_get_overflow()`, `stackinfo_get_overflow_kern_va()`, `stackinfo_get_hyp()`, `stackinfo_get_hyp_kern_va()`), translate hyp stack frame addresses to kernel VAs (`kvm_nvhe_stack_kern_va()`, `kvm_nvhe_stack_kern_record_va()`), perform frame unwinding (`unwind_next()`, `unwind()`), print entries (`kvm_nvhe_dump_backtrace_entry()`), and select non-protected vs pKVM dumping (`hyp_dump_backtrace()`, `pkvm_dump_backtrace()`).

Control flow: `kvm_nvhe_dump_backtrace()` checks whether protected KVM is enabled. Non-protected mode obtains saved nVHE FP/PC from the per-CPU `kvm_stacktrace_info`, builds kernel-VA stack ranges for the normal and overflow stacks, initializes an unwind state, then repeatedly converts each hyp FP to a kernel VA and calls the generic frame-record unwinder. Each PC is masked to hyp VA bits, translated by `hyp_offset`, adjusted for KASLR when symbolizing, and printed. Protected mode reads a per-CPU shared `pkvm_stacktrace` array generated by EL2 when `CONFIG_PKVM_STACKTRACE` is enabled; otherwise it prints that protected stack traces are unavailable.

State and persistence: this file reads per-CPU nVHE symbols such as `kvm_stacktrace_info`, `overflow_stack`, `kvm_arm_hyp_stack_base`, and optionally `pkvm_stacktrace`. It does not persist new state; it consumes saved stacktrace state after a hyp fault/panic path has populated it.

Dependencies and integration: depends on nVHE stacktrace ABI structures, arm64 stacktrace frame-record unwinder, hyp VA sizing, KASLR offset handling, protected KVM mode detection, and per-CPU nVHE symbol accessors. It integrates with KVM error reporting paths that call `kvm_nvhe_dump_backtrace()` with the hyp offset.

Risks: address translation is mode-specific. Non-protected unwinding assumes the host can safely read hyp stack pages and that frame records fall within either the hyp or overflow stack. Protected mode must not dereference hyp-private memory, so it relies on bounded shared buffers. Wrong hyp offset, VA masking, or stack bounds can produce misleading symbols or stop unwinding early. Lack of `CONFIG_PKVM_STACKTRACE` intentionally reduces diagnostics for protected mode.

Test signals: fault-injection or debug paths should verify readable non-protected nVHE traces, overflow-stack frame handling, pKVM shared-buffer traces when enabled, graceful message when disabled, symbolization with KASLR, and termination on invalid frame records rather than out-of-bounds reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/stacktrace.c -->
