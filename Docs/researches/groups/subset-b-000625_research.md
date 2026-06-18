# Research: subset-b-000625

Grouped research for Alpha architecture headers, UAPI ABI headers, and core PCI/kernel support files under the Ceph client source mirror. Each section preserves the source path and is wrapped for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mmu_context.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/mmu_context.h

**Purpose:** Defines Alpha MMU context management: address-space-number allocation, PCB reloads, mm switch hooks, lazy-TLB entry, and page-fault declaration. It is the bridge between Linux `mm_struct` context arrays and Alpha PALcode ASNs/TB behavior.

**Important APIs/types/functions:** `__reload_thread`, `EV4_MAX_ASN`, `EV5_MAX_ASN`, `EV6_MAX_ASN`, `MAX_ASN`, `cpu_last_asn`, ASN version masks, `__get_new_mm_context`, `ev5_switch_mm`, `check_mmu_context`, `ev5_activate_mm`, `init_new_context`, and `enter_lazy_tlb`.

**Control flow:** Context switches compare the target mm context version for the current CPU against `cpu_last_asn`; stale versions allocate a new ASN and may flush all user TB entries with `tbiap()` when hardware ASNs wrap. SMP temporarily marks `asn_lock`, defers reloads via `need_new_asn`, and clears the lock in `check_mmu_context` after `alpha_switch_to` returns.

**State and persistence behavior:** Persistent runtime state is per-mm `mm->context[cpu]`, per-CPU or global `last_asn`, `cpu_data[].need_new_asn`, and PCB `asn`/`ptbr`. The file does not persist data to disk, but bad context versioning can expose stale translations across processes.

**Dependencies and integration points:** Depends on Alpha PAL calls (`PAL_swpctx`, `tbiap`, `imb`), `asm/smp.h`, `asm/machvec.h`, `asm/io.h`, Linux scheduler/mm types, and generic mmu hooks. It integrates with context switching in `switch_to.h`, TLB flushing, page fault handling, and process setup.

**Risks:** ASN wrap and SMP races are the key hazards. EV4 ASNs are documented as unreliable, so assumptions must follow configured CPU family. Missing `check_mmu_context` after a switch can leave deferred ASN work pending. `ptbr` setup assumes Alpha kernel virtual-to-physical layout.

**Test signals:** Build Alpha generic and EV5/EV6 configurations, boot SMP and UP kernels, stress fork/exec/context switching, run memory isolation tests across ASID reuse, and exercise TLB-heavy workloads after `flush_tlb_mm` and ASN wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/module.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/module.h

**Purpose:** Adds Alpha-specific module metadata on top of the generic module header. It records the GOT section index needed for Alpha GP-relative relocation handling and declares the small-data section flag.

**Important APIs/types/functions:** `struct mod_arch_specific { unsigned int gotsecindex; }`, `ARCH_SHF_SMALL`, and the module-only inline assembly that creates an aligned `.got` section.

**Control flow:** There is no runtime control flow in the header. Module loading code consumes `mod_arch_specific` while resolving module sections and Alpha relocations; the `MODULE` preprocessor branch emits the GOT section at compile time.

**State and persistence behavior:** The state is loader-visible module metadata, not persistent storage. `gotsecindex` persists only for the lifetime of a loaded module.

**Dependencies and integration points:** Depends on `asm-generic/module.h`, ELF section flags such as `SHF_ALPHA_GPREL`, and the Alpha module loader implementation.

**Risks:** Relocation failures or missing GOT section setup can break loadable modules that use GP-relative addressing. ABI drift in `mod_arch_specific` affects module loader expectations.

**Test signals:** Build and load Alpha kernel modules with GP-relative data, inspect section layout for `.got`, and compile both built-in and `MODULE` configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/page.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/page.h

**Purpose:** Defines Alpha page primitives, strict page-table wrapper types, the kernel direct-map offset, and virtual/physical translation helpers. It anchors the architecture's 8 KiB page assumptions through `vdso/page.h`.

**Important APIs/types/functions:** `clear_page`, `copy_page`, `copy_user_page`, `pte_t`, `pmd_t`, `pgd_t`, `pgprot_t`, `pgtable_t`, `PAGE_OFFSET`, `__pa`, `__va`, `virt_to_page`, and `virt_addr_valid`.

**Control flow:** Most behavior is macro expansion. Callers convert between kernel virtual and physical addresses by adding/subtracting `PAGE_OFFSET`; copy/clear operations delegate to assembly routines.

**State and persistence behavior:** The file stores no mutable state. Its constants define address interpretation for every memory-management user, core-file helper, boot layout, and page-table routine.

**Dependencies and integration points:** Depends on `asm/pal.h`, `vdso/page.h`, generic memory model helpers, and Linux page allocator interfaces.

**Risks:** Wrong `PAGE_OFFSET` selection for 48-bit KSEG versus legacy layouts corrupts all address translation. Strict type wrappers catch some PTE/PMD/PGD mixups, while non-strict builds lose that safety.

**Test signals:** Compile with and without strict MM type checks, boot kernels using both KSEG choices, and run page allocator, high-memory, and virt-to-phys validation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pal.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/pal.h

**Purpose:** Wraps Alpha PALcode operations used by the kernel: halt, instruction barriers, drain, TLB invalidation, context switching, interrupt priority, user stack pointer, FP enable, performance monitor writes, and machine-check status.

**Important APIs/types/functions:** `__halt`, `imb`, `draina`, PAL call wrapper macros, `tbi`, `tbisi`, `tbisd`, `tbis`, `tbiap`, `tbia`, and inline helpers such as `rdmces`, `wrmces`, `wrusp`, `rdusp`, `swpipl`, `rdps`, `wrent`, `wrkgp`, `wrvptptr`, and `wrfen`.

**Control flow:** Inline assembly binds PAL call arguments to Alpha calling registers and invokes `call_pal`. TBI helpers encode specific invalidation modes and optional address operands.

**State and persistence behavior:** PAL calls mutate CPU-local privileged state, TB state, interrupt priority, unique/user pointers, FP enable, and machine-check state. Nothing is file-persistent.

**Dependencies and integration points:** Depends on UAPI PAL number definitions and Alpha compiler/register conventions. Used by MMU context, TLB flush, SMP, thread switching, signal/ptrace, machine-check, and shutdown paths.

**Risks:** Register constraints and clobber lists are architecture-critical. Wrong PAL number or argument placement can corrupt CPU state. Some calls have ordering requirements with `mb`, `imb`, and `draina`.

**Test signals:** Alpha boot smoke tests, PAL-assisted TLB flush tests, machine-check recovery paths, signal/user-stack pointer tests, FP enable paths, and shutdown/halt validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/parport.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/parport.h

**Purpose:** Provides the Alpha hook used by `drivers/parport/parport_pc.c` to discover PC-style non-PCI parallel ports.

**Important APIs/types/functions:** `parport_pc_find_nonpci_ports(autoirq, autodma)` and the static declaration for `parport_pc_find_isa_ports`.

**Control flow:** The non-PCI discovery function simply delegates to ISA port probing with the caller's IRQ/DMA autodetection flags.

**State and persistence behavior:** No local state. The parport driver owns any registered port state.

**Dependencies and integration points:** Integrated only with `parport_pc.c` and ISA-style I/O probing on Alpha systems.

**Risks:** The header is intended for one driver include path; broader inclusion would expose static prototypes in surprising scopes. Incorrect ISA probing can touch legacy I/O ranges.

**Test signals:** Build with parallel-port support, boot on systems with and without ISA parports, and verify autodetected IRQ/DMA settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/parport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pci.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/pci.h

**Purpose:** Declares Alpha's PCI controller abstraction and legacy PCI interfaces. It represents multi-hose systems, dense/sparse I/O windows, DMA arenas, and domain numbering.

**Important APIs/types/functions:** `struct pci_controller`, `pcibios_assign_all_busses`, `PCIBIOS_MIN_IO`, `PCIBIOS_MIN_MEM`, `pci_domain_nr`, `pci_proc_domain`, IOBASE constants, `isa_bridge`, and legacy read/write/mmap helpers.

**Control flow:** PCI core code obtains per-bus hose data from `bus->sysdata`, derives PCI domains from `hose->index`, and uses machine-vector minimum I/O and memory addresses for resource assignment.

**State and persistence behavior:** Each hose carries resource pointers, sparse/dense base addresses, config-space base, optional SG arenas, a linked-list node, index, and system-specific private data. This state lives for the booted kernel.

**Dependencies and integration points:** Depends on Linux PCI, DMA, scatterlist, spinlock, and `asm/machvec.h`. Populated by Alpha core-logic files and consumed by generic PCI enumeration, sysfs, legacy mmap, and DMA mapping.

**Risks:** Bad hose ranges or domain numbering can break resource allocation on multi-controller systems. Dense/sparse base mistakes expose wrong physical I/O windows to user space and drivers.

**Test signals:** Boot PCI enumeration on single-hose and multi-hose Alpha machines, verify `/proc/bus/pci` domain behavior, legacy I/O mmap, DMA arena setup, and resource assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/percpu.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/percpu.h

**Purpose:** Documents and selects the Alpha per-CPU implementation. Alpha module GP-relative addressing cannot reach kernel per-CPU offsets above 4 GiB, so module per-CPU variables require weak definitions.

**Important APIs/types/functions:** Includes `asm-generic/percpu.h`; architecture behavior is tied to `CONFIG_ARCH_MODULE_NEEDS_WEAK_PER_CPU`.

**Control flow:** No runtime flow. Compile-time configuration changes symbol emission and relocation strategy for module per-CPU variables.

**State and persistence behavior:** Per-CPU state is owned by generic per-CPU infrastructure; this header only constrains module linkage.

**Dependencies and integration points:** Depends on Alpha GCC GP-relative addressing rules, module relocation, and generic per-CPU helpers.

**Risks:** If the Kconfig flag is removed or ignored, module per-CPU references can overflow 32-bit GP displacements.

**Test signals:** Build and load modules declaring per-CPU variables; inspect relocations and run SMP module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/percpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/perf_event.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/perf_event.h

**Purpose:** Acts as the Alpha architecture perf-event header placeholder. It satisfies generic include expectations without declaring extra Alpha perf interfaces here.

**Important APIs/types/functions:** Only the include guard is present.

**Control flow:** No runtime or compile-time behavior beyond preventing missing-header failures.

**State and persistence behavior:** No state.

**Dependencies and integration points:** Included by generic perf-event code when Alpha perf support is configured elsewhere.

**Risks:** Adding declarations here without matching implementation can break perf builds; leaving it empty means callers must not assume architecture-specific perf helpers.

**Test signals:** Build with `CONFIG_PERF_EVENTS` and run perf compile/smoke tests on Alpha.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pgalloc.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/pgalloc.h

**Purpose:** Defines Alpha page-table population helpers and declares `pgd_alloc`. It wires allocated PTE/PMD pages into Alpha's three-level page-table encoding.

**Important APIs/types/functions:** `pmd_populate`, `pmd_populate_kernel`, `pud_populate`, and `pgd_alloc`.

**Control flow:** MM code allocates lower-level tables through generic helpers, then these functions encode physical or kernel virtual table addresses with `pmd_set`/`pud_set`.

**State and persistence behavior:** No independent state; it mutates page-table entries inside an `mm_struct`.

**Dependencies and integration points:** Depends on `asm-generic/pgalloc.h`, `asm/pgtable.h` helpers, page allocator descriptors, and Linux `mm_struct`.

**Risks:** Using the user versus kernel populate variant incorrectly changes whether `page_to_pa()+PAGE_OFFSET` or a direct pointer is encoded. Bad encoding breaks page-table walks.

**Test signals:** Run fork/exec/mmap/page-fault tests, page-table debug checks, and kernel mapping tests on Alpha builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pgtable.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/pgtable.h

**Purpose:** Defines Alpha page-table layout, protection bits, PTE/PMD/PUD transformations, swap-PTE encoding, TLB-update hooks, and vmalloc ranges.

**Important APIs/types/functions:** `set_pte`, `PMD_SHIFT`, `PGDIR_SHIFT`, pointer counts, `VMALLOC_START/END`, `_PAGE_*` flags, `PAGE_*` protections, `pgprot_modify`, `pfn_pte`, `pte_modify`, `pmd_set`, `pud_set`, `pmd_offset`, `pte_offset_kernel`, compaction helpers `ptep_get_and_clear`/`ptep_clear_flush`, swap helpers, and `paging_init`.

**Control flow:** Page fault and mmap code construct PTEs from PFNs plus protection bits, walk PUD/PMD/PTE levels with Alpha-specific address shifts, and use explicit read barriers for dependent page-table loads because Alpha can reorder them. Compaction clear paths flush migrated pages through `migrate_flush_tlb_page`.

**State and persistence behavior:** State is the live page table tree, swap PTE markers, software dirty/accessed bits, and protection flags. The file persists ABI-like layout for core dumps, memory management, and user mappings.

**Dependencies and integration points:** Depends on generic nopud handling, page definitions, processor `TASK_SIZE`, machine-vector layout, setup constants, page table check, and TLB/migration code.

**Risks:** Dirty/accessed bits are partly software conventions. `PHYS_TWIDDLE` exists for legacy X server KSEG-address quirks and can be dangerous if physical address assumptions change. Missing Alpha barriers in page-table walks can expose uninitialized page tables on SMP.

**Test signals:** Run mm selftests, swap/COW/mprotect/exec tests, compaction/migration tests, vmalloc/ioremap tests, and Alpha SMP stress with page-table debug enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/processor.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/processor.h

**Purpose:** Defines Alpha user address-space limits, stack tops, thread structure shell, start-thread entry point, stack inspection helpers, and prefetch primitives.

**Important APIs/types/functions:** `TASK_SIZE`, `STACK_TOP`, `STACK_TOP_MAX`, `TASK_UNMAPPED_BASE`, `struct thread_struct`, `INIT_THREAD`, `start_thread`, `__get_wchan`, `KSTK_EIP`, `KSTK_ESP`, `cpu_relax`, `prefetch`, and `prefetchw`.

**Control flow:** Exec and signal code initialize user register state through `start_thread`; scheduler/debug code reads saved PC/SP from `pt_regs`; prefetch helpers emit Alpha prefetch instructions.

**State and persistence behavior:** Alpha keeps almost no C-level `thread_struct` state here; key task state lives in `thread_info` and PAL PCB fields.

**Dependencies and integration points:** Depends on `ptrace` register layout, task stacks, scheduler code, and Alpha assembler instructions.

**Risks:** Address constants are ABI-sensitive. Wrong `KSTK_ESP` indexing into `pt_regs` breaks proc/debug output and stack unwinding.

**Test signals:** Exec, ptrace, core dump, proc stack reporting, and scheduler tests; compile tests for prefetch intrinsics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/ptrace.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/ptrace.h

**Purpose:** Connects UAPI Alpha register frames to kernel ptrace and syscall helpers. It defines user-mode tests, register accessors, and task/current `pt_regs` placement.

**Important APIs/types/functions:** `arch_has_single_step`, `user_mode`, `instruction_pointer`, `profile_pc`, `current_user_stack_pointer`, `task_pt_regs`, `current_pt_regs`, `force_successful_syscall_return`, and `regs_return_value`.

**Control flow:** Exception, signal, audit, and ptrace code locate the saved register frame at the top of the two-page kernel stack and inspect or modify PC, PS, SP, and syscall return registers.

**State and persistence behavior:** No local state; it interprets per-task stack-resident `pt_regs` and PAL `rdusp` state.

**Dependencies and integration points:** Depends on UAPI `struct pt_regs`, `thread_info` stack size, PAL user stack pointer access, and scheduler task stack helpers.

**Risks:** The top-of-stack arithmetic must match `THREAD_SIZE`. Misclassifying `ps` user-mode bit can send kernel faults down user paths.

**Test signals:** Ptrace single-step/register tests, signal delivery return value tests, syscall tracing, and stack-size build validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/rwonce.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/rwonce.h

**Purpose:** Overrides `READ_ONCE` on Alpha SMP to include a full memory barrier after volatile loads, covering Alpha implementations that can reorder address-dependent loads.

**Important APIs/types/functions:** `__READ_ONCE(x)` under `CONFIG_SMP`, then generic `rwonce` definitions.

**Control flow:** On SMP, `READ_ONCE` expands to a volatile scalar load followed by `mb()` before returning the value; UP builds use generic behavior.

**State and persistence behavior:** No state; it defines memory-ordering semantics used throughout the kernel.

**Dependencies and integration points:** Depends on `asm/barrier.h`, generic `rwonce`, and Alpha's memory model.

**Risks:** Removing the barrier can break RCU and lockless algorithms that rely on address dependencies on other architectures. Overuse costs performance but preserves correctness.

**Test signals:** RCU torture, LKMM litmus tests for Alpha, lockless list/hash tests, and SMP stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/rwonce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/seccomp.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/seccomp.h

**Purpose:** Defines Alpha's native seccomp audit architecture identity and syscall count for generic seccomp filtering.

**Important APIs/types/functions:** `SECCOMP_ARCH_NATIVE`, `SECCOMP_ARCH_NATIVE_NR`, and `SECCOMP_ARCH_NATIVE_NAME`.

**Control flow:** Generic seccomp code compares filter architecture tokens against `AUDIT_ARCH_ALPHA` and bounds syscall numbers by `NR_syscalls`.

**State and persistence behavior:** No local state. Seccomp state is per-task in generic code.

**Dependencies and integration points:** Depends on Alpha `unistd.h`, generic seccomp, and Linux audit UAPI.

**Risks:** Wrong audit architecture lets filters match the wrong ABI or reject valid Alpha tasks. Syscall-count drift can affect validation.

**Test signals:** Run seccomp BPF tests for allowed/denied Alpha syscalls and audit-arch mismatch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/serial.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/serial.h

**Purpose:** Defines default 8250 serial port baud base, flags, and standard COM port table for Alpha PC-style UARTs.

**Important APIs/types/functions:** `BASE_BAUD`, `STD_COM_FLAGS`, `STD_COM4_FLAGS`, and `SERIAL_PORT_DFNS` for ttyS0-ttyS3.

**Control flow:** The 8250 serial driver consumes the macro table at initialization to register legacy ports and optionally detect IRQs.

**State and persistence behavior:** No local state; registered UART state is owned by serial core.

**Dependencies and integration points:** Depends on `CONFIG_SERIAL_8250_DETECT_IRQ` and 8250 port flag definitions.

**Risks:** Legacy I/O addresses and IRQs may collide with platform quirks; COM4 deliberately skips `UPF_SKIP_TEST` due to the 8514 problem.

**Test signals:** Boot with serial console, verify ttyS0-ttyS3 registration, IRQ autodetection, and no false COM4 conflict.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/setup.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/setup.h

**Purpose:** Defines Alpha boot-time physical layout, kernel start addresses, initial page-table pages, command-line/initrd handoff locations, and bootstrap constants.

**Important APIs/types/functions:** `BOOT_PCB`, `BOOT_ADDR`, `BOOT_SIZE`, `KERNEL_START_PHYS`, `KERNEL_START`, `SWAPPER_PGD`, `INIT_STACK`, `EMPTY_PGT`, `EMPTY_PGE`, `ZERO_PGE`, `START_ADDR`, `PARAM`, `COMMAND_LINE`, `INITRD_START`, and `INITRD_SIZE`.

**Control flow:** Early boot and linker/setup code use fixed offsets from `PAGE_OFFSET + KERNEL_START_PHYS`; after VM init the zero page is reclaimed, so command line and initrd values must be copied out.

**State and persistence behavior:** Defines boot memory contract rather than mutable state. Command line and initrd values originate from the secondary bootstrap loader.

**Dependencies and integration points:** Depends on `uapi/asm/setup.h`, page constants, `CONFIG_ALPHA_LEGACY_START_ADDRESS`, MILO/SRM boot conventions, and early MM setup.

**Risks:** Wrong start address breaks older bootloaders or large systems like Wildfire/Titan/Marvel. Zero-page handoff data must be consumed before reclaim.

**Test signals:** Boot with legacy and modern start-address configs, pass command-line/initrd, and validate early page-table addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/sfp-machine.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/sfp-machine.h

**Purpose:** Supplies Alpha machine parameters for the kernel's soft-float library: word size, multiplication/division meat macros, NaN selection, rounding modes, and exception flags.

**Important APIs/types/functions:** `_FP_W_TYPE_SIZE`, `_FP_W_TYPE`, `_FP_MUL_MEAT_*`, `_FP_DIV_MEAT_*`, `_FP_NANFRAC_*`, `_FP_CHOOSENAN`, `FP_ROUNDMODE`, `FP_RND_*`, `FP_EX_*`, `FP_DENORM_ZERO`, and `FP_INHIBIT_RESULTS`.

**Control flow:** Soft-float operations include this header so generic `soft-fp` code expands arithmetic with Alpha word width, FPCR rounding fields, and IEEE software-control flags.

**State and persistence behavior:** No local state; it reads caller-provided `mode` and `swcr` variables and maps exceptions to Alpha IEEE control bits.

**Dependencies and integration points:** Depends on Alpha FPU UAPI flags and generic soft-fp macros from the imported library.

**Risks:** NaN and rounding behavior are ABI-visible for emulated FP traps. The comment notes Alpha preference for NaN operands; changing it can alter numeric results.

**Test signals:** Soft-float exception/rounding tests, FP trap emulation, NaN propagation, denormal handling, and cross-checks against hardware FP where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/sfp-machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/shmparam.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/shmparam.h

**Purpose:** Defines Alpha SysV shared-memory low-boundary alignment.

**Important APIs/types/functions:** `SHMLBA` equal to `PAGE_SIZE`.

**Control flow:** Generic SysV SHM code uses `SHMLBA` when validating/rounding attach addresses.

**State and persistence behavior:** No state.

**Dependencies and integration points:** Depends on page size definitions and generic IPC memory code.

**Risks:** Changing alignment would affect userspace ABI for `shmat` address placement.

**Test signals:** SysV shared memory attach tests for aligned and unaligned addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/shmparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/signal.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/signal.h

**Purpose:** Defines kernel-side Alpha signal set sizing and OSF-compatible signal action structures while importing UAPI signal numbers.

**Important APIs/types/functions:** `_NSIG`, `_NSIG_BPW`, `_NSIG_WORDS`, `old_sigset_t`, kernel `sigset_t`, `struct osf_sigaction`, `__ARCH_HAS_KA_RESTORER`, and `asm/sigcontext.h` inclusion.

**Control flow:** Signal delivery and compat OSF syscall paths use these layouts to copy masks/actions and build restorer-aware frames.

**State and persistence behavior:** Per-task signal state is generic; this file defines the Alpha binary layout for masks and legacy OSF actions.

**Dependencies and integration points:** Depends on UAPI signal definitions, `sigcontext`, and generic signal core.

**Risks:** Kernel `_NSIG=64` differs from UAPI `NSIG=32`; libc and kernel must agree on exposed behavior. Layout changes break signal ABI.

**Test signals:** Signal mask/action tests, legacy OSF signal syscalls, restorer frame validation, and real-time signal boundary checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/smp.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/smp.h

**Purpose:** Defines Alpha SMP CPU identity helpers, per-CPU `cpuinfo_alpha`, IPI hooks, and raw CPU-number access.

**Important APIs/types/functions:** `__hard_smp_processor_id`, `hard_smp_processor_id`, `raw_smp_processor_id`, `struct cpuinfo_alpha`, `cpu_data`, `smp_num_cpus`, call-function IPI hooks, and `NO_PROC_ID`.

**Control flow:** The hard CPU id comes from `PAL_whami`; scheduler and low-level code use `current_thread_info()->cpu` for raw logical CPU id. SMP builds store ASN, machine-check, profiling, and IPI counters in cacheline-aligned `cpu_data`.

**State and persistence behavior:** Persistent per-CPU runtime state includes last ASN, ASN locks, IPI counts, profiling counters, and machine-check flags.

**Dependencies and integration points:** Depends on PAL calls, cpumasks, IRQ headers, thread_info, and generic SMP call-function code.

**Risks:** The Cabrio WHAMI comment signals platform quirks. Incorrect CPU id mapping breaks per-CPU state, ASN tracking, and IPI targeting.

**Test signals:** SMP boot, CPU hotplug where supported, IPI tests, per-CPU ASN stress, and machine-check flag handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/socket.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/socket.h

**Purpose:** Imports Alpha socket UAPI and fixes the nonblocking socket type flag to avoid conflict with Alpha `O_NONBLOCK` bits.

**Important APIs/types/functions:** `SOCK_NONBLOCK` set to `0x40000000`.

**Control flow:** Socket creation flag validation uses this architecture-specific value when translating userspace `SOCK_NONBLOCK` into file flags.

**State and persistence behavior:** No local state.

**Dependencies and integration points:** Depends on UAPI socket constants and generic socket code.

**Risks:** Using the generic `SOCK_NONBLOCK` value would collide with Alpha file flag bits and misinterpret socket types.

**Test signals:** Create sockets with `SOCK_NONBLOCK`, verify nonblocking behavior and no type-bit corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/sparsemem.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/sparsemem.h

**Purpose:** Defines sparsemem section sizing and maximum physical address width for Alpha.

**Important APIs/types/functions:** `SECTION_SIZE_BITS` as 27 and `MAX_PHYSMEM_BITS` as 48 under `CONFIG_SPARSEMEM`.

**Control flow:** Memory initialization uses these constants to divide physical memory into sparse sections and bound PFNs.

**State and persistence behavior:** No mutable state; constants shape memmap allocation and section lookup.

**Dependencies and integration points:** Depends on `CONFIG_SPARSEMEM` and Alpha architecture maximum physical-address limits.

**Risks:** Wrong section size wastes memory or breaks section indexing; wrong max bits can reject valid memory or overrun arrays.

**Test signals:** Sparsemem boot tests across low/high memory layouts and memory hotplug compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/sparsemem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/special_insns.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/special_insns.h

**Purpose:** Wraps Alpha special instructions for implementation version and architectural mask probing.

**Important APIs/types/functions:** `enum implver_enum`, `implver()`, `enum amask_enum`, and `amask(mask)`.

**Control flow:** Generic kernels emit `implver` at runtime; CPU-specific builds fold it to constants. `amask` returns unsupported feature bits for the supplied mask.

**State and persistence behavior:** No state; it reads CPU architectural feature state.

**Dependencies and integration points:** Depends on Alpha assembler support and config options such as `CONFIG_ALPHA_GENERIC`, `CONFIG_ALPHA_EV56`, and `CONFIG_ALPHA_EV6`.

**Risks:** Compile-time constant folding must match the actual CPU target. Misinterpreting `amask` can enable unsupported instructions.

**Test signals:** Boot generic and CPU-specific kernels, compare detected features with `/proc/cpuinfo`, and run instruction-alternative paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/special_insns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/spinlock.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/spinlock.h

**Purpose:** Implements Alpha raw spinlock and rwlock operations using load-locked/store-conditional loops and memory barriers.

**Important APIs/types/functions:** `arch_spin_is_locked`, `arch_spin_value_unlocked`, `arch_spin_unlock`, `arch_spin_lock`, `arch_spin_trylock`, `arch_read_lock`, `arch_write_lock`, `arch_read_trylock`, `arch_write_trylock`, `arch_read_unlock`, and `arch_write_unlock`.

**Control flow:** Spin lock acquisition loops with `ldl_l`/`stl_c`, writes owner-like nonzero values, calls `cpu_relax`, and uses `smp_mb`/`mb` to enforce lock ordering. RW locks count readers and use a negative writer marker.

**State and persistence behavior:** State is the volatile `lock` word inside `arch_spinlock_t` or `arch_rwlock_t`; no other persistence.

**Dependencies and integration points:** Depends on Alpha barriers, current task pointer for debug-like lock values, processor relax, and generic raw spinlock wrappers.

**Risks:** Alpha's weak memory model makes barrier placement critical. LL/SC loops can livelock under heavy contention if relax/order assumptions are wrong. RW lock count overflow is theoretically possible under misuse.

**Test signals:** Lock torture, SMP stress, lockdep builds, rwlock reader/writer fairness tests, and interrupt-context locking tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/spinlock_types.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/spinlock_types.h

**Purpose:** Defines Alpha raw spinlock and rwlock storage types for the generic spinlock layer.

**Important APIs/types/functions:** `arch_spinlock_t`, `__ARCH_SPIN_LOCK_UNLOCKED`, `arch_rwlock_t`, and `__ARCH_RW_LOCK_UNLOCKED`.

**Control flow:** No runtime flow; generic spinlock code instantiates these volatile words and uses operations from `spinlock.h`.

**State and persistence behavior:** The lock word is the entire lock state.

**Dependencies and integration points:** Must be included through `linux/spinlock_types_raw.h`; depends on generic raw spinlock layering.

**Risks:** Direct inclusion is rejected. Layout changes affect every raw lock object and module ABI assumptions.

**Test signals:** Compile raw spinlock users, run lockdep/locking selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/string.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/string.h

**Purpose:** Declares Alpha-optimized string/memory routines and maps selected operations to compiler builtins or architecture-specific implementations.

**Important APIs/types/functions:** `memcpy`, `memmove`, `__memcpy`, `__constant_c_memset`, `___memset`, inline `__memset`, `memset`, string routines, `memchr`, `__memset16`, and `memset16`.

**Control flow:** Constant `memset` calls either expand to compiler builtins for constant sizes or to Alpha constant-byte fill helpers; non-constant values call assembly/C implementations. `memset16` uses constant replicated 16-bit patterns where possible.

**State and persistence behavior:** No state; mutates caller-provided memory.

**Dependencies and integration points:** Depends on kernel builds, GCC builtin behavior, Alpha string assembly implementations, and framebuffer/VGA users of `memset16`.

**Risks:** The header deliberately avoids recursive builtin expansion issues in old GCC. Incorrect constant folding can choose the wrong byte pattern or alignment behavior.

**Test signals:** KUnit/lib string tests, boot memory tests, framebuffer text console tests, and module compatibility for `__memcpy`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/switch_to.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/switch_to.h

**Purpose:** Defines Alpha's task switch macro around the low-level `alpha_switch_to` routine and MMU context post-switch check.

**Important APIs/types/functions:** `alpha_switch_to` declaration and `switch_to(P,N,L)` macro.

**Control flow:** The macro passes the physical address of the next task's PCB to PAL-aware switch code, stores the returned previous task in `L`, then runs `check_mmu_context` to finish deferred ASN work.

**State and persistence behavior:** Mutates CPU current task, PCB state, and MMU context side effects. No file-persistent state.

**Dependencies and integration points:** Depends on `task_thread_info`, `virt_to_phys`, `mmu_context.h`, and low-level assembly switch code.

**Risks:** Skipping `check_mmu_context` would leave SMP ASN locks/deferred reloads unresolved. Wrong PCB physical address corrupts context switch state.

**Test signals:** Scheduler stress, SMP context-switch tests, fork/exec workloads, and MMU context validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/syscall.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/syscall.h

**Purpose:** Provides generic syscall tracing/audit helpers for Alpha: syscall architecture, number, arguments, return values, and rollback.

**Important APIs/types/functions:** `syscall_get_arch`, `syscall_get_return_value`, `syscall_get_nr`, `syscall_set_nr`, `syscall_get_arguments`, `syscall_set_arguments`, `syscall_set_return_value`, and `syscall_rollback`.

**Control flow:** Helpers read and write Alpha `pt_regs` fields. Alpha uses `r0` for return value, `r19` as the error flag, `r0`/`r16`-`r20` argument conventions around syscall entry, and `orig_r0` for rollback.

**State and persistence behavior:** State is the saved register frame for the current task. No other persistence.

**Dependencies and integration points:** Depends on audit UAPI, scheduler task structs, and Alpha register layout.

**Risks:** Alpha syscall ABI differs from many architectures because success/error uses `r19`; tracing code must preserve that convention. Argument indexing mistakes break seccomp/audit/ptrace modifications.

**Test signals:** strace/ptrace syscall injection, seccomp user-notification or filter tests, audit syscall classification, and error-return tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/thread_info.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/thread_info.h

**Purpose:** Defines Alpha `thread_info`, task flags, thread status flags, unaligned-access control mapping, and FPU save helper.

**Important APIs/types/functions:** `struct thread_info`, `INIT_THREAD_INFO`, `current_thread_info`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `TIF_*`, `_TIF_*`, `_TIF_WORK_MASK`, `TS_UAC_*`, `TS_SAVED_FP`, `TS_RESTORE_FP`, `SET_UNALIGN_CTL`, `GET_UNALIGN_CTL`, `__save_fpu`, and `save_fpu`.

**Control flow:** Entry/exit assembly and scheduler code inspect `_TIF_WORK_MASK` before returning to user mode. Unaligned-control helpers translate user sysinfo bits into thread status bits. `save_fpu` records FP state once per thread until restored.

**State and persistence behavior:** Per-task state includes flags, status, CPU id, PCB, address limit, FP registers, FP control, and syscall number.

**Dependencies and integration points:** Depends on Alpha processor, HWRPB, sysinfo constants, task stack layout, and low-level entry/FPU code.

**Risks:** Bit positions are consumed by assembly and userspace unaligned-control ABI. Thread size must match `ptrace.h` frame placement.

**Test signals:** Syscall return work flags, signal/seccomp/audit tracing, unaligned access policy tests, FPU save/restore tests, and assembly offset checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/timex.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/timex.h

**Purpose:** Defines Alpha timer frequency and cycle-counter access.

**Important APIs/types/functions:** `CLOCK_TICK_RATE`, `cycles_t`, and `get_cycles()` using `rpcc`.

**Control flow:** Timekeeping and scheduler code call `get_cycles` to read the low 32 bits of the processor cycle counter; platform timer code uses the 32.768 kHz tick-rate constant.

**State and persistence behavior:** No local state; reads CPU cycle counter.

**Dependencies and integration points:** Depends on Alpha `rpcc` instruction and generic timekeeping expectations.

**Risks:** Only low 32 bits are continuously useful, so wraparound is frequent. Code must treat `cycles_t` accordingly.

**Test signals:** Clocksource/scheduler timing tests, wraparound handling, and boot calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/tlb.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/tlb.h

**Purpose:** Adapts generic TLB-gather freeing to Alpha page-table descriptor removal.

**Important APIs/types/functions:** `__pte_free_tlb` and `__pmd_free_tlb` mapped to `tlb_remove_ptdesc` with page or virtual ptdesc conversion.

**Control flow:** MM teardown queues freed page-table pages through generic TLB gather so actual freeing occurs after required TLB invalidation.

**State and persistence behavior:** No local state; operates on generic MMU gather batches.

**Dependencies and integration points:** Depends on `asm-generic/tlb.h`, ptdesc helpers, and Alpha page-table allocation.

**Risks:** Wrong ptdesc conversion can free incorrect page-table memory or race with active walkers.

**Test signals:** mmap/munmap teardown, exit, memory pressure, page-table debug, and TLB gather tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/tlbflush.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/tlbflush.h

**Purpose:** Defines Alpha TLB flush helpers for current mm, pages, ranges, all address spaces, and kernel ranges. EV5/EV6 paths use ASN invalidation where possible.

**Important APIs/types/functions:** `flush_tlb_current`, `flush_tlb_current_page`, `flush_tlb_all`, `flush_tlb_mm`, `flush_tlb_page`, `flush_tlb_range`, and `flush_tlb_kernel_range` plus `__load_new_mm_context` integration.

**Control flow:** For EV5-style builds, flushing the current mm reloads the mm context; flushing a page can call `tbis`. Non-current mm flushes invalidate `mm->context` entries so the next switch allocates a new ASN. Generic or SMP paths may use external implementations.

**State and persistence behavior:** Mutates per-mm context versions, current PCB ASN, and CPU TB contents.

**Dependencies and integration points:** Depends on `mmu_context.h`, PAL TBI calls, scheduler current mm, and generic VM invalidation callers.

**Risks:** Too-narrow flushes leave stale translations; too-broad flushes cost performance. Current-versus-noncurrent mm distinction must be correct under SMP.

**Test signals:** mprotect/COW/unmap tests, kernel vmalloc/ioremap flush tests, migration/compaction, and SMP TLB shootdown workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/topology.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/topology.h

**Purpose:** Provides Alpha topology include glue, deferring most NUMA/topology behavior to generic code.

**Important APIs/types/functions:** Includes Linux SMP/thread/NUMA headers, `asm/machvec.h`, and `asm-generic/topology.h`.

**Control flow:** No direct control flow. Generic scheduler and memory code consume topology definitions through this header.

**State and persistence behavior:** No state here; topology state is generic or machine-vector-provided.

**Dependencies and integration points:** Depends on generic topology and Alpha machine-vector data.

**Risks:** Alpha-specific topology omissions may make all CPUs/nodes appear generic even on complex systems.

**Test signals:** Build NUMA/SMP configs and inspect scheduler/sysfs topology output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/types.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/types.h

**Purpose:** Kernel wrapper that exposes Alpha UAPI integer type definitions.

**Important APIs/types/functions:** Includes `<uapi/asm/types.h>`.

**Control flow:** No control flow.

**State and persistence behavior:** No state.

**Dependencies and integration points:** Depends on UAPI type header and generic integer typedefs.

**Risks:** Type-size ABI drift affects all kernel/userspace interfaces.

**Test signals:** UAPI header build and ABI size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/uaccess.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/uaccess.h

**Purpose:** Implements Alpha user-memory access primitives for scalar get/put, raw copy, clear, and string-length/copy helpers.

**Important APIs/types/functions:** `put_user`, `get_user`, `__put_user`, `__get_user`, exception-table macro `EXC`, sized load/store macros, `raw_copy_from_user`, `raw_copy_to_user`, `clear_user`, `strncpy_from_user`, and `strnlen_user`.

**Control flow:** Checked variants call `__access_ok` before inline assembly loads/stores; unchecked variants rely on caller validation. Faulting instructions emit Alpha exception-table fixups that set `-EFAULT` or zero values. Bulk copies delegate to `__copy_user`.

**State and persistence behavior:** No local state; reads/writes user memory and kernel buffers. Exception table entries become part of the kernel image.

**Dependencies and integration points:** Depends on generic access_ok, Alpha byte/word load-store helpers, exception-table handling, and `asm/extable.h`.

**Risks:** Inline assembly and exception fixup encoding are fragile. User pointers share address space with kernel mappings, so access checks and fault handling are the safety boundary.

**Test signals:** lib/uaccess tests, fault-injection around invalid user pointers, copy_to/from_user boundary tests, hardened usercopy, and syscall argument copy tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/ucontext.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/ucontext.h

**Purpose:** Defines Alpha kernel `struct ucontext` used for signal frames and user context save/restore.

**Important APIs/types/functions:** `struct ucontext` with flags, link, OSF signal mask, stack, machine context, and extensible signal mask tail.

**Control flow:** Signal delivery builds this structure; signal return restores machine context and masks from it.

**State and persistence behavior:** The structure is userspace-visible signal-frame state, not kernel-persistent.

**Dependencies and integration points:** Depends on `old_sigset_t`, `stack_t`, `struct sigcontext`, and kernel `sigset_t` from signal headers.

**Risks:** Layout changes break signal ABI and `sigreturn`. The final `uc_sigmask` placement is intentionally extensible.

**Test signals:** Signal handler context tests, alternate stack tests, `getcontext`/libc compatibility where applicable, and sigreturn validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/unistd.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/unistd.h

**Purpose:** Kernel syscall-number wrapper and Alpha syscall implementation request list.

**Important APIs/types/functions:** `NR_syscalls`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_OLD_READDIR`, `__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_*` flags for legacy syscall implementations.

**Control flow:** Generic syscall table/build code uses the `__ARCH_WANT_*` macros to include compatibility or legacy syscall handlers needed by Alpha.

**State and persistence behavior:** No runtime state; shapes compiled syscall surface.

**Dependencies and integration points:** Depends on UAPI syscall numbers generated from Alpha syscall table and generic syscall implementation selection.

**Risks:** Removing a wanted syscall breaks Alpha userspace ABI. Wrong `NR_syscalls` affects seccomp and bounds checks.

**Test signals:** Syscall table build checks, LTP syscall coverage, legacy stat/readdir/umount/fork/vfork tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/user.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/user.h

**Purpose:** Defines the Alpha `struct user` core-file header layout used by traditional core dumps and debuggers.

**Important APIs/types/functions:** `struct user` with integer/FP register storage, segment sizes, start addresses, signal, register pointer, magic, and command name.

**Control flow:** Core dump code emits this structure so GDB/BFD can locate registers and process address ranges.

**State and persistence behavior:** Represents serialized process state in a core file. The header itself stores no live state.

**Dependencies and integration points:** Depends on task/ptrace headers, Alpha register indices from `asm/reg.h`, and page sizing.

**Risks:** Layout is debugger ABI. Register array sizing must match `EF_SIZE` plus FP registers.

**Test signals:** Generate core dumps, inspect with GDB, validate registers/segments and command name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/vga.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/vga.h

**Purpose:** Provides VGA text-memory accessors and hose-aware address fixups for Alpha systems whose VGA device is not on hose 0.

**Important APIs/types/functions:** `scr_writew`, `scr_readw`, `scr_memsetw`, `scr_memcpyw`, `scr_memmovew`, `vga_readb`, `vga_writeb`, `pci_vga_hose`, VGA port/memory classifiers, `FIXUP_IOADDR_VGA`, `FIXUP_MEMADDR_VGA`, and `VGA_MAP_MEM`.

**Control flow:** Console code uses direct memory operations for RAM-like addresses and raw I/O operations for I/O addresses. When `CONFIG_VGA_HOSE` is enabled, legacy VGA port/memory addresses are rebased through `pci_vga_hose` resources.

**State and persistence behavior:** The selected VGA hose is global runtime state declared here and set by console/core logic.

**Dependencies and integration points:** Depends on Alpha I/O helpers, PCI controller resources, console code, and string `memset16`.

**Risks:** Incorrect hose selection sends VGA reads/writes to the wrong PCI window. `scr_memsetw` assumes count in bytes and converts to 16-bit count for memory.

**Test signals:** Boot VGA console on multi-hose systems, switch consoles, load fonts, and test `CONFIG_VGA_HOSE` selection from firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/vga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/vmalloc.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/vmalloc.h

**Purpose:** Empty Alpha vmalloc architecture wrapper used to satisfy generic include structure.

**Important APIs/types/functions:** Only include guard.

**Control flow:** No behavior.

**State and persistence behavior:** No state.

**Dependencies and integration points:** Generic vmalloc code includes it for architecture overrides.

**Risks:** Any Alpha-specific vmalloc behavior must be added elsewhere or here deliberately.

**Test signals:** Build vmalloc users and run vmalloc/ioremap smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/word-at-a-time.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/word-at-a-time.h

**Purpose:** Implements Alpha word-at-a-time zero-byte detection for optimized string routines.

**Important APIs/types/functions:** `struct word_at_a_time`, `WORD_AT_A_TIME_CONSTANTS`, `has_zero`, `prep_zero_mask`, `create_zero_mask`, `find_zero`, and `zero_bytemask`.

**Control flow:** `has_zero` uses Alpha `cmpbge` helper to identify zero-byte positions. `find_zero` uses CIX count-trailing-zero where available or a small bit search fallback.

**State and persistence behavior:** No state.

**Dependencies and integration points:** Depends on Alpha compiler helpers `__kernel_cmpbge` and optionally `__kernel_cttz`, plus generic word-at-a-time string code.

**Risks:** Byte-position masks are endian/architecture-specific. Wrong `find_zero` mapping corrupts string length/copy termination.

**Test signals:** String tests for NUL at every byte position, CIX and non-CIX builds, and unaligned string workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/word-at-a-time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/wrperfmon.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/wrperfmon.h

**Purpose:** Defines Alpha performance-monitor PAL command codes, counter masks, shifts, and event selections for EV5/EV6/EV67 processors.

**Important APIs/types/functions:** `PERFMON_CMD_*`, EV5/EV6/EV67 counter bit masks, count shifts/masks, mode/event masks, and event encodings such as cycles, instructions, branches, ITB/DTB misses, and traps.

**Control flow:** Perf or low-level monitor code composes PAL `wrperfmon` command values from these constants and interprets packed counter fields.

**State and persistence behavior:** No local state; hardware performance counters hold runtime state.

**Dependencies and integration points:** Depends on PAL `wrperfmon` support, CPU family detection, and perf-event implementation.

**Risks:** Event encodings differ by CPU family; using EV6 constants on EV5 or EV67 can program the wrong counter. Command value overlap is intentional and context-dependent.

**Test signals:** Perf event smoke tests on EV5/EV6/EV67 hardware or emulator support, counter overflow/read/write tests, and event sanity comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/wrperfmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/Kbuild -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/Kbuild

**Purpose:** UAPI header that exports Alpha UAPI generated-header policy. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** the `generated-y += unistd_32.h` and `generic-y += bpf_perf_event.h` declarations.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in uapi header generation rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with uapi header generation. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/a.out.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/a.out.h

**Purpose:** UAPI header that defines Alpha a.out executable and ECOFF-derived header layouts. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `struct filehdr`, `struct aouthdr`, `struct scnhdr`, `struct exec`, `N_TXTADDR`, `N_DATADDR`, `N_BSSADDR`, and `N_TXTOFF`.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in legacy binary loaders and core/binfmt tooling rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with legacy binary loaders and core/binfmt tooling. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/a.out.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/auxvec.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/auxvec.h

**Purpose:** UAPI header that defines Alpha auxiliary-vector entries for sysinfo and cache-shape metadata. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `AT_SYSINFO`, `AT_SYSINFO_EHDR`, `AT_L1I_CACHESHAPE`, `AT_L1D_CACHESHAPE`, `AT_L2_CACHESHAPE`, `AT_L3_CACHESHAPE`, and `AT_VECTOR_SIZE_ARCH`.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in ELF loader, VDSO, and libc startup rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with ELF loader, VDSO, and libc startup. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/bitsperlong.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/bitsperlong.h

**Purpose:** UAPI header that declares Alpha userspace long width. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `__BITS_PER_LONG 64` plus generic bits-per-long inclusion.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in UAPI type sizing rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with UAPI type sizing. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/byteorder.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/byteorder.h

**Purpose:** UAPI header that declares Alpha little-endian byte order. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `linux/byteorder/little_endian.h`.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in network/filesystem endian helpers rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with network/filesystem endian helpers. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/compiler.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/compiler.h

**Purpose:** UAPI header that provides userspace-visible Alpha compiler instruction helpers for byte/word loads and stores. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `__kernel_ldbu`, `__kernel_ldwu`, `__kernel_stb`, and `__kernel_stw` with compiler-dependent inline assembly or fallbacks.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in UAPI helpers and kernel shared instruction abstractions rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with UAPI helpers and kernel shared instruction abstractions. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/console.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/console.h

**Purpose:** UAPI header that defines SRM console callback command and environment variable numbers. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `CCB_*` console operations and `ENV_*` identifiers.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in SRM console/environment access rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with SRM console/environment access. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/console.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/errno.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/errno.h

**Purpose:** UAPI header that defines Alpha-specific errno numbering beyond generic base errors. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `EAGAIN`, socket/network errors, SysV/stream errors, `EOVERFLOW`, and compatibility aliases.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in syscall ABI and libc errno tables rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with syscall ABI and libc errno tables. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/fcntl.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/fcntl.h

**Purpose:** UAPI header that defines Alpha file open and fcntl command values. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `O_*`, `__O_SYNC`, `F_GETLK`, `F_SETLK`, lock constants, then generic fcntl inclusion.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in open/fcntl syscall ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with open/fcntl syscall ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/fpu.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/fpu.h

**Purpose:** UAPI header that defines Alpha FPCR and IEEE software-control bits. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `FPCR_*`, dynamic rounding masks, `IEEE_TRAP_ENABLE_*`, `IEEE_MAP_*`, `IEEE_STATUS_*`, and `IEEE_INHERIT`.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in FPU trap handling, signal state, and libc floating-point control rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with FPU trap handling, signal state, and libc floating-point control. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/gentrap.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/gentrap.h

**Purpose:** UAPI header that defines Alpha generic trap negative reason codes. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `GEN_INTOVF`, `GEN_FLTOVF`, `GEN_FLTDIV`, range/subscript errors, and assertion/null/stack errors.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in PAL `gentrap`, signal, and language-runtime trap mapping rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with PAL `gentrap`, signal, and language-runtime trap mapping. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/gentrap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/ioctl.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/ioctl.h

**Purpose:** UAPI header that defines Alpha ioctl command bit packing. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `_IOC_*` bit widths, shifts, direction constants, `_IO`, `_IOR`, `_IOW`, `_IOWR`, and legacy `IOC_*` masks.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in ioctl syscall ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with ioctl syscall ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/ioctls.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/ioctls.h

**Purpose:** UAPI header that defines Alpha terminal, socket, serial, and file ioctl numbers. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `FIOCLEX`, `FIONBIO`, `TCGETS`, `TIOC*`, `TIOCSER*`, pty, RS485, ISO7816, and modem controls.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in tty, socket, and serial userspace ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with tty, socket, and serial userspace ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/mman.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/mman.h

**Purpose:** UAPI header that defines Alpha memory-protection, mmap, mlock, and madvise flags. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `PROT_*`, `MAP_*`, `MS_*`, `MCL_*`, `MADV_*`, `MAP_FILE`, and pkey masks.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in mmap/mprotect/madvise syscall ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with mmap/mprotect/madvise syscall ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/pal.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/pal.h

**Purpose:** UAPI header that defines PALcode operation numbers exposed to assembly and low-level code. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** unprivileged and privileged `PAL_*` numbers including halt, callsys, tbi, swpctx, wrent, swpipl, and rti.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in PAL wrapper headers and assembly rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with PAL wrapper headers and assembly. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/pal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/param.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/param.h

**Purpose:** UAPI header that defines Alpha userspace timing and exec page constants. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `__USER_HZ 1024`, `EXEC_PAGESIZE 8192`, and generic param inclusion.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in time accounting and exec ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with time accounting and exec ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/posix_types.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/posix_types.h

**Purpose:** UAPI header that defines Alpha-specific POSIX kernel typedefs. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `__kernel_ino_t` as unsigned int and `__kernel_sigset_t` as unsigned long.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in UAPI struct layout and libc type compatibility rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with UAPI struct layout and libc type compatibility. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/ptrace.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/ptrace.h

**Purpose:** UAPI header that defines Alpha saved register frames. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `struct pt_regs` and `struct switch_stack` with integer registers, PAL frame, PC/PS/GP, and saved callee registers.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in ptrace, signal, core dump, and assembly entry ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with ptrace, signal, core dump, and assembly entry ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/reg.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/reg.h

**Purpose:** UAPI header that defines Alpha core-file/register index constants. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `EF_*` indices, `EF_SIZE`, `HWEF_SIZE`, `EF_SSIZE`, and `CORE_REG`.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in debugger/core register mapping rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with debugger/core register mapping. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/regdef.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/regdef.h

**Purpose:** UAPI header that maps symbolic Alpha register names for assembly. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `v0`, `t0`-`t12`, `s0`-`s6`, `a0`-`a5`, `ra`, `pv`, `gp`, `sp`, and `zero`.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in assembly sources and UAPI-compatible assembler code rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with assembly sources and UAPI-compatible assembler code. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/regdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/resource.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/resource.h

**Purpose:** UAPI header that defines Alpha resource-limit numbering and infinity value. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `RLIMIT_NOFILE`, `RLIMIT_AS`, `RLIMIT_NPROC`, `RLIMIT_MEMLOCK`, and `RLIM_INFINITY`.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in getrlimit/setrlimit ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with getrlimit/setrlimit ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/setup.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/setup.h

**Purpose:** UAPI header that defines Alpha command-line size. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `COMMAND_LINE_SIZE 256`.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in boot ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with boot ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/sigcontext.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/sigcontext.h

**Purpose:** UAPI header that defines Alpha signal machine context layout. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `struct sigcontext` containing on-stack flag, mask, PC, PS, general registers, FP registers, FPCR, trap args, and unique value.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in signal delivery and sigreturn ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with signal delivery and sigreturn ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/siginfo.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/siginfo.h

**Purpose:** UAPI header that delegates Alpha siginfo layout to generic UAPI. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `asm-generic/siginfo.h` inclusion.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in signal information ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with signal information ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/siginfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/signal.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/signal.h

**Purpose:** UAPI header that defines Alpha userspace signal numbers, action flags, stacks, and sigaction layouts. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `NSIG`, `sigset_t`, signal numbers, `SA_*`, stack sizes, `SIG_BLOCK`, `struct sigaction`, `stack_t`, and `struct sigstack`.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in signal syscall/libc ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with signal syscall/libc ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/socket.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/socket.h

**Purpose:** UAPI header that defines Alpha socket option numbers and timestamp option variants. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `SOL_SOCKET`, `SO_*`, `SCM_*`, old/new timestamp options, and buf-lock/netns options.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in setsockopt/getsockopt ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with setsockopt/getsockopt ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/sockios.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/sockios.h

**Purpose:** UAPI header that defines Alpha socket ioctl numbers. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `FIOGETOWN`, `FIOSETOWN`, `SIOCATMARK`, `SIOCSPGRP`, `SIOCGPGRP`, and old timestamp ioctls.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in socket ioctl ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with socket ioctl ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/sockios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/stat.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/stat.h

**Purpose:** UAPI header that defines Alpha `stat` and `stat64` userspace layouts. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `struct stat` and `struct stat64` with Alpha field order, padding, and sizes.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in stat-family syscall ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with stat-family syscall ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/statfs.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/statfs.h

**Purpose:** UAPI header that sets Alpha statfs word size before generic statfs layout. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `__statfs_word __u32` plus generic statfs inclusion.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in statfs syscall ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with statfs syscall ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/statfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/swab.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/swab.h

**Purpose:** UAPI header that provides Alpha byte-swap optimization. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `__arch_swab32` using Alpha byte-manipulation helpers when available.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in endian conversion helpers rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with endian conversion helpers. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/sysinfo.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/sysinfo.h

**Purpose:** UAPI header that defines Alpha `osf_getsysinfo` and `osf_setsysinfo` operation numbers and unaligned-access flags. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `GSI_*`, `SSI_*`, `SSIN_UACPROC`, `UAC_BITMASK`, `UAC_NOPRINT`, `UAC_NOFIX`, and `UAC_SIGBUS`.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in OSF compatibility syscalls and thread unaligned policy rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with OSF compatibility syscalls and thread unaligned policy. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/sysinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/termbits.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/termbits.h

**Purpose:** UAPI header that defines Alpha termios bit layout and baud/control constants. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `tcflag_t`, `cc_t`, `speed_t`, `NCCS`, `struct termios`, `termios2`, `ktermios`, control-character indexes, input/output/control/local flags, and baud values.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in tty termios ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with tty termios ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/termbits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/termios.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/termios.h

**Purpose:** UAPI header that defines legacy Alpha terminal structs and control-character indexes. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `sgttyb`, `tchars`, `ltchars`, `winsize`, `NCC`, `struct termio`, and `_V*` indexes.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in legacy tty ioctl ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with legacy tty ioctl ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/termios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/types.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/types.h

**Purpose:** UAPI header that selects Alpha UAPI integer typedef model. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `__SANE_USERSPACE_TYPES__`-dependent inclusion of `int-l64.h` or `int-ll64.h`.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in fixed-width UAPI types rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with fixed-width UAPI types. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/unistd.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/unistd.h

**Purpose:** UAPI header that defines Alpha syscall aliases and includes generated syscall numbers. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `__NR_umount`, OSF shmat/getpid/getuid/getgid aliases, and `asm/unistd_32.h`.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in syscall-number ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with syscall-number ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/Makefile -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/Makefile

**Purpose:** Builds the Alpha kernel architecture objects. It selects common entry/trap/process/time/syscall/error/I/O objects, optional subsystem objects, and platform-specific core logic, board, IRQ, and machine-check files.

**Important APIs/types/functions:** `obj-y`, `obj-$(CONFIG_*)`, `always-$(KBUILD_BUILTIN)`, `asflags-y`, and `ccflags-y` assignments.

**Control flow:** Kbuild evaluates Alpha configuration symbols to decide whether to build a generic multi-platform kernel or a specific machine family. Generic builds include multiple core logic and board files; non-generic builds include only selected platform support.

**State and persistence behavior:** No runtime state; it determines linked kernel contents and therefore the available platform initialization paths.

**Dependencies and integration points:** Depends on Kbuild, Alpha Kconfig symbols, linker script generation, and source files in `arch/alpha/kernel`.

**Risks:** Missing object selections can produce kernels that boot but lack IRQ/core-logic/error support for a board. Generic versus non-generic conditional differences are easy to regress.

**Test signals:** Build Alpha generic and representative non-generic configs, verify `vmlinux.lds` generation, and boot platform-specific images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/asm-offsets.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/asm-offsets.c

**Purpose:** Generates Alpha assembly offsets for `thread_info`, `pt_regs`, `switch_stack`, and machine-vector fields.

**Important APIs/types/functions:** `DEFINE(TI_FLAGS)`, `TI_FP`, `TI_STATUS`, `SP_OFF`, `SIZEOF_PT_REGS`, `SWITCH_STACK_SIZE`, `HAE_CACHE`, and `HAE_REG`.

**Control flow:** Kbuild compiles this file specially and post-processes emitted `DEFINE` statements into an offsets header consumed by assembly files.

**State and persistence behavior:** No runtime state; generated constants must match C structure layout.

**Dependencies and integration points:** Depends on Linux kbuild offset macros, scheduler/ptrace headers, and `asm/machvec.h`.

**Risks:** Stale offsets break entry, trap, and context-switch assembly in ways that are hard to diagnose.

**Test signals:** Full Alpha build, inspect generated asm-offsets, and boot syscall/trap/context-switch paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/audit.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/audit.c

**Purpose:** Registers Alpha syscall audit classes and classifies selected syscall numbers for the audit subsystem.

**Important APIs/types/functions:** `dir_class`, `read_class`, `write_class`, `chattr_class`, `signal_class`, `audit_classify_arch`, `audit_classify_syscall`, and `audit_classes_init`.

**Control flow:** At initcall time, generic audit class bitmaps are registered. Runtime syscall classification maps Alpha `open`, `openat`, `openat2`, and `execve` to specific audit classes; all others are native.

**State and persistence behavior:** The audit subsystem retains registered class tables. This file owns only static class arrays.

**Dependencies and integration points:** Depends on generic audit class include fragments and Alpha syscall numbers.

**Risks:** Incomplete classification can reduce audit rule precision. `audit_classify_arch` returns zero, so arch discrimination relies on higher-level audit arch handling.

**Test signals:** Audit rule tests for open/exec/write/read/chattr/signal classes and syscall-number drift checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/bugs.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/bugs.c

**Purpose:** Reports Alpha CPU vulnerability status for sysfs based on CPU family.

**Important APIs/types/functions:** `cpu_is_ev6_or_later`, `cpu_show_meltdown`, `cpu_show_spectre_v1`, and `cpu_show_spectre_v2` under `CONFIG_SYSFS`.

**Control flow:** Sysfs vulnerability attribute reads inspect the HWRPB processor type; EV6 through EV69 report `Vulnerable`, older CPUs report `Not affected`.

**State and persistence behavior:** No mutable state; reads boot-time HWRPB CPU descriptor.

**Dependencies and integration points:** Depends on HWRPB structures, Linux CPU sysfs vulnerability plumbing, and CPU type constants.

**Risks:** The status is a coarse family-based report and does not model mitigations. CPU type range mistakes misreport vulnerability files.

**Test signals:** Read `/sys/devices/system/cpu/vulnerabilities/*` on EV5 and EV6+ configs and validate strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/bugs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/console.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/console.c

**Purpose:** Finds and initializes VGA console resources on Alpha systems where VGA lives behind a nonzero PCI hose.

**Important APIs/types/functions:** `pci_vga_hose`, `alpha_vga`, `default_vga_hose_select`, `locate_and_init_vga`, and `find_console_vga_hose`.

**Control flow:** `locate_and_init_vga` scans VGA-class PCI devices, chooses a hose, requests VGA I/O resources relative to that hose, sets `pci_vga_hose`, and takes over the VGA console. Firmware CTB parsing can preselect the console graphics hose.

**State and persistence behavior:** Global `pci_vga_hose` records the active VGA hose; `alpha_vga` resource is rebased and requested once.

**Dependencies and integration points:** Depends on PCI enumeration, HWRPB CTB, VGA console, console locking, Alpha PCI hose list, and `asm/vga.h` fixups.

**Risks:** `alpha_vga.start/end` are mutated by adding hose offset; repeated calls can double-add if not guarded by hose/console state. Wrong hose selection breaks console I/O.

**Test signals:** Boot VGA console on multi-hose hardware, scan multiple VGA devices with custom selector, and verify resource requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_cia.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/core_cia.c

**Purpose:** Implements CIA/PYXIS core logic support for PCI config access, DMA windows, broken scatter-gather TLB workarounds, SRM restoration, and machine-check decoding. This is platform hardware glue rather than Ceph client logic; it makes Linux PCI, DMA, I/O mapping, and machine-check paths work on CIA/PYXIS Alpha systems.

**Important APIs/types/functions:** `cia_pci_ops`, `cia_pci_tbi`, `cia_init_arch`, `pyxis_init_arch`, `cia_kill_arch`, `cia_init_pci`, and `cia_machine_check`, plus static helpers for config-address construction, controller register access, DMA-window programming, and error clearing/decoding.

**Control flow:** config accesses program CIA CFG for type-1 cycles, clear error registers, mark expected machine checks, perform sparse config-space load/store, then restore CFG. Initialization clears error masks, enables machine checks, sets HAE and DMA windows, prepares or verifies TBIA workarounds, and common PCI init runs after machine checks are available.

**State and persistence behavior:** single hose with ISA SG window, 2 GiB direct map, optional DAC window, HAE resources, CIA/PYXIS controller registers, saved SRM configuration, and machine-check expected/taken flags. None of this is filesystem-persistent, but it persists for the lifetime of the booted kernel and controls all PCI/DMA behavior on the platform.

**Dependencies and integration points:** Depends on Alpha core-specific register headers, `asm/io.h`, `asm/ptrace.h`, `pci_impl.h`, `proto.h`, Linux PCI/resource/memblock APIs, IOMMU arena helpers, PAL machine-check state, and generic PCI enumeration.

**Risks:** These paths intentionally handle absent devices and bad PCI cycles with expected machine checks. Barrier ordering, readbacks that force posted writes, DMA window masks, and firmware restoration are all high-risk. Wrong hose resources or SG TLB invalidation can corrupt DMA or make PCI devices disappear.

**Test signals:** Boot a CIA/PYXIS kernel or emulator target, enumerate PCI, exercise config reads/writes to present and absent devices, run DMA through ISA and PCI windows, test ioremap/legacy I/O, and inject or observe machine checks during config probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_cia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_irongate.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/core_irongate.c

**Purpose:** Implements IRONGATE/AMD 751-761 core logic support for PCI config space, Albacore memory reservation, AGP aperture ioremap, and error clearing. This is platform hardware glue rather than Ceph client logic; it makes Linux PCI, DMA, I/O mapping, and machine-check paths work on IRONGATE Alpha systems.

**Important APIs/types/functions:** `irongate_pci_ops`, `irongate_pci_clr_err`, `irongate_init_arch`, `irongate_ioremap`, and `irongate_iounmap`, plus static helpers for config-address construction, controller register access, DMA-window programming, and error clearing/decoding.

**Control flow:** config reads/writes access IRONGATE config addresses directly with byte/word helpers and readbacks. Initialization clears errors, warns about old PALcode on Albacore, reserves memory above PCI space when needed, disables AGP GART by default, and sets direct-map DMA.

**State and persistence behavior:** single hose, dense I/O and memory bases with 43-bit user bias, direct-map DMA state, optional AGP GATT mappings, global `IronECC`, and temporarily reserved memory above PCI aperture. None of this is filesystem-persistent, but it persists for the lifetime of the booted kernel and controls all PCI/DMA behavior on the platform.

**Dependencies and integration points:** Depends on Alpha core-specific register headers, `asm/io.h`, `asm/ptrace.h`, `pci_impl.h`, `proto.h`, Linux PCI/resource/memblock APIs, IOMMU arena helpers, PAL machine-check state, and generic PCI enumeration.

**Risks:** These paths intentionally handle absent devices and bad PCI cycles with expected machine checks. Barrier ordering, readbacks that force posted writes, DMA window masks, and firmware restoration are all high-risk. Wrong hose resources or SG TLB invalidation can corrupt DMA or make PCI devices disappear.

**Test signals:** Boot a IRONGATE kernel or emulator target, enumerate PCI, exercise config reads/writes to present and absent devices, run DMA through ISA and PCI windows, test ioremap/legacy I/O, and inject or observe machine checks during config probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_irongate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_marvel.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/core_marvel.c

**Purpose:** Implements Marvel IO7 core logic support for discovering IO7s, creating PCI hoses per enabled IO7 port, setting DMA windows, config access, RTC callbacks, MMIO/port mapping, VGA hose detection, and AGP support. This is platform hardware glue rather than Ceph client logic; it makes Linux PCI, DMA, I/O mapping, and machine-check paths work on Marvel/EV7 IO7 Alpha systems.

**Important APIs/types/functions:** `marvel_next_io7`, `marvel_find_io7`, `io7_clear_errors`, `marvel_init_arch`, `marvel_pci_ops`, `marvel_pci_tbi`, `marvel_ioremap`, `marvel_iounmap`, `marvel_is_mmio`, `marvel_ioportmap`, `marvel_ioread8`, `marvel_iowrite8`, `marvel_agp_ops`, and `marvel_agp_info`, plus static helpers for config-address construction, controller register access, DMA-window programming, and error clearing/decoding.

**Control flow:** boot parses the GCT for IO7 nodes or accepts `io7=` overrides, allocates IO7s, initializes enabled ports as PCI hoses, configures SG/direct DMA windows, disables the AGP monster window, and locates console VGA. Config access builds hose-relative addresses and rejects disabled ports or oversized primary-bus IDs.

**State and persistence behavior:** sorted `io7_head` list, per-IO7 port enable state, hose resources and saved DMA windows, direct map at 2 GiB/1 GiB, ISA and PCI SG arenas, RTC index shadow, and AGP aperture reservations. None of this is filesystem-persistent, but it persists for the lifetime of the booted kernel and controls all PCI/DMA behavior on the platform.

**Dependencies and integration points:** Depends on Alpha core-specific register headers, `asm/io.h`, `asm/ptrace.h`, `pci_impl.h`, `proto.h`, Linux PCI/resource/memblock APIs, IOMMU arena helpers, PAL machine-check state, and generic PCI enumeration.

**Risks:** These paths intentionally handle absent devices and bad PCI cycles with expected machine checks. Barrier ordering, readbacks that force posted writes, DMA window masks, and firmware restoration are all high-risk. Wrong hose resources or SG TLB invalidation can corrupt DMA or make PCI devices disappear.

**Test signals:** Boot a Marvel/EV7 IO7 kernel or emulator target, enumerate PCI, exercise config reads/writes to present and absent devices, run DMA through ISA and PCI windows, test ioremap/legacy I/O, and inject or observe machine checks during config probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_marvel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_mcpcia.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/core_mcpcia.c

**Purpose:** Implements MCbus-PCI adaptor support for multi-hose Rawhide-style systems: config access, hose probing, DMA window setup, TLB invalidation, and machine-check printing. This is platform hardware glue rather than Ceph client logic; it makes Linux PCI, DMA, I/O mapping, and machine-check paths work on MCPCIA Alpha systems.

**Important APIs/types/functions:** `mcpcia_pci_ops`, `mcpcia_pci_tbi`, `mcpcia_init_arch`, `mcpcia_init_hoses`, and `mcpcia_machine_check`, plus static helpers for config-address construction, controller register access, DMA-window programming, and error clearing/decoding.

**Control flow:** boot creates hose 0 early, then after IRQs probes each possible hose by intentionally allowing expected machine checks on absent hardware. Startup configures abort reporting, SG/direct windows, HBASE/HAE registers, and TBIA. Config access uses type-1 cycles for all buses and marks expected machine checks around sparse loads/stores.

**State and persistence behavior:** multiple `pci_controller` hoses, per-hose sparse/dense resources and HAE window, ISA and PCI SG arenas, 2 GiB direct map, MCPCIA CAP error state, and per-CPU machine-check flags. None of this is filesystem-persistent, but it persists for the lifetime of the booted kernel and controls all PCI/DMA behavior on the platform.

**Dependencies and integration points:** Depends on Alpha core-specific register headers, `asm/io.h`, `asm/ptrace.h`, `pci_impl.h`, `proto.h`, Linux PCI/resource/memblock APIs, IOMMU arena helpers, PAL machine-check state, and generic PCI enumeration.

**Risks:** These paths intentionally handle absent devices and bad PCI cycles with expected machine checks. Barrier ordering, readbacks that force posted writes, DMA window masks, and firmware restoration are all high-risk. Wrong hose resources or SG TLB invalidation can corrupt DMA or make PCI devices disappear.

**Test signals:** Boot a MCPCIA kernel or emulator target, enumerate PCI, exercise config reads/writes to present and absent devices, run DMA through ISA and PCI windows, test ioremap/legacy I/O, and inject or observe machine checks during config probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_mcpcia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_polaris.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/core_polaris.c

**Purpose:** Implements POLARIS core logic support for straightforward dense PCI config access, single-hose setup, fixed direct-map DMA, and minimal machine-check clearing. This is platform hardware glue rather than Ceph client logic; it makes Linux PCI, DMA, I/O mapping, and machine-check paths work on POLARIS Alpha systems.

**Important APIs/types/functions:** `polaris_pci_ops`, `polaris_init_arch`, and `polaris_machine_check`, plus static helpers for config-address construction, controller register access, DMA-window programming, and error clearing/decoding.

**Control flow:** config-space addresses include bus/devfn/register plus the dense config base; the chip chooses type-0 versus type-1 by bus number. Initialization trusts firmware setup, creates the hose, and sets direct-map DMA.

**State and persistence behavior:** single hose with dense memory/I/O bases, fixed 2 GiB direct-map window, no SG arenas, and POLARIS status register bits. None of this is filesystem-persistent, but it persists for the lifetime of the booted kernel and controls all PCI/DMA behavior on the platform.

**Dependencies and integration points:** Depends on Alpha core-specific register headers, `asm/io.h`, `asm/ptrace.h`, `pci_impl.h`, `proto.h`, Linux PCI/resource/memblock APIs, IOMMU arena helpers, PAL machine-check state, and generic PCI enumeration.

**Risks:** These paths intentionally handle absent devices and bad PCI cycles with expected machine checks. Barrier ordering, readbacks that force posted writes, DMA window masks, and firmware restoration are all high-risk. Wrong hose resources or SG TLB invalidation can corrupt DMA or make PCI devices disappear.

**Test signals:** Boot a POLARIS kernel or emulator target, enumerate PCI, exercise config reads/writes to present and absent devices, run DMA through ISA and PCI windows, test ioremap/legacy I/O, and inject or observe machine checks during config probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_polaris.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_t2.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/core_t2.c

**Purpose:** Implements T2/SABLE core logic support for sparse PCI config access, saved SRM DMA-window restoration, direct and ISA SG DMA windows, TLB invalidation, and broadcast-style machine-check filtering. This is platform hardware glue rather than Ceph client logic; it makes Linux PCI, DMA, I/O mapping, and machine-check paths work on T2 Alpha systems.

**Important APIs/types/functions:** `t2_pci_ops`, `t2_init_arch`, `t2_kill_arch`, `t2_pci_tbi`, and `t2_machine_check`, plus static helpers for config-address construction, controller register access, DMA-window programming, and error clearing/decoding.

**Control flow:** config access validates primary-bus device IDs, toggles `T2_HAE_3` for type-1 cycles, marks expected machine checks, performs sparse config load/store, delays for possible broadcast checks, then restores HAE. Init enables SG TLB, saves SRM config, creates resources, sets windows, and zeros HAE registers.

**State and persistence behavior:** single hose, saved T2 window/HAE/HBASE registers, direct map window 1, ISA SG window 2, per-CPU `mcheck_expected/taken`, and global `t2_mcheck_any_expected/last_taken` masks. None of this is filesystem-persistent, but it persists for the lifetime of the booted kernel and controls all PCI/DMA behavior on the platform.

**Dependencies and integration points:** Depends on Alpha core-specific register headers, `asm/io.h`, `asm/ptrace.h`, `pci_impl.h`, `proto.h`, Linux PCI/resource/memblock APIs, IOMMU arena helpers, PAL machine-check state, and generic PCI enumeration.

**Risks:** These paths intentionally handle absent devices and bad PCI cycles with expected machine checks. Barrier ordering, readbacks that force posted writes, DMA window masks, and firmware restoration are all high-risk. Wrong hose resources or SG TLB invalidation can corrupt DMA or make PCI devices disappear.

**Test signals:** Boot a T2 kernel or emulator target, enumerate PCI, exercise config reads/writes to present and absent devices, run DMA through ISA and PCI windows, test ioremap/legacy I/O, and inject or observe machine checks during config probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_t2.c -->
