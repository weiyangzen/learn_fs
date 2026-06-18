# subset-b-000782 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/ranges.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kexec/ranges.c

## Purpose
Builds and edits PowerPC kexec/kdump physical memory range lists. The code is shared between `CONFIG_KEXEC_FILE` load-time segment placement and `CONFIG_CRASH_DUMP` crash-memory export paths, producing lists for reserved ranges, excluded ranges, usable kdump ranges, crash ELF core ranges, and explicit removals.

## Important APIs, Types, And Functions
The core type is `struct crash_mem`, with `struct range` entries stored as inclusive `[start,end]` spans. Generic helpers are `realloc_mem_ranges`, `add_mem_range`, and `sort_memory_ranges`; private helpers include `__add_mem_range`, `__merge_memory_ranges`, and `rngcmp`. Kexec-file range population is handled by `get_reserved_memory_ranges` and `get_exclude_memory_ranges`, which pull RTAS, OPAL, TCE table, retained initrd, kernel image, hash table, and firmware `/reserved-ranges` data. Crash-dump paths include `get_usable_memory_ranges`, `get_crash_memory_ranges`, `crash_exclude_mem_range_guarded`, and `remove_mem_range`.

## Control Flow
Range insertion grows the crash-memory array in `MEM_RANGE_CHUNK_SZ` chunks, appends inclusive ranges, and optionally sorts and merges adjacent spans. Kexec-file exclusion first adds device-tree and platform-reserved areas, then sorts and merges to make later segment placement checks cheap. Crash memory collection walks `memblock` memory, skips the backup source area, excludes the crashkernel and crashk CMA ranges with guarded reallocation, appends RTAS/OPAL and the backup source header, and finally sorts without merging so ELF program headers remain distinct where required.

## State And Persistence
All state is transient kernel memory owned by the caller through `struct crash_mem **`. The code reads persistent boot/runtime state from the device tree, `saved_command_line`, `crashk_res`, `crashk_cma_ranges`, `htab_address`, `htab_size_bytes`, and memblock, but does not persist changes itself. Firmware-provided reserved ranges and platform structures become copied into range arrays used by later kexec or kdump code.

## Dependencies And Integration Points
Depends on Linux kexec, crash core, memblock, Open Firmware helpers, kernel section symbols, PPC64 crashdump constants, and optional hash-MMU globals. It integrates with `kexec_file_load` placement, crash dump ELF core generation, crashkernel reservation, RTAS/OPAL firmware data, TCE tables, and kexec-tools compatibility expectations.

## Risks And Edge Cases
Inclusive end arithmetic can overflow if callers pass extreme base/size pairs. `add_mem_range` only updates the first overlapping range and relies on later sort/merge for full canonicalization. The source snapshot contains a duplicated local declaration in `crash_exclude_mem_range_guarded`, which is a compile-time risk if present in the active tree. Device-tree properties may be absent, malformed, or partially read; `add_tce_mem_ranges` tolerates missing TCE properties but aborts other read errors. Crash range splitting requires enough spare capacity before calling `crash_exclude_mem_range`, hence the guarded reallocation.

## Test Signals
Useful coverage is `kexec_file_load` on pseries and powernv, kdump boot with crashk CMA ranges, retained-initrd loads, hash-MMU and radix-MMU builds, and device trees with RTAS, OPAL, TCE, and `/reserved-ranges`. Unit-style tests should stress adjacent range merging, exact removal, edge trimming, middle splitting, backup source handling, and full-array reallocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/ranges.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/relocate_32.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kexec/relocate_32.S

## Purpose
Implements the 32-bit PowerPC low-level kexec relocation trampoline. It runs as position-independent code from the kexec control page, establishes a safe MMU/TLB state, copies source pages to destination pages from the kexec indirection list, flushes caches, and branches to the new kernel entry point.

## Important APIs, Types, And Functions
Exports `relocate_new_kernel` and `relocate_new_kernel_size`. The entry uses register arguments `r3` for the kexec page list, `r4` for the reboot code buffer/control page, and `r5` for the new kernel start address. It consumes kexec indirection flags `IND_DESTINATION`, `IND_INDIRECTION`, `IND_DONE`, and `IND_SOURCE`. Platform-specific setup is compiled for `CONFIG_PPC_85xx`, `CONFIG_44x`, and `CONFIG_PPC_47x`.

## Control Flow
The generic path disables translation by loading `SRR0/SRR1` and returning with `rfi`. PPC85xx includes the special entry mapping sequence. PPC44x cannot simply disable the MMU, so it invalidates all but the currently executing TLB entry, installs a temporary mapping in the alternate translation space, builds 1:1 256 MiB mappings for 0-2 GiB, jumps back to the original translation space, and removes the temporary entry. PPC47x performs equivalent UTLB invalidation and 1:1 setup using 47x TLB word formats. After translation setup, the copy loop parses the indirection list, sets destination/source page pointers, copies one page at a time with `lwzu/stwu`, performs data and instruction cache maintenance, synchronizes, and calls the new kernel.

## State And Persistence
No durable state is created. The code deliberately mutates processor state: MSR, PID/MMUCR, TLB entries, stack pointer, caches, and link register. It also writes destination memory pages that become the new kernel image. Register preservation is limited to what the trampoline itself needs before the final branch.

## Dependencies And Integration Points
Depends on PPC assembly register definitions, MMU/TLB constants, kexec control page layout, platform-specific entry mapping snippets, and the generic kexec page-list format. It integrates with the C kexec loader that places this code in the reboot code buffer and with architecture reset/secondary CPU shutdown code that transfers control here.

## Risks And Edge Cases
This is highly timing- and CPU-sensitive code. A wrong TLB index, page-size decode, translation-space bit, or cache flush can corrupt the running trampoline or the new kernel. PPC44x/47x paths assume the low 2 GiB mapping coverage is sufficient. The copy loop assumes page-aligned encoded addresses and valid indirection pages. Interrupts and translation must remain in the expected state until the new kernel is entered.

## Test Signals
Signals are architecture boot tests for kexec and crash kexec on PPC85xx, PPC44x, PPC47x, and generic 32-bit Book3S/BookE systems. Important cases are kernels loaded above/below existing mappings, many indirection pages, self-overlapping copy plans, SMP shutdown before relocation, and instruction-cache correctness after relocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/relocate_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/vmcore_info.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kexec/vmcore_info.c

## Purpose
Adds PowerPC-specific metadata to the crash vmcore information block so dump tools can interpret memory layout, MMU mode, KASLR offset, CPU features, and vmemmap backing structures after a crash.

## Important APIs, Types, And Functions
Defines `arch_crash_save_vmcoreinfo`. It emits entries with `VMCOREINFO_SYMBOL`, `VMCOREINFO_LENGTH`, `VMCOREINFO_STRUCT_SIZE`, `VMCOREINFO_OFFSET`, and `vmcoreinfo_append_str`. Important exported facts include `node_data`, `contig_page_data`, `vmemmap_list`, `mmu_vmemmap_psize`, `mmu_psize_defs`, `cur_cpu_spec`, `cpu_spec.cpu_features`, `cpu_spec.mmu_features`, `RADIX_MMU`, and `KERNELOFFSET`.

## Control Flow
At crash metadata construction time the function conditionally records NUMA or contiguous page-data symbols, optional PPC64 sparse-vmemmap details, CPU-spec offsets, the early radix mode state, and the KASLR offset. There is no loop or dynamic allocation.

## State And Persistence
The function appends text metadata to the vmcore info note that persists into the crash dump. It reads current architecture globals and does not mutate runtime state beyond the vmcoreinfo buffer.

## Dependencies And Integration Points
Depends on `linux/vmcore_info.h`, PPC page allocation/MMU definitions, NUMA configuration, sparse vmemmap configuration, `early_radix_enabled()`, and `kaslr_offset()`. It integrates with makedumpfile/crash tooling and the generic crash core.

## Risks And Edge Cases
Missing or wrong offsets break postmortem tools rather than normal runtime. Conditional emission must match the crashed kernel configuration; NUMA and sparse-vmemmap mismatches can cause dump tools to walk invalid structures. Radix/hash mode and KASLR offset are essential for correct address translation in modern PPC64 dumps.

## Test Signals
Validate by booting NUMA and non-NUMA kernels, hash and radix PPC64 kernels, collecting vmcores, and confirming `makedumpfile` or `crash` resolves page metadata, CPU feature flags, vmemmap backing, and kernel virtual addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/vmcore_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/Kconfig

## Purpose
Defines the PowerPC KVM configuration surface: generic virtualization menu visibility, shared KVM enablement, Book3S PR/HV variants, BookE/e500 variants, interrupt-controller support, timing/debug options, nested PMU workaround, and hypervisor PMU support.

## Important APIs, Types, And Functions
This is Kconfig data rather than C APIs. Key symbols are `VIRTUALIZATION`, `KVM`, `KVM_BOOK3S_HANDLER`, `KVM_BOOK3S_32`, `KVM_BOOK3S_64`, `KVM_BOOK3S_64_HV`, `KVM_BOOK3S_64_PR`, `KVM_BOOK3S_HV_P9_TIMING`, `KVM_BOOK3S_HV_P8_TIMING`, `KVM_BOOK3S_HV_NESTED_PMU_WORKAROUND`, `KVM_BOOK3S_HV_PMU`, `KVM_E500V2`, `KVM_E500MC`, `KVM_MPIC`, `KVM_XICS`, and `KVM_XIVE`.

## Control Flow
Kconfig dependency resolution selects common KVM support and one or more architecture implementations. Book3S 32-bit depends on uniprocessor non-64-bit PTE Book3S and excludes context tracking. Book3S 64 selects hash MMU support and optionally SPAPR TCE IOMMU. HV mode is powernv-only and selects CMA and the HV PMU; PR mode excludes context tracking and is hash-only. Timing options depend on debugfs and HV or e500 support. XICS/XIVE depend on interrupt-controller capabilities and Book3S 64 support.

## State And Persistence
The only persistent state is the kernel configuration. Selected symbols drive object inclusion, exported module capabilities, `/dev/kvm` availability, and runtime feature sets.

## Dependencies And Integration Points
Integrates with `virt/kvm/Kconfig`, PowerPC platform symbols, MMU mode symbols, IOMMU support, pseries/powernv platform support, debugfs, PMU, MPIC, XICS, and XIVE code. It directly feeds the local KVM Makefile object lists.

## Risks And Edge Cases
Bad dependency combinations can build unsupported KVM modes, omit required MMU or interrupt-controller code, or enable PR KVM with host features it cannot tolerate. PR KVM has platform-wide side effects called out in help text, including SCV and AIL behavior. Timing options add overhead and are not production defaults.

## Test Signals
Primary signals are `olddefconfig` and build coverage for Book3S 32 PR, Book3S 64 PR, Book3S 64 HV, pseries/powernv hash and radix combinations, e500v2/e500mc, and XICS/XIVE variants. Runtime signals are `/dev/kvm`, module load, guest boot, interrupt controller creation, and timing/debugfs file presence when selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/Makefile

## Purpose
Maps PowerPC KVM Kconfig symbols to the C and assembly objects linked into common KVM, e500, Book3S PR, Book3S HV, interrupt controller, SPAPR TCE, and built-in real-mode handler components.

## Important APIs, Types, And Functions
This file defines Kbuild object groups: `common-objs-y`, `kvm-e500-objs`, `kvm-e500mc-objs`, `kvm-pr-y`, `kvm-hv-y`, `kvm-book3s_64-builtin-objs-*`, `kvm-book3s_64-module-objs`, and `kvm-book3s_32-objs`. It also sets include flags, assembly flags for BookE interrupts, and disables KASAN for 64-bit Book3S real-mode KVM code.

## Control Flow
Kbuild expands `obj-$(CONFIG_...)` and group variables. e500 variants build `kvm.o`; Book3S 64 builds the common module plus optional `kvm-pr.o` and `kvm-hv.o`; Book3S 32 builds PR-only support into `kvm.o`. HV-capable builds add real-mode handlers, P9 entry, nestedv2, guest-state-buffer, HMI/RAS, TM, XICS, XIVE, and UV memory objects as selected.

## State And Persistence
No runtime state. Build state is the selected object graph and resulting modules/built-ins.

## Dependencies And Integration Points
Depends on `virt/kvm/Makefile.kvm`, Kconfig symbols, PowerPC assembly offsets, and object naming conventions. It integrates C/assembly files that must agree on offsets and real-mode constraints. The `obj-y += $(kvm-book3s_64-builtin-objs-y)` line ensures real-mode Book3S 64 handlers are built in when required even if KVM is modular.

## Risks And Edge Cases
Object grouping affects symbol visibility and link order. Missing built-in handler objects can break exception entry before modules load. Including sanitizer instrumentation in real-mode code would be unsafe, hence the explicit KASAN disable. Optional XICS/XIVE/TM/UV selections must match both C references and assembly branches.

## Test Signals
Cross-build Book3S 32, Book3S 64 PR, Book3S 64 HV, e500v2, e500mc, XICS, XIVE, SPAPR TCE, transactional memory, and UV configurations. Link failures, unresolved exported symbols, and early guest-entry crashes are the main signals for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s.c

## Purpose
Provides shared Book3S KVM glue for both PR and HV implementations: statistics descriptors, interrupt queuing and delivery, address translation wrappers, register ioctls, vCPU and VM operation dispatch, dirty-log/memslot delegation, logical cache-inhibited hypercalls, IRQ routing, and module initialization.

## Important APIs, Types, And Functions
Important exported or core functions include `kvmppc_inject_interrupt`, `kvmppc_book3s_queue_irqprio`, `kvmppc_core_queue_*`, `kvmppc_core_prepare_to_enter`, `kvmppc_gpa_to_pfn`, `kvmppc_xlate`, `kvmppc_load_last_inst`, `kvm_arch_vcpu_ioctl_get_regs`, `kvm_arch_vcpu_ioctl_set_regs`, `kvmppc_get_one_reg`, `kvmppc_set_one_reg`, `kvmppc_set_msr`, `kvmppc_vcpu_run`, `kvmppc_core_init_vm`, `kvmppc_core_destroy_vm`, `kvmppc_h_logical_ci_load`, `kvmppc_h_logical_ci_store`, and `kvmppc_book3s_init`. It relies heavily on `kvm->arch.kvm_ops` for mode-specific behavior.

## Control Flow
Interrupt requests are translated from vectors to priority bits, queued in `pending_exceptions`, and delivered by `kvmppc_core_prepare_to_enter` in priority order if guest MSR and critical-section checks permit. Register ioctls first delegate mode-specific registers through `kvm_ops`, then handle common DAR/DSISR/FPR/VSX/debug/interrupt-controller/FSCR/TAR/EBB/BESCR/IC cases. Memory and VM lifecycle functions mostly delegate through `kvm_ops`, with shared PPC64 setup and teardown for RTAS tokens and SPAPR TCE tables. Logical CI hcalls perform MMIO bus reads/writes with big-endian size conversion. Module init calls `kvm_init`, PR init for 32-bit handler builds, and XICS/XIVE device registration.

## State And Persistence
Per-vCPU state includes pending exception bitmaps, one-shot external interrupt state, guest registers, FPU/VSX state, magic page addresses, and statistics counters. Per-VM state includes mode-specific operations, RTAS token lists, SPAPR TCE table lists, XICS/XIVE device pointers, and memory-slot/MMU state delegated to HV or PR code. No filesystem persistence is involved.

## Dependencies And Integration Points
Depends on generic KVM core, PPC register helpers, Book3S PR/HV ops, MMU code, XICS/XIVE, RTAS, MMIO buses, SRCU, and module infrastructure. It is the main user-visible `/dev/kvm` Book3S module entry for common ioctls and mode-independent hypercall support.

## Risks And Edge Cases
Interrupt delivery must respect guest critical sections, MSR[EE], nestedv2 behavior, and one-shot external interrupts. Magic-page PFN override must keep page references and 32-bit truncation correct. Register ioctl fallbacks must not expose unavailable VSX/XIVE/XICS state. The source snapshot contains duplicated braces/preprocessor lines in sensitive areas, which would be compile-time risks if active. Logical CI hcalls depend on exact endian conversion and MMIO bus behavior.

## Test Signals
Use KVM selftests/QEMU guest boot for Book3S PR and HV, interrupt injection tests, decrementer and external IRQ tests, register get/set ABI tests, MMIO load/store hypercalls, XICS/XIVE device creation, migration register save/restore, dirty-log ioctls, and 32-bit guest-on-64-bit host cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s.h

## Purpose
Declares internal Book3S KVM entry points shared between the common Book3S core, PR implementation, HV implementation, and MMU/memslot code.

## Important APIs, Types, And Functions
Declarations include HV memslot/MMU invalidation hooks `kvmppc_core_flush_memslot_hv`, `kvm_unmap_gfn_range_hv`, `kvm_age_gfn_hv`, and `kvm_test_age_gfn_hv`; PR hooks `kvmppc_mmu_init_pr`, `kvmppc_mmu_destroy_pr`, `kvmppc_core_emulate_op_pr`, `kvmppc_core_emulate_mtspr_pr`, `kvmppc_core_emulate_mfspr_pr`, `kvmppc_book3s_init_pr`, `kvmppc_book3s_exit_pr`, and `kvmppc_handle_exit_pr`; transactional-memory abort emulation; and HV interrupt/MSR helpers `kvmppc_set_msr_hv` and `kvmppc_inject_interrupt_hv`.

## Control Flow
This header has no runtime control flow. It supplies compile-time contracts that allow common Book3S code and mode-specific files to call each other.

## State And Persistence
No state is stored here. The declared functions operate on `struct kvm`, `struct kvm_vcpu`, `struct kvm_memory_slot`, and `struct kvm_gfn_range` owned by KVM core and mode-specific implementations.

## Dependencies And Integration Points
Integrates Book3S PR, Book3S HV, transactional memory, and generic KVM memory invalidation paths. The `CONFIG_PPC_TRANSACTIONAL_MEM` guard provides a no-op inline when TM is unavailable.

## Risks And Edge Cases
Prototype drift between this header and C definitions breaks builds or, worse for assembly-adjacent code, ABI assumptions. The no-op TM helper must be acceptable for non-TM builds. HV and PR hooks have similar names but different semantics, so caller selection must be mode-aware.

## Test Signals
Compile coverage across PR-only, HV-only, PR+HV possible, and no transactional-memory configurations is the main signal. Runtime signals come indirectly from memslot invalidation, PR emulation, and HV interrupt injection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_32_mmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_32_mmu.c

## Purpose
Implements guest effective-address translation for 32-bit Book3S PR KVM. It emulates BAT and hash-page-table lookup, updates guest PTE accessed/dirty bits, handles segment-register state, and installs function pointers in `vcpu->arch.mmu`.

## Important APIs, Types, And Functions
Key helpers are `find_sr`, `sr_vsid`, `sr_valid`, `sr_ks`, `sr_kp`, `kvmppc_mmu_book3s_32_xlate_bat`, `kvmppc_mmu_book3s_32_xlate_pte`, `kvmppc_mmu_book3s_32_xlate`, `kvmppc_mmu_book3s_32_mfsrin`, `kvmppc_mmu_book3s_32_mtsrin`, `kvmppc_mmu_book3s_32_tlbie`, `kvmppc_mmu_book3s_32_esid_to_vsid`, `kvmppc_mmu_book3s_32_ea_to_vp`, and `kvmppc_mmu_book3s_32_init`.

## Control Flow
Translation first checks the supervisor-only magic page override, then tries matching DBAT/IBAT entries with permission checks, then searches primary and secondary guest PTE groups derived from SDR1, VSID, and page index. PTE groups are read from guest memory through HVA mapping, decoded as big-endian 32-bit pairs, and permissions are derived from segment key bits plus PTE PP bits. If an entry is used, the code writes guest accessed and dirty bits back as single-byte updates to mimic hardware. Segment updates write guest SR state and map the corresponding shadow segment; `tlbie` flushes matching shadow PTEs on all vCPUs.

## State And Persistence
State lives in the vCPU Book3S extension: segment registers, BAT arrays, SDR1, magic-page addresses, and MMU callback table. Guest PTE A/C bits are persisted into guest memory, so swapper and OS memory management see hardware-like reference/change behavior.

## Dependencies And Integration Points
Depends on generic Book3S KVM MMU data structures, guest memory access helpers, PR shadow HPTE caching, segment mapping in `book3s_32_mmu_host.c`, and PPC 32-bit hash MMU formats. It is wired into PR guest execution by `kvmppc_mmu_book3s_32_init`.

## Risks And Edge Cases
Guest PTE reads can fail if SDR1 points outside memslots. BAT permissions differ by MSR[PR] and segment key state. The magic-page path uses `pte->raddr` offset bits and must not leak stale values. Primary/secondary hash lookup and single-byte A/C updates are subtle and race-prone with guest modification. The code assumes 4 KiB pages.

## Test Signals
Boot 32-bit Book3S guests under PR KVM, exercise BAT mappings, primary and secondary hash PTEs, read-only and no-access faults, dirty/accessed bit updates, `tlbie`, SR changes, magic page access, and 32-bit real/relocated MSR combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_32_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_32_mmu_host.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_32_mmu_host.c

## Purpose
Creates and manages host shadow hash-page-table entries for 32-bit Book3S PR KVM. It maps translated guest PTEs to host physical pages, maintains guest-VSID to host-VSID mappings, flushes shadow segments, and initializes/destroys PR MMU host context state.

## Important APIs, Types, And Functions
Exports `kvmppc_mmu_invalidate_pte`, `kvmppc_mmu_map_page`, `kvmppc_mmu_unmap_page`, `kvmppc_mmu_map_segment`, `kvmppc_mmu_flush_segments`, `kvmppc_mmu_destroy_pr`, and `kvmppc_mmu_init_pr`. Helpers include `kvmppc_sid_hash`, `find_sid_vsid`, `kvmppc_mmu_get_pteg`, and `create_sid_map`. File-level globals `htab` and `htabmask` mirror the host SDR1 hash table.

## Control Flow
Initialization allocates multiple MMU context IDs, fills a pool of host VSIDs, records the host HTAB base/mask from SDR1, and initializes the HPTE cache. Segment mapping converts a guest ESID to a guest VSID using the active MMU callback, finds or creates a host VSID, and writes a shadow segment register. Page mapping faults in a host PFN, ensures a shadow segment exists, computes the host PTEG, picks a free or evicted slot, writes a 32-bit HPTE pair with interrupts disabled, and records it in the HPTE cache. Invalidations zero the HPTE and issue `tlbie`.

## State And Persistence
Persistent runtime state is per-vCPU context IDs, VSID pool cursors, SID map entries, shadow segment registers, HPTE cache entries, and host HTAB entries. Dirty pages are marked when writable mappings are created. All state is in-memory and is destroyed with the vCPU.

## Dependencies And Integration Points
Depends on 32-bit hash MMU definitions, context allocation/destruction, `kvmppc_gpa_to_pfn`, HPTE cache helpers, shadow-vCPU accessors, host SDR1, and local IRQ/TLB primitives. It is paired with `book3s_32_mmu.c` for guest translation.

## Risks And Edge Cases
The file explicitly rejects SMP and 64-bit PTE builds, so configuration coverage matters. Shadow HTAB insertion can evict entries after primary/secondary scans. Host VSID pool exhaustion flushes all mappings. Page references must be released correctly on HPTE cache exhaustion. Local IRQ disabling protects HPTE writes but broader hash-locking is unavailable in the supported uniprocessor configuration.

## Test Signals
Run 32-bit PR guests through hash faults, segment remaps, writable/read-only mappings, HPTE eviction, VSID pool wraparound, vCPU teardown, and TLB invalidation. Build tests should verify the SMP and PTE_64BIT exclusions remain enforced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_32_mmu_host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_32_sr.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_32_sr.S

## Purpose
Provides 32-bit Book3S PR assembly macros for switching segment-register and BAT state between host and guest on KVM entry/exit.

## Important APIs, Types, And Functions
Defines `LOAD_GUEST_SEGMENTS` and `LOAD_HOST_SEGMENTS` macros. Internal helper macros include `XCHG_SR`, `KVM_KILL_BAT`, and `KVM_LOAD_BAT`. It references shadow-vCPU offsets such as `SVCPU_SR`, saved BAT data in `BATS`, and kernel MM context fields.

## Control Flow
On guest entry, `LOAD_GUEST_SEGMENTS` loads all 16 guest shadow segment registers with `mtsr` and clears guest-visible BATs by writing zero to IBAT/DBAT upper and lower registers. On exit, `LOAD_HOST_SEGMENTS` restores saved host BAT registers, reconstructs high kernel segment registers for segments `0xc` to `0xf`, briefly enables data relocation to call `switch_mmu_context(current->mm)`, and disables paging again before returning to the exit path.

## State And Persistence
The macros directly mutate CPU segment registers, BAT SPRs, MSR[DR], and temporary GPRs. Persistent state is the saved host BAT table and shadow-vCPU segment array maintained elsewhere.

## Dependencies And Integration Points
Used by Book3S PR assembly entry/exit code. Depends on `asm-offsets`, SPR constants, `switch_mmu_context`, `current->mm`, and the convention that the guest runs with host R1/R2 and shadow-vCPU pointer in the expected registers.

## Risks And Edge Cases
Wrong register clobber assumptions or offset mismatches corrupt host or guest address translation. Calling `switch_mmu_context` requires paging enabled and preserves the exit-handler ID explicitly. BAT restoration only overwrites saved upper/lower pairs and must match host setup.

## Test Signals
Signals are 32-bit PR guest entry/exit stability, host memory access after guest exit, segment-register stress, BAT-using guests, and exception exits taken immediately after segment switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_32_sr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_entry.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_entry.S

## Purpose
Implements 64-bit Book3S KVM exception entry dispatch and POWER9 HV guest entry/exit assembly. It normalizes hcalls and interrupts from exception handlers, routes PR versus HV exits, supports skip-mode fault recovery, and saves/restores guest/host register state around P9 HV guest execution.

## Important APIs, Types, And Functions
Global entry points are `kvmppc_hcall`, `kvmppc_interrupt`, and `kvmppc_p9_enter_guest` (exported). Local paths include `.Lgot_save_area`, `.Lmaybe_skip`, `.Lret_to_ultra`, `kvmppc_p9_exit_hcall`, `kvmppc_p9_exit_interrupt`, and `kvmppc_p9_bad_interrupt`. It uses PACA `HSTATE_*`, `EX_*` save areas, `VCPU_*` offsets, `KVM_GUEST_MODE_*`, `HRFI_TO_GUEST`, `RFI_TO_KERNEL`, and ultravisor `UV_RETURN`.

## Control Flow
`kvmppc_hcall` detects P9 HV guest mode and branches to the P9 hcall exit path, otherwise normalizes state to look like a generic interrupt. `kvmppc_interrupt` chooses the correct PACA save area, saves CFAR/PPR/CTR and scratch registers, and dispatches to PR or HV handlers based on `HSTATE_IN_GUEST`. Skip-mode faults from guest-context instruction loads are handled by advancing SRR0/HSRR0 and returning to kernel code without going through full KVM exit. `kvmppc_p9_enter_guest` saves host nonvolatile state, loads guest LR/CTR/XER/CR/CFAR/PPR/GPRs, and enters with `HRFI_TO_GUEST` or returns to the ultravisor for secure guests. P9 exit saves guest state to the vCPU, restores host stack/nonvolatile registers, optionally flushes the link stack, and returns to C.

## State And Persistence
The code persists guest GPRs, CR, LR, XER, PC, MSR, CFAR/PPR, and selected scratch values in `struct kvm_vcpu` and PACA HSTATE fields. It temporarily mutates host stack, PACA guest mode flags, SRR/HSRR state, and special registers. Secure guest paths coordinate with Ultravisor state.

## Dependencies And Integration Points
Depends on 64S exception handlers, PACA layout, generated asm offsets, PR and HV interrupt handlers, P9 entry C code, ultravisor ABI, CPU feature patching, and link-stack flush patch sites. It is the assembly bridge between Linux exception entry and KVM Book3S execution.

## Risks And Edge Cases
Register save/restore omissions cause silent guest or host corruption. Skip-mode recovery intentionally advances faulting host loads and must only apply to expected MCE/DSI/segment faults. P9 bad-interrupt recovery is best-effort and loops for hash hosts. Secure guest ultracall return uses a special register contract. Feature-patched CFAR/PPR/link-stack code must match CPU capabilities.

## Test Signals
Guest boot and migration on POWER9/POWER10 HV, PR syscall reflection, hcall exits, external/decrementer/data-storage interrupts, prefixed instruction faults, secure guest ultravisor exits, injected machine checks/system resets, and host stability after repeated entry/exit cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu.c

## Purpose
Implements 64-bit Book3S PR guest hash-MMU translation and SLB emulation. It decodes guest SLB entries, locates guest HPTEs, computes guest physical addresses and permissions, updates guest reference/change bits, and installs the 64-bit Book3S PR MMU callback table.

## Important APIs, Types, And Functions
Major helpers include `kvmppc_mmu_book3s_64_find_slbe`, `kvmppc_slb_calc_vpn`, `kvmppc_mmu_book3s_64_get_pteg`, `kvmppc_mmu_book3s_64_get_avpn`, `decode_pagesize`, `kvmppc_mmu_book3s_64_xlate`, `kvmppc_mmu_book3s_64_slbmte`, `slbfee`, `slbmfee`, `slbmfev`, `slbie`, `slbia`, `mtsrin`, `tlbie`, `esid_to_vsid`, `ea_to_vp`, `is_dcbz32`, and `kvmppc_mmu_book3s_64_init`.

## Control Flow
Translation checks the magic page, finds a matching 256 MiB or 1 TiB SLB entry, constructs the AVPN and HPTE search mask, locks the VM HPT mutex, scans primary then secondary guest PTEGs, decodes page size and permission bits, computes RPN plus effective-address offset, and writes R/C bits back with single-byte updates. SLB instructions mutate the emulated SLB array and trigger shadow segment mapping or flushing. `tlbie` computes a vpage flush mask based on processor generation and large-page encoding and flushes all vCPUs.

## State And Persistence
State is per-vCPU SLB entries, SDR1, hflags, HID bits, magic page data, and callback function pointers. Guest HPTE R/C updates persist into guest memory. Shadow segment mappings are maintained in the host PR MMU layer.

## Dependencies And Integration Points
Depends on Book3S 64 hash MMU definitions, HPT hash helpers, guest memory copy helpers, PR host MMU mapping in `book3s_64_mmu_host.c`, and common Book3S translation wrappers. It supports PAPR guests where SDR1 may contain an HVA rather than a GPA.

## Risks And Edge Cases
The source snapshot contains questionable duplicated assignment (`key = 4`) and a debug print referencing `page` outside the visible local declaration, which are correctness/compile risks if active. Mixed page-size decoding is limited. SLB bounds checks use slot numbers from guest registers and must prevent array overflow. R/C updates race with guest HPTE modification but intentionally mimic hardware byte writes. Magic-page translation depends on correct segment fallback when no SLB exists.

## Test Signals
Boot 64-bit PR hash guests, exercise 4K/64K/16M mappings, primary/secondary HPT lookup, SLB insert/remove/all-invalidate, `mtsrin`, `tlbie` old and POWER6+ encodings, PAPR SDR1 HVA mode, magic page access, NX/disable-kernel-NX behavior, and dirty/reference bit observation by guest OS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu_host.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu_host.c

## Purpose
Manages host shadow hash-MMU mappings for 64-bit Book3S PR KVM. It maps translated guest PTEs into host HPTEs, manages guest-to-host VSID mappings and shadow SLB entries, flushes segments, and initializes/destroys PR MMU context state.

## Important APIs, Types, And Functions
Exports `kvmppc_mmu_invalidate_pte`, `kvmppc_mmu_map_page`, `kvmppc_mmu_unmap_page`, `kvmppc_mmu_map_segment`, `kvmppc_mmu_flush_segment`, `kvmppc_mmu_flush_segments`, `kvmppc_mmu_destroy_pr`, and `kvmppc_mmu_init_pr`. Helpers include `kvmppc_sid_hash`, `find_sid_vsid`, `create_sid_map`, and `kvmppc_mmu_next_segment`.

## Control Flow
Page mapping snapshots `mmu_invalidate_seq`, faults in the GPA to a host PFN, ensures a host VSID/SLB mapping exists, computes VPN/hash, allocates an HPTE cache record, and inserts a primary or secondary HPTE using `mmu_hash_ops`. On collisions it retries secondary and may remove old entries after repeated attempts. Segment mapping chooses or allocates a shadow SLB slot, translates guest ESID to VSID, creates a scrambled host VSID, and writes an SLB entry with optional 64K page-size encoding. Context init allocates a hash context ID and derives a proto-VSID range.

## State And Persistence
Per-vCPU state includes context ID, proto-VSID cursor/range, SID map array, shadow SLB entries, and HPTE cache entries. Per-VM state includes the host hash table and invalidation sequence. Dirty pages are marked when writable mappings are installed.

## Dependencies And Integration Points
Depends on `mmu_hash_ops`, hash context allocation, VSID scrambling, pkey-to-HPTE permission bits, HPTE cache helpers, `kvmppc_gpa_to_pfn`, KVM MMU notifier sequencing, and shadow-vCPU accessors. It pairs with `book3s_64_mmu.c` for guest translation.

## Risks And Edge Cases
MMU invalidation races are controlled by sequence checks under `kvm->mmu_lock`; missing a retry risks installing stale PFNs. 64K host-page handling must preserve low guest real-address bits when the guest segment is not 64K-capable. SID-map collisions and proto-VSID exhaustion flush segments and PTEs. The source snapshot contains a duplicated `if (backwards_map)` line, a compile/logic risk if active.

## Test Signals
Signals include 64-bit PR guest boot, host page invalidation under memory pressure, dirty logging, 64K-page kernels, NX mappings, writable-to-readonly downgrade, SLB exhaustion, VSID wraparound, HPTE insertion collisions, and vCPU teardown freeing contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu_host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu_hv.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu_hv.c

## Purpose
Implements Book3S HV hash-MMU management and hash/radix delegation for KVM-HV. It allocates and resets guest HPTs, maps VRMA, translates HV hash entries, handles hash page faults and MMIO emulation, manages reverse maps, aging and dirty logging, supports HPT resize and migration file descriptors, and exposes debugfs HPT dumps.

## Important APIs, Types, And Functions
Important APIs include `kvmppc_allocate_hpt`, `kvmppc_set_hpt`, `kvmppc_alloc_reset_hpt`, `kvmppc_free_hpt`, `kvmppc_map_vrma`, `kvmppc_mmu_hv_init`, `kvmppc_book3s_hv_page_fault`, `kvmppc_rmap_reset`, `kvm_unmap_gfn_range_hv`, `kvmppc_core_flush_memslot_hv`, `kvm_age_gfn_hv`, `kvm_test_age_gfn_hv`, `kvmppc_hv_get_dirty_log_hpt`, `kvmppc_pin_guest_page`, `kvmppc_unpin_guest_page`, `kvm_vm_ioctl_resize_hpt_prepare`, `kvm_vm_ioctl_resize_hpt_commit`, `kvm_vm_ioctl_get_htab_fd`, `kvmppc_mmu_debugfs_init`, and `kvmppc_mmu_book3s_hv_init`. Internal structures include `struct kvm_resize_hpt`, `struct kvm_htab_ctx`, and `struct debugfs_htab_state`.

## Control Flow
HPT allocation obtains CMA or normal pages, zeroes the table, allocates a reverse-map array, and stores SDR1. Reset blocks vCPUs via `mmu_setup_lock`/`mmu_ready`, switches radix VMs back to HPT if needed, clears or reallocates the table, resets rmaps, and requests TLB flushes. Hash page fault handling verifies the real-mode-found HPTE, translates GPA, handles MMIO for missing memslots, faults in host pages, checks host PTE attributes and WIMG compatibility, locks HPTE/rmap chains, installs the real HPTE, and records R/C bits. Rmap functions unmap, age, test age, and clear dirty bits by walking HPTE chains. Resize prepare allocates a new HPT asynchronously; commit stops vCPUs, rehashes bolted entries, pivots tables, and resumes the VM. HPT fd read/write serializes or restores guest HPTE state for migration.

## State And Persistence
Per-VM persistent runtime state includes `kvm->arch.hpt`, reverse maps in memslots, `mmio_update`, `mmu_ready`, resize work state, LPID, VRMA SLB value, and HPTE modification interest. Per-vCPU state includes page-fault cache fields, SLB entries, and MMU callback pointers. Migration read/write exposes HPT state through an anonymous inode; debugfs exposes a read-only textual view.

## Dependencies And Integration Points
Depends on PPC hash MMU operations, KVM-HV hcall implementation, rmap helpers, KVM SRCU and MMU notifier sequencing, Linux page faulting, memslot dirty bitmaps, debugfs, anon inode APIs, radix helpers for radix VMs, pseries/powernv LPID behavior, and partition table setup on POWER9+. It integrates with QEMU migration through `KVM_GET_HTAB_FD` and HPT resize ioctls.

## Risks And Edge Cases
This is one of the highest-risk files in the subset. HPTE lock ordering against rmap locks is explicit to avoid ABBA deadlocks. Dirty/reference bit harvesting is inherently racy with running vCPUs. HPT resize must stop vCPUs and preserve bolted entries without losing rmaps. MMIO emulation reads the faulting instruction after translation and must avoid advancing the PC on mismatched prefixed/non-prefixed instructions. The source snapshot has duplicated lines in control blocks, which are compile/logic risks if present. Attribute mismatches, huge-page alignment, secure/nested transitions, and hash-vs-radix dispatch all need careful coverage.

## Test Signals
Run KVM-HV hash guests through VRMA boot, H_ENTER/H_REMOVE, hash faults, MMIO loads/stores including prefixed instructions, dirty logging with huge pages, live migration via HPT fd, HPT resize prepare/commit/cancel, memory slot deletion, page aging, nested disabled/enabled builds, POWER7/8/9 variants, and debugfs HPT reads. Stress with concurrent vCPUs and host MMU invalidations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu_hv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu_radix.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu_radix.c

## Purpose
Implements Book3S HV radix-MMU support: guest radix table walking, guest memory copy through LPID/PID contexts, second-level radix page-table creation and teardown, radix page fault handling, TLB/PWC invalidation, aging and dirty logging, RMMU capability reporting, secure guest handling, nested rmap integration, debugfs dumps, and radix page-table slab cache lifecycle.

## Important APIs, Types, And Functions
Key APIs are `__kvmhv_copy_tofrom_guest_radix`, `kvmhv_copy_from_guest_radix`, `kvmhv_copy_to_guest_radix`, `kvmppc_mmu_walk_radix_tree`, `kvmppc_mmu_radix_translate_table`, `kvmppc_mmu_radix_xlate`, `kvmppc_radix_tlbie_page`, `kvmppc_unmap_pte`, `kvmppc_free_pgtable_radix`, `kvmppc_free_radix`, `kvmppc_create_pte`, `kvmppc_hv_handle_set_rc`, `kvmppc_book3s_instantiate_page`, `kvmppc_book3s_radix_page_fault`, `kvm_unmap_radix`, `kvm_age_radix`, `kvm_test_age_radix`, `kvmppc_hv_get_dirty_log_radix`, `kvmppc_radix_flush_memslot`, `kvmhv_get_rmmu_info`, `kvmppc_init_vm_radix`, `kvmhv_radix_debugfs_init`, `kvmppc_radix_init`, and `kvmppc_radix_exit`.

## Control Flow
Guest copy uses pseries hypercalls when necessary or switches LPID/PID and copies through radix quadrants with page faults disabled. Translation walks process/partition table entries, validates supported radix geometry, reads guest PTEs, and derives GPA and permissions. Page faults reject unsupported DSISR cases, translate `fault_gpa`, hand secure pages to the ultravisor, emulate MMIO for missing memslots, reflect readonly writes as DSI, optionally handles hardware set-R/C failures, faults in host pages, chooses 4K/2M/1G mappings when dirty logging and alignment allow, and inserts second-level PTEs under `mmu_lock`. Unmap/free paths recursively clear page tables, flush TLB/PWC, update dirty maps, and remove nested rmaps.

## State And Persistence
Per-VM state includes `arch.pgtable`, process-table pointer, LPID, secure guest flags, large-page counters, nested rmaps, and MMU invalidation sequence. Slab caches `kvm_pte_cache` and `kvm_pmd_cache` persist while KVM radix support is loaded. Guest page-table R/C state and KVM dirty bitmaps are updated as part of fault and dirty-log handling.

## Dependencies And Integration Points
Depends on radix MMU helpers, pseries `H_COPY_TOFROM_GUEST`, RPT invalidate hypercalls, ultravisor/secure guest APIs, KVM memslots and MMU notifiers, nested-HV rmap helpers, Linux page-table allocation, debugfs, and Power9-supported radix geometry. It is dispatched from the HV MMU path when `kvm_is_radix(kvm)` is true.

## Risks And Edge Cases
LPID/PID switching must restore host state exactly and is disabled for nestedv2. Geometry validation rejects unsupported guest trees but must return the right guest-visible fault. Large-page insertion races with existing smaller mappings and invalidations; `PTE_BITS_MUST_MATCH` limits acceptable concurrent differences. Dirty logging forces 4K mappings. Secure guest state bypasses normal unmap/age/dirty behavior. The source snapshot contains duplicate declarations in `kvm_radix_test_clear_dirty`, a compile risk if active. TLB invalidation differs between bare metal, pseries hcalls, and RPT invalidate firmware.

## Test Signals
Boot radix HV guests with 4K and 64K base pages, exercise 4K/2M/1G mappings, dirty logging transitions, memslot removal, MMIO faults, DSISR set-R/C handling, secure guest page sharing, nested guest shadow pgtable updates, RMMU info ioctl, debugfs radix output, pseries and powernv invalidation paths, and slab init/exit failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu_radix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_slb.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_slb.S

## Purpose
Provides 64-bit Book3S PR assembly macros for loading guest SLB entries on entry and restoring host bolted SLB entries on exit.

## Important APIs, Types, And Functions
Defines `LOAD_GUEST_SEGMENTS` and `LOAD_HOST_SEGMENTS`. It uses shadow SLB entry offsets `SVCPU_SLB`, `SVCPU_SLB_MAX`, PACA `PACA_SLBSHADOWPTR`, `SLBSHADOW_SAVEAREA`, `SLB_NUM_BOLTED`, firmware feature patch sections, and labels `slb_loop_enter`, `slb_do_enter`, and `slb_do_exit`.

## Control Flow
Guest entry clears the LPAR SLB shadow count, invalidates the SLB with `slbia`, then iterates the shadow-vCPU SLB array and issues `slbmte` for valid guest entries. Host exit clears the current SLB, restores the LPAR shadow count for bolted entries, reads bolted ESID/VSID pairs from the PACA shadow save area, reloads nonzero entries, and synchronizes.

## State And Persistence
The macros mutate hardware SLB entries and the firmware-visible PACA SLB shadow count. Guest SLB state is sourced from the shadow vCPU; host bolted state is sourced from PACA shadow storage.

## Dependencies And Integration Points
Used by Book3S PR entry/exit code for 64-bit hash MMU guests. Depends on generated offsets, SLB instruction availability, LPAR firmware feature detection, and PACA SLB shadow layout.

## Risks And Edge Cases
Failure to restore bolted host SLB entries can leave the host unable to address kernel mappings after exit. Guest SLB count and entry validity must be trusted only within the allocated shadow array. LPAR shadow count handling must match firmware expectations.

## Test Signals
Boot 64-bit PR guests under LPAR and non-LPAR, stress guest SLB insert/remove/all-invalidate operations, force exits after many guest SLB entries, and verify host stability after repeated entry/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_slb.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_vio.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_vio.c

## Purpose
Implements SPAPR virtual I/O TCE table support for 64-bit Book3S KVM. It creates mmap-able emulated TCE tables, attaches host IOMMU tables, translates guest TCEs to userspace and hardware mappings, and implements PAPR TCE hypercalls.

## Important APIs, Types, And Functions
Important APIs are `kvm_spapr_tce_release_iommu_group`, `kvm_spapr_tce_attach_iommu_group`, `kvm_vm_ioctl_create_spapr_tce`, `kvmppc_h_put_tce`, `kvmppc_h_put_tce_indirect`, `kvmppc_h_stuff_tce`, and `kvmppc_h_get_tce`. Helpers include `kvmppc_find_table`, `kvmppc_tce_pages`, `kvmppc_stt_pages`, `kvm_spapr_get_tce_page`, `kvmppc_tce_to_ua`, `kvmppc_tce_validate`, `kvmppc_tce_put`, `kvmppc_clear_tce`, `kvmppc_tce_iommu_map`, and `kvmppc_tce_iommu_unmap`.

## Control Flow
Table creation validates size/page shift/offset, charges locked memory, allocates a flexible table structure, rejects duplicate LIOBNs, creates an anonymous fd, and links the table into `kvm->arch.spapr_tce_tables`. Table pages are allocated lazily on mmap faults or nonzero TCE stores. IOMMU attach validates that a hardware table covers the guest DMA window, refs it, and records it with RCU/kref lifetime. `H_PUT_TCE` validates one TCE, maps or unmaps every attached IOMMU table, updates the emulated table, and rolls back hardware entries on failure. Indirect put validates up to 512 big-endian TCEs from guest memory, then maps each. Stuff TCE unmaps ranges and writes poison/zero values. Get TCE returns zero for unallocated pages or the stored entry in GPR4.

## State And Persistence
Per-VM state is the RCU list of SPAPR TCE tables. Each table stores LIOBN, page shift, offset, size, lazily allocated TCE pages, attached IOMMU tables, krefs, and a KVM reference held by the fd. Hardware IOMMU table mappings and userspace-entry arrays are mutated and persist until unmapped or released.

## Dependencies And Integration Points
Depends on KVM Book3S PAPR hypercall handling, Linux IOMMU table APIs, mm IOMMU pin/accounting helpers, KVM memslots/SRCU, anon inode fds, mmap fault handling, RCU, krefs, and PAPR TCE ABI constants. It integrates emulated devices, VFIO/IOMMU-backed passthrough, and userspace migration/inspection through the TCE fd.

## Risks And Edge Cases
Reference, RCU, and locked-memory accounting must be balanced across fd release, IOMMU group release, and attach races. Indirect TCE validation intentionally rereads userspace entries, relying on later checks to keep host safety. Attached IOMMU page shifts may be smaller than guest TCE page shifts, requiring subpage loops and full `iommu_tce_kill` coverage. The source snapshot includes duplicate local declarations and a duplicated function-call line in mapping code, which are compile risks if active. Lazy TCE pages mean zero entries are implicit.

## Test Signals
Use PAPR guests with virtio/vhost/VFIO DMA, create/destroy TCE windows, mmap TCE fds, attach/detach IOMMU groups, run `H_PUT_TCE`, `H_PUT_TCE_INDIRECT`, `H_STUFF_TCE`, and `H_GET_TCE`, test invalid LIOBN/IOBA/page shift/offsets, stress table fd release during DMA window changes, and verify locked memory accounting returns to zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_vio.c -->
