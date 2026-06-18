# Research: subset-b-000845

This grouped report covers SPARC kernel boot, trap, interrupt, hypervisor, IOMMU/DMA, and LDOM service code under `sources/distributed-fs/ceph-client/arch/sparc/kernel`. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ds.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/ds.c

## Purpose
`ds.c` implements the Sun Logical Domains domain-services VIO driver. It negotiates the domain-services protocol over an LDC stream, registers service capabilities, dispatches service data to handlers, and exposes LDOM control helpers for reboot, poweroff, variable updates, machine-description updates, and CPU dynamic reconfiguration.

## Important APIs, Types, and Functions
The protocol is modeled by `ds_msg_tag`, version/register/unregister/data/nack packet structs, and `ds_cap_state`. `ds_info` owns one LDC channel, receive buffer, handshake state, capability table copy, and list linkage. Exported or externally meaningful functions are `ldom_set_var()`, `ldom_reboot()`, and `ldom_power_off()`. Service handlers include `md_update_data()`, `domain_shutdown_data()`, `domain_panic_data()`, optional `dr_cpu_data()`, `ds_pri_data()`, and `ds_var_data()`. Driver entry points are `ds_probe()` and `ds_init()`.

## Control Flow and State
`ds_probe()` allocates per-channel state, copies `ds_states_template`, creates an LDC channel, binds it, and links `ds_info_list` under `ds_lock`. `ds_event()` reacts to LDC up/reset/data events. On up, `ds_up()` sends `DS_INIT_REQ`; `ds_handshake()` expects `DS_INIT_ACK`, then `register_services()` sends `DS_REG_REQ` for each capability. Registration ACK/NACK updates each `ds_cap_state.state`. `DS_DATA` packets are copied into `ds_work_list` and processed by `ds_thread()`, so service-specific work runs outside the LDC receive loop.

## Persistence and Dependencies
Persistent kernel state includes `ds_info_list`, per-capability handles/states, `ds_var_doorbell` and `ds_var_response`, `full_boot_str`, and `reboot_data_supported`. The file depends on LDC/VIO, hypervisor calls, machine-description code, CPU hotplug, reboot/poweroff APIs, and the local `kernel.h` helper `kimage_addr_to_ra()` on sparc64.

## Integration Points, Risks, and Test Signals
Integration points include the VIO bus match type `domain-services-port`, LDC transport, `mdesc_update()`, `add_cpu()`/`remove_cpu()`, `fixup_irqs()`, and hypervisor reboot-data APIs. Risks center on packet length trust, deadlocks around global `ds_lock`, timeout-only `ldom_set_var()` completion, missing driver remove path, and the assumption that handles encode capability index in the top 32 bits. Test signals are successful service registration messages, variable set responses, LDOM shutdown/panic requests, machine-description update handling, CPU hotplug DR requests, and reboot command behavior on systems with and without `HV_GRP_REBOOT_DATA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/dtlb_miss.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/dtlb_miss.S

## Purpose
`dtlb_miss.S` is an inline trap-table fragment for sparc64 data TLB misses. It performs the fastest possible TSB lookup for non-context-zero misses and loads the DTLB directly when the TSB tag matches.

## Important APIs, Types, and Functions
There are no callable C-style functions. The fragment uses privileged ASIs `ASI_DMMU_TSB_8KB_PTR`, `ASI_DMMU`, and `ASI_DTLB_DATA_IN`, the `TSB_LOAD_QUAD()` macro, and external trap labels `kvmap_dtlb` and `tsb_miss_dtlb`.

## Control Flow and State
The handler reads the current DMMU TSB pointer and tag target, extracts the context, and branches to `kvmap_dtlb` for context zero. Otherwise it masks the context out of the tag, loads the candidate TSB entry, compares tags, branches to the full miss path with `FAULT_CODE_DTLB` on mismatch, or writes the TTE into `ASI_DTLB_DATA_IN` and `retry`s.

## Persistence and Dependencies
The only state mutated is the hardware DTLB. Correctness depends on TSB entry format, register conventions in the trap table, and the miss/fault handlers included by `head_64.S`.

## Integration Points, Risks, and Test Signals
This code integrates with `ktlb.S`, `tsb.S`, and the sparc64 trap table. It is latency-sensitive and line-padded for trap-table/icache layout. Risks include register convention drift, incorrect context masking, and TSB/TTE format changes. Test signals are successful user/kernel data accesses after TLB eviction, no unexpected `tsb_miss_dtlb` floods, and boot stability under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/dtlb_miss.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/dtlb_prot.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/dtlb_prot.S

## Purpose
`dtlb_prot.S` is a sparc64 trap-table fragment for data TLB protection faults, mainly writes to read-only pages from user mode, nucleus-to-user accesses, and higher-trap-level stack-frame faults.

## Important APIs, Types, and Functions
It has no exported callable functions. It uses `TLB_SFSR`, `TLB_TAG_ACCESS`, `ASI_DMMU`, `PSTATE_AG`, `PSTATE_MG`, `FAULT_CODE_DTLB`, `FAULT_CODE_WRITE`, and external labels `winfix_trampoline` and `sparc64_realfault_common`.

## Control Flow and State
The fragment clears the DMMU fault-valid bit, switches to alternate globals, checks the trap level, reads tag-access to recover the faulting virtual address without context bits, and builds a DTLB-write fault code. For trap levels above one it branches to window-fixup before real fault processing; otherwise it enters `sparc64_realfault_common`.

## Persistence and Dependencies
It mutates DMMU fault state and processor global register state during trap handling. It depends on V9 trap-level semantics, window-fixup code, and the generic sparc64 fault path.

## Integration Points, Risks, and Test Signals
Integration is with the trap table, winfixup, and memory fault handlers. Risks are high because this path runs before normal C state exists; incorrect fault address extraction or trap-level routing can corrupt user windows or panic on copy-to-user faults. Test signals include copy-on-write behavior, user write-protect faults, kernel user-access fault recovery, and no recursive TL>1 trap loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/dtlb_prot.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ebus.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/ebus.c

## Purpose
`ebus.c` provides EBus DMA controller helper routines for SPARC systems. It abstracts CSR programming, DMA setup, interrupt enable/disable, residue/address reporting, and optional shared interrupt handling for EBus clients.

## Important APIs, Types, and Functions
The public API is `ebus_dma_register()`, `ebus_dma_irq_enable()`, `ebus_dma_unregister()`, `ebus_dma_request()`, `ebus_dma_prepare()`, `ebus_dma_residue()`, `ebus_dma_addr()`, and `ebus_dma_enable()`. It operates on `struct ebus_dma_info` from `<asm/ebus_dma.h>`. Internal functions are `__ebus_dma_reset()` and `ebus_dma_irq()`.

## Control Flow and State
Registration validates MMIO registers, flags, callback requirements, and name, then resets the channel and programs burst/count/TCI bits. `ebus_dma_prepare()` resets and programs direction plus next-descriptor support. `ebus_dma_request()` refuses oversized or inactive transfers, verifies no next address is loaded, then writes count and bus address. Interrupt enable optionally calls `request_irq()` and toggles `EBDMA_CSR_INT_EN`; the IRQ handler acknowledges pending bits by writing CSR back and calls the client callback for error, DMA terminal count, or device interrupt events.

## Persistence and Dependencies
Persistent state is in device registers and the caller-owned `ebus_dma_info` lock, flags, IRQ, callback, and cookie. The file depends on MMIO accessors, Linux IRQ APIs, delays, and exported EBus DMA ABI.

## Integration Points, Risks, and Test Signals
Drivers using EBus DMA integrate through these helpers and must initialize `p->lock`, MMIO `regs`, IRQ, callback, and flags. Risks include reset timeout being silent, incorrect use of `no_drain`, races if callers manipulate registers outside the lock, and transfer length limited to 24 bits. Test signals are DMA completion callbacks, error callbacks, stable residue/address reads, correct IRQ free on disable/unregister, and no stuck drain/cycle-pending bits after prepare.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ebus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/entry.S

## Purpose
`entry.S` is the 32-bit SPARC low-level trap, interrupt, syscall, FPU, delay, KGDB, and register-window support file. It is the bridge between trap-table entries and C-level kernel handlers.

## Important APIs, Types, and Functions
Global entry points include `bad_trap_handler`, `real_irq_entry`, `linux_sparc_syscall`, `ret_from_fork`, `ret_from_kernel_thread`, `fpsave`, `fpload`, `__ndelay`, `__udelay`, `breakpoint_trap`, `flushw_all`, `restore_current`, optional `arch_kgdb_breakpoint`, `kgdb_trap_low`, and SMP IPI handlers. It calls C handlers such as `handler_irq()`, `do_hw_interrupt()`, `do_illegal_instruction()`, `do_sparc_fault()`, signal-return helpers, `sparc_fork()`/`sparc_clone()`/`sparc_vfork()`/`sparc_clone3()`, and ptrace syscall tracing.

## Control Flow and State
Trap handlers preserve PSR/WIM/window state with `SAVE_ALL`/`RESTORE_ALL`, re-enable traps where safe, and pass `pt_regs` plus PC/NPC/PSR to C. IRQ entry raises PIL, dispatches to platform IRQ handlers, and handles SMP soft IPIs and level-15 cross calls specially for sun4m, sun4d, LEON, and PCIC. Syscalls validate `%g1` against `NR_syscalls`, save user registers, optionally trace entry/exit, call the syscall table target, set/clear carry for errno, advance PC/NPC, and return through common trap exit. FPU helpers save queue/register state and recover from FSR-store traps. Delay helpers use calibrated loop counts.

## Persistence and Dependencies
State is CPU architectural state: PSR, WIM, windows, `thread_info` flags, trap table patches, floppy pseudo-DMA globals, and FPU registers. The file depends on `etrap_32.S`, `rtrap_32.S`, `winmacro.h`, generated offsets, IRQ/platform code, syscall table, and traps/signal/process C code.

## Integration Points, Risks, and Test Signals
This file is central to sparc32 execution. Risks include register convention breakage, incorrect PC/NPC advancement, window spill/fill corruption, SMP IPI misclassification, and trap recursion in FPU or unaligned paths. Test signals are clean boot, syscall/ptrace/signal tests, SMP IPIs, timer/floppy interrupts where configured, KGDB breakpoint behavior, FPU context switching, and stress tests that force register-window overflow/underflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/entry.h -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/entry.h

## Purpose
`entry.h` declares the C/assembly interface for SPARC trap, IRQ, syscall, patching, error, and interrupt-vector paths. It is the shared contract between low-level assembly and C handlers.

## Important APIs, Types, and Functions
Common declaration: `handler_irq()`. The sparc32 side declares trap handlers, `fpsave()`, and `fpload()`. The sparc64 side declares patch entry structs for popcount and pause instructions, sun4v/M7 patch helpers, trap C handlers, fault/error reporters, hypervisor TLB error handlers, `init_irqwork_curcpu()`, `sun4v_register_mondo_queues()`, and the interrupt-vector `struct ino_bucket`.

## Control Flow and State
There is no runtime control flow. The header fixes function signatures and data layouts consumed by assembly. `struct cheetah_err_info` is explicitly layout-sensitive and records AFSR/AFAR plus cache/ecache diagnostic state. `struct ino_bucket` layout is likewise consumed by vector interrupt assembly.

## Persistence and Dependencies
Persistent state declarations include cache parity flags, `cheetah_error_log`, `ivector_table`, and `ivector_table_pa`. The header depends on trap block definitions, architecture offsets, and Linux type/init declarations.

## Integration Points, Risks, and Test Signals
Integration is broad: trap table fragments, C trap handlers, IRQ allocation, hypervisor error reporting, and patching code rely on these exact declarations. Risks include silent ABI breakage if structure fields move without matching hand-coded assembly, incorrect prototype drift, and architecture-config mismatch. Test signals are successful allmodconfig/defconfig builds for sparc32 and sparc64 and boot-time trap/IRQ/error handling on representative sun4u/sun4v hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/etrap_32.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/etrap_32.S

## Purpose
`etrap_32.S` builds 32-bit SPARC kernel trap frames and handles register-window preparation when entering Linux from traps. It turns raw trap-time PSR/PC/NPC/WIM state into a `pt_regs` frame on the correct kernel stack.

## Important APIs, Types, and Functions
Primary labels are `trap_setup`, `trap_setup_from_user`, `trap_setup_kernel_spill`, `trap_setup_user_spill`, and `tsetup_srmmu_stackchk`. Patch labels `tsetup_patch*` and `tsetup_7win_patch*` are modified at boot for 7-window CPUs.

## Control Flow and State
Trap callers enter with `%l0` PSR, `%l1` PC, `%l2` NPC, `%l3` WIM, and `%l6` return PC. Kernel traps allocate a frame below `%fp`, store registers, and spill a kernel window if the trap landed in the invalid window. User traps load `current_thread_info`, compute the top-of-thread trap frame, store `pt_regs`, update `TI_UWINMASK`, and clear `TI_W_SAVED`. If a user stack window must be spilled, it temporarily adjusts WIM, turns on SRMMU/LEON no-fault behavior, stores the window, and falls back to `SAVE_BOLIXED_USER_STACK` on bad user stacks.

## Persistence and Dependencies
It mutates WIM, `thread_info` window masks, kernel/user stack memory, and trap-frame contents. Dependencies include SRMMU/LEON ASIs, `winmacro.h`, generated offsets, and boot-time patching in `head_32.S`.

## Integration Points, Risks, and Test Signals
This code integrates with every sparc32 trap path using `SAVE_ALL`. Risks are severe: wrong window masks corrupt user registers, bad no-fault handling loops on user stack faults, and patching errors break 7-window CPUs. Test signals include signal delivery/return, deep call stacks, user stack fault handling, ptrace register visibility, and stress that forces window spills from user and kernel mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/etrap_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/etrap_64.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/etrap_64.S

## Purpose
`etrap_64.S` prepares sparc64 V9 trap entry frames. It saves trap state, handles user/kernel window spill cases, switches context/register globals safely, and provides TL>1 trap capture.

## Important APIs, Types, and Functions
Global labels are `etrap`, `etrap_irq`, `etrap_syscall`, and `etraptl1`. It relies on patch sections `.fast_win_ctrl_1insn_patch`, `.sun4v_1insn_patch`, and `.sun_m7_1insn_patch`, and uses `TRAP_LOAD_THREAD_REG`, `LOAD_PER_CPU_BASE`, and `PT_V9_*` offsets.

## Control Flow and State
Normal entry reads PIL/TSTATE/TPC/TNPC/TT/Y, chooses task-stack or current stack based on privilege, clears or preserves FPU state based on `TSTATE_PEF`, saves register globals and ins, switches to privileged interrupt-enabled TSTATE, and returns with `done` to the assembly caller's continuation. If no clean windows are available it reassigns `otherwin`, `wstate`, primary context, and saves user or kernel windows. `etraptl1` snapshots TSTATE/TPC/TNPC/TT for multiple trap levels and then rejoins the common trap-frame setup.

## Persistence and Dependencies
It writes `pt_regs`, `thread_info` FP bookkeeping, trap-level save areas, context registers, PSTATE/TSTATE, WSTATE, and per-cpu base state. Dependencies include V9 privileged registers, sun4v and M7 runtime patches, trap block layout, and `rtrap_64.S`.

## Integration Points, Risks, and Test Signals
Integration points include all sparc64 trap-table handlers, syscalls, IRQ entry, FPU traps, ADI/M7 tagged memory behavior, and TL1 error handling. Risks include corrupting global sets, losing user register windows, disabling ADI enforcement, and mishandling sun4v context ASI differences. Test signals are syscall/interrupt entry stability, ADI tests on M7+, FPU lazy state tests, TL1 error reporting, and register-window stress under SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/etrap_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/fpu_traps.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/fpu_traps.S

## Purpose
`fpu_traps.S` handles sparc64 FPU disabled and FPU exception traps. It lazily restores/saves floating-point state, handles unfinished `fitos` cases, and enters C trap handlers when emulation or exception processing is needed.

## Important APIs, Types, and Functions
Global labels are `do_fpdis`, `do_fpother_check_fitos`, and `do_fptrap`; internal label `fp_other_bounce` calls `do_fpother()`. It uses `TI_FPSAVED`, `TI_FPREGS`, `TI_XFSR`, `TI_GSR`, `FPRS_*`, `TSTATE_PEF`, secondary context registers, block ASIs, and sun4v patch sections.

## Control Flow and State
`do_fpdis()` enables FPRS, restores saved lower/upper FP register halves from thread storage when present, zeroes unsaved halves, restores GSR/FSR, sets `TSTATE_PEF`, clears dirty FPRS bits, and retries. If FPU state is already enabled in a special Cheetah state it traps through `etrap`. `do_fpother_check_fitos()` detects a specific unfinished integer-to-single conversion without inexact, decodes source/destination registers via jump tables, emulates with `fitod` then `fdtos`, restores `%f62`, and `done`s. Other cases enter `do_fptrap_after_fsr`, save dirty FP banks and GSR/FSR to thread_info, clear FPRS, and branch to `etrap`.

## Persistence and Dependencies
Persistent state is per-thread FP register storage, FSR, GSR, and FPRS dirty/saved flags. Dependencies include V9 FP register layout, DMMU/MMU context ASIs, thread_info offsets, and C handlers declared in `entry.h`.

## Integration Points, Risks, and Test Signals
Integration is with lazy FPU context switching, signal/ptrace FP state, and trap return. Risks include stale secondary context restoration, partial FP bank saves, incorrect `fitos` instruction decoding, and trap recursion while accessing thread FP storage. Test signals include FP-heavy context switching, ptrace/signal FP register validation, unfinished FP exception tests, and sun4v versus sun4u ASI patch coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/fpu_traps.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/ftrace.c

## Purpose
`ftrace.c` implements SPARC dynamic ftrace and function graph tracer patching. It converts call sites between SPARC `call` instructions and NOPs and hooks return addresses for graph tracing.

## Important APIs, Types, and Functions
Key functions are `ftrace_make_nop()`, `ftrace_make_call()`, `ftrace_update_ftrace_func()`, optional `ftrace_enable_ftrace_graph_caller()`, `ftrace_disable_ftrace_graph_caller()`, and `prepare_ftrace_return()`. Internal helpers are `ftrace_call_replace()` and `ftrace_modify_code()`.

## Control Flow and State
Dynamic ftrace computes a PC-relative call displacement, atomically compares/exchanges the instruction word at the target IP, flushes the instruction address, and uses exception-table fixup to report faults. Graph tracing updates `ftrace_graph_call` to call either `ftrace_graph_caller` or `ftrace_stub`. `prepare_ftrace_return()` skips paused graph tracing, calls `function_graph_enter()`, and returns `return_to_handler` when the graph stack accepts the frame; otherwise it returns the original parent adjusted by SPARC call delay semantics.

## Persistence and Dependencies
State is patched kernel text and per-task graph tracing state. Dependencies include `asm/ftrace.h`, SPARC instruction encoding, exception tables, cache flush semantics, and ftrace core APIs.

## Integration Points, Risks, and Test Signals
Integration is with dynamic ftrace, modules, and function graph tracer assembly. Risks include displacement overflow/truncation on far calls, CAS failures if text differs from expected old/new values, instruction cache coherency bugs, and off-by-one return address adjustment. Test signals are enabling/disabling function tracing, tracing module functions, graph tracer call/return balance, and no unexpected `ftrace_modify_code()` fault result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/getsetcc.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/getsetcc.S

## Purpose
`getsetcc.S` implements sparc64 helpers for software traps that get or set integer condition codes in a saved `pt_regs` frame.

## Important APIs, Types, and Functions
The two global functions are `getcc` and `setcc`. Both accept a `struct pt_regs *` in `%o0` and use `PT_V9_TSTATE` plus `PT_V9_G1` offsets.

## Control Flow and State
`getcc()` loads saved TSTATE, shifts the ICC bits into the low nibble, masks them, and stores the result into saved `%g1`. `setcc()` loads saved TSTATE and saved `%g1`, clears the `TSTATE_ICC` field, masks the user-provided condition code bits, merges them into TSTATE, and stores the updated TSTATE.

## Persistence and Dependencies
Only the saved trap frame is mutated. The helpers depend on V9 TSTATE layout and `pt_regs` offsets matching assembly expectations.

## Integration Points, Risks, and Test Signals
These helpers integrate with user-visible get/set condition-code trap emulation. Risks are limited but include letting non-ICC TSTATE bits leak from user input or using stale offsets. Test signals include compatibility tests that execute getcc/setcc traps and verify only condition-code bits change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/getsetcc.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/head_32.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/head_32.S

## Purpose
`head_32.S` is the 32-bit SPARC boot entry. It validates supported machines, remaps the kernel to high virtual memory when needed, initializes early CPU/platform state, patches register-window routines, installs the trap table, and calls `sparc32_start_kernel()`.

## Important APIs, Types, and Functions
Important global data includes boot header fields `root_flags`, `root_dev`, `ram_flags`, `sparc_ramdisk_image`, `sparc_ramdisk_size`, `prom_vector_p`, `nwindows`, `nwindowsm1`, `linux_dbvec`, and `lvl14_save`. Key labels are `gokernel`, `execute_in_high_mem`, `leon_init`, `sun4d_init`, `sun4m_init`, `continue_boot`, and unsupported-machine paths.

## Control Flow and State
The entry saves ROM/debug vectors, detects whether the kernel is already mapped, copies the PROM level-14 handler, verifies SRMMU/LEON support, and creates a KERNBASE mapping by editing SRMMU page tables. Once high-mapped, it queries PROM `compatible`, chooses LEON/sun4m/sun4d initialization, sets boot CPU ID, clears stale MMU fault registers, enables supervisor/FPU/PIL state, initializes the stack, zeroes BSS, initializes `current_set`, computes the number of register windows, patches 7-window variants, installs `trapbase` in TBR, enables traps, and calls C startup.

## Persistence and Dependencies
Persistent boot state includes PROM pointers, CPU type string, register-window counts, boot CPU ID, trap table base, and boot header fields consumed by bootloaders. Dependencies include PROM node ops, SRMMU/LEON ASIs, trap table include `ttable_32.S`, patch labels in window/trap/return files, and platform-specific IRQ/SMP code.

## Integration Points, Risks, and Test Signals
Integration points are bootloader ABI, PROM, trap setup, CPU probing, SMP platform code, and early memory mapping. Risks include unsupported machine detection, incorrect physical/virtual relocation, 7-window patch mismatch, stale PROM timer/trap state, and bootloader header compatibility. Test signals are successful boot on sun4m, sun4d, and LEON configurations, correct unsupported sun4u message for 32-bit kernel, stable timer interrupts after trap-table switch, and correct `nwindows` reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/head_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/head_64.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/head_64.S

## Purpose
`head_64.S` is the sparc64 boot entry and assembly aggregation point. It maps the kernel at `KERNBASE`, detects sun4u/sun4v CPU families, applies CPU-specific patching, initializes trap/TSB layout, and includes the core sparc64 low-level assembly files.

## Important APIs, Types, and Functions
Global entry labels are `_start`, `start`, `_stext`, `stext`, `setup_trap_table`, and `setup_tba`. Global state includes boot header fields, PROM strings and caches, `prom_root_node`, `is_sun4v`, `sun4v_chip_type`, `prom_tba`, `tlb_type`, `swapper_tsb`, and `swapper_4m_tsb`.

## Control Flow and State
Boot clears address masking, uses PROM CIF calls to find root/chosen nodes, gets the MMU ihandle, translates the current PC mapping, maps the full kernel at `KERNBASE`, detects sun4v and CPU compatible strings, configures Cheetah/Spitfire/Niagara/M7-specific registers, selects and records `tlb_type`, runs copy/clear/page/cache/TLB patchers, initializes stack/current/per-cpu base, clears BSS, calls `prom_init()`, then `start_early_boot()`. `setup_trap_table()` asks firmware to install Linux's trap table, configures sun4v fault-info scratchpad, sets kernel primary context, disables PROM tick/STICK interrupts, initializes IRQ work state, and restores interrupt state.

## Persistence and Dependencies
Persistent state includes PROM metadata, physical boot mapping records, chip type, TLB type, TSB memory, trap table address, and boot header fields. The file includes `etrap_64.S`, `rtrap_64.S`, `fpu_traps.S`, `ivec.S`, `hvcalls.S`, TLB miss code, syscall tables, and CPU error handlers.

## Integration Points, Risks, and Test Signals
Integration spans bootloaders, OpenPROM, hypervisor, trap table, TSB/TLB code, IRQ init, CPU-specific optimized routines, and early C boot. Risks include PROM call-frame mistakes, KERNBASE mapping size/alignment errors, chip misclassification, wrong patch selection, and trap table placement constraints. Test signals are successful boot on sun4u/sun4v variants, correct `tlb_type`/chip logs, working trap-table handoff, stable TLB refill behavior, and no PROM timer interrupts after setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/head_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/helpers.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/helpers.S

## Purpose
`helpers.S` contains small sparc64 assembly helpers for register-window flushing, stack trace preparation, and hardware CPU ID retrieval.

## Important APIs, Types, and Functions
Exports include `__flushw_user`, `stack_trace_flush`, `real_hard_smp_processor_id`, and, under SMP, `hard_smp_processor_id`. `__flushw_user` is exported to modules.

## Control Flow and State
`__flushw_user()` repeatedly performs `save` until `%otherwin` reaches zero, then restores back the same number of windows. `stack_trace_flush()` disables interrupts, walks restorable register windows by changing CWP, stores `%fp` and `%i7` to each window's stack slots, restores CWP and PSTATE, and returns. CPU ID helpers use `__GET_CPUID()`.

## Persistence and Dependencies
State changes are limited to transient register-window state, stack slots for frame pointer/return address, and interrupt-enable state during the flush. It depends on V9 window registers, stack bias, and CPU-ID macros.

## Integration Points, Risks, and Test Signals
Integration points include stack unwinding, debugging, SMP CPU identification, and any caller needing user windows materialized. Risks include interrupt-state restoration mistakes, bad stack slots if window layout changes, and CPU-ID macro mismatch for sun4v/sun4u. Test signals are reliable stack traces without full `flushw`, correct CPU IDs on SMP, and no register-window corruption during signal/debug tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/helpers.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/hvapi.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/hvapi.c

## Purpose
`hvapi.c` manages negotiated sun4v hypervisor API group versions. It centralizes version registration, reference counting, lookup, and mandatory early registration for core groups.

## Important APIs, Types, and Functions
The core type is `struct api_info`, with group, major/minor, refcount, and `FLAG_PRE_API`. Public functions are `sun4v_hvapi_register()`, `sun4v_hvapi_unregister()`, `sun4v_hvapi_get()`, and boot-time `sun4v_hvapi_init()`. The static `api_table` lists supported HV groups.

## Control Flow and State
Registration looks up the group under `hvapi_lock`. If already referenced, only the same major version is accepted and the existing minor is returned. If unreferenced, it calls `sun4v_set_version()`, stores the actual minor on success, or emulates major 1 minor 0 for pre-API groups when the hypervisor reports bad trap/not supported. Successful registration increments refcount. Unregister decrements and when the refcount reaches zero calls `sun4v_set_version(group, 0, 0)` and clears stored versions. Init registers SUN4V 1.0 and CORE 1.6 or halts via PROM.

## Persistence and Dependencies
Persistent state is `api_table` and `hvapi_lock`. Dependencies are hypervisor version calls and PROM halt/printf for fatal early boot.

## Integration Points, Risks, and Test Signals
Integration includes IRQ negotiation, LDC/service channels, performance counters, reboot-data support, and other sun4v drivers. Risks include unbalanced unregister underflow, rejecting compatible minor-only differences due to major-only matching, and assumptions for pre-API fallback. Test signals are boot-time HVAPI registration, successful registration/unregistration by users, correct minor return values, and graceful failure on unsupported groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/hvapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/hvcalls.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/hvcalls.S

## Purpose
`hvcalls.S` provides assembly wrappers around sun4v hypervisor fast and core trap calls. It exposes the low-level ABI used by IRQ, CPU, MMU, LDC, console, service-channel, performance, reboot, and DAX/CCB code.

## Important APIs, Types, and Functions
Wrappers include interrupt functions (`sun4v_devino_to_sysino`, `sun4v_intr_*`, `sun4v_vintr_*`), CPU functions (`sun4v_cpu_*`), MMU functions, version negotiation, TOD/console/machine state, LDC queue/map/copy calls, service channel calls, MMU statistics, performance-register calls for Niagara/N2/VT/T5/M7, reboot data, and CCB functions. Several symbols are exported, including watchdog/perf/CCB helpers.

## Control Flow and State
Most wrappers place the HV function number in `%o5`, execute `ta HV_FAST_TRAP` or `ta HV_CORE_TRAP`, store out-parameters from `%o1`/`%o2`/`%o3` into caller-provided pointers, and return `%o0` status. Some wrappers translate results, such as `sun4v_cpu_state()` returning negative status or state, and console read mapping break/hup pseudo-results. Service send/recv use a register window because they need more stable argument preservation.

## Persistence and Dependencies
The file mutates no kernel data directly except caller-provided out-parameters. It depends completely on the sun4v hypervisor ABI, constants in `<asm/hypervisor.h>`, CCB offsets, and SPARC calling convention.

## Integration Points, Risks, and Test Signals
Integration is foundational for sun4v boot, IRQ, LDC/VIO, domain services, CPU hotplug, console, performance counters, and reboot. Risks include mismatched out-parameter registers, ABI drift across hypervisor versions, missing error handling in callers, and a suspicious `sun4v_ccb_submit()` dependence on `%o4/%o5` pointer conventions. Test signals are HVAPI negotiation, CPU start/stop, interrupt enable/EOI, LDC traffic, console I/O, reboot data setting, and CCB submit/info/kill status on capable hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/hvcalls.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/hvtramp.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/hvtramp.S

## Purpose
`hvtramp.S` is the sun4v hypervisor secondary-CPU startup trampoline. It runs with physical addressing, installs required permanent mappings and fault areas, enables the MMU, initializes CPU-local kernel state, and enters SMP bring-up.

## Important APIs, Types, and Functions
Global symbols are `hv_cpu_startup` and `hv_cpu_startup_end`. It consumes a descriptor in `%o0` using `HVTRAMP_DESCR_*` and `HVTRAMP_MAPPING_*` offsets and calls hypervisor traps for permanent mapping, fault-area configuration, and MMU enablement.

## Control Flow and State
The trampoline initializes privileged CPU registers, trap table base, scratchpad CPU ID and fault-info virtual address, iterates descriptor mappings with `HV_FAST_MMU_MAP_PERM_ADDR`, configures the fault area, sets privileged PSTATE, loads the thread register, enables the MMU and branches to a virtual continuation. After MMU enable it clears FPRS/ASI, zeros primary/secondary contexts, sets `%g6`, current task, and stack, initializes IRQ work, registers mondo queues, initializes current CPU trap state, enables interrupts, calls `smp_callin()`, and panics if it returns. Any HV failure loops forever.

## Persistence and Dependencies
State includes CPU privileged registers, scratchpad registers, MMU permanent mappings, trap table base, thread register, stack pointer, and per-CPU mondo queues. Dependencies include descriptor layout, hypervisor ABI, trap block state, `init_cur_cpu_trap()`, and SMP bring-up.

## Integration Points, Risks, and Test Signals
Integration is with sun4v SMP CPU start (`sun4v_cpu_start()`), irq mondo setup, and trap initialization. Risks include descriptor mismatch, no diagnostics on failure loops, mapping order errors before MMU enable, and calling routines that rely on not-yet-initialized CPU state. Test signals are secondary CPU online success, correct hard CPU IDs, registered mondo queues, working IPIs on hotplugged CPUs, and no early trap-table faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/hvtramp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/idprom.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/idprom.c

## Purpose
`idprom.c` reads and validates the SPARC IDPROM, exposes the platform MAC address, and prints machine-type information on sparc32.

## Important APIs, Types, and Functions
Global `struct idprom *idprom` is exported. Functions are `arch_get_platform_mac_address()`, `idprom_init()`, internal `calc_idprom_cksum()`, and sparc32 `display_system_type()`.

## Control Flow and State
`idprom_init()` asks PROM to copy the IDPROM into `idprom_buffer`, points `idprom` at it, warns on unknown format or checksum mismatch, displays machine type, and logs Ethernet address. The checksum is XOR over bytes 0 through 0x0e. On sparc32, `display_system_type()` matches `id_machtype` against known Sun/LEON machine constants or queries `banner-name` for OBP sun4m systems.

## Persistence and Dependencies
Persistent state is the static `idprom_buffer` and exported `idprom` pointer. Dependencies include PROM IDPROM APIs, machine constants, and Ethernet address formatting.

## Integration Points, Risks, and Test Signals
Integration includes network default MAC address selection and platform identification. Risks are mostly diagnostic: checksum failure does not stop boot, unknown machine types only warn, and callers assume `idprom_init()` has run before requesting MAC address. Test signals are valid Ethernet address log, correct `TYPE:` log on sparc32, and warning behavior for corrupted IDPROM fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/idprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/iommu-common.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/iommu-common.c

## Purpose
`iommu-common.c` implements shared bitmap/pool allocation for SPARC IOMMU mapping tables. It is derived from the powerpc allocator and supports per-pool hints, optional large allocation pool, segment-boundary constraints, and lazy flush callbacks.

## Important APIs, Types, and Functions
Public functions are `iommu_tbl_pool_init()`, `iommu_tbl_range_alloc()`, and `iommu_tbl_range_free()`. Internal helpers manage `IOMMU_NEED_FLUSH`, per-CPU pool hashes, and mapping entry-to-pool selection.

## Control Flow and State
Initialization hashes CPUs to pools, sets table shift and flush callback, configures pool count, flags, pool size, hints, and optional top-quarter large pool. Allocation chooses a pool from per-CPU hash or the large pool, honors a caller handle if it is inside the pool, clamps to device DMA mask, computes boundary constraints, calls `iommu_area_alloc()`, retries from pool starts and across pools, marks flush-needed on wrap/failure, and invokes `lazy_flush()` before reusing wrapped space. Free computes or accepts an entry index, finds the owning pool, and clears the bitmap range under the pool lock.

## Persistence and Dependencies
Persistent state lives in `struct iommu_map_table`: bitmap, pools, hints, flags, table base/shift, and lazy flush callback. Dependencies include `iommu-helper`, DMA segment-boundary helpers, per-CPU hashes, and spinlocks.

## Integration Points, Risks, and Test Signals
Used by sparc64 IOMMU DMA mapping code and potentially other SPARC IOMMU users. Risks include pool size assumptions when `nr_pools` is not power-of-two, DMA mask limit edge cases, lazy flush ordering, and bitmap leaks after failed multi-segment maps. Test signals are DMA map/unmap stress, SG merging with boundaries, low DMA mask devices, large allocations, and no bitmap exhaustion after repeated failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/iommu-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/iommu.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/iommu.c

## Purpose
`iommu.c` implements sparc64 sun4u-style DMA mapping operations through an IOMMU and streaming buffer. It provides the architecture `dma_map_ops` for coherent allocation, physical and scatterlist streaming mappings, unmapping, synchronization, and DMA mask checks.

## Important APIs, Types, and Functions
Publicly visible functions include `iommu_table_init()` and exported `dma_ops`. DMA operations are `dma_4u_alloc_coherent()`, `dma_4u_free_coherent()`, `dma_4u_map_phys()`, `dma_4u_unmap_phys()`, `dma_4u_map_sg()`, `dma_4u_unmap_sg()`, sync helpers, and `dma_4u_supported()`. Internal helpers include `iommu_flushall()`, `iopte_make_dummy()`, context allocation/free, `strbuf_flush()`, and `fetch_sg_ctx()`.

## Control Flow and State
Table init allocates the bitmap, dummy page, and IOMMU page table, fills all IOPTEs with dummy-page mappings, and sets up the shared pool allocator. Coherent allocation gets pages, allocates IOMMU entries, writes consistent writable IOPTEs, and returns CPU plus DVMA address. Streaming map allocates entries and optional context, writes IOPTEs with streaming-buffer or consistent flags and write permission based on direction. Unmap records context, flushes streaming buffers for device-to-CPU paths unless skipped, replaces IOPTEs with dummy mappings, frees context, and frees bitmap entries. SG mapping allocates and writes per-element IOPTEs while merging adjacent DMA segments subject to max segment and boundary rules, with rollback on failure.

## Persistence and Dependencies
Persistent state is in `struct iommu`, `struct strbuf`, the IOPTE table, context bitmap, dummy page, flush flag memory, and allocator bitmap. Dependencies include physical bypass ASIs, streaming buffer registers, `iommu-common`, device archdata, PCI quirk `ali_sound_dma_hack()`, and Linux DMA API.

## Integration Points, Risks, and Test Signals
Integration points are all sparc64 DMA-capable devices using `dma_ops`. Risks include context leaks on allocation failures, dummy mappings hiding stale-device DMA, streaming-buffer flush timeouts, SG rollback under lock while freeing allocator ranges, unsupported MMIO map path, and order limit for coherent allocation. Test signals are DMA API selftests, disk/network I/O under IOMMU, streaming buffer timeout absence, SG map/unmap leak checks, DMA mask rejection/quirk behavior, and cache coherency for bidirectional transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/iommu_common.h -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/iommu_common.h

## Purpose
`iommu_common.h` defines shared constants and helpers for UltraSPARC SBUS/PCI IOMMU code.

## Important APIs, Types, and Functions
It defines `IO_PAGE_SHIFT`, `IO_PAGE_SIZE`, `IO_PAGE_MASK`, `IO_PAGE_ALIGN()`, `IO_TSB_ENTRIES`, `IO_TSB_SIZE`, `IOMMU_PAGE_SHIFT`, `SG_ENT_PHYS_ADDRESS()`, and helper `is_span_boundary()`.

## Control Flow and State
The only executable logic is `is_span_boundary()`, which computes a physical address from the output SG entry, computes the number of IO pages covering the merged output length plus candidate SG length, and delegates to `iommu_is_span_boundary()`.

## Persistence and Dependencies
There is no persistent state. The header depends on Linux SG/device/IOMMU helper definitions and `<asm/iommu.h>`.

## Integration Points, Risks, and Test Signals
The constants define the IOMMU page geometry used by `iommu.c` and `iommu-common.c`. Risks include mismatch with hardware IOTLB page size or incorrect SG virtual-to-physical assumptions for non-linear scatterlists. Test signals are SG DMA mappings that respect segment boundaries, correct table sizing, and no off-by-one mapping around 8 KiB IO page boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/iommu_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ioport.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/ioport.c

## Purpose
`ioport.c` implements sparc32 I/O virtual mapping allocation and DVMA resource reservation. It backs `ioremap()`, `iounmap()`, OF resource mapping, `/proc` map visibility, and limited DMA cache synchronization behavior.

## Important APIs, Types, and Functions
Public APIs are `ioremap()`, `iounmap()`, `of_ioremap()`, `of_iounmap()`, `sparc_dma_alloc_resource()`, `sparc_dma_free_resource()`, optional `sbus_set_sbus64()`, and `arch_sync_dma_for_cpu()`. Internal helpers are `_sparc_alloc_io()`, `_sparc_ioremap()`, `_sparc_free_io()`, `xres_alloc()`, and `xres_free()`.

## Control Flow and State
The file maintains root resources `sparc_iomap` and `_sparc_dvma`. Early mappings use a static `xresv` mini-allocator before falling back to `kmalloc`. `_sparc_ioremap()` allocates virtual space from `sparc_iomap`, maps physical bus pages with `srmmu_mapiorange()`, and returns the offset-adjusted virtual address. `iounmap()` looks up the resource by page-aligned virtual address, unmaps via `srmmu_unmapiorange()`, releases the resource, and frees static or dynamic storage. DVMA allocation creates a named resource under `_sparc_dvma`; free validates address alignment and size. Proc handlers list child resources.

## Persistence and Dependencies
Persistent state includes resource trees, static `xresv`, and proc entries. Dependencies include SRMMU IO-range mapping, Open Firmware resources, LEON cache-snooping helpers, Linux resource allocator, and procfs.

## Integration Points, Risks, and Test Signals
Integration points include PCI/SBUS drivers, early timers/interrupt controllers, OF device mapping, and DMA allocators. Risks include hard PROM halt on IO map exhaustion, linear lookup cost in `iounmap()`, static name truncation, resource leaks on invalid frees, and full D-cache flush for non-snooping LEON DMA. Test signals are successful early device MMIO, `/proc/io_map` and `/proc/dvma_map` content, ioremap/iounmap leak tests, and DMA coherency on LEON.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ioport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/irq.h -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/irq.h

## Purpose
`irq.h` is the local sparc32 IRQ interface shared by platform IRQ implementations and low-level entry code.

## Important APIs, Types, and Functions
It defines `struct irq_bucket`, sun4m hard/soft interrupt bit macros, sun4d IRQ limits, `irq_map`, sun4m interrupt register layouts, feature bits, and `struct sparc_config`. It declares `irq_alloc()`, `irq_link()`, `irq_unlink()`, `handler_irq()`, `leon_get_irqmask()`, `sparc_floppy_irq()`, `sun4m_nmi()`, `sun4d_handler_irq()`, and optional `sun4d_ipi_interrupt()`.

## Control Flow and State
There is no implementation. The header defines how virtual IRQs map from platform hardware identifiers/PILs into linked `irq_bucket` chains, and how platform init functions provide timer and IRQ construction callbacks through `sparc_config`.

## Persistence and Dependencies
Persistent shared state is `irq_map` and `sparc_config`, with external sun4m interrupt-controller MMIO pointers. Dependencies include platform devices and CPU type definitions.

## Integration Points, Risks, and Test Signals
Integration includes `irq_32.c`, sun4m/sun4d/LEON IRQ controller files, trap handlers in `entry.S`, timer setup, and floppy fast interrupt support. Risks are ABI/layout mismatch with assembly and platform files, insufficient `SUN4D_MAX_IRQ`, and incorrect feature flags causing timer misuse. Test signals are platform-specific IRQ init, `/proc/interrupts` counts, timer tick delivery, sun4d virtual IRQ allocation, and SMP IPI handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/irq_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/irq_32.c

## Purpose
`irq_32.c` provides generic sparc32 IRQ glue: local interrupt enable/disable primitives, virtual IRQ allocation and PIL chaining, generic IRQ dispatch from trap level, `/proc/interrupts` extras, floppy fast interrupt integration, and platform IRQ initialization dispatch.

## Important APIs, Types, and Functions
Exported functions include `arch_local_irq_save()`, `arch_local_irq_enable()`, `arch_local_irq_restore()`, and optional `sparc_floppy_request_irq()`. Other key functions are `irq_alloc()`, `irq_link()`, `irq_unlink()`, `arch_show_interrupts()`, `handler_irq()`, `sparc_floppy_irq()`, and `init_IRQ()`.

## Control Flow and State
Local IRQ primitives manipulate PSR PIL bits. `irq_alloc()` reuses or creates a virtual IRQ in `irq_table` for a `(real_irq,pil)` pair. `irq_link()` inserts the bucket into `irq_map[pil]`; `irq_unlink()` removes it. `handler_irq()` sets IRQ regs, enters IRQ context, walks the bucket chain for the PIL, and invokes `generic_handle_irq()`. Floppy setup requests a normal IRQ, records globals used by `floppy_hardint`, patches trap table entries for a fast handler, and flushes caches. `init_IRQ()` selects sun4m, sun4d, or LEON controller initialization based on `sparc_cpu_model`.

## Persistence and Dependencies
Persistent state includes `sparc_config`, `irq_table`, `irq_map`, locks, optional floppy pseudo-DMA globals, and patched trap table instructions. Dependencies include generic IRQ core, platform IRQ files, cache flush, PCIC, LEON, and assembly entry points.

## Integration Points, Risks, and Test Signals
Integration points are trap-level IRQ entry, platform interrupt controllers, floppy driver, SMP interrupt statistics, and timer setup. Risks include linked-list corruption in `irq_unlink()` if bucket is absent, virtual IRQ exhaustion, trap-table patch coherency, and PSR PIL manipulation bugs. Test signals include timer and device interrupts, shared PIL dispatch, request/free cycles, floppy transfer interrupts, `/proc/interrupts` RES/CAL/NMI lines, and platform boot on sun4m/sun4d/LEON.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/irq_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/irq_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/irq_64.c

## Purpose
`irq_64.c` implements sparc64 IRQ initialization, allocation, interrupt-vector routing, sun4u register-backed IRQ chips, sun4v hypervisor IRQ/VIRQ chips, hard/soft IRQ stacks, PROM timer shutdown, and sun4v mondo queue setup.

## Important APIs, Types, and Functions
Global state includes `ivector_table`, `ivector_table_pa`, `hardirq_stack`, and `softirq_stack`. Public functions include `irq_alloc()`, `irq_free()`, `build_irq()`, `sun4v_build_irq()`, `sun4v_build_virq()`, `handler_irq()`, `do_softirq_own_stack()`, `fixup_irqs()`, `init_irqwork_curcpu()`, `sun4v_register_mondo_queues()`, and `init_IRQ()`. Key types are `struct irq_handler_data`, `struct ino_bucket`, and `struct sun5_timer`.

## Control Flow and State
Boot calls `irq_init_hv()` to negotiate `HV_GRP_INTR`, initializes the ivector table unless using cookie-only VIRQs, maps and disables PROM timers, allocates sun4v mondo/error queues, initializes send-mondo info, registers boot CPU queues, clears pending softints, enables interrupts, and installs a timer action on IRQ0. sun4u `build_irq()` derives INO from IMAP, stores the virtual IRQ in the ivector bucket, and uses `sun4u_irq` callbacks to program IMAP/ICLR. sun4v can either use sysino buckets or cookie-only VIRQ delivery; cookie mode stores an inverted physical pointer to a per-IRQ bucket via the hypervisor. `handler_irq()` atomically grabs and clears the per-CPU irq worklist, switches to hardirq stack, walks bucket chains using bypass ASIs, clears chain pointers, and dispatches generic IRQs.

## Persistence and Dependencies
Persistent state includes IRQ descriptors, handler data, ivector buckets, hypervisor IRQ API version, mondo queue real addresses, PROM timer saved limits, trap-block irq worklists, and stack arrays. Dependencies include hypervisor wrappers, generic IRQ core, Open Firmware, UPA/IMAP registers, Starfire CPU translation, cpumap, trap block, and softirq stack support.

## Integration Points, Risks, and Test Signals
Integration points include PCI/UPA device IRQ construction, LDC/VIO virtual interrupts, SMP IPIs/mondos, CPU hotplug affinity fixups, timer initialization, and trap-vector assembly. Risks include HV IRQ API version ambiguity, cookie/sysino duplicate detection, ivector table sizing for large devhandle/devino systems, bypass/non-bypass coherency, lost bucket chains if `handler_irq()` races, PROM timer side effects, and queue allocation alignment requirements. Test signals are successful IRQ API log, device IRQ delivery and affinity changes, VIRQ cookie interrupts, hotplug `fixup_irqs()`, mondo queue registration on all CPUs, hardirq/softirq stack operation, and no BAD IRQ acknowledgements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/irq_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/itlb_miss.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/itlb_miss.S

## Purpose
`itlb_miss.S` is the sparc64 instruction TLB miss trap-table fragment. It performs a fast TSB lookup and loads the ITLB when the entry matches and is executable.

## Important APIs, Types, and Functions
There are no callable functions. The fragment uses `ASI_IMMU_TSB_8KB_PTR`, `ASI_IMMU`, `ASI_ITLB_DATA_IN`, `TSB_LOAD_QUAD()`, `_PAGE_EXEC_4U`, and external labels `kvmap_itlb`, `tsb_miss_itlb`, and `tsb_do_fault`.

## Control Flow and State
The code reads the IMMU TSB pointer and tag target, branches context-zero misses to kernel-vmap handling, loads a TSB quad, compares tags, routes misses to `tsb_miss_itlb` with `FAULT_CODE_ITLB`, checks the executable bit, routes non-executable translations to the fault path, writes a valid executable TTE to the ITLB, and retries.

## Persistence and Dependencies
It mutates only ITLB hardware state. Dependencies include TSB layout, executable bit encoding, trap-table register conventions, and sparc64 TLB/fault handlers.

## Integration Points, Risks, and Test Signals
Integration is with instruction fetch fault handling and kernel/user execution permissions. Risks include executing from non-executable mappings if `_PAGE_EXEC_4U` handling is wrong, excessive full miss handling due to tag mismatch bugs, and icache-line layout sensitivity. Test signals include NX permission faults, execution after ITLB eviction, module/text execution, and stable boot under instruction TLB pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/itlb_miss.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ivec.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/ivec.S

## Purpose
`ivec.S` handles sparc64 interrupt-vector packets received from UPA-style devices. It chains interrupt buckets onto a per-CPU worklist and raises the appropriate soft interrupt level for later C dispatch.

## Important APIs, Types, and Functions
The global function is `do_ivec`, with an internal cross-call path `do_ivec_xcall`. It uses `ivector_table_pa`, `trap_block[].irq_worklist_pa`, `ino_bucket.__irq_chain_pa`, and softint/processor interrupt registers.

## Control Flow and State
The handler extracts the INO from the incoming vector data, handles cross-call vectors specially, computes the physical address of the matching `ino_bucket`, links it at the head of the current CPU's `irq_worklist_pa`, and sets a soft interrupt bit so `handler_irq()` will later drain the list. If the vector is a cross-call, it jumps directly to the cross-call target.

## Persistence and Dependencies
Persistent state is the per-CPU physical worklist and bucket chain pointers. Dependencies include exact `struct ino_bucket` layout from `entry.h`, trap block layout, and IRQ dispatch in `irq_64.c`.

## Integration Points, Risks, and Test Signals
Integration is with hardware interrupt vector traps, SMP cross-calls, and generic IRQ delivery. Risks include bucket-chain corruption, lost interrupts from non-atomic list updates, incorrect physical addressing, and layout drift. Test signals are high-rate device interrupts, SMP cross-calls, correct `/proc/interrupts` increments, and absence of stuck nonzero bucket chains after IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ivec.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/jump_label.c

## Purpose
`jump_label.c` implements SPARC static key text patching, replacing NOPs with unconditional branches and back.

## Important APIs, Types, and Functions
The public architecture hook is `arch_jump_label_transform(struct jump_entry *entry, enum jump_label_type type)`.

## Control Flow and State
For `JUMP_LABEL_JMP`, the function computes target-code offset, validates word alignment, chooses a V9 predicted branch encoding on sparc64 when the displacement fits WDISP19, otherwise uses WDISP22 `ba`, and asserts WDISP22 range. For non-jump it writes SPARC NOP `0x01000000`. The write is protected by `text_mutex` and followed by `flushi()`.

## Persistence and Dependencies
Persistent state is patched kernel text. Dependencies include jump-label core, `text_mutex`, SPARC branch encoding, and instruction-cache flush.

## Integration Points, Risks, and Test Signals
Integration includes static keys across the kernel. Risks are branch displacement overflow, sign/range mistakes, lack of atomic patching beyond mutex protection, and stale icache if `flushi()` is insufficient on a CPU variant. Test signals are static key enable/disable tests, boot with jump labels enabled, and no illegal instruction traps near patched sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/kernel.h -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/kernel.h

## Purpose
`kernel.h` is a local SPARC kernel-private declaration hub. It connects architecture assembly and C files without exporting all declarations through global UAPI-style headers.

## Important APIs, Types, and Functions
It declares process creation helpers (`sparc_clone`, `sparc_fork`, `sparc_vfork`, `sparc_clone3`), sparc64 setup/syscall/trap/SMP/compat helpers, sparc32 setup/trap/IRQ/SMP/signal/ptrace/window helpers, and platform externs. The sparc64 inline `kimage_addr_to_ra()` converts a kernel virtual address to real address using `kern_base` and `KERNBASE`.

## Control Flow and State
There is no implementation. It fixes architecture-local linkage between files such as `entry.S`, `ds.c`, IRQ code, trap handlers, signal code, and setup code.

## Persistence and Dependencies
The header declares persistent state such as `sparc_pmu_type`, `fsr_storage`, `ncpus_probed`, boot/trap symbols, PCIC registers, and platform vectors. Dependencies include trap, head, IO, ftrace, and interrupt headers.

## Integration Points, Risks, and Test Signals
Integration is broad across sparc32 and sparc64 architecture code. Risks include stale declarations after function signature changes, config-guard mismatches, and misuse of `kimage_addr_to_ra()` before `kern_base` is valid. Test signals are clean sparc32/sparc64 builds across configs and boot paths that exercise declared assembly/C interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/kgdb_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/kgdb_32.c

## Purpose
`kgdb_32.c` implements KGDB architecture support for 32-bit SPARC, including register conversion, breakpoint trap handling, continue/detach semantics, and PC updates.

## Important APIs, Types, and Functions
Key functions are `pt_regs_to_gdb_regs()`, `sleeping_thread_to_gdb_regs()`, `gdb_regs_to_pt_regs()`, `kgdb_arch_handle_exception()`, `kgdb_trap()`, `kgdb_arch_init()`, `kgdb_arch_exit()`, and `kgdb_arch_set_pc()`. It defines `arch_kgdb_ops` with breakpoint instruction `ta 0x7d`.

## Control Flow and State
Register conversion copies globals/outs from `pt_regs`, locals/ins from the register window pointed to by frame pointer, and fills unavailable FP/control registers with zero. Sleeping-thread conversion uses `thread_info` saved kernel stack, PSR/WIM, and PC. Reverse conversion updates saved registers and preserves PSR CWP when changing PSR. `kgdb_arch_handle_exception()` handles continue and detach/kill packets, optionally sets PC from a hex parameter, and skips over `arch_kgdb_breakpoint` when resuming. `kgdb_trap()` forwards user-mode traps to normal hardware interrupt handling; kernel-mode traps flush windows, disable local IRQs, invoke KGDB core, and restore IRQs.

## Persistence and Dependencies
Persistent state is minimal; it reads/writes `pt_regs`, task `thread_info`, and live register windows. Dependencies include KGDB core, trapbase symbols, `flushw_all()`, `arch_kgdb_breakpoint`, and 32-bit register-window layout.

## Integration Points, Risks, and Test Signals
Integration points are `entry.S` KGDB trap entry, GDB remote protocol, and normal trap handling for user-mode breakpoints. Risks include dereferencing invalid user frame pointers while converting locals/ins, PSR/CWP corruption, and failing to skip breakpoint instructions. Test signals are KGDB connect, register read/write, continue from breakpoint, sleeping task inspection, and user-mode breakpoint fallback to normal trap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/kgdb_32.c -->
