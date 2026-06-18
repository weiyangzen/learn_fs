# subset-b-000627 Research

This grouped report covers Alpha architecture kernel sources under `sources/distributed-fs/ceph-client/arch/alpha/kernel/`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/pci_impl.h -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/pci_impl.h

## Purpose
`pci_impl.h` is the private Alpha PCI implementation contract used by host bridge, platform vector, and IOMMU code in this directory. It centralizes default PCI I/O and memory allocation base constants, explains Alpha-specific interrupt swizzling assumptions, declares the shared PCI hose and IOMMU arena state, and exposes helper APIs used by board support files and common PCI initialization.

## Important APIs, Types, And Constants
- PCI resource constants include `EISA_DEFAULT_IO_BASE`, `DEFAULT_IO_BASE`, `XL_DEFAULT_MEM_BASE`, `APECS_AND_LCA_DEFAULT_MEM_BASE`, `MCPCIA_DEFAULT_MEM_BASE`, `T2_DEFAULT_MEM_BASE`, `DEFAULT_MEM_BASE`, `CIA_DEFAULT_MEM_BASE`, `IRONGATE_DEFAULT_MEM_BASE`, and `DEFAULT_AGP_APER_SIZE`. These encode host-bridge and board-specific limitations such as sparse-space reachability, HAE avoidance, and BIOS/VGA side effects around I/O addresses.
- `COMMON_TABLE_LOOKUP` is the shared table-driven IRQ mapping macro for many single-bus Alpha platform files. It maps PCI slot/pin to an IRQ table entry when `slot` and `pin` are inside caller-provided bounds.
- `struct pci_iommu_arena` is the core IOMMU allocation unit: it holds a spinlock, owning `pci_controller`, PTE table, DMA base, window size, next allocation pointer, and allocation alignment. Its PTE sentinel values `IOMMU_INVALID_PTE` and `IOMMU_RESERVED_PTE` are consumed by `pci_iommu.c`.
- SRM restore feature macros define whether `pci_restore_srm_config()` is a real external function or a no-op. This matters during reboot/halt paths that must put firmware-visible PCI state back.
- Externs expose `hose_head`, `hose_tail`, `pci_isa_hose`, `alpha_agpgart_size`, `common_init_pci()`, `alloc_pci_controller()`, `alloc_resource()`, `iommu_arena_new[_node]()`, `size_for_memory()`, and AGP/IOMMU reservation helpers.

## Control Flow And Integration
This header has no runtime control flow beyond macros, but it drives downstream behavior. Platform files include it to choose default resource bases and to use `COMMON_TABLE_LOOKUP` in their `pci_map_irq` implementations. `pci_iommu.c` implements the declared arena and AGP helpers. `process.c` calls `pci_restore_srm_config()` during SRM shutdown when restoration is enabled. Host bridge code and platform vectors depend on the global hose list and resource allocators declared here.

## State And Persistence
State is externalized: the header defines the shape of `pci_iommu_arena` and declares global hose pointers and AGP aperture size. Those are process-lifetime kernel structures, initialized during boot and used for DMA mappings until shutdown. There is no disk persistence; firmware-visible state can be restored through the conditional SRM restore hook.

## Dependencies And Integration Points
The header assumes Linux PCI types, Alpha `pci_controller` and machine-vector infrastructure, and Alpha-specific SRM/CIA configuration options. It is tightly coupled to `pci_iommu.c`, `bios32.c`/PCI setup code, host bridge sources, and board support files such as `sys_alcor.c` and `sys_cabriolet.c`.

## Risks
- Constants are board- and bridge-specific; changing them can break device resource assignment, sparse-space access, or firmware compatibility.
- `COMMON_TABLE_LOOKUP` depends on caller-local variables named `slot`, `pin`, `min_idsel`, `max_idsel`, `irqs_per_slot`, and `irq_tab`, so misuse can fail at compile time or silently map wrong interrupts.
- `struct pci_iommu_arena` is shared with low-level DMA code; field semantics and sentinel values must remain aligned with IOMMU allocator logic.

## Test Signals
- Alpha PCI boot logs showing expected I/O and memory resource assignment.
- PCI devices receive stable IRQs on each supported board.
- DMA tests through `alpha_pci_ops`, including AGP aperture reservation when enabled.
- SRM reboot/halt smoke tests on configurations with `ALPHA_RESTORE_SRM_SETUP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/pci_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/pci_iommu.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/pci_iommu.c

## Purpose
`pci_iommu.c` implements Alpha PCI DMA mapping operations. It chooses among direct-map DMA windows, DAC addressing, and scatter-gather IOMMU arenas; maintains arena PTE allocation; maps and unmaps streaming and coherent buffers; maps scatterlists; and exposes AGP GART reservation/bind APIs. Its public output is `alpha_pci_ops`, the `dma_map_ops` table used by devices on Alpha PCI systems.

## Important APIs, Types, And Functions
- `mk_iommu_pte()` builds a valid Alpha IOMMU PTE from a physical address.
- `size_for_memory()` returns a power-of-two window size no larger than a cap and at least large enough for low memory.
- `iommu_arena_new_node()` and `iommu_arena_new()` allocate boot-time IOMMU arena structures and PTE arrays with `memblock_alloc_or_panic()`.
- `iommu_arena_find_pages()`, `iommu_arena_alloc()`, and `iommu_arena_free()` implement locked bitmap-like PTE allocation by scanning the PTE table for zero entries, honoring segment-boundary constraints and alignment.
- `pci_dac_dma_supported()` checks whether a PCI device and machine vector can use DAC addressing via `alpha_mv.pci_dac_offset`.
- `pci_map_single_1()` is the central single-buffer mapper. It first tries the direct window, then DAC when allowed, then host-bridge SG/ISA IOMMU arenas.
- `alpha_gendev_to_pci()` maps generic `struct device` pointers to PCI devices, ISA bridge pseudo-devices, or NULL for ISA bus masters.
- `alpha_pci_map_phys()`, `alpha_pci_unmap_phys()`, `alpha_pci_alloc_coherent()`, and `alpha_pci_free_coherent()` implement DMA map/unmap and coherent allocation hooks.
- `sg_classify()`, `sg_fill()`, `alpha_pci_map_sg()`, and `alpha_pci_unmap_sg()` merge scatterlist entries, choose direct/DAC/IOMMU mappings, and release mappings.
- `alpha_pci_supported()` answers `dma_supported`.
- `iommu_reserve()`, `iommu_release()`, `iommu_bind()`, and `iommu_unbind()` are AGP/GART-style arena reservation helpers.
- `alpha_pci_ops` wires these functions into the DMA mapping layer and reuses common mmap/sgtable/page allocation helpers.

## Control Flow
Single-buffer mapping starts in `alpha_pci_map_phys()`, rejects `DMA_ATTR_MMIO`, converts generic devices, checks DAC eligibility, and delegates to `pci_map_single_1()`. `pci_map_single_1()` returns immediately for direct-map or DAC-capable addresses. If those fail, it requires `alpha_mv.mv_pci_tbi`, selects `hose->sg_pci` unless it exceeds the device mask, falls back to `hose->sg_isa`, allocates PTEs, writes PTEs for each page, and returns the DMA window address plus original offset. Unmapping reverses this by recognizing direct/DAC addresses, otherwise freeing arena PTEs and flushing the IOMMU TLB if freed entries lie beyond the next allocation pointer.

Scatter-gather mapping classifies entries into physical or virtual runs, chooses an arena if the platform has a TBI function, and emits compact DMA segments. `sg_fill()` uses direct/DAC for physically contiguous leaders and IOMMU mappings for virtual contiguity. If IOMMU allocation fails for a virtually contiguous run, it reclassifies without virtual merging and retries. Unmap walks the mapped output entries until a zero `dma_length` marker and frees only IOMMU-backed ranges.

AGP helpers reserve PTE ranges as `IOMMU_RESERVED_PTE`, later bind them to page arrays, and unbind them back to reserved state rather than free state.

## State And Persistence
Persistent in-kernel state lives in each `pci_iommu_arena`: a PTE array, spinlock, allocation cursor, base, size, and alignment. PTE values track free (`0`), invalid in-use, reserved AGP ranges, or valid physical mappings. Coherent allocations allocate kernel pages and map them through the same DMA path. There is no disk persistence, but incorrect arena state persists until reboot and can corrupt future DMA mappings.

## Dependencies And Integration Points
The code depends on Alpha machine-vector fields (`alpha_mv.mv_pci_tbi`, `alpha_mv.pci_dac_offset`), PCI hose fields (`sg_pci`, `sg_isa`), global direct-map exports (`__direct_map_base`, `__direct_map_size`), `isa_bridge`, Linux DMA/IOMMU helpers, scatterlist APIs, and memblock boot allocation. It is integrated through `alpha_pci_ops`, which architecture setup assigns to devices.

## Risks
- The arena allocator is linear and cursor-based; fragmentation or repeated large mappings can cause allocation failures until wrap and TLB flush.
- `alpha_gendev_to_pci()` uses `BUG_ON(!isa_bridge)` for non-PCI devices, so unexpected device classes can crash the kernel.
- Some error paths assume `pdev` is non-NULL when unmapping via generic DMA APIs; ISA/NULL handling should be treated carefully.
- SG code temporarily overloads `dma_address` and `dma_length` for classification markers, so changes must preserve marker interpretation.
- Incorrect TLB flush boundaries can leave stale DMA translations visible to hardware.

## Test Signals
- Boot on Alpha systems with and without `mv_pci_tbi`.
- DMA API tests covering streaming map/unmap, coherent allocation, SG mapping, direct window, DAC, and ISA-mask-limited devices.
- Stress with small/large scatterlists to exercise coalescing and allocation fallback.
- AGP/GART reservation tests verifying reserve-bind-unbind-release state transitions.
- Kernel warnings `pci_map_single failed`, `Bogus pci_unmap_single`, and SG allocation failures should be absent under normal device workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/pci_iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/perf_event.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/perf_event.c

## Purpose
`perf_event.c` provides Linux perf hardware counter support for Alpha EV67-class CPUs and later compatible EV6/EV7 variants. It maps perf event types onto the Alpha PAL `wrperfmon` interface, schedules up to two EV67 PMCs under hardware pairing constraints, handles overflow interrupts, and registers a CPU PMU named `cpu`.

## Important APIs, Types, And Functions
- `struct cpu_hw_events` is per-CPU scheduling state: enabled flag, scheduled events, event types, current PMC indices, aggregate config, and active index mask.
- `struct alpha_pmu_t` describes a CPU PMU: event map, number of PMCs, bit shifts/masks, max periods, minimum counter-left values, constraint checker, and raw event validator.
- EV67-specific event identifiers include cycles, instructions, Bcache misses, and Mbox replay traps. `ev67_perfmon_event_map` maps Linux hardware events to these IDs; cache references are unsupported.
- `ev67_check_constraints()` validates one- or two-event combinations and assigns PMC indices/configs. Hardware only supports specific pairings such as instructions+cycles, instructions+Bcache misses, and cycles+Mbox replay.
- `alpha_write_pmc()` and `alpha_read_pmc()` isolate PMC bitfields inside the PCTR register via `wrperfmon`.
- `alpha_perf_event_set_period()` reloads a counter while respecting hardware limits near max period.
- `alpha_perf_event_update()` calculates deltas, including explicit overflow correction from the interrupt handler.
- `collect_events()` and `alpha_check_constraints()` validate perf groups.
- PMU callbacks `alpha_pmu_add`, `del`, `read`, `stop`, `start`, `enable`, `disable`, and `event_init` implement Linux perf operations.
- `alpha_perf_event_irq_handler()` services PMI overflows and calls `perf_event_overflow()`.
- `init_hw_perf_events()` detects supported CPUs, installs `perf_irq`, sets `alpha_pmu`, and registers the PMU at `early_initcall`.

## Control Flow
At early init, `supported_cpu()` reads CPU type from HWRPB and enables PMU support only for EV67 through EV69-compatible types. Event initialization validates event type, maps to Alpha event ID, checks group constraints, and leaves hardware config/PMC index unresolved until scheduling. Adding an event disables the PMU, disables interrupts, appends it if constraints allow, marks start/stop state, and reenables. PMU enable recomputes configuration when events were added, programs logging options and desired events, then enables the active PMC mask.

On overflow, the handler disables PMCs to avoid nested overflows, validates the overflow index from `la_ptr`, finds the matching scheduled event, updates its count with one full-period correction, reloads the period, reports overflow when needed, and reenables active counters.

## State And Persistence
PMU state is per-CPU in `cpu_hw_events`; event state lives in each `perf_event->hw`, including `event_base`, `config_base`, `idx`, `prev_count`, `period_left`, and state flags. Global `alpha_pmu` is set once at boot. Counts persist in perf event objects until deleted. No disk persistence exists.

## Dependencies And Integration Points
The file depends on Linux perf core, PAL `wrperfmon`, HWRPB CPU descriptors, Alpha interrupt plumbing through global `perf_irq`, per-CPU IRQ counters such as `irq_pmi_count`, and perf group APIs. It does not arbitrate PMU ownership with any other subsystem.

## Risks
- Counter overflow handling is inherently race-prone; the code compensates for negative deltas but depends on PMI timing and hardware period size.
- Only a narrow EV67 PMU model is supported. Later or earlier CPUs with subtly different counters may be misdetected or unsupported.
- Constraint logic assumes at most two events for EV67 and uses `BUG_ON(n_ev != 2)` in the multi-event path.
- `PERF_PMU_CAP_NO_EXCLUDE` means exclude-user/kernel settings are not honored.
- Raw event validation accepts only internal event IDs, not arbitrary PAL configurations.

## Test Signals
- Boot logs should show either unsupported CPU or supported CPU perf registration.
- `perf stat -e cycles,instructions` should work on supported Alpha hardware.
- Unsupported cache events should return `-EOPNOTSUPP` or `-EINVAL`.
- Group scheduling tests should accept valid EV67 pairings and reject invalid pairs.
- Sampling workloads should increment counts and handle overflow without `PMI: silly index` or `No event at index` warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/perf_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/process.c

## Purpose
`process.c` implements Alpha-specific process lifecycle hooks: idle support, restart/halt/poweroff, SRM-aware shutdown cleanup, register display, exec-thread setup, thread cloning, ELF core register export, floating-point core export, and wait-channel lookup.

## Important APIs, Types, And Functions
- `pm_power_off` defaults to `machine_power_off` and is exported.
- `arch_cpu_idle()` and `arch_cpu_idle_dead()` use `wtint()` on `CONFIG_ALPHA_WTINT` systems.
- `struct halt_info` carries reboot mode and optional restart command across `on_each_cpu()`.
- `common_shutdown_1()` is the low-level per-CPU shutdown handler.
- `machine_restart()`, `machine_halt()`, and `machine_power_off()` all call `common_shutdown()`.
- `show_regs()` delegates to `dik_show_regs()`.
- `start_thread()` sets user PC, user PS, and user stack pointer for exec.
- `flush_thread()` resets FPU exception state and TLS/UNIQUE.
- `copy_thread()` builds child kernel stacks for fork and kernel threads.
- `dump_elf_thread()`, `dump_elf_task()`, and `elf_core_copy_task_fpregs()` export register state for ELF core dumps.
- `thread_saved_pc()` and `__get_wchan()` derive blocked-thread wait PCs from Alpha switch stack frames.

## Control Flow
Shutdown is broadcast to all CPUs. Secondaries clear HWRPB flags, mark themselves not present/possible, and halt. The boot CPU records warm/cold bootstrap or halt flags in its HWRPB per-CPU structure, waits for other CPUs to disappear, restores SRM console/video/PCI/HAE state when booted from SRM, invokes `alpha_mv.kill_arch()`, optionally stops SRM paging, and halts. Non-SRM halt/poweroff may return to a loop because MILO cannot reliably honor HWRPB halt state.

`copy_thread()` handles two paths. Kernel threads get zeroed child frames, `ret_from_kernel_thread`, function pointer/argument in saved registers, HAE cache, zeroed FP state, and no user stack. User clones inherit register and switch-stack state, set child return registers for fork semantics, optionally set TLS from `CLONE_SETTLS`, and arrange return through `ret_from_fork`.

## State And Persistence
Shutdown mutates HWRPB per-CPU flags, CPU masks, HAE state, and possibly PCI configuration visible to SRM. Thread setup mutates `thread_info` PCB fields, FPU save area, stack frames, and TLS/UNIQUE. Core dump helpers read stack and thread state without persistence.

## Dependencies And Integration Points
The file depends on HWRPB layout, Alpha PAL/halt primitives, SRM status from `setup.c`, machine-vector `kill_arch` and `hae_cache`, PCI SRM restore from `pci_impl.h`, SMP CPU masks, `ret_from_fork`/`ret_from_kernel_thread` assembly entries, FPU helpers, and ELF core infrastructure.

## Risks
- Shutdown paths manipulate interrupt and console state in unusual contexts, including hardirq SysRq paths.
- `__get_wchan()` depends on fragile stack-frame layout and schedule frame offsets.
- Incorrect fork register semantics can break OSF/1-compatible ABI expectations around `r20`.
- SRM restore and HAE restore order matters for firmware reboot reliability.

## Test Signals
- Reboot/halt/poweroff under SRM and non-SRM boot paths.
- SMP shutdown confirms secondaries halt and CPU masks drain.
- Fork, clone with `CLONE_SETTLS`, kernel thread creation, and exec smoke tests.
- ELF core dumps contain expected integer, UNIQUE, user stack, and FP register data.
- `ps`/wait-channel reporting remains stable under blocked tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/proto.h -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/proto.h

## Purpose
`proto.h` is the internal Alpha kernel cross-file declaration hub. It collects prototypes, global variables, low-level assembly entry declarations, platform host-bridge hooks, SRM console hooks, SMP hooks, RTC hooks, trap/signal/ptrace functions, and machine-check helpers used among files in `arch/alpha/kernel`.

## Important APIs, Types, And Declarations
- Volatile pointer aliases `vucp`, `vusp`, `vip`, `vuip`, and `vulp` support memory-mapped register access in board files.
- Host bridge sections declare CIA/PYXIS, Irongate, Marvel, MCPCIA, Polaris, T2, Titan, Tsunami, and Wildfire operations including PCI ops, architecture init/kill, machine checks, and PCI TBI callbacks.
- Console declarations expose VGA hose discovery when `CONFIG_VGA_HOSE` is enabled.
- Setup globals include `srm_hae`, `boot_cpuid`, optional `alpha_verbose_mcheck`, `move_initrd()`, and `vgacon_screen_info`.
- SRM console declarations are conditional no-ops when unavailable.
- SMP declarations expose `setup_smp()`, `handle_ipi()`, and `smp_callin()`.
- RTC declarations expose `rtc_timer_interrupt()`, `init_clockevent()`, `common_init_rtc()`, and `est_cycle_freq`.
- Super I/O init declarations expose `SMC93x_Init()` and `SMC669_Init()`.
- Assembly/PAL declarations include FP register helpers, `wrmces`, console-service enable/disable, `__smp_callin`, and trap entry symbols.
- Ptrace/signal/trap declarations expose syscall tracing, signal returns, pending-work processing, register display, trap handlers, and unaligned access handlers.
- `__alpha_remap_area_pages()` builds Alpha kernel page protections and calls `ioremap_page_range()`.
- `mcheck_expected/taken/extra` macros abstract machine-check state for SMP and UP builds.

## Control Flow
The header has little direct flow. Its main executable helper, `__alpha_remap_area_pages()`, constructs a kernel read/write, ASM-valid `pgprot_t` and maps a physical range. The machine-check macros route to per-CPU `cpu_data` under SMP or a single `__mcheck_info` structure under UP.

## State And Persistence
The header declares shared global boot state and machine-check state but does not allocate most of it. The inline remap helper changes kernel page tables through generic ioremap APIs. All state is volatile kernel runtime state.

## Dependencies And Integration Points
Nearly every file in this subset includes `proto.h` for cross-module hooks. It depends on Linux interrupt, screen, and I/O headers plus Alpha-specific structures. It is especially coupled to `setup.c`, `smp.c`, `rtc.c`, `signal.c`, `ptrace.c`, trap handling, host bridge files, and board support vectors.

## Risks
- Because this is a broad internal declaration header, stale prototypes can hide cross-file ABI changes until link or runtime failures.
- Conditional no-op SRM/VGA helpers must match call-site expectations in generic builds.
- Low-level assembly prototypes need exact signatures; mismatches can corrupt registers or stack state.
- Machine-check state macros evaluate CPU arguments differently in SMP/UP builds, so side effects in arguments would be dangerous.

## Test Signals
- Full Alpha kernel build across generic, SMP, SRM, VGA, and board-specific configs.
- Link-time coverage for all weak or conditional symbols.
- Boot tests that exercise setup, trap, signal, ptrace, RTC, and SMP hooks.
- I/O remapping users successfully map and access expected physical ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/ptrace.c

## Purpose
`ptrace.c` implements Alpha architecture ptrace support: register access, user memory peek/poke, software single-step through breakpoint patching, regset access, syscall trace entry/exit, audit integration, and seccomp enforcement.

## Important APIs, Types, And Functions
- `BREAKINST` is the Alpha breakpoint instruction `call_pal bpt`.
- `regoff[]` maps Alpha integer registers, floating registers, and PC to offsets in the task stack or `thread_info`.
- `get_reg_addr()`, `get_reg()`, and `put_reg()` read/write Alpha register slots, including special handling for user stack pointer (`r30`), UNIQUE (`65`), zero register, and FPCR/software IEEE state.
- `read_int()` and `write_int()` patch child text through `access_process_vm()`.
- `ptrace_set_bpt()` computes future execution addresses and writes breakpoint instructions for single-step.
- `ptrace_cancel_bpt()` restores saved instructions and clears pending breakpoint state.
- `user_enable_single_step()`, `user_disable_single_step()`, and `ptrace_disable()` integrate with generic ptrace stepping hooks.
- `arch_ptrace()` handles Alpha-specific peek/poke, register, and regset requests, delegating unknown requests to `ptrace_request()`.
- `syscall_trace_enter()` handles syscall-entry ptrace, seccomp, audit entry, syscall cancellation, and return-value setup.
- `syscall_trace_leave()` emits audit and ptrace syscall-exit notifications.

## Control Flow
Register peek/poke requests route through `arch_ptrace()`. Legacy `PTRACE_PEEKUSR/POKEUSR` access register numbers directly; `GETREGSET/SETREGSET` currently supports only `NT_PRSTATUS` and copies raw `pt_regs` to/from a user iovec, updating `iov_len`.

Single-step is software-based. `user_enable_single_step()` marks stepping with `bpt_nsaved = -1`; the signal path later calls `ptrace_set_bpt()`. That function reads the current instruction at PC, determines whether it is a branch, jump, or normal instruction, computes one or two possible next PCs, saves original instructions, and writes `BREAKINST` at those addresses. `ptrace_cancel_bpt()` restores those instructions before signal handling or detach.

Syscall entry reports to ptrace first; if tracing cancels the syscall, it sets syscall number to `-1` and may synthesize `-ENOSYS`. Seccomp runs after ptrace and follows the same cancellation convention. Audit entry runs only if the syscall remains valid.

## State And Persistence
Single-step state persists in `thread_info` fields `bpt_addr[]`, `bpt_insn[]`, and `bpt_nsaved` between ptrace operations and signal handling. Register writes mutate saved task stack frames and `thread_info` FPU/IEEE state. There is no persistent storage.

## Dependencies And Integration Points
This file depends on Alpha stack layout, `pt_regs`, `switch_stack`, FPU state helpers, Linux ptrace core, seccomp, audit, generic ptrace memory helpers, signal delivery (`signal.c` calls breakpoint helpers), and syscall register helpers from `asm/syscall.h`.

## Risks
- Breakpoint single-step writes into traced process memory; failures during partial installation can leave inconsistent state.
- Branch displacement and jump-target decoding must match Alpha instruction encoding.
- `GETREGSET/SETREGSET` copies raw `pt_regs`, not the legacy full register numbering including FP registers.
- `get_reg_addr()` returns a shared static `zero` for invalid/zero registers; writes to invalid registers silently write that temporary.
- Seccomp/ptrace ordering is intentional and sensitive to syscall cancellation semantics.

## Test Signals
- `strace` and `gdb` on Alpha for syscall tracing, register reads/writes, and single-step through branches and jumps.
- Ptrace tests for `PTRACE_GETREGSET/SETREGSET` with `NT_PRSTATUS`.
- Seccomp trace/errno actions combined with ptrace syscall cancellation.
- Signal delivery while single-stepping should restore old instructions and deliver `SIGTRAP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/rtc.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/rtc.c

## Purpose
`rtc.c` provides an Alpha-specific RTC class device around the MC146818-compatible CMOS clock. It avoids the generic `rtc-cmos` alarm-capable driver because alarm interrupts are indistinguishable from timer interrupts on these systems, and it handles non-1900 RTC epochs used by Alpha firmware and operating systems.

## Important APIs, Types, And Functions
- `rtc_epoch` stores the active RTC epoch and can be set with the boot parameter `epoch=`.
- `specifiy_epoch()` parses the boot parameter, accepting epochs at or after 1900.
- `init_rtc_epoch()` detects PC, NT, Digital UNIX, or 2000-style epoch based on CMOS year.
- `alpha_rtc_read_time()` reads via `mc146818_get_time()` and adjusts `tm_year` for non-1900 epochs.
- `alpha_rtc_set_time()` reverses the epoch adjustment before `mc146818_set_time()`.
- `alpha_rtc_ioctl()` implements `RTC_EPOCH_READ` and `RTC_EPOCH_SET`.
- `alpha_rtc_ops` is the normal RTC ops table.
- Under selected SMP generic/Marvel configs, `remote_rtc_ops` marshals reads/writes to `boot_cpuid` through `smp_call_function_single()` when `alpha_mv.rtc_boot_cpu_only` is true.
- `alpha_rtc_init()` registers platform device `rtc-alpha`, allocates an RTC device, assigns ops, and registers it at `device_initcall`.

## Control Flow
Initialization detects or accepts an epoch, registers a simple platform device, allocates an RTC class device, selects normal or remote ops, and registers with the RTC core. Read calls fetch CMOS time using generic MC146818 logic, then undo/reapply century adjustment if the epoch is not 1900. Set calls subtract the epoch delta before programming CMOS. Remote ops execute the same read/set functions on the boot CPU for hardware that only permits CMOS access there.

## State And Persistence
`rtc_epoch` is runtime kernel state and can be changed through ioctl. The CMOS RTC hardware persists date/time across reboots. The code intentionally does not support alarms. Platform and RTC device registration persists for the lifetime of the kernel.

## Dependencies And Integration Points
The file depends on Linux RTC class, platform device APIs, MC146818 CMOS helpers, BCD conversion, Alpha `alpha_mv.rtc_boot_cpu_only`, `boot_cpuid`, and SMP call-function support. Time initialization elsewhere uses `common_init_rtc()` declared in `proto.h`.

## Risks
- The boot parameter function name is misspelled `specifiy_epoch`, but the `__setup("epoch=", ...)` binding is correct.
- Epoch inference from two-digit CMOS year is heuristic; unusual firmware settings can produce wrong years.
- Remote RTC access must not deadlock if invoked in contexts unsuitable for synchronous cross-CPU calls.
- `platform_device_register_simple()` failure is not checked before using `pdev->dev`, which is a potential robustness issue.

## Test Signals
- Boot logs show chosen epoch and RTC year.
- `hwclock`/RTC class reads produce expected full year across PC, NT, Digital UNIX, and 2000 epochs.
- `RTC_EPOCH_READ/SET` ioctl tests reject epochs before 1900 and affect subsequent read/set conversion.
- SMP boot-CPU-only platforms can read/set RTC from non-boot CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/setup.c

## Purpose
`setup.c` is the central Alpha architecture boot setup file. It parses firmware/HWRPB state and command-line overrides, selects the `alpha_machine_vector`, initializes SRM callbacks, memory, HAE, resources, machine architecture hooks, console defaults, SMP discovery, paging, CPU cache descriptors, `/proc/cpuinfo`, panic handling, and a PC speaker platform device.

## Important APIs, Types, And Functions
- Global boot state includes `hwrpb`, `srm_hae`, cache shape globals, `alpha_verbose_mcheck`, `boot_cpuid`, `srmcons_output`, `mem_size_limit`, `alpha_agpgart_size`, `alpha_mv`, `alpha_using_srm`, `alpha_using_qemu`, `__direct_map_base`, and `__direct_map_size`.
- Weak machine vector declarations allow generic kernels to reference many board vectors.
- `reserve_std_resources()` reserves legacy PC-compatible I/O regions under the first hose or global I/O resource.
- `get_mem_size_limit()` parses `mem=` and `gartsize=` units.
- `move_initrd()` relocates initrd below the memory limit when needed.
- `setup_memory()` reads HWRPB memory clusters, adds/reserves memblock ranges, applies memory limits, reserves kernel/initrd memory, and sets `max_low_pfn`.
- `page_is_ram()` checks if a PFN belongs to a non-reserved HWRPB memory cluster.
- `register_cpus()` creates CPU devices for possible CPUs.
- `setup_arch()` is the boot entry point for most architecture setup.
- `get_sysvec()`, `get_sysvec_byname()`, and `get_sysnames()` map HWRPB type/variation/CPU to machine vectors and printable names.
- `platform_string()`, `show_cpuinfo()`, and `cpuinfo_op` back `/proc/cpuinfo`.
- `determine_cpu_caches()` and `external_cache_probe()` populate cache shape data.
- `alpha_panic_event()` hard-halts certain SRM console panic paths.
- `add_pcspkr()` registers `pcspkr`.

## Control Flow
`setup_arch()` starts by locating the HWRPB, capturing boot CPU ID, normalizing negative system types, registering the panic notifier, detecting SRM/MILO and QEMU, initializing SRM callbacks, and parsing command-line options such as `alpha_mv=`, `cycle=`, `mem=`, `srmcons`, `console=srm`, `gartsize=`, and `verbose_mcheck=`.

It then optionally registers SRM console output, adjusts SysRq reboot behavior under SRM, derives system names, selects a machine vector by command line or HWRPB, copies it into `alpha_mv`, logs boot options, saves/restores HAE state, enables machine checks, sets up memory, probes cache sizes, calls `alpha_mv.init_arch()`, reserves legacy I/O resources, registers VGA screen info, sets default root to `sda2`, enables EISA when configured, validates ASN, discovers SMP CPUs, and finally calls `paging_init()`.

Machine vector selection first tries fixed system tables and API/unofficial tables, then variation-specific member IDs for Alcor, EB164, Marvel, Titan, Tsunami, and several legacy platforms. Name lookup allows command-line override against a list of known vectors.

## State And Persistence
This file establishes long-lived architecture globals and boot memory state. It mutates HWRPB checksum/state for system type normalization, stores SRM HAE, sets memblock regions, root device, cache shape globals, selected machine vector, CPU masks via `setup_smp()`, and registered CPU/platform devices. No disk persistence exists; firmware-provided HWRPB data is the persistent input.

## Dependencies And Integration Points
`setup.c` integrates with Alpha firmware/HWRPB, SRM callbacks, machine vectors from many `sys_*.c` files, host bridge init, memblock, initrd, VGA/VT console, EISA, SMP, paging, panic notifiers, sysrq, `/proc/cpuinfo`, and platform devices. Other files consume globals declared here through `proto.h`.

## Risks
- Machine-vector selection is table-heavy and depends on HWRPB type/variation quirks; wrong vector selection breaks interrupts, PCI, memory windows, and shutdown.
- Memory cluster handling reserves only usage bits 0/1 and enforces a default 32 GiB cap for non-discontiguous NUMA cases.
- External cache probing reads physical address zero with timing loops; it assumes safe early boot conditions.
- Command-line parsing uses destructive `strsep()` and restores from `boot_command_line`; future edits must preserve command-line lifetime.
- `alpha_panic_event()` hard-halts under SRM serial console, bypassing ordinary panic progression.

## Test Signals
- Boot logs identify correct system type, variation, machine vector, SRM/MILO source, HAE, memory clusters, cache sizes, and options.
- `mem=`, `gartsize=`, `cycle=`, `alpha_mv=`, `srmcons`, and `console=srm` command-line options behave as expected.
- `/proc/cpuinfo` reports CPU, system, cache, unaligned access, and SMP fields.
- Supported board configs boot through `alpha_mv.init_arch/init_irq/init_pci`.
- Initrd relocation works when initrd lies above memory limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/signal.c

## Purpose
`signal.c` implements Alpha signal ABI support: OSF/1-compatible signal syscalls, RT signal action, signal frame creation/restoration, signal-return syscalls, syscall restart handling, ptrace single-step interaction, and pending user-mode work processing.

## Important APIs, Types, And Functions
- `_BLOCKABLE` masks out `SIGKILL` and `SIGSTOP`.
- `osf_sigprocmask`, `osf_sigaction`, and `rt_sigaction` implement Alpha/OSF ABI signal mask/action variants.
- `struct sigframe` and `struct rt_sigframe` define user stack frame layouts; a compile-time assertion protects `rt_sigframe` offset ABI.
- Instruction constants encode an inline return stub: move stack pointer to argument, load syscall number, and `callsys`.
- `restore_sigcontext()` restores PC, integer registers, switch-stack saved registers, user stack pointer, FP registers, FPCR, restart block, and FPU restore status.
- `do_sigreturn()` and `do_rt_sigreturn()` validate user frames, restore blocked masks, restore context, and generate `SIGTRAP` if single-stepping.
- `get_sigframe()` chooses altstack/current stack and aligns the frame to 32 bytes.
- `setup_sigcontext()`, `setup_frame()`, and `setup_rt_frame()` build non-RT and RT signal frames.
- `handle_signal()` selects frame type and calls `signal_setup_done()`.
- `syscall_restart()` implements Alpha syscall restart register/PC adjustments.
- `do_signal()` coordinates signal selection, restart behavior, saved mask restoration, and ptrace breakpoint reset.
- `do_work_pending()` loops over reschedule, signal, notify, and resume-user-mode work before returning to userspace.

## Control Flow
Signal delivery starts from `do_work_pending()` when `_TIF_SIGPENDING` or `_TIF_NOTIFY_SIGNAL` is present. It enables interrupts, saves FPU state, and calls `do_signal()`. `do_signal()` cancels pending single-step breakpoints before inspecting signals. If a signal is available, it optionally rewinds/restarts a syscall, builds a frame via `handle_signal()`, and arranges user registers to enter the handler. If no signal is delivered, it handles syscall restart cases and restores saved signal mask. Finally it reinstalls single-step breakpoints when needed.

Signal return validates the user-provided `sigcontext` or `ucontext`, restores blocked signal mask, restores register state through `restore_sigcontext()`, and reports a breakpoint trap if a single-step breakpoint had been active.

## State And Persistence
State moves between kernel register frames and user stack frames. The file mutates current signal mask, restart block, FPU restore flags, FP save area, user stack pointer, and syscall result registers. User-space signal frames persist until the handler returns or user code overwrites them.

## Dependencies And Integration Points
This code depends on Alpha ABI structs (`sigcontext`, `ucontext`), syscall numbers, `pt_regs`/`switch_stack` layout, ptrace breakpoint helpers from `ptrace.c`, FPU save/restore conventions, generic signal APIs, altstack helpers, and user-mode resume work.

## Risks
- Signal frame layout is ABI-sensitive; offsets and `siginfo_t` sizing cannot change without breaking userland unwinders and signal return.
- Inline return stubs require executable user stack or supplied restorer behavior consistent with Alpha ABI expectations.
- Register restore reads many user fields; partial faults must reliably force `SIGSEGV`.
- Syscall restart depends on Alpha `r0`, `r19`, and PC rewind semantics.
- Ptrace single-step state must be canceled and restored around signal delivery to avoid stale breakpoints.

## Test Signals
- OSF and RT signal action/mask ABI tests.
- Signal delivery and return for normal and `SA_SIGINFO` handlers, including altstack.
- Syscall restart tests for `ERESTARTSYS`, `ERESTARTNOHAND`, `ERESTARTNOINTR`, and `ERESTART_RESTARTBLOCK`.
- Ptrace single-step across signal delivery should produce expected `SIGTRAP`.
- Fault injection with invalid signal frames should force `SIGSEGV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/smc37c669.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/smc37c669.c

## Purpose
`smc37c669.c` configures the SMC37c669 Super I/O controller during Alpha platform initialization. It detects the controller, defines its configuration register map, translates platform IRQ/DRQ wiring, keeps a shadow configuration for logical devices, and programs serial, parallel, floppy, and IDE decode state.

## Important APIs, Types, And Functions
- Device and resource constants define logical functions `SERIAL_0`, `SERIAL_1`, `PARALLEL_0`, `FLOPPY_0`, and `IDE_0`, default COM/parallel/FDC ports, IRQs, and DRQs.
- Device IRQ/DRQ macros tag SMC internal lines with high-bit masks and translate to/from ISA numbers.
- Numerous `SMC37c669_CRxx` unions describe bitfields for configuration registers `CR00` through `CR29`; aliases map registers to device ID, base address, IRQ, and DRQ roles.
- `SMC37c669_CONFIG_REGS` models index/data ports.
- `struct DEVICE_CONFIG local_config[NUM_FUNCS]` is the shadow port/IRQ/DRQ table.
- IRQ translation tables include the default and Monet/XP1000 mappings; DRQ translation uses a default table.
- `SMC37c669_detect()` probes 0x3f0 and 0x370, verifies device ID, selects translation tables, enters config mode, and initializes the local shadow copy.
- `SMC37c669_enable_device()` writes a logical device's saved port/IRQ/DRQ mapping into hardware.
- `SMC37c669_disable_device()` clears the device's decode and interrupt/DMA mappings.
- `SMC37c669_configure_device()` updates the shadow copy and reprograms hardware if the device is currently enabled.
- `SMC37c669_is_device_enabled()` checks base address decode bits.
- `SMC37c669_display_device_info()` prints logical device state.
- `SMC37c669_config_mode()`, `read_config()`, and `write_config()` wrap config-space access; entry is protected by `smc_lock`.
- `SMC37c669_init_local_config()` reads current hardware registers into `local_config`.
- `SMC37c669_xlate_irq()` and `SMC37c669_xlate_drq()` translate between SMC internal and ISA numbering.
- `SMC669_Init()` is the platform-facing initializer.

## Control Flow
`SMC669_Init(index)` disables local interrupts, probes for the controller, optionally dumps debug state, then disables/configures/enables COM1, COM2, parallel, and floppy with fixed legacy resources. It writes `0x0c` to port `0x3f2` to wake the floppy on affected systems, disables IDE decode, restores interrupts, and logs the controller base. Detection enters/exits config mode around ID reads, then leaves the chip in normal mode after local configuration import.

Device enable/disable functions switch on logical function. Serial devices program shared serial IRQ register nibbles and base address registers. Parallel and floppy program shared IRQ/DRQ registers plus base address registers. IDE programs base and alternate address registers but is disabled by the default init path.

## State And Persistence
The controller hardware retains programmed I/O decode, IRQ, and DRQ mappings until reset or reconfiguration. Kernel runtime state includes the global `SMC37c669` config-port pointer, selected translation table pointers, `local_config`, and `smc_lock`. All major functions are `__init`, so code/data may be freed after boot.

## Dependencies And Integration Points
The file depends on legacy ISA I/O port access, Alpha HWRPB/platform init, `proto.h`, and board vectors that call `SMC669_Init()` with a translation table index. It affects serial, parallel, floppy, and IDE subsystem visibility by enabling or disabling legacy decode.

## Risks
- The code is old firmware-derived logic with many register bitfield assumptions; wrong table index or board wiring can misroute interrupts.
- Config-mode entry needs two uninterrupted writes; only entry writes are spinlock-protected, while broader config sequences rely on disabled interrupts in the top-level init path.
- Several functions accept only low-byte IRQ/DRQ and 16-bit port values; invalid negative values are used intentionally as "none" in some calls and can be subtle.
- IDE is always disabled by `SMC669_Init()`, which is board-policy-sensitive.
- Pointer casts treat ISA port numbers as `SMC37c669_CONFIG_REGS *`, which is intentional for `inb/outb` wrappers but unsafe outside this context.

## Test Signals
- Boot log reports `SMC37c669 Super I/O Controller found`.
- Serial ports COM1/COM2 work at 0x3f8/0x2f8 with IRQ 4/3.
- Parallel and floppy controllers enumerate and receive expected IRQ/DRQ.
- IDE decode remains disabled when the platform expects a PCI IDE controller.
- Debug builds with `SMC_DEBUG` show stable before/after register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/smc37c669.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/smc37c93x.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/smc37c93x.c

## Purpose
`smc37c93x.c` initializes SMC FDC37C93x Ultra I/O controllers on Alpha systems. It probes standard Super I/O config ports, enables legacy serial, parallel, keyboard/mouse, and floppy functions, and leaves IDE disabled for boards such as PC164 that use a PCI IDE controller.

## Important APIs, Types, And Functions
- Logical device constants identify FDC, IDE1/2, PARP, serial ports, RTC, keyboard, and AUX I/O.
- Register constants model logical device selection, device ID/revision, power, activation, base address, interrupt, and DMA registers.
- `SMCConfigState()` enters config mode, retries device ID reads, and returns the base address when `VALID_DEVICE_ID` is found.
- `SMCRunState()` exits config mode.
- `SMCDetectUltraIO()` probes 0x3f0 and 0x370.
- `SMCEnableDevice()` selects a logical device, programs base address and primary interrupt, and activates it.
- `SMCEnableKYBD()` programs keyboard and mouse interrupt lines and activates the logical keyboard device.
- `SMCEnableFDC()` enables floppy burst mode, IRQ 6, DMA 2, and activates FDC.
- `SMCReportDeviceStatus()` is debug-only status output.
- `SMC93x_Init()` is the exported `__init` entry point.

## Control Flow
`SMC93x_Init()` disables local interrupts, probes for the controller, optionally reports debug state, enables SER1 at COM1/IRQ4, SER2 at COM2/IRQ3, parallel at 0x3bc/IRQ7, keyboard/mouse at IRQ1/12, and FDC at IRQ6/DMA2. It exits config mode, restores interrupts, logs success, and returns `1`. On no device found, it restores interrupts and returns `0`.

## State And Persistence
The Super I/O chip persists programmed logical device activation and resource registers until reset. The code has no long-lived kernel state beyond hardware side effects. All helpers are `__init`.

## Dependencies And Integration Points
The file uses ISA `inb/outb`, early delay, local interrupt save/restore, and is invoked by board PCI init paths such as `alphapc164_init_pci()` in `sys_cabriolet.c`. Its resource choices affect serial, parport, keyboard, mouse, and floppy drivers.

## Risks
- Probe retries are simple and assume the device ID value `2`; other compatible revisions may not be detected.
- Resource programming is fixed; conflicts with firmware-assigned resources or variant board wiring would be problematic.
- Config mode remains active until `SMCRunState()` after all enables; failures mid-sequence could leave the chip in config mode.
- No explicit error checking exists for individual register writes.

## Test Signals
- Boot log `SMC FDC37C93X Ultra I/O Controller found @ ...`.
- Functional COM1/COM2, parallel port, keyboard/mouse, and floppy after boot.
- PC164/LX164 boards continue to use PCI IDE rather than Super I/O IDE.
- Absence of the controller returns 0 without disrupting boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/smc37c93x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/smp.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/smp.c

## Purpose
`smp.c` implements Alpha SMP discovery, secondary CPU startup through SRM/HWRPB console mechanisms, per-CPU bookkeeping, IPI dispatch, remote function calls, CPU stop, instruction-cache barriers, and TLB/icache shootdowns.

## Important APIs, Types, And Functions
- `cpu_data[NR_CPUS]` stores Alpha per-CPU data and is exported.
- `ipi_data[NR_CPUS]` stores pending IPI bitmasks; message types are reschedule, call-function, and CPU-stop.
- `smp_secondary_alive`, `smp_num_probed`, and `smp_num_cpus` coordinate boot and exported CPU counts.
- `smp_store_cpu_info()` initializes loops-per-jiffy and ASN state for a CPU.
- `smp_setup_percpu_timer()` initializes profiling timer fields.
- `smp_callin()` is the C entry point for secondary CPUs.
- `wait_for_txrdy()`, `send_secondary_console_msg()`, and `recv_secondary_console_msg()` marshal console/HWRPB IPC messages.
- `secondary_cpu_start()` prepares the secondary HWPCB, HWRPB restart fields, checksum, flags, and sends `START`.
- `smp_boot_one_cpu()`, `setup_smp()`, `smp_prepare_cpus()`, `__cpu_up()`, and `smp_cpus_done()` implement CPU discovery and bring-up.
- `send_ipi_message()` sets pending bits and calls `wripir()`.
- `handle_ipi()` dispatches reschedule, generic call-function, CPU-stop, and secondary console messages.
- `arch_smp_send_reschedule()`, `smp_send_stop()`, `arch_send_call_function_ipi_mask()`, and `arch_send_call_function_single_ipi()` are architecture hooks.
- `smp_imb()`, `flush_tlb_all()`, `flush_tlb_mm()`, `flush_tlb_page()`, `flush_tlb_range()`, and `flush_icache_user_page()` implement cross-CPU cache/TLB maintenance.

## Control Flow
`setup_smp()` reads HWRPB processor entries, identifies runnable CPUs by flag mask `0x1cc`, copies boot PAL revision, and sets possible/present masks. `smp_prepare_cpus()` initializes IPI state and boot CPU info; if multiple CPUs are available, `__cpu_up()` calls `smp_boot_one_cpu()`. Startup prepares a minimal HWPCB for the idle task, publishes `__smp_callin` in HWRPB restart fields, updates the HWRPB checksum, toggles CPU flags, and sends `START` to the secondary console. The secondary enters `smp_callin()`, sets itself online, initializes traps/interrupts/clockevent/MM state, notifies CPU startup, calibrates delay after boot CPU releases it, stores CPU info, signals alive, and enters idle.

IPI senders set bits in per-CPU `ipi_data`, memory-barrier around bit publication, and issue hardware IPIs. `handle_ipi()` atomically drains the bitmask and invokes scheduler, generic call-function, or halt actions. TLB and icache flush paths perform local flushes when possible, invalidate remote MM contexts for single-user address spaces, or use `smp_call_function()` for synchronized remote maintenance.

## State And Persistence
State includes exported `cpu_data`, `ipi_data` pending bits, HWRPB per-CPU flags/HWPCB/restart fields, Linux CPU masks, `smp_secondary_alive`, and per-MM context arrays. It is all runtime state. Secondary startup mutates firmware-visible HWRPB structures.

## Dependencies And Integration Points
The file depends on SRM/HWRPB layout, Alpha PAL calls (`wrmces`, `wrent`, `wripir`), trap and clock initialization, machine-vector `smp_callin`, generic SMP hotplug hooks, scheduler IPIs, generic call-function APIs, Alpha ASN/MMU context management, and TLB/cache flush helpers.

## Risks
- Secondary startup is firmware-protocol-sensitive; HWRPB flags, checksum, restart address, and console IPC ordering are critical.
- Bring-up timeouts can hang or leave CPUs stuck depending on firmware behavior.
- IPI pending bits require memory barriers and atomic exchange; missed ordering can lose work.
- TLB flush optimizations invalidate remote `mm->context[cpu]` based on `mm_users`, which must remain consistent with Alpha ASN semantics.
- Some comments and constants are legacy and hardware-specific, making changes hard to validate without real Alpha SMP hardware.

## Test Signals
- SMP boot logs show probed and activated CPU counts.
- CPU hotplug/bring-up path returns online status for each secondary.
- Scheduler reschedule IPIs and generic `smp_call_function()` work under load.
- TLB shootdown stress with multithreaded mmap/munmap/mprotect workloads.
- `smp_imb()` and executable page updates behave correctly across CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/srm_env.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/srm_env.c

## Purpose
`srm_env.c` exposes Alpha SRM firmware environment variables through procfs. It creates named and numbered proc entries, reads variables through SRM callbacks, writes variables through callback set/save operations, and loads only on systems detected as SRM-booted.

## Important APIs, Types, And Functions
- Proc layout constants create `/proc/srm_environment/named_variables` and `/proc/srm_environment/numbered_variables`.
- `srm_env_t` maps human-readable names to SRM environment IDs.
- `srm_named_entries[]` includes variables such as `auto_action`, boot device/file/flags, dump device, audit, license, charset, language, and `tty_dev`.
- `srm_env_proc_show()` allocates a page, calls `callback_getenv()`, and writes returned bytes to seq_file when callback status is successful.
- `srm_env_proc_open()` binds `pde_data()` as the variable ID.
- `srm_env_proc_write()` copies user input, calls `callback_setenv()`, then loops on `callback_save_env()` while status indicates busy.
- `srm_env_proc_ops` wires open/read/lseek/release/write.
- `srm_env_init()` validates `alpha_using_srm`, creates proc directories and entries, and handles cleanup on failure.
- `srm_env_exit()` removes the proc subtree.

## Control Flow
Module init rejects non-SRM systems. It creates the base directory, named subdirectory, numbered subdirectory, all named entries with their IDs, then entries `0` through `255` for raw variable numbers. Reads allocate a temporary page and decode SRM callback status from the top three bits of the returned value. Writes reject page-sized or larger input, NUL-terminate the copied buffer, set the variable, and save the environment until firmware is no longer busy.

## State And Persistence
Kernel state consists of proc directory entries and static variable tables. Writes persist into SRM firmware environment storage through `callback_save_env()`, so they survive reboot depending on firmware behavior. Temporary pages are allocated per read/write.

## Dependencies And Integration Points
The module depends on SRM callback APIs, `alpha_using_srm` from setup, procfs, seq_file, module init/exit, and user-copy helpers. It is an optional firmware-management interface for user space.

## Risks
- Firmware callbacks can fail or return status-encoded values; the code treats any top status bits as `-EFAULT`.
- Write loops on `callback_save_env()` while busy with no explicit timeout.
- Proc entry creation failures trigger subtree cleanup, but partially visible entries can exist briefly during init.
- User input is passed to firmware with its original `count`, including any newline written by shell tools.

## Test Signals
- On SRM systems, `/proc/srm_environment` appears with named and numbered variables.
- Reading known variables returns firmware values.
- Writing a safe test variable changes SRM state and survives a save.
- On non-SRM/MILO systems, module init returns `-ENODEV`.
- Error injection for proc creation cleans up the subtree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/srm_env.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/srmcons.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/srmcons.c

## Purpose
`srmcons.c` implements an SRM callback-backed console and TTY driver. It supports early/full console output through firmware callbacks, a one-device system TTY named `srm`, periodic polling for input, CR insertion after newlines, and registration/unregistration hooks used during Alpha setup and time initialization.

## Important APIs, Types, And Functions
- `srmcons_callback_lock` serializes SRM callback get/put operations.
- `srm_is_registered_console` tracks console registration.
- `struct srmcons_private` contains a `tty_port` and polling timer; `srmcons_singleton` is the only device instance.
- `srmcons_result` decodes 61-bit character/count and 3-bit status return values from callbacks.
- `srmcons_do_receive_chars()` polls `callback_getc()`, inserts up to 10 available chars, and pushes tty flip buffer.
- `srmcons_receive_chars()` is the timer callback that tries the callback lock, polls input, and reschedules quickly or slowly based on activity.
- `srmcons_do_write()` writes output in chunks via `callback_puts()`, polls input during writes when a TTY port exists, and emits carriage returns after newlines.
- TTY operations include `srmcons_open()`, `srmcons_close()`, `srmcons_write()`, and `srmcons_write_room()`.
- `srmcons_init()` allocates/registers the TTY driver only if the console was registered earlier.
- Console operations include `srm_console_write()`, `srm_console_device()`, and `srm_console_setup()`.
- `register_srm_console()` opens the firmware console and registers `srmcons`.
- `unregister_srm_console()` closes and unregisters it.

## Control Flow
`setup.c` calls `register_srm_console()` when SRM console output is requested. That opens the firmware console and registers the console driver. Later `srmcons_init()` creates the TTY driver only if the console is registered. Opening `/dev/srm` links the singleton port to the tty and starts the polling timer. The timer periodically polls firmware input and reschedules while the tty is present. Writes lock the callback path, write bounded chunks, interleave receive polling, and add CR after newline for firmware console conventions. Closing the last tty deletes the timer.

## State And Persistence
State includes the singleton tty port, timer, registered tty driver pointer, console registration flag, and firmware console open/closed state. There is no disk persistence. Firmware console state may outlive Linux only in the sense that callbacks target SRM.

## Dependencies And Integration Points
The file depends on SRM callback APIs (`callback_open_console`, `callback_close_console`, `callback_getc`, `callback_puts`), Linux console and TTY subsystems, timers, spinlocks, and setup-time SRM console selection. `setup.c` and `process.c` use registration and shutdown interactions.

## Risks
- Callback operations happen with interrupts disabled/spinlocks held; firmware latency can affect responsiveness.
- Input is polling-based, so responsiveness depends on timer intervals and write-side polling.
- TTY port refcounting is noted as not fully proper (`port->tty` direct assignment).
- TTY driver initialization depends on early console registration ordering.
- CR insertion logic emits a carriage return after chunks containing newline, which is firmware-console-specific.

## Test Signals
- `srmcons` or `console=srm` boot options produce early console output.
- `/dev/srm` opens only when SRM console was registered and supports read/write.
- Input polling receives firmware console input without flooding when idle.
- Unregister during console transition stops callback console use cleanly.
- Panic/SysRq paths with SRM console do not deadlock on callback lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/srmcons.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_alcor.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_alcor.c

## Purpose
`sys_alcor.c` provides board support for Alpha Alcor and XLT systems. It implements GRU interrupt mask/ack logic, PCI interrupt dispatch and slot mapping, CIA PCI initialization with XLT detection, SRM reset behavior, and the `alpha_machine_vector` definitions for Alcor and XLT.

## Important APIs, Types, And Functions
- `cached_irq_mask` mirrors enabled GRU interrupt bits; unlike Cabriolet, mask bit true means enabled.
- `alcor_update_irq_hw()`, `alcor_enable_irq()`, `alcor_disable_irq()`, and `alcor_mask_and_ack_irq()` program GRU interrupt mask/clear registers.
- `alcor_isa_mask_and_ack_irq()` chains i8259A ack and clears the ISA summary bit in GRU.
- `alcor_irq_type` is the IRQ chip for platform IRQs 16-47.
- `alcor_device_interrupt()` reads `GRU_INT_REQ`, filters with `GRU_INT_REQ_BITS`, and dispatches either ISA cascade or `handle_irq(16 + bit)`.
- `alcor_init_irq()` initializes GRU registers, IRQ chips, i8259A, ISA DMA, and ISA cascade IRQ.
- `alcor_map_irq()` maps PCI IDSEL/pin combinations to IRQs using `COMMON_TABLE_LOOKUP`.
- `alcor_kill_arch()` chains CIA shutdown and, when SRM restore setup is not compiled in, can write `GRU_RESET` with `0x0000dead` for SRM restart.
- `alcor_init_pci()` calls `cia_init_pci()` and detects XLT-family motherboards by a built-in DEC Tulip at devfn 6.
- `alcor_mv` and `xlt_mv` define machine vectors.

## Control Flow
IRQ initialization optionally switches device interrupts to SRM dispatch when booted under SRM, clears and configures GRU masks/edge/polarity, installs level IRQ handlers except unconnected lines 36-46, overrides ISA ack, initializes ISA PIC/DMA, and requests the ISA cascade. Device interrupts loop over pending GRU bits, dispatching bit 31 to ISA and other bits to Linux IRQ numbers.

PCI init first performs CIA setup, then probes for a DEC Tulip in slot 6. Finding it changes `alpha_mv.sys.cia.gru_int_req_bits` to XLT request bits and logs AS500/XLT detection.

## State And Persistence
State includes `cached_irq_mask`, GRU hardware registers, i8259A ack hook, machine-vector system CIA bits, and registered IRQ descriptors. Hardware interrupt mask state persists until reset or reprogramming.

## Dependencies And Integration Points
The file depends on CIA core logic, GRU register definitions, common IRQ helpers, i8259A, ISA DMA, PCI device probing, SRM interrupt dispatch, and machine-vector macros. `setup.c` selects these vectors for Alcor/XLT variants.

## Risks
- GRU mask polarity differs from other platforms; confusing enabled/disabled semantics can invert interrupts.
- Lines 20-30 relative to PCI range are skipped to avoid spurious interrupts; enabling them during probing can misbehave.
- XLT detection depends on a DEC Tulip at a specific devfn.
- `alcor_kill_arch()` has conditional behavior depending on SRM restore compile options.

## Test Signals
- Alcor/XLT boot logs show correct vector and optional XLT Tulip detection.
- PCI interrupts route according to slot/pin table and ISA cascade works.
- IRQ masking/ack clears GRU state without interrupt storms.
- Restart under SRM behaves as expected for the board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_alcor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_cabriolet.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_cabriolet.c

## Purpose
`sys_cabriolet.c` provides board support for Cabriolet-family Alpha systems, especially PC164 and LX164. It implements ISA-port interrupt masking and dispatch, SRM and PC164 interrupt workarounds, PCI slot IRQ mapping tables, Super I/O/IDE initialization, and machine vectors for LX164 and PC164.

## Important APIs, Types, And Functions
- `cached_irq_mask` mirrors disabled IRQ bits; here mask bit true means disabled.
- `cabriolet_update_irq_hw()`, `cabriolet_enable_irq()`, and `cabriolet_disable_irq()` write mask bytes to ISA ports 0x804-0x806.
- `cabriolet_irq_type` is the IRQ chip for platform IRQs.
- `cabriolet_device_interrupt()` reads summary ports 0x804-0x806 and dispatches bit 4 to ISA cascade or `handle_irq(16 + bit)`.
- `common_init_irq()` initializes i8259A, chooses SRM or native IRQ setup, installs level IRQ handlers, initializes ISA DMA, and requests ISA cascade.
- `cabriolet_init_irq()` and `pc164_init_irq()` specialize common init.
- `pc164_srm_device_interrupt()` and `pc164_device_interrupt()` raise `__min_ipl` during interrupt dispatch to work around broken PC164 interrupt masking.
- `eb66p_map_irq()`, `cabriolet_map_irq()`, and `alphapc164_map_irq()` are table-based PCI IRQ mappers.
- `cabriolet_enable_ide()` probes PC873xx Super I/O and enables IDE.
- `cia_cab_init_pci()` combines CIA PCI init and PC873xx IDE enable.
- `alphapc164_init_pci()` combines CIA PCI init and `SMC93x_Init()`.
- `lx164_mv` and `pc164_mv` define machine vectors.

## Control Flow
Native interrupt setup masks all summary ports, installs IRQ chips for Linux IRQs 16-34, and uses the i8259A for ISA cascade. Under SRM, it switches `alpha_mv.device_interrupt` to a supplied SRM dispatch function and initializes SRM IRQs. PC164 wraps both native and SRM dispatch with `__min_ipl = getipl()` to prevent recursive interrupts because hardware masking/ack is unreliable.

PCI IRQ mapping is purely table-driven by IDSEL and interrupt pin. LX164 uses Pyxis I/O and DAC offset, calls `pyxis_init_arch`, and initializes PCI with `alphapc164_init_pci()`. PC164 uses CIA I/O and the same AlphaPC164 IRQ map and SMC93x Super I/O initialization.

## State And Persistence
State includes `cached_irq_mask`, ISA summary/mask registers, IRQ descriptors, `__min_ipl` during PC164 dispatch, and Super I/O hardware configuration from SMC/PC873xx init. Machine vectors are init-time structures selected by setup.

## Dependencies And Integration Points
The file depends on CIA/Pyxis core logic, i8259A/ISA DMA helpers, SRM IRQ helpers, PC873xx Super I/O helpers, `SMC93x_Init()`, PCI common swizzle/table lookup, and machine-vector macros. `setup.c` selects `lx164_mv` or `pc164_mv` based on HWRPB variation.

## Risks
- Interrupt mask polarity differs from Alcor and is write-only through ISA ports, so software shadow state must stay correct.
- PC164 masking is known broken; the `__min_ipl` workaround reduces recursion but may affect interrupt latency.
- Several mapping tables are board-layout-specific; wrong vector selection misroutes PCI interrupts.
- `cia_cab_init_pci()` is present for Cabriolet-style IDE enable but not wired into the shown PC164/LX164 vectors, so callers must choose the right init path.
- Super I/O initialization can alter legacy device decode expected by firmware or other drivers.

## Test Signals
- PC164 and LX164 boot with correct machine vector and IRQ count 35.
- PCI devices receive expected interrupts on each slot/pin.
- PC164 handles interrupt load without recursive interrupt storms.
- SMC93x initialization finds and enables expected legacy devices.
- LX164 DMA can use `PYXIS_DAC_OFFSET` for DAC-capable devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_cabriolet.c -->
