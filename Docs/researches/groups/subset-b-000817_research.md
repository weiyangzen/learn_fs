# subset-b-000817 research

This grouped report covers the RISC-V KVM source files requested for `subset-b-000817`. Each file section is source-tree-aligned and wrapped in deterministic markers for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/aia.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/aia.c

Purpose: This file implements the host-level RISC-V Advanced Interrupt Architecture integration for KVM. It owns global AIA availability, host guest-external-interrupt-line discovery, HGEI allocation/freeing, per-CPU SGEI interrupt handling, AIA CSR save/restore around vCPU load/put, and in-kernel emulation of selected AIA indirect registers.

Important APIs/types/functions: `struct aia_hgei_control` tracks a per-CPU raw spinlock, free HGEI bitmap, and owner vCPUs. Public state includes `kvm_riscv_aia_nr_hgei`, `kvm_riscv_aia_max_ids`, and static key `kvm_riscv_aia_available`. vCPU-facing APIs include `kvm_riscv_vcpu_aia_has_interrupts`, `kvm_riscv_vcpu_aia_update_hvip`, `kvm_riscv_vcpu_aia_load`, `kvm_riscv_vcpu_aia_put`, CSR get/set helpers, `kvm_riscv_vcpu_aia_rmw_topei`, and `kvm_riscv_vcpu_aia_rmw_ireg`. Host resource APIs include `kvm_riscv_aia_alloc_hgei`, `kvm_riscv_aia_free_hgei`, `kvm_riscv_aia_enable`, `kvm_riscv_aia_disable`, `kvm_riscv_aia_init`, and `kvm_riscv_aia_exit`.

Control flow: Initialization requires the SxAIA ISA extension, probes `HGEIE` to learn available HGEI lines, clamps that count against IMSIC guest files, initializes per-CPU HGEI state, requests the per-CPU SGEI interrupt when any HGEI is available, registers `KVM_DEV_TYPE_RISCV_AIA`, and enables the static key. CPU virtualization enable programs HVICTL/HVIPRIO state and enables SGEI delivery. On vCPU load, saved AIA CSRs are written through NACL shared memory or direct CSR writes, then IMSIC load is delegated if the VM AIA device is initialized. On put, IMSIC state is put first and CSRs are captured back into `vcpu->arch.aia_context`. SGEI interrupts clear enabled HGEI bits and kick owner vCPUs.

State and persistence: HGEI ownership persists per CPU while a vCPU owns a hardware IMSIC VS-file. Guest AIA CSR state persists in `struct kvm_vcpu_aia_csr` and is synchronized at vCPU load/put. Interrupt pending bits use `irqs_pending` plus `irqs_pending_mask`, with special 32-bit high-half handling. Static keys make AIA paths no-ops on unsupported hosts.

Dependencies and integration points: It depends on RISC-V IMSIC IRQ-chip configuration, INTC irqdomains, KVM vCPU request/kick paths, CSR accessors, NACL CSR synchronization, AIA device ops from `aia_device.c`, and IMSIC helpers from `aia_imsic.c`. PMU overflow interrupt filtering is enabled when Sscofpmf exists.

Risks and test signals: HGEI allocation is per-CPU and lock-protected, so migration and CPU hotplug paths must not leak ownership or leave `HGEIE` enabled for freed lines. CSR load/put fast paths must stay in sync with one-reg CSR setters. Tests should cover hosts with zero HGEI, automatic fallback to emulation, 32-bit high AIA CSR paths, vCPU blocking wakeups through SGEI, AIA init failure cleanup, and PMU overflow interrupt filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/aia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/aia_aplic.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/aia_aplic.c

Purpose: This file emulates the RISC-V APLIC interrupt controller for a KVM VM. It exposes APLIC MMIO/device-attribute access, maintains per-source configuration/pending/enable/input/target state, converts source-level changes into MSI injections, and registers the emulated controller on the VM MMIO bus.

Important APIs/types/functions: `struct aplic_irq` holds per-source `sourcecfg`, `state`, `target`, and a raw spinlock. `struct aplic` embeds a `kvm_io_device` plus domain configuration, generated-MSI value, source counts, and IRQ array. Core helpers read/write source configuration, target, pending, enable, and input state. `kvm_riscv_aia_aplic_inject` applies external line-level changes. Attribute helpers are `kvm_riscv_aia_aplic_set_attr`, `get_attr`, and `has_attr`. Lifecycle APIs are `kvm_riscv_aia_aplic_init` and `kvm_riscv_aia_aplic_cleanup`.

Control flow: VM AIA initialization allocates `struct aplic` when `nr_sources` is nonzero, creates `nr_sources + 1` IRQ slots because source 0 is invalid, initializes locks, registers `aplic_mmio_read/write` over the configured APLIC address range, and installs default IRQ routing. Guest MMIO writes update source, pending, enable, domain, target, or genmsi registers, then call `aplic_update_irq_range` to inject any enabled-and-pending source as an MSI and clear its pending bit. External kernel/user injection enters through `kvm_riscv_aia_aplic_inject`, which applies edge/level semantics, updates raw input state, and injects when domain interrupt enable and source enable permit delivery.

State and persistence: APLIC state is VM-scoped and persists until VM AIA cleanup. Per-source state is protected by raw spinlocks and includes guest-visible configuration and transient input/pending bits. `domaincfg` only honors the interrupt-enable bit and always reports direct MSI mode. `genmsi` records the last generated MSI value with guest index masked out.

Dependencies and integration points: It depends on Linux `riscv-aplic` register definitions, `kvm_io_device`, KVM MMIO bus registration, KVM IRQ routing, and AIA MSI injection in `aia_device.c`. It is created from the VM AIA device init path and removed during VM teardown.

Risks and test signals: Edge/level source semantics are subtle because pending updates are suppressed for inactive or nonmatching level states. MMIO access is 32-bit aligned only and returns `-ENODEV` for unknown offsets, so register coverage tests should hit all APLIC register windows. Tests should validate source 0 rejection, big-endian `SETIPNUM_BE`, domain-enable gating, target hart/guest/EIID extraction, default IRQ routing, cleanup unregistering the MMIO device, and lock-safe concurrent injection with guest MMIO writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/aia_aplic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/aia_device.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/aia_device.c

Purpose: This file implements the userspace-visible KVM AIA device. It validates and stores VM AIA configuration, APLIC and per-vCPU IMSIC addresses, initializes the emulated/accelerated interrupt controller graph, exposes KVM device attributes, and provides VM/vCPU AIA lifecycle and injection helpers.

Important APIs/types/functions: `kvm_riscv_aia_device_ops` supplies create/destroy/set/get/has attribute handlers for `KVM_DEV_TYPE_RISCV_AIA`. Internal helpers include `aia_config`, `aia_aplic_addr`, `aia_imsic_addr`, `aia_imsic_ppn`, `aia_imsic_hart_index`, and `aia_init`. Public integration helpers include `kvm_riscv_vcpu_aia_update`, `reset`, `init`, `deinit`, `kvm_riscv_aia_inject_msi_by_id`, `kvm_riscv_aia_inject_msi`, `kvm_riscv_aia_inject_irq`, `kvm_riscv_aia_init_vm`, and `kvm_riscv_aia_destroy_vm`.

Control flow: Device creation refuses duplicate in-kernel irqchip state, requires host SSAIA availability, locks all vCPUs, and rejects creation once any vCPU has run. Userspace sets mode, IDS, source count, address geometry, APLIC base, and per-vCPU IMSIC bases through device attributes. `KVM_DEV_RISCV_AIA_CTRL_INIT` verifies vCPU creation is stable, checks source/ID limits and required bases, initializes APLIC, validates all IMSIC pages share the same base PPN under configured hart/group/guest addressing, derives each vCPU hart index, initializes each IMSIC, then marks the VM AIA initialized.

State and persistence: VM state in `kvm->arch.aia` persists mode, ID/source counts, group/hart/guest addressing geometry, APLIC address, initialized flag, and APLIC state. vCPU AIA state persists IMSIC address, hart index, AIA CSR shadow, and IMSIC state. Writes to configuration/address attributes are blocked after initialization. VM defaults choose AUTO mode when HGEI exists and EMUL otherwise.

Dependencies and integration points: It coordinates `aia_aplic.c`, `aia_imsic.c`, KVM device attributes, KVM vCPU lookup/locking, KVM MSI routing, and VM creation/destruction hooks. IRQ injection routes either by abstract hart/guest/EIID or by MSI address decoding against per-vCPU IMSIC pages.

Risks and test signals: The most important correctness boundary is initialization immutability: changing address geometry after IMSIC allocation would misroute MSIs. Address alignment, common PPN checks, online-vCPU count checks, and cleanup of partially initialized IMSICs all need coverage. Tests should exercise userspace AIA device creation ordering, all config validation failures, mode behavior with and without HGEI, MSI-by-address routing, hart-index derivation with group bits, and teardown after partial init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/aia_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/aia_imsic.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/aia_imsic.c

Purpose: This file emulates and optionally hardware-accelerates per-vCPU IMSIC state for RISC-V KVM AIA. It maintains a software MRIF image, moves state to and from hardware IMSIC VS-files when HGEI lines are available, handles IMSIC MMIO/MSI injection, and implements IMSIC register access for CSR emulation and KVM device attributes.

Important APIs/types/functions: `struct imsic_mrif_eix` stores EIP/EIE bit arrays, `struct imsic_mrif` stores EIX arrays plus delivery/threshold, and `struct imsic` owns MMIO device state, MSI counts, VS-file lock/details, SW-file memory, and external IRQ lock. Major helpers include IMSIC CSR read/swap/write/set switch macros, MRIF atomic RMW/or/read/write, `imsic_mrif_topei`, `imsic_mrif_rmw`, VS-file local read/rw/clear/update helpers, SW-file update/read helpers, and lifecycle/injection APIs such as `kvm_riscv_vcpu_aia_imsic_update`, `release`, `rmw`, `rw_attr`, `inject`, `init`, and `cleanup`.

Control flow: IMSIC init allocates a per-vCPU `struct imsic`, sets software and hardware EIX counts, allocates a zeroed MRIF page, and registers an MMIO page. In emulation mode, MSIs set EIP bits in the SW-file and `imsic_swfile_extirq_update` drives `IRQ_VS_EXT` based on delivery, enable, pending, and threshold state. In AUTO/HWACCEL mode, `kvm_riscv_vcpu_aia_imsic_update` allocates a CPU-local HGEI/VS-file on vCPU entry, maps the guest IMSIC GPA to the hardware VS-file PA, updates `HSTATUS.VGEIN`, migrates register state from old VS-file or SW-file to the new VS-file, and frees old HGEI resources. Release reverses the process by unmapping the GPA, reading/clearing hardware VS-file state, merging it into SW-file state, and freeing the HGEI.

State and persistence: IMSIC state persists in exactly one of two places: hardware VS-file when `vsfile_cpu >= 0`, or SW-file MRIF when not accelerated. `vsfile_lock` protects transitions and concurrent attribute/MSI access. `swfile_extirq_lock` prevents lost external-interrupt state between TOPEI calculation and HVIP updates. The SW-file page and MMIO registration live for the vCPU IMSIC lifetime.

Dependencies and integration points: It integrates with AIA HGEI allocation in `aia.c`, G-stage MMIO remapping in `mmu.c`, KVM MMIO bus, CSR/HSTATUS access, on-CPU callbacks, AIA device attributes, and vCPU interrupt injection. It has explicit TODOs for IOMMU mapping when VS-files are remapped.

Risks and test signals: State migration between SW-file and VS-file is concurrency-sensitive and must not drop pending MSIs. HWACCEL mode must fail entry if a VS-file cannot be allocated, while AUTO must fall back cleanly. Tests should cover IMSIC register RMW on 32/64-bit, TOPEI clear semantics, MSI little/big-endian setipnum offsets, vCPU migration across CPUs, blocking wakeups through HGEI, release on CPU virtualization disable, attribute access while accelerated, and cleanup after MMIO registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/aia_imsic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/gstage.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/gstage.c

Purpose: This file implements RISC-V KVM G-stage page-table primitives. It detects supported HGATP modes, walks and edits guest-physical translations, maps pages and huge pages, splits huge mappings for dirty logging, write-protects or clears ranges, and issues the corresponding HFENCE invalidations.

Important APIs/types/functions: Global `kvm_riscv_gstage_max_pgd_levels` records the selected G-stage depth. Helpers include `gstage_pte_index`, `gstage_page_size_to_level`, `gstage_level_to_page_order/size`, `kvm_riscv_gstage_get_leaf`, `gstage_tlb_flush`, `kvm_riscv_gstage_set_pte`, `kvm_riscv_gstage_map_page`, `kvm_riscv_gstage_split_huge`, `kvm_riscv_gstage_op_pte`, `kvm_riscv_gstage_unmap_range`, `kvm_riscv_gstage_wp_range`, and `kvm_riscv_gstage_mode_detect`.

Control flow: Mapping starts by converting a requested page size into a page-table level, choosing read/write/execute protections with A/D bits set, and checking for an existing leaf. Existing huge mappings are split downward when dirty logging needs 4K tracking; compatible existing leaves only have protection updated. New mappings allocate intermediate tables from the KVM MMU cache and install a leaf. Clear/write-protect operations recursively walk page tables and operate at leaf granularity, freeing child tables during clear. Mode detection writes candidate HGATP modes from largest to smallest and records the first supported depth.

State and persistence: Persistent state is the VM's G-stage page-table tree rooted at `kvm->arch.pgd`; this file mutates PTEs but does not own the root allocation. `KVM_GSTAGE_FLAGS_LOCAL` selects local versus remote flush behavior. Mapping state persists until memory-slot invalidation, shadow flush, or VM teardown clears it.

Dependencies and integration points: It depends on Linux PTE/page helpers, `struct kvm_gstage` from architecture headers, KVM MMU memory caches, and TLB/HFENCE functions from `tlb.c`. It is used by MMU fault handling, AIA IMSIC MMIO remapping, dirty logging, aging, and memory-slot invalidation.

Risks and test signals: Huge-page splitting and write-protecting must preserve PFN offsets and permissions exactly. `gstage_level_to_page_order` treats invalid levels conservatively, but callers must pass supported levels. Tests should cover Sv32x4/Sv39x4/Sv48x4/Sv57x4 detection, 4K and huge mappings, dirty-log write-protection, unmap of sparse ranges, page-table free recursion, local versus remote HFENCE paths, and retry behavior when a huge mapping already exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/gstage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/isa.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/isa.c

Purpose: This file maps KVM RISC-V ISA extension IDs to kernel RISC-V extension IDs and centralizes host availability plus guest enable/disable policy. It is the policy source used by one-reg ISA configuration and vCPU default ISA setup.

Important APIs/types/functions: `kvm_isa_ext_arr` maps `KVM_RISCV_ISA_EXT_*` IDs to `RISCV_ISA_EXT_*` IDs. `kvm_riscv_base2isa_ext` converts legacy single-letter base extension indices into KVM extension IDs. `__kvm_riscv_isa_check_host` validates an extension ID, handles host-side aliasing such as guest Smnpm backed by host Ssnpm, and returns the guest extension bit. `kvm_riscv_isa_enable_allowed` and `kvm_riscv_isa_disable_allowed` encode guest policy restrictions.

Control flow: Callers validate a KVM extension ID against array bounds, use nospec indexing, translate any special host availability case, then query host ISA availability. Enable policy rejects exposing H to guests, requires SSAIA for Sscofpmf interrupt filtering, requires hardware PTE young support for Svadu, and checks vector user control for V. Disable policy marks many architectural extensions as non-disableable because no architectural control exists, while allowing selected extensions where Smstateen or hardware ADUE controls can enforce behavior.

State and persistence: This file is mostly static data and pure policy. Guest ISA bitmaps persist in each vCPU and are modified by `vcpu_onereg.c`; this file decides which requested transitions are legal before the first vCPU run.

Dependencies and integration points: It depends on kernel cpufeature helpers, `asm/kvm_isa.h`, page-table young/dirty capability, and vector state control. It feeds vCPU creation, KVM_GET/SET_ONE_REG ISA extension handling, and configuration of HENVCFG/HSTATEEN in `vcpu_config.c`.

Risks and test signals: A wrong mapping or permissive disable decision can advertise an extension that KVM cannot virtualize or cannot hide. Tests should enumerate all `KVM_RISCV_ISA_EXT_MAX` IDs, compare GET_REG_LIST with host capabilities, verify pre-run enable/disable restrictions, confirm post-run changes are rejected by callers, and cover special cases for SSAIA/Sscofpmf, Svadu/Svade, Smstateen, V, and pointer masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/isa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/main.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/main.c

Purpose: This file is the RISC-V KVM module entry point and per-CPU virtualization enable/disable hook. It validates architectural and SBI prerequisites, initializes optional NACL/AIA acceleration, detects G-stage mode and VMID width, registers KVM core, and tears everything down on exit.

Important APIs/types/functions: `DEFINE_STATIC_KEY_FALSE(kvm_riscv_vsstage_tlb_no_gpa)` records an Andes vendor quirk. `kvm_arch_enable_virtualization_cpu` enables NACL shared memory, clears delegation CSRs, permits only time counter access, clears HVIP, and enables AIA. `kvm_arch_disable_virtualization_cpu` disables AIA, clears VSIE/HVIP/delegation CSRs in a safe order, and disables NACL. Module functions are `riscv_kvm_init`, `riscv_kvm_exit`, and helper `kvm_riscv_teardown`.

Control flow: Module init refuses hosts without H extension, SBI v0.2+, or RFENCE. It initializes NACL if available, probes G-stage mode, detects VMID bits, initializes AIA when available, prints discovered capabilities, enables vendor quirks, registers perf callbacks, and calls `kvm_init`. Failures unwind NACL/AIA/perf state through `kvm_riscv_teardown`. CPU enable/disable hooks program hypervisor CSRs each time KVM virtualization is activated on a CPU.

State and persistence: Persistent module state includes static keys for vendor TLB behavior, NACL feature keys, AIA availability, VMID mode information, and registered device/perf/KVM core callbacks. Per-CPU virtualization state lives in CSRs and is reset on disable.

Dependencies and integration points: It depends on SBI probing, cpufeature discovery, NACL, G-stage/VMID helpers, AIA init, perf callbacks, and generic KVM module registration. It bridges Linux KVM core with RISC-V hardware virtualization.

Risks and test signals: CSR disable ordering matters because stale HVIP plus VSIE can deliver spurious host interrupts after clearing delegation. Init unwind must not leak NACL pages or AIA IRQ/device registrations. Tests should cover unsupported-H/SBI/RFENCE paths, NACL feature combinations, AIA absent/present hosts, G-stage mode detection failures, module load/unload, CPU hotplug virtualization enable/disable, and Andes AX66 quirk behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/mmu.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/mmu.c

Purpose: This file connects generic KVM memory-slot/MMU operations to RISC-V G-stage page tables. It maps guest faults to host PFNs, validates memory regions, supports dirty logging and aging, handles IO remaps such as IMSIC VS-files, allocates/frees VM G-stage roots, and programs HGATP for vCPUs.

Important APIs/types/functions: Key functions include `kvm_riscv_mmu_ioremap`, `kvm_riscv_mmu_iounmap`, `kvm_arch_mmu_enable_log_dirty_pt_masked`, `kvm_arch_commit_memory_region`, `kvm_arch_prepare_memory_region`, `kvm_unmap_gfn_range`, `kvm_age_gfn`, `kvm_test_age_gfn`, `kvm_riscv_mmu_map`, `kvm_riscv_mmu_alloc_pgd`, `kvm_riscv_mmu_free_pgd`, and `kvm_riscv_mmu_update_hgatp`. Helpers handle memory-slot write-protection, THP alignment, host page-table size discovery, and huge-page adjustment.

Control flow: Fault handling validates/top-ups the vCPU page-table cache, inspects the host VMA for page size and PFNMAP/logging restrictions, snapshots `mmu_invalidate_seq`, faults in the PFN, acquires `mmu_lock`, retries if invalidation raced, optionally adjusts to THP PMD size, marks writable pages dirty, and maps through `kvm_riscv_gstage_map_page`. Memory-region preparation rejects GPAs outside the selected G-stage address space, writable slots backed by read-only VMAs, and dirty logging on PFNMAP IO regions. Dirty logging write-protects memslots by clearing G-stage write bits and flushing remote TLBs.

State and persistence: The VM owns `arch.pgd`, `pgd_phys`, and `pgd_levels`; this file allocates and frees that root and updates `HGATP` with mode, VMID, and PPN. Per-vCPU `mmu_page_cache` persists preallocated page-table pages. Dirty logging state is reflected by write-protected G-stage PTEs and KVM dirty bitmaps.

Dependencies and integration points: It depends on Linux VMA/mmap locking, KVM memory slots, dirty-ring/dirty-log APIs, host page-table walkers, RISC-V G-stage primitives in `gstage.c`, VMID helpers, NACL CSR writes, and TLB invalidation. AIA IMSIC hardware acceleration uses `ioremap/iounmap` to map guest IMSIC GPAs to hardware VS-file pages.

Risks and test signals: Race handling around host MMU invalidation and page-table promotion is subtle; `get_hva_mapping_size` deliberately reads entries once with IRQs disabled. Tests should cover memory-slot validation, read-only slots, PFNMAP IO slots, dirty logging enable/disable, THP and hugetlb mappings, HWPOISON signaling, `mmu_invalidate_seq` retry, aging queries, IMSIC IO remaps, and HGATP updates with and without VMID hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/nacl.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/nacl.c

Purpose: This file implements KVM support for the SBI Nested Acceleration extension. It probes NACL and feature availability, allocates per-CPU shared memory, enables/disables NACL shmem on CPU virtualization entry/exit, and queues shared-memory HFENCE requests for accelerated synchronization.

Important APIs/types/functions: Static keys include `kvm_riscv_nacl_available`, `kvm_riscv_nacl_sync_csr_available`, `kvm_riscv_nacl_sync_hfence_available`, `kvm_riscv_nacl_sync_sret_available`, and `kvm_riscv_nacl_autoswap_csr_available`. `DEFINE_PER_CPU(struct kvm_riscv_nacl, kvm_riscv_nacl)` stores shmem virtual/physical addresses. Public functions are `__kvm_riscv_nacl_hfence`, `kvm_riscv_nacl_enable`, `kvm_riscv_nacl_disable`, `kvm_riscv_nacl_init`, and `kvm_riscv_nacl_exit`.

Control flow: Init requires SBI 1.0+ and the NACL extension, enables the base static key, probes individual NACL features, and allocates zeroed per-CPU shared-memory pages. CPU enable sets the per-CPU shared memory through `SBI_EXT_NACL_SET_SHMEM`; disable passes the SBI disable sentinel. HFENCE enqueue searches NACL shmem entries for a nonpending slot, tries a sync flush up to five times if full, and writes little-endian control/page/count fields.

State and persistence: Per-CPU shmem persists from module init to NACL exit and is registered/unregistered with firmware on CPU virtualization enable/disable. Feature static keys persist module-wide and drive optimized CSR, HFENCE, SRET, and autoswap paths in other files.

Dependencies and integration points: It depends on SBI extension calls and NACL shmem layout macros from `asm/kvm_nacl.h`. It is used by `main.c` CPU hooks, `vcpu.c` context switching and CSR sync, `vcpu_config.c` CSR load, and `tlb.c` HFENCE request processing.

Risks and test signals: Shared-memory entries can fill under heavy HFENCE load; the retry path must not spin indefinitely or silently corrupt pending entries. Tests should cover absence of NACL, all feature-bit combinations, per-CPU allocation failure cleanup, CPU enable/disable SBI errors, HFENCE queue saturation warning, little-endian shmem encoding, and fallback to direct CSR/HFENCE paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/nacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/tlb.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/tlb.c

Purpose: This file implements local and remote RISC-V KVM instruction-cache and TLB invalidation. It emits HFENCE/HINVAL sequences for G-stage and VS-stage translations, sanitizes stale VMID mappings on CPU migration, processes vCPU fence requests, queues bounded HFENCE work, and broadcasts requests to selected vCPUs.

Important APIs/types/functions: Local flush APIs include `kvm_riscv_local_hfence_gvma_vmid_gpa/all`, `kvm_riscv_local_hfence_gvma_gpa/all`, `kvm_riscv_local_hfence_vvma_asid_gva/all`, `kvm_riscv_local_hfence_vvma_gva/all`, and `kvm_riscv_local_tlb_sanitize`. Request processors include `kvm_riscv_fence_i_process`, `kvm_riscv_tlb_flush_process`, `kvm_riscv_hfence_vvma_all_process`, and `kvm_riscv_hfence_process`. Broadcast APIs include `kvm_riscv_fence_i`, all `kvm_riscv_hfence_*` variants, and `kvm_arch_flush_remote_tlbs_range`.

Control flow: Local range flushes fall back to whole-scope flushes when the requested range spans too many pages, otherwise use Svinval sequences if available or legacy HFENCE instructions. VS-stage flushes temporarily swap `HGATP` to the target VMID before issuing VVMA operations, then restore it. Remote requests select vCPUs by hart base/mask, enqueue detailed HFENCE data into a per-vCPU ring, and fall back to broader requests when the ring is full. vCPU request processing drains the queue and dispatches either NACL accelerated HFENCEs or local instructions.

State and persistence: Each vCPU has a bounded `hfence_queue` with head/tail protected by `hfence_lock`. `last_exit_cpu` and the VMID static/vendor quirk state control migration sanitization. Firmware-event PMU counters are incremented for received fence operations.

Dependencies and integration points: It depends on RISC-V instruction-definition macros, Svinval extension detection, KVM request bits, NACL HFENCE helpers, VMID state, and PMU firmware counters. G-stage mapping code uses these APIs after PTE changes.

Risks and test signals: Incorrect VMID/HGATP swapping can flush the wrong address space or leave host state corrupted. Queue overflow deliberately broadens invalidation and must remain conservative. Tests should cover Svinval and non-Svinval hosts, no-VMID hosts, vendor VS-stage TLB quirk, hart-mask selection, queue-full fallback, NACL and direct paths, instruction-cache flush requests, and range flushes crossing fallback thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/trace.h -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/trace.h

Purpose: This header defines RISC-V KVM tracepoints for guest entry and exit. It gives ftrace/perf consumers a compact view of guest PC on entry and trap CSRs on exit.

Important APIs/types/functions: `TRACE_EVENT(kvm_entry)` records `vcpu->arch.guest_context.sepc` as `pc`. `TRACE_EVENT(kvm_exit)` records `sepc`, `scause`, `stval`, `htval`, and `htinst` from `struct kvm_cpu_trap`. `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` make the tracepoint definitions instantiate from `vcpu.c`.

Control flow: `vcpu.c` defines `CREATE_TRACE_POINTS` before including this header, which instantiates the tracepoints. The run loop calls `trace_kvm_entry(vcpu)` immediately before guest entry and `trace_kvm_exit(&trap)` after returning from guest mode and restoring interrupt state.

State and persistence: The header owns no runtime state beyond the generated tracepoint descriptors. Recorded data is transient trace-buffer state managed by the Linux tracing subsystem.

Dependencies and integration points: It depends on `linux/tracepoint.h`, `struct kvm_vcpu`, and `struct kvm_cpu_trap`. It integrates with the RISC-V vCPU run loop and generic Linux trace tooling under the `kvm` trace system.

Risks and test signals: Format-string stability matters for external tracing tools. The entry print format uses `"PC: 0x016%lx"`, which may be unusual compared with `%016lx` and should be checked if trace formatting is changed. Tests should enable KVM tracepoints, run a guest, and verify entry/exit records contain expected PC and trap CSR values without instrumentation recursion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu.c

Purpose: This file implements RISC-V KVM vCPU lifecycle, ioctls, interrupt state, MP state, load/put CSR and extension context switching, request handling, guest entry/exit, and the main `KVM_RUN` loop. It is the central integration point for timers, AIA, SBI, PMU, FP/vector state, NACL, G-stage VMID, and tracepoints.

Important APIs/types/functions: It defines vCPU stats descriptors/header and per-CPU `kvm_former_vcpu` for CSR reload elision. Lifecycle functions include `kvm_arch_vcpu_create`, `postcreate`, and `destroy`; runtime helpers include `kvm_arch_vcpu_load`, `put`, `kvm_arch_vcpu_ioctl_run`, and `kvm_riscv_vcpu_enter_exit`. Interrupt APIs include flush/sync/set/unset/has-interrupts. MP state, guest-debug, one-reg ioctls, and reset logic are also implemented.

Control flow: vCPU creation initializes config, ISA, vendor IDs, hfence queue, vector/timer/PMU/AIA/SBI state, then resets the vCPU. Nonboot vCPUs are powered off after creation. `KVM_RUN` first completes pending userspace MMIO/SBI/CSR exits, checks signals, loads the vCPU, updates VMID, handles requests, updates AIA hardware, disables preemption/interrupts, flushes pending interrupts into HVIP/HVICTL, sanitizes local TLB state, traces entry, switches to guest through NACL or direct assembly, syncs interrupts/timers after exit, traces exit, and dispatches traps through `vcpu_exit.c`.

State and persistence: Guest context, CSRs, smstateen CSRs, interrupt bitmaps, MP state, reset state, hfence queue, MMU cache, PMU/timer/AIA/SBI/vector/FP state all persist in `vcpu->arch`. Host FP/vector and select CSRs are saved while guest state is loaded. `csr_dirty` forces CSR reload when ioctls changed saved CSR state. `ran_atleast_once` freezes configuration that must not change after execution.

Dependencies and integration points: It depends on KVM core vCPU APIs, SRCU, preempt notifiers, NACL, MMU/VMID/TLB helpers, timers, SBI emulation, PMU, AIA, vector/FP save-restore, one-reg handling, dirty-ring requests, and tracepoints.

Risks and test signals: The guest-entry path is ordering-sensitive: request checks, SRCU unlock, interrupt flush, mode transition, and local IRQ state must match KVM expectations. CSR reload elision requires every mutating ioctl to set `csr_dirty`. Tests should cover vCPU create/destroy, KVM_RUN returns for MMIO/SBI/CSR, signals, sleep/wakeup, reset requests, interrupt set/unset races, guest debug breakpoint exits, CPU migration, NACL and non-NACL entry, FP/vector preservation, and stats increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_config.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_config.c

Purpose: This file derives and loads the hypervisor configuration CSRs that shape guest-visible behavior for a vCPU. It initializes default exception/interrupt delegation, adjusts delegation for guest debugging, enables HENVCFG/HSTATEEN bits according to the configured guest ISA, and writes those CSRs through NACL or direct CSR paths.

Important APIs/types/functions: `KVM_HEDELEG_DEFAULT` delegates common guest exceptions such as illegal instruction, syscall, and page faults. `KVM_HIDELEG_DEFAULT` delegates VS software, timer, and external interrupts. Public functions are `kvm_riscv_vcpu_config_init`, `kvm_riscv_vcpu_config_guest_debug`, `kvm_riscv_vcpu_config_ran_once`, and `kvm_riscv_vcpu_config_load`.

Control flow: vCPU creation initializes default delegation. Guest debug toggles breakpoint delegation so breakpoints exit to userspace when debug is enabled and marks CSRs dirty. Just before the first run, `ran_once` adds HENVCFG bits for Svpbmt, Sstc, Zicbom, Zicboz, and Svadu-without-Svade, and HSTATEEN bits for HSENVCFG, AIA, IMSIC, ISELECT, and nested stateen exposure when the host supports Smstateen. Load writes HEDELEG/HIDELEG/HENVCFG and optional high halves/HSTATEEN through NACL shared memory when available or direct CSR writes otherwise.

State and persistence: The derived configuration persists in `vcpu->arch.cfg`. It is mostly immutable after first run except guest-debug toggling of breakpoint delegation. CSR writes are runtime CPU state and are refreshed by `kvm_arch_vcpu_load`.

Dependencies and integration points: It depends on ISA policy and vCPU ISA bitmaps, NACL CSR sync, RISC-V CSR/HENVCFG/HSTATEEN definitions, guest debug ioctls, and the vCPU load fast path in `vcpu.c`.

Risks and test signals: Missing HENVCFG/HSTATEEN bits can advertise an extension without granting access to its CSRs or behavior; overly broad bits expose unsupported state. Tests should cover first-run derivation for each gated extension, guest debug enable/disable before and after load, 32-bit high CSR writes, NACL/direct load equivalence, and `csr_dirty` forcing reload after debug changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_exit.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_exit.c

Purpose: This file dispatches traps returned from guest execution. It handles G-stage page faults, unprivileged guest memory instruction reads, redirecting exceptions back into the guest, SBI ecalls, virtual instruction traps, MMIO faults, debug exits, and diagnostic logging for unexpected errors.

Important APIs/types/functions: `gstage_page_fault` resolves guest page faults to memory-slot mappings or MMIO emulation. `kvm_riscv_vcpu_unpriv_read` uses HLV/HLVX instructions under a temporary trap vector to safely read guest memory or instructions. `kvm_riscv_vcpu_trap_redirect` synthesizes guest VS exception state. `vcpu_redirect` redirects only when the trap came from virtual supervisor mode. `kvm_riscv_vcpu_exit` is the top-level trap dispatcher.

Control flow: G-stage faults reconstruct the fault GPA from `htval` and `stval`, look up a memslot/HVA, route invalid or write-protected accesses to MMIO load/store emulation, or call `kvm_riscv_mmu_map` to populate G-stage PTEs. Trap dispatch ignores host interrupts, increments PMU firmware counters and stats for selected guest exceptions, redirects guest-visible faults when `HSTATUS.SPV` is set, invokes virtual instruction emulation for virtual instruction faults, calls SBI emulation for supervisor ecalls, and exits to userspace on breakpoints.

State and persistence: Redirecting a trap mutates VSSTATUS, VSCAUSE, VSTVAL, VSEPC, guest `sepc`, and guest privilege bits so the guest resumes at its exception vector. MMU mapping persists in G-stage page tables. No long-lived file-local state is kept.

Dependencies and integration points: It depends on CSR accessors, hypervisor load instructions from `insn-def.h`, MMU mapping, MMIO/instruction emulation in `vcpu_insn.c`, SBI emulation, PMU firmware counters, and the vCPU run loop.

Risks and test signals: Fault GPA reconstruction and transformed instruction handling are architecture-sensitive. Trap redirection must preserve SPP/SPIE/SIE semantics exactly. Tests should cover guest page faults mapping RAM, MMIO load/store fallback, instruction fetch faults while decoding trapped instructions, illegal/misaligned/access redirects, SBI exits, breakpoint debug exits, and error logging for unsupported traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_fp.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_fp.c

Purpose: This file manages guest and host floating-point state for RISC-V KVM and exposes F/D register state through the KVM one-reg ABI. It resets guest FS state, lazily saves dirty guest FP registers, restores guest FP state when enabled, preserves host FP state, and validates user register access sizes.

Important APIs/types/functions: Under `CONFIG_FPU`, core functions are `kvm_riscv_vcpu_fp_reset`, `kvm_riscv_vcpu_guest_fp_save`, `kvm_riscv_vcpu_guest_fp_restore`, `kvm_riscv_vcpu_host_fp_save`, and `kvm_riscv_vcpu_host_fp_restore`. ABI functions are `kvm_riscv_vcpu_get_reg_fp` and `kvm_riscv_vcpu_set_reg_fp` for `KVM_REG_RISCV_FP_F` and `KVM_REG_RISCV_FP_D`.

Control flow: Reset sets guest `sstatus.FS` to INITIAL when F or D is exposed and OFF otherwise. Guest save only writes back registers when FS is DIRTY, choosing D save before F when D is available, then marks FS CLEAN. Restore loads F/D registers when FS is not OFF and marks clean. Host save/restore mirrors host availability. One-reg handlers select fcsr or f[0..31], enforce 32-bit F register/fcsr or 64-bit D register sizes, use nospec indexing, and copy values to or from userspace.

State and persistence: Guest FP state persists inside `vcpu->arch.guest_context.fp`, plus FS bits in guest `sstatus`. Host temporary state persists in `vcpu->arch.host_context` while guest state is active. One-reg writes directly mutate saved guest FP state.

Dependencies and integration points: It depends on RISC-V FPU assembly helpers, cpufeature/ISA checks, KVM one-reg dispatch in `vcpu_onereg.c`, and vCPU load/put in `vcpu.c`.

Risks and test signals: FS state must correctly track dirty/clean/off or guest FP state can be lost or host FP state corrupted. Tests should cover F-only, D, and no-FPU guests, one-reg get/set size validation, fcsr handling, guest dirty-save behavior, host FP preservation across KVM_RUN, and build coverage with `CONFIG_FPU` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_fp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_insn.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_insn.c

Purpose: This file emulates trapped guest instructions that KVM can handle in-kernel and prepares exits for userspace emulation. It covers virtual instruction faults for SYSTEM opcodes, CSR accesses, WFI/WRS behavior, illegal/virtual trap injection, MMIO load/store decoding, and completion of MMIO or CSR exits.

Important APIs/types/functions: `struct insn_func` and `struct csr_func` define decode tables. Trap helpers are `truly_illegal_insn` and `truly_virtual_insn`. Runtime APIs include `kvm_riscv_vcpu_wfi`, `kvm_riscv_vcpu_csr_return`, `kvm_riscv_vcpu_virtual_insn`, `kvm_riscv_vcpu_mmio_load`, `kvm_riscv_vcpu_mmio_store`, and `kvm_riscv_vcpu_mmio_return`. CSR handling integrates AIA, HPM counter, and seed CSR callbacks.

Control flow: Virtual instruction emulation uses `stval` when available or unprivileged instruction fetch when not, rejects compressed SYSTEM traps as illegal, then dispatches SYSTEM instructions. CSR instructions decode read/write masks and new values, populate `run->riscv_csr`, try in-kernel CSR handlers first, complete in-kernel reads immediately, or exit to userspace. WFI may halt the vCPU until runnable; WRS calls spin/yield handling. MMIO load/store decode transformed `htinst` or fetch the original instruction, determine width/sign-extension and source/destination register, try KVM MMIO bus access, and either complete immediately or populate `run->mmio` for userspace.

State and persistence: Decode state persists across userspace exits in `vcpu->arch.csr_decode` and `vcpu->arch.mmio_decode`, including return-handled flags to avoid double completion. Instruction completion advances guest `sepc`; load completion writes the destination register.

Dependencies and integration points: It depends on RISC-V instruction masks, compressed instruction helpers, CSR emulation from AIA/PMU, MMIO bus, unprivileged read/trap redirection in `vcpu_exit.c`, and the run-loop return handling in `vcpu.c`.

Risks and test signals: Instruction decoding must distinguish signed/unsigned loads, compressed register aliases, transformed instruction lengths, and misaligned MMIO. Tests should cover all load/store widths on RV32/RV64, compressed MMIO forms, in-kernel versus userspace MMIO, CSR read/write/set/clear/immediate variants, seed CSR userspace exits, WFI wakeup, WRS accounting, and illegal/virtual trap injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_onereg.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_onereg.c

Purpose: This file implements the RISC-V KVM one-reg ABI for vCPU configuration, core registers, CSRs, ISA extensions, timers, FP, vector, SBI extension state, and register-list enumeration. It is the main userspace migration/configuration interface for vCPU architectural state.

Important APIs/types/functions: `kvm_riscv_vcpu_setup_isa` initializes the guest ISA bitmap from host-supported and allowed extensions. Get/set helpers cover config registers, core registers, general/AIA/Smstateen CSRs, single and multi ISA extension registers, and register-index copy/count functions. Public APIs are `kvm_riscv_vcpu_num_regs`, `kvm_riscv_vcpu_copy_reg_indices`, `kvm_riscv_vcpu_set_reg`, and `kvm_riscv_vcpu_get_reg`.

Control flow: Config getters return base ISA, cache block sizes, vendor IDs, and SATP mode. Config setters allow base ISA and vendor ID changes only before first run and validate block sizes as read-only host properties. Core access maps PC, GPRs, and mode to `guest_context`. CSR access dispatches to general, AIA, or Smstateen subtypes and marks `csr_dirty` on successful writes. ISA extension access supports old single-register and newer multi-register enable/disable masks, applying host availability plus policy from `isa.c`. Register-list construction emits only state supported by the current guest ISA.

State and persistence: One-reg writes directly modify persistent vCPU state: ISA bitmaps, vendor IDs, guest context, CSR shadows, timer/FP/vector/SBI state, and dirty flags. Many configuration fields become immutable once `ran_atleast_once` is true. `csr_dirty` persists until the next vCPU load reloads CSRs.

Dependencies and integration points: It depends on cpufeature and ISA policy, cache-block globals, AIA CSR helpers, timer/FP/vector/SBI one-reg helpers, KVM user-copy APIs, and the vCPU ioctl path in `vcpu.c`.

Risks and test signals: Register ID encoding and size validation are ABI-critical for migration. Multi-extension setters currently ignore individual helper return values inside the mask loop, so tests should confirm unsupported bits do not silently produce unexpected guest state. Tests should cover GET_REG_LIST counts against actual copied indices, pre-run/post-run config mutability, CSR dirty reload, AIA/Smstateen conditional CSR exposure, RV32/RV64 sizes, vector variable-size registers, and migration round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_onereg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_pmu.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_pmu.c

Purpose: This file implements the RISC-V KVM virtual PMU and SBI PMU extension backend. It maps SBI PMU event IDs to Linux perf events or firmware counters, manages virtual counter allocation/start/stop/read, handles overflow injection, exposes snapshot shared memory, and initializes/deinitializes per-vCPU PMU state.

Important APIs/types/functions: Event helpers include `kvm_pmu_get_perf_event_type`, `kvm_pmu_get_perf_event_config`, fixed/programmatic counter selection, and `kvm_pmu_create_perf_event`. Runtime APIs include `kvm_riscv_vcpu_pmu_incr_fw`, `kvm_riscv_vcpu_pmu_read_hpm`, snapshot/event-info helpers, `kvm_riscv_vcpu_pmu_num_ctrs`, `ctr_info`, `ctr_cfg_match`, `ctr_start`, `ctr_stop`, firmware counter reads, `kvm_riscv_vcpu_pmu_init`, `deinit`, and `reset`.

Control flow: PMU init only succeeds when host Sscofpmf privilege filtering is available and host PMU info reports usable counters. It creates virtual hardware counters plus firmware counters, reserving counter 1 for time and assigning CSR numbers sequentially. Counter configuration validates masks, maps events, selects fixed or free programmable counters, creates pinned perf events for hardware/raw/cache events, or marks firmware events. Start sets initial values from flags or snapshot memory, clears overflow, and enables perf or firmware counting. Stop disables counters, optionally snapshots values and overflow bits to guest memory, and optionally resets/release events. Perf overflow stops the event, adjusts sample period, marks overflow, injects `IRQ_PMU_OVF`, then restarts.

State and persistence: `struct kvm_pmu` persists counter metadata, `pmc_in_use`, `pmc_overflown`, firmware event counters, snapshot address, and snapshot buffer. Each `struct kvm_pmc` persists event index, accumulated counter value, perf event pointer, started flag, and counter info. Deinit releases perf events, clears bitmaps, frees snapshot memory, and resets firmware counters.

Dependencies and integration points: It depends on Linux perf, RISC-V PMU host APIs, SBI PMU definitions, KVM guest-memory read/write, AIA/interrupt delivery for PMU overflow, CSR emulation via `vcpu_insn.c`, and firmware-event increments from exit/TLB paths.

Risks and test signals: Perf event lifecycle and overflow handling can leak host counters or inject stale overflows if reset paths miss state. Snapshot shared memory requires careful guest address validation and RV32 high-address handling. Tests should cover PMU absent hosts, fixed cycle/instret mapping, programmable hardware/cache/raw events, firmware event counters, overflow interrupt injection and clear, start/stop/reset error codes, snapshot init/take behavior, RV32 high reads, and vCPU teardown releasing all perf events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_pmu.c -->
