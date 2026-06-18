# subset-b-000777 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci-common.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci-common.c

Purpose: this is the shared PowerPC PCI host bridge and bus-management implementation used by both 32-bit and 64-bit platform code. It owns PHB allocation, domain numbering, Open Firmware range parsing, resource fixups and claiming, IRQ discovery, early config-space access, and the top-level `pcibios_scan_phb()` path that turns a `struct pci_controller` into a Linux `struct pci_bus`.

Important APIs and types: global `hose_list`, `phb_bitmap`, `isa_mem_base`, and `pci_dma_ops` hold cross-PHB state. Exported entry points include `set_pci_dma_ops()`, `pcibios_alloc_controller()`, `pcibios_free_controller()`, `pcibios_free_controller_deferred()`, `pci_address_to_pio()`, `pci_domain_nr()`, `pci_find_hose_for_OF_device()`, `pci_find_controller_for_domain()`, legacy read/write/mmap helpers, `pci_process_bridge_OF_ranges()`, `pcibios_fixup_bus()`, `pcibios_align_resource()`, `pcibios_resource_survey()`, hotplug helpers `pcibios_claim_one_bus()` and `pcibios_finish_adding_to_bus()`, device enable/disable hooks, early config accessors, `pcibios_get_phb_of_node()`, and `pcibios_scan_phb()`. The file also defines the `pci_intx_virq` refcount list used to release INTx irq mappings when PCI devices are removed.

Control flow: PHBs are discovered through the machine descriptor at `core_initcall(discover_phbs)`. Platform code allocates controllers, parses DT bridge ranges into IO and memory resources, then architecture-specific `pcibios_init()` code scans each PHB through `pcibios_scan_phb()`. Scanning maps IO space, builds root-bus resources, creates a root bus, chooses DT or normal probing through `controller_ops.probe_mode`, runs platform fixups, and configures PCIe settings. Later `pcibios_resource_survey()` claims bridge and device resources, reserves legacy IO/VGA apertures, and assigns unassigned resources unless `PCI_PROBE_ONLY` is set.

State and persistence: PHB domain ids persist in `phb_bitmap` until controller free. `hose_list` is protected by `hose_spinlock`, while INTx mapping lifetime is protected by `intx_mutex` and `kref`. Resources are persisted in `struct pci_controller` fields: IO base physical/virtual address, `pci_io_size`, three memory windows plus offsets, ISA legacy ranges, bus number resource, and platform callback table. Device state is updated through DMA ops, NUMA node, MSI domain, interrupt number, resource flags, and PCI command registers.

Dependencies and integration points: this file depends on OF PCI parsing, generic PCI core scanning/resource APIs, irq domains, EEH headers, vgaarb-visible resource conventions, `ppc_md` machine callbacks, and per-PHB `controller_ops`. It is called by `pci_32.c`, `pci_64.c`, hotplug, OF scanning, and platform PHB discovery.

Risks: host bridge numbering can collide if firmware properties are duplicated, and the fallback bitmap path panics if all ids are exhausted. OF range parsing supports only one IO range and three memory ranges, so unusual firmware maps may be skipped. Resource fixups intentionally clear or shrink firmware resources and can cause reassignment surprises. Legacy mmap emulates missing VGA memory for user space compatibility. IRQ fallback uses legacy config-space line values when DT mapping fails, which is platform-sensitive. Hotplug resource claiming is separate from boot allocation and can diverge.

Test signals: boot logs should show PHB range parsing, root bus creation, resource survey, and no unexpected "Cannot allocate resource" warnings. PCI enumeration, `/proc/bus/pci` legacy access, MSI domain inheritance, INTx removal, SR-IOV enable/disable hooks, and hotplug add/remove paths are the main runtime signals. Useful tests include DT-probed and config-probed systems, multiple PHBs with stable domain numbers, legacy IO mmap, resource reassignment modes, and device removal confirming irq mappings are disposed once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci-hotplug.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci-hotplug.c

Purpose: this file provides PowerPC-specific PCI hotplug helpers for finding buses by device-tree node, releasing `pci_dn` firmware data when a PCI device goes away, recursively removing devices below a bus, and adding newly visible devices to an existing bus.

Important APIs and functions: `pci_find_bus_by_node()` walks the PHB root bus children to find the `struct pci_bus` matching a DT node. `pcibios_release_device()` invokes optional PHB release callbacks and frees a deferred dead `pci_dn`. `pci_hp_remove_devices()` recursively descends child buses and calls `pci_stop_and_remove_bus_device()` in reverse device order. `pci_hp_add_devices()` chooses OF-rescan or normal probing based on `controller_ops.probe_mode`, scans slots and bridges, then calls `pcibios_finish_adding_to_bus()`. The helper `traverse_siblings_and_scan_slot()` maps DT children to slots for partial hotplug rescans.

Control flow: a hotplug add operation starts with a bus whose DT node still exists. In `PCI_PROBE_DEVTREE` mode the bus is rescanned by `of_rescan_bus()`. In normal mode, the code scans endpoint or bridge slots described by DT children, then performs two bridge scans: one for already configured bridges and one allowing reconfiguration. It finishes through common PCI code to claim or assign resources and register devices. Removal is bottom-up: child buses are processed first, then devices on the current bus are stopped and removed.

State and persistence: hotplug state is mostly held elsewhere, in `struct pci_bus`, `struct pci_dev`, DT nodes, PHB `controller_ops`, EEH state, and `pci_dn` objects. This file is responsible for final deferred freeing of `PCI_DN_FLAG_DEAD` objects during device release, which ties dynamic DT node removal to PCI core object lifetime.

Dependencies and integration points: it integrates with `pci_dn.c` for `PCI_DN()`/`pci_get_pdn()`, `pci_of_scan.c` for OF rescans, `pci-common.c` for final resource registration, generic PCI bridge/slot scanning, EEH, and platform-specific release hooks.

Risks: partial hotplug relies on DT child class codes and `PCI_DN(devfn)` data being accurate. The sibling scan has a subtle dependency on `start->child` while iterating children, so malformed or stale nodes can lead to skipped or repeated scans. Resource assignment is delegated after probing, so failures show up later. Removing devices while firmware data is still referenced requires the deferred `pci_dn` lifetime to be correct.

Test signals: hot-add should create only missing devices and then expose them in sysfs/proc. Hot-remove should remove child buses before parents and free dead `pci_dn` objects without use-after-free reports. Run with OF probe mode and normal probe mode, partial bridge removal, EEH-enabled kernels, and platform `release_device` callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci-hotplug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_32.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_32.c

Purpose: this is the 32-bit PowerPC PCI initialization and compatibility layer. It supplies 32-bit globals, Open Firmware bus-number mapping for platforms that renumber PCI buses, 32-bit PHB IO resource adjustment, the 32-bit PCI initialization pass, and the `pciconfig_iobase` syscall implementation.

Important APIs and state: exported globals are `isa_io_base`, `pci_dram_offset`, and `isa_bridge_pcidev`. `pcibios_assign_bus_offset` controls spacing after scanned hose bus ranges. `pci_assign_all_buses` tracks reassignment mode. Under `CONFIG_PPC_PCI_OF_BUS_MAP`, `pci_to_OF_bus_map` and `pci_bus_count` maintain a kernel-to-firmware bus map. `pci_device_from_OF_node()` translates OF nodes to bus/devfn, optionally remapping through that table. `pci_create_OF_bus_map()` creates the root DT property used by `/proc` device tree consumers. `pcibios_setup_phb_io_space()` adjusts resource windows by the virtual IO offset. `pcibios_init()` scans all registered hoses and invokes common resource survey and machine fixups.

Control flow: after PHBs are discovered into `hose_list`, `subsys_initcall(pcibios_init)` probes all controllers. It may force bus reassignment based on PCI flags, sets first and last bus numbers, calls `pcibios_scan_phb()`, adds devices, updates the next bus number, optionally builds OF bus maps for PMAC/CHRP, runs `pcibios_resource_survey()`, and then calls machine `pcibios_fixup` and `pcibios_after_init`. The syscall finds a hose for a bus and returns bridge number, memory offset, IO base, ISA IO base, or ISA memory base.

Dependencies and integration points: this file relies on `hose_list` and common scan/resource logic from `pci-common.c`, platform callbacks from `ppc_md`, Open Firmware node properties, generic PCI device lookup, memblock allocation for early properties, and compatibility with old users of `pciconfig_iobase`.

Risks: bus-map support assumes OF bridge nodes have usable `bus-range`, `class-code`, and `reg` properties. If buses are reassigned, OF-to-kernel translation can be ambiguous when several kernel buses match one OF bus. The syscall is legacy and domain-limited. The 32-bit IO resource adjustment mutates `hose->io_resource` in place and depends on common code having a valid virtual mapping.

Test signals: 32-bit PMAC/CHRP/PReP boots should show PCI probing, stable device discovery, and correct OF bus maps when bus reassignment is active. Regression checks include `pci_device_from_OF_node()` users, `pciconfig_iobase` return values for old X/server tooling, resource survey warnings, and machine fixup ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_64.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_64.c

Purpose: this file supplies 64-bit PowerPC PCI initialization, PHB IO-space mapping/unmapping, the 64-bit `pciconfig_iobase` syscall compatibility path, NUMA lookup for PCI buses, and PMAC OF-node device translation.

Important APIs and functions: `pci_io_base` is exported as the base for IO BAR offsets. `pcibios_init()` is a synchronous subsys initcall that sets `ppc_md.phys_mem_access_prot`, enables PCI domains, scans each PHB, runs common resource survey, adds devices, and runs machine fixups. `pcibios_unmap_io_space()` handles PHB and bridge hot-unmap cases. `ioremap_phb()` allocates virtual space between `PHB_IO_BASE` and `PHB_IO_END` and maps physical IO pages. `pcibios_map_io_space()` and `pcibios_setup_phb_io_space()` map PHB IO resources. `pcibus_to_node()` returns PHB NUMA node when enabled. `pci_device_from_OF_node()` reads `PCI_DN` bus/devfn for PMAC.

Control flow: the 64-bit path scans PHBs before adding devices, unlike the 32-bit path that adds devices per hose before the resource survey. IO mapping aligns the physical base and size to pages, records `io_base_alloc`, computes `io_base_virt`, and adjusts `io_resource` by `pcibios_io_space_offset()`. Unmapping a bridge flushes hash-table entries for the bridge IO range on Book3S; unmapping a PHB iounmaps the stored allocation.

State and persistence: PHB IO mapping state lives in `io_base_phys`, `pci_io_size`, `io_base_alloc`, `io_base_virt`, and adjusted `io_resource`. Domain/proc visibility is controlled with PCI flags. The syscall uses `pci_root_buses` and DT-backed `PCI_DN(hose_node)->phb` to recover the controller.

Dependencies and integration points: depends on VM area allocation, page-range ioremap, hash MMU flushing, OF compatibility checks for MacRISC4 AGP routing, generic PCI root bus lists, `pci-common.c` scanning/resource code, and platform callbacks.

Risks: IO mapping requires page-aligned inputs and enough virtual address space in the PHB IO region. Hot-unmap for bridges only flushes hash entries and assumes page tables remain valid, which is architecture-specific. `pciconfig_iobase` is not domain-correct and returns the first matching root bus. The MacRISC4 AGP special case is intentionally compatibility-driven and fragile.

Test signals: 64-bit boot should show PCI probing done, devices added after resource survey, and valid `/proc` domain behavior. Hotplug tests should exercise PHB unmap and bridge hash flush. NUMA tests should confirm PCI devices inherit the PHB node. Legacy users of `pciconfig_iobase` should receive stable IO and memory bases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_dn.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_dn.c

Purpose: this file maintains PowerPC PCI firmware metadata (`struct pci_dn`) attached to Open Firmware device nodes and bridges it to Linux `pci_dev` objects. It also creates synthetic `pci_dn` and EEH metadata for SR-IOV virtual functions that do not have DT nodes.

Important APIs and functions: lookup helpers are `pci_get_pdn_by_devfn()` and `pci_get_pdn()`, backed by `pci_bus_to_pdn()`. SR-IOV support is provided by `add_sriov_vf_pdns()` and `remove_sriov_vf_pdns()`. `pci_add_device_node_info()` allocates and fills `pci_dn` fields from DT properties, initializes EEH state, and attaches the node to its parent child list. `pci_remove_device_node_info()` marks or frees `pci_dn` objects during dynamic node removal. `pci_traverse_device_nodes()` walks PCI-looking DT nodes depth first. `pci_devs_phb_init_dynamic()` initializes a PHB node and all child metadata. An early PCI fixup stores the resolved `pci_dn` in `pdev->dev.archdata.pci_data`.

Control flow: PHB initialization creates a root `pci_dn` with invalid bus/devfn, then traverses child nodes and allocates metadata for each device. PCI device creation or early fixup resolves fast-path archdata. Lookups first check live `pci_dev` archdata, then the device node, then the firmware child list. Dynamic removal detaches from parent lists, handles parent node references, and defers freeing if a matching `pci_dev` still exists. SR-IOV creation iterates total VFs and creates child-list entries with bus/devfn from PCI IOV helpers.

State and persistence: `dn->data` owns the pointer to `pci_dn`; parent/child lists model the PCI firmware hierarchy. Fields cache PHB pointer, bus number, devfn, vendor/device/class, extended config-space flag, PE number, flags, and optional EEH device. `PCI_DN_FLAG_DEAD` persists until `pcibios_release_device()` frees a metadata object after the PCI device release path is safe.

Dependencies and integration points: integrates with Open Firmware properties, EEH (`eeh_dev`, PE tree removal), PCI IOV helpers, `pci-hotplug.c` deferred release, `pci_of_scan.c` device creation, and PHB setup.

Risks: metadata lifetime is split between DT nodes and PCI devices, so removal order is critical. SR-IOV VF metadata is synthetic and must be kept consistent with PF total VFs and activated VF state. EEH cleanup must remove PE tree entries only when configured. Traversal uses class-code heuristics and can skip malformed firmware nodes.

Test signals: check that every scanned PCI device has `dev.archdata.pci_data`, dynamic PHB add/remove leaves no stale child-list entries, SR-IOV enable/disable creates and frees VF `pci_dn` plus EEH objects, and hotplug removal logs deferred dead pdn freeing without leaks or crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_dn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_of_scan.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_of_scan.c

Purpose: this file builds Linux PCI devices and buses from Open Firmware PCI device-tree nodes. It decodes PCI address cells, creates `pci_dev` objects without config-space enumeration, parses BAR and bridge resources from DT properties, and recursively scans child buses.

Important APIs and functions: `pci_parse_of_flags()` converts OF PCI `phys.hi` address bits into Linux resource and PCI BAR flags. `of_create_pci_dev()` allocates a `pci_dev`, populates IDs, class, revision, config size, OF node, MSI mask, header type, ROM register, and resources, then calls `pci_device_add()`. `of_scan_pci_bridge()` creates or finds child buses and parses bridge `bus-range` and `ranges`. Public scan functions are `of_scan_bus()` and `of_rescan_bus()`.

Control flow: `of_scan_bus()` scans each direct DT child through `of_scan_pci_dev()`. A child must be available and have a valid `reg` property. Existing devices are reused by slot lookup, and EEH-removed nodes are skipped. New devices run early PCI fixups before address parsing. After direct children are created, new bus setup runs `pcibios_setup_bus_self()`, then all PCI bridges are recursively scanned. Rescans skip the bus-self setup for already configured buses.

State and persistence: parsed resources are written into `dev->resource[]` and `bus->resource[]` with bus-to-CPU address translation through `pcibios_bus_to_resource()`. Devices retain OF node references. Bridge bus-number resources are inserted using firmware `bus-range`. Device power and error state start at unknown/normal, and default DMA mask is 32-bit while MSI address mask starts at 64-bit.

Dependencies and integration points: this code is called by `pcibios_scan_phb()` and hotplug rescans. It depends on `pci_dn.c` for DT node PCI metadata, `pci-common.c` for bus setup/resource translation, generic PCI device allocation and bridge scanning, EEH removal markers, and OF property formats.

Risks: the code trusts firmware properties for IDs, class, ranges, and bus numbers. Missing `bus-range` or `ranges` prevents bridge scanning. It supports one IO bridge range and a finite number of memory ranges. `reg` fallback in `of_pci_parse_addrs()` marks resources unset, so later resource assignment behavior is important. Multifunction detection is conservative and may be inaccurate.

Test signals: DT-only probe mode should enumerate all available firmware nodes with correct BARs and bridge windows. Hot-rescan should reuse existing slots and create only new devices. Test unavailable nodes, EEH removed nodes, bridges with multiple memory ranges, ROM resources, and config-space access after `pci_device_add()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_of_scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/pmc.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/kernel/pmc.c

Purpose: this file arbitrates ownership of PowerPC performance monitor counter interrupt handling and supplies low-level enable/disable helpers for PMC hardware. It is a small shared layer used by perf/perfmon-style users that need exclusive access to PMU interrupt delivery.

Important APIs and state: `perf_irq` is the active PMU interrupt handler and defaults to `dummy_perf()`. `reserve_pmc_hardware()` installs a caller-provided handler if no owner is active, records `pmc_owner_caller`, and returns `-EBUSY` on contention. `release_pmc_hardware()` clears ownership and restores the dummy handler. On Book3S 64-bit, `power4_enable_pmcs()` performs the POWER4 HID0 sequence required to enable counters.

Control flow: callers reserve the hardware before programming counters. If no handler is supplied, the dummy handler remains active. Interrupts arriving while dummy is installed clear/disable the PMU interrupt-enable condition using the CPU-family-specific register path: FSL embedded PMR, IBM MMCR0 with PMAO handling, or generic MMCR0 PMXE clearing. Release resets ownership under the same raw spinlock.

State and persistence: ownership is process-independent kernel state protected by `pmc_owner_lock`. The only persistent state in this file is the active handler pointer and debugging caller address. Hardware state changes are immediate SPR/PMR writes and are not persisted beyond CPU PMU registers.

Dependencies and integration points: depends on `cur_cpu_spec->pmc_type`, PMU SPR/PMR definitions, low-level interrupt paths that call `perf_irq`, and external PMU/perf code that reserves and releases the hardware.

Risks: incorrect reserve/release pairing leaves PMU hardware unavailable. `release_pmc_hardware()` warns but still clears even if there is no owner. The dummy handler must correctly disable interrupts for all configured CPU families; otherwise stray PMU interrupts can loop. The owner address is only diagnostic and not a full owner identity.

Test signals: concurrent reserve attempts should return `-EBUSY` for the second caller. Releasing should restore dummy handling. PMU overflow interrupts with no owner should be disabled without interrupt storms. POWER4 systems need validation of the exact HID0 enable sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/pmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ppc_save_regs.S -->
## sources/distributed-fs/ceph-client/arch/powerpc/kernel/ppc_save_regs.S

Purpose: this assembly helper snapshots the current PowerPC register state into a `pt_regs`-shaped buffer for diagnostic or low-level callers. It is explicitly approximate because the caller's prologue has already modified some state before this function can save it.

Important API: `_GLOBAL(ppc_save_regs)` expects `r3` to point past the interrupt-frame register area, then subtracts `STACK_INT_FRAME_REGS` so standard `pt_regs` offsets can be used. It stores general-purpose registers, stack pointer, caller link register, current NIP, MSR, CTR, XER, CCR, and clears trap/original GPR3 fields. On 64-bit it also stores PACA soft interrupt mask in `SOFTE`; on 32-bit it uses `stmw` for GPR2 and above.

Control flow: the function adjusts the destination pointer, saves volatile and nonvolatile GPRs using ABI-specific macros, records `r1` as the current stack pointer, walks the caller stack frame to recover the caller's saved LR, records its own LR as NIP, reads machine state registers, writes zero for synthetic fields, and returns with `blr`.

State and persistence: it does not modify global state. The persistent effect is the filled caller-provided buffer. It reads architectural registers and, on 64-bit, the PACA soft-mask byte through `r13`.

Dependencies and integration points: depends on PowerPC stack-frame layout, `asm-offsets.h` `pt_regs` offsets, `ppc_asm.h` save macros, `asm-compat.h` load/store width macros, and ABI differences between PPC32 and PPC64. Consumers must provide a buffer large enough for the adjusted frame layout.

Risks: saved state can be misleading because the caller already executed a prologue. Recovering caller LR from stack-frame save area depends on a conventional frame. The function assumes `r3` points to a buffer with enough room before the original address. Architecture offset changes would corrupt the output if not rebuilt consistently.

Test signals: callers should see plausible GPR/MSR/CTR/XER/CCR/NIP/LR values in the resulting `pt_regs`. Build tests across PPC32 and PPC64 are important because register save sequences differ. Runtime tests should verify no buffer underrun and sane stack traces from saved regs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ppc_save_regs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/proc_powerpc.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/kernel/proc_powerpc.c

Purpose: this file creates PowerPC-specific `/proc` entries, especially the PPC64 `systemcfg` page and compatibility directory/symlink layout under `/proc/powerpc`, `/proc/ppc64`, and `/proc/rtas`.

Important APIs and state: under `CONFIG_PPC64_PROC_SYSTEMCFG`, `systemcfg_data_store` is a page-aligned union that backs exported `struct systemcfg *systemcfg`. `page_map_proc_ops` implements fixed-size seek, read, and mmap of exactly one page. `proc_ppc64_init()` fills `systemcfg` fields from PVR, firmware LPAR feature, memblock physical size, and cache descriptors, then creates `powerpc/systemcfg`. `proc_ppc64_create()` creates the `powerpc` root directory, the `ppc64` symlink on 64-bit, and RTAS directory/symlink when `/rtas` exists in the DT.

Control flow: `proc_ppc64_create()` is a `core_initcall`, so it runs early enough for later drivers to assume `/proc/powerpc` and optional RTAS paths exist. `proc_ppc64_init()` runs as an `__initcall` when configured and publishes the one-page systemcfg file after initializing content.

State and persistence: the systemcfg page persists for the lifetime of the kernel and may be read or mapped by user space. Proc dentries persist after init. The page contains static boot-time hardware and platform details rather than live counters.

Dependencies and integration points: depends on procfs, memblock, DT lookup for `/rtas`, firmware feature flags, RTAS headers, VDSO/systemcfg ABI definitions, and global cache descriptors. User-space compatibility is a key integration point because old PPC64 software may mmap `/proc/ppc64/systemcfg` through symlinked paths.

Risks: `page_map_mmap()` remaps a kernel physical page read-only by proc permissions but uses the VMA page protections supplied by the caller, so permission expectations rely on procfs open mode and mmap checks. The systemcfg ABI is fixed-size and compatibility-sensitive. Creation failures return nonzero but have limited recovery.

Test signals: boot should expose `/proc/powerpc`, `/proc/ppc64` on 64-bit, optional `/proc/powerpc/rtas`, optional `/proc/rtas`, and `powerpc/systemcfg` when configured. Read, seek, and one-page mmap should succeed; oversized mmap should return `-EINVAL`. Validate fields such as eye catcher, PVR, memory size, cache line sizes, and LPAR bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/proc_powerpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/process.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/kernel/process.c

Purpose: this is the central PowerPC process, thread, context-switch, user-entry, facility-state, breakpoint, stack, and diagnostic implementation. It handles lazy save/restore of FP, Altivec, VSX, SPE, transactional memory, special-purpose registers, debug/watchpoint registers, fork/exec register setup, thread personality controls, stack unwinding, and runlatch control.

Important APIs and functions: exported facility helpers include `msr_check_and_set()`, `__msr_check_and_clear()`, `giveup_fpu()`, `flush_fp_to_thread()`, `enable_kernel_fp()`, Altivec/VSX/SPE equivalents, `giveup_all()`, `flush_all_to_thread()`, `restore_math()`, `tm_reclaim_current()`, breakpoint helpers, `kvmppc_save_user_regs()`, `kvmppc_save_current_sprs()`, `__switch_to()`, `show_regs()`, `flush_thread()`, `arch_setup_new_exec()`, `set_thread_tidr()`, `arch_dup_task_struct()`, `copy_thread()`, `start_thread()`, `set/get_fpexc_mode()`, `set/get_endian()`, `set/get_unalign_ctl()`, `validate_sp*()`, `__get_wchan()`, `show_stack()`, runlatch helpers, and `arch_align_stack()`.

Control flow: context switching saves SPRs, gives up active math facilities, handles transactional-memory reclaim/recheckpoint, restores new-thread SPRs, marks return regs changed, and calls low-level `_switch()`. New tasks are created by `copy_thread()` with a synthetic switch frame returning through fork or kernel-thread stubs. Exec uses `start_thread()` to clear user registers, set ABI-specific entry/TOC/MSR state, and reset per-thread facility state. Lazy math restore occurs on exception exit through `restore_math()` when load flags require reloading but user MSR lacks live facility bits.

State and persistence: most state lives in `thread_struct`: saved FP/VR/SPE/TM states, SPR snapshots, debug registers, TIDR, DEXCR/HASHKEYR, DSCR, kernel stack pointer, user regs pointer, and lazy-load counters. Global `strict_msr_control` is set by early param. Per-CPU `current_brk[]` tracks installed hardware breakpoints. Stack validation reads task stacks, IRQ stacks, and emergency stacks without taking ownership beyond `try_get_task_stack()`.

Dependencies and integration points: this code is tightly coupled to scheduler switching, ptrace/hw-breakpoint, KVM HV, signal/TM code, ELF ABI setup, MMU/hash/radix support, livepatch, KUAP, firmware CPU features, pkeys, ftrace stack graph handling, and interrupt return paths.

Risks: facility state transitions are highly ordering-sensitive, especially with transactional memory and lazy FP/VMX/VSX. Preemption must be disabled while saving live registers. Incorrect MSR updates can leak user register state or corrupt checkpointed TM state. Breakpoint code varies across DAWR, DABR, BookE, and 8xx. Stack walking must avoid invalid stacks and nofault failures. New code after `_switch()` will not run for freshly created tasks.

Test signals: kernel selftests for ptrace, hw breakpoints, TM, FP/vector/VSX, endian prctl, unaligned-control prctl, fork/clone/exec, KVM register save, and stack unwinding are key. Runtime signals include no WARNs in lazy facility paths, correct user ABI register setup for ELFv1/ELFv2/compat tasks, stable `wchan`, valid crash register dumps, and runlatch state on PPC64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom.c

Purpose: this file performs early PowerPC flattened device-tree parsing and boot-time platform discovery. It establishes memory limits and memblock state, reserves kernel/initrd/crash/fadump/DT memory, scans CPU features and boot CPU identity, initializes early MMU and firmware feature state, handles transactional-memory boot policy, and exports chip-id lookup helpers.

Important APIs and state: early parameters include `mem=` and `ppc_tm=`. Global state includes `chip_id_lookup_table`, `iommu_is_off`, `iommu_force_on`, TCE allocation bounds, `ppc64_rma_size`, `boot_cpu_node_count`, `first_memblock_size`, and `boot_cpu_count`. Major functions are `move_device_tree()`, CPU feature scanners for `ibm,pa-features` and `ibm,pi-features`, `early_init_dt_scan_cpus()`, `early_init_dt_scan_chosen_ppc()`, memory validators and dynamic-memory scanning, `early_init_dt_add_memory_arch()`, reservation helpers, `tm_init()`, `early_init_devtree()`, relocatable `early_get_first_memblock_info()`, `of_get_ibm_chip_id()`, `cpu_to_chip_id()`, and `arch_match_cpu_phys_id()`.

Control flow: `early_init_devtree()` verifies the FDT, scans model and firmware debug nodes, parses `/chosen`, appends fadump args, scans memory, initializes jump labels, parses early params, sets initial memory limits, reserves kernel and crash regions, enforces memory caps, permits memblock resize, moves the FDT if it overlaps restricted areas, scans CPU features and boot CPU data, initializes early MMU, firmware and paravirt features, pkeys, PS3 flags, PLPKS, and transactional memory. Later callers use chip-id helpers against the live device tree.

State and persistence: memblock additions/reservations and `memory_limit` shape the physical memory map for the rest of boot. CPU feature bits are mutated in `cur_cpu_spec` and user-visible feature masks. Boot CPU logical/physical ids and hardware description strings are persisted. Chip-id lookup can be cached by core index.

Dependencies and integration points: depends on libfdt, OF flat tree helpers, memblock, crash/fadump/kdump, RTAS/OPAL/pseries/powernv firmware probes, MMU setup, CPU feature tables, dynamic reconfiguration memory, ultravisor, pkeys, PLPKS, SMP boot data, and initrd handling.

Risks: this code runs before normal allocators and full diagnostics, so failures often panic. Firmware property parsing must handle endian and cell-size conventions exactly. Moving the FDT must avoid memory limits, crashkernel, initrd, and non-memory. `iommu_is_off` restricts usable memory below 2 GiB on PPC64. Incorrect CPU feature mutation affects user ABI and facility availability.

Test signals: early boot logs should identify model, memory, boot CPU, and feature setup without panics. Validate `mem=`, crashkernel/fadump, initrd overlap, relocatable kernel first-block discovery, dynamic LMB memory on pseries, TM disabled/enabled policy, chip-id lookup, SMP boot CPU mapping, and firmware feature detection on pseries, powernv, and BookE-style systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_entry_64.S -->
## sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_entry_64.S

Purpose: this 64-bit assembly entry helper calls Open Firmware/PROM code that runs in 32-bit big-endian mode, while preserving the 64-bit kernel register and MSR state needed to return safely.

Important API: `_GLOBAL(enter_prom)` is the exported entry point. It saves LR, creates a switch frame, saves registers PROM may clobber, saves CR and MSR, loads the PROM entry address from `r4` into SRR0, sets a local return trampoline in LR, constructs a 32-bit big-endian MSR in SRR1, and transfers control using the proper return-from-interrupt sequence for Book3E or Book3S. On return, it fixes endian state, repairs the high half of `r1`, restores MSR, registers, CR, LR, stack pointer, and returns.

Control flow: caller enters with a PROM function address. The helper builds a protected frame, switches processor mode through SRR0/SRR1, PROM executes and returns to the trampoline label, and the helper restores 64-bit kernel execution context. `FIXUP_ENDIAN`, `MTMSRD`, and `RFI_TO_KERNEL` abstract CPU-family details.

State and persistence: it does not own global state. It temporarily persists saved GPRs, CR, MSR, and LR on the kernel stack. Processor state changes include clearing 64-bit and little-endian bits before PROM entry, then restoring the original MSR after return.

Dependencies and integration points: depends on PowerPC exception return mechanics, stack-frame offsets from `asm-offsets.h`, Book3S/Book3E exception macros, PROM calling conventions, and `ppc_asm.h` save/restore helpers. It is part of the low-level Open Firmware call path used during early boot or firmware interactions on 64-bit systems.

Risks: any mismatch in saved frame layout or MSR bit manipulation can prevent returning to the kernel. PROM clobbers upper halves of registers it saves, which is why the helper saves nonvolatile state; missing a clobbered register would corrupt callers. Endianness and 32/64-bit mode transitions are fragile and CPU-family-specific.

Test signals: firmware calls through this path should return with preserved nonvolatile registers, CR, MSR, stack pointer, and LR. Boot-time OF interactions on 64-bit Book3S and Book3E configurations are the main validation. Failures usually appear as early boot hangs, bad return addresses, or corrupted stack/register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_entry_64.S -->
