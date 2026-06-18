# subset-b-000822 research

This grouped report covers the s390 architecture headers requested for `subset-b-000822`. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/ftrace.h

Purpose: This header defines the s390 architecture contract for function tracing, dynamic ftrace patching, ftrace register access, syscall-name matching, and function graph callbacks.

Important APIs/types/functions: `ARCH_SUPPORTS_FTRACE_OPS`, `MCOUNT_INSN_SIZE`, `return_address()`, `ftrace_return_address`, `ftrace_caller`, `ftrace_func`, empty `struct dyn_arch_ftrace`, `ftrace_need_init_nop()`, `ftrace_init_nop()`, ftrace register helpers, optional `arch_ftrace_set_direct_caller()`, `arch_syscall_match_sym_name()`, `ftrace_graph_func()`, and assembler macros `FTRACE_NOP_INSN`, `FTRACE_GEN_MCOUNT_RECORD`, and `FTRACE_GEN_NOP_ASM` are the exposed surface.

Control flow: Compiled function entry code emits a six-byte `brcl 0,0` nop and, unless compiler hotpatch support owns the records, an entry in `__mcount_loc`. Dynamic ftrace later rewrites those nop slots to branch through `ftrace_caller`; callbacks inspect `struct ftrace_regs`, and full `pt_regs` are only returned when `PIF_FTRACE_FULL_REGS` is set.

State and persistence: The header owns no storage except external declarations, but it defines persistent text patch sites and module hotpatch metadata consumed by ftrace. Direct-call tracing stores the direct target in `orig_gpr2` inside the ftrace register frame as an in-band trampoline signal.

Dependencies and integration points: It depends on s390 stack frames, `pt_regs` flags, Linux ftrace register wrappers, modules, dynamic ftrace records, perf sampling register fill, syscall tracing, and kprobes-on-ftrace classification.

Risks and test signals: Instruction size and nop encoding must match the patcher exactly or live text patching can corrupt functions. Tests should include dynamic ftrace enable/disable, graph tracing, direct calls, perf samples from ftrace, module tracing, syscall event matching for `__s390x_` prefixes, and kprobe-on-ftrace sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ftrace.lds.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/ftrace.lds.h

Purpose: This linker-script helper reserves s390 ftrace hotpatch trampoline text proportional to the number of mcount locations.

Important APIs/types/functions: `SIZEOF_MCOUNT_LOC_ENTRY`, `SIZEOF_FTRACE_HOTPATCH_TRAMPOLINE`, `FTRACE_HOTPATCH_TRAMPOLINES_SIZE(n)`, and `FTRACE_HOTPATCH_TRAMPOLINES_TEXT` are the main definitions; the latter emits start/end symbols only under `CONFIG_FUNCTION_TRACER`.

Control flow: The architecture linker script expands `FTRACE_HOTPATCH_TRAMPOLINES_TEXT`, aligns the location to eight bytes, computes space from `__start_mcount_loc` and `__stop_mcount_loc`, and advances the location counter to reserve trampoline bytes.

State and persistence: State is persistent kernel text layout rather than runtime data. The generated `__ftrace_hotpatch_trampolines_start` and end symbols delimit space consumed by the ftrace hotpatch implementation.

Dependencies and integration points: It integrates with ftrace record emission in `ftrace.h`, module ftrace trampoline accounting, and the final vmlinux linker script.

Risks and test signals: A wrong size formula can under-reserve text and overlap later sections, while over-reserving wastes executable memory. Build/link tests with and without `CONFIG_FUNCTION_TRACER`, plus runtime dynamic ftrace patching, are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ftrace.lds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/futex.h

Purpose: This header implements s390 user-memory atomic futex operations used by the generic futex subsystem.

Important APIs/types/functions: `FUTEX_OP_FUNC` generates `__futex_atomic_set/add/or/and/xor`; `arch_futex_atomic_op_inuser()` dispatches generic futex op codes; `futex_atomic_cmpxchg_inatomic()` performs user-space compare-and-swap. The assembly uses `sacf`, load, arithmetic/logical instructions, `cs`, and user-access exception-table fixups.

Control flow: A futex operation instruments the user read, enables SACF user access, loads the old value, computes the new value, loops on failed compare-and-swap, restores access mode, and reports either the old value or a user-access fault. The cmpxchg helper follows the same access-mode and exception-table pattern.

State and persistence: The only persistent state is the user futex word modified atomically; kernel local variables hold old/new values and fault status. Instrumentation hooks feed KMSAN/usercopy accounting but do not persist futex state.

Dependencies and integration points: It depends on Linux futex op codes, uaccess instrumentation, s390 SACF access helpers from `mmu_context.h`, errno values, and `EX_TABLE_UA_FAULT` exception fixups.

Risks and test signals: The access-mode restore path is critical on all fault exits, and the compare-and-swap loop must preserve user atomicity. Tests should cover each futex op, bad user addresses, concurrent waiter/waker stress, KMSAN builds, and 31/64-bit user access edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/gmap_helpers.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/gmap_helpers.h

Purpose: This small header declares helper entry points for KVM guest address-space mapping maintenance.

Important APIs/types/functions: `gmap_helper_zap_one_page()`, `gmap_helper_discard()`, `gmap_helper_disable_cow_sharing()`, and `gmap_helper_try_set_pte_unused()` are the exported helpers.

Control flow: KVM or guest-memory management code calls these helpers to zap one host virtual page, discard a range, disable copy-on-write sharing for a protected guest context, or opportunistically mark a PTE unused.

State and persistence: State lives in the target `mm_struct`, its gmap list, PTEs, and COW-sharing flags; the header declares operations that mutate those structures but stores nothing itself.

Dependencies and integration points: It integrates with s390 KVM gmap code, `mm_struct` context fields from `mmu.h`, page-table helpers, and protected virtualization memory-sharing restrictions.

Risks and test signals: Misuse can leave stale guest translations or shared pages where secure/protected guests require exclusivity. Tests should include protected guest startup, KSM/zeropage disable paths, discard/zap range handling, and mm teardown with active gmapped memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/gmap_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/hardirq.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/hardirq.h

Purpose: This header adapts generic hardirq/softirq accounting to s390 lowcore storage.

Important APIs/types/functions: `local_softirq_pending()`, `set_softirq_pending()`, and `or_softirq_pending()` access `get_lowcore()->softirq_pending`; `__ARCH_IRQ_STAT` and `__ARCH_IRQ_EXIT_IRQS_DISABLED` advertise architecture behavior; `ack_bad_irq()` logs unexpected IRQ vectors.

Control flow: Softirq raise and processing code reads or updates the current CPU lowcore field directly. Unexpected IRQ handling emits a critical printk from `ack_bad_irq()`.

State and persistence: Softirq pending bits persist per CPU in lowcore. The header does not allocate state, but it defines the canonical accessors for that lowcore field.

Dependencies and integration points: It depends on `asm/lowcore.h` and integrates with generic hardirq, softirq, and IRQ-exit code.

Risks and test signals: Lowcore access must always refer to the current CPU; wrong prefix/lowcore setup would corrupt softirq state. Tests include IRQ/softirq stress, CPU hotplug, lowcore relocation builds, and bad IRQ injection/logging checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/hiperdispatch.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/hiperdispatch.h

Purpose: This header declares s390 HiperDispatch topology control hooks.

Important APIs/types/functions: `hd_reset_state()`, `hd_add_core(int cpu)`, `hd_disable_hiperdispatch()`, and `hd_enable_hiperdispatch()` are the public functions.

Control flow: Topology or CPU bring-up code resets state, records cores as CPUs appear, and enables or disables HiperDispatch according to platform capability and policy.

State and persistence: Persistent state is maintained by the implementation, likely CPU/core topology and dispatch enablement state; this header only exposes lifecycle entry points.

Dependencies and integration points: It integrates CPU topology management, scheduler capacity/placement logic, and IBM Z firmware/hypervisor dispatch hints.

Risks and test signals: Incorrect core accounting can degrade scheduling or target unavailable dispatch state. Tests should cover boot on LPAR/zVM/KVM, CPU hotplug, HiperDispatch disable fallback, and topology reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/hiperdispatch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/hugetlb.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/hugetlb.h

Purpose: This header provides s390-specific huge TLB page operations and declares the architecture overrides consumed by generic hugetlb code.

Important APIs/types/functions: `hugepages_supported()` maps support to `cpu_has_edat1()`. It declares `set_huge_pte_at()`, `__set_huge_pte_at()`, `huge_ptep_get()`, and `__huge_ptep_get_and_clear()`, and implements clear, get-and-clear, access-flag, write-protect, and userfaultfd-wp stubs.

Control flow: Hugepage operations inspect whether the entry is a region-3 or segment entry, clear it to the matching empty value, and update access flags by clearing and reinstalling a huge PTE. Write protection clears the current entry and writes a protected version.

State and persistence: The persistent state is the hugepage PTE/RSTE in the process page tables. Userfaultfd write-protect state is explicitly unsupported for huge PTEs here and always acts as no-op/false.

Dependencies and integration points: It depends on CPU EDAT1 capability, `pgtable.h` encodings, swap/swapops helpers, and generic hugetlb fallbacks.

Risks and test signals: Wrong region-vs-segment selection can corrupt hugepage mappings or fail TLB invalidation. Tests should include hugetlb mount/use, 1M and 2G mappings where supported, write-protect/accessed/dirty transitions, migration/swap markers, and no-EDAT1 fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/hugetlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/hw_irq.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/hw_irq.h

Purpose: This header declares initialization entry points for s390 hardware interrupt classes.

Important APIs/types/functions: `init_airq_interrupts()` initializes adapter interrupt handling and `init_cio_interrupts()` initializes channel I/O interrupts.

Control flow: Architecture boot code invokes these init functions before devices that depend on adapter or channel interrupts are activated.

State and persistence: Interrupt descriptor and low-level dispatch state lives in the implementations; this header only publishes init hooks.

Dependencies and integration points: It includes Linux MSI/PCI headers and integrates with channel I/O, PCI MSI/adapter interrupts, and boot-time IRQ setup.

Risks and test signals: Ordering mistakes can leave devices without interrupt routing. Tests should cover boot with CIO devices, PCI MSI devices, adapter interrupt users, and configs with or without PCI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/hw_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/idals.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/idals.h

Purpose: This header implements Indirect Data Address List helpers used by s390 channel command words and QDIO-style I/O buffers when data crosses addressing boundaries.

Important APIs/types/functions: It defines IDA block sizes, `idal_is_needed()`, word-count helpers for 4K and 2K IDA lists, `idal_create_words()`, `set_normalized_cda()`, `clear_normalized_cda()`, `struct idal_buffer`, allocation/free helpers for single and array IDAL buffers, CDA setup, and user-copy helpers.

Control flow: Callers decide whether a CCW can address the buffer directly or needs an IDAL. Allocation paths build page-granular DMA64 address arrays, attach them to CCWs with `CCW_FLAG_IDA`, and teardown paths free allocated lists or page chunks. User-copy helpers walk each IDA block and copy chunk by chunk.

State and persistence: Persistent state includes allocated IDAL arrays, page chunks referenced by `struct idal_buffer`, and CCW `cda` plus `CCW_FLAG_IDA` state. The array allocator returns a NULL-terminated list of buffers for large transfers split at `CCW_MAX_BYTE_COUNT`.

Dependencies and integration points: It depends on s390 DMA address types, channel I/O `struct ccw1`, GFP allocation, uaccess copy helpers, and CCW maximum byte-count rules.

Risks and test signals: Leaks or double frees are easy if `clear_normalized_cda()`/array_free are not paired with setup. Boundary calculations must match channel hardware requirements. Tests should cover below/above-2GB buffers, multi-page transfers, partial user-copy faults, allocation failure unwinds, and channel I/O drivers using direct and IDA addressing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/idals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/idle.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/idle.h

Purpose: This header defines per-CPU idle accounting data and exported sysfs attributes for s390 idle reporting.

Important APIs/types/functions: `struct s390_idle_data` stores idle counts, accumulated idle time, entry clock/timer values, and MT-cycle snapshots. `s390_idle` is declared per-CPU, and `dev_attr_idle_count` plus `dev_attr_idle_time_us` expose attributes.

Control flow: Idle entry/exit code updates the per-CPU structure, and device/sysfs code reads the exported attributes to report counts and time.

State and persistence: State persists per CPU in `s390_idle`; entry fields are transient timestamps used to accumulate totals.

Dependencies and integration points: It depends on Linux per-CPU and device attribute support and integrates with CPU idle, accounting, and sysfs CPU device reporting.

Risks and test signals: Accounting must be CPU-local and monotonic across idle transitions. Tests should cover idle sysfs reads, CPU hotplug, tickless idle, and virtualization environments with steal/MT-cycle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/idle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/io.h

Purpose: This header wires s390 generic I/O memory APIs to s390 physical mapping and zPCI instruction-backed MMIO helpers.

Important APIs/types/functions: `xlate_dev_mem_ptr()`, `unxlate_dev_mem_ptr()`, `ioremap_prot`, `ioremap_wc`, no-op `ioport_map/unmap`, PCI-specific `pci_iomap` overrides, `memcpy_fromio/toio`, `memset_io`, `mmiowb`, raw read/write aliases, and `__iowrite32_copy`/`__iowrite64_copy` are the key interfaces.

Control flow: Non-port I/O either maps device memory through architecture mapping helpers or, for PCI, uses s390 private pci_iomap cookies because BAR spaces are not disjoint. MMIO reads/writes route through zPCI load/store instructions and larger copy helpers.

State and persistence: The header stores no state; mapping cookies and zPCI iomap tables persist in the PCI implementation. It defines policy that legacy port I/O has no address space (`IO_SPACE_LIMIT 0`).

Dependencies and integration points: It depends on `page.h`, `pgtable.h`, `pci_io.h`, and `asm-generic/io.h`, integrating Linux MMIO abstractions with zPCI BAR mapping and write-combining protection helpers.

Risks and test signals: Treating s390 PCI cookies like linear ioremap addresses can address the wrong BAR. Tests should include pci_iomap/iounmap, raw read/write sizes, memcpy_to/fromio crossing boundaries, write-combine mappings, and non-PCI builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ipl.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/ipl.h

Purpose: This header defines s390 Initial Program Load and re-IPL data structures, dump-type detection, IPL reports, and DIAG 308 restart/load operations.

Important APIs/types/functions: `struct ipl_parameter_block`, IPL length constants, `struct save_area` helpers, `s390_reset_system()`, `ipl_block_get_ascii_vmparm()`, `enum ipl_type`, global `ipl_info`, `setup_ipl()`, `set_os_info_reipl_block()`, `is_ipl_type_dump()`, IPL report component/certificate APIs, `enum diag308_subcode`, `diag308()`, `store_status()`, and `lgr_info_log()` are the exposed surface.

Control flow: Boot code parses the IPL parameter block into `ipl_info`, optionally builds OS-info re-IPL data, and kexec/dump paths build IPL reports by adding loaded components and certificates. Re-IPL/reset uses DIAG 308 subcodes against prepared parameter blocks.

State and persistence: Persistent state includes global `ipl_info`, lowcore IPL pointers, `ipl_report` lists, the IPL parameter block page, and OS-info re-IPL data used by later dump or reboot tools.

Dependencies and integration points: It depends on lowcore, CIO device identifiers, setup/parmarea definitions, UAPI IPL block layouts, kexec buffers, and firmware DIAG 308 semantics.

Risks and test signals: Packed layout and length constants must match firmware. Tests should cover CCW/FCP/NVMe/ECKD/NSS boots, dump IPL detection, kexec_file component reports, certificate handling, DIAG 308 store/set/load paths, and reboot after crash dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ipl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/irq.h

Purpose: This header defines s390 architectural IRQ numbers, external interruption codes, per-class IRQ statistics, and external interrupt registration APIs.

Important APIs/types/functions: `EXT_INTERRUPT`, `IO_INTERRUPT`, `THIN_INTERRUPT`, external code constants, `enum interruption_class`, `struct irq_stat`, per-CPU `irq_stat`, `inc_irq_stat()`, `struct ext_code`, `ext_int_handler_t`, `register_external_irq()`, `unregister_external_irq()`, `enum irq_subclass`, and `irq_subclass_register/unregister()` are the main definitions.

Control flow: Low-level interrupt handlers classify external, I/O, thin, NMI, and restart events, increment per-class counters, and dispatch registered external handlers by interruption code. Subclass registration manipulates control-register masks for selected external subclasses.

State and persistence: Per-CPU IRQ counters persist in `irq_stat`; external-handler tables and subclass reference state live in implementation code. The header establishes only the ABI and constants.

Dependencies and integration points: It depends on hardirq/percpu/cache helpers and control-register masks from `ctlreg.h`, integrating with `/proc/interrupts`, timer, service-signal, IUCV, CIO, DASD, QDIO, PCI MSI, and NMI paths.

Risks and test signals: Interrupt code mismatches or unbalanced subclass registration can mask required events globally. Tests should cover external handler register/unregister, interrupt counter reporting, timer/service/IUCV delivery, PCI/CIO IRQs, and CPU hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/irq_work.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/irq_work.h

Purpose: This header tells generic irq_work that s390 can raise an interrupt for queued irq_work.

Important APIs/types/functions: `arch_irq_work_has_interrupt()` always returns true.

Control flow: Generic irq_work code uses this predicate to decide that queued work can be kicked asynchronously instead of relying only on polling or timer fallback.

State and persistence: There is no header-owned state.

Dependencies and integration points: It integrates generic irq_work with the s390 external-interrupt mechanism.

Risks and test signals: If interrupt delivery is broken, irq_work users can stall. Tests include irq_work selftests, scheduler/perf users that queue irq_work from hardirq/NMI-like contexts, and CPU hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/irq_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/irqflags.h

Purpose: This header implements s390 local interrupt flag save, disable, enable, restore, and query primitives.

Important APIs/types/functions: `ARCH_IRQ_ENABLED`, `__arch_local_irq_stosm()`, `__arch_local_irq_stnsm()`, `__arch_local_irq_ssm()`, `arch_local_save_flags()`, `arch_local_irq_save()`, `arch_local_irq_disable()`, `arch_local_irq_enable_external()`, `arch_local_irq_enable()`, `arch_local_irq_restore()`, `arch_irqs_disabled_flags()`, and `arch_irqs_disabled()` are defined.

Control flow: The helpers use `stosm`, `stnsm`, and `ssm` to read and modify the system mask. Save/disable clears external and I/O interrupt enable bits, enable sets external or both external/I/O bits, and restore only transitions from disabled to the saved enabled state.

State and persistence: Persistent state is the current CPU PSW/system-mask interrupt enable bits. Under KMSAN, functions gain noinline/notrace/no-sanitize attributes to avoid instrumentation recursion.

Dependencies and integration points: It depends on Linux types, PSW/system mask semantics, KMSAN configuration, and generic irqflags consumers across scheduler, locking, and MM context switching.

Risks and test signals: Incorrect mask constants can globally enable or suppress interrupts. Tests should cover lockdep IRQ state, nested save/restore, external-only enable users, KMSAN builds, context switch paths, and interrupt delivery after local_irq_enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/isc.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/isc.h

Purpose: This header centralizes s390 I/O interruption subclass assignments so channel, PCI, crypto, and guest drivers avoid collisions.

Important APIs/types/functions: `MAX_ISC`, driver-specific ISC constants (`IO_SCH_ISC`, `CONSOLE_ISC`, `PCI_ISC`, `AP_ISC`, `GAL_ISC`, etc.), and `isc_register()`/`isc_unregister()` are exposed.

Control flow: Drivers register the subclass they use before enabling devices and unregister when the last user goes away. Hardware priorities follow the architecture rule that ISC 0 is highest and 7 is lowest.

State and persistence: Subclass reference counts or masks live in implementation code; constants here define persistent driver policy.

Dependencies and integration points: It integrates CIO, console, EADM, CHSC, VFIO-CCW, QDIO, PCI, GIB alert, and adjunct-processor interrupt routing.

Risks and test signals: Two drivers sharing a subclass unintentionally can affect interrupt priority and masking. Tests should check balanced register/unregister, boot with all driver classes, and interrupt delivery under subclass masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/isc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/itcw.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/itcw.h

Purpose: This header declares helpers for incrementally constructing FCX transport command words and associated DCW/TIDAW data.

Important APIs/types/functions: `ITCW_OP_READ`, `ITCW_OP_WRITE`, opaque `struct itcw`, `itcw_get_tcw()`, `itcw_calc_size()`, `itcw_init()`, `itcw_add_dcw()`, `itcw_add_tidaw()`, `itcw_set_data()`, and `itcw_finalize()` are the public API.

Control flow: A caller calculates buffer size, initializes an ITCW builder for read or write, adds device command words and transport indirect data address words, optionally assigns data, then finalizes the TCW before issuing channel I/O.

State and persistence: State is the caller-provided ITCW buffer containing a TCW and appended DCW/TIDAW structures. The header itself owns no memory.

Dependencies and integration points: It depends on `asm/fcx.h` layouts and integrates with channel subsystem drivers using FCX and TCW-based I/O.

Risks and test signals: Builder bounds and finalization order must match hardware layout. Tests should cover calculated sizes, maximum TIDAW counts, read/write operations, malformed command rejection, and real FCX-capable device I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/itcw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/jump_label.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/jump_label.h

Purpose: This header implements s390 static-key branch sites for Linux jump labels.

Important APIs/types/functions: `HAVE_JUMP_LABEL_BATCH`, `JUMP_LABEL_NOP_SIZE`, compiler-specific `JUMP_LABEL_STATIC_KEY_CONSTRAINT`, `arch_static_branch()`, and `arch_static_branch_jump()` are defined. The branch sites emit `brcl` instructions and `__jump_table` records.

Control flow: For a false-by-default static branch, code emits a distinguishable `brcl 0,label` nop-like instruction; for jump form it emits `brcl 15,label`. Runtime jump-label patching rewrites those sites based on static-key state using the table metadata.

State and persistence: Persistent state is encoded in kernel text and `__jump_table`; static-key counters live in generic jump-label structures.

Dependencies and integration points: It depends on compiler inline-asm constraints, Linux static keys, and s390 text patching/alternatives code. Perf, tracing, KVM, PAI, and other fast paths consume these branches.

Risks and test signals: Instruction size, table relocation, or constraint errors break runtime patching. Tests should include GCC/Clang builds, static-key selftests, toggling features that use jump labels, and objdump validation of six-byte patch sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/jump_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kasan.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/kasan.h

Purpose: This header defines the s390 KASAN shadow address layout when KASAN is enabled.

Important APIs/types/functions: `KASAN_SHADOW_SCALE_SHIFT`, `KASAN_SHADOW_SIZE`, `KASAN_SHADOW_OFFSET`, `KASAN_SHADOW_START`, and `KASAN_SHADOW_END` are defined under `CONFIG_KASAN`.

Control flow: KASAN initialization and address translation use the configured shadow offset and region-size-derived shadow span to map kernel shadow memory.

State and persistence: The header defines address constants only; shadow memory state is allocated and managed by KASAN core and s390 memory setup.

Dependencies and integration points: It depends on page-table region shifts from the s390 MM layout and Linux KASAN configuration.

Risks and test signals: A wrong shadow range can overlap vmalloc/modules or miss instrumented memory. Tests should include KASAN boot, slab/page out-of-bounds detection, vmalloc/module accesses, and randomized-base configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kasan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kdebug.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/kdebug.h

Purpose: This header declares s390 debug die-notifier reason codes and the fatal `die()` entry point.

Important APIs/types/functions: `enum die_val` includes oops, breakpoint, single-step, panic, NMI, trap, GPF, call, and debug reasons; `die(struct pt_regs *, const char *)` is declared noreturn.

Control flow: Trap, probe, NMI, and fault handlers use the enum values when notifying debug infrastructure or terminating execution through `die()`.

State and persistence: No state is stored here; notifier chains and crash/oops state live elsewhere.

Dependencies and integration points: It integrates ptrace register context with oops handling, kprobes, kgdb-like debug paths, panic, and NMI handling.

Risks and test signals: Wrong reason codes reduce diagnostic quality or can confuse notifier consumers. Tests include breakpoint/single-step traps, oops reporting, panic paths, and debug-notifier consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kexec.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/kexec.h

Purpose: This header defines s390 kexec and kdump architecture limits, loader state, relocation hooks, IPL-report integration, and crash-kernel protection hooks.

Important APIs/types/functions: It defines memory limits, `KEXEC_ARCH`, `KEXEC_BUF_MEM_UNKNOWN`, dummy `crash_setup_regs()`, `struct s390_load_data`, `s390_verify_sig()`, `kexec_file_add_components()`, `arch_kexec_do_relocs()`, `struct kimage_arch`, image ops declarations, crash-dump protect/unprotect APIs, and kexec_file relocation/cleanup hooks.

Control flow: The kexec_file loader verifies the kernel, loads segments into memory, tracks parmarea and total segment size, builds IPL report components, applies relocations for purgatory or image sections, and prepares firmware-visible IPL data for the next boot.

State and persistence: Persistent state includes `kimage_arch.ipl_buf`, loaded segment memory, parmarea content, IPL report state, and crashkernel reserved memory protection.

Dependencies and integration points: It depends on processor/page/setup definitions, Linux kexec_file_ops, ELF relocation handling, `ipl.h` reports, purgatory, and crash dump configuration.

Risks and test signals: Address limit mistakes can place control pages outside firmware-reachable memory, and relocation errors can make purgatory fail. Tests should cover kexec_file ELF/image load, signature verification, crashkernel reservation/protection, dump kernel boot, and segment-at-zero support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kfence.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/kfence.h

Purpose: This header provides s390 KFENCE pool setup and guard-page protection hooks.

Important APIs/types/functions: `__kernel_map_pages()`, `arch_kfence_init_pool()`, `arch_kfence_test_address()`, and `kfence_protect_page()` are the relevant interfaces.

Control flow: During KFENCE initialization the pool is forced to 4K mappings with `set_memory_4k()`. Guard pages are protected or unprotected by toggling kernel page mappings for the corresponding page.

State and persistence: Persistent state is KFENCE pool page-table mapping granularity and per-page access permissions; the header holds no counters.

Dependencies and integration points: It integrates Linux KFENCE with s390 set-memory and page mapping operations.

Risks and test signals: Failure to split large mappings or protect guard pages weakens detection. Tests should include KFENCE boot, allocation/free sampling, guard-page fault detection, and configs with huge direct-map mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kfence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kmsan.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/kmsan.h

Purpose: This header provides s390 KMSAN address metadata hooks, especially for lowcore aliases.

Important APIs/types/functions: `is_lowcore_addr()`, `arch_kmsan_get_meta_or_null()`, and `kmsan_virt_addr_valid()` are defined for non-module code.

Control flow: When KMSAN sees a lowcore address, the hook resolves the current CPU prefixed lowcore to its real per-CPU lowcore page before asking generic KMSAN for metadata. Address validity checks disable preemption to avoid scheduler recursion while `pfn_valid()` uses RCU.

State and persistence: State is KMSAN shadow/origin metadata and per-CPU lowcore mappings; the header only redirects lookup behavior.

Dependencies and integration points: It depends on lowcore, KMSAN core, memory-zone validity, preemption controls, and raw CPU IDs.

Risks and test signals: Lowcore alias handling is subtle: returning shared metadata for all lowcores would create false positives or missed reports. Tests should include KMSAN boot, lowcore field accesses, CPU hotplug, module/non-module builds, and invalid virtual address checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kmsan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kprobes.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/kprobes.h

Purpose: This header defines s390 kprobes instruction and per-CPU control-block contracts.

Important APIs/types/functions: `BREAKPOINT_INSTRUCTION`, fixup flags, `probe_is_prohibited_opcode()`, `probe_get_fixup_type()`, `probe_is_insn_relative_long()`, `kprobe_opcode_t`, `MAX_INSN_SIZE`, `MAX_STACK_SIZE`, `struct arch_specific_insn`, `struct prev_kprobe`, `struct kprobe_ctlblk`, `arch_remove_kprobe()`, and `kprobe_fault_handler()` are the public pieces.

Control flow: Kprobes copies the original s390 instruction into an insn slot, replaces the target with the breakpoint instruction, and uses fixup classification to emulate or adjust PSW/register state after single-stepping or trap handling. The per-CPU control block saves probe status, interrupt mask, selected control registers, and nested probe state.

State and persistence: Persistent state includes per-probe copied instructions and per-CPU kprobe control blocks while probes are armed. Instruction slots need no cache flush according to this header.

Dependencies and integration points: It depends on `ctlreg.h`, generic kprobes, ptrace, per-CPU storage, and task stack helpers.

Risks and test signals: Probing prohibited opcodes, relative-long branches, or stack-sensitive code can corrupt execution. Tests should include kprobe and kretprobe selftests, prohibited opcode rejection, relative branch fixups, nested probe faults, and CONFIG_KPROBES=n builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kvm_host.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/kvm_host.h

Purpose: This is the main s390 KVM host header, defining vCPU/VM architectural state, interrupt queues, CPU model data, crypto/AP state, GISA adapter interrupt structures, protected virtualization state, statistics, and SIE entry declarations.

Important APIs/types/functions: Key definitions include KVM limits and requests, `struct kvm_vcpu_stat`, program-interruption constants, pending IRQ enums and masks, `struct kvm_s390_interrupt_info`, local and floating interrupt state, guest-debug state, `struct kvm_vcpu_arch`, `struct kvm_arch`, async page-fault hooks, crypto mask helpers, `__sie64a()`/`sie64a()`, SIE enter/exit declarations, GISC register APIs, protected-guest predicates, and zPCI KVM hooks.

Control flow: A vCPU run path prepares the SIE block and arch state, enters SIE via `sie64a` or `kvm_s390_enter_exit_sie`, handles intercept codes by updating stats and delivering/injecting queued interrupts, and uses request bits to enable/disable IBS, migration, VSIE restart, or prefix refresh. VM-level paths manage floating interrupts, CPU model/facility masks, crypto/AP controls, GISA alert state, protected virtualization imports, and memory-slot/gmap checks.

State and persistence: Persistent state is extensive: per-vCPU SIE pointers, timers, local interrupt bitmaps, debug state, pfault tokens, CPU timer seqcount data, guarded-storage/SKEY flags, protected-vCPU handles, per-VM gmap, adapters, IPTE locks, model facilities, crypto control block, VSIE pages, idle masks, GISA interrupt state, protected VM storage, and zPCI device lists.

Dependencies and integration points: It depends on Linux KVM core, hrtimers, interrupts, seqlocks, PCI, mmu notifiers, s390 SIE layouts from `kvm_host_types.h`, debug, CPU/fpu, ISC, guarded storage, gmap/MMU, AP crypto, and zPCI.

Risks and test signals: This is high-risk virtualization ABI code: IRQ priority masks, SIE state, protected-guest ownership, and facility masks must match hardware and userspace KVM API expectations. Tests should include KVM unit tests, nested/VSIE, protected virtualization, async page faults, SIGP/interruption injection, AP crypto passthrough, zPCI passthrough, migration start/stop, and stats validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kvm_host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kvm_host_types.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/kvm_host_types.h

Purpose: This header defines packed hardware-facing s390 KVM data structures, especially SCA/ESCA/BSCA blocks and the SIE control block layout.

Important APIs/types/functions: It defines CPU slot counts, SIGP control unions, SCA entries and blocks, IPTE control, utility fields, volatile machine-check save data, CR initial masks, SIDA helpers, CPUSTAT bits, `struct kvm_s390_sie_block`, `struct kvm_s390_itdb`, and `struct sie_page`.

Control flow: KVM allocates and fills these structures before entering SIE. Hardware and low-level assembly read/write fields at fixed offsets for CPU state, intercept reasons, guest PSW, timers, control registers, facilities, crypto control, protected-virtualization handles, and interruption data.

State and persistence: State persists in DMA/aligned pages shared between host KVM code, SIE hardware, and assembly. The `sie_page` combines the SIE block, volatile machine-check data, protected-guest GPR save area, and ITDB with reserved padding.

Dependencies and integration points: It depends on atomic types, s390 page/PSW/control-register definitions, and the architecture Principles of Operation layout for SIE/SCA.

Risks and test signals: Offset, packing, or alignment changes can break guest execution silently. Tests should include compile-time offset checks where available, KVM boot/run, machine-check while guest running, ESCA/BSCA CPU-count limits, protected guests, and migration across facility variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kvm_host_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kvm_para.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/kvm_para.h

Purpose: This header implements the s390 guest-side KVM paravirtual hypercall ABI using DIAG 0x500.

Important APIs/types/functions: Macro families generate `__kvm_hypercall0..6()` and `kvm_hypercall0..6()` with register arguments: R1 for hypercall number, R2-R6 for args 1-5, R7 for arg 6, and R2 return. It also defines `kvm_para_available()`, `kvm_arch_para_features()`, `kvm_arch_para_hints()`, and `kvm_check_and_clear_guest_paused()`.

Control flow: A guest hypercall wrapper increments DIAG 0x500 statistics, loads the required registers, executes `diag 2,4,0x500`, and returns the value from R2.

State and persistence: No persistent state is stored here beyond diagnostic counters updated by `diag_stat_inc()`. Feature and hint queries currently report no assigned feature bits.

Dependencies and integration points: It depends on UAPI KVM paravirt definitions and `asm/diag.h`, integrating guest kernel code with KVM hypercall handling.

Risks and test signals: Register constraints and calling convention must match both guest ABI and KVM host decode. Tests should cover each argument count, unavailable/non-KVM behavior assumptions, diag statistics, and hypercall error returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/kvm_para.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/linkage.h

Purpose: This header defines s390 symbol alignment used by assembly linkage macros.

Important APIs/types/functions: `__ALIGN` expands to `.balign CONFIG_FUNCTION_ALIGNMENT, 0x07`, and `__ALIGN_STR` stringifies it.

Control flow: Assembly symbol macros include this alignment so functions begin on the configured boundary and padding bytes are the s390 no-op pattern.

State and persistence: There is no runtime state; it affects object text layout.

Dependencies and integration points: It integrates Linux linkage macros, s390 assembly sources, and function alignment configuration.

Risks and test signals: Wrong alignment or padding can affect alternatives, ftrace, unwind/probe expectations, or performance. Tests are build/objdump checks for assembly functions and boot coverage with non-default function alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/lowcore.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/lowcore.h

Purpose: This header defines the s390 lowcore layout: the per-CPU architected low-address save area used for interrupt old/new PSWs, machine-check data, timers, stacks, current task, ASCEs, and register save areas.

Important APIs/types/functions: `LC_ORDER`, `LC_PAGES`, `LOWCORE_ALT_ADDRESS`, `struct pgm_tdb`, packed/aligned `struct lowcore`, `get_lowcore()`, `lowcore_ptr[]`, `set_prefix()`, and assembler macros `GET_LC`/`STMG_LC` are central.

Control flow: Exception entry and low-level CPU code read and write fixed lowcore offsets for interruption parameters, old/new PSWs, save areas, stack pointers, per-CPU pointers, timers, current task, kernel/user ASCEs, IPL/OS info pointers, machine-check extended save area, and register save areas. `get_lowcore()` uses alternatives to return either address zero or relocated lowcore.

State and persistence: The lowcore is persistent per CPU and architecturally visible through prefixing. Its offsets are part of the low-level ABI with assembly, dump tools, firmware expectations, and KVM/machine-check paths.

Dependencies and integration points: It depends on machine-feature alternatives, ptrace PSW types, control registers, CPU definitions, and assembly alternative infrastructure.

Risks and test signals: Changing field offsets can break interrupts, dumps, restart, or machine-check recovery. Tests should include boot, interrupt delivery, CPU hotplug/prefix changes, lowcore relocation, crash dumps, machine checks, KMSAN lowcore metadata, and objdump/offset validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/lowcore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/maccess.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/maccess.h

Purpose: This header declares real-memory copy helpers used when normal virtual mappings are unavailable or old memory must be read after crash.

Important APIs/types/functions: `MEMCPY_REAL_SIZE`, `MEMCPY_REAL_MASK`, external `__memcpy_real_area`, `memcpy_real_ptep`, `memcpy_real_iter()`, `memcpy_real()`, and crash-dump `copy_oldmem_kernel()` are exposed.

Control flow: Implementation code maps a real physical source through a special PTE-sized window, copies into a destination or iov iterator, and in crash-dump mode reads memory from the old kernel.

State and persistence: Persistent state includes the special memcpy-real mapping area and PTE pointer; per-copy mapping changes are transient.

Dependencies and integration points: It depends on PTE types, iov_iter, crash dump configuration, and low-level memory mapping code.

Risks and test signals: Incorrect real-address mapping can read wrong memory or fault in dump paths. Tests should include `/proc/vmcore` reads, crash dump oldmem copying, page-boundary copies, and invalid physical ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/maccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/machine.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/machine.h

Purpose: This header defines runtime machine-feature bits and efficient predicates for platform capabilities such as relocated lowcore, PCI MIO, SCC, guest TLB support, transactional execution, ESOP, DIAG9C, VM, KVM, and LPAR.

Important APIs/types/functions: `MFEATURE_*` constants, global `machine_features`, bit set/clear/test helpers, alternative-backed `__test_machine_feature_constant()`, generated `machine_has_*()` predicates, and aliases `machine_is_vm/kvm/lpar` are the main APIs.

Control flow: Early machine detection sets feature bits, alternatives can patch constant feature tests, and later code uses predicates to select platform-specific paths.

State and persistence: Persistent state is the global machine feature bitmap and any alternative-patched instruction sites derived from it.

Dependencies and integration points: It depends on Linux bitops and s390 alternative patching, integrating boot environment detection with lowcore, PCI, virtualization, and CPU feature consumers.

Risks and test signals: Feature misdetection sends code down unsupported privileged paths. Tests should cover boot under LPAR, z/VM, KVM, bare-metal-like environments, and alternatives using each feature bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/march.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/march.h

Purpose: This header exposes compile-time machine-architecture level feature macros for s390 builds.

Important APIs/types/functions: `MARCH_HAS_Z10_FEATURES` is always defined, while `MARCH_HAS_Z196_FEATURES` through `MARCH_HAS_Z17_FEATURES` are defined from corresponding Kconfig options outside the decompressor.

Control flow: Architecture code uses these macros to choose instruction sequences or optimized per-CPU atomics at compile time.

State and persistence: There is no runtime state; the macros affect generated code.

Dependencies and integration points: It integrates Kconfig selected march levels with headers such as `percpu.h` and other instruction-selection code.

Risks and test signals: Using instructions above the configured baseline breaks older machines. Tests should include builds for each supported march baseline and boot/runtime checks on compatible emulators or hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/march.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/mem_encrypt.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/mem_encrypt.h

Purpose: This header declares s390 memory encryption/decryption attribute APIs.

Important APIs/types/functions: `set_memory_encrypted(unsigned long vaddr, int numpages)` and `set_memory_decrypted(unsigned long vaddr, int numpages)` are exported for C code.

Control flow: Callers request page attribute transitions over a virtual address range; implementation code updates architecture-specific secure/encrypted state.

State and persistence: State persists in page attributes and protected/secure memory ownership, not in the header.

Dependencies and integration points: It integrates with protected virtualization, DMA sharing, and generic set-memory style code needing encrypted/decrypted transitions.

Risks and test signals: Incorrect transitions can expose protected memory or make shared buffers inaccessible. Tests should cover protected guest memory sharing, DMA bounce/shared pages, error handling, and non-assembler build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/mem_encrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/mmu.h

Purpose: This header defines the s390 `mm_context_t` fields used for address-space control, TLB flushing, guest mappings, protected guest tracking, and COW-sharing policy.

Important APIs/types/functions: `mm_context_t` contains a lock, attached CPU mask, flush counter and flag, gmap list and ASCE, active ASCE and limit, VDSO base, protected-count, and `allow_cow_sharing`. `INIT_MM_CONTEXT` initializes lock and gmap list for `init_mm`.

Control flow: MM creation initializes this context, switch code loads ASCEs from it, TLB flush paths coordinate via counters and CPU masks, and KVM gmap/protected-guest code tracks guest mappings and sharing restrictions.

State and persistence: Persistent state is per-mm and lives for the lifetime of the address space. The `protected_count` and COW-sharing bit directly affect page-table behavior in `pgtable.h` and gmap helpers.

Dependencies and integration points: It depends on cpumasks, errno, exception-table support, and s390 ASCE/page-table code, integrating memory management, KVM, TLB flush, VDSO, and protected virtualization.

Risks and test signals: Incorrect ASCE limits or protected counts can break address translation or secure guest isolation. Tests should include exec/fork, ASCE upgrade, context switch, KVM gmap use, protected guests, and TLB shootdowns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/mmu_context.h

Purpose: This header implements s390 MM context initialization and switch operations, including ASCE setup, lowcore ASCE fields, CPU attach masks, and delayed TLB flush synchronization.

Important APIs/types/functions: `init_new_context()`, `switch_mm_irqs_off()`, `switch_mm()`, `finish_arch_post_lock_switch()`, and `activate_mm()` are the architecture overrides.

Control flow: New contexts initialize locks, gmap state, flush counters, protected/COW flags, determine 3/4/5-level ASCE type from `asce_limit`, build `mm->context.asce`, and initialize the top table. Switch paths update lowcore user ASCE, attach CPU masks, clear CR1/CR7 to invalid ASCEs, wait for pending flushes, lazily flush TLBs, then reload CR1/CR7 according to thread flags.

State and persistence: Persistent state is in `mm->context`, `mm_cpumask`, lowcore `user_asce`/`kernel_asce`, and control registers. The code carefully transitions CR1/CR7 with interrupts disabled.

Dependencies and integration points: It depends on `pgalloc.h`, uaccess, TLB flush, control-register load helpers, ASCE definitions, lowcore, scheduler MM hooks, and KVM context fields.

Risks and test signals: Races in CPU masks or flush counters can leave stale translations active. Tests should cover fork/exec, 3-to-5-level ASCE upgrades, context-switch stress, TLB shootdowns, `TIF_ASCE_PRIMARY`, KVM protected contexts, and CPU hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/module.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/module.h

Purpose: This header defines s390 module-loader architecture state for GOT/PLT management, per-symbol offsets, and optional ftrace hotpatch trampolines.

Important APIs/types/functions: `struct mod_arch_syminfo`, `struct mod_arch_specific`, and `find_section()` are defined. The arch state records GOT/PLT offsets and sizes, symbol-specific initialization, and ftrace trampoline allocation pointers when function tracing is enabled.

Control flow: The module loader scans ELF sections, allocates or initializes GOT/PLT entries per symbol, and reserves/consumes ftrace trampoline slots for module text patching.

State and persistence: Persistent state is attached to each loaded module in `mod_arch_specific` and lives until module unload.

Dependencies and integration points: It depends on generic module ELF types, ftrace hotpatch structures, and s390 relocation code.

Risks and test signals: Incorrect GOT/PLT offsets or ftrace trampoline ranges can break module calls or tracing. Tests should include module load/unload, symbols needing PLT/GOT, ftrace on modules, and missing-section handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/msi.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/msi.h

Purpose: This header adapts generic MSI support for s390 and declares MSI isolation behavior.

Important APIs/types/functions: It includes `asm-generic/msi.h` and defines `arch_is_isolated_msi()` as true with a note about s390 not using irq_domain in the same way as other architectures.

Control flow: Generic MSI code queries the predicate while configuring MSI isolation; s390 reports isolation even though userspace may still trigger MSIs within the same GISA.

State and persistence: There is no local state; MSI routing state lives in zPCI/adapter interrupt code.

Dependencies and integration points: It integrates generic MSI core with s390 zPCI/GISA interrupt behavior.

Risks and test signals: The isolation semantics are weaker than some architectures, so passthrough/security tests must account for same-GISA exposure. Tests should cover MSI allocation, VFIO/zPCI passthrough, interrupt remapping assumptions, and non-irqdomain paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/msi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/nmi.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/nmi.h

Purpose: This header defines s390 machine-check/NMI bit meanings, the machine-check extended save area layout, and machine-check handling entry points.

Important APIs/types/functions: `MCIC_SUBCLASS_MASK`, many `MCCK_CODE_*` bits, `union mci`, `MCESA_*` constants, `struct mcesa`, `nmi_alloc_mcesa_early()`, `nmi_alloc_mcesa()`, `nmi_free_mcesa()`, `s390_handle_mcck()`, and `s390_do_machine_check()` are exposed.

Control flow: Machine-check entry code decodes MCIC bits, uses MCESA storage for vector/guarded-storage state when valid, and dispatches low/high-level handlers with `pt_regs` context.

State and persistence: Persistent state includes per-CPU MCESA allocation referenced from lowcore `mcesad`; individual machine-check status is transient but may be saved for diagnostics.

Dependencies and integration points: It depends on Linux bit definitions, lowcore machine-check fields, ptrace context, vector and guarded-storage state, and KVM guest machine-check paths.

Risks and test signals: Machine-check validity bits determine which saved registers can be trusted; mishandling can corrupt recovery or dump data. Tests are mostly hardware/error-injection oriented: MCESA allocation, simulated machine checks, storage-error reporting, guest-running machine checks, and crash dump validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/nmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/nospec-branch.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/nospec-branch.h

Purpose: This header declares s390 speculative-execution branch mitigation controls and expoline indirect-jump thunk symbols.

Important APIs/types/functions: `nospec_disable`, `nobp`, `nobp_enabled()`, `nospec_init_branches()`, `nospec_auto_detect()`, `nospec_revert()`, `nospec_uses_trampoline()`, and `__s390_indirect_jump_r1..r15()` are the main declarations.

Control flow: Boot mitigation code detects facility support and command-line policy, initializes or reverts indirect branch mitigation sites, and thunk-aware code branches through register-specific expoline symbols when enabled.

State and persistence: Persistent state includes global mitigation flags and patched branch sites in `.s390_indirect_branches`; thunk text symbols persist in kernel/module text.

Dependencies and integration points: It depends on facility bit 82, compiler expoline mode, alternatives/text patching, and assembly macros in `nospec-insn.h`.

Risks and test signals: Mitigation policy must match hardware and compiler-generated call sequences. Tests should include boot with `nobp`/`nospec_disable` variants, facility-present/absent systems, objdump of thunk calls, and speculative mitigation selftests where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/nospec-branch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/nospec-insn.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/nospec-insn.h

Purpose: This assembly header defines expoline thunk generation and branch-site recording macros for s390 indirect branch mitigation.

Important APIs/types/functions: Under `CC_USING_EXPOLINE`, it defines thunk prolog/epilog macros, register decode helpers, `GEN_BR_THUNK`, `BR_EX`, and `BASR_EX`; without expoline it falls back to raw `br`/`basr`.

Control flow: Assembly code uses `BR_EX` or `BASR_EX` for indirect branches. In expoline builds, the macro emits a branch to the register-specific thunk and records the site offset in `.s390_indirect_branches` for later revert/patching.

State and persistence: Persistent state is generated thunk text, optional exported extern thunk symbols, and the `.s390_indirect_branches` metadata section.

Dependencies and integration points: It depends on assembler register syntax, linkage/export macros, DWARF CFI wrappers, compiler expoline configuration, and nospec branch runtime code.

Risks and test signals: Register decode macro errors or missing CFI can break assembly or unwinding. Tests should include assembler builds for all register variants, CONFIG_EXPOLINE_EXTERN on/off, module linkage to thunks, and runtime mitigation toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/nospec-insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/numa.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/numa.h

Purpose: This header exposes s390 NUMA setup only when NUMA is configured.

Important APIs/types/functions: `numa_setup()` is declared under `CONFIG_NUMA`; otherwise an empty inline stub is provided.

Control flow: Boot code calls `numa_setup()` unconditionally, and the stub compiles the call away for non-NUMA kernels.

State and persistence: NUMA topology state is maintained by implementation and generic NUMA core, not this header.

Dependencies and integration points: It integrates s390 topology discovery with Linux NUMA initialization.

Risks and test signals: Stub behavior must keep non-NUMA builds clean while NUMA builds populate nodes correctly. Tests should include NUMA and non-NUMA builds, boot topology, memory policy, and CPU/memory hotplug if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/numa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/os_info.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/os_info.h

Purpose: This header defines the s390 OS-info memory block used to expose crash, re-IPL, KASLR, vmemmap, AMODE31, and image metadata to dump/reboot tooling.

Important APIs/types/functions: `OS_INFO_*` version, magic, entry indexes, `OS_INFO_FLAG_REIPL_CLEAR`, `struct os_info_entry`, `struct os_info`, `os_info_init()`, entry add helpers, `os_info_crashkernel_add()`, `os_info_csum()`, and crash-dump `os_info_old_entry()`/`os_info_old_value()` are exposed.

Control flow: Boot initializes an OS-info block, adds pointer or scalar entries with per-entry checksums, records crashkernel ranges, and crash kernels can query the old block for metadata from the previous kernel.

State and persistence: Persistent state is the packed OS-info block, referenced from lowcore, with checksummed entries and crashkernel address/size fields.

Dependencies and integration points: It depends on Linux uio types, lowcore OS-info pointer conventions, crash dump mode, IPL/re-IPL setup, and KASLR/VM layout producers.

Risks and test signals: Packed layout, magic, version, and checksums are external contracts with dump tools. Tests should include normal boot OS-info population, kdump old-entry reads, checksum validation, KASLR fields, and re-IPL clear flag behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/os_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/page-states.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/page-states.h

Purpose: This header wraps the s390 ESSA instruction for page state transitions used by CMMA and memory-management paths.

Important APIs/types/functions: `ESSA_*` command constants, external `cmma_flag`, `essa()`, `__set_page_state()`, `__set_page_unused()`, `__set_page_stable_dat()`, `__set_page_stable_nodat()`, `__arch_set_page_nodat()`, and `__arch_set_page_dat()` are defined.

Control flow: Callers pass a virtual address and page count; helpers translate to physical page addresses and issue ESSA per page. The CMMA-aware wrappers no-op when CMMA is disabled and choose DAT or NODAT stable commands based on `cmma_flag`.

State and persistence: Persistent state is the hardware page state maintained by ESSA/CMMA. The header itself only reads the global capability/policy flag.

Dependencies and integration points: It depends on `page.h` translation macros and integrates memory freeing/allocation, KVM CMMA, and host/guest page-state tracking.

Risks and test signals: Using the wrong ESSA command can mislead hypervisor page-state accounting. Tests should include CMMA enabled/disabled boot, page free/alloc state transitions, KVM guest memory state, and multi-page ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/page-states.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/page.h

Purpose: This header defines core s390 page constants, hugepage geometry, storage-key helpers, page copy/clear, strict MM type wrappers, physical/virtual translation, KASLR identity mapping, and architecture page allocation hooks.

Important APIs/types/functions: Important definitions include page access-key constants, `HPAGE_*`, hugepage capability macros, `storage_key_init_range()`, `copy_page()`, `pgprot_t/pte_t/pmd_t/pud_t/p4d_t/pgd_t` wrappers and value constructors, `page_set_storage_key()`, `page_get_storage_key()`, `page_reset_referenced()`, `split_pud_page()`, arch page alloc/free hooks, `arch_make_folio_accessible()`, `struct vm_layout`, `kaslr_offset()`, `kaslr_enabled()`, `__pa/__pa32/__va`, PFN/page conversion helpers, `AMODE31_SIZE`, kernel image bounds, and `TEXT_OFFSET`.

Control flow: Memory-management code uses these constants and helpers to create page-table entries, copy or clear pages, manipulate storage keys with SSKE/ISKE/RRBE instructions, translate addresses according to identity/KASLR layout, and validate direct-map addresses.

State and persistence: Persistent state includes storage keys on real pages and global `vm_layout`/KASLR fields. The type wrappers affect compile-time type safety rather than runtime state.

Dependencies and integration points: It depends on VDSO page size definitions, setup/KASLR data, generic memory model/getorder, and s390 storage-key instructions. It feeds nearly every MM, KVM, kexec, and I/O mapping header in this subset.

Risks and test signals: Address translation and storage-key mistakes are system-wide failures. Tests should include boot with/without KASLR and randomized identity base, storage-key operations, hugepage allocation, debug-virtual checks, page copy correctness, and protected/accessible folio paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pai.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/pai.h

Purpose: This header defines Processor Activity Instrumentation support for crypto and NNPA counters and perf context transitions.

Important APIs/types/functions: `struct qpaci_info_block`, `qpaci()`, event number ranges (`PAI_CRYPTO_BASE`, `PAI_NNPA_BASE`, limits), static key `pai_key`, `pai_kernel_enter()`, `pai_kernel_exit()`, and perf-event field accessor macros are exposed.

Control flow: Perf or PMU setup queries counter availability with QPACI. On user-to-kernel transitions, the enter/exit helpers use a static key and lowcore CCD presence to set or clear the kernel-offset bit so crypto counter attribution is adjusted only for user-origin samples.

State and persistence: Persistent state includes lowcore `ccd` and `aicd` designations plus perf event bookkeeping; the static key controls fast-path patching.

Dependencies and integration points: It depends on lowcore, ptrace user-mode checks, perf events, static keys, and s390 QPACI instruction encoding.

Risks and test signals: Incorrect enter/exit filtering can misattribute counters or write CCD in unsupported contexts. Tests should cover perf PAI events, user/kernel transition attribution, static-key disabled overhead, QPACI size/error returns, and CPU hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pai.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/pci.h

Purpose: This is the central s390 zPCI header, defining PCI mapping hooks, zPCI function/bus state, measurement blocks, hotplug/sysfs/IOMMU/DMA/IRQ/debug prototypes, and device helper conversions.

Important APIs/types/functions: It defines PCI min windows, zPCI device/domain constants, function-control bits, FMB formats, `enum zpci_state`, `struct zpci_bar_struct`, `struct zpci_bus`, `struct zpci_dev`, `zdev_enabled()`, sysfs attribute groups, globals such as `zpci_aipb`, and a broad API for create/add/enable/disable/scan/deconfigure/reset, CLP operations, UID checking, firmware sysfs, IOMMU, hotplug, DMA, IRQ/MSI, FMB, debug, and error reporting.

Control flow: Firmware discovery scans CLP-provided functions, creates `zpci_dev` objects, queries function/group attributes, enables functions to obtain handles, registers I/O address translation, maps BAR resources, initializes IOMMU/MSI/debug/hotplug state, and handles availability/error events for recovery or deconfiguration.

State and persistence: Persistent state is large per zPCI function and bus: krefs/RCU/list membership, state locks, firmware IDs/handles, RID/topology/PFIP/UID, BAR mapping pointers, MSI vectors and adapter interrupt bit vectors, DMA table and address limits, IOMMU domain/device, FMB counters, debugfs entries, KVM passthrough pointer, and hotplug slot state.

Dependencies and integration points: It depends on Linux PCI, IOMMU, IRQ domains, hotplug, CLP records, zPCI instruction helpers, SCLP, debug, and KVM zPCI hooks.

Risks and test signals: State transitions must be serialized because firmware handles, DMA windows, MSI routing, and hotplug removal interact. Tests should cover CLP scan, enable/disable/re-enable, BAR mmap/iomap, DMA map/unmap, MSI delivery, FMB counters, hotplug, error recovery, IOMMU attach/detach, and passthrough.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_clp.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_clp.h

Purpose: This header defines packed CLP request/response layouts and constants for s390 PCI firmware discovery and function control.

Important APIs/types/functions: It declares CLP command codes, `struct clp_fh_list_entry`, CLP response codes, list-entry sizing, set-operation controls, utility/PFIP sizes, function type constants, global `zpci_unique_uid`, and packed request/response structures for SLPC, list PCI, query function, query function group, set PCI, and combined request/response blocks.

Control flow: zPCI firmware code issues CLP list commands with resume tokens, queries each function handle for BARs, DMA ranges, RID/topology, utility strings, MIO data, and group capabilities, then enables/disables functions through set-PCI commands.

State and persistence: Persistent state is not stored here, but the packed responses populate `struct zpci_dev` and bus capabilities. Resume tokens and function handles are firmware-visible transient state.

Dependencies and integration points: It depends on `asm/clp.h` and Linux PCI BAR constants, integrating zPCI core with IBM Z CLP firmware.

Risks and test signals: Packed bitfields and byte order must match firmware exactly. Tests should cover list pagination, query of optional MIO/util/RID/TID fields, group capability parsing, response-code error paths, and enable/disable commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_clp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_debug.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_debug.h

Purpose: This header provides zPCI debug-feature logging wrappers.

Important APIs/types/functions: `pci_debug_msg_id`, `pci_debug_err_id`, `zpci_dbg()`, `zpci_err()`, `zpci_err_hex_level()`, and `zpci_err_hex()` are defined.

Control flow: zPCI code writes formatted messages to the normal debug area and text or binary data to the error debug area.

State and persistence: Persistent state is held by `debug_info_t` debug feature instances allocated by zPCI debug initialization.

Dependencies and integration points: It depends on s390 `asm/debug.h` and integrates with zPCI core, error handling, and debugfs/debug feature tooling.

Risks and test signals: The fixed 16-byte text buffer in `zpci_err()` truncates messages, so callers should keep text concise. Tests should cover debug init/exit, message/error logging, hex dumps, and disabled debug feature behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_dma.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_dma.h

Purpose: This header defines s390 zPCI I/O translation anchor and IOMMU page-table encodings plus DMA mapping counters.

Important APIs/types/functions: `enum zpci_ioat_dtype`, IOTA flags and table-size constants, region/segment/page-table type, shift, mask, valid/protection bits, `struct zpci_iommu_ctrs`, and `zpci_get_iommu_ctrs()` are provided.

Control flow: The zPCI IOMMU code builds I/O translation tables using the defined region/segment/page-table hierarchy, encodes the IOTA for firmware registration, and updates counters for mapped/unmapped pages and RPCIT invalidations.

State and persistence: Persistent state is the DMA translation table tree attached to a zPCI device/domain and its atomic counter block.

Dependencies and integration points: It depends on page default storage key definitions and zPCI device structures, integrating DMA API/IOMMU core with zPCI firmware instructions.

Risks and test signals: Bit encoding mistakes can map wrong DMA addresses or fail invalidation. Tests should cover DMA map/unmap for 4K/1M/2G ranges, IOMMU domain attach, RPCIT counter updates, protection bits, and device DMA under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_insn.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_insn.h

Purpose: This header defines zPCI privileged instruction status codes, request encodings, function/interrupt information blocks, and low-level instruction wrappers.

Important APIs/types/functions: It includes status/condition-code constants, address-space identifiers, modify-function controls, FIB control bits, `struct zpci_fib` and format unions, SIC operation controls, directed-interrupt blocks, `union zpci_sic_iib`, static key `have_mio`, and wrappers such as `zpci_mod_fc()`, `zpci_refresh_trans()`, `zpci_load()`, `zpci_store()`, `__zpci_store_block()`, `zpci_barrier()`, and `zpci_set_irq_ctrl()`.

Control flow: zPCI core prepares FIB/SIC blocks, issues modify-function-control instructions, registers IOAT/MSI state, performs load/store/store-block MMIO operations, refreshes translations, and uses barriers for ordering.

State and persistence: Persistent state is in firmware/device function controls, registered interrupt vectors, IOAT state, FMB address, and static MIO capability key; structures here are command blocks passed to instructions.

Dependencies and integration points: It depends on Linux jump labels and integrates with `pci.h`, `pci_io.h`, DMA/IOMMU, MSI, and zPCI firmware/hardware instruction handlers.

Risks and test signals: Instruction status handling must distinguish busy, invalid handle, and function error cases. Tests should cover MMIO loads/stores of all sizes, store-block, MIO on/off, IOAT registration, MSI direct/all modes, translation refresh, and error status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_io.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_io.h

Purpose: This header implements zPCI MMIO cookie decoding and read/write/copy helpers used by `io.h` under `CONFIG_PCI`.

Important APIs/types/functions: It defines max read/write sizes, 4K boundary constraints, virtual iomap cookie layout (`ZPCI_ADDR`, `ZPCI_IDX`, `ZPCI_OFFSET`), `struct zpci_iomap_entry`, `ZPCI_CREATE_REQ`, generated typed reads/writes, `zpci_write_single()`, `zpci_read_single()`, `zpci_write_block()`, `zpci_get_max_io_size()`, `zpci_memcpy_fromio()`, `zpci_memcpy_toio()`, and `zpci_memset_io()`.

Control flow: Mapped PCI BAR addresses are encoded as high virtual cookies. Access helpers decode the cookie into zPCI request fields and split copies into hardware-supported chunks that do not cross 4K boundaries, using store-block for larger aligned writes.

State and persistence: Persistent state is the global iomap table beginning at `zpci_iomap_start`, with reference counts and function/bar identifiers. Copy helpers allocate temporary memory only for memset.

Dependencies and integration points: It depends on zPCI instruction wrappers, slab allocation, and kernel alignment helpers, integrating generic MMIO APIs with zPCI-specific load/store instructions.

Risks and test signals: Boundary and size splitting are critical because zPCI load/store have strict limits. Tests should include every access width, unaligned copies, 4K boundary crossing, NULL memset allocation failure, BAR unmap refcounts, and firmware error returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/percpu.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/percpu.h

Purpose: This header implements optimized s390 per-CPU access and atomic this_cpu operations using lowcore `percpu_offset` and architecture instructions.

Important APIs/types/functions: `__my_cpu_offset`, `arch_raw_cpu_ptr()`, simple compare-and-swap based operations, z196+ load-and-op sequences for 4/8-byte add/and/or, return variants, `arch_this_cpu_cmpxchg()`, `this_cpu_cmpxchg128()`, and `arch_this_cpu_xchg()` are defined before generic percpu inclusion.

Control flow: Per-CPU pointer calculation adds lowcore `percpu_offset` with an alternative for relocated lowcore. Mutating this_cpu operations disable preemption, operate on the raw CPU pointer, and re-enable preemption; newer march levels use atomic load-and-op instructions where available.

State and persistence: Persistent state is the per-CPU data area addressed through lowcore. The operations themselves only modify caller-selected per-CPU variables.

Dependencies and integration points: It depends on preemption control, cmpxchg helpers, march feature macros, lowcore, and alternatives.

Risks and test signals: Missing preemption protection could update the wrong CPU variable after migration, and instruction selection must match march baseline. Tests should include per-CPU selftests, 1/2/4/8/128-bit operations, relocated lowcore, preemptible kernels, and older march builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/percpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/perf_event.h

Purpose: This header provides s390 perf-event definitions for CPU measurement facilities, sample register setup, and architecture-specific perf callbacks.

Important APIs/types/functions: `PMU_F_*` state/error flags, `cpumf_cf_event_group()`, `cpumf_events_sysfs_show()`, event attribute macros, `perf_arch_instruction_pointer()`, `perf_arch_misc_flags()`, `perf_arch_bpf_user_pt_regs`, `struct perf_sf_sde_regs`, and `perf_arch_fetch_caller_regs()` are provided.

Control flow: Perf PMU code exposes counter facility events via sysfs, records instruction pointer/misc flags from pt_regs, and can synthesize caller regs with current frame pointer for sampling.

State and persistence: Persistent state is perf PMU/event state and sysfs attributes; the header defines flags and helpers, not storage.

Dependencies and integration points: It depends on Linux perf events, devices, s390 stacktrace frame layout, and ptrace register formats. It also integrates with PAI and CPU measurement facility drivers.

Risks and test signals: Incorrect sample flags can misclassify guest/user/kernel samples. Tests should include perf list/sysfs events, CPU counter sampling, BPF perf regs access, guest sample indicators, and callchain capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pfault.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/pfault.h

Purpose: This header wraps s390 pseudo-page-fault initialization for optional `CONFIG_PFAULT` support.

Important APIs/types/functions: `__pfault_init()`, `__pfault_fini()`, `pfault_init()`, and `pfault_fini()` are defined; the public wrappers return `-EOPNOTSUPP` or no-op when the feature is disabled.

Control flow: Initialization code calls `pfault_init()` to enable host/hypervisor pseudo-page-fault handling and `pfault_fini()` during teardown.

State and persistence: Persistent state is maintained by the implementation and hypervisor registration, not the header.

Dependencies and integration points: It depends on Linux errno and integrates with s390 virtualization paging notifications and KVM/zVM-style pfault handling.

Risks and test signals: Callers must handle disabled support cleanly. Tests should include CONFIG_PFAULT on/off builds, init/fini idempotence, page-fault notification delivery under virtualization, and fallback on unsupported machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pfault.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/pgalloc.h

Purpose: This header defines s390 page-table allocation/free/populate helpers for CRST and PTE tables, ASCE upgrades, vmemmap mapping allocation, and deferred PTE freeing.

Important APIs/types/functions: `CRST_ALLOC_ORDER`, `crst_table_alloc/free`, `page_table_alloc/free`, `crst_table_init()`, `crst_table_upgrade()`, `check_asce_limit()`, `p4d/pud/pmd/pgd_alloc_one` and free helpers, populate helpers, PTE allocation/free macros, `pte_free_defer()`, `vmem_map_init()`, `vmem_crst_alloc()`, `vmem_pte_alloc()`, `base_asce_alloc()`, and `base_asce_free()` are exposed.

Control flow: MM code allocates CRST tables, initializes them with the correct empty entry for their level, upgrades ASCE limits when a mapping exceeds the current address-space size, populates parent entries with physical table addresses, and frees tables unless the level is folded.

State and persistence: Persistent state is page-table memory owned by an `mm_struct` or vmem/base ASCE mapping. Constructors/destructors update generic page-table accounting/checking metadata.

Dependencies and integration points: It depends on `pgtable.h` folding and entry encodings, Linux MM allocation hooks, page-table constructors, and vmemmap/base ASCE code.

Risks and test signals: Incorrect folded-level handling or ASCE upgrade failure can corrupt address spaces. Tests should cover fork/exit page-table allocation, mmap above current ASCE limit, vmemmap add/remove, THP split/collapse interactions, and page-table-check builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/pgtable.h

Purpose: This is the central s390 page-table header, defining page/segment/region entry encodings, ASCE layout, protection modes, folded table levels, PTE/PMD/PUD manipulation, TLB invalidation instruction wrappers, huge/THP support, swap encodings, vmem mapping hooks, and protected-guest page teardown behavior.

Important APIs/types/functions: It exports kernel page-table globals, direct-map counters, ZERO_PAGE selection, vmalloc/module/KMSAN layout, all hardware/software PTE/RSTE bit definitions, page protection constants, folding predicates, protected-mm and zeropage policy helpers, `cspg()`/`crdte()`, present/none/bad/leaf/query helpers, pte/pmd/pud modify and dirty/young/write helpers, IPTE/IDTE/RDP assembly helpers, `ptep_xchg_*`/`pmdp_xchg_*` declarations, access-flag and clear/flush overrides, THP helpers, swap-entry conversion helpers, vmem map functions, and unmapped-area declarations.

Control flow: Fault and mapping code construct entries from physical pages and protections, update entries with direct or lazy exchange helpers that also perform required TLB invalidation, use RDP for allowed read-only-to-writable protection resets, clear protected secure pages through UV conversion/destroy hooks, and traverse folded 3/4/5-level tables through lockless offset helpers.

State and persistence: Persistent state is every s390 page table, ASCE, direct-map accounting counter, no-execute mask, module/vmalloc layout value, and secure/protected page ownership. Swap entries encode type/offset differently for PTEs and RSTE huge entries, requiring conversion shims.

Dependencies and integration points: It depends on scheduler/MM types, CPU feature checks, page-table check, radix tree, mmap locks, control registers, UV protected-virtualization APIs, `page.h`, `mmu.h`, TLB flush code, hugepage/THP configs, NUMA balancing, soft-dirty, KMSAN, and KVM protected guest state.

Risks and test signals: This is high-risk MM code: bit patterns define present/none/swap semantics used locklessly, and TLB invalidation must happen at modification time on s390. Tests should include page fault/mprotect/munmap stress, fork/exit, GUP-fast bounds, THP and hugetlb, soft-dirty and swap, NUMA balancing, KMSAN vmalloc layout, protected guest memory conversion, page_table_check, and direct-map vmem add/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/physmem_info.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/physmem_info.h

Purpose: This header defines early physical memory detection metadata, reserved ranges, iterators, and source-name helpers for s390 boot memory setup.

Important APIs/types/functions: `enum physmem_info_source`, `struct physmem_range`, `enum reserved_range_type`, `struct reserved_range`, `struct physmem_info`, global `physmem_info`, `add_physmem_online_range()`, `__get_physmem_range()`, usable/online range iterators, `get_physmem_info_source()`, reserved range iterators, `get_physmem_reserved()`, and `AMODE31_START/END` are defined.

Control flow: Early detection records online ranges from SCLP, DIAG, storage limits, or binary search, tracks reserved ranges for decompressor/initrd/vmlinux/AMODE31/IPL report/cert lists/vmem, and later boot code iterates usable or all online ranges to initialize memory.

State and persistence: Persistent boot state is global `physmem_info`, including inline range storage and optional extended storage carved from known memory. Reserved ranges can chain additional nodes by physical addresses converted with `__va()`.

Dependencies and integration points: It depends on page translation helpers and integrates decompressor/boot memory detection, memblock setup, crash dump reservations, AMODE31, IPL report, certificate lists, and vmemmap allocation.

Risks and test signals: Range truncation at `usable`, chained reserved-range address conversion, and overlap handling are critical. Tests should cover each detection source, more than 255 memory ranges, reserved range iteration, usable limit enforcement, and crash/initrd/IPL report reservations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/physmem_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pkey.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/pkey.h

Purpose: This header exposes the in-kernel API for converting s390 key blobs into protected keys through the pkey device driver.

Important APIs/types/functions: `pkey_key2protkey()` is declared along with execution flags `PKEY_XFLAG_NOMEMALLOC` and `PKEY_XFLAG_NOCLEARKEY`.

Control flow: Kernel crypto users pass a key blob and output buffers; the pkey implementation derives a protected key, optionally avoiding allocations or rejecting clear-key tokens according to flags.

State and persistence: Persistent state is in protected-key material produced for callers and any pkey driver/preallocated buffers; the header owns no state.

Dependencies and integration points: It depends on UAPI pkey definitions and integrates with s390 crypto hardware, protected-key ciphers, and callers constrained by crypto allocation rules.

Risks and test signals: Key length/type outputs and no-allocation constraints must be respected to avoid sleeping in crypto paths or accepting insecure clear keys. Tests should cover all supported key blob types, flag combinations, insufficient output buffers, no-memory paths, and crypto driver integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pkey.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pnet.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/pnet.h

Purpose: This header declares lookup of IBM Z physical network identifiers by Linux device and port.

Important APIs/types/functions: `pnet_id_by_dev_port(struct device *dev, unsigned short port, u8 *pnetid)` is the single API.

Control flow: Network or device code passes a device and port number; implementation fills the PNET ID associated with platform topology metadata.

State and persistence: State lives in firmware/device attributes queried by the implementation, not in the header.

Dependencies and integration points: It depends on Linux device model types and integrates network, PCI/CCW devices, and platform PNET ID discovery.

Risks and test signals: Incorrect port mapping can bind networking policy to the wrong physical network. Tests should cover devices with/without PNET IDs, multi-port adapters, error returns, and hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/pnet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/preempt.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/preempt.h

Purpose: This header implements s390 preempt-count handling with the inverted NEED_RESCHED bit folded into lowcore `preempt_count`.

Important APIs/types/functions: `PREEMPT_NEED_RESCHED`, `PREEMPT_ENABLED`, `preempt_count()`, `preempt_count_set()`, need-resched set/clear/test helpers, `__preempt_count_add/sub()`, `__preempt_count_dec_and_test()`, `should_resched()`, idle init stubs, and preempt schedule declarations/dynamic dispatch macros are defined.

Control flow: Fast paths read or update lowcore `preempt_count` directly, using alternatives for relocated lowcore and short immediate atomic instructions when possible. Decrement-and-test returns true when the count reaches the encoded resched-enabled value.

State and persistence: Persistent state is per-CPU lowcore `preempt_count`; dynamic preemption state lives in generic static calls/keys used by declared schedule functions.

Dependencies and integration points: It depends on current/thread info, atomic ops, cmpxchg, march features, lowcore, and scheduler preemption core.

Risks and test signals: The inverted bit convention is subtle: comparisons must mask or preserve it correctly. Tests should include preempt count debugging, voluntary/full/dynamic preemption configs, IRQ/softirq nesting, scheduler selftests, and relocated lowcore builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/preempt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/processor.h

Purpose: This header defines s390 per-CPU processor metadata, thread state, CPU flags, task address layout, PSW helpers, machine-check mask helpers, stack helpers, and low-level CPU instructions.

Important APIs/types/functions: It exposes CIF flags, `struct pcpu`, per-CPU `pcpu_devices`, CPU-flag bit helpers, `get_cpu_id()`, `get_cpu_timer()`, CPU MHz helpers, VDSO/task layout constants, `__stackleak_poison()`, `struct thread_struct`, `INIT_THREAD`, `start_thread()`/`start_thread31()`, register display hooks, guarded-storage hooks, task register macros, stack pointer helpers, `stap()`, `__ecag()`, `psw_set_key()`, PSW load/extract helpers, machine-check save/restore, PSW rewind/forward, `disabled_wait()`, `regs_irqs_disabled()`, and `bpon()`.

Control flow: Scheduler and entry code use lowcore to find per-CPU data, set task PSWs and stacks at exec, account CPU timers, manage guarded storage/runtime instrumentation/FPU state in `thread_struct`, and manipulate PSW masks for wait, machine checks, and branch prediction controls.

State and persistence: Persistent state includes per-CPU `pcpu` objects, thread_struct fields in each task, lowcore stack/current pointers, PSW state, timers, guarded-storage/runtime-instrumentation control blocks, and FPU save areas.

Dependencies and integration points: It depends on cpumasks, linkage, irqflags, instruction-pointer helpers, bitops, FPU types, CPU/page/ptrace/setup/runtime-instr/fault definitions, lowcore, and alternatives.

Risks and test signals: PSW and thread layout mistakes break exec, context switch, signals, or machine-check handling. Tests should include 31/64-bit exec, VDSO placement, stackleak, CPU flag hotplug paths, guarded storage, runtime instrumentation, disabled wait/restart, and register dump paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/ptrace.h

Purpose: This header defines s390 PSW bit encodings, `pt_regs` layout, PER debug structures, ptrace flags, and register accessor helpers.

Important APIs/types/functions: `PIF_*` flags, 32-bit and 64-bit PSW masks, `struct psw_bits`, `psw32_t`, `struct pt_regs`, `struct per_regs`, `struct per_event`, `struct per_struct_kernel`, PER masks, pt_regs flag helpers, `update_cr_regs()`, single/block-step support, `profile_pc`, `user_mode()`, `regs_return_value()`, instruction pointer helpers, register name/offset queries, stack pointer helpers, `regs_get_register()`, kernel stack/argument readers, and `regs_set_return_value()` are exposed.

Control flow: Exception, syscall, tracing, and ptrace code save user-visible registers in `pt_regs`, inspect PSW bits for user/kernel mode and IRQ state, expose registers by offset/name, and use PER structures for branch/store/ifetch/transaction debug events.

State and persistence: Persistent state is on task kernel stacks in `pt_regs` during entry/exit and in per-thread PER debug structures. Flags annotate syscall, adjusted PSW, guest fault, and ftrace-full-reg states.

Dependencies and integration points: It depends on UAPI ptrace layouts, thread info, TPI info, storage-key constants, and generic profiling/ptrace consumers.

Risks and test signals: The `pt_regs` and PSW layouts are ABI-sensitive for signals, ptrace, BPF, perf, ftrace, and KVM. Tests should include ptrace register get/set, syscall tracing, single/block step, PER events, signal frames, ftrace full regs, and BPF/perf register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/purgatory.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/purgatory.h

Purpose: This header declares the s390 kexec purgatory digest verification entry point.

Important APIs/types/functions: `verify_sha256_digest()` is declared when not assembling, alongside generic purgatory definitions.

Control flow: Kexec purgatory code calls the verifier before transferring control to the loaded kernel image.

State and persistence: State is the purgatory image and digest data provided by kexec; the header stores none.

Dependencies and integration points: It depends on Linux purgatory infrastructure and integrates with `kexec.h` loader and relocation code.

Risks and test signals: Digest verification failure must stop booting the new kernel. Tests should include kexec_file loads, tampered image/digest failure, purgatory relocation, and crash-kernel boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/purgatory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/qdio.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/qdio.h

Purpose: This header defines the public s390 QDIO queue layout and driver API used by high-speed channel I/O devices such as qeth, zfcp, and IQDIO.

Important APIs/types/functions: It defines queue limits, qfmt constants, packed/aligned hardware structures (`qdesfmt0`, `qdr`, `qib`, `slibe`, `qaob`, `slib`, `qdio_buffer_element`, `qdio_buffer`, `sl`, `slsb`, `qdio_ssqd_desc`), SBAL/QIB/CHSC flags, `qdio_handler_t`, error flags, cleanup flags, `struct qdio_initialize`, buffer allocation helpers, and lifecycle APIs from `qdio_allocate()` through `qdio_free()` plus queue inspect/add operations and SSQD query.

Control flow: Drivers allocate SBAL buffers, fill `qdio_initialize`, establish queues on a CCW device, activate/start IRQ processing, add buffers to input or output queues, receive callbacks with processed ranges/errors, inspect queues, and shut down/free queues during device removal.

State and persistence: Persistent state is allocated QDIO queue memory, QDR/QIB/SLIB/SL/SLSB/SBAL/QAOB hardware-visible blocks, handler pointers, interruption parameter, and device queue activation state.

Dependencies and integration points: It depends on Linux interrupts, s390 DMA types, CCW devices, CIO definitions, and channel subsystem CHSC/QEBSM capabilities.

Risks and test signals: Packed alignment and buffer counts are hardware contracts; callback ranges and SLSB states must be handled correctly to avoid data loss. Tests should cover qeth/zfcp/IQDIO devices, multi-queue setup, input/output buffer recycling, async QAOB completions, QEBSM/data-div flags, shutdown via halt/clear, and error callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/qdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/runtime-const.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/runtime-const.h

Purpose: This header implements s390 runtime constant patching for pointer loads and shift immediates.

Important APIs/types/functions: `runtime_const_ptr(sym)`, `runtime_const_shift_right_32(val, sym)`, `runtime_const_init(type, sym)`, `__runtime_fixup_32()`, `__runtime_fixup_ptr()`, `__runtime_fixup_shift()`, and `runtime_const_fixup()` are defined.

Control flow: Code emits placeholder instructions and a section containing relative offsets to those instructions. Initialization walks the section for a symbol and patches the immediate fields with the runtime value using `s390_kernel_write()`.

State and persistence: Persistent state is patched kernel text and the runtime metadata sections `runtime_ptr_*` and `runtime_shift_*`.

Dependencies and integration points: It depends on safe kernel text write support from uaccess and is used by code needing runtime-known constants without an extra memory load.

Risks and test signals: Patch offsets and instruction field masks must match the exact generated instructions. Tests should include boot-time fixups, objdump of placeholders, KASLR/runtime symbol values, read-only text write safety, and users of runtime shift constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/runtime-const.h -->
