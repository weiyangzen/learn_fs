# Research: subset-b-000873

Grouped research for x86 page layout, page table, paravirtualization, PCI, per-CPU, perf, protection-key, posted-interrupt, and processor support headers. Each section is keyed by exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/page_32_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/page_32_types.h

Purpose: defines 32-bit x86 page and virtual-address layout constants used before the rest of the paging headers can derive generic limits. It fixes `__PAGE_OFFSET`, `TASK_SIZE`, stack limits, thread/IRQ stack sizing, exception-stack count, kernel-image virtual limit, and physical/virtual mask widths for PAE and non-PAE builds.

Important APIs, types, and functions: the public surface is macro-based: `__PAGE_OFFSET_BASE`, `__PAGE_OFFSET`, `__START_KERNEL_map`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `IRQ_STACK_SIZE`, `N_EXCEPTION_STACKS`, `__PHYSICAL_MASK_SHIFT`, `__VIRTUAL_MASK_SHIFT`, `TASK_SIZE*`, `DEFAULT_MAP_WINDOW`, `STACK_TOP*`, and `KERNEL_IMAGE_SIZE`. Non-assembler users also see `__VMALLOC_RESERVE`, `sysctl_legacy_va_layout`, and `find_low_pfn_range()`.

Control flow: no executable flow is implemented here. Compile-time configuration selects PAE versus non-PAE physical mask definitions and exports constants consumed by page-table setup, memory layout, KASLR, vmalloc/highmem, and user address-space limit code.

State and persistence: runtime state is limited to extern declarations for vmalloc reserve, legacy VA layout sysctl, and low PFN discovery implemented elsewhere. There is no persistence.

Dependencies and integration points: depends on `CONFIG_PAGE_OFFSET`, `CONFIG_X86_PAE`, `CONFIG_VMSPLIT_*`, and highmem/vmalloc users. It feeds `page_types.h`, `pgtable_32_types.h`, boot memory initialization, user-stack placement, and module/vmalloc area calculation.

Risks: changing `__PAGE_OFFSET` or mask shifts changes the 32-bit kernel/user split and can break highmem, KASLR placement, and PAE PROT_NONE inversion assumptions. The PAE physical mask is intentionally wider than the real 44-bit PFN limit to preserve guest inverted PROT_NONE behavior.

Test signals: build both PAE and non-PAE i386 configurations, boot with different VMSPLIT/HIGHMEM options, verify `/proc/meminfo` lowmem/highmem sizing, vmalloc range, stack top, and KASLR placement, and exercise mappings near `TASK_SIZE` and `PAGE_OFFSET`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/page_32_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/page_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/page_64.h

Purpose: supplies x86-64 page helpers that require C code rather than pure constants: virtual-to-physical conversion for kernel mappings, page clearing/copying declarations, and dynamic user task-size calculation for 4-level versus 5-level paging.

Important APIs, types, and functions: exports `max_pfn`, `phys_base`, `page_offset_base`, `vmalloc_base`, `vmemmap_base`, and `direct_map_physmem_end`. Key inline helpers are `__phys_addr_nodebug()`, `__phys_addr_symbol()`, `clear_pages()`, `clear_page()`, and `task_size_max()`. It declares `__phys_addr()` when `CONFIG_DEBUG_VIRTUAL` is active, `__clear_pages_unrolled()`, and `copy_page()`.

Control flow: `__phys_addr_nodebug()` distinguishes kernel image addresses from direct-map addresses by subtracting `__START_KERNEL_map` and using carry behavior to choose `phys_base` or the direct-map delta. `clear_pages()` unpoisons KMSAN metadata, then uses alternative patching to select unrolled stores, `rep stosq`, or ERMS `rep stosb`. `task_size_max()` uses `alternative_io()` to return the highest user address for LA57 or non-LA57 CPUs.

State and persistence: this header reads boot/runtime layout globals but does not own them. Page clearing mutates memory only in caller-supplied kernel mappings.

Dependencies and integration points: depends on `page_64_types.h`, CPU feature alternatives, KMSAN, debug virtual checks, KCFI references, and x86 boot memory layout. It integrates with generic page clear/copy code, `virt_to_phys()` paths, and `TASK_SIZE_MAX`.

Risks: physical address conversion is security- and crash-sensitive; wrong range logic corrupts DMA, page tables, or symbol fixups. `clear_pages()` inline assembly must accurately declare clobbers despite embedding a call. `task_size_max()` protects against highest-canonical-page CPU errata and SYSRET hazards.

Test signals: boot 4-level and 5-level paging systems, run `CONFIG_DEBUG_VIRTUAL`, KMSAN, and alternatives tests, validate `virt_to_phys()` for direct map and kernel text, clear/copy page selftests, and mmap tests near `DEFAULT_MAP_WINDOW` and `TASK_SIZE_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/page_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/page_64_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/page_64_types.h

Purpose: defines x86-64 page-size-adjacent layout constants: thread, IRQ, and exception stack sizes; IST indexes; page-offset base addresses for 4-level and 5-level paging; kernel image virtual base and size; address mask shifts; and user-space task/stack limits.

Important APIs, types, and functions: key macros are `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `EXCEPTION_STACK_ORDER`, `EXCEPTION_STKSZ`, `IRQ_STACK_ORDER`, `IRQ_STACK_SIZE`, `IST_INDEX_*`, `__PAGE_OFFSET_BASE_L5`, `__PAGE_OFFSET_BASE_L4`, `__PAGE_OFFSET`, `__START_KERNEL_map`, `__PHYSICAL_MASK_SHIFT`, `__VIRTUAL_MASK_SHIFT`, `TASK_SIZE_MAX`, `DEFAULT_MAP_WINDOW`, `IA32_PAGE_OFFSET`, `TASK_SIZE_LOW`, `TASK_SIZE`, `TASK_SIZE_OF()`, `STACK_TOP*`, and `KERNEL_IMAGE_SIZE`.

Control flow: there is no runtime control flow except macro expansion. `KASAN_STACK_ORDER`, `RANDOMIZE_BASE`, `pgtable_l5_enabled()`, `TIF_ADDR32`, and process personality control the concrete values selected by users.

State and persistence: the header itself has no state. It reads `page_offset_base` through `__PAGE_OFFSET` and tests thread flags when task-size macros are used.

Dependencies and integration points: included by `page_64.h` and `page_types.h`, and indirectly by paging, entry, signal, stack, KASLR, module-layout, and compat mmap code. IST indexes must match the TSS hardware exception stack layout.

Risks: address constants must stay synchronized with `Documentation/arch/x86/x86_64/mm.rst`, PTI LDT remap space, Xen hypervisor slots, module/fixmap placement, and KASLR constraints. Stack-size changes affect interrupt/exception overflow margins and kernel memory footprint.

Test signals: boot tests with KASAN on/off, KASLR on/off, LA57 on/off, compat 32-bit tasks, and PTI; verify stack overflow tests, IST exception delivery for DF/NMI/DB/MCE/VC, module range placement, and user mappings just below task-size boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/page_64_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/page_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/page_types.h

Purpose: provides common x86 page constants shared by 32-bit and 64-bit builds, including physical/virtual masks, huge-page sizes, page offset, kernel load address, ioremap maximum order, and architecture hooks for memory initialization and mapped PFN queries.

Important APIs, types, and functions: defines `__VIRTUAL_MASK`, `PHYSICAL_PAGE_MASK`, `PHYSICAL_PMD_PAGE_MASK`, `PHYSICAL_PUD_PAGE_MASK`, `HPAGE_SHIFT`, `HPAGE_SIZE`, `HPAGE_MASK`, `HUGETLB_PAGE_ORDER`, `HUGE_MAX_HSTATE`, `PAGE_OFFSET`, `LOAD_PHYSICAL_ADDR`, and `__START_KERNEL`. C-visible exports include `physical_mask` when dynamic, `devmem_is_allowed()`, `max_low_pfn_mapped`, `max_pfn_mapped`, `get_max_mapped()`, `pfn_range_is_mapped()`, and `initmem_init()`.

Control flow: compile-time architecture selection includes either `page_64_types.h` or `page_32_types.h`, and sets `IOREMAP_MAX_ORDER` to PUD or PMD scale. `get_max_mapped()` derives bytes from `max_pfn_mapped`.

State and persistence: state is external memory-map state initialized by boot code. No persistent storage is touched.

Dependencies and integration points: depends on generic page constants, `mem_encrypt.h`, vDSO page constants, `CONFIG_DYNAMIC_PHYSICAL_MASK`, and architecture-specific page type headers. It feeds devmem access checks, direct-map setup, ioremap, huge page definitions, and memory initialization.

Risks: mask calculations must handle 32-bit PAE sign-extension, SME/CoCo encryption masks, and dynamic physical address widths. Incorrect `LOAD_PHYSICAL_ADDR` or `__START_KERNEL` breaks decompressor/kernel relocation assumptions.

Test signals: build 32/64-bit, PAE, SME/SEV, and dynamic physical mask configurations; validate `/dev/mem` filtering, direct-map range detection, hugepage mapping attributes, boot-time memory initialization, and ioremap with large-order mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/page_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt-base.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt-base.h

Purpose: defines the small base layer shared by x86 paravirtualization headers: metadata about the active paravirt environment, the callee-save wrapper type used by paravirt call sites, and common stubs/capability hooks.

Important APIs, types, and functions: `struct paravirt_callee_save` wraps non-standard calling-convention functions. `struct pv_info` records `name`, `io_delay`, and, under `CONFIG_PARAVIRT_XXL`, `extra_user_64bit_cs`. It declares `default_banner()`, global `pv_info`, `paravirt_ret0()`, optional `_paravirt_ident_64()`, `paravirt_nop`, `call_io_delay()`, and `paravirt_set_cap()`.

Control flow: this header is mostly declarations and compile-time selection. When paravirt spinlocks are disabled, `paravirt_set_cap()` becomes an inline no-op; when `CONFIG_PARAVIRT` is enabled, `call_io_delay()` reads `pv_info.io_delay`.

State and persistence: `pv_info` is runtime global metadata selected during boot by native or hypervisor setup. There is no persistence.

Dependencies and integration points: consumed by `paravirt_types.h`, `paravirt.h`, and `paravirt-spinlock.h`; implemented by native, Xen PV, and other paravirt setup code. `paravirt_nop` points to `nop_func` for alternative patching.

Risks: `struct paravirt_callee_save` is part of the low-level calling convention contract used from inline assembly. Incorrect `pv_info` setup affects boot banners, I/O delay behavior, and segment assumptions under paravirt XXL.

Test signals: native and Xen PV boot logs, paravirt alternative patching, `io_delay` behavior, spinlock capability setup, and build coverage across `CONFIG_PARAVIRT`, `CONFIG_PARAVIRT_XXL`, and `CONFIG_PARAVIRT_SPINLOCKS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt-base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt-spinlock.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt-spinlock.h

Purpose: defines the paravirtualized queued-spinlock interface and the fallback virtual spinlock shortcut for x86 guests. It lets hypervisors replace queued spinlock slow paths, unlock, wait/kick, and vCPU-preemption checks with PV-aware operations.

Important APIs, types, and functions: `struct pv_lock_ops` contains `queued_spin_lock_slowpath`, callee-save `queued_spin_unlock`, `wait`, `kick`, and callee-save `vcpu_is_preempted`. It declares global `pv_ops_lock`, native/PV slowpath and unlock symbols, `nopvspin`, `native_pv_lock_init()`, native test helpers, and `virt_spin_lock_key`. Inline wrappers include `pv_queued_spin_lock_slowpath()`, `pv_queued_spin_unlock()`, `pv_vcpu_is_preempted()`, `pv_wait()`, `pv_kick()`, `queued_spin_lock_slowpath()`, `queued_spin_unlock()`, `vcpu_is_preempted()`, `native_queued_spin_unlock()`, and `virt_spin_lock()`.

Control flow: under `CONFIG_PARAVIRT_SPINLOCKS`, queued spinlock calls dispatch through `PVOP_*` macros and can be patched to native byte-store unlock or no-preemption behavior when features are absent. `virt_spin_lock()` uses a static key to optionally replace fair queueing with test-and-set spinning in guests without PV spinlock support.

State and persistence: global PV ops and static key state are runtime-only. Lock state lives in each `qspinlock`.

Dependencies and integration points: depends on qspinlock layout, `paravirt_types.h`, static keys, KCSAN release annotation, CPU feature alternatives, KVM/Xen PV spinlock setup, and scheduler vCPU preemption reporting.

Risks: unlock uses a callee-save paravirt calling convention and must preserve release semantics on the low byte. Enabling `virt_spin_lock_key` trades fairness for avoiding holder-preemption stalls; incorrect use can regress native scalability or guest latency.

Test signals: qspinlock stress on native, KVM, and Xen; lock holder preemption tests; `nopvspin` boot option; static-key transitions during PV setup; KCSAN/lockdep validation; and CPU-hotplug with `vcpu_is_preempted()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt-spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt.h

Purpose: provides the user-facing inline replacements for privileged x86 operations when paravirtualization is enabled. It routes TLB flushes, halt/IRQ operations, descriptor/MSR/control-register operations, page-table manipulation, lazy MMU mode, fixmap setup, and context-switch hooks through `pv_ops`.

Important APIs, types, and functions: major wrappers include `__flush_tlb_local/global/one_user/multi()`, `paravirt_arch_exit_mmap()`, `notify_page_enc_status_changed()`, `arch_safe_halt()`, `halt()`, `load_sp0()`, `__cpuid()`, `get_debugreg()/set_debugreg()`, `read_cr0/cr2/cr3()`, `write_cr0/cr2/cr3/cr4()`, `rdmsr/wrmsr` variants, `rdpmc()`, descriptor table accessors, LDT/TLS helpers, paravirt page-table allocation/release hooks, `__pte()/pte_val()` and higher-level entry makers/value readers, `set_pte/pmd/pud/p4d/pgd()`, `ptep_modify_prot_*()`, clear helpers, `arch_start/end_context_switch()`, lazy MMU hooks, `__set_fixmap()`, and IRQ flag helpers.

Control flow: callers invoke normal architecture APIs; inline wrappers expand to `PVOP_*` macros that issue patchable indirect calls or alternative native instruction sequences. Many hot paths use `ALT_NOT_XEN` to bypass PV calls when not running Xen PV.

State and persistence: state is in the global `pv_ops` table and paravirt-patched instruction stream. The header itself persists nothing but can mutate page tables and CPU registers via callbacks.

Dependencies and integration points: depends on `paravirt_types.h`, `pgtable_types.h`, alternatives, nospec branch annotations, descriptor and thread types, and Xen/native paravirt implementations. It is deeply integrated with MM, entry, scheduler, TLB, and CPU setup.

Risks: these wrappers replace privileged instructions, so calling-convention, clobber, alternative-patching, and type-width mistakes can corrupt registers, page tables, or interrupt state. The `set_pgd()`/5-level folding logic must match page-table configuration.

Test signals: native and Xen PV boot, TLB shootdown tests, MSR safe/unsafe error paths, descriptor/TLS updates, page-table modification under fork/exec/mprotect, lazy MMU batching, PTI/fixmap setup, and objtool/IBT/retpoline validation of patched call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt_types.h

Purpose: defines the paravirtualization operation tables and the inline-assembly machinery used to call and patch those operations. It is the ABI between normal x86 architecture code and native/hypervisor-specific paravirt backends.

Important APIs, types, and functions: operation tables include `struct pv_lazy_ops`, `struct pv_cpu_ops`, `struct pv_irq_ops`, `struct pv_mmu_ops`, and aggregate `struct paravirt_patch_template pv_ops`. Macro APIs include `paravirt_ptr()`, `PARAVIRT_CALL`, `PVOP_CALL*`, `PVOP_VCALL*`, `PVOP_CALLEE*`, `PVOP_ALT_*`, `PV_SAVE_ALL_CALLER_REGS`, `PV_RESTORE_ALL_CALLER_REGS`, `PV_CALLEE_SAVE_REGS_THUNK()`, `PV_CALLEE_SAVE()`, and `__PV_IS_CALLEE_SAVE()`.

Control flow: `PVOP_*` macros marshal up to four arguments into x86 calling-convention registers, emit an indirect call through a table slot, and mark it for runtime alternative patching to direct calls or inline native sequences. Callee-save variants call generated thunks that preserve scratch registers around functions used from constrained assembly contexts.

State and persistence: global `pv_ops` is runtime state set by boot/hypervisor code. Alternative patching changes executable text during boot but has no external persistence.

Dependencies and integration points: depends on descriptor and page-table types, nospec/retpoline annotations, alternative call patching, ENDBR/IBT constraints, `CONFIG_X86_32` versus `CONFIG_X86_64` calling conventions, and paravirt backends.

Risks: this file is highly sensitive to compiler constraints and CPU control-flow protections. Wrong clobbers, argument constraints, return masking, or thunk definitions can silently corrupt state. Operation struct layout is intentionally not randomized because offsets identify patch targets.

Test signals: build 32-bit and 64-bit paravirt configurations, boot native and Xen PV, run objtool/CFI/IBT validation, inspect alternative patch sites, exercise all PV CPU/MMU/IRQ operations, and compile with `CONFIG_ZERO_CALL_USED_REGS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/parport.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/parport.h

Purpose: provides the x86 architecture hook used by the parport PC driver to discover non-PCI parallel ports. On x86, non-PCI probing is just ISA probing.

Important APIs, types, and functions: declares internal `parport_pc_find_isa_ports(int autoirq, int autodma)` and defines `parport_pc_find_nonpci_ports(int autoirq, int autodma)` as a wrapper returning the ISA probe result.

Control flow: callers invoke `parport_pc_find_nonpci_ports()`; it immediately delegates to `parport_pc_find_isa_ports()` with the auto IRQ/DMA policy supplied by the driver.

State and persistence: no state is owned. Detected ports and resource registrations are handled by the parport driver.

Dependencies and integration points: included by the parallel port subsystem's PC driver. It assumes ISA-style legacy port probing is the correct non-PCI path for x86.

Risks: small but ABI-like: if non-PCI discovery semantics change, this wrapper controls what legacy hardware is found. ISA probing can touch legacy I/O ports, so policy must remain in the driver.

Test signals: build parport PC support on x86, boot with legacy parallel port hardware or emulation, verify PCI and non-PCI ports are discovered appropriately, and test `autoirq`/`autodma` module parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/parport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pc-conf-reg.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pc-conf-reg.h

Purpose: defines helpers for the legacy PC indexed configuration register pair at I/O ports `0x22` and `0x23`, used by MP Spec IMCR, Cyrix CPUs, and old chipsets.

Important APIs, types, and functions: constants are `PC_CONF_INDEX`, `PC_CONF_DATA`, and `PC_CONF_MPS_IMCR`. It declares `raw_spinlock_t pc_conf_lock`. Inline helpers `pc_conf_get(u8 reg)` and `pc_conf_set(u8 reg, u8 data)` perform index/data port I/O.

Control flow: `pc_conf_get()` writes the register index to port `0x22` then reads the value from `0x23`. `pc_conf_set()` writes the index then the data byte. Serialization is not performed in the helpers; callers are expected to use `pc_conf_lock` where necessary.

State and persistence: state lives in hardware configuration registers and the external lock. Writes can persist in chipset/CPU register state until reset or later writes.

Dependencies and integration points: depends on `linux/io.h`, raw spinlocks, and low-level users such as Cyrix register access and IMCR/chipset setup code.

Risks: register access order is mandatory. Missing locking can interleave index/data cycles across CPUs or drivers. Touching unknown indexed registers can misconfigure legacy chipsets.

Test signals: Cyrix and MP-table legacy paths should read/write expected registers, lockdep should catch misuse when lock wrappers exist, and I/O tracing or hardware tests should confirm ordered `outb(0x22)` then `inb/outb(0x23)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pc-conf-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pci-direct.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pci-direct.h

Purpose: declares early direct PCI configuration-space accessors used before the generic PCI subsystem is initialized.

Important APIs, types, and functions: exports `read_pci_config()`, `read_pci_config_byte()`, `read_pci_config_16()`, `write_pci_config()`, `write_pci_config_byte()`, `write_pci_config_16()`, and `early_pci_allowed()`. All accessors take bus, slot, function, offset, and for writes a value.

Control flow: no implementation is in this header. Early boot code calls these functions to query or modify PCI config space before `struct pci_bus` and normal `pci_ops` are available. `early_pci_allowed()` gates whether such direct access is permitted in the current environment.

State and persistence: reads and writes target hardware PCI configuration registers. State persists in device configuration until reset or later reconfiguration.

Dependencies and integration points: implemented by x86 PCI direct access code and used by early quirks, chipset discovery, and boot-time PCI setup.

Risks: early direct config cycles bypass normal resource ownership, locking, and firmware mediation. Wrong bus/device/function or offsets can alter device decode, interrupts, or bridge windows before kernel PCI enumeration.

Test signals: early quirk logs, PCI enumeration after direct access, `early_pci_allowed()` behavior under firmware/virtualization restrictions, and boot tests on systems needing config type 1/type 2 access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pci-direct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pci-functions.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pci-functions.h

Purpose: provides conventional PCI BIOS function numbers for legacy PC BIOS interrupt/service interfaces.

Important APIs, types, and functions: defines constants such as `PCIBIOS_PCI_FUNCTION_ID`, `PCIBIOS_PCI_BIOS_PRESENT`, `PCIBIOS_FIND_PCI_DEVICE`, `PCIBIOS_FIND_PCI_CLASS_CODE`, special cycle generation, config byte/word/dword reads and writes, routing options, and interrupt assignment functions.

Control flow: there is no code. Legacy PCI BIOS callers use these constants when invoking BIOS services or decoding requests.

State and persistence: no state is owned. BIOS calls using these identifiers may read or modify firmware-managed PCI state.

Dependencies and integration points: consumed by `CONFIG_PCI_BIOS` x86 code and any compatibility logic that still talks to conventional PCI BIOS functions.

Risks: constants are firmware ABI values and must not be changed. This path is legacy but can matter on old systems without robust ACPI/MMCONFIG/direct PCI setup.

Test signals: build `CONFIG_PCI_BIOS`, boot legacy BIOS systems or emulators, validate `pci_pcbios_init()` detects BIOS presence and can read/write config space and routing information using these function IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pci-functions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pci.h

Purpose: defines x86 architecture data and hooks for the generic PCI subsystem, including per-root-bus metadata, PCI domain/NUMA lookup, MSI fwnode retrieval, VMD detection, legacy IRQ routing, mmap policy, early quirks, and IOMMU allocation.

Important APIs, types, and functions: `struct pci_sysdata` holds `domain`, `node`, optional ACPI companion, IOMMU private data, MSI fwnode, and VMD root device. Inline helpers include `to_pci_sysdata()`, `pci_domain_nr()`, `pci_proc_domain()`, `_pci_root_bus_fwnode()`, `is_vmd()`, `__pcibus_to_node()`, and `cpumask_of_pcibus()`. Externs include `pci_routeirq`, `noioapicquirk`, `noioapicreroute`, `pcibios_assign_all_busses()`, `pci_legacy_init()`, `pci_mem_start`, `pcibios_enabled`, `pcibios_scan_root()`, IRQ routing table helpers, `pci_dev_has_default_msi_parent_domain()`, `early_quirks()`, and `pci_iommu_alloc()`.

Control flow: generic PCI code calls architecture hooks during root-bus scanning, domain reporting, MSI domain assignment, mmap setup, early quirk execution, and IRQ routing. NUMA helpers map bus node metadata to CPU masks.

State and persistence: persistent hardware state is managed elsewhere; this header exposes runtime metadata embedded in each PCI bus. Globals configure boot-time PCI policy.

Dependencies and integration points: depends on generic PCI, ACPI, MSI IRQ domains, VMD, NUMA, PAT/memtype, and x86 IOMMU setup.

Risks: incorrect `pci_sysdata` initialization mislabels domains, NUMA nodes, IOMMU domains, MSI routing, or VMD membership. Legacy IRQ routing globals affect old systems and boot parameters.

Test signals: PCI enumeration with multiple domains, ACPI and legacy init paths, VMD root domains, MSI interrupt delivery, NUMA locality of PCI devices, PCI resource mmap with write-combining, and early quirk behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pci_x86.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pci_x86.h

Purpose: centralizes low-level x86 PCI probing policy, legacy IRQ routing structures, raw PCI config access backends, MMCONFIG region management, and x86-specific PCI init hook defaults.

Important APIs, types, and functions: defines `PCI_PROBE_*` and policy flags such as `PCI_ASSIGN_ALL_BUSSES`, `PCI_USE__CRS`, `PCI_NOASSIGN_BARS`, and `PCI_USE_E820`. It declares `pci_probe`, `pirq_table_addr`, `pci_bf_sort_state`, `pcibios_resource_survey()`, `pcibios_set_cache_line_size()`, `pcibios_last_bus`, `pci_root_ops`, `pcibios_scan_specific_bus()`, IRQ routing structs `irq_info`, `irq_routing_table`, `irt_routing_table`, raw ops `struct pci_raw_ops`, `raw_pci_ops`, `raw_pci_ext_ops`, `pci_mmcfg`, `pci_direct_conf1`, probe/init hooks, MMCONFIG region struct and functions, `pci_mmcfg_list`, and `mmio_config_read/write[bwl]()`.

Control flow: boot PCI initialization selects BIOS, direct config, or MMCONFIG access based on flags and DMI/ACPI checks. MMCONFIG helpers add/map/unmap regions. Raw ops provide read/write callbacks for generic PCI config access. Inline MMIO config helpers force `%eax/%ax/%al` for AMD Fam10h requirements.

State and persistence: global probe flags, raw ops pointers, config lock, PIRQ data, and MMCONFIG list are runtime state. Writes affect PCI config hardware.

Dependencies and integration points: ties together arch PCI files, ACPI, DMI, PCI IRQ routing, MMCONFIG resource tracking, direct PCI config, and legacy BIOS support.

Risks: probe flags can disable resource assignment or select unsafe access methods. MMCONFIG mapping must avoid invalid firmware ranges. Raw config access must be locked and respect AMD register constraints. PIRQ table layout is packed firmware ABI.

Test signals: boot with `pci=` options, ACPI and non-ACPI systems, MMCONFIG insert/delete, direct config fallback, PIRQ routing, DMI quirks, AMD Fam10h MMIO config accesses, and PCI resource allocation regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pci_x86.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/percpu.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/percpu.h

Purpose: implements x86-specific per-CPU access primitives using segment-relative addressing (`gs` on x86-64, `fs` on x86-32), optimized inline assembly operations, early per-CPU storage, and size-specialized raw/this-CPU APIs.

Important APIs, types, and functions: defines `__percpu_seg`, `PER_CPU_VAR()`, `__my_cpu_offset`, `arch_raw_cpu_ptr()`, per-CPU type/register/op macros, raw and this CPU read/write/add/and/or/xchg/add_return/cmpxchg/try_cmpxchg variants for 1/2/4/8 bytes, 64-bit and 128-bit cmpxchg helpers where supported, `this_cpu_read_stable()`, bit-test helpers, `DECLARE_PER_CPU_CACHE_HOT(unsigned long, this_cpu_off)`, and `DEFINE/DECLARE/EXPORT_EARLY_PER_CPU*` macros.

Control flow: compile-time configuration selects assembler versus C, SMP versus UP, named address-space support versus explicit segment prefixes, and 32-bit versus 64-bit atomic widths. Operations expand to single x86 instructions where possible, often without LOCK because the target is CPU-local. Early per-CPU macros use temporary arrays before real per-CPU areas exist.

State and persistence: per-CPU variables are runtime kernel state. Early maps live in init data and hand off to normal per-CPU areas. No external persistence exists.

Dependencies and integration points: depends on generic per-CPU infrastructure, x86 segment setup, CPU feature alternatives for CMPXCHG8B/16B, `this_cpu_off`, and many scheduler/MM/IRQ fast paths.

Risks: segment prefix, address-space annotations, and inline-asm constraints are fragile. `raw_cpu_*` assumes CPU-local access without preemption/IRQ safety. 32-bit VDSO and 64-bit kernel combinations have special restrictions. Using XCHG would impose expensive lock semantics, so cmpxchg loops are deliberate.

Test signals: per-CPU selftests, SMP and UP builds, KCSAN/lockdep with raw versus this-CPU use, preemption stress, early boot CPU bring-up, 32-bit builds without CX8, x86-64 CX16 paths, and objdump inspection for expected segment-relative instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/percpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/perf_event.h

Purpose: defines the x86 perf hardware contract: Intel/AMD event-select bitfields, CPUID capability structures, fixed and topdown pseudo counter indexes, PEBS/architectural PEBS record layouts, AMD IBS controls, perf architecture hooks, guest PMU switching interfaces, and vendor virtualization helpers.

Important APIs, types, and functions: key constants cover `ARCH_PERFMON_EVENTSEL_*`, Intel fixed counter MSRs/indexes, TopDown metric encodings, global status bits, AMD64 event and L3 masks, IBS capability/control bits, and PEBS data configuration bits. Important types include CPUID unions for leaves 0x0a, 0x23, 0x1c, and 0x80000022, `struct x86_pmu_capability`, PEBS/arch-PEBS record structs, `struct x86_perf_regs`, `struct perf_guest_switch_msr`, and `struct x86_pmu_lbr`. Helper APIs include `use_fixed_pseudo_encoding()`, `is_metric_idx()`, `is_topdown_idx()`, `get_ibs_caps()`, `forward_event_to_ibs()`, `perf_events_lapic_init()`, architecture IP/misc flag hooks, `perf_arch_fetch_caller_regs`, PMU capability/config getters, microcode/dirty-counter hooks, RDPMC index lookup, guest LVTPC/MSR/LBR helpers, Intel PT VMX callback, AMD PMU virtualization, and optional low-power callback static call.

Control flow: this header does not drive PMU programming directly; it defines encodings and dispatch declarations consumed by Intel/AMD perf drivers, KVM, APIC setup, and generic perf. Compile-time vendor/config guards provide no-op fallbacks when perf or vendor support is absent.

State and persistence: data structures describe CPU MSR/PEBS state and sampled register payloads. Actual counters, LBRs, PEBS buffers, and IBS state are hardware/runtime state owned by perf drivers.

Dependencies and integration points: integrates with `linux/perf_event`, static calls, local APIC, KVM guest switching, Intel PT, AMD BRS, PEBS, IBS, RDPMC, and `copy_from_user_nmi` for perf output copying.

Risks: event encodings are user-visible ABI through perf raw events and sysfs. Record layouts must match hardware exactly. Pseudo-counter indexes overlap with overflow status bits by design and must remain coordinated with PMI handling. Guest PMU switching must preserve host counters and virtualization isolation.

Test signals: `perf list`, raw event programming on Intel/AMD, fixed counters, TopDown metrics, PEBS sampling with memory/GPR/XMM/LBR/counter payloads, IBS fetch/op sampling, KVM PMU passthrough/mediated modes, RDPMC index tests, microcode update handling, and low-power AMD BRS callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/perf_event_p4.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/perf_event_p4.h

Purpose: defines NetBurst/Pentium 4 perf event encodings, ESCR/CCCR bitfields, event masks, PEBS metrics, HyperThreading handling helpers, and packed configuration format used by the P4 PMU driver.

Important APIs, types, and functions: constants include `ARCH_P4_TOTAL_ESCR`, `ARCH_P4_MAX_ESCR`, `ARCH_P4_MAX_CCCR`, counter width masks, ESCR event/eventmask/tag/thread bits, CCCR overflow/PMI/cascade/edge/thread bits, raw config masks, alias masks, PEBS config bits, and PEBS enable bits. Helpers include `p4_config_pack/unpack_escr/cccr()`, `p4_config_unpack_emask/event/metric/pebs()`, `p4_config_pebs_has()`, `p4_is_event_cascaded()`, HT helpers `p4_ht_config_thread()`, `p4_set/clear_ht_bit()`, `p4_ht_active()`, `p4_ht_thread()`, `p4_should_swap_ts()`, `p4_default_cccr_conf()`, and `p4_default_escr_conf()`. Enums enumerate `P4_EVENTS`, opcode encodings, ESCR event masks, and `P4_PEBS_METRIC`.

Control flow: the P4 perf implementation packs ESCR in the high 32 bits and CCCR in the low 32 bits of `perf_event_attr.config`, uses opcode/event-mask enums to select hardware registers, and applies HT thread swaps based on logical CPU sibling position.

State and persistence: no state is owned. The packed config is carried in perf events and eventually programmed into P4 hardware MSRs.

Dependencies and integration points: depends on CPU sibling maps, `__max_threads_per_core`, bitops, and the NetBurst PMU implementation. It intersects with legacy PEBS and HT-shared MSR behavior.

Risks: NetBurst PMU register topology is irregular, shared across HT siblings, and contains reserved/dangerous bits. Aliasable events must preserve caller bits while hiding kernel-internal bits. Incorrect thread selection or ESCR restriction mapping gives wrong counts or wrong PMI routing.

Test signals: perf event programming on Pentium 4/old Xeon or emulator, HT on/off, raw event mask validation, cascaded events, PEBS metrics on allowed counters, event alias handling, and counter overflow PMI delivery to the correct logical thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/perf_event_p4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgalloc.h

Purpose: provides x86 page-table allocation and population hooks layered on generic `pgalloc`, including PTI-aware PGD allocation order, paravirt notifications, and helpers for installing lower-level page-table pages.

Important APIs, types, and functions: defines `__HAVE_ARCH_PTE_ALLOC_ONE`, `__HAVE_ARCH_PGD_FREE`, `pgd_allocation_order()`, `pgd_alloc()`, `pgd_free()`, `pte_alloc_one()`, `___pte_free_tlb()`, `__pte_free_tlb()`, `pmd_populate_kernel()`, `pmd_populate_kernel_safe()`, `pmd_populate()`, and level-dependent `__pmd_free_tlb()`, `pud_populate()`, `pud_populate_safe()`, `p4d_populate()`, `p4d_populate_safe()`, `__pud_free_tlb()`, `pgd_populate()`, `pgd_populate_safe()`, and `__p4d_free_tlb()`.

Control flow: allocation order returns order-1 when PTI is enabled so each PGD has kernel and user halves. Populate helpers notify paravirt backends of page-table page allocation, then install entries with `_PAGE_TABLE` and physical addresses. Free helpers route through architecture TLB gather destructors.

State and persistence: page-table pages are allocated runtime memory attached to `mm_struct`s or kernel mappings. Paravirt hooks may maintain hypervisor shadow state.

Dependencies and integration points: depends on generic pgalloc, x86 page-table levels, `set_p*d()` helpers, `__pa()`, PTI feature detection, and paravirt XXL hooks.

Risks: missing paravirt notifications can desynchronize shadow page tables. Safe populate helpers must only be used when TLB flushing is unnecessary. PTI allocation order and 5-level folding must match top-level page-table layout.

Test signals: fork/exec/mmap page-table allocation, PTI on/off, Xen PV or other paravirt page-table tracking, THP/PUD/P4D allocation/free, TLB gather teardown, and debug page-table checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-2level.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-2level.h

Purpose: implements native page-table entry operations and swap-PTE encoding for traditional non-PAE i386 two-level paging.

Important APIs, types, and functions: defines `pte_ERROR()` and `pgd_ERROR()` diagnostics, `native_set_pte()`, `native_set_pmd()`, no-op `native_set_pud()`, `native_set_pte_atomic()`, `native_pmd_clear()`, `native_pud_clear()`, `native_pte_clear()`, SMP-aware `native_ptep_get_and_clear()`, `native_pmdp_get_and_clear()`, `native_pudp_get_and_clear()`, `pte_bitop()`, swap macros `SWP_TYPE_BITS`, `_SWP_TYPE_MASK`, `_SWP_TYPE_SHIFT`, `SWP_OFFSET_SHIFT`, `MAX_SWAPFILES_CHECK()`, `__swp_type()`, `__swp_offset()`, `__swp_entry()`, `__pte_to_swp_entry()`, `__swp_entry_to_pte()`, `_PAGE_SWP_EXCLUSIVE`, and non-inverting PROT_NONE helpers.

Control flow: native setters directly store entry values. SMP get-and-clear uses `xchg()`; UP uses local generic helpers. Swap entry encode/decode places type and offset into the limited 32-bit PTE format.

State and persistence: mutates page-table memory only. No external persistence exists.

Dependencies and integration points: included by `pgtable_32.h` when `CONFIG_X86_PAE` is off. It integrates with swap, userfaultfd/anon-exclusive swap markers through shared flags, and generic MM page-table operations.

Risks: 32-bit swap encoding has limited type bits and no inverted PFN protection. Direct stores are safe only under the generic MM locking rules. `native_pudp_*` is structurally present but effectively folded/no-op.

Test signals: non-PAE i386 boot, swap in/out, anon-exclusive swap markers, SMP page-table clear races, mprotect/mmap tests, and bad-entry diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-2level.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-2level_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-2level_types.h

Purpose: defines the fundamental value types and geometry for traditional 32-bit two-level x86 paging.

Important APIs, types, and functions: typedefs `pteval_t`, `pmdval_t`, `pudval_t`, `p4dval_t`, `pgdval_t`, and `pgprotval_t` as `unsigned long`, and defines `pte_t` as a union exposing `pte` and `pte_low`. Geometry constants include `ARCH_PAGE_TABLE_SYNC_MASK`, `PGDIR_SHIFT`, `PTRS_PER_PGD`, `PTRS_PER_PMD`, `PTRS_PER_PTE`, and `PGD_KERNEL_START`.

Control flow: no executable code. Configuration is fixed for non-PAE i386: page directory entries cover 4 MiB (`PGDIR_SHIFT` 22), PMD is folded, and PTE pages contain 1024 entries.

State and persistence: no state is owned.

Dependencies and integration points: used by `pgtable_32_types.h`, `pgtable_types.h`, and generic folded-level page-table code. `PGD_KERNEL_START` derives the kernel/user split from `CONFIG_PAGE_OFFSET`.

Risks: value type widths are part of the page-table ABI for the architecture. Changing geometry breaks low-level MM, swap encoding, boot page tables, and kernel/user split calculations.

Test signals: non-PAE i386 builds, page-table walking, `CONFIG_PAGE_OFFSET` variants, boot-time initial page-table reservation sizing, and generic MM compile-time assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-2level_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-3level.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-3level.h

Purpose: implements PAE i386 page-table entry operations, including ordered 64-bit PTE writes on 32-bit CPUs, atomic exchange helpers, PTI-aware PUD setting, swap-PTE encoding using the full 64-bit PTE, and PROT_NONE PFN inversion.

Important APIs, types, and functions: defines diagnostics for PTE/PMD/PGD, `pxx_xchg64()`, `native_set_pte()`, `native_set_pte_atomic()`, `native_set_pmd()`, `native_set_pud()`, `native_pte_clear()`, `native_pmd_clear()`, `native_pud_clear()`, `pud_clear()`, SMP get-and-clear helpers, `pmdp_establish()`, swap macros (`SWP_TYPE_BITS`, `SWP_OFFSET_FIRST_BIT`, `SWP_OFFSET_SHIFT`, `__swp_type()`, `__swp_offset()`, `__swp_entry()`, `__swp_entry_to_pte()`, `__pte_to_swp_entry()`), `_PAGE_SWP_EXCLUSIVE`, and includes `pgtable-invert.h`.

Control flow: present PTE updates write high half first, issue `smp_wmb()`, then write low half so hardware never sees a bogus present entry. Clearing reverses the order by clearing low/present half first. Atomic operations use `try_cmpxchg64()` loops. `pmdp_establish()` avoids expensive cmpxchg64 when installing non-present PMDs.

State and persistence: mutates page-table memory. PTI helper calls can update paired user page tables through `pti_set_user_pgtbl()`.

Dependencies and integration points: used by `CONFIG_X86_PAE` 32-bit builds, swap, THP-like PMD operations, PTI, and generic MM page-table APIs.

Risks: write ordering is critical because hardware may read split 64-bit entries on 32-bit CPUs. Swap encoding inverts offsets to set high physical bits and reduce L1TF-style speculation exposure. PUD/PGD flushing assumptions are documented and must match callers.

Test signals: PAE i386 SMP boot, swap/migration, mprotect and page-fault races, PTI enabled builds, pmdp establishment tests, bad-entry diagnostics, and TLB flush coverage after top-level changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-3level.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-3level_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-3level_types.h

Purpose: defines PAE i386 page-table value types and geometry for three-level paging.

Important APIs, types, and functions: typedefs page-table value/protection types as `u64`, defines `pte_t` and `pmd_t` unions with low/high 32-bit halves and full 64-bit values, and sets `ARCH_PAGE_TABLE_SYNC_MASK`, `PGDIR_SHIFT`, `PTRS_PER_PGD`, `PMD_SHIFT`, `PTRS_PER_PMD`, `PTRS_PER_PTE`, `MAX_POSSIBLE_PHYSMEM_BITS`, and `PGD_KERNEL_START`.

Control flow: no code executes. The constants describe PAE layout: four top-level PGD entries, PMDs with 512 entries mapping 2 MiB each, and PTE pages with 512 entries.

State and persistence: no state is owned.

Dependencies and integration points: included by `pgtable_32_types.h` under `CONFIG_X86_PAE`, consumed by PAE page-table operations, boot page-table allocation, and generic MM level-folding code.

Risks: split low/high representation underlies ordered update code in `pgtable-3level.h`. Geometry changes would invalidate boot page tables, swap encoding, and the 36-bit possible physical memory assumption.

Test signals: PAE 32-bit builds, highmem boot, page-table walk tests, PMD huge mapping where supported, swap encoding round trips, and compile-time checks for folded levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-3level_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-invert.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-invert.h

Purpose: provides helpers that invert the PFN bits of non-present, non-empty PTEs to mitigate speculative use of physical addresses in PROT_NONE or swap-like entries.

Important APIs, types, and functions: inline helpers are `__pte_needs_invert(u64 val)`, `protnone_mask(u64 val)`, and `flip_protnone_guard(u64 oldval, u64 val, u64 mask)`.

Control flow: `__pte_needs_invert()` returns true for nonzero entries without `_PAGE_PRESENT`; zero clear entries are excluded. `protnone_mask()` returns all ones when inversion is needed. `flip_protnone_guard()` detects transitions into or out of the inversion-needed state and flips PFN bits under the supplied mask while preserving non-PFN flags.

State and persistence: no state is owned. The helpers transform page-table values before storage or interpretation.

Dependencies and integration points: included by PAE and x86-64 page-table headers. It depends on `_PAGE_PRESENT` and caller-supplied PFN masks, and integrates with `pte_pfn()`/entry construction logic that undoes the inversion.

Risks: zero entries must not be inverted. Transition detection must be applied consistently, or PTE PFNs will be double-inverted or left exposed. This is part of the L1TF/speculation mitigation surface.

Test signals: PROT_NONE mappings, swap/migration entries, L1TF mitigation tests, PTE transition tests through mprotect/unmap/fault, and PFN extraction round trips for inverted and normal entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-invert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable.h

Purpose: implements the main x86 page-table API consumed by generic MM: protection transformations, native or paravirt entry setters, entry predicates and flag manipulation, page-table walking helpers, access/dirty/young operations, PTI top-level cloning helpers, swap metadata helpers, protection-key access checks, and safe setter wrappers.

Important APIs, types, and functions: major exports include `pgprot_noncached()`, `pgprot_encrypted/decrypted()`, page-table dump functions, `early_top_pgt`, `__early_make_pgtable()`, `pgd_lock`, `pgd_list`, `pgd_page_get_mm()`, native `set_pte/pmd/pud/p4d/pgd` fallbacks, `pte_*`, `pmd_*`, `pud_*`, `p4d_*`, and `pgd_*` flag/pfn/present/none/bad/same/modify helpers, `lookup_address*()`, `kernel_map/unmap_pages_in_pgd()`, local get-and-clear helpers, access/young/dirty operations such as `ptep_set_access_flags()` and `pmdp_set_access_flags()`, huge get-and-clear, write-protect helpers using cmpxchg, `pmdp_establish()`, `pudp_establish()`, PTI pointer conversion helpers, `clone_pgd_range()`, page-level size helpers, MMU cache no-ops, swap soft-dirty/uffd-wp/exclusive helpers, `pte_flags_pkey()`, `__pte_access_permitted()`, `pfn_modify_allowed()`, zapped-entry checks, SGX memory failure/platform-page hooks, and `set_pte/pmd/pud/p4d/pgd_safe()`.

Control flow: most operations are inline transformations around entry values and page-table memory. Critical updates call page-table check hooks, preserve hardware dirty semantics for shadow stacks, use atomic exchanges where races with hardware or other CPUs matter, and duplicate top-level PTI entries when cloning PGDs.

State and persistence: mutates in-memory page tables, page-table tracking lists, and boot mappings. There is no disk persistence.

Dependencies and integration points: integrates with generic MM, TLB flush code, PTI, PKRU/pkeys, CoCo encryption, KMSAN/debug WX page dumps, paravirt, page-table check, THP, swap, userfaultfd, NUMA balancing, SGX, and L1TF mitigation.

Risks: this is a core MM contract. Flag mistakes can create writable/executable mappings, shadow-stack-invalid PTEs, stale TLBs, incorrect swap metadata, or L1TF exposure. Safe setters must only be used when existing present entries are identical or non-present.

Test signals: x86 MM selftests, fork/exec/mmap/mprotect/munmap, THP split/collapse, swap soft-dirty and uffd-wp tests, PTI enabled/disabled, debug-WX checks, page-table-check, pkeys/PKRU access tests, SGX memory failure, and KVM/Xen paravirt page-table paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_32.h

Purpose: provides the i386 top-level page-table header, selecting PAE or non-PAE operations and declaring initial kernel page tables and boot paging initialization helpers.

Important APIs, types, and functions: declares `swapper_pg_dir[1024]`, `initial_page_table[1024]`, `initial_pg_pmd[]`, `paging_init()`, and `sync_initial_page_table()`. Includes either `pgtable-3level.h` or `pgtable-2level.h`. Defines `kpte_clear_flush()`, `PAGE_TABLE_SIZE(pages)`, and `LOWMEM_PAGES`.

Control flow: compile-time PAE selection pulls in the appropriate implementation. `kpte_clear_flush()` clears a kernel PTE from `init_mm` then flushes the kernel TLB entry. `PAGE_TABLE_SIZE()` computes `.brk` reservation for enough initial page tables to cover lowmem, accounting for separate PMD pages under PAE.

State and persistence: initial page-table arrays are boot/runtime memory. No persistence exists.

Dependencies and integration points: depends on `pgtable_32_types.h`, processor/thread definitions, TLB flush helpers, and boot lowmem layout. It feeds early page-table allocation and lowmem direct-map setup.

Risks: initial table sizing must cover all lowmem or boot mapping will fail. `LOWMEM_PAGES` avoids assembler overflow warnings and must track `__PAGE_OFFSET`. PAE and non-PAE include selection changes many entry semantics.

Test signals: i386 boot with PAE and non-PAE, highmem direct-map sizing, early page-table reservation, kernel PTE clear/flush behavior, and lowmem boundary mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_32_areas.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_32_areas.h

Purpose: defines 32-bit x86 virtual address ranges for vmalloc, kmap/PKMAP, LDT remap, CPU entry area, modules, and maximum low memory.

Important APIs, types, and functions: key macros are `VMALLOC_OFFSET`, `VMALLOC_START`, `LAST_PKMAP`, `CPU_ENTRY_AREA_PAGES`, `CPU_ENTRY_AREA_BASE`, `LDT_BASE_ADDR`, `LDT_END_ADDR`, `PKMAP_BASE`, `VMALLOC_END`, `MODULES_VADDR`, `MODULES_END`, `MODULES_LEN`, and `MAXMEM`. It declares `__vmalloc_start_set`.

Control flow: no functions are implemented. Constants are derived from `high_memory`, fixmap totals, CPU entry area size, PAE/highmem configuration, and vmalloc reserve.

State and persistence: `__vmalloc_start_set` records when `high_memory` is available. The rest are virtual layout calculations.

Dependencies and integration points: depends on `cpu_entry_area.h`, fixmap layout, highmem PKMAP users, vmalloc, module loader, and LDT/PTI remap code.

Risks: ranges are tightly packed near fixmap on 32-bit kernels. Off-by-one or ordering mistakes can overlap vmalloc, PKMAP, LDT, CPU entry area, modules, or reserved holes. `MODULES_LEN` is defined as `MODULES_VADDR - MODULES_END`, which callers must treat carefully because the range endpoints are unusual on 32-bit.

Test signals: boot with highmem and non-highmem, vmalloc stress, module loading, kmap/PKMAP use, CPU entry area mapping for all CPUs, LDT use under PTI, and address-range assertions/debug page-table dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_32_areas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_32_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_32_types.h

Purpose: selects the 32-bit x86 page-table type model and derives common page-directory size/mask constants.

Important APIs, types, and functions: includes `pgtable-3level_types.h` and defines `PMD_SIZE`/`PMD_MASK` when `CONFIG_X86_PAE` is enabled, otherwise includes `pgtable-2level_types.h`. Defines `pgtable_l5_enabled()` as `0`, `PGDIR_SIZE`, and `PGDIR_MASK`.

Control flow: no runtime code. Compile-time PAE selection determines type widths and table geometry.

State and persistence: no state is owned.

Dependencies and integration points: included by `pgtable_types.h` and `pgtable_32.h`; consumed by all 32-bit MM code that needs `PGDIR_*` and folded-level behavior.

Risks: `pgtable_l5_enabled()` must remain false on 32-bit. PAE selection changes not only geometry but atomic update requirements and swap encoding.

Test signals: 32-bit PAE and non-PAE builds, compile-time folding checks, direct-map setup, and page-table walking across PGD boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_32_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_64.h

Purpose: provides x86-64 page-table operations and boot page-table declarations, including 4/5-level folding, PTI-aware top-level entry writes, swap-entry encoding, kernel virtual mapping helpers, and assembler macros for early identity mappings.

Important APIs, types, and functions: declares boot tables such as `level4_kernel_pgt`, `level4_ident_pgt`, `level3_kernel_pgt`, `level2_kernel_pgt`, fixmap tables, and `init_top_pgt`. Defines `swapper_pg_dir`, `paging_init()`, error diagnostics, `mm_p4d_folded()`, `set_pte_vaddr_p4d()`, `set_pte_vaddr_pud()`, native setters/clearers/get-and-clear for PTE/PMD/PUD/P4D/PGD, swap macros `SWP_TYPE_BITS`, `__swp_type()`, `__swp_offset()`, `__swp_entry()`, conversions to PTE/PMD, `cleanup_highmap()`, unmapped-area feature flags, `PAGE_AGP`, kcore address conversions, `vmemmap`, extra mapping init helpers, and `gup_fast_permitted()`. Assembler side defines `l4_index()`, `pud_index()`, page-aligned symbol macro, and `PMDS()`.

Control flow: native setters use `WRITE_ONCE`; top-level P4D/PGD setters account for PTI by updating user shadow page tables when necessary. Swap entries store type in high bits and inverted offset in middle bits. `gup_fast_permitted()` rejects ranges above the virtual mask.

State and persistence: mutates kernel and user page-table memory. Boot tables and highmap cleanup affect runtime address translation.

Dependencies and integration points: depends on `pgtable_64_types.h`, fixmap, PTI, kcore, vmemmap, GUP-fast, boot assembly, and generic MM.

Risks: PTI mirroring and 5-level folding are subtle. Swap encoding must avoid A/D/L/G conflicts and speculative PFN exposure. Boot table symbols must match head_64.S layout.

Test signals: x86-64 boot with LA57/PTI/KASLR, swap and migration entries, GUP-fast boundary tests, kcore reads, highmap cleanup, fixmap setup, page-table dump validation, and early identity mapping assembly checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_64_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_64_types.h

Purpose: defines x86-64 page-table value types, runtime 5-level paging controls, table geometry, and the canonical kernel virtual address layout for direct map, vmalloc, vmemmap, modules, fixmap-adjacent areas, EFI, CPU entry area, and KMSAN metadata.

Important APIs, types, and functions: typedefs PTE/PMD/PUD/P4D/PGD/protection value types as `unsigned long`, defines `pte_t` and `pmd_t`, declares `__pgtable_l5_enabled`, `pgtable_l5_enabled()`, `pgdir_shift`, and `ptrs_per_p4d`. Geometry macros include `PGDIR_SHIFT`, `PTRS_PER_PGD`, `P4D_SHIFT`, `PTRS_PER_P4D`, `PUD_SHIFT`, `PMD_SHIFT`, sizes/masks, and `MAX_POSSIBLE_PHYSMEM_BITS`. Layout macros include `MAXMEM`, guard hole, LDT, VMALLOC/VMEMMAP bases, KMSAN shadow/origin ranges, modules, ESPFIX, CPU entry area, EFI VA range, `EARLY_DYNAMIC_PAGE_TABLES`, `PGD_KERNEL_START`, and `_PAGE_SWP_EXCLUSIVE`.

Control flow: `pgtable_l5_enabled()` either reads early boot state or CPU feature state. Many address macros select L4 versus L5 layout at runtime through base globals.

State and persistence: runtime state is limited to 5-level enable and geometry/base globals initialized during boot/KASLR.

Dependencies and integration points: depends on sparsemem, KASLR, CPU feature detection, KMSAN, PTI/LDT, modules, EFI runtime mapping, and CPU entry area setup.

Risks: layout overlaps are fatal and security-sensitive. KASLR ranges must not collide with fixed regions. KMSAN shrinks usable vmalloc and reserves shadow/origin quarters. `PGDIR_SHIFT` is runtime on x86-64, so code must not assume it is constant.

Test signals: 4-level and 5-level boot, KASLR memory randomization, KMSAN builds, module loading, vmalloc/vmemmap stress, EFI runtime calls, CPU entry area mapping, and address sanitizer/debug page-table layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_64_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_areas.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_areas.h

Purpose: defines architecture-neutral x86 CPU entry area address constants, adding 32-bit-specific area definitions when needed.

Important APIs, types, and functions: includes `pgtable_32_areas.h` for 32-bit builds, then defines `CPU_ENTRY_AREA_RO_IDT`, `CPU_ENTRY_AREA_PER_CPU`, `CPU_ENTRY_AREA_RO_IDT_VADDR`, and `CPU_ENTRY_AREA_MAP_SIZE`.

Control flow: no executable code. `CPU_ENTRY_AREA_MAP_SIZE` is derived differently for 32-bit and 64-bit: precise per-CPU map span on 32-bit and a full `P4D_SIZE` on 64-bit.

State and persistence: no state is owned; these constants describe reserved virtual layout.

Dependencies and integration points: consumed by entry-area setup, IDT mapping, per-CPU entry stacks, fixmap/page-table initialization, and debug page-table validation.

Risks: CPU entry area layout is used by entry/exception code and must remain page-aligned and isolated from adjacent regions. 32-bit and 64-bit map-size assumptions differ significantly.

Test signals: boot on SMP, IDT read-only mapping tests, CPU hotplug entry area setup, page-table dumps of CPU entry area, and exception/interrupt delivery through per-CPU entry structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_areas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_types.h

Purpose: defines the common x86 page-table bit layout, protection constants, cache-mode encodings, page-table entry value wrappers, flag masks, table-level geometry includes, and kernel mapping helper declarations.

Important APIs, types, and functions: constants cover hardware bits (`_PAGE_PRESENT`, `_PAGE_RW`, `_PAGE_USER`, PWT/PCD/A/D/PSE/PAT/GLOBAL/NX), software bits (special, CPA test, UFFD-WP, soft-dirty, kernel-4K, saved-dirty, no-PTI-shadow), pkeys, PROT_NONE, cache modes, encryption/confidential-computing bits, user and kernel `PAGE_*` protections, identity mapping attributes, PFN/flags masks, `PGD_ALLOWED_BITS`, and `enum pg_level`. Types and helpers include `pgprot_t`, `pgd_t`, folded or real `p4d_t/pud_t/pmd_t`, `pte_t`, native make/value helpers, pfn/flag mask helpers, PAT conversion helpers, `pgtable_t`, supported/default PTE masks, `pgprot_writecombine()`, `pgprot_writethrough()`, `phys_mem_access_prot()`, `set_pte_vaddr()`, `native_pagetable_init`, page-count updating, lookup helpers, `slow_virt_to_phys()`, and kernel map/unmap helpers.

Control flow: mostly compile-time flag composition and inline value extraction. Cache-mode conversion maps software cache modes to PTE PAT/PWT/PCD bits. PAE masks top-level PGD values to architecturally allowed bits.

State and persistence: declares global supported/default PTE masks and page-count accounting. Entry values persist only in page tables.

Dependencies and integration points: depends on page masks, memory encryption, CoCo mask helpers, 32/64 page-table type headers, PAT/memtype, procfs page counts, and generic MM.

Risks: bit assignments are central ABI. Conflicts among soft-dirty, UFFD-WP, pkeys, saved dirty, PTI shadow bits, and swap encodings can corrupt memory semantics. Kernel protection constants control W^X, encryption, and cacheability.

Test signals: page protection selftests, PAT/cache-mode tests, pkeys, soft-dirty, uffd-wp, shadow stack write-protect behavior, SME/CoCo encrypted/decrypted mappings, `/proc` page counts, kernel address lookup, and PAE top-level reserved-bit validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pkeys.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pkeys.h

Purpose: implements x86 memory protection key allocation helpers and integration points for `mprotect_pkey()` and execute-only mappings.

Important APIs, types, and functions: defines `arch_max_pkey()`, `arch_set_user_pkey_access()`, `arch_pkeys_enabled()`, `__execute_only_pkey()`, `execute_only_pkey()`, `__arch_override_mprotect_pkey()`, `arch_override_mprotect_pkey()`, `ARCH_VM_PKEY_FLAGS`, `mm_pkey_allocation_map()`, `mm_set_pkey_allocated()`, `mm_set_pkey_free()`, `mm_pkey_is_allocated()`, `mm_pkey_alloc()`, `mm_pkey_free()`, and `vma_pkey()`.

Control flow: pkey support is available only when `X86_FEATURE_OSPKE` is enabled. Allocation checks whether all hardware-supported keys are in use, finds the first zero bit with `ffz()`, and marks it allocated. Freeing rejects unallocated keys and execute-only reserved keys. `execute_only_pkey()` and mprotect override wrappers fall back when OSPKE is absent.

State and persistence: per-mm pkey state lives in `mm->context.pkey_allocation_map` and `execute_only_pkey`. It is process address-space state, not external persistence.

Dependencies and integration points: depends on CPU feature detection, `mm_struct` context, VM flag pkey bits, PKRU setup, mprotect, exec-only mapping logic, and user pkey syscalls.

Risks: only 16 keys are assumed; expanding hardware support requires type/mask audits. The execute-only key is allocated internally but hidden from user allocation. Incorrect allocation can allow wrong PKRU permissions or expose reserved keys.

Test signals: pkey syscall selftests, OSPKE absent fallback, allocation exhaustion, freeing invalid/execute-only keys, mprotect_pkey override behavior, execute-only mappings, fork/exec pkey state, and PKRU access enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pkeys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pkru.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pkru.h

Purpose: provides low-level helpers for reading, writing, and interpreting the x86 PKRU register used by memory protection keys.

Important APIs, types, and functions: defines `PKRU_AD_BIT`, `PKRU_WD_BIT`, `PKRU_BITS_PER_PKEY`, `init_pkru_value`, `pkru_get_init_value()`, `__pkru_allows_read()`, `__pkru_allows_write()`, `read_pkru()`, `write_pkru()`, and `pkru_write_default()`.

Control flow: read/write helpers check `X86_FEATURE_OSPKE` before executing `rdpkru`/`wrpkru`. `write_pkru()` avoids an expensive `wrpkru` if the requested value already matches. Permission helpers shift AD/WD bits by `pkey * 2`; write access requires neither access-disable nor write-disable.

State and persistence: PKRU is per-logical-processor architectural state saved/restored by context-switch/FPU paths. `init_pkru_value` is global runtime policy when pkeys are enabled.

Dependencies and integration points: depends on CPU feature detection, pkey allocation/access checks in `pgtable.h`, task state management, and user PKRU instructions.

Risks: WRPKRU changes userspace access rights and must only be executed when supported. Stale or wrong default PKRU can grant or deny access after exec/fork/signal paths. Permission helpers assume pkey values are already range-validated.

Test signals: pkeys selftests, direct `rdpkru`/`wrpkru` behavior, context-switch PKRU preservation, default PKRU after exec, OSPKE-disabled builds, and page-fault access checks for read/write-disabled pkeys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pkru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/platform_sst_audio.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/platform_sst_audio.h

Purpose: defines Intel SST/Merrifield audio platform data structures and firmware pipeline identifiers used by platform audio drivers.

Important APIs, types, and functions: constants include `MAX_NUM_STREAMS_MRFLD` and `MAX_NUM_STREAMS`. Enums define `sst_audio_task_id_mrfld` and `sst_audio_device_id_mrfld` pipeline IDs for output and input paths. Data structures include `sst_dev_stream_map`, `sst_platform_data`, `sst_info`, `sst_lib_dnld_info`, `sst_res_info`, `sst_ipc_info`, and `sst_platform_info`. It declares `add_sst_platform_device()`.

Control flow: no implementation is present. Platform code passes these tables to SST audio drivers so they can map ALSA/device streams to firmware task IDs, resource windows, IPC mailboxes, DSP memory regions, and library download metadata.

State and persistence: structures describe static or firmware/platform runtime state. No state is allocated here.

Dependencies and integration points: consumed by Intel SST platform, ACPI/platform-device setup, DSP firmware loader, IPC, DMA, and ALSA SoC components.

Risks: pipeline IDs are firmware ABI. Wrong resource offsets, mailbox locations, DMA limits, or suspend behavior flags can break DSP boot, audio routing, or resume. Stream maps must match platform-specific firmware topology.

Test signals: Merrifield/SST device probe, firmware load, playback/capture on each mapped pipeline, suspend/resume with `streams_lost_on_suspend`, IPC mailbox traffic, resource mapping from ACPI indices, and module/library download paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/platform_sst_audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pm-trace.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pm-trace.h

Purpose: implements x86 suspend/resume tracing macros that record source location metadata into a `.tracedata` section and call the PM trace generator when tracing is enabled.

Important APIs, types, and functions: defines `TRACE_RESUME(user)` and aliases `TRACE_SUSPEND(user)` to it. The macro references `pm_trace_enabled` and `generate_pm_trace()`.

Control flow: when `pm_trace_enabled` is true, inline assembly stores a local label address in `tracedata`, emits the source line and file pointer into `.tracedata`, returns to normal text, and calls `generate_pm_trace(tracedata, user)`.

State and persistence: the macro creates static trace metadata in the kernel image and updates PM trace state through `generate_pm_trace()`, which is implemented elsewhere and may encode failure breadcrumbs for reboot diagnosis.

Dependencies and integration points: depends on `asm/asm.h` for pointer-sized move/directives and on generic PM trace infrastructure. Used by suspend/resume code paths.

Risks: inline assembly must produce correctly typed section data for both 32-bit and 64-bit. Trace metadata leaks file/line information intentionally for diagnostics and must only run when enabled. Section format must match PM trace decoding.

Test signals: enable PM trace, suspend/resume failure injection, verify trace data points to the last suspend/resume marker, build both 32/64-bit, and inspect `.tracedata` section formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pm-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/posix_types.h

Purpose: selects the x86 POSIX type definitions appropriate for 32-bit or 64-bit builds.

Important APIs, types, and functions: conditionally includes `asm/posix_types_32.h` when `CONFIG_X86_32` is set, otherwise `asm/posix_types_64.h`.

Control flow: no runtime code; this is a compile-time include selector.

State and persistence: no state is owned.

Dependencies and integration points: used by UAPI/internal headers needing architecture-specific POSIX scalar type definitions, especially syscall ABI and filesystem interfaces.

Risks: selecting the wrong type header would break ABI sizes and layouts for system calls, stat structures, user/kernel data exchange, and compat behavior.

Test signals: 32-bit and 64-bit builds, syscall ABI tests, userspace header export checks, and compat structure layout validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/posted_intr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/posted_intr.h

Purpose: defines Intel posted-interrupt descriptor layout and helpers for manipulating posted interrupt request/control bits, including posted MSI support.

Important APIs, types, and functions: constants include `POSTED_INTR_ON`, `POSTED_INTR_SN`, `PID_TABLE_ENTRY_VALID`, `NR_PIR_VECTORS`, and `NR_PIR_WORDS`. `struct pi_desc` is a 64-byte aligned descriptor containing PIR bitmap and control fields `notifications`, `nv`, and `ndst`. Helpers include `pi_harvest_pir()`, atomic `pi_test_and_set_on()`, `pi_test_and_clear_on()`, `pi_test_and_clear_sn()`, `pi_test_and_set_pir()`, `pi_is_pir_empty()`, setters/clearers/testers for ON/SN/PIR bits, non-atomic `__pi_set_sn()`/`__pi_clear_sn()`, optional `pi_pending_this_cpu()`, and `intel_posted_msi_init()`.

Control flow: software harvest first reads all PIR words into a caller buffer and ORs them to avoid expensive cacheline bouncing; only nonzero words are then cleared with `arch_xchg()`. Control helpers manipulate bits in the descriptor control word. Posted MSI code checks the per-CPU posted MSI descriptor for pending external vectors.

State and persistence: `pi_desc` instances are runtime shared state between CPU, IOMMU, and virtualization code. No persistent storage exists.

Dependencies and integration points: depends on x86 interrupt vectors, bitmap helpers, atomic bitops, per-CPU `posted_msi_pi_desc`, IOMMU interrupt remapping, posted MSI, and KVM posted interrupts.

Risks: descriptor cacheline layout and harvesting order are performance-critical and concurrency-sensitive. CPU and IOMMU concurrently access the same cacheline. Vector validation in `pi_pending_this_cpu()` prevents invalid PIR reads.

Test signals: KVM posted-interrupt delivery, posted MSI interrupt remapping, PIR harvest with multiple vectors, suppress-notification behavior, IOMMU stress, CPU hotplug/per-CPU descriptor setup, and cacheline-aligned structure layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/posted_intr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/preempt.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/preempt.h

Purpose: implements x86 per-CPU preemption count handling, folding an inverted need-resched bit into `__preempt_count` so `preempt_enable()` can decrement and test for rescheduling efficiently.

Important APIs, types, and functions: declares per-CPU `__preempt_count`, defines `PREEMPT_NEED_RESCHED` and `PREEMPT_ENABLED`, and provides `preempt_count()`, `preempt_count_set()`, `init_task_preempt_count()`, `init_idle_preempt_count()`, `set_preempt_need_resched()`, `clear_preempt_need_resched()`, `test_preempt_need_resched()`, `__preempt_count_add()`, `__preempt_count_sub()`, `__preempt_count_dec_and_test()`, and `should_resched()`. Under preemption it declares schedule thunks and dynamic/static-call wrappers for `__preempt_schedule()` and `__preempt_schedule_notrace()`.

Control flow: preempt count reads mask off the inverted need-resched bit. Setting need-resched clears the MSB; clearing need-resched sets it. `__preempt_count_dec_and_test()` uses an x86 decrement-and-condition-code helper to detect zero. Dynamic preemption can call schedule thunks through static-call trampolines.

State and persistence: `__preempt_count` is per-CPU scheduler state. No external persistence exists.

Dependencies and integration points: depends on x86 per-CPU ops, RMW condition-code helpers, scheduler/preemption code, static calls, and dynamic preemption.

Risks: the inverted bit convention is subtle; treating raw `__preempt_count` as a plain count gives wrong results. Atomic cmpxchg in `preempt_count_set()` preserves need-resched across count writes. Schedule thunk calls must satisfy calling constraints.

Test signals: preemption selftests, voluntary/full/dynamic preemption modes, scheduler stress, interrupt/softirq nesting, idle task initialization, objtool validation, and tracing/notrace preemption paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/preempt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/probe_roms.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/probe_roms.h

Purpose: declares x86 PCI BIOS ROM mapping helpers used by ROM probing code.

Important APIs, types, and functions: forward declares `struct pci_dev` and exports `pci_map_biosrom(struct pci_dev *pdev)`, `pci_unmap_biosrom(void __iomem *rom)`, and `pci_biosrom_size(struct pci_dev *pdev)`.

Control flow: no implementation is present. Callers map a device BIOS ROM, inspect or copy it, query its size, and then unmap it.

State and persistence: mappings are temporary kernel I/O mappings of device ROM address space. The header owns no state.

Dependencies and integration points: used by x86 ROM probing and PCI device firmware/option-ROM paths. It depends on PCI device metadata and ioremap/unmap implementation elsewhere.

Risks: ROM windows can be disabled, shared, or require decode enabling. Incorrect mapping size or missing unmap can leak mappings or access invalid firmware memory.

Test signals: option ROM reads on PCI devices, size detection, map/unmap leak checks, disabled ROM BAR handling, and systems with legacy BIOS extension ROMs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/probe_roms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/processor-cyrix.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/processor-cyrix.h

Purpose: provides ordered inline accessors for NSC/Cyrix CPU indexed configuration registers using the legacy PC configuration port pair.

Important APIs, types, and functions: includes `pc-conf-reg.h` and defines `getCx86(u8 reg)` and `setCx86(u8 reg, u8 data)` as wrappers around `pc_conf_get()` and `pc_conf_set()`.

Control flow: `getCx86()` writes the index and reads data through `pc_conf_get()`. `setCx86()` writes the index and value through `pc_conf_set()`. The functions are inline rather than macros to preserve access ordering.

State and persistence: reads and writes CPU/chipset indexed registers. State persists in hardware until reset or later modification.

Dependencies and integration points: used by old Cyrix/NSC CPU identification and setup code, relying on `pc_conf_lock` discipline from callers where concurrent access matters.

Risks: ordering through ports `0x22/0x23` is mandatory. Wrong registers can change CPU/chipset behavior on legacy hardware.

Test signals: legacy Cyrix CPU detection/setup builds, ordered I/O tracing, register readback after writes, and regression tests for callers that serialize indexed access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/processor-cyrix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/processor-flags.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/processor-flags.h

Purpose: extends UAPI x86 processor flag definitions with kernel-only masks for VM86 support and CR3 address/PCID/no-flush handling.

Important APIs, types, and functions: includes `uapi/asm/processor-flags.h` and `mem_encrypt.h`, defines `X86_VM_MASK` based on `CONFIG_VM86`, and defines `CR3_ADDR_MASK`, `CR3_PCID_MASK`, and `CR3_NOFLUSH` differently for 64-bit and 32-bit builds. Under PTI it defines `X86_CR3_PTI_PCID_USER_BIT`.

Control flow: no executable code. Macros are used by CR3 read/write and TLB context switching paths.

State and persistence: no state is owned. The masks interpret or construct CR3 register values.

Dependencies and integration points: depends on SME encryption bit clearing through `__sme_clr()`, physical page masks, PCID support, LAM/CR3 layout comments, VM86, and PTI address-space ID selection.

Risks: CR3 contains physical address bits, PCID, optional no-flush bit, SME encryption bit, and LAM mode bits. Incorrect masking can flush unexpectedly, fail to flush when required, switch to the wrong page table, or include encryption/metadata bits in a physical address.

Test signals: TLB context switch tests with PCID on/off, PTI user/kernel PCIDs, SME/SEV boot, VM86 builds, CR3 physical address readback, and no-flush behavior during address-space switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/processor-flags.h -->
