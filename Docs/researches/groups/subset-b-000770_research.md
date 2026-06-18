# subset-b-000770 research

This grouped report covers the subset B PowerPC header files requested for `subset-b-000770`. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_pfunc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_pfunc.h

Purpose: This header defines the PowerMac platform-function framework used by old Apple Open Firmware based machines. It describes tokenized firmware "platform-do-..." functions, their flags, the argument convention, driver interpreter callbacks, interrupt clients, and public lookup/call APIs.

Important APIs/types/functions: `struct pmf_args` carries up to four u32 values or u32 pointers plus a count. `struct pmf_handlers` is the driver interpreter vtable with lifecycle callbacks `begin`/`end`, optional IRQ enable/disable hooks, register/GPIO/I2C/config read-write and read-modify-write handlers, delay/wait handlers, and `owner` for module ownership. `struct pmf_function` stores a parsed function list entry with OF node, driver data, name, phandle filter, flags, token blob, IRQ client list, and `kref`. `struct pmf_irq_client` registers a callback and owner against one interrupt-capable function. Public calls include `pmf_register_driver`, `pmf_unregister_driver`, `pmf_register_irq_client`, `pmf_unregister_irq_client`, `pmf_do_irq`, `pmf_do_functions`, `pmf_call_function`, `pmf_find_function`, `pmf_get_function`, `pmf_put_function`, `pmf_call_one`, `pmac_pfunc_base_install`, and suspend/resume hooks.

Control flow: A platform-function-capable driver registers handlers for a device node. The core parses firmware command lists and associates `pmf_function` objects with the device. Calls either match all functions by flags/phandle/name through `pmf_do_functions`, use the higher-level `pmf_call_function` on a target node and OnDemand functions, or pre-find a function for low latency and invoke `pmf_call_one`. Interpreter execution starts with `begin`, passes the returned instance data through each handler, and finishes with `end`.

State and persistence: The header defines in-memory kernel state only: linked lists of functions and interrupt clients, per-function parsed blobs, and refcounts. Firmware command data is treated as immutable source data, while driver-provided `driver_data` and handler instance data hold runtime state. IRQ clients persist until explicitly unregistered and cannot reuse the same embedded list node.

Dependencies and integration points: It depends on Linux list and type support, device tree `struct device_node`, modules, and krefs. It integrates platform firmware data with PowerMac device drivers, PMU suspend/resume paths, GPIO/I2C/config-space accesses, and interrupt dispatch from low-level handlers into client callbacks.

Risks and test signals: Callers must supply the right argument count and pointer/value convention because the firmware format does not encode type safety. IRQ callbacks run under a spinlock and must not reenter PMF APIs. Handler callbacks may be NULL, so parser/executor paths must guard unsupported commands. Useful tests are PowerMac boot coverage, sleep/wake paths, IRQ client registration lifetime, module unload while functions are referenced, and negative tests for missing handlers or mismatched args.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_pfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmc.h

Purpose: This header provides the architecture interface for reserving and enabling PowerPC performance monitor counters and for coordinating PMU ownership with pseries/LPAR and KVM HV state.

Important APIs/types/functions: `perf_irq_t` is a callback taking `struct pt_regs *`; `perf_irq` is the registered interrupt handler pointer. `reserve_pmc_hardware`, `release_pmc_hardware`, and `ppc_enable_pmcs` form the generic PMU reservation and enable API. On Book3S 64-bit, `ppc_set_pmu_inuse` updates lppaca and/or paca state so firmware or KVM can know PMU registers are in use. `ppc_get_pmu_inuse` exists for KVM HV builds, and `power4_enable_pmcs` is declared for POWER4-style PMU enablement.

Control flow: Perf or low-level PMU code reserves hardware with a new interrupt handler, enables PMCs, handles PMU interrupts through `perf_irq`, and releases the reservation on teardown. On LPAR systems or KVM HV capable builds, the reservation path can mark PMU usage in per-CPU/shared processor accounting structures.

State and persistence: The main persistent state is the global `perf_irq` pointer and per-CPU/per-partition PMU-in-use flags in `lppaca` and `paca`. The header itself has no storage, but its inline setter mutates firmware-visible and hypervisor-visible state.

Dependencies and integration points: It includes `asm/ptrace.h` for interrupt register context. Book3S 64-bit paths depend on `lppaca`, `paca`, and `firmware_has_feature(FW_FEATURE_LPAR)`. It integrates with perf, PMU interrupt handlers, pseries shared processor firmware, and KVM HV virtualization.

Risks and test signals: Reservation must serialize users so two PMU clients do not install competing handlers. PMU-in-use state must be set and cleared around guest and host PMU access to avoid corrupting counters or exposing stale state. Tests should cover perf event setup/teardown, nested KVM/pseries builds, LPAR and bare-metal builds, and PMU interrupt delivery with `pt_regs` content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pnv-ocxl.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pnv-ocxl.h

Purpose: This header declares PowerNV platform services for OpenCAPI/OCXL devices, including translation layer capabilities, XSL register mapping, SPA setup, LPAR mapping, and TLB invalidation control.

Important APIs/types/functions: Constants define TL template/rate-buffer sizes and ATS/ATSD register offsets and bitfields such as `PNV_OCXL_ATSD_LNCH_RIC`, `PID`, `AP`, `L`, and AVA masks. Public APIs include `pnv_ocxl_get_actag`, `pnv_ocxl_get_pasid_count`, `pnv_ocxl_get_tl_cap`, `pnv_ocxl_set_tl_conf`, `pnv_ocxl_get_xsl_irq`, `pnv_ocxl_map_xsl_regs`, `pnv_ocxl_unmap_xsl_regs`, `pnv_ocxl_spa_setup`, `pnv_ocxl_spa_release`, `pnv_ocxl_spa_remove_pe_from_cache`, `pnv_ocxl_map_lpar`, `pnv_ocxl_unmap_lpar`, and `pnv_ocxl_tlb_invalidate`.

Control flow: An OCXL PCI driver queries ACTAG/PASID/TL capabilities, configures TL rates with a physical rate buffer, maps interrupt and XSL fault/status registers, initializes SPA memory for process elements, maps an LPAR address register view, and issues ATSD invalidates by writing launch/address fields. Release paths unmap registers and LPAR views and tear down SPA platform data.

State and persistence: Runtime state is owned by callers and returned platform data: mapped MMIO pointers, SPA memory, platform-private data, PE cache state, and LPAR ARVA mappings. The header encodes register layout but does not allocate storage.

Dependencies and integration points: It depends on `linux/bitfield.h`, `linux/pci.h`, and PowerPC `PPC_BIT`/`PPC_BITMASK` semantics. It integrates PCI OCXL drivers with PowerNV OPAL/platform code, radix translation invalidation, XSL interrupt handling, and process address space management.

Risks and test signals: Register bitfield mistakes can invalidate the wrong PID, page size, scope, or address. Rate-buffer physical addresses and sizes must match firmware expectations. Mapping lifetimes must avoid stale MMIO pointers after device removal. Tests should include OCXL capability probing, TL setup round trips, SPA create/remove, PE cache removal, TLB invalidation for 4K/64K/2M/1G pages, and device hot-unplug cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pnv-ocxl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pnv-pci.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pnv-pci.h

Purpose: This header exposes PowerNV PCI and PCI hotplug interfaces backed by OPAL, including slot ID encoding, device-tree retrieval, slot presence/power state, MSI EOI helpers, and PowerNV hotplug slot state.

Important APIs/types/functions: `PCI_SLOT_ID_PREFIX`, `PCI_SLOT_ID`, and `PCI_PHB_SLOT_ID` encode OPAL slot identifiers. Declarations include `pnv_pci_get_slot_id`, `pnv_pci_get_device_tree`, presence and power state getters, `pnv_pci_set_power_state`, `pnv_opal_pci_msi_eoi`, and `is_pnv_opal_msi`. `struct pnv_php_slot` wraps `struct hotplug_slot` and records OPAL ID, name, flags such as `PNV_PHP_FLAG_BROKEN_PDC`, kref, slot state, IRQ, workqueue, device nodes, PCI objects, attention/power state, FDT/change-set state, parent/children, and list links.

Control flow: PowerNV PCI code identifies slots from device-tree nodes, queries OPAL for presence and power, retrieves slot device-tree fragments, applies OF changesets for hotplug, and powers slots through OPAL with asynchronous messages. MSI handling checks whether an IRQ chip is PowerNV OPAL MSI and sends EOI through OPAL.

State and persistence: Hotplug slot structures persist across registration, population, offline, and removal states. They own krefs, OF changeset state, dynamic FDT buffers, child lists, and links into broader hotplug management. Power state and attention state mirror platform state.

Dependencies and integration points: It depends on Linux PCI, PCI hotplug, IRQ, Open Firmware, and `asm/opal-api.h`. It integrates PHB/slot management with OPAL firmware, dynamic device tree updates, workqueues, PCI device/bus objects, and the IRQ/MSI subsystem.

Risks and test signals: OPAL slot IDs must be encoded consistently or power operations can target the wrong PHB/device. Dynamic OF changesets and FDT buffers need correct lifetime handling. Hotplug transitions must be serialized across workqueue, IRQ, and kref paths. Tests should cover physical slot presence/power operations, hotplug add/remove, broken PDC handling, MSI EOI behavior, and error paths from OPAL calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pnv-pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/powernv.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/powernv.h

Purpose: This compact header declares PowerNV-only platform hooks for nest MMU PTCR setup, CPU hotplug LPCR programming, and transactional memory initialization, with no-op stubs outside `CONFIG_PPC_POWERNV`.

Important APIs/types/functions: Under `CONFIG_PPC_POWERNV`, it exports `powernv_set_nmmu_ptcr`, `pnv_program_cpu_hotplug_lpcr`, and `pnv_tm_init`. Without PowerNV support, `powernv_set_nmmu_ptcr` and `pnv_tm_init` become empty inline functions; `pnv_program_cpu_hotplug_lpcr` is only declared for the PowerNV case.

Control flow: PowerNV initialization or CPU hotplug code calls these hooks to configure platform-specific MMU and LPCR state, and TM setup code calls `pnv_tm_init`. Non-PowerNV builds compile call sites away for the no-op functions.

State and persistence: State is platform CPU/MMU register state rather than header-owned memory. PTCR/LPCR programming persists in processor/platform registers until changed during boot, hotplug, or reconfiguration.

Dependencies and integration points: It depends on `CONFIG_PPC_POWERNV` and integrates with PowerNV CPU bringup, nest MMU configuration, OPAL/platform initialization, and transactional memory setup.

Risks and test signals: Stubs can hide accidental calls on unsupported platforms, so call sites must have correct config guards when they need real effects. LPCR and PTCR values are low-level architectural state and mistakes can break translation or hotplug. Tests are PowerNV boot, CPU online/offline cycles, radix/hash MMU mode coverage, and TM feature initialization checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/powernv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc-opcode.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc-opcode.h

Purpose: This header is the central PowerPC instruction encoding catalog used by assembly, code patching, emulation, probes, alternatives, and inline assembly that must emit instructions unsupported by older assemblers.

Important APIs/types/functions: It defines register number macros (`__REG_R*`, `_R*`), immediate field helpers (`IMM_L`, `IMM_DS`, `IMM_DQ`, `IMM_HA`, `IMM_H18`), primary opcode and extended opcode constants, instruction images and masks such as `PPC_INST_SYNC`, `PPC_INST_MTMSRD`, and `PPC_INST_BRANCH_COND`, field insertion helpers (`___PPC_RA`, `__PPC_SPR`, `__PPC_SH64`, etc.), and a large set of `PPC_RAW_*` macros that produce 32-bit instruction words. It also provides assembler-string wrappers like `PPC_WAIT`, `PPC_TLBIE_5`, `PPC_COPY`, `LXVD2X`, `XXSWAPD`, `TRECLAIM`, `TABORT`, and `PPC_RAW_TRAP`.

Control flow: There is no runtime control flow in the header. Consumers compose instruction words by ORing base opcodes with encoded operands, then use the raw value in generated code, `.long` inline assembly, patch sites, decode masks, or probe filters. Conditional aliases select 32-bit or 64-bit forms for load/store/cmp macros.

State and persistence: The only state is compile-time constants. Persisted effects occur in generated kernel text when these macros are used for static code, runtime patching, alternatives, or instruction emulation tables.

Dependencies and integration points: It includes `asm/asm-const.h` and is used by assembly helpers, kprobes, feature fixups, barrier code, TLB/cache code, transactional memory paths, radix/hash MMU code, and low-level exception code. It is tightly coupled to ISA encodings and assembler syntax.

Risks and test signals: A single bit error can emit a different privileged instruction, wrong register, wrong page-size invalidation, or broken barrier. Immediate helpers must match sign-extension and alignment rules. Tests include build coverage with old/new binutils, objdump inspection of emitted instructions, kprobes single-step exclusions, runtime TLB/cache/PMU/TM paths on real hardware or emulators, and instruction patch selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc-opcode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc-pci.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc-pci.h

Purpose: This header collects generic PowerPC PCI declarations spanning host bridges, ISA bridge state, device-tree traversal, RTAS PCI configuration, IOMMU registration, EEH, and optional ULI1575 initialization.

Important APIs/types/functions: It declares `isa_io_base`, `hose_list`, `isa_bridge_pcidev`, `BUID_HI`, `BUID_LO`, `pci_traverse_device_nodes`, `pci_devs_phb_init_dynamic`, optional `ppc_iommu_register_device` and unregister stubs, RTAS helpers `init_pci_config_tokens`, `get_phb_buid`, `rtas_setup_phb`, config accessors `rtas_pci_dn_read_config` and write, EEH cache/state/sysfs helpers, `uli_init`, and `PCI_BUSNO`.

Control flow: PCI initialization sets config tokens, discovers PHBs, initializes device nodes, registers IOMMU devices when pseries/PowerNV IOMMU API is available, and sets up RTAS-backed config access. EEH code inserts/removes devices from address caches, marks or clears PE states, resets PEs, saves BARs, and updates sysfs.

State and persistence: The header references global PCI topology state: host bridge lists, ISA bridge pointer, EEH caches, IOMMU registration, and per-PHB/device-node metadata. It defines no storage itself.

Dependencies and integration points: It is gated by `CONFIG_PCI` and includes Linux PCI plus `asm/pci-bridge.h`. It integrates PowerPC PCI host bridge code with Open Firmware nodes, RTAS calls, IOMMU API, EEH error recovery, sysfs, and Freescale ULI1575 support.

Risks and test signals: Config-dependent stubs must preserve buildability when PCI or IOMMU is disabled. RTAS config access must use the correct `pci_dn` and size. EEH state transitions can affect recovery and device removal. Tests should cover PCI boot enumeration, dynamic PHB init, RTAS config reads/writes, EEH injection/recovery, IOMMU add/remove, and no-PCI builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc-pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc4xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc4xx.h

Purpose: This small header declares the PPC4xx platform reset entry point.

Important APIs/types/functions: `ppc4xx_reset_system(char *cmd)` is declared `__noreturn`, indicating the platform reset path does not return to its caller.

Control flow: Board or architecture restart code passes an optional command string to `ppc4xx_reset_system`, which performs the machine reset in platform implementation code.

State and persistence: The function affects persistent machine state by resetting the system. The header owns no data.

Dependencies and integration points: It relies on `__noreturn` being defined by surrounding kernel headers and integrates with PowerPC 4xx reboot/restart machinery.

Risks and test signals: Because the function never returns, callers must not expect cleanup after invocation. Tests are limited to PPC4xx reboot paths, watchdog/reset-controller behavior, and build coverage for configs including this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc4xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc_asm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc_asm.h

Purpose: This header provides PowerPC assembly macros for register save/restore, symbol declarations, stack frame construction, TOC/address loading, endian fixups, TLB/cache helpers, register names, soft-mask/restart tables, and ABI-specific constants.

Important APIs/types/functions: Major assembler macros include `OP_REGS`, `ZEROIZE_REGS`, `SAVE_GPRS`, `REST_GPRS`, `SAVE_NVGPRS`, FPR/VR/VSR/EVR save and restore groups, `SANITIZE_*` register clearing macros, HMT priority macros, `_GLOBAL`, `_GLOBAL_TOC`, `DOTSYM`, `_ASM_NOKPROBE_SYMBOL`, `LOAD_REG_IMMEDIATE`, `LOAD_REG_ADDR`, `LOAD_REG_ADDR_PIC`, `LOAD_PACA_TOC`, `PPC_CREATE_STACK_FRAME`, `MFTB`, `TLBSYNC`, `MTOCRF`, `tlbia`, `DCBT_*`, `toreal/fromreal/tophys/tovirt`, `MTMSRD`, `FIXUP_ENDIAN`, `FIXUP_ENDIAN_HV`, `SOFT_MASK_TABLE`, `RESTART_TABLE`, and `BTB_FLUSH`.

Control flow: The macros expand into low-level assembly sequences used by exception entry/exit, context switch, VDSO, boot, TLB invalidation, endian mode correction, feature alternatives, and ABI entry points. Some macros create table entries in named sections, while others use nested feature fixup sections to patch instructions by CPU feature.

State and persistence: Generated code saves/restores architectural register state to `pt_regs` or thread structures, updates stack frames, manipulates MSR/SRR/HSRR state for endian trampolines, writes SPRs for BTB/TLB/cache behavior, and emits metadata sections consumed by runtime fixup code.

Dependencies and integration points: It includes assembler compatibility, processor definitions, opcode macros, firmware flags, feature fixups, and exception-table support. It sits at the intersection of C-visible ABI definitions, assembly source files, kprobe blacklists, CPU feature patching, KVM/BookE/Book3S variants, and endian/TOC models.

Risks and test signals: Incorrect offsets or ABI variants corrupt saved registers, stack unwinding, or TOC setup. Endian fixup code is deliberately raw instruction data and must preserve exact encodings. Sanitization macros affect security hardening. Tests should include allmodconfig/defconfig builds for 32/64-bit, BE/LE, ELFv1/ELFv2, BookE/Book3S, boot tests, exception return tests, objdump checks, kprobe blacklist validation, and CPU feature alternative patch coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/preempt.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/preempt.h

Purpose: This header adapts generic preemption support for PowerPC and exposes a PowerPC-specific `need_irq_preemption()` predicate for IRQ-entry/exit preemption decisions.

Important APIs/types/functions: It includes `asm-generic/preempt.h`. With `CONFIG_PREEMPT_DYNAMIC`, it declares the static key `sk_dynamic_irqentry_exit_cond_resched` and defines `need_irq_preemption()` as a static-branch check. Otherwise it returns `IS_ENABLED(CONFIG_PREEMPTION)`.

Control flow: IRQ return or entry/exit code can call `need_irq_preemption()` to decide whether conditional rescheduling is enabled. Dynamic preemption changes update the static key so the branch can be patched efficiently.

State and persistence: The dynamic build stores state in the jump-label static key; non-dynamic builds encode the state at compile time. The header owns no runtime data beyond the external key declaration.

Dependencies and integration points: It integrates generic preempt accounting, Linux jump labels, dynamic preemption, and PowerPC interrupt entry/exit paths.

Risks and test signals: Incorrect static-key polarity would change IRQ preemption behavior globally. Build tests should cover `CONFIG_PREEMPT_DYNAMIC`, `CONFIG_PREEMPTION`, and non-preempt configs. Runtime tests include preemption model switching, IRQ return latency, scheduler selftests, and lockdep/preempt count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/preempt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/probes.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/probes.h

Purpose: This header centralizes PowerPC kprobe/uprobe probe support helpers: breakpoint instruction selection, trap detection, single-step eligibility, and enabling single-step state in `pt_regs` and debug registers.

Important APIs/types/functions: `BREAKPOINT_INSTRUCTION` uses `PPC_RAW_TRAP()`. `IS_TW`, `IS_TD`, `IS_TDI`, and `IS_TWI` identify trap encodings, with `is_trap()` selecting 64-bit or 32-bit forms. `MSR_SINGLESTEP` maps to `MSR_DE` for advanced debug registers or `MSR_SE` otherwise. `can_single_step(u32 inst)` rejects trap, syscall, return-from-interrupt, sleep/nap/stop, and MSR-mutating instructions. `enable_single_step(struct pt_regs *regs)` sets the return MSR single-step bit and, on advanced debug systems, disables critical interrupts and programs `DBCR0`.

Control flow: Probe code checks whether an instruction may be single-stepped. If safe, it updates the saved return MSR so execution resumes with single-step enabled. Advanced debug hardware also receives DBCR0 changes before returning to the probed instruction.

State and persistence: State changes are saved in `pt_regs->msr` for the return path and possibly in the live DBCR0 SPR. The choice avoids stepping instructions that alter control privilege, interrupt return, power state, or MSR.

Dependencies and integration points: It depends on disassembly helpers, opcode definitions, MSR/SPR definitions from `reg.h`, and `pt_regs` mutation helpers. It integrates with kprobes, uprobes, ftrace event tracing, BookE advanced debug, and exception return code.

Risks and test signals: Stepping an unsupported privileged/control instruction can hang, recurse, or corrupt exception state. Advanced debug paths must account for critical interrupts and BookE errata requiring `isync`. Tests include kprobe single-step selftests, trap/syscall probe rejection, BookE advanced debug builds, 32/64-bit trap decode coverage, and stress tests with probes around interrupt-return and MSR instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/probes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/processor.h

Purpose: This header defines PowerPC processor and thread state visible to core kernel code: task/thread register state, floating point/vector/SPE/TM state, debug state, initial thread setup, task register accessors, idle hooks, prefetch helpers, alignment emulation hooks, and VMX usercopy entry points.

Important APIs/types/functions: Key definitions include FPR/VSX layout macros, default PPR setup, PREP/CHRP legacy platform constants, `start_thread`, `struct thread_fp_state`, `struct thread_vr_state`, `struct debug_reg`, and the large `struct thread_struct`. `thread_struct` stores kernel stack pointer, saved regs, BookE exception scratch, page directory/RTAS/KUAP fields, debug registers, FP/Altivec/VSX/SPE/TM checkpointed state, KVM pointers, DSCR/FSCR/TIDR, EBB/perf state, and DEXCR state depending on config. Other APIs include `INIT_THREAD`, `task_pt_regs`, `KSTK_EIP`, `KSTK_ESP`, prctl helpers for FPEXC/endian/unaligned/DEXCR, FP/VR load-store functions, `spin_begin`, `spin_cpu_relax`, `spin_end`, stack validation helpers, `prefetch`, `prefetchw`, idle stop functions, `fix_alignment`, math emulation functions, and VMX copy helpers.

Control flow: Scheduler and fork/exec code initialize `thread_struct`, context-switch code uses the saved FP/vector/SPE/TM flags and state, ptrace/prctl code reads or sets per-task modes, idle code selects platform stop/nap paths, and exception handling uses alignment/math emulation and stack validation helpers.

State and persistence: `thread_struct` is persistent per task and is the owner for lazy-loaded processor facilities, debug registers, transactional checkpoint state, DSCR inheritance, DEXCR-on-exec behavior, and saved register pointers. `INIT_THREAD` defines boot task initial state.

Dependencies and integration points: It includes VDSO processor definitions, `reg.h`, thread info, ptrace, hardware breakpoints, task-size headers, KVM, perf/hw breakpoint, MMU, idle, VMX/VSX/SPE, transactional memory, KUAP/KUEP, and BookE/Book3S variants.

Risks and test signals: Layout and alignment are ABI-sensitive for context switch and assembly offsets. Lazy facility flags must match save/restore code or user state can leak/corrupt. TM checkpoint state is especially sensitive. Tests include context-switch stress with FP/Altivec/VSX/SPE/TM, ptrace/prctl mode tests, hardware breakpoints, stack unwinding validation, idle/resume, alignment emulation, and 32/64-bit build variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/prom.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/prom.h

Purpose: This header defines PowerPC Open Firmware / flattened device tree boot structures and client-architecture-support option vector constants used during early boot and firmware capability negotiation.

Important APIs/types/functions: `struct boot_param_header` describes the flattened device tree block passed by prom_init or kexec, including structure/string/reserve-map offsets, version fields, boot CPU ID, string size, and structure size. It defines OF token constants such as `OF_DT_BEGIN_NODE`, `OF_DT_PROP`, and `OF_DT_END`, `MIN_RMA`, `of_parse_dma_window`, `of_instantiate_rtc`, `of_get_ibm_chip_id`, `struct of_drc_info`, `of_read_drc_info_cell`, and `boot_cpu_node_count`. It also defines CAS option vector bits from architecture levels through firmware options, PAPR features, XIVE, MMU modes, dynamic reconfiguration, and Linux OS hint bits.

Control flow: Early boot receives and parses the FDT header, memory reserve map, structure block, and strings block. Firmware negotiation uses option vector constants either through root `ibm,client-architecture-support` or legacy fake ELF notes. Later platform code parses DMA windows, RTC nodes, chip IDs, and DRC info cells.

State and persistence: The FDT boot block and reserved memory map persist through boot long enough to instantiate kernel device nodes. `boot_cpu_node_count` records boot CPU node discovery. Option vectors influence firmware-selected capabilities for the lifetime of the boot.

Dependencies and integration points: It depends on Linux types, device-tree structures, and firmware feature logic. It integrates prom_init, kexec boot, pseries/PAPR negotiation, dynamic reconfiguration, XIVE, radix/hash MMU selection, NUMA affinity, MSI, large pages, memory hotplug, and RTC initialization.

Risks and test signals: FDT offsets and endian fields must be parsed exactly. Option vector bits overlap by vector index, so `OV5_FEAT` and `OV5_INDX` must be used correctly. CAS negotiation mistakes can disable required features or request unsupported ones. Tests include pseries boot under firmware/PowerVM/QEMU, kexec, memory hotplug DRC parsing, DMA window parsing, XIVE/radix/hash negotiation, and old firmware fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/prom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3.h

Purpose: This header defines the PS3 platform interface for firmware versioning, OS area storage, DMA/MMIO regions, interrupt setup, LV1 result codes, system-bus devices and drivers, system manager operations, preallocated buffers, logical performance monitor access, and early debug shutdown.

Important APIs/types/functions: It defines `union ps3_firmware_version`, OS area helpers, flash ops, `enum ps3_dma_page_size`, `enum ps3_dma_region_type`, `struct ps3_dma_region`, `struct ps3_dma_region_ops`, DMA init/create/free/map/unmap APIs, `enum ps3_mmio_page_size`, `struct ps3_mmio_region`, MMIO init/create/free and physical-to-LPAR helpers, many IRQ setup/destroy functions, `enum lv1_result` and `ps3_result`, match IDs/module aliases, `struct ps3_system_bus_device`, `struct ps3_system_bus_driver`, registration helpers, driver-data accessors, `struct ps3_sys_manager_ops`, power/restart/halt/WOL APIs, prealloc descriptors, LPM rights/types, LPM open/close/copy/bookmark/signal APIs, PM counter accessors, and `ps3_early_mm_init`.

Control flow: PS3 platform discovery creates `ps3_system_bus_device` objects with DMA/MMIO regions and interrupts. Drivers register `ps3_system_bus_driver` instances matching IDs/sub-IDs, open LV1 devices, create regions, set up IRQs, perform I/O, and tear down on remove/shutdown. System manager operations are registered for power/restart. LPM/perf functions interact with LV1 monitor services.

State and persistence: Persistent runtime state includes per-device DMA region chunk lists, MMIO mappings, IRQ plugs, system bus core device state, driver private data, OS area RTC diff and flash state, system manager ops, preallocated video/flash buffers, and LPM session state.

Dependencies and integration points: It depends on Linux device, spinlock/list/completion/user access types through included headers, Cell PMU definitions, and PS3 LV1 hypervisor calls in implementation files. It integrates PS3 USB/network/storage/AV/GPU/sound/LPM drivers with the PS3 system bus, hypervisor, firmware OS area, interrupt domain, DMA/IOMMU, and power management.

Risks and test signals: LV1 result handling may compile to empty strings outside verbose builds, so diagnostics differ by config. DMA and MMIO region lifetimes must match hypervisor mappings. Flexible system-bus matching and module aliases are ABI for PS3 drivers. Tests include PS3 boot/device enumeration, DMA map/unmap alignment and page-size coverage, IRQ setup/destroy per class, system manager restart/poweroff, LPM open/copy, firmware version comparison, and driver probe/remove cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3av.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3av.h

Purpose: This header defines the PS3 AV backend command ABI: command IDs, video/audio/HDMI constants, event/status bits, packet structures, and high-level command helper declarations for video and audio mode control.

Important APIs/types/functions: It defines `PS3AV_VERSION`, command IDs for AV init/finalize, hardware config, monitor info, events, mute, video color-space/mode/format/pitch, audio mode/mute/control, and AVB parameter batches. It encodes port/head counts, event bits, video modes, color spaces, audio layouts, sampling rates, HDMI/DVI flags, region/default modes, `enum ps3av_mode_num`, send/reply headers, monitor info structures, packet structures for every command class, `struct ps3av_pkt_avb_param`, `ps3av_mode_cs_info`, status codes, and helper APIs such as `ps3av_set_hdr`, `ps3av_do_pkt`, `ps3av_cmd_init`, mode/mute/audio helpers, monitor info query, auto-mode selection, and resolution conversion.

Control flow: Callers build typed packets, fill headers with `ps3av_set_hdr`, send them through `ps3av_do_pkt`, and interpret backend status codes. High-level helpers generate packet payloads for video/color/audio configuration and batch them via AVB param when needed. Mode selection can use monitor info, region flags, and automatic resolution masks.

State and persistence: Header-defined packet layouts describe data exchanged with the AV backend over PS3 communication channels. Persistent state lives in the backend/driver: current mode, monitor info, audio channel-status data, mute state, and event subscription.

Dependencies and integration points: It depends on Linux integer typedefs and integrates PS3 AV setting drivers with VUART/syscon/backend firmware, framebuffer/video mode setup, HDMI/AVMULTI/SPDIF ports, audio drivers, monitor EDID-like data, and user-visible mode selection.

Risks and test signals: Packet structure sizes and packing are firmware ABI. Several constants warn not to use backend AV values directly but convert from video values. Flexible audio blocks and AVB variable buffer layout require careful bounds checks. Tests should cover command packet size/version fields, monitor info parsing, all supported video modes/regions, HDMI/DVI flags, audio channel layouts, mute/unmute paths, event enable/disable, and backend error status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3av.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3gpu.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3gpu.h

Purpose: This header defines PS3 GPU LV1 context-attribute constants and inline wrappers used by framebuffer/video code to synchronize display, flip buffers, set up framebuffer memory, blit, and close framebuffer state.

Important APIs/types/functions: Constants include display sync/flip attributes, framebuffer setup/blit/sync/close attributes, blit wait flag, and HSYNC/VSYNC sync selectors. `ps3_gpu_mutex` is declared as the mutex synchronizing GPU accesses and video mode changes. Inline wrappers call `lv1_gpu_context_attribute`: `lv1_gpu_display_sync`, `lv1_gpu_display_flip`, `lv1_gpu_fb_setup`, `lv1_gpu_fb_blit`, and `lv1_gpu_fb_close`.

Control flow: GPU/framebuffer code locks around mode or GPU access, calls LV1 context-attribute wrappers with a context handle and offsets/LPAR addresses, waits or syncs as needed, flips display heads, and closes framebuffer mappings at teardown.

State and persistence: The mutex serializes shared GPU/video state. Persistent state resides in LV1 GPU context handles, DDR/XDR/ioif offsets, and framebuffer setup configured by hypervisor calls.

Dependencies and integration points: It includes `linux/mutex.h` and `asm/lv1call.h`, integrating PS3 framebuffer and AV/video mode code with the LV1 hypervisor GPU interface.

Risks and test signals: Incorrect offsets or context handles can corrupt display memory or fail LV1 calls. Missing mutex coverage can race mode changes with blits/flips. Tests include framebuffer setup/close, display flip on both heads, sync modes, blit with/without wait flag, video mode changes under load, and LV1 error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3gpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3stor.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3stor.h

Purpose: This header defines the common PS3 storage-device structure and command helpers used by disk, ROM, and flash storage drivers.

Important APIs/types/functions: `struct ps3_storage_region` records a region id, start, and size. `struct ps3_storage_device` embeds a `ps3_system_bus_device`, DMA region, IRQ, block size, async tag/status/completion, bounce buffer metadata, region count, accessible region bitmap, selected region index, and a flexible array of regions. `to_ps3_storage_device` converts from core `struct device`. Public functions are `ps3stor_setup`, `ps3stor_teardown`, `ps3stor_read_write_sectors`, and `ps3stor_send_command`.

Control flow: A PS3 storage driver allocates a device with region records, registers it on the system bus, calls setup with an IRQ handler, uses bounce/DMA memory to submit LV1 storage commands, waits on `done`, checks `lv1_status`, and tears down IRQ/DMA state during removal.

State and persistence: Device state persists across I/O: DMA mapping, IRQ number, block size, command tag/status, completion, bounce buffer LPAR/DMA addresses, accessible regions, and the current region index.

Dependencies and integration points: It depends on Linux interrupts and PS3 system bus/DMA declarations from `ps3.h`. It integrates block/flash/ROM drivers with PS3 LV1 storage commands, the PS3 system bus, DMA bounce buffering, and interrupt completion.

Risks and test signals: Flexible-array allocation must include all regions. Bounce buffer size/alignment and DMA lifetime are critical. Region selection must respect `accessible_regions`. Tests include setup/teardown, read/write sector commands, command timeout/error status paths, IRQ completion, multi-region devices, and suspend/remove during outstanding I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3stor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pte-walk.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pte-walk.h

Purpose: This header wraps PowerPC page-table walking helpers for locating Linux PTEs and translating kernel vmap/ioremap addresses to physical addresses without locking, including real-mode-safe use cases.

Important APIs/types/functions: `__find_linux_pte` is the underlying walker. `find_linux_pte` checks that IRQs are disabled, calls the walker, and debug-warns if huge-page shift is reported when hugepage configs are disabled. `find_init_mm_pte` walks `init_mm.pgd`. `ppc_find_vmap_phys` resolves a vmalloc/ioremap address to a physical address using the PTE PFN and hugepage/PAGE_SHIFT offset.

Control flow: Callers disable IRQs before general PTE walking, call `find_linux_pte` with optional THP and hugepage shift outputs, and handle a returned PTE pointer. Real-mode or vmap translation code calls `ppc_find_vmap_phys`, which finds the `init_mm` PTE, warns and returns zero if missing, computes PFN physical base, chooses hugepage shift or `PAGE_SHIFT`, and adds the page offset.

State and persistence: The functions read page-table state but do not mutate it. `init_mm` page tables are assumed not to be freed and not to use THP, although huge vmalloc/ioremap pages may exist.

Dependencies and integration points: It depends on scheduler/MM types, page table types/macros, IRQ state checks, `init_mm`, `VM_WARN`, and PTE helpers. It integrates with MMU code, hash/radix page table walking, vmalloc/ioremap translation, and real-mode code paths that cannot take normal locks.

Risks and test signals: Calling with IRQs enabled can race page-table changes. Missing PTEs in `ppc_find_vmap_phys` return zero after warning. Hugepage shift handling must match mapping size or physical offsets are wrong. Tests should cover vmalloc and ioremap translations, huge vmalloc mappings, debug VM warnings, IRQ-disabled callers, and real-mode users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pte-walk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ptrace.h

Purpose: This header defines the kernel PowerPC `pt_regs` stack-frame ABI and helper functions used by syscall tracing, exception handling, probes, stack inspection, and user register access.

Important APIs/types/functions: `struct pt_regs` overlays `struct user_pt_regs` with named GPR/NIP/MSR/CTR/LR/XER/CCR/orig/result/trap/DAR/DSISR fields plus config-specific SOFTE/MQ, PPR/exit/KUAP/AMR/IAMR padding, and BookE MAS/SRR/CSRR/DSRR fields. It defines stack frame sizes for 32/64-bit and ELF ABI variants, redzone sizes, signal frame sizes, `profile_pc`, syscall trace entry/leave declarations, return-register mutation helpers, `instruction_pointer`, `user_stack_pointer`, `user_mode`, `force_successful_syscall_return`, `current_pt_regs`, trap flag helpers, syscall success/return value helpers, recoverability helpers around `MSR_RI`, single-step capability macros, register query APIs, `regs_get_register`, stack bounds helpers, `regs_get_kernel_stack_nth`, and `regs_get_kernel_argument`.

Control flow: Exception and syscall entry code saves volatile state into `pt_regs`; helpers mutate return NIP/MSR and invalidate PACA saved return copies when needed. Syscall tracing inspects traps, computes success/error return values, and can force no-error handling. Kprobes/ftrace read registers by offset and extract up to eight kernel arguments.

State and persistence: `pt_regs` lives on the kernel stack for an exception/syscall frame. Trap low bits encode flags such as no-restart. Return MSR/NIP updates are persistent until exception return. Book3S 64-bit updates clear `local_paca` SRR/HSRR validity caches.

Dependencies and integration points: It includes UAPI ptrace layout, register definitions, asm constants, PACA, thread info, and kernel stack helpers. It is ABI-coupled to assembly offsets, ptrace userspace layout, syscall tracing, kprobes, ftrace, signal delivery, and exception return.

Risks and test signals: Field order and size are stack/ptrace ABI and must remain aligned. `MAX_REG_OFFSET` excludes fields past `dsisr`, so trace users must handle inaccessible offsets. Syscall success differs for SCV versus classic syscall. Tests include ptrace register tests, syscall tracing, signal delivery, kprobe/ftrace argument extraction, stack unwinding, SCV/classic syscall return semantics, and BookE/Book3S build variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/qspinlock.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/qspinlock.h

Purpose: This header implements the PowerPC front end for queued spinlocks, including fast-path trylock/unlock assembly, owner encoding, contention checks, and architecture spinlock macro bindings.

Important APIs/types/functions: Tunables include `_Q_SPIN_EH_HINT`, `_Q_SPIN_TRY_LOCK_STEAL`, `_Q_SPIN_SPEC_BARRIER`, `_Q_SPIN_MISO`, `_Q_SPIN_MISO_UNLOCK`, and `_Q_SPIN_PREFETCH_NEXT`. Helpers include `queued_spin_is_locked`, `queued_spin_value_unlocked`, `queued_spin_is_contended`, `queued_spin_encode_locked_val`, `__queued_spin_trylock_nosteal`, `__queued_spin_trylock_steal`, `queued_spin_trylock`, `queued_spin_lock`, `queued_spin_unlock`, and external `queued_spin_lock_slowpath`. It maps `arch_spin_*` operations to queued spinlock helpers and declares/stubs `pv_spinlocks_init`.

Control flow: Lock acquisition first attempts the inline trylock. The no-steal path succeeds only if the whole word is zero; the steal path may acquire when the locked bits are clear even if a tail exists, preserving the tail bits. Both use `lwarx/stwcx.` with acquire barriers. Failure falls into `queued_spin_lock_slowpath`. Unlock performs a release store to the `locked` byte and optionally emits `miso`.

State and persistence: `struct qspinlock` contains a 32-bit value with locked, owner CPU, and tail fields as defined by `qspinlock_types.h`. The owner CPU is encoded from `smp_processor_id`. Contention is inferred from `_Q_TAIL_CPU_MASK`.

Dependencies and integration points: It depends on compiler helpers, PowerPC qspinlock layout, paravirt spinlocks, PowerPC acquire barrier macros, and SMP CPU IDs. It integrates with generic locking, paravirtual spinlock initialization, slowpath queueing code, and architecture lock API macros.

Risks and test signals: Inline assembly must preserve reservation semantics and memory ordering. Trylock stealing changes fairness and can interact with slowpath queue assumptions. Owner CPU encoding depends on mask widths. Tests include locktorture/lockstorm, queued-spinlock selftests, paravirt spinlock builds, 32/64-bit SMP builds, contention/fairness measurements, and memory-order litmus tests around unlock release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/qspinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/qspinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/qspinlock_types.h

Purpose: This header defines the PowerPC queued spinlock word layout, static initializer, and byte ordering for the locked byte.

Important APIs/types/functions: It defines `_Q_SPINLOCK_LOCKED_BYTE` as byte 0 on big-endian and byte 3 on little-endian. `struct qspinlock` overlays a 32-bit `val` with `locked` and `locked_pending` byte/halfword views selected by endian layout. `__ARCH_SPIN_LOCK_UNLOCKED` initializes `.val = 0`. Bitfield constants define locked, pending, tail index, tail CPU offset, and masks. `_Q_TAIL_CPU_BITS` is 14 and `_Q_TAIL_CPU_MASK` spans the tail CPU field.

Control flow: There is no executable flow. Lock algorithms in `qspinlock.h` and slowpath code use these offsets and masks to test, set, and preserve locked/tail state.

State and persistence: The persistent state is the 32-bit lock word embedded in every queued spinlock. Endian-specific byte layout ensures `smp_store_release(&lock->locked, 0)` clears the correct byte across BE and LE kernels.

Dependencies and integration points: It depends on Linux type definitions and is consumed by architecture spinlock code, generic qspinlock slowpath, atomic operations, and assembly fast paths.

Risks and test signals: Layout mistakes break every spinlock on the architecture. The tail CPU bit width limits representable CPUs in the queue encoding and must align with NR_CPUS expectations. Tests include compile-time layout checks, locktorture on BE/LE, SMP stress with high CPU counts, qspinlock slowpath contention, and objdump/source checks of locked byte offset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/qspinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg.h

Purpose: This is the main PowerPC register definition header, covering common MSR bits, SPR numbers, fault/status bitfields, power/performance/debug/cache controls, PVR values, SPRG usage conventions, and inline helpers for MSR/SPR access.

Important APIs/types/functions: It defines MSR bit numbers and masks, transactional memory state helpers, default kernel/user MSR values by Book3S/BookE/32/64-bit config, FPSCR/SPEFSCR fields, SPR numbers for PID, CTR, DSCR, DABR/DAWR, DAR/DSISR, time base, hypervisor registers, FSCR/HFSCR, LPCR, PCR, HID, BAT, cache, performance monitor, EBB, SIER/SIAR/SDAR, and many processor-specific registers. It documents SPRG usage and defines `GET_PACA`, `SET_PACA`, `GET_SCRATCH0`, `SET_SCRATCH0`, `MTFSF_L`, PVR extraction macros, `ppc_inst_t`, `mfmsr`, `mtmsr`, `mtmsr_isync`, `mfspr`, `mtspr`, `wrtspr`, `wrtee`, MSR strict-control helpers, 32-bit segment register helpers, `current_stack_frame`, `current_stack_pointer`, SCOM accessors, and `ppc_save_regs`.

Control flow: Most content is compile-time register encoding. Inline functions and macros emit direct MSR/SPR operations with required barriers or feature-conditioned `isync`. Assembly macros select PACA/scratch SPRs based on Book3S HV mode and other config.

State and persistence: The header describes core CPU state: MSR, SPRs, perf counters, fault registers, power management registers, debug registers, SPRGs, PVRs, and stack pointer. Inline helpers mutate processor state directly and persist until overwritten by context switch, exception handling, or platform code.

Dependencies and integration points: It includes cputable, asm constants, feature fixups, BookE/FSL/8xx variant headers, and stringification. It is foundational for exception code, MMU, PMU, KVM, idle/power management, debugging, ptrace, cache/TLB control, boot CPU detection, and assembly code.

Risks and test signals: Numeric definitions are architectural contracts. Wrong masks can mis-handle faults, privilege, endian, TM, radix/hash, or hypervisor state. Inline SPR/MSR helpers are privileged and ordering-sensitive. Tests include broad PowerPC build matrix, boot tests on Book3S/BookE/8xx/FSL configs, PMU/perf tests, fault injection for DSISR/SRR1 decoding, KVM HV tests, idle/power tests, PVR matching, and objdump validation of MSR/SPR instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg_8xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg_8xx.h

Purpose: This header defines MPC8xx-specific special purpose registers and cache/debug command/status bits used by low-level 8xx code.

Important APIs/types/functions: It defines instruction/data cache control/status/address/data SPRs (`SPRN_IC_CST`, `SPRN_DC_CST`, etc.), debug/CAM/RAM registers, special MSR manipulation registers `SPRN_EIE`, `SPRN_EID`, `SPRN_NRI`, debug compare/count/control registers, `SPRN_ICTRL` for `CONFIG_PPC_8xx`, and cache commands/status such as `IDC_ENABLE`, `IDC_DISABLE`, `IDC_LDLCK`, `IDC_INVALL`, `DC_FLINE`, `DC_SFWT`, `DC_SLES`, `IDC_ENABLED`, cache error bits, `DC_DFWT`, and `DC_LES`.

Control flow: Low-level 8xx cache/MMU/debug code writes command values to cache control/status SPRs, uses address/data helper SPRs for line operations, and uses special EE/RI manipulation SPRs to change interrupt/recoverability state.

State and persistence: These definitions control 8xx processor cache mode, lock state, endian swap mode, debug compare settings, and MSR manipulation. State persists in CPU SPRs and caches until changed or reset.

Dependencies and integration points: It is included by `reg.h` and consumed by 8xx-specific MMU/cache/exception/debug code. It has no external include dependencies.

Risks and test signals: 8xx cache command values have hardware side effects and can invalidate, lock, or alter endian behavior. Tests should include PPC_8xx build coverage, cache enable/disable/invalidate paths, data cache flush line operations, debug register users, and boot on MPC8xx hardware or emulator where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg_8xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg_booke.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg_booke.h

Purpose: This header defines BookE-specific MSR bits, SPR numbers, exception/debug/MMU/cache/timer fields, thread-management registers, and access helpers for BookE PowerPC variants.

Important APIs/types/functions: It defines BookE MSR fields (`MSR_GS`, `MSR_UCLE`, `MSR_SPE`, `MSR_IS`, `MSR_DS`, `MSR_CM`), BookE kernel/user MSR defaults, many SPRs for DECAR/IVPR/USPRG/SPRG/EPCR/MSRP/IAC/DAC/DVC/LPID/MAS/TLB/guest registers/IVOR/MCSR/DBSR/DBCR/TCR/TSR/cache/EPCR/EPLC/EPSC/thread control, machine-check bits for 47x/e500, debug event masks, watchdog/FIT/PIT fields, L1/L2 cache controls, branch unit controls, guest/hypervisor routing fields, and inline `mftmr`/`mttmr`. It declares `global_dbcr0`.

Control flow: BookE exception setup uses IVPR/IVOR and MSR defaults, MMU code uses MAS/TLB/EPLC/EPSC fields, debug and ptrace code uses DBCR/DBSR/IAC/DAC definitions, timer/watchdog code uses TCR/TSR, cache code uses L1/L2/BUCSR fields, and threaded core code uses TMR/TENS registers.

State and persistence: The header maps persistent BookE CPU state in SPRs: MMU assist registers, debug control/status, machine-check syndrome, timer/watchdog state, cache controls, guest/hypervisor context, and thread enable state. `global_dbcr0` suggests global debug-control shadowing in implementation code.

Dependencies and integration points: It includes opcode macros for TMR instructions and is included from `reg.h` when `CONFIG_BOOKE` is enabled. It integrates with BookE exception vectors, KVM/guest state, e500/47x hardware, debug/hw-breakpoint support, PMU/timer code, and cache/TLB management.

Risks and test signals: BookE has many overlapping and implementation-specific SPR numbers, so config guards are critical. Debug range/mask fields can alter ptrace breakpoints. Watchdog reset fields can reset core/chip/system. Tests include BookE/e500/47x build and boot, TLB miss/refill, machine-check decoding, watchdog/FIT/PIT behavior, hardware breakpoints, KVM BookE guest paths, and cache/branch predictor setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg_booke.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg_fsl_emb.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg_fsl_emb.h

Purpose: This header defines Freescale Embedded Performance Monitor register accessors and PMR numbers/bitfields for BookE embedded performance monitoring.

Important APIs/types/functions: In C builds, `mfpmr(unsigned int rn)` and `mtpmr(unsigned int rn, unsigned int val)` emit e300 `mfpmr`/`mtpmr` instructions inside `.machine` push/pop blocks. PMR definitions cover counters `PMRN_PMC0` through `PMRN_PMC5`, local control A/B registers, global control, user counters and user local controls. Bitfields include `PMLCA_FC`, supervisor/user/PMM freeze bits, condition enable, guest/hypervisor freeze bits, event mask/shift, threshold fields, and `PMGC0_FAC`, `PMGC0_PMIE`, `PMGC0_FCECE`.

Control flow: Embedded perf code reads and writes PMRs through the inline helpers, programs event selection in PMLCA, thresholds in PMLCB, and global freeze/interrupt behavior in PMGC0, then reads counters from privileged or user PMR ranges as allowed.

State and persistence: PMR state persists in the processor performance monitor facility: counters, event selectors, freeze controls, threshold controls, interrupt enable, and user-visible PMU registers.

Dependencies and integration points: It depends on stringification and assembler support for e300 machine mode. It is included by `reg.h` only under `CONFIG_FSL_EMB_PERFMON`, integrating Freescale embedded PMU support with perf and low-level PMU code.

Risks and test signals: The inline `mtpmr` constraint should be checked carefully because the asm names an output-like operand for a write-only operation. PMR numbers and event masks are hardware ABI. Tests include FSL embedded perf build coverage, counter start/stop/read, event selection, PMU interrupts, user counter access policy, and objdump checks for `mfpmr`/`mtpmr` emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg_fsl_emb.h -->
