# Research: subset-b-000686

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/pgtable.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/pgtable.c

## Purpose
This file implements the standalone ARM64 KVM page-table engine used by hyp stage-1 mappings and guest stage-2 mappings. It provides a generic page-table walker, hyp mapping/unmapping helpers, VTCR construction, stage-2 map/unmap/attribute/age/flush/split logic, and destruction helpers. It is a core correctness boundary for guest isolation, hyp mappings, break-before-make ordering, cache maintenance, and TLB invalidation.

## Important APIs, Types, and Functions
- `struct kvm_pgtable_walk_data` carries walker state: current address, start/end range, and callback wrapper.
- `kvm_pgtable_walk()` and `kvm_pgtable_get_leaf()` are the generic traversal interfaces for all later operations.
- Hyp stage-1 APIs include `kvm_pgtable_hyp_init()`, `kvm_pgtable_hyp_map()`, `kvm_pgtable_hyp_unmap()`, `kvm_pgtable_hyp_destroy()`, and `kvm_pgtable_hyp_pte_prot()`.
- Stage-2 APIs include `kvm_get_vtcr()`, `kvm_pgtable_stage2_map()`, `kvm_pgtable_stage2_annotate()`, `kvm_pgtable_stage2_unmap()`, `kvm_pgtable_stage2_wrprotect()`, `kvm_pgtable_stage2_mkyoung()`, `kvm_pgtable_stage2_test_clear_young()`, `kvm_pgtable_stage2_relax_perms()`, `kvm_pgtable_stage2_flush()`, `kvm_pgtable_stage2_split()`, `kvm_pgtable_stage2_create_unlinked()`, `__kvm_pgtable_stage2_init()`, and stage-2 destroy/free helpers.
- The file relies on `struct kvm_pgtable_mm_ops` for allocation, refcounting, address conversion, cache maintenance, and deferred freeing.

## Control Flow
The generic walker aligns ranges to pages, descends from the PGD start level, and invokes callbacks for leaf, table pre-order, and table post-order visits. Callbacks may replace PTEs and request retries through `-EAGAIN`; callers outside fault handling can use `KVM_PGTABLE_WALK_IGNORE_EAGAIN`.

Hyp mapping builds leaf entries when block/page alignment allows it, allocates child tables otherwise, and stores new entries with release ordering. Hyp unmapping clears leaves and empty tables, performs stage-1 TLBI, syncs, and drops refcounts.

Stage-2 mapping first computes memory attributes and access/execute permissions, tries to install a leaf, and if needed breaks an existing PTE, performs cache/instruction maintenance, then makes the new PTE visible. Table pre-order callbacks allow replacing a table with a block mapping and freeing the detached table. Leaf callbacks allocate tables when the requested mapping cannot be represented at the current level.

Stage-2 unmap clears valid or counted invalid entries, optionally defers TLBI range invalidation, performs dcache maintenance when FWB is absent, and recursively frees empty tables. Attribute walkers update write protection, access flags, executable permissions, and access-age state without rebuilding the tree when possible. Split walkers replace block mappings with prepopulated lower-level tables from a memory cache.

## State and Persistence
Persistent state is the content of page-table pages plus refcounts held on containing table pages. Stage-2 can represent invalid but counted PTEs for nonzero ownership annotations and temporary locked PTEs for concurrent walkers. The code uses `smp_store_release()`, `READ_ONCE()`, `WRITE_ONCE()`, `cmpxchg()`, DSB/ISB barriers, and explicit TLB invalidation to preserve architectural ordering. The page table's `ia_bits`, `start_level`, `flags`, `mmu`, and optional `force_pte_cb` configure behavior for the lifetime of the table.

## Dependencies and Integration Points
This file depends on ARM64 page-table format macros from `asm/kvm_pgtable.h` and `asm/stage2_pgtable.h`, CPU feature checks such as LPA2, XNX, FWB, HAFDBS, BTI, and TLB range support, and hyp-call TLB helpers such as `__kvm_tlb_flush_vmid_ipa`. It is consumed heavily by `arch/arm64/kvm/mmu.c`, pKVM variants via `KVM_PGT_FN()`, nested virtualization shadow stage-2 code, dirty logging, memory-notifier aging, and hyp mapping setup.

## Risks and Edge Cases
The main risks are stale TLB entries after permission or table replacement, incorrect cache maintenance for noncoherent or non-FWB systems, refcount leaks on partial failures, races in shared walks, and block mappings that cover too much memory. The code mitigates these with locked invalid PTEs, break-before-make sequencing, `-EAGAIN` retry semantics, deferred table freeing through callbacks supplied by the caller, alignment checks, and explicit warnings on impossible levels or invalid permissions. Stage-2 permission relaxation preserves software bits carefully, while full remaps drop and reconstruct entries.

## Test Signals
Useful signals include KVM selftests that stress dirty logging, access-flag aging, hugepage split/collapse, memory slot moves/deletes, MTE guest memory, nested stage-2 translation, pKVM protected guests, and concurrent vCPU faults. Kernel test runs should also monitor lockdep, RCU warnings, KASAN/KCSAN, refcount underflow, TLB shootdown failures, and guest memory corruption under heavy MMU notifier churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/pgtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vgic-v2-cpuif-proxy.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vgic-v2-cpuif-proxy.c

## Purpose
This hyp helper emulates selected trapped accesses to the GICv2 virtual CPU interface (`GICV`) directly in EL2. It avoids a full exit for normal 32-bit aligned accesses below the deactivate register while preserving architectural behavior for illegal or unsupported accesses.

## Important APIs, Types, and Functions
- `__vgic_v2_perform_cpuif_access(struct kvm_vcpu *vcpu)` is the sole exported function in the file.
- `__is_be()` determines the guest endianness from AArch32 SPSR or AArch64 SCTLR.
- It uses `struct vgic_dist`, `kvm_vgic_global_state.vcpu_hyp_va`, and `kvm_vcpu_dabt_*()` syndrome helpers.

## Control Flow
The handler reconstructs the fault IPA from `FAR`/`HPFAR`, verifies that it falls within the guest's GICv2 CPU interface window, rejects non-32-bit and unaligned accesses by skipping the instruction and returning `-1`, and leaves deactivate-register accesses to the normal exit path. For accepted accesses it computes the hyp VA of the backing GICV register, byte-swaps when the guest is big-endian, performs `readl_relaxed()` or `writel_relaxed()`, updates the target guest register for reads, skips the instruction, and returns `1`.

## State and Persistence
The persistent state is the real or emulated GICV register state behind `vcpu_hyp_va`; this file does not maintain its own storage. Guest architectural state changes are limited to the destination register for reads and the PC advance.

## Dependencies and Integration Points
It integrates with the hyp data-abort exit path and VGIC global state. It depends on fault-syndrome helpers, `kern_hyp_va()` conversion for `vcpu->kvm`, and the global VGIC CPU interface base configured by the main VGIC code.

## Risks and Edge Cases
Risks include incorrect endian conversion, mishandling illegal access sizes, and accidentally emulating deactivate operations that need full VGIC overflow handling. The function deliberately returns `0` for non-GICV and deactivate accesses so the normal KVM path can handle them.

## Test Signals
Test GICv2 guests with little- and big-endian modes, unaligned and wrong-size MMIO, interrupt acknowledge/priority/EOI register accesses, and deactivate accesses that must still exit. Tracepoints around guest exits should show fewer full exits for valid CPU-interface accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vgic-v2-cpuif-proxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vgic-v3-sr.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vgic-v3-sr.c

## Purpose
This file implements hyp-side save/restore and trap emulation for the GICv3 virtual CPU interface. It manages list registers, active priority registers, VMCR/HCR state, SRE/v2 compatibility mode, GIC configuration probing, and emulation of trapped ICC_* system registers, including nested-virtualization forwarding rules.

## Important APIs, Types, and Functions
- `__gic_v3_get_lr()` and `__gic_v3_set_lr()` read/write the 16 possible `ICH_LR<n>_EL2` registers.
- `__vgic_v3_save_state()`, `__vgic_v3_restore_state()`, `__vgic_v3_activate_traps()`, and `__vgic_v3_deactivate_traps()` are the world-switch core.
- `__vgic_v3_save_aprs()`, `__vgic_v3_restore_vmcr_aprs()`, and APR helpers preserve priority state.
- `__vgic_v3_init_lrs()` and `__vgic_v3_get_gic_config()` initialize/probe CPU-interface capability.
- `__vgic_v3_perform_cpuif_access()` dispatches trapped ICC_* sysreg accesses to local emulation helpers.
- Trap emulation covers IAR, EOIR, DIR, IGRPEN, BPR, APxR, HPPIR, PMR, RPR, and CTLR views.

## Control Flow
Save state first synchronizes memory-mapped and sysreg GIC views when needed, snapshots non-empty LRs, clears hardware LRs, saves VMCR, merges EOIcount from HCR when LRENPIE is active, disables ICH_HCR, and reads MISR to force nested effects. Restore writes HCR with trap bits, restores LRs, and synchronizes for non-SRE guests.

Trap activation programs `ICC_SRE_EL1`/`ICC_SRE_EL2` according to whether the guest uses the system-register interface, whether v2 compatibility is present, and whether global CPU-interface trapping or ITS VPE state requires ICH_HCR enablement. Deactivation reverses this and clears HCR when traps were enabled only for emulation.

The CPU-interface access handler rejects non-VGICv3 models, decodes AArch32 or AArch64 sysreg ISS, checks nested forwarding through HFGRTR/HFGWTR/HCR trap bits, chooses a register-specific handler, reads VMCR, invokes the handler, skips the instruction, and returns whether EL2 handled it. IAR emulation selects the highest-priority pending LR, checks group enable and PMR/HAP priority, transitions LR state to active, sets APR priority, and returns the virtual INTID. EOIR/DIR drop active priority and deactivate LRs or bump EOIcount when deactivation cannot be represented locally.

## State and Persistence
State is persisted in `struct vgic_v3_cpu_if`: `vgic_lr[]`, `used_lrs`, `vgic_vmcr`, `vgic_hcr`, `vgic_sre`, APR arrays, and ITS VPE state. Hardware state lives in ICH/ICC sysregs and is transferred across guest entry/exit. Priority and active state are encoded both in LRs and APR registers; misordering can cause lost interrupts or wrong priority masking.

## Dependencies and Integration Points
The file depends on GICv3 sysreg accessors, `vgic_ich_hcr_trap_bits()`, `static_branch` feature keys for v2 compatibility and CPU-interface trapping, KVM sysreg/fault helpers, nested-virtualization sysregs, and VGIC data structures from `../../vgic/vgic.h`. It is compiled into VHE hyp via the VHE Makefile and is also shared by other hyp build variants.

## Risks and Edge Cases
Risks include failing to clear stale LRs, violating required barriers between memory-mapped and sysreg GIC views, wrong APR count derived from VTR priority bits, incorrect group/BPR priority comparisons, and mishandling nested forwarding. GICv2 compatibility is especially sensitive because SRE programming changes whether Group0 interrupts appear as FIQs. DIR/EOIR behavior also must distinguish LPIs, EOImode, and hardware-backed physical interrupts.

## Test Signals
Use KVM VGIC selftests and guest stress tests covering GICv3, GICv2-on-v3 compatibility, nested VGIC traps, LPI and non-LPI interrupts, EOImode 0/1, priority masking, big LR counts, and live migration state save/restore. Useful symptoms include stuck interrupts, spurious IAR reads, EOIcount overflow exits, and mismatched interrupt priority after nested transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vgic-v3-sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vgic-v5-sr.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vgic-v5-sr.c

## Purpose
This file adds hyp-side GICv5 CPU-interface save/restore helpers. It handles VMCR/APR, ICSR, and private interrupt state for architected and implementation-defined PPIs, including direct virtual interrupt state.

## Important APIs, Types, and Functions
- `__vgic_v5_save_apr()` saves `ICH_APR_EL2`.
- `__vgic_v5_restore_vmcr_apr()` disables v3 compatibility mode and restores VMCR/APR.
- `__vgic_v5_save_ppi_state()` saves PPI active/pending snapshots and priority registers.
- `__vgic_v5_restore_ppi_state()` restores DVI, active, enable, pending, and priority state.
- `__vgic_v5_save_state()` and `__vgic_v5_restore_state()` save/restore VMCR and ICSR-level state.

## Control Flow
Save reads PPI active and pending registers into per-host hyp data, copies priority registers into the vCPU interface state, handles a 64- or 128-private-IRQ layout, and disables DVI after the snapshot. Restore enables guest DVI bits, restores active and enable state, computes pending state for non-DVI PPIs from host-saved state, restores priority registers, and clears the high bank when the implementation exposes only 64 private IRQs.

## State and Persistence
Persistent state is split between `struct vgic_v5_cpu_if` fields and per-CPU `vgic_v5_ppi_state` host data. The code assumes `VGIC_V5_NR_PRIVATE_IRQS` is divisible by 64 and only supports 64 or 128 private IRQ storage shapes. Compatibility mode is controlled through `SYS_ICH_VCTLR_EL2`.

## Dependencies and Integration Points
It depends on GICv5 sysreg definitions from `linux/irqchip/arm-gic-v5.h`, hyp data accessors, bitmap helpers, and the broader VGIC world-switch sequence that calls these helpers around guest entry/exit. The VHE Makefile includes it with other hyp VGIC code.

## Risks and Edge Cases
The sensitive areas are bitmap bank alignment, clearing high-bank registers on 64-PPI systems, and preserving host pending state only for PPIs not delegated through DVI. Incorrect ordering can leak host PPI state into guests or lose virtual pending state.

## Test Signals
GICv5-capable test coverage should exercise 64- and 128-PPI configurations, DVI-enabled and non-DVI PPIs, priority migration, save/restore across vCPU preemption, and compatibility transitions between GICv3 and GICv5 CPU-interface modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vgic-v5-sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/Makefile

## Purpose
This Makefile defines the VHE hyp object set and compiler/assembler defines for ARM64 KVM when the host kernel runs with Virtualization Host Extensions.

## Important APIs, Types, and Functions
It sets `asflags-y` and `ccflags-y` to `-D__KVM_VHE_HYPERVISOR__`, suppresses override-initializer warnings for `switch.o`, and builds `timer-sr.o`, `sysreg-sr.o`, `debug-sr.o`, `switch.o`, `tlb.o`, plus shared hyp objects from the parent directory such as VGIC, entry, FPSIMD, hyp entry, exception, and GICv5 support.

## Control Flow
There is no runtime control flow. The build flow marks these objects as VHE hyp code and links a mixture of VHE-specific source files and common hyp code into the KVM hyp object set.

## State and Persistence
The file persists build configuration only. Its `__KVM_VHE_HYPERVISOR__` define changes conditional compilation in included hyp headers and source code.

## Dependencies and Integration Points
It integrates with the ARM64 KVM build system and determines that VHE uses common `../vgic-v3-sr.o`, `../vgic-v2-cpuif-proxy.o`, `../entry.o`, `../fpsimd.o`, `../hyp-entry.o`, `../exception.o`, and `../vgic-v5-sr.o`.

## Risks and Edge Cases
Missing an object here can silently remove a hyp entry point required by VHE world switch. Wrong flags can compile code with nVHE assumptions or expose incompatible symbols. The warning override for `switch.o` is deliberate because the exit-handler array uses range initialization.

## Test Signals
Build tests should cover VHE-enabled ARM64 configurations, nested virtualization options, VGICv5 options, and warning-clean builds with W=1 where practical. Runtime smoke tests should confirm VHE guest entry, timer, sysreg, debug, and TLB paths resolve symbols from this object set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/debug-sr.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/debug-sr.c

## Purpose
This file provides VHE wrappers for switching debug register state between host and guest.

## Important APIs, Types, and Functions
- `__debug_switch_to_guest(struct kvm_vcpu *vcpu)` delegates to `__debug_switch_to_guest_common()`.
- `__debug_switch_to_host(struct kvm_vcpu *vcpu)` delegates to `__debug_switch_to_host_common()`.

## Control Flow
The VHE world-switch code calls the guest wrapper after restoring guest system registers and calls the host wrapper after restoring host system registers. The wrappers contain no VHE-specific policy beyond selecting the common implementation.

## State and Persistence
Debug state is held in vCPU and host CPU contexts managed by the common debug-switch helpers. This file does not allocate or persist independent state.

## Dependencies and Integration Points
It depends on `hyp/debug-sr.h`, `linux/kvm_host.h`, and `asm/kvm_hyp.h`. It is called from `hyp/vhe/switch.c` around `__guest_enter()`.

## Risks and Edge Cases
The file is small, but its placement in the world switch matters. Calling the wrappers in the wrong order could expose host breakpoints/watchpoints to the guest or lose guest debug state.

## Test Signals
Run guest debug-register selftests, breakpoint/watchpoint tests, single-step tests, and VHE guest entry/exit stress. Failures usually appear as unexpected debug exceptions, lost breakpoints, or host debug state corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/debug-sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/switch.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/switch.c

## Purpose
This is the VHE guest run and world-switch implementation. It computes HCR_EL2 for normal and nested guests, activates/deactivates traps, loads stage-2 context, handles fast hyp exits that can be resolved without returning to the host kernel, and restores host state after guest exit or hyp panic.

## Important APIs, Types, and Functions
- Per-CPU state: `kvm_host_data`, `kvm_hyp_ctxt`, and `kvm_hyp_vector`.
- `__compute_hcr()` merges KVM HCR policy with nested-virtualization guest HCR bits while excluding unsafe bits.
- `__activate_traps()` and `__deactivate_traps()` program HCR, timer offsets, CPTR traps, and exception vectors.
- `kvm_vcpu_load_vhe()` and `kvm_vcpu_put_vhe()` load/put long-lived vCPU sysregs and stage-2 state.
- Fast handlers include `kvm_hyp_handle_timer()`, `kvm_hyp_handle_eret()`, `kvm_hyp_handle_tlbi_el2()`, `kvm_hyp_handle_cpacr_el1()`, `kvm_hyp_handle_zcr_el2()`, and `kvm_hyp_handle_impdef()`.
- `__kvm_vcpu_run_vhe()` is the core run loop; `__kvm_vcpu_run()` wraps it with DAIF/PMR handling.
- `hyp_panic()` and `kvm_unexpected_el2_exception()` cover fatal hyp paths.

## Control Flow
On vCPU load, VHE stores the running vCPU in per-CPU host data, switches sysregs, activates common traps, and loads stage-2. The run loop lazily switches FPSIMD to the guest, saves host common state, activates traps, adjusts the guest PC, restores guest return state, switches debug state, enters the guest, and repeats while `fixup_guest_exit()` can handle exits locally. When a real exit remains, it saves guest state, deactivates traps, restores host state and debug state, issues an ISB, returns FPSIMD to the host, and saves 32-bit FP exception state if needed.

Fast exit handling synchronizes PSTATE, fixes virtual EL2 mode bits for nested guests, and dispatches by ESR class. Timer reads in virtual EL2 context can be satisfied locally. ERET from a VHE guest hypervisor can be converted to a canonical EL1 return when no forwarding is required. Nested EL2 TLBI operations can be remapped to EL1 operations through `__kvm_tlbi_s1e2()`. CPACR_EL1 accesses in virtual hyp context are redirected to CPTR_EL2 state. ZCR_EL2 forces FP context loading before slow-path handling.

## State and Persistence
State spans per-CPU host data flags, `__hyp_running_vcpu`, guest/host CPU contexts, vCPU sysreg arrays, HCR_EL2, VNCR_EL2 mappings, VBAR_EL1, timer CVAL/offset registers, CPTR/FP ownership, and debug registers. The code preserves the invariant that a vCPU entered in virtual hyp context exits in virtual hyp context.

## Dependencies and Integration Points
It depends on common hyp trap helpers, sysreg save/restore code, stage-2 loading, arch timer helpers, FPSIMD/SVE/SME handling, nested virtualization helpers, pointer-auth ERET authentication, PMR/DAIF interrupt masking, and VHE-specific vectors. It integrates with `sysreg-sr.c`, `debug-sr.c`, `tlb.c`, and the generic KVM vCPU run path.

## Risks and Edge Cases
Risks include HCR bits leaking guest control into host execution, incorrect virtual EL2 PSTATE fixup, timer CVAL offset mistakes when CNTPOFF is present, failing to restore host vectors, and fast-handling an exit that should be forwarded to a nested hypervisor. Erratum handling requires stage-1 and stage-2 to be configured before clearing TGE, and TLB handling must consider VNCR mappings that force slow-path processing.

## Test Signals
Test VHE guest entry/exit, nested virtualization with virtual EL2, timer virtualization with and without ECV/CNTPOFF, nested TLBI, CPACR/FP/SVE/SME traps, pointer-auth ERET, PMU implementation-defined traps, and hyp panic paths. Lockdep, KASAN, kprobes exclusion, and tracepoints around exit reasons are useful regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/sysreg-sr.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/sysreg-sr.c

## Purpose
This file implements VHE system-register save/restore for host, guest EL1, and virtual EL2 contexts. It lets KVM avoid saving all EL1-visible state on every exit while still handling nested virtualization cases where the guest runs a virtual hypervisor.

## Important APIs, Types, and Functions
- `__sysreg_save_vel2_state()` and `__sysreg_restore_vel2_state()` translate between the CPU's EL1 register view and the vCPU's virtual EL2 sysreg array.
- `sysreg_save_host_state_vhe()`, `sysreg_save_guest_state_vhe()`, `sysreg_restore_host_state_vhe()`, and `sysreg_restore_guest_state_vhe()` wrap common and return-state helpers.
- `__vcpu_load_switch_sysregs()` loads guest/user/EL1 or virtual EL2 state on vCPU load.
- `__vcpu_put_switch_sysregs()` saves guest state and restores host user state on vCPU put.
- `__mpam_guest_load()` maps host EL0 MPAM partition state into guest MPAM1 when supported.

## Control Flow
On load, the host user state is saved, nested guests receive a DSB to complete speculative walks, AArch32 state is restored before sysregs for CPU errata, guest user state and MPAM state are restored, and either virtual EL2 or EL1 state is written to hardware. On put, virtual EL2 or EL1 state is saved, guest user and AArch32 state are saved, host user state is restored, and `SYSREGS_ON_CPU` is cleared.

Virtual EL2 save stores common EL1-compatible registers into their EL2 slots and, when E2H is set, saves compatible SCTLR/TTBR/TCR/CNTHCTL-style state directly from EL1-named sysregs. Restore reverses the process, translating SCTLR/CPTR/TTBR/TCR from EL2 to EL1 format when the virtual EL2 is not in E2H mode.

## State and Persistence
State persists in `struct kvm_cpu_context` and the vCPU sysreg array. The file handles PAR, TPIDR, ESR/AFSR/FAR, MAIR/AMAIR, VBAR, CONTEXTIDR, SCTLR/TTBR/TCR/TCR2, PIRE/PIR/POR, CNTHCTL/CNTKCTL, SP/ELR/SPSR, SCTLR2, VPIDR/VMPIDR, user registers, and AArch32 state. It marks whether sysregs are currently on CPU with `SYSREGS_ON_CPU`.

## Dependencies and Integration Points
It depends on common hyp sysreg helpers, nested virtualization translation helpers, MPAM support, feature predicates for TCR2/S1PIE/S1POE/SCTLR2, and the VHE run/load/put flow in `switch.c`.

## Risks and Edge Cases
Ordering is critical: AArch32 restore must precede sysregs for affected CPUs, speculative walks must complete before NV context switches, and CPACR/CPTR are special because CPACR_EL1 is trapped to keep CPTR_EL2's memory copy current. Incorrect E2H translation can corrupt a nested hypervisor's view of EL2 state.

## Test Signals
Run nested virtualization sysreg tests, VHE load/put stress, AArch32 guest tests, MPAM-enabled configurations, TCR2/S1PIE/S1POE/SCTLR2 feature combinations, and migration tests that compare sysreg state before and after repeated exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/sysreg-sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/timer-sr.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/timer-sr.c

## Purpose
This file provides the VHE hyp helper for programming the virtual counter offset register.

## Important APIs, Types, and Functions
- `__kvm_timer_set_cntvoff(u64 cntvoff)` writes `cntvoff_el2`.

## Control Flow
There is one direct control path: callers pass the desired virtual counter offset and the helper writes it to the EL2 register.

## State and Persistence
The only persistent state touched is hardware `CNTVOFF_EL2`. It affects the virtual counter view observed by guests.

## Dependencies and Integration Points
It depends on `asm/kvm_hyp.h` and is built into the VHE hyp object set. It integrates with ARM generic timer virtualization and world-switch timer state management in the wider KVM timer code.

## Risks and Edge Cases
Incorrect offset programming changes guest time. The helper intentionally does not add policy, validation, or barriers; callers must sequence it with timer context management.

## Test Signals
Guest clocksource stability tests, PV time tests, migration timekeeping tests, and repeated vCPU scheduling with changing offsets should expose regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/timer-sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/tlb.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/tlb.c

## Purpose
This file implements VHE TLB invalidation helpers for guest VMID contexts and nested virtualization TLBI emulation. Since VHE host execution normally uses EL2/EL0 translation, it temporarily changes HCR_EL2.TGE and stage-2 state so TLBI instructions target the guest EL1/EL0 regime.

## Important APIs, Types, and Functions
- `struct tlb_inv_context` saves previous MMU, IRQ flags, and erratum-protected TCR/SCTLR state.
- `enter_vmid_context()` and `exit_vmid_context()` switch into and out of the target VMID context.
- Flush APIs include `__kvm_tlb_flush_vmid_ipa()`, `__kvm_tlb_flush_vmid_ipa_nsh()`, `__kvm_tlb_flush_vmid_range()`, `__kvm_tlb_flush_vmid()`, `__kvm_flush_cpu_context()`, and `__kvm_flush_vm_context()`.
- `__kvm_tlbi_s1e2()` emulates guest EL2 stage-1 TLBI instructions by remapping them to EL1-equivalent operations.

## Control Flow
For VMID-specific operations, the helper saves IRQ state, records any currently running vCPU MMU that differs from the target, applies erratum protection by blocking speculative EL1 walks when required, loads the target stage-2 context, clears HCR.TGE, issues the relevant TLBI, synchronizes, restores host HCR, reloads the previous stage-2 context if needed, restores erratum-protected sysregs, and restores IRQ state.

IPA flushes invalidate stage-2 for the IPA and then all stage-1 entries to avoid refills from stale combined walks. Range flushes use range TLBI with worst-case page stride. Full VMID flush uses `vmalls12e1is`. CPU context flush also invalidates I-cache. The nested TLBI emulator maps EL2, non-shareable, outer-shareable, and nXS encodings onto inner-shareable EL1 XS operations and returns `-EINVAL` for unsupported encodings.

## State and Persistence
State is transient but highly sensitive: HCR_EL2, stage-2 MMU context, IRQ mask state, TCR_EL1/SCTLR_EL1 under erratum workarounds, and TLB/cache hardware state. It may also restore the running vCPU's previous hardware MMU after flushing a different target.

## Dependencies and Integration Points
It depends on `__load_stage2()`, ARM64 TLBI macros, erratum feature caps, hyp TLB synchronization helpers, and nested virtualization instruction decoders. It is called by page-table code, MMU invalidation code, and VHE fast sysreg trap handling.

## Risks and Edge Cases
The core risks are targeting the host TLB instead of guest TLB, failing to restore HCR.TGE or the previous stage-2 context, and insufficient ordering between stage-2 and stage-1 invalidations. Nested TLBI emulation also risks accepting an unsupported encoding or under-invalidating by preserving non-shareable/nXS semantics that are unsafe for KVM.

## Test Signals
Stress KVM MMU notifier invalidations, VMID rollover, nested EL2 TLBI traps, range TLBI capability on/off, erratum-affected CPU configurations, and concurrent vCPU execution during remote TLB flushes. Failures often manifest as stale translations, data corruption, or host instability after guest TLBI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp_trace.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp_trace.c

## Purpose
This file registers and manages remote tracing for nVHE hypervisor events. It creates shared trace buffers, maps or shares pages with hyp, synchronizes a hyp trace clock with kernel boot time, exposes tracefs controls, and bridges event enable/reset/swap operations to hyp calls.

## Important APIs, Types, and Functions
- `struct hyp_trace_clock` stores cycle/boot epochs, mult/shift conversion, delayed work, completion, and running state.
- `__hyp_clock_work()` computes clock conversion and updates hyp through `__tracing_update_clock`.
- `struct hyp_trace_buffer` stores the hyp trace descriptor and descriptor size.
- Buffer lifecycle functions include `hyp_trace_load()`, `hyp_trace_unload()`, `hyp_trace_buffer_share_hyp()`, and `hyp_trace_buffer_unshare_hyp()`.
- Trace callbacks implement load/unload, enable tracing, reader-page swap, reset, enable event, and tracefs initialization.
- `kvm_hyp_trace_init()` validates platform support, initializes event IDs, and registers the remote tracer.

## Control Flow
Trace initialization exits early for VHE kernels, rejects out-of-line arch timer counter workarounds that hyp tracing cannot handle, assigns event IDs, and calls `trace_remote_register()`. When a remote trace buffer is loaded, the code allocates a descriptor, maps it into hyp when host-owned hyp mappings are available, allocates backing pages for simple ring-buffer pages, lets trace_remote initialize per-CPU buffers, shares metadata and data pages with hyp, and calls `__tracing_load`.

Tracing enable starts the clock worker, waits for the initial conversion, and calls hyp to enable tracing. The delayed worker periodically compares arch-counter-derived time against kernel boot time, recalculates mult/shift when drift appears, fast-forwards epochs before overflow, and pushes updates into hyp. Event enabling either calls hyp directly for protected KVM or vmap-writes the hyp event's shared atomic flag for normal nVHE.

## State and Persistence
Persistent runtime state includes the global `hyp_clock`, global `trace_buffer`, allocated trace descriptors, ring buffer pages, bpage backing storage, shared page ownership state, tracefs files, and event IDs generated from linker ranges. The clock worker remains scheduled while tracing is enabled.

## Dependencies and Integration Points
It depends on `trace_remote`, `tracefs`, `simple_ring_buffer`, arch timer snapshots, hyp tracing ABI functions such as `__tracing_load`, `__tracing_enable`, `__tracing_swap_reader`, `__tracing_reset`, and KVM hyp mapping/sharing helpers from `mmu.c`. Event definitions are pulled in through `asm/kvm_define_hypevents.h`.

## Risks and Edge Cases
Important risks include leaking shared pages on partial allocation failure, freeing with an incorrect descriptor size, clock drift beyond trace precision, unsupported timer workarounds, and event-enable races between host and hyp. Protected KVM changes the event-enable path because direct host writes are not allowed.

## Test Signals
Enable hyp tracing through tracefs, toggle individual events, swap reader pages on each CPU, reset buffers, unload/reload tracing, and run under pKVM and non-pKVM nVHE. Watch for allocation unwind warnings, clock drift warnings, trace event timestamp monotonicity, and page sharing errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp_trace.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp_trace.h

## Purpose
This header provides the public initialization declaration for ARM64 KVM hyp tracing, with a stub when nVHE EL2 tracing is disabled.

## Important APIs, Types, and Functions
- `kvm_hyp_trace_init()` is declared when `CONFIG_NVHE_EL2_TRACING` is enabled.
- A static inline no-op returning `0` is provided otherwise.

## Control Flow
There is no runtime control flow beyond compile-time selection. Callers can invoke `kvm_hyp_trace_init()` unconditionally and receive either real initialization or a successful no-op depending on configuration.

## State and Persistence
The header holds no state. It gates access to state managed by `hyp_trace.c`.

## Dependencies and Integration Points
It is included by ARM64 KVM initialization code that wants optional hyp tracing without scattering `#ifdef CONFIG_NVHE_EL2_TRACING` checks.

## Risks and Edge Cases
The main risk is mismatched configuration: code may appear to initialize tracing but receive a no-op if the config is disabled. The include guard prevents duplicate declarations.

## Test Signals
Build with `CONFIG_NVHE_EL2_TRACING=y` and disabled. The enabled build should link `hyp_trace.c`; the disabled build should compile callers against the inline stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hypercalls.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hypercalls.c

## Purpose
This file implements ARM64 KVM handling for SMCCC/PSCI-facing hypercalls and firmware pseudo-registers. It exposes architecture workarounds, PV time, stolen time, TRNG, KVM vendor hypervisor features, PTP time, userspace filtering/forwarding, and firmware register get/set ioctls.

## Important APIs, Types, and Functions
- `kvm_smccc_call_handler()` is the main HVC/SMC dispatch path.
- `kvm_arm_init_hypercalls()` and `kvm_arm_teardown_hypercalls()` initialize and destroy SMCCC feature/filter state.
- Firmware-register APIs include `kvm_arm_get_fw_num_regs()`, `kvm_arm_copy_fw_reg_indices()`, `kvm_arm_get_fw_reg()`, and `kvm_arm_set_fw_reg()`.
- SMCCC filter APIs include `kvm_vm_smccc_has_attr()`, `kvm_vm_smccc_set_attr()`, `kvm_smccc_set_filter()`, `kvm_smccc_filter_get_action()`, and `kvm_smccc_get_action()`.
- `kvm_ptp_get_time()` implements KVM vendor PTP using synchronized system time snapshots.

## Control Flow
The call handler obtains the SMCCC function ID, consults the filter and feature bitmaps, denies unsupported calls, forwards configured calls to userspace by filling `KVM_EXIT_HYPERCALL`, or handles the call in-kernel. Architecture calls report SMCCC version and Spectre workaround status. PV time calls report features or stolen-time GPA. Vendor calls report KVM UID, feature bitmaps, and PTP time. TRNG calls delegate to `kvm_trng_call()`, and unknown/default calls fall through to PSCI.

Firmware register get/set paths expose PSCI version, workaround levels, and feature bitmaps. Setters validate register size, userspace values, kernel mitigation capability, whether PSCI 0.2 was requested for the vCPU, unsupported feature bits, and whether the VM has already run. SMCCC filters are stored in a maple tree and reserve architecture ranges so userspace cannot misrepresent mitigation status.

## State and Persistence
State lives under `kvm->arch.smccc_feat` feature bitmaps, `kvm->arch.smccc_filter`, and `kvm->arch.psci_version`. Values are VM-wide and mostly immutable after first run. Hypercall return values are placed in guest registers; userspace exits are represented in `struct kvm_run`.

## Dependencies and Integration Points
It depends on ARM SMCCC constants, PSCI helpers, TRNG helpers, KVM PV time/stolen-time code, Spectre mitigation state queries, maple tree APIs, userspace copy helpers, and KVM one-reg/device-attr ioctls. It is reached from the KVM exception handling path for HVC/SMC traps.

## Risks and Edge Cases
Risks include allowing userspace to spoof architecture mitigation calls, changing feature bitmaps after a VM has run, mishandling PSCI 0.1 vs 0.2 compatibility, returning inconsistent PTP cycles if the clocksource is not the arch counter, and filter overlap/overflow mistakes. The reserved architecture filter ranges and config lock reduce these risks.

## Test Signals
Use KVM selftests for firmware registers, SMCCC filter insertion, PSCI version configuration, TRNG exposure, PV time/stolen time, vendor UID/features, PTP calls, and userspace-forwarded hypercalls. Negative tests should cover unsupported feature bits, late mutation after first run, invalid filter ranges, and disallowed workaround levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hypercalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/inject_fault.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/inject_fault.c

## Purpose
This file builds and queues guest-visible exceptions for ARM64 KVM, covering synchronous aborts, undefined instructions, size faults, exclusive/atomic faults, synchronous external aborts, and SErrors for AArch64, AArch32, and nested virtualization contexts.

## Important APIs, Types, and Functions
- Target selection helpers: `exception_target_el()`, `exception_esr_elx()`, `exception_far_elx()`.
- Queue helpers: `pend_sync_exception()` and `pend_serror_exception()`.
- Main injectors: `kvm_inject_sync()`, `kvm_inject_sea()`, `kvm_inject_dabt_excl_atomic()`, `kvm_inject_size_fault()`, `kvm_inject_undefined()`, and `kvm_inject_serror_esr()`.
- Format-specific helpers include `inject_abt64()`, `inject_abt32()`, `inject_undef64()`, and `inject_undef32()`.
- Nested routing helpers include SEA, exclusive atomic, and SError decisions.

## Control Flow
For AArch64 abort injection, the code determines whether the exception targets virtual EL1 or virtual EL2, optionally re-walks stage-1 descriptors for S1PTW abort levels, chooses sync exception or SError based on SCTLR2.EASE, builds ESR with instruction length, exception class, and fault status, and writes FAR/ESR to the selected ELx sysregs. AArch32 aborts build DFSR/IFSR/FAR encodings based on LPAE.

SEA injection may route to nested EL2 when HCR/HCRX policy requires it; otherwise it injects locally. Unsupported exclusive/atomic faults can become nested sync exceptions when nested stage-2 translation is active. Size faults are represented as address-size faults for AArch64/LPAE guests where possible. Undefined instruction injection selects AA32 undefined or AA64 unknown exception.

SError injection first decides whether a nested hypervisor should receive it, handles virtual EL2 cases where an SError is pending but not directly deliverable, emulates exception entry when unmasked, or programs virtual SError state through VSE/VSESR.

## State and Persistence
The file mutates vCPU pending-exception flags, ESR/FAR/IFSR sysregs, virtual SError state (`VSESR`, `HCR_VSE`, `NESTED_SERROR_PENDING`), CPSR-derived routing, and nested exception state. It assumes callers hold `vcpu->mutex` for SEA and SError paths that need synchronized state.

## Dependencies and Integration Points
It depends on KVM emulation helpers, nested virtualization injection helpers, ESR/FSC macros, HCR/HCRX routing bits, SCTLR2 feature support, and guest mode detection. It is called from MMU abort handling, MMIO failure paths, sysreg emulation failures, and generic exception injection APIs.

## Risks and Edge Cases
Risks include injecting to the wrong virtual EL, losing S1PTW level information, mishandling FEAT_DoubleFault2 EASE/NMEA semantics, and exposing an exception encoding not valid for AArch32 vs AArch64. Nested contexts are especially sensitive because routing may depend on current mode, TGE, AMO, TEA, TMEA, and whether the guest is already in virtual EL2.

## Test Signals
Test AArch32 and AArch64 guests for undefined instructions, data/instruction aborts, address-size faults, S1PTW faults, SEAs, SErrors with A masked/unmasked, nested EL2 routing, and unsupported exclusive/atomic accesses. Inspect guest ESR/FAR/IFSR values and pending exception flags after injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/inject_fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/mmio.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/mmio.c

## Purpose
This file decodes and completes guest MMIO abort handling for ARM64 KVM. It converts register values to/from MMIO byte buffers, routes MMIO to in-kernel emulation or userspace, handles returns from userspace emulation, and deals with no-valid-syndrome or special LD/ST64B-style exits.

## Important APIs, Types, and Functions
- `kvm_mmio_write_buf()` and `kvm_mmio_read_buf()` marshal 1, 2, 4, or 8 byte accesses.
- `kvm_handle_mmio_return()` completes reads after in-kernel or userspace emulation and advances the PC.
- `io_mem_abort()` is called when a stage-2 abort targets an IPA outside RAM or otherwise needs MMIO handling.
- `kvm_pending_external_abort()` detects whether an exception was already injected before MMIO completion.

## Control Flow
`io_mem_abort()` first checks whether the data abort syndrome is valid. If not, protected guests get a SEA; configured VMs can exit with `KVM_EXIT_ARM_NISV`; otherwise KVM returns `-ENOSYS`. Certain load/store type encodings are sent to userspace as `KVM_EXIT_ARM_LDST64B`.

For valid syndromes, the handler decodes write/read, access size, and target register. Writes convert guest register data to host byte order, trace the access, and try `kvm_io_bus_write()`. Reads trace an unsatisfied read and try `kvm_io_bus_read()`. It then fills `run->mmio`, marks `vcpu->mmio_needed`, completes immediately when the in-kernel bus handled the access, or exits to userspace with `KVM_EXIT_MMIO`.

`kvm_handle_mmio_return()` ignores already-handled or aborted accesses, clears `mmio_needed`, reads returned data for load instructions, applies sign extension and 32-bit masking, converts host data back to guest format, stores the destination register, traces the completed read, and increments the PC.

## State and Persistence
State is stored in `vcpu->mmio_needed`, `vcpu->run->mmio`, `vcpu->stat.mmio_exit_kernel`, `vcpu->stat.mmio_exit_user`, guest registers, and the guest PC. It also respects pending exception flags so an externally injected abort is not overwritten by MMIO completion.

## Dependencies and Integration Points
It depends on KVM data-abort syndrome helpers, MMIO bus APIs, tracepoints, `struct kvm_run` userspace ABI fields, guest/host data conversion helpers, and fault injection for protected/no-syndrome cases. `mmu.c` calls `io_mem_abort()` when a faulting IPA is not backed by a memory slot.

## Risks and Edge Cases
Risks include incorrect sign extension, wrong 32-bit register truncation, treating invalid syndrome accesses as emulatable, and completing MMIO after an exception has been injected. Special LD/ST64B handling is punted to userspace because full emulation cannot be inferred from ordinary syndrome fields.

## Test Signals
Exercise 8/16/32/64-bit MMIO reads/writes, sign-extending loads, AArch32 register truncation, in-kernel device emulation, userspace MMIO exits, NISV exits, protected VM invalid syndrome paths, and LD/ST64B exits. Tracepoints should reflect write, unsatisfied read, and completed read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/mmu.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/mmu.c

## Purpose
This file is the host-side ARM64 KVM MMU implementation. It initializes hyp and stage-2 page tables, manages hyp mappings and pKVM sharing, maps guest RAM/device memory on abort, handles memory-slot changes, dirty logging, hugepage splitting, MTE tag preparation, guest external abort routing, TLB/cache maintenance, and MMU notifier callbacks.

## Important APIs, Types, and Functions
- Global hyp state: `hyp_pgtable`, `kvm_hyp_pgd_mutex`, `hyp_idmap_*`, `__hyp_va_bits`, and `io_map_base`.
- Stage-2 lifecycle: `kvm_init_stage2_mmu()`, `kvm_uninit_stage2_mmu()`, `kvm_free_stage2_pgd()`, `stage2_unmap_vm()`, `kvm_stage2_unmap_range()`, and `kvm_stage2_flush_range()`.
- Hyp mapping APIs: `__create_hyp_mappings()`, `create_hyp_mappings()`, `hyp_alloc_private_va_range()`, `create_hyp_stack()`, `create_hyp_io_mappings()`, `create_hyp_exec_mappings()`, `kvm_share_hyp()`, and `kvm_unshare_hyp()`.
- Fault handling: `kvm_handle_guest_abort()`, `user_mem_abort()`, `gmem_abort()`, `pkvm_mem_abort()`, `handle_access_fault()`, and `kvm_handle_guest_sea()`.
- Dirty logging and split helpers: `kvm_stage2_wp_range()`, `kvm_arch_mmu_enable_log_dirty_pt_masked()`, `kvm_mmu_wp_memory_region()`, and `kvm_mmu_split_huge_pages()`.
- Memory-region hooks: `kvm_arch_prepare_memory_region()`, `kvm_arch_commit_memory_region()`, and `kvm_arch_flush_shadow_memslot()`.
- Cache/TLB controls: `kvm_arch_flush_remote_tlbs()`, `kvm_arch_flush_remote_tlbs_range()`, `kvm_set_way_flush()`, and `kvm_toggle_cache()`.

## Control Flow
Initialization builds hyp idmap metadata, allocates a hyp page table, maps the hyp init text executable, records hyp VA bits, initializes stage-2 VTCR/PGD state, allocates per-CPU last-vCPU state, and configures eager split caches. Hyp mappings are either created by the host-owned hyp page table, delegated to pKVM hyp calls, or expressed through share/unshare PFN refcounting depending on kernel-in-hyp/protected mode.

Stage-2 range operations chunk large ranges at minimum block granularity and optionally drop/reacquire `mmu_lock` to avoid stalls. Dirty logging write-protects and optionally splits memory slots. Memory-slot deletion/move unmaps stage-2 ranges and nested stage-2 mappings. I/O mapping maps device PAs into guest IPA as device memory when protected KVM is not enabled.

Guest abort handling first routes SEAs, validates IPA range, traces the fault, supports translation/permission/access-flag/exclusive-atomic faults, resolves nested stage-2 translations when applicable, locates the memory slot/HVA, sends invalid slot or readonly write faults to instruction/data abort or MMIO handling, handles access-flag faults by making the PTE young, then dispatches to pKVM, guest_memfd, or userspace-VMA backed mapping.

`user_mem_abort()` tops up the MMU cache, captures VMA metadata and invalidation sequence, faults in a PFN, validates device/cacheability and MTE requirements, computes stage-2 permissions, decides mapping size including hugetlb/THP/nested constraints, sanitizes MTE tags, maps or relaxes permissions under the fault lock, releases the pinned page, and marks dirty pages. `gmem_abort()` maps private guest memory from guest_memfd with invalidation sequence protection. `pkvm_mem_abort()` pins long-term anonymous/shmem pages and maps them through pKVM stage-2.

## State and Persistence
Persistent state includes hyp page tables, stage-2 page tables, VTCR/PGD physical addresses, per-CPU `last_vcpu_ran`, split-page memory caches, protected hyp memcaches, RB-tree reference counts for shared hyp PFNs, memory-slot metadata, dirty bitmaps, MTE page-tag state, and vCPU fault/stat state. The file uses `mmu_lock`, `slots_lock`, `config_lock`, SRCU, `mmap_read_lock`, RCU callbacks, invalidation sequence counters, and page pins/refcounts to coordinate with Linux memory management.

## Dependencies and Integration Points
It depends on the page-table engine in `hyp/pgtable.c`, pKVM hyp calls and protected VM state, Linux MM/VMA/GUP/memslot APIs, MTE helpers, cache maintenance primitives, nested virtualization translation helpers, MMIO handling, fault injection, tracepoints, arch timer and ACPI/system headers, and KVM generic MMU notifier interfaces.

## Risks and Edge Cases
Major risks are stale stage-2 mappings after MMU invalidation, mapping the wrong PFN when HVA/IPA alignment differs, dirty logging with huge mappings, cache incoherency for uncached guest mappings without FWB, unsafe cacheable PFNMAP mappings, missing MTE tag initialization, pKVM memslot mutation after protected VM creation, private/shared memory confusion, and nested translation permission mismatches. The code mitigates these with invalidation sequence checks, block-mapping alignment tests, VMA cacheability validation, mapping-size caps, permission relaxation rules, and explicit protected-VM restrictions.

## Test Signals
Run KVM selftests for stage-2 faults, dirty logging, THP/hugetlb mapping, memslot create/move/delete, MMU notifier invalidation, access aging, MTE, guest_memfd/private memory, pKVM, nested virtualization, device PFNMAP MMIO, cache maintenance trapping, and SEA userspace exits. Kernel signals include tracepoints for guest faults and cache toggles, lockdep, RCU stalls, page refcount leaks, HWPOISON behavior, and data-integrity stress under concurrent memory reclaim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/mmu.c -->
