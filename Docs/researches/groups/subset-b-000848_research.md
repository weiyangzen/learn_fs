# Research: subset-b-000848

Grouped research for SPARC process handling, PROM/device-tree setup, interrupt translation, SYSIO/SBUS/PCI support, ptrace, return-from-trap, boot setup, and signal handling. Each section is keyed by exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/process.c

Purpose: provides the architecture-neutral SPARC syscall wrappers for `fork`, `vfork`, `clone`, and `clone3`. It translates the SPARC register calling convention into `kernel_clone()` or `sys_clone3()` arguments and preserves SPARC's historical child/parent return-value convention.

Important APIs/functions: exported syscall entry helpers are `sparc_fork()`, `sparc_vfork()`, `sparc_clone()`, and `sparc_clone3()`. They build `struct kernel_clone_args`, call `synchronize_user_stack()` before cloning register-window state, and use `compat_ptr()` for 32-bit compat user pointers when `CONFIG_COMPAT` and `TIF_32BIT` apply.

Control flow: `fork` and `vfork` reuse the parent's frame pointer as the child stack, with `vfork` adding `CLONE_VFORK | CLONE_VM`. `clone` extracts flags, signal, TLS, parent/child TID pointers, and optional stack from incoming `%i` registers; if no child stack is supplied it falls back to the parent frame pointer. After `kernel_clone()`, all three legacy wrappers restore `%i1` if an error/restart code is returned because lower-level `copy_thread()` may have clobbered the parent's second return register. `clone3` passes the user `clone_args` pointer and size directly to `sys_clone3()`.

State and persistence: state is per-syscall only. The wrappers mutate the live `pt_regs` for `%i1` restoration and pass clone attributes onward; no persistent storage is touched.

Dependencies and integration points: depends on SPARC register-window synchronization, generic clone/fork implementation, compat pointer translation, signal constants, and `copy_thread()` in the 32-bit or 64-bit process files. It is the syscall ABI bridge used by assembly entry code.

Risks: restart handling is delicate because SPARC legacy fork/clone returns use `%o0/%o1` differently from generic Linux. Missing `synchronize_user_stack()` risks cloning stale register-window contents. Compat pointer handling must match the 32-bit ABI exactly.

Test signals: fork/vfork/clone/clone3 syscall tests on both native and compat tasks, clone with supplied and omitted stacks, `CLONE_SETTLS`, parent/child TID and pidfd paths, and forced `-ERESTART*` syscall restart cases that verify `%i1` restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/process_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/process_32.c

Purpose: implements 32-bit SPARC process mechanics: idle hook, halt/restart/poweroff, register/stack dumps, FPU cleanup, thread creation, register-window stack cloning, and wait-channel discovery.

Important APIs/functions: architecture entry points include `arch_cpu_idle()`, `machine_halt()`, `machine_restart()`, `machine_power_off()`, `show_regs()`, `show_stack()`, `exit_thread()`, `flush_thread()`, `copy_thread()`, and `__get_wchan()`. Key helpers are `clone_stackframe()`, external `fpsave()`, and assembly return targets `ret_from_fork` and `ret_from_kernel_thread`. Global state includes `sparc_idle`, `pm_power_off`, `scons_pwroff`, `last_task_used_math`, and `current_set`.

Control flow: idle invokes a platform-provided `sparc_idle` callback when installed. Halt/restart/poweroff route through PROM and AUXIO, with a serial-console poweroff policy gate. `copy_thread()` saves the current FPU state when needed, builds a child stack containing a stack frame plus `pt_regs`, initializes kernel-thread frames separately, copies user frames for normal forks, optionally clones a supplied user stack frame, disables child FPU state on SMP, applies either clone3 or SunOS-style fork return values, and installs `%g7` TLS for `CLONE_SETTLS`. `__get_wchan()` walks saved kernel frames until it finds a non-scheduler return PC.

State and persistence: per-task state lives in `thread_info` and `thread_struct`: `ksp`, `kpc`, `kpsr`, `kwim`, `kregs`, saved FPU registers/queue, and register-window counters. Runtime-only globals track the last FPU owner on UP and power/idle hooks. No filesystem persistence is used.

Dependencies and integration points: integrates with PROM, AUXIO, scheduler fork/return assembly, SPARC PSR/WIM window mechanics, SMP FPU flags, generic reboot/poweroff APIs, stack dumping, and `copy_thread()` callers from generic process creation.

Risks: child stack layout must match assembly return paths. User stack cloning copies variable-sized register-window frames and can fault. FPU ownership differs between UP and SMP, so stale `TIF_USEDFPU` or `last_task_used_math` state can corrupt floating-point context. Poweroff behavior depends on console device type and AUXIO availability.

Test signals: boot/reboot/halt/poweroff on sparc32 systems, fork/clone/kernel-thread creation, clone with alternate stack, FPU-using tasks across fork/exit/exec, SMP FPU disable behavior, stack dump readability, and wait-channel output for sleeping tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/process_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/process_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/process_64.c

Purpose: implements 64-bit SPARC process mechanics: sun4u/sun4v idle behavior, CPU hotplug death, register diagnostics, sysrq global CPU/PMU snapshots, thread exit/flush, user register-window synchronization, thread cloning, ADI task duplication, and wait-channel walking.

Important APIs/functions: key exported hooks are `arch_cpu_idle()`, `arch_cpu_idle_dead()`, `show_regs()`, `arch_trigger_cpumask_backtrace()`, `exit_thread()`, `flush_thread()`, `synchronize_user_stack()`, `fault_in_user_windows()`, `copy_thread()`, `arch_dup_task_struct()`, and `__get_wchan()`. Diagnostic helpers include `__global_reg_self()`, `pmu_snapshot_all_cpus()`, and sysrq registrations for global registers and PMU counters.

Control flow: idle either touches the NMI watchdog on non-hypervisor systems or enters a sun4v yield with interrupts carefully toggled and scheduler-poke handling. Register dumps flush windows and print native or compat windows. `synchronize_user_stack()` flushes user windows and copies buffered windows to user stacks, compacting the buffer after successful writes; `fault_in_user_windows()` performs the stricter return-to-user path and signals `SIGBUS` or `SIGSEGV` on bad windows. `copy_thread()` constructs the child trap frame, handles kernel threads, adjusts 32-bit stack values, clones alternate stack frames for user clone, bumps shared user trap table references, applies clone3 versus SunOS return conventions, and sets `%g7` TLS. `arch_dup_task_struct()` samples ADI `%mcdper` so lazy per-task MCDPER state is inherited correctly.

State and persistence: owns runtime per-thread state in `thread_info`: saved windows, window stack pointers, FPU saved flags/registers, utrap reference table, child trap frame, CWP byte, and ADI-related flags. Global diagnostics use `global_cpu_snapshot` and a spinlock only while dumping. No durable storage is written.

Dependencies and integration points: depends on sun4v hypervisor calls, scheduler and CPU hotplug, SPARC V9 register-window ABI, `kstack_valid()`, FPU/VIS helpers, ADI capability checks, PMU PCR operations, SMP cross-calls, sysrq, context tracking, and generic fork/clone entry points.

Risks: return-to-user correctness hinges on flushing register windows without racing signal/reschedule work. Stack-bias and 32-bit stack detection are easy to break. Utrap reference counts must not leak or be freed too early. Sysrq snapshots intentionally avoid hard synchronization, so consumers must tolerate missing or stale CPU entries. ADI MCDPER lazy state must be updated before copying a task.

Test signals: native and compat clone/fork/TLS tests, register-window fault injection, signal delivery with pending windows, sun4v idle/poke behavior, CPU hotplug offline, sysrq `y` and `x` dumps on SMP, ADI-enabled task duplication, and wait-channel reporting under deep kernel stacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/process_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/prom.h -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/prom.h

Purpose: small internal header shared by SPARC PROM/device-tree builders. It exposes the console initialization hook and early PROM allocation accounting.

Important APIs/types/functions: declares `of_console_init()` and `extern unsigned int prom_early_allocated`; includes Linux spinlocks and architecture PROM declarations needed by PROM implementation files.

Control flow: no runtime logic is present. The header coordinates compile-time visibility between `prom_common.c` and the 32-bit/64-bit PROM implementations.

State and persistence: `prom_early_allocated` is an init-time byte counter for allocations made while constructing the device tree and console metadata. It is not persistent after boot.

Dependencies and integration points: integrates with Open Firmware PROM code, `of_pdt_build_devicetree()`, and architecture-specific `prom_early_alloc()` definitions.

Risks: declarations must remain consistent with both SPARC32 and SPARC64 implementations. Changing the allocation counter type or lifetime would affect boot diagnostics.

Test signals: successful SPARC boot device-tree construction, console initialization, and a sane `PROM: Built device tree with ... bytes` message from `prom_common.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/prom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_32.c

Purpose: supplies SPARC32-specific Open Firmware device-tree path construction, early allocation, console discovery, and stub CPU/IRQ device-tree hooks.

Important APIs/functions: implements `prom_early_alloc()`, `build_path_component()`, `of_console_init()`, `of_fill_in_cpu_data()`, and `irq_trans_init()`. Path helpers format node names for platform, SBUS, PCI, EBus, and LEON AMBA bus children.

Control flow: early allocation uses `memblock_alloc_or_panic()` and increments `prom_early_allocated`. `build_path_component()` dispatches by parent bus type and falls back to platform naming. `of_console_init()` handles PROM V0, V2, and V3 differently: V0 maps stdout enum values to display or serial nodes; V2 resolves stdout instance to package and appends tty suffixes; V3 uses root `stdout-path`. Fatal console discovery failures halt via PROM.

State and persistence: creates boot-time strings for `of_console_path` and records `of_console_device` and `of_console_options`. These are runtime device-tree/console state, not disk-persistent.

Dependencies and integration points: depends on `romvec`, PROM versioned callbacks, `prom_lock`, `restore_current()`, OF property helpers, LEON AMBA register formats, memblock, and shared globals from `prom_common.c`.

Risks: PROM versions have incompatible stdout interfaces. Path formatting relies on PROM `reg` property layouts and fixed temporary buffer sizes. Console failures are fatal very early in boot. The SPARC32 `irq_trans_init()` is intentionally empty, so platform IRQ setup must not assume the SPARC64 translator exists.

Test signals: boot on PROM V0/V2/V3 systems, serial and display console discovery, correct `/proc/device-tree` full names for SBUS/PCI/EBus/AMBA devices, and early boot halt on malformed stdout data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_64.c

Purpose: supplies SPARC64-specific Open Firmware device-tree path construction, CPU-node discovery/topology population, and console discovery for sun4u and sun4v systems.

Important APIs/functions: implements `prom_early_alloc()`, `build_path_component()`, `arch_find_n_match_cpu_physical_id()`, `of_find_node_by_cpuid()`, `of_populate_present_mask()`, `of_fill_in_cpu_data()`, and `of_console_init()`. Bus-specific path helpers cover sun4u, sun4v, SBUS, PCI/PCIe, UPA, virtual-devices, EBus, I2C, USB, and IEEE1394.

Control flow: path construction first checks parent bus type, then falls back to sun4v or sun4u root/platform formatting based on `tlb_type`. CPU iteration chooses `reg` on hypervisor systems or `upa-portid`/`portid`/`cpuid` elsewhere, validates CPU IDs against `NR_CPUS`, and invokes callbacks to find nodes, count present CPUs, or populate cache/topology data. Hypervisor systems skip OF CPU mask/cache population because those come from machine descriptions. Console init uses PROM stdout instance path/package resolution and validates display or serial device type.

State and persistence: stores boot-time console path/options/device and fills runtime `cpu_data()` fields for cache sizes, clock tick, core IDs, and processor IDs. It also marks possible/present CPUs. No persistent storage is written.

Dependencies and integration points: depends on PROM instance/path APIs, OF property traversal, `tlb_type`, sun4v/sun4u CPU identity conventions, SMP CPU masks, `cpu_data()`, `smp_fill_in_sib_core_maps()`, and shared `prom_common.c` globals.

Risks: CPU ID property choice varies by platform and firmware; missing IDs halt boot during iteration. Full-path formatting must preserve historic OF naming for boot device matching. Hypervisor systems deliberately bypass parts of OF CPU discovery, so code changes must not regress MDESC-based topology.

Test signals: boot on sun4u and sun4v systems, correct CPU present/possible masks, cache/topology fields in `/proc/cpuinfo`, `of_find_node_by_cpuid()` matches, device paths for PCI/UPA/virtual devices, and valid serial/display console paths with options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_common.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_common.c

Purpose: provides shared SPARC Open Firmware device-tree support: console globals, integer property lookup, runtime OF property mutation, string-list search, PROM property iteration quirks, and boot-time PDT-to-OF tree construction.

Important APIs/functions: exports `of_console_device`, `of_console_path`, `of_console_options`, `of_getintprop_default()`, `of_set_property_mutex`, `of_set_property()`, and `of_find_in_proplist()`. Internal helpers are `handle_nextprop_quirks()` and `prom_common_nextprop()`. `prom_build_devicetree()` builds the device tree and initializes the console.

Control flow: property reads return a default unless an exactly 4-byte property exists. `of_set_property()` duplicates the new value, locks a mutex plus `devtree_lock`, calls `prom_setprop()`, updates the in-memory property value/length on success, frees old dynamic values, and marks the property dynamic. Device-tree building uses `of_pdt_build_devicetree()` with SPARC PROM operations, then calls architecture-specific `of_console_init()`.

State and persistence: maintains in-memory OF property lists and console globals. `prom_early_allocated` counts init-time allocations for boot logging. `of_set_property()` also attempts to update firmware property state via PROM, but no filesystem persistence is involved.

Dependencies and integration points: depends on Linux OF/PDT infrastructure, SPARC PROM callbacks (`prom_nextprop`, `prom_getproperty`, `prom_setprop`, child/sibling traversal), `devtree_lock`, and 32/64-bit PROM implementations.

Risks: SPARC32 and SPARC64 `prom_nextprop()` differ, requiring explicit quirk handling. Runtime property mutation must keep firmware and in-memory OF state coherent. The code currently notes procfs update gaps after property changes.

Test signals: early tree build, correct console globals, drivers reading integer properties with defaults, runtime `of_set_property()` success/failure paths, dynamic property replacement without leaks, and property iteration on both SPARC32 and SPARC64 PROMs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_irqtrans.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_irqtrans.c

Purpose: translates Open Firmware interrupt numbers into Linux IRQs for SPARC64 PCI, SBUS, central, and sun4v virtual-device interrupt controllers. It attaches per-node `of_irq_controller` builders during early device-tree setup.

Important APIs/functions: main entry is `irq_trans_init()`. PCI builders include `psycho_irq_build()`, `sabre_irq_build()`, `schizo_irq_build()`, `pci_sun4v_irq_build()`, and `fire_irq_build()` with init functions for PSYCHO, Sabre, Schizo, Tomatillo, sun4v PCI, and Fire. SBUS uses `sbus_of_build_irq()`. Central FHC devices use `central_build_irq()`. Virtual devices use `sun4v_vdev_irq_build()`. DMA ordering prehandlers are `sabre_wsync_handler()` and `tomatillo_wsync_handler()`.

Control flow: `irq_trans_init()` matches a node by PCI model/compatible string, SBUS/SBI name, central/FHC placement, or virtual-device/NIU name, then allocates an IRQ translation object with `prom_early_alloc()`. Each builder masks or transforms the firmware INO/devino, computes controller-specific IMAP and ICLR register addresses, applies INO/IGN fixups where hardware requires them, and calls `build_irq()` or `sun4v_build_irq()`. Sabre and Tomatillo may install prehandlers that drain posted DMA writes before invoking device handlers.

State and persistence: per-device-node state is `dp->irq_trans` plus controller data such as base registers, sync registers, port IDs, chip version, and bus ranges. State exists for runtime IRQ construction and is not persistent.

Dependencies and integration points: depends on OF properties (`reg`, `model`, `compatible`, `bus-range`, `portid`, `version#`), UPA and physical-bypass ASI accesses, SPARC IRQ core (`build_irq`, `irq_install_pre_handler`, `sun4v_build_irq`), PCI/SBUS config layouts, and early PROM allocation.

Risks: register-offset tables are hardware ABI. Wrong INO fixups can route interrupts to the wrong target. Sabre/Tomatillo DMA synchronization is required for correctness behind certain bridges and can hang or log if sync never completes. Bad SYSIO INOs halt the machine. Model matching must include legacy compatible names.

Test signals: boot IRQ enumeration on PSYCHO, Sabre, Schizo, Tomatillo, Fire, SBUS/SYSIO, central, and sun4v virtual-device systems; functional PCI/SBUS device interrupts; DMA completion correctness behind bridges; and logs-free boot with valid `reg`/`model` data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_irqtrans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/psycho_common.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/psycho_common.c

Purpose: provides common support for PSYCHO-family SPARC PCI controllers: streaming-buffer diagnostics, IOMMU error reporting, PCI error interrupt handling, IOMMU initialization, and PBM common initialization.

Important APIs/functions: exported/common functions are `psycho_check_iommu_error()`, `psycho_pcierr_intr()`, `psycho_iommu_init()`, and `psycho_pbm_init_common()`. Internal helpers include `psycho_check_stc_error()`, `psycho_record_iommu_tags_and_data()`, `psycho_dump_iommu_tags_and_data()`, `psycho_pcierr_intr_other()`, and `psycho_iommu_flush()`.

Control flow: PCI error IRQ handling reads AFSR/AFAR, clears primary error bits, logs primary/secondary PCI error types, scans PCI buses for abort/parity sources, and calls IOMMU/STC diagnostics for target aborts. IOMMU diagnostics lock the IOMMU, clear translation error state, snapshot and clear tag/data entries, dump entries with error bits, and inspect streaming-buffer diagnostic tags/lines. IOMMU init enables diagnostic mode, clears old tags/data, allocates and installs the IOMMU page table, sets TSB size, and enables translation.

State and persistence: modifies controller registers, IOMMU fields (`iommu_control`, `iommu_tsbbase`, `iommu_flush`, `iommu_tags`, `write_complete_reg`, page table), and PBM metadata. Static diagnostic buffers are protected by `stc_buf_lock`. All state is hardware/runtime only.

Dependencies and integration points: depends on `pci_pbm_info`, `iommu`/`strbuf` structures, UPA register accessors, PCI config helpers, `iommu_table_init()`, PCI bus error scan helpers, NUMA metadata, and PSYCHO-derived controller drivers that call the common routines.

Risks: diagnostic-mode streaming-buffer probing is explicitly dangerous because dirty STC data can be invalidated if tags are cleared incorrectly. Error handling runs after severe bus faults, so concurrent DVMA may already be corrupting state. TSB size validation only accepts supported sizes. Register bit definitions must match controller manuals.

Test signals: PSYCHO PCI probe, IOMMU table setup for 64K/128K TSBs, DMA through IOMMU, injected/observed PCI parity/abort/SERR conditions, IOMMU translation errors, streaming-buffer error logs, and PBM metadata/resource reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/psycho_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/psycho_common.h -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/psycho_common.h

Purpose: declares shared PSYCHO-family PCI controller helpers and defines config-space address encoding used by common error and setup code.

Important APIs/types/functions: macros `PSYCHO_CONFIG_BASE()` and `PSYCHO_CONFIG_ENCODE()` build controller config-space addresses. `psycho_pci_config_mkaddr()` returns a config-space pointer for bus/devfn/register. `enum psycho_error_type` names UE, CE, and PCI error contexts. Function declarations cover IOMMU checking, PCI error IRQ handling, IOMMU init, and PBM common init.

Control flow: the only executable logic is the inline config address constructor, which ORs controller config-space base with encoded bus, device/function, and register fields.

State and persistence: no state is owned by this header.

Dependencies and integration points: consumed by PSYCHO-derived PCI controller implementations and `psycho_common.c`. It depends on `pci_pbm_info`, platform devices, IRQ return types, and the U2P configuration-space address format.

Risks: config address bit packing is hardware-defined; a small macro error would break all config reads/writes for PSYCHO-family controllers.

Test signals: PCI config space enumeration on PSYCHO-derived controllers, successful reads of root bus PCI status in error handlers, and compile coverage of all declared common functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/psycho_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ptrace_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/ptrace_32.c

Purpose: implements 32-bit SPARC ptrace and core-dump register views for general registers, register windows, floating-point state, legacy ptrace requests, and syscall tracing.

Important APIs/functions: public hooks are `ptrace_disable()`, `task_user_regset_view()`, `arch_ptrace()`, and `syscall_trace()`. Regset helpers include `regwindow32_get/set()`, `genregs32_get/set()`, `fpregs32_get/set()`, `getregs_get()`, `setregs_set()`, `getfpregs_get()`, and `setfpregs_set()`.

Control flow: regset getters flush user windows for the current task, copy global/out registers from `pt_regs`, fetch locals/ins from the user register window using `copy_from_user()` or `access_process_vm()`, and append PSR/PC/NPC/Y. Setters copy incoming data back while restricting PSR writes to condition-code and syscall bits. Legacy `arch_ptrace()` maps SPARC requests such as `PTRACE_GETREGS`, `PTRACE_SETREGS`, `PTRACE_GETFPREGS`, `PTRACE_READTEXT`, and `PTRACE_WRITETEXT` onto regset or generic ptrace helpers, translating `PTRACE_SPARC_DETACH` to `PTRACE_DETACH`.

State and persistence: mutates stopped task `pt_regs`, user register-window memory, `thread.float_regs`, and `thread.fsr`. State is task-local and appears in ptrace/core-dump ABI; no persistent storage is written.

Dependencies and integration points: depends on generic ptrace/regset helpers, ELF notes (`PRSTATUS`, `PRFPREG`, `EM_SPARC`), SPARC register-window layout, `access_process_vm()`, FPU thread state, and syscall entry/exit tracing flags.

Risks: register-window access can fault if the saved user frame pointer is invalid. Regset layout is ABI and must match gdb/core expectations. The FPU save/clear calls are disabled with `#if 0`, so correctness relies on surrounding FPU ownership handling. Partial ptrace data copies must return `-EIO` consistently for legacy APIs.

Test signals: gdb attach/detach, `PTRACE_GETREGS/SETREGS`, FP register access, core dumps with SPARC regsets, text/data read-write ptrace operations, syscall tracing stops on entry/exit, and invalid user-window fault paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ptrace_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ptrace_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/ptrace_64.c

Purpose: implements SPARC64 ptrace, compat ptrace, cache maintenance for ptrace page access, 64-bit and 32-bit user regsets, syscall trace/audit/seccomp hooks, and generic register lookup/stack helpers.

Important APIs/functions: public hooks are `ptrace_disable()`, `flush_ptrace_access()`, `task_user_regset_view()`, `compat_arch_ptrace()`, `arch_ptrace()`, `syscall_trace_enter()`, `syscall_trace_leave()`, `regs_query_register_offset()`, and `regs_get_kernel_stack_nth()`. Regset helpers cover native and compat general/FPU register views plus legacy GETREGS/GETFPREGS layouts.

Control flow: `flush_ptrace_access()` handles D-cache alias invalidation and pre-Cheetah I-cache flushes after `access_process_vm()` copies. Native regsets copy globals/out registers from `pt_regs`, read or write the user register window in 32-bit or biased 64-bit format, and restrict `tstate` writes to condition-code/syscall bits. FPU regsets save current FPU first, then expose lower/upper FP banks, FSR, GSR, and FPRS according to saved flags. Compat paths translate PSR/TSTATE and 32-bit register-window formats. Syscall enter runs strict seccomp, NOHZ user exit, ptrace entry, tracepoint, and audit; syscall leave runs audit, tracepoint, ptrace exit, and NOHZ user enter.

State and persistence: mutates task `pt_regs`, user register-window memory, per-thread FP/VIS state (`fpregs`, `xfsr`, `gsr`, `fpsaved`), and cache lines. Ptrace-visible state is task-local and core-dump-visible; no durable storage is written.

Dependencies and integration points: depends on generic ptrace/regset/compat ptrace APIs, seccomp, audit, syscall tracepoints, SPARC cache ASIs, VIS/FPU helpers, `psrcompat`, `access_process_vm()`, stack-bias conventions, and `thread_info` flags including `TIF_32BIT` and `TIF_NOHZ`.

Risks: cache alias handling is CPU-generation sensitive. Compat register-window setters contain pointer and position arithmetic that must preserve ABI behavior. Allowing only safe TSTATE bits is necessary to prevent privilege/control-state corruption. Syscall tracing order affects seccomp, audit, ptrace, and context tracking semantics.

Test signals: native and 32-bit compat gdb sessions, core dumps for `EM_SPARCV9` and `EM_SPARC`, ptrace text modification on aliasing-cache systems, syscall tracepoints/audit/seccomp ordering, FP/VIS register read-write tests, register offset lookup, and kernel stack nth-entry queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ptrace_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/reboot.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/reboot.c

Purpose: implements SPARC64 reboot, halt, and poweroff hooks using PROM services, plus the serial-console poweroff policy and `pm_power_off` compatibility symbol.

Important APIs/functions: defines `scons_pwroff`, `pm_power_off`, `machine_power_off()`, `machine_halt()`, and `machine_restart()`.

Control flow: poweroff calls `prom_halt_power_off()` unless the console is serial and `scons_pwroff` is disabled, then falls back to `prom_halt()`. Halt directly calls `prom_halt()` and panics if it returns. Restart strips a newline from `reboot_command`, tries the explicit command, then the configured command, then an empty PROM reboot command, and panics if all return.

State and persistence: runtime global `reboot_command` comes from setup/sysctl code, `scons_pwroff` controls serial-console poweroff behavior, and `pm_power_off` points to `machine_power_off`. No persistent state is modified.

Dependencies and integration points: depends on PROM reboot/halt/poweroff operations, OF console device type, generic reboot and PM hooks, and sysctl registration in `setup.c`.

Risks: PROM calls are expected not to return. Serial-console poweroff is policy-sensitive because powering off may remove the only management console. Command string mutation strips at the first newline.

Test signals: `reboot`, `halt`, and `poweroff` commands on serial and non-serial consoles; `/proc/sys/kernel/reboot-cmd`; `/proc/sys/kernel/scons-poweroff`; and panic fallback only if PROM unexpectedly returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/rtrap_32.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/rtrap_32.S

Purpose: low-level SPARC32 return-from-trap path. It handles rescheduling, signal/notify work, buffered register windows, WIM/CWP manipulation, user stack validation, unaligned return PCs, and final `rett`.

Important APIs/symbols: exported labels include `ret_trap_entry`, `ret_trap_lockless_ipi`, `srmmu_rett_stackchk`, and runtime patch labels for 7-window or CPU-specific window-mask code. It calls `schedule`, `do_notify_resume`, `try_to_clear_window_buffer`, `do_memaccess_unaligned`, and `window_ret_fault`.

Control flow: the path first distinguishes kernel versus user returns via `PSR_PS`. User returns check `_TIF_NEED_RESCHED`, call `schedule`, then loop through `_TIF_DO_NOTIFY_RESUME_MASK` handling. If saved windows exist, it enables traps and asks C code to clear the buffer, then rechecks work. Otherwise it loads user outs, verifies there is a live user window or pulls one from the user stack by rotating `%wim`, validates stack alignment and address range, checks PC/NPC alignment, restores registers/Y/PSR, and executes `rett`. Kernel returns repair invalid windows if the return would hit WIM before restoring all registers.

State and persistence: mutates processor PSR, WIM, register windows, thread-info flags/counters, and saved trap-frame state. No persistent storage is involved.

Dependencies and integration points: depends on SPARC32 trap-frame layout, `thread_info` offsets, SRMMU/LEON MMU ASIs, window macros, scheduler, signal code, and setup-time patching for different window counts/CPU models.

Risks: interrupts/traps must be enabled and disabled in exact order around scheduler and user-memory window loads. Incorrect WIM rotation can corrupt register windows. Returning to unaligned PC/NPC must route to fault handling. User stack probing uses MMU status registers and must not expose kernel addresses.

Test signals: syscall/interrupt return to user with pending reschedule or signal, register-window overflow/underflow cases, bad user stack pointer, unaligned PC/NPC fault, kernel trap return with invalid window, LEON and sun4m/sun4d patched instruction paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/rtrap_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/rtrap_64.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/rtrap_64.S

Purpose: low-level SPARC V9 return-from-trap path. It atomically handles user work, preemption, signal delivery, saved user windows, FPU restore depth, interrupt state, MMU context restoration, and final `retry`.

Important APIs/symbols: main labels include `rtrap`, `rtrap_irq`, `rtrap_nmi`, `rtrap_xcall`, `rtrap_no_irq_enable`, `to_user`, `to_kernel`, `rt_continue`, `user_rtt_restore`, and `kern_rtt_restore`. It calls `schedule`/`schedule_user`, `fault_in_user_windows`, `do_notify_resume`, `trace_hardirqs_on`, and `preempt_schedule_irq`.

Control flow: on entry it extracts PIL from `tstate`, skips IRQ tracing for NMI/PIL cases, and branches user versus kernel. User returns clear PSTATE interrupt enable while testing `_TIF_USER_WORK_MASK`, repeatedly handling reschedule, signal/notify, and saved windows with IRQs held off until return. It clears/restores FPU state as required, reloads globals/ins/tpc/tnpc/y/tstate, restores primary context nucleus bits, manages window state (`canrestore`, `otherwin`, `wstate`), fills user register windows for 32-bit or 64-bit stacks if needed, and retries. Kernel returns optionally preempt, then restore nested FPU state based on `TI_FPDEPTH`.

State and persistence: mutates privileged registers (`pstate`, `pil`, `tl`, `tstate`, `tpc`, `tnpc`, `wstate`, window control), MMU context registers, per-thread flags/window/FPU depth fields, and trap-frame slots. Runtime only.

Dependencies and integration points: depends on SPARC V9 trap-frame offsets, sun4v/sun_m7/fast-window runtime patch sections, context tracking, IRQ tracing, scheduler/preemption, signal code, MMU context globals, FPU/VIS save areas, and register-window fill fixup handlers elsewhere.

Risks: the user-return work check must be atomic with interrupts disabled or signals/reschedules can be missed until a later interrupt. NMI returns must avoid softirq/tracing/preemption side effects. ADI requires M7 patching of PSTATE.MCDE on certain transitions. Stack-bias and 32-bit window fill paths are ABI-critical.

Test signals: user syscall/IRQ return with concurrent signal/resched, NMI return, kernel preemption on return from IRQ, saved user windows, 32-bit compat window fill, nested FPU/VIS use, sun4v and M7 patch application, and stress under IRQ tracing/context tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/rtrap_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sbus.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sbus.c

Purpose: initializes UltraSPARC SYSIO/SBUS controller support: 64-bit DVMA slot configuration, SYSIO IRQ construction, ECC/SBUS error interrupt handlers, IOMMU and streaming-buffer setup, Starfire hookup, and OF archdata propagation.

Important APIs/functions: exported API is `sbus_set_sbus64()`. Internal flow uses `sbus_build_irq()`, `sysio_ue_handler()`, `sysio_ce_handler()`, `sysio_sbus_error_handler()`, `sysio_register_error_handlers()`, `sbus_iommu_init()`, and `sbus_init()`.

Control flow: `sbus_init()` iterates OF `sbus` nodes, finds platform devices, initializes SYSIO IOMMU/streaming-buffer state, and propagates archdata. IOMMU init maps controller registers from `reg`, allocates `iommu` and `strbuf`, programs TSB/control registers, clears diagnostic entries, installs the page table, enables streaming buffer and DVMA arbitration, optionally hooks Starfire, then registers UE/CE/SBUS error IRQs and enables ECC/error bits. Error handlers read AFSR/AFAR, clear primary/secondary bits, and print decoded fault details.

State and persistence: attaches `iommu`, `strbuf`, and NUMA archdata to SBUS platform devices; programs hardware registers; stores streaming-buffer flush flag addresses. State is runtime hardware state only.

Dependencies and integration points: depends on OF/platform devices, UPA register access, SPARC IRQ builder, IOMMU common allocation/table code, DMA burst flags, Starfire support, NUMA metadata, and `of_propagate_archdata()` for child devices.

Risks: SYSIO register offsets and INO mapping are fixed hardware contracts. Bad allocation or missing `reg` data is fatal during boot. Error IRQ registration failures halt the machine. `sbus_set_sbus64()` depends on slot-specific config offsets and silently returns for unsupported slots.

Test signals: SBUS boot/probe, child devices receiving IOMMU archdata, SBUS DMA including 64-bit DVMA burst configuration, UE/CE/SBUS error IRQ delivery and logs, Starfire platform hookup, and clean initcall behavior with multiple SBUS nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/setup.c

Purpose: registers SPARC kernel sysctls shared by 32-bit and 64-bit builds for reboot command, STOP-A behavior, serial-console poweroff, and 64-bit TSB ratio.

Important APIs/functions: defines `sparc_sysctl_table` and `init_sparc_sysctls()`, registered with `arch_initcall()`.

Control flow: at arch init time, `register_sysctl_init("kernel", sparc_sysctl_table)` exposes `/proc/sys/kernel/reboot-cmd`, `/proc/sys/kernel/stop-a`, `/proc/sys/kernel/scons-poweroff`, and on SPARC64 `/proc/sys/kernel/tsb-ratio`.

State and persistence: sysctls mutate runtime globals `reboot_command`, `stop_a_enabled`, `scons_pwroff`, and `sysctl_tsb_ratio`. Values are runtime kernel state; persistence is external if user space saves/restores sysctls.

Dependencies and integration points: integrates with generic sysctl registration, reboot/poweroff code, STOP-A PROM break handlers in setup files, and SPARC64 TSB management.

Risks: sysctl names are user-facing ABI. Buffer length for `reboot_command` must match command storage. Permissions allow root writes that directly affect reboot and PROM break behavior.

Test signals: presence and mutability of the sysctls under `/proc/sys/kernel`, reboot command honored by `machine_restart()`, STOP-A enable/disable behavior, serial console poweroff policy, and SPARC64 TSB ratio changes where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/setup_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/setup_32.c

Purpose: performs SPARC32 early boot and architecture setup: PROM sync hook, command-line boot switches, CPU model detection, runtime instruction patching, memory base discovery, root/initrd setup, MMU/paging handoff, STOP-A handling, CPU topology registration, and UP delay calibration finalization.

Important APIs/functions: key entry points are `sparc32_start_kernel()`, `setup_arch()`, `sun_do_break()`, `topology_init()`, and `arch_cpu_finalize_init()`. Helpers include `prom_sync_me()`, `process_switch()`, `boot_flags_init()`, `per_cpu_patch()`, and `leon_patch()`. Globals include `cmdline_memory_size`, `boot_cpu_id`, `reboot_command`, `sparc_cpu_model`, `sparc_ttable`, and `stop_a_enabled`.

Control flow: `sparc32_start_kernel()` initializes PROM, identifies CPU model from `cputypval`, applies LEON patching, and enters `start_kernel()`. `setup_arch()` installs trap table pointer, obtains boot args, parses early params and SPARC switches, registers early PROM console, logs architecture, initializes IDPROM/MMU, computes `phys_base`/`pfn_base` from PROM banks, sets root and ramdisk state, registers PROM sync hook, optionally syncs KADB trap table, applies per-CPU instruction patches, initializes paging, and sets possible CPU map. `topology_init()` counts physical CPUs via PROM and registers online CPUs.

State and persistence: initializes runtime boot globals, physical memory base values, root device flags, early console state, trap table pointer, CPU model, and CPU topology. No durable storage is written.

Dependencies and integration points: depends on PROM services, trap table symbols, LEON/sun4m/sun4d CPU model patch sections, MMU load/paging init, IDPROM, generic root/initrd variables, KADB debug vector, sysctl-shared `stop_a_enabled`, and CPU registration.

Risks: early code runs before normal kernel services. CPU model misclassification selects wrong instruction patches. `mem=` parsing overrides PROM memory size. PROM sync temporarily swaps TBR and is marked broken. Topology registration allocates memory during init and reports errors only through return value.

Test signals: boot on sun4m/sun4d/sun4u/LEON, `mem=` command-line behavior, early PROM console, KADB boot path, PROM `sync` command, STOP-A shell entry, `/proc/cpuinfo` physical CPU count, and instruction patch correctness for LEON/non-LEON systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/setup_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/setup_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/setup_64.c

Purpose: performs SPARC64 early boot and architecture setup: PROM console/boot arguments, boot switches, runtime instruction patching for CPU/hypervisor features, sun4v hypervisor setup, hardware capability reporting, root/initrd/IP autoconfig setup, trap-block initialization, paging, and IRQ stack allocation.

Important APIs/functions: entry points include `start_early_boot()`, `setup_arch()`, `cpucap_info()`, and `sun_do_break()`. Patch helpers are `per_cpu_patch()`, `sun4v_patch_1insn_range()`, `sun4v_patch_2insn_range()`, `sun_m7_patch_2insn_range()`, `sun4v_patch()`, `popc_patch()`, and `pause_patch()`. HWCAP helpers include `mdesc_cpu_hwcap_list()`, `init_sparc64_elf_hwcap()`, and reporting functions.

Control flow: `start_early_boot()` checks Starfire, applies CPU/sun4v patches, initializes CPU poke support, records boot CPU ID, initializes early time, reports PROM, and calls `start_kernel()`. `setup_arch()` reads boot args, parses early params, processes SPARC switches (`-h`, `-p`, `-P`, etc.), optionally registers early PROM console, logs SUN4U/SUN4V, initializes IDPROM/root/initrd/IP-PNP state, initializes the boot CPU trap block, runs paging, computes ELF hardware capabilities from TLB type, sun4v chip type, and MDESC `hwcap-list`, applies popc/pause patches when supported, then allocates per-CPU hardirq and softirq stacks.

State and persistence: initializes runtime globals including `cmdline_memory_size`, `reboot_command`, `sparc64_elf_hwcap`, `stop_a_enabled`, early console flags, root device flags, IRQ stacks, and CPU trap state. HWCAPs become user ABI through ELF auxiliary vectors and `/proc/cpuinfo`.

Dependencies and integration points: depends on PROM, machine description APIs, sun4v hypervisor API init, Starfire, SMP CPU IDs, trap blocks, paging/MMU context, early console, IP autoconfig, memblock, ELF HWCAP definitions, and patch sections emitted by assembly.

Risks: runtime patching writes executable instructions and must flush each patched address. HWCAP bits are user ABI and must reflect real instruction availability. `-P` forcing P-cache taints the kernel and applies only to Cheetah. IRQ stack allocation must happen after possible CPUs are known.

Test signals: boot on sun4u and sun4v chip families, `mem=` and boot switch behavior, HWCAP output and auxv values, MDESC-based capability discovery, popc/pause/sun4v/M7 patch activation, IP-PNP PROM properties, IRQ stack allocation on all possible CPUs, and STOP-A handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/setup_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/signal32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/signal32.c

Purpose: implements 32-bit compat signal handling on SPARC64, including old and RT signal frames, sigreturn paths, V8PLUS extra register state, FPU/register-window save areas, syscall restart, altstack compatibility, and siginfo ABI assertions.

Important APIs/functions: entry points are `do_sigreturn32()`, `do_rt_sigreturn32()`, `do_signal32()`, and `do_sys32_sigstack()`. Helpers include `invalid_frame_pointer()`, `get_sigframe()`, `flush_signal_insns()`, `setup_frame32()`, `setup_rt_frame32()`, `handle_signal32()`, and `syscall_restart32()`.

Control flow: sigreturn validates aligned 32-bit frame pointers, frame FP, PC/NPC alignment, restores Y/PSR-derived condition codes, G/I registers, optional V8PLUS upper halves and ASI, optional FPU and register-window state, signal mask, and altstack for RT frames, then clears syscall restart state. Signal delivery synchronizes user windows, saves/clears FPU, sizes a frame with optional FPU and saved windows, selects altstack, writes register state plus V8PLUS extras, saves FPU/windows, copies siginfo/mask/stack, copies or reconstructs the register-window save area, sets handler arguments, and installs either user restorer or a two-instruction sigreturn trampoline with explicit I-cache flush.

State and persistence: mutates current `pt_regs`, current blocked signal mask, compat altstack fields, FPU saved state, thread saved-window buffer, and user signal-frame memory. State is per-task ABI state only.

Dependencies and integration points: depends on compat signal types, `psrcompat`, `save_fpu_state()`/`restore_fpu_state()`, `save_rwin_state()`/`restore_rwin_state()`, SPARC64 register-window synchronization, page table walking for instruction flush, generic signal selection, and syscall restart conventions using `%g6`.

Risks: frame layout is userspace ABI and protected by static assertions for siginfo offsets. Manual I-cache flushing walks page tables with interrupts disabled to avoid teardown races. V8PLUS upper register reconstruction uses 32-bit indexing into 64-bit regs and is easy to regress. Bad frame validation must reliably force `SIGSEGV`.

Test signals: 32-bit compat signal and RT signal delivery, SA_SIGINFO and non-SA_SIGINFO handlers, user-provided and kernel trampolines, sigaltstack and old sigstack, syscall restart cases, V8PLUS register preservation, FPU and saved-window preservation, and malformed frame fault tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/signal32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/signal_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/signal_32.c

Purpose: implements native SPARC32 signal delivery and return, including old and RT signal frames, FPU/register-window save areas, syscall restart, legacy `sigstack`, and notify-resume integration.

Important APIs/functions: entry points are `do_sigreturn()`, `do_rt_sigreturn()`, `do_notify_resume()`, and `do_sys_sigstack()`. Internal helpers include `invalid_frame_pointer()`, `get_sigframe()`, `setup_frame()`, `setup_rt_frame()`, `handle_signal()`, `syscall_restart()`, and `do_signal()`.

Control flow: sigreturn validates frame alignment/access, saved FP, PC/NPC alignment, restores `pt_regs` or selected RT fields, limits PSR changes to condition codes/FPU enable, clears syscall restart state, restores optional FPU and saved register-window buffers, restores signal mask and altstack, and returns to user. Signal setup synchronizes user windows, computes extra space for FPU/window state, builds an aligned frame on normal or alternate stack, copies current regs and mask, saves FPU/windows if present, copies the current register window into the signal frame, sets handler arguments, points PC/NPC at the handler, and installs either a user restorer or a sigreturn trap trampoline flushed with `flush_sig_insns()`. `do_signal()` handles `%g6` orig-arg preservation and SPARC restart PC rewinding.

State and persistence: modifies current task `pt_regs`, blocked signal mask, altstack state, thread FPU/window buffers, and user stack frames. No external persistence.

Dependencies and integration points: depends on generic signal core, SPARC32 `pt_regs`/PSR/register-window layout, `sigutil` FPU/window helpers, `flush_sig_insns()`, `resume_user_mode_work()`, and syscall restart markers in PSR.

Risks: signal-frame ABI and trampoline instruction encodings are fixed. Register-window save/restore can fault and must synchronize with return-from-trap window handling. `sigstack` is lossy because it guesses stack extent. Incorrect orig `%i0` handling breaks restarted syscalls under ptrace/libc expectations.

Test signals: native SPARC32 signal/RT signal delivery, sigreturn/rt_sigreturn, SA_RESTART and non-restart syscalls, sigaltstack and old sigstack, FPU-using signal handlers, saved register windows, handler restorer and kernel trampoline paths, and malformed user frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/signal_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/signal_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/signal_64.c

Purpose: implements native SPARC64 signal and user-context handling, including `getcontext`/`setcontext`, RT signal frame setup/return, 32-bit compat delegation, syscall restart, uprobe/notify resume, FPU/register-window preservation, and siginfo ABI assertions.

Important APIs/functions: entry points are `sparc64_set_context()`, `sparc64_get_context()`, `do_rt_sigreturn()`, and `do_notify_resume()`. Internal helpers include `invalid_frame_pointer()`, `get_sigframe()`, `setup_rt_frame()`, `syscall_restart()`, and `do_signal()`.

Control flow: `set_context` validates user context, optionally restores signal mask, applies PC/NPC alignment and 32-bit truncation, restores safe TSTATE bits, selected globals/outs, register-window FP/I7 slots, and optional FPU state. `get_context` clears a user context, advances past the trap instruction, writes mask/register/window/FPU metadata, and signals on faults. RT sigreturn validates the biased frame, restores PC/NPC, Y, safe TSTATE bits, all user regs, optional FPU/window state, mask and altstack, clears syscall state, then returns. Signal delivery delegates to `do_signal32()` for `TIF_32BIT`; otherwise it saves windows/FPU, builds an aligned RT frame, saves regs/mask/altstack/siginfo/window state, sets handler arguments according to the SPARC64 libc sigcontext convention, and uses the user-provided restorer.

State and persistence: mutates current `pt_regs`, signal mask, altstack state, FPU/VIS saved state, register-window buffers, and user ucontext/signal-frame memory. No persistent storage.

Dependencies and integration points: depends on generic signal/uprobes/resume-user-mode work, context tracking, compat signal32 code, SPARC64 ucontext ABI, stack-bias rules, `save_fpu_state()`/`restore_fpu_state()`, register-window helpers, and syscall restart conventions.

Risks: native SPARC64 requires a user restorer for signal return. `set_context` deliberately skips `%g7` because it is the user thread register. Safe TSTATE masking is critical to avoid privilege-state corruption. Bias handling for frame and saved FP values is error-prone, especially when dispatching compat tasks.

Test signals: 64-bit signal delivery/rt_sigreturn, libc `getcontext`/`setcontext`, signal masks and altstack restoration, FPU/VIS state preservation, saved register windows, syscall restart behavior, uprobe notify resume, compat 32-bit signal delegation, and malformed biased frame tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/signal_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sigutil.h -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sigutil.h

Purpose: declares shared SPARC signal helpers for saving/restoring FPU state and register-window state into signal-frame side buffers.

Important APIs/functions: declares `save_fpu_state()`, `restore_fpu_state()`, `save_rwin_state()`, and `restore_rwin_state()`.

Control flow: no executable logic is present. The header provides common prototypes for `signal_32.c`, `signal32.c`, `signal_64.c`, and the SPARC32 implementation in `sigutil_32.c` or corresponding 64-bit implementation.

State and persistence: no state is owned by the header.

Dependencies and integration points: depends on `struct pt_regs`, SPARC signal-frame FPU/window types, and user pointer annotations from architecture headers.

Risks: prototypes must remain synchronized with all signal implementations. These helpers are ABI-facing because they serialize task state into user signal frames.

Test signals: compile coverage for all signal files and runtime signal tests that include FPU and saved register-window state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sigutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sigutil_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/sigutil_32.c

Purpose: implements SPARC32 signal helper routines that serialize/restore FPU state and buffered register windows for signal frames.

Important APIs/functions: implements `save_fpu_state()`, `restore_fpu_state()`, `save_rwin_state()`, and `restore_rwin_state()`. It uses external FPU save logic through `fpsave()` and shared state such as `last_task_used_math` or `TIF_USEDFPU`.

Control flow: `save_fpu_state()` forces FPU state into `current->thread`, clears live FPU ownership, copies float registers/FSR/queue depth and optional queue entries to user memory, then clears used-math state. `restore_fpu_state()` validates alignment/access, clears live FPU ownership, marks used-math, copies registers/FSR/queue depth and optional queue entries back into the thread. `save_rwin_state()` copies each buffered register window and stack pointer to the user side buffer. `restore_rwin_state()` validates count, copies windows and stack pointers back, sets `w_saved`, then calls `synchronize_user_stack()` and fails if any windows remain buffered.

State and persistence: mutates current FPU ownership flags, `thread.float_regs`, `thread.fsr`, `thread.fpqueue`, `thread.fpqdepth`, used-math state, `thread_info.reg_window`, `rwbuf_stkptrs`, and `w_saved`. User signal-frame buffers receive serialized state.

Dependencies and integration points: used by SPARC32 signal setup/return, depends on SMP versus UP FPU ownership conventions, `access_ok()`, user copy helpers, `NSWINS`, and register-window synchronization.

Risks: FPU ownership differs for SMP and UP and must clear PSR_EF/TIF state consistently. Register-window restore accepts user-provided saved windows and must bound `wsaved` to `NSWINS`. A restored window set that cannot be synchronized back to user stack is treated as `-EFAULT`.

Test signals: signal delivery to FPU-using tasks, restore of FPU queue state, SMP and UP FPU ownership transitions, signals with saved register windows, invalid FPU/window buffer alignment, overlarge `wsaved`, and faulting user copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/sigutil_32.c -->
