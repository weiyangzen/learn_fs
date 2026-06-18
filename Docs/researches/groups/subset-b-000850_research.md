# subset-b-000850 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/traps_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/traps_64.c

## Purpose
Implements the SPARC64 C-side trap, exception, and processor-error handlers used by the trap tables and low-level assembly entry paths. It covers bad traps, instruction/data access exceptions, unaligned memory traps, illegal instruction emulation dispatch, FPU exceptions, Cheetah/Spitfire/Sun4v error reporting, stack traces, panic/oops handling, and per-CPU trap block initialization.

## Important APIs, Types, And Functions
Key exported or externally reached entry points include `bad_trap`, `bad_trap_tl1`, `spitfire_insn_access_exception`, `sun4v_insn_access_exception`, `spitfire_data_access_exception`, `sun4v_data_access_exception`, `spitfire_access_error`, `cheetah_fecc_handler`, `cheetah_cee_handler`, `cheetah_deferred_handler`, `cheetah_plus_parity_error`, `sun4v_resum_error`, `sun4v_nonresum_error`, `do_fpieee`, `do_fpother`, `do_tof`, `do_div0`, `do_illegal_instruction`, `mem_address_unaligned`, `sun4v_do_mna`, `sun4v_mem_corrupt_detect_precise`, `do_privop`, `do_getpsr`, `init_cur_cpu_trap`, and `trap_init`. Important data structures include `tl1_traplog`, `afsr_error_table`, `sun4v_error_entry`, the global `trap_block[NR_CPUS]`, `cpu_mondo_counter`, and the Cheetah error scoreboard `cheetah_error_log`.

## Control Flow
Low-level trap-table vectors enter these handlers with populated `pt_regs` and architecture-specific status arguments. Normal user exceptions call `notify_die`, normalize 32-bit PCs when needed, and deliver `SIGSEGV`, `SIGBUS`, `SIGILL`, `SIGFPE`, or `SIGEMT`. Kernel exceptions first consult exception tables for uaccess fixups and otherwise call `die_if_kernel`. Cheetah and Spitfire error flows decode AFSR/AFAR, flush or repair caches, log DIMM syndrome data, and decide whether recovery is possible. Sun4v resumable/non-resumable flows copy hypervisor error queue entries out of per-CPU buffers, release the queue slot, handle shutdown/MCD/user PIO cases, and panic only when the error cannot be contained. `do_illegal_instruction` tries POPC, LDQ/STQ, VIS, and math emulation before signaling an illegal opcode.

## State And Persistence
Persistent kernel state includes registered DIMM-printer callbacks, per-CPU trap blocks, Cheetah cache-flush geometry, Cheetah error tables, Sun4v overflow counters, and saved global TLB error-report fields. Handlers mutate `pt_regs` PCs for signal delivery, instruction emulation, exception-table recovery, and syscall-compatible `getpsr`. Error handlers can intentionally pin bad physical pages with `get_page` so they are not reused.

## Dependencies And Integration Points
This file integrates with trap vectors in `ttable_64.S`, TSB and window-fixup assembly, `unaligned_64.c`, VIS and math emulation, FPU state helpers, perf software events, notifier/die chains, exception tables, Sun4v hypervisor queues, OBP/prom DIMM lookup, PCI poke probing, cache/ASI accessors, and Linux signal/oops machinery.

## Risks And Edge Cases
Most routines run in fragile trap context with limited register and locking freedom. Wrong PC/TNPC updates can retry or skip the wrong instruction. Cache-error recovery depends on CPU-family-specific AFSR semantics and can silently become unrecoverable if error status changes while traps are disabled. Exception-table fixups must only be used for known kernel uaccess sites. Sun4v error queue handling must release entries after copying, and user-address recovery for deferred errors may only be approximate.

## Test Signals
Signals include SPARC64 boot and trap-table bring-up, compile-time `BUILD_BUG_ON` offset checks in `trap_init`, fault-injection paths for uaccess exception-table fixups, unaligned-access tests, illegal POPC/VIS/mathemu emulation tests, PCI probe fault handling, Sun4v LDOM error queue events, and observable kernel logs/panics from ECC/parity handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/traps_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/tsb.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/tsb.S

## Purpose
Provides SPARC64 TSB and TLB miss assembly paths, plus helper routines for TSB insertion, invalidation, context switching, copying, and initialization. It is the fast path between hardware or hypervisor TLB misses and Linux page tables.

## Important APIs, Types, And Functions
Entry labels include `tsb_miss_dtlb`, `tsb_miss_itlb`, `tsb_miss_page_table_walk`, `tsb_reload`, `tsb_do_fault`, `sparc64_realfault_common`, `winfix_trampoline`, `__tsb_insert`, `tsb_flush`, `__tsb_context_switch`, `copy_tsb`, `tsb_init`, and `NGtsb_init`. It relies heavily on macros such as `TRAP_LOAD_TRAP_BLOCK`, `USER_PGTABLE_WALK_TL1`, `TSB_LOAD_QUAD`, `TSB_LOCK_TAG`, `TSB_WRITE`, and `TSB_STORE`.

## Control Flow
DTLB/ITLB miss stubs read the faulting virtual address, attempt a huge-page TSB lookup when enabled, then walk the current page table from the per-CPU trap block. Valid PTEs are written into the TSB and loaded into DTLB/ITLB, with Sun4v patched paths branching to hypervisor TLB load code. Invalid, non-executable, or missing mappings branch through `tsb_do_fault` into `do_sparc64_fault`; nested trap cases use `winfix_trampoline`. Context switches update per-CPU PGD/TSB state and either hypervisor scratchpad/fast-trap descriptors or Sun4u MMU TSB registers and locked TLB mappings.

## State And Persistence
State lives in TSB entries, per-CPU `trap_per_cpu` fields for page-table physical addresses and huge TSB config, Sun4v scratchpad registers, MMU context registers, and optional locked TLB mappings for TSB virtual aliases. `tsb_init` and `NGtsb_init` persist invalid-bit initialization across a TSB allocation.

## Dependencies And Integration Points
This code is included from SPARC64 TLB miss vectors in `ttable_64.S` and depends on page-table format bits, hypervisor fast traps, Sun4v patch sections, huge-page setup, `do_sparc64_fault`, and linker-collected patch sections from `vmlinux.lds.S`.

## Risks And Edge Cases
TSB tag locking must avoid racing with concurrent invalidation. Huge-page TSB allocation may be required from trap context and therefore bounces through a full trap frame. Sun4u versus Sun4v patching changes real instructions in place, so section boundaries and register conventions must remain exact. A bad PTE executable check on ITLB misses would execute non-executable pages.

## Test Signals
Signals include successful SPARC64 boot, context switching across processes, demand faults, ITLB execute-permission faults, hugepage and transparent hugepage faults, TSB resize/copy operations, and stress tests that invalidate TSB entries under concurrent TLB misses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/tsb.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ttable_32.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/ttable_32.S

## Purpose
Defines the SPARC32 trap table starting at `_start`, including boot entry, hardware traps, interrupt levels, syscall traps, register-window traps, compatibility traps, and optional SMP per-CPU trap tables.

## Important APIs, Types, And Functions
Primary exported labels are `_start`, `_stext`, `trapbase`, `trapbase_cpu0` through `trapbase_cpu3` under SMP, `t_nmi`, and `end_traptable`. The table is built with macros including `TRAP_ENTRY`, `TRAP_ENTRY_INTERRUPT`, `BAD_TRAP`, `SRMMU_TFAULT`, `SRMMU_DFAULT`, `WINDOW_SPILL`, `WINDOW_FILL`, `BREAKPOINT_TRAP`, `LINUX_SYSCALL_TRAP`, `GETCC_TRAP`, `SETCC_TRAP`, `GETPSR_TRAP`, and `KGDB_TRAP`.

## Control Flow
Hardware vectors index directly into fixed-width trap-table slots. The reset vector branches to `gokernel`; memory-management faults enter SRMMU handlers; window overflow and underflow branch to the dedicated window assembly; interrupts dispatch by level; trap `0x90` enters the Linux syscall path; selected software traps implement breakpoint, flush-window, get/set condition codes, and get-PSR behavior. Most unused vectors explicitly land in `BAD_TRAP`.

## State And Persistence
The file defines static boot and trap-table code rather than mutable runtime state. Under SMP, duplicate trap tables persist for secondary CPUs so each CPU can use the same vector layout.

## Dependencies And Integration Points
It depends on SPARC32 trap macros and handlers from entry, fault, syscall, IRQ, KGDB, SRMMU, and window-management code. Link placement is controlled by the kernel linker script and the `__HEAD` section.

## Risks And Edge Cases
Trap slots are architectural ABI: instruction count, alignment, and vector number must be exact. SMP duplicate tables must stay semantically equivalent to the boot CPU table. Misrouting trap `0x90` or register-window traps would break basic process execution.

## Test Signals
Signals include SPARC32 boot to `gokernel`, syscall smoke tests, timer and device IRQ handling, page faults, illegal instruction and divide-by-zero traps, register-window spill/fill paths, KGDB/breakpoint traps, and SMP secondary CPU bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ttable_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ttable_64.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/ttable_64.S

## Purpose
Defines SPARC V9 trap tables for TL0 and TL1, including boot, faults, interrupts, TLB misses, register-window spill/fill vectors, syscall traps, kprobes, kgdb, uprobes, Sun4v mondos, and patchable Cheetah/Sun4v error vectors.

## Important APIs, Types, And Functions
Exported labels include `sparc64_ttable_tl0`, `sparc64_ttable_tl1`, `tl0_icpe`, `tl1_icpe`, `tl0_dcpe`, `tl1_dcpe`, `tl0_fecc`, `tl1_fecc`, `tl0_cee`, `tl1_cee`, `tl0_iae`, `tl1_iae`, `tl0_dae`, and `tl1_dae`. It uses macros such as `TRAP`, `TRAP_NOSAVE`, `TRAP_7INSNS`, `TRAP_SAVEFPU`, `TRAP_IRQ`, `TRAP_NMI_IRQ`, `SUN4V_ITSB_MISS`, `SUN4V_DTSB_MISS`, `TRAP_UTRAP`, `UPROBES_TRAP`, and the spill/fill macros.

## Control Flow
TL0 handles ordinary exceptions and includes fast TLB miss handlers from `itlb_miss.S`, `dtlb_miss.S`, and `dtlb_prot.S`. TL1 handles nested traps and generally routes unexpected conditions to fatal TL1 C handlers. Trap vectors for cache/ECC/parity start as bad traps and are patched by `cheetah_ecache_flush_init`. Syscall, kprobe, kgdb, uprobe, get/set context, and user-trap vectors dispatch to their specialized entry paths.

## State And Persistence
The table is static executable state, but selected vector slots are intentionally mutable during CPU-family initialization. Its labels are also persistent anchors for patching and diagnostics.

## Dependencies And Integration Points
It is the direct caller of many handlers in `traps_64.c`, entry assembly, TSB miss code, interrupt handling, syscall paths, uprobe/kprobe code, and register-window macros. It also depends on linker placement and patch sections collected by `vmlinux.lds.S`.

## Risks And Edge Cases
Vector width and instruction layout are hardware contracts. TL1 paths cannot rely on normal trap-entry state. Patching cache-error vectors must occur after CPU type detection and before such traps are enabled. Uprobe/kprobe trap numbers must match userspace/kernel breakpoint encodings.

## Test Signals
Signals include SPARC64 boot, user and kernel traps, all syscall ABIs, TLB miss/fault behavior, interrupt delivery, nested TL1 trap diagnostics, Cheetah error-vector patching, user-trap delivery, and uprobe traps at `0x173`/`0x174`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ttable_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/una_asm_32.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/una_asm_32.S

## Purpose
Provides SPARC32 byte-wise integer load/store helpers used by C unaligned-access trap handling when the kernel must emulate unaligned halfword, word, or doubleword memory accesses.

## Important APIs, Types, And Functions
Exports `__do_int_store` and `do_int_load`; local `retl_efault` returns `-EFAULT`. The helper contract is shared with `unaligned_32.c`.

## Control Flow
`__do_int_store` reads one or two source words, decomposes them into bytes, and stores 2, 4, or 8 bytes to the destination. `do_int_load` reads bytes from the unaligned source and assembles 2, 4, or 8 byte values into the destination register storage, sign-extending halfword loads when requested. Each faultable byte access has an exception-table entry that redirects to `retl_efault`.

## State And Persistence
No persistent state is maintained. The only mutation is the requested memory store or destination-register memory write, plus exception-table metadata emitted into `__ex_table`.

## Dependencies And Integration Points
Called from `kernel_unaligned_trap` in `unaligned_32.c`; relies on the generic exception-table fixup mechanism and the SPARC register calling convention.

## Risks And Edge Cases
Byte order and sign extension must match SPARC load/store semantics. Partial stores can occur before a later byte faults, so callers must treat `-EFAULT` as a trap-fixup condition. The C caller must only pass supported sizes.

## Test Signals
Signals include kernel unaligned load/store tests for 2-, 4-, and 8-byte accesses, injected faulting addresses that exercise `__ex_table`, and comparison against naturally aligned SPARC load/store results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/una_asm_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/una_asm_64.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/una_asm_64.S

## Purpose
Provides SPARC64 ASI-aware byte-wise integer load/store helpers for kernel unaligned-access emulation.

## Important APIs, Types, And Functions
Exports `__do_int_store` and `do_int_load`. Both save and restore `%asi`, accept an ASI selected by `unaligned_64.c`, and use `__retl_efault` exception fixups for failing byte accesses.

## Control Flow
`__do_int_store` switches to the requested ASI, splits a 64-bit source value into bytes, and stores 2, 4, or 8 bytes. `do_int_load` switches ASI, loads bytes with `lduba`, assembles 2-, 4-, 8-, or 16-byte logical results, applies signed extension for halfword/word loads, and writes destination register slots. Exception-table entries for every faultable byte load/store return `-EFAULT` after restoring normal control.

## State And Persistence
No durable state is kept. The routine temporarily changes `%asi`, restores it before return, and emits `__ex_table` metadata. Destination memory/register slots are the intended side effects.

## Dependencies And Integration Points
Called from `unaligned_64.c` for kernel integer unaligned emulation and no-fault load handling. It depends on ASI definitions, SPARC64 register ABI, and exception-table code.

## Risks And Edge Cases
Incorrect ASI restore would corrupt later kernel accesses. Little-endian alternate ASIs are normalized by the C caller, so helper byte order assumptions must stay aligned with that caller. The 16-byte case represents ldd/std register-pair semantics and must match the caller’s destination layout.

## Test Signals
Signals include SPARC64 kernel unaligned accesses across primary/secondary/no-fault/little-endian ASIs, faulting byte loads/stores that return `-EFAULT`, and regression checks for `%asi` preservation after emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/una_asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/unaligned_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/unaligned_32.c

## Purpose
Implements SPARC32 C-side handling for memory-address-not-aligned traps, emulating supported kernel integer accesses and signaling user unaligned accesses.

## Important APIs, Types, And Functions
Defines `enum direction`, instruction decoders `decode_direction`, `decode_access_size`, `decode_signedness`, register helpers `fetch_reg`, `safe_fetch_reg`, `fetch_reg_addr`, address helpers `compute_effective_address` and `safe_compute_effective_address`, `kernel_unaligned_trap`, and `user_unaligned_trap`. It calls assembly helpers `do_int_load` and `__do_int_store`.

## Control Flow
Kernel traps decode the instruction, reject floating-point and atomic/swap accesses, compute the effective address after flushing register windows if needed, record a perf alignment fault, and emulate integer load or store. If byte-wise emulation faults, `kernel_mna_trap_fault` searches exception tables and either redirects to a fixup or oopses. User traps compute a safe best-effort fault address and send `SIGBUS` with `BUS_ADRALN`.

## State And Persistence
The handler mutates `pt_regs` PC/NPC to advance successful emulation or to branch to exception-table fixups. It can read/write stack-resident register windows and touched memory but keeps no global state.

## Dependencies And Integration Points
Integrated with SPARC32 trap-table `mna_handler`, register-window mechanics, perf software counters, exception tables, uaccess, and `una_asm_32.S`.

## Risks And Edge Cases
Unsafe register-window access is acceptable only for kernel-mode emulation; user-facing effective-address calculation uses guarded loads. Unsupported floating-point or atomic unaligned kernel accesses panic. Partial byte-wise stores may occur before a fault, so correctness depends on exception semantics matching existing kernel assumptions.

## Test Signals
Signals include kernel tests or fault injection for unaligned integer loads/stores, userspace unaligned access returning `SIGBUS`, exception-table fixups for faulting kernel uaccess, and perf alignment-fault counter increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/unaligned_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/unaligned_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/unaligned_64.c

## Purpose
Implements SPARC64 unaligned access handling and selected instruction emulation, including kernel integer unaligned loads/stores, POPC emulation, no-fault loads, and user floating-point quad/double unaligned handling.

## Important APIs, Types, And Functions
Key routines include `decode_direction`, `decode_access_size`, `decode_asi`, `fetch_reg`, `fetch_reg_addr`, exported `compute_effective_address`, `kernel_unaligned_trap`, `handle_popc`, `handle_ldf_stq`, `handle_ld_nf`, `handle_lddfmna`, and `handle_stdfmna`. It calls assembly helpers `do_int_load` and `__do_int_store`, and trap handlers in `traps_64.c`.

## Control Flow
Kernel MNA traps store current unaligned context in `thread_info`, decode ASI and direction, immediately route `ASI_AIUS` uaccess faults to exception-table fixup, reject unsupported kernel FP/atomic traps, and otherwise emulate integer access. Successful emulation advances TPC/TNPC; faults search exception tables and may set the ASI in `tstate` for the fixup path. Illegal-instruction and no-fault paths use `handle_popc`, `handle_ldf_stq`, and `handle_ld_nf` to emulate missing or special SPARC64 instructions. User FP MNA handlers load/store FPU state with ASI validation and endian conversion, or delegate to data-access exception handlers.

## State And Persistence
State changes include `pt_regs` PC updates, destination integer registers or user stack register windows, FPU saved state, `thread_info` `kern_una_regs`/`kern_una_insn`, `xfsr`, `fpsaved`, and `gsr`. No durable storage is created beyond perf events and ratelimited logs.

## Dependencies And Integration Points
Used by `traps_64.c` unaligned, illegal-instruction, and no-fault handlers. It depends on FPU state helpers, register-window flushing, alternate ASI definitions, exception tables, perf counters, ratelimit logging, Sun4v versus Spitfire data-access handling, and `una_asm_64.S`.

## Risks And Edge Cases
ASI and endian handling are subtle; the code strips little-endian ASI bits for byte emulation and then swaps values in C. Register-window flushing differs for kernel and user contexts. No-fault loads must return zero without signaling. Floating-point quad register alignment and FPRS flags must be exact or user FP state is corrupted.

## Test Signals
Signals include unaligned integer kernel access, faulting `get_user`/`put_user` exception-table paths, user `SIGBUS` for normal MNA, POPC emulation, LDQ/STQ and no-fault load emulation, FP unaligned load/store behavior, perf alignment/emulation counters, and 32-bit compat register-window cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/unaligned_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/uprobes.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/uprobes.c

## Purpose
Implements SPARC architecture support for Linux uprobes, including breakpoint address selection, out-of-line instruction copying, single-step preparation and completion, trap notification handling, and uretprobe return-address hijacking.

## Important APIs, Types, And Functions
Important entry points include `uprobe_get_swbp_addr`, `arch_uprobe_copy_ixol`, `arch_uprobe_analyze_insn`, `arch_uprobe_skip_sstep`, `arch_uprobe_pre_xol`, `arch_uprobe_post_xol`, `uprobe_trap`, `arch_uprobe_exception_notify`, `arch_uprobe_abort_xol`, `arch_uprobe_xol_was_trapped`, and `arch_uretprobe_hijack_return_addr`. Helpers include `copy_to_page`, `relbranch_fixup`, and `retpc_fixup`.

## Control Flow
Probe setup copies the original instruction into the XOL slot and appends the single-step trap, clearing branch annul bits when necessary. Pre-XOL saves TPC/TNPC and redirects execution to the XOL slot. Post-XOL reconstructs the real next PC for relative branches and fixes return-PC writes for `call` and `jmpl`. Trap `0x173` triggers breakpoint notification, trap `0x174` triggers single-step notification, and only user-mode traps are accepted.

## State And Persistence
Per-task uprobe state stores saved PCs and XOL addresses. The XOL page is modified with the copied instruction and step trap. `pt_regs` TPC/TNPC and return-register slots are updated during pre/post handling.

## Dependencies And Integration Points
Connected to `ttable_64.S` uprobe trap vectors, Linux generic uprobe core, die notifier chain, highmem page mapping, cache-flush expectations for executable copied instructions, and SPARC register-window handling via `flushw_all` for hard `jmpl` cases.

## Risks And Edge Cases
Branch annul handling is essential so the single-step trap is reached. `retpc_fixup` must write either `%o7`/integer registers or stack-resident locals with correct 32/64-bit stack layout. Kernel-mode probes are rejected because uprobe breakpoints should never exist in kernel code.

## Test Signals
Signals include uprobes on NOP, call, branch, and jmpl instructions; uretprobe return hijacking; 32-bit and 64-bit user stack layouts; breakpoint and single-step die notifications; and aborted XOL execution resetting the instruction pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/uprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/urtt_fill.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/urtt_fill.S

## Purpose
Provides a SPARC64 return-from-trap fill fixup path for user register-window fill faults, restoring enough kernel context to call C fault, unaligned, or data-access handlers safely.

## Important APIs, Types, And Functions
Exports `user_rtt_fill_fixup_common`. It calls `do_sparc64_fault`, `sun4v_do_mna`, `mem_address_unaligned`, `sun4v_data_access_exception`, and `spitfire_data_access_exception` depending on saved fault classification and platform.

## Control Flow
The routine adjusts CWP and WSTATE, restores kernel primary context, saves fault code/address from `%g4/%g5`, drops trap level, restores global level and PSTATE, reloads current/per-CPU state, and then dispatches. A zero saved subtype calls the normal page fault handler; subtype `2` is memory-not-aligned; other values are data-access exceptions. All paths return through `rtrap`.

## State And Persistence
It mutates privileged registers `%cwp`, `%wstate`, `%tl`, `%pstate`, MMU primary context, and per-thread fault fields `TI_FAULT_CODE` and `TI_FAULT_ADDR`. No independent persistent storage exists.

## Dependencies And Integration Points
Integrated with register-window return paths, Sun4v patch sections, ADI/MCD PSTATE handling, `trap_block`, thread-info offsets, and C handlers in `traps_64.c`.

## Risks And Edge Cases
The code runs while unwinding a failed trap return, so register conventions and PSTATE restoration are critical. Sun4v and M7 patches alter MMU/PSTATE behavior. Misclassifying `%l3` would call the wrong C handler for MNA versus DAX.

## Test Signals
Signals include user register-window fill faults during trap return, user stack page faults, unaligned user stack windows, Sun4v versus Spitfire data faults, and ADI-enabled M7 return paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/urtt_fill.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/utrap.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/utrap.S

## Purpose
Implements SPARC64 user-trap dispatch for trap-table `TRAP_UTRAP` entries, invoking per-thread user trap handlers when registered or falling back to `bad_trap`.

## Important APIs, Types, And Functions
Exports `utrap_trap`. It reads `TI_UTRAPS`, indexes the handler table by the trap number in `%g3`, and calls `bad_trap` through `etrap`/`rtrap` when no table is present.

## Control Flow
On entry, the code loads current thread info and checks for a user-trap table. Without one it builds a normal trap frame and reports a bad trap. With a table, it loads the target handler, creates a new register window, updates `tstate` CWP, preserves original TPC/TNPC in locals, writes the handler into `%tnpc`, and executes `done` so user execution resumes at the handler path.

## State And Persistence
Persistent state is the per-thread `TI_UTRAPS` pointer maintained elsewhere. This routine mutates trap registers, CWP, and the user-visible control-flow target for immediate delivery.

## Dependencies And Integration Points
Used by `ttable_64.S` user-trap vectors and depends on thread-info layout, `etrap`, `rtrap`, `bad_trap`, and SPARC V9 trap-return semantics.

## Risks And Edge Cases
Handler table indexing assumes `%g3` is a valid user-trap index from the macro caller. The `done` path is sensitive to exact TPC/TNPC semantics. Missing table fallback must preserve the trap level for `bad_trap`.

## Test Signals
Signals include registered user trap handlers receiving software trap control, unregistered user traps producing bad-trap SIGILL behavior, and 32/64-bit user trap compatibility cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/utrap.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/vio.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/vio.c

## Purpose
Implements the SPARC64 VIO bus and machine-description discovery layer for LDOM virtual I/O devices. It registers the `vio` bus, creates `vio_dev` objects from MDESC channel-device nodes, handles hotplug matching, and tracks dynamic add/remove notifications.

## Important APIs, Types, And Functions
Important functions include `vio_match_device`, `vio_hotplug`, `vio_bus_match`, `vio_device_probe`, `vio_device_remove`, `__vio_register_driver`, `vio_unregister_driver`, `vio_vdev_node`, `vio_set_intr`, `vio_create_one`, `vio_add`, `vio_remove`, `vio_add_ds`, and initcall `vio_init`. Global state includes `vio_bus_type`, `root_vdev`, `cdev_node`, and `cdev_cfg_handle`.

## Control Flow
`vio_init` registers the bus, locates and validates the MDESC `channel-devices` root and matching OBP node, creates a root VIO device, then registers MDESC notifiers for virtual-device and domain-service ports. Device creation reads type, compatible data, IDs, cfg handles, channel IDs, and interrupt numbers, sets a Linux device name, attaches sysfs attributes, and registers the device. Driver probe matching compares `type` and OF-style compatible lists, builds virtual IRQs unless suppressed, and calls the driver probe.

## State And Persistence
The bus and devices persist in the Linux device model. Each `vio_dev` stores MD node identity, channel IDs, tx/rx INOs and IRQs, cfg handle, OF node pointer, port/dev IDs, type, compatible strings, and node info for later MD updates. Global `cdev_cfg_handle` is used for interrupt control.

## Dependencies And Integration Points
Depends on Linux driver core, sysfs attributes, MDESC APIs, OF node lookup, Sun4v virtual interrupt hypercalls, and VIO driver structures from `asm/vio.h`. Downstream virtual network, disk, console, and domain-service drivers bind through this bus.

## Risks And Edge Cases
MD node numbers can change, so removal must re-resolve by saved node identity. IRQ allocation has no corresponding deallocation support in remove. Overlong MD strings are rejected. Domain-service ports are filtered to avoid OBP-reserved ports. `vio_init` returns `0` even when no MDESC root exists, so absence of VIO hardware is non-fatal.

## Test Signals
Signals include boot on Sun4v/LDOM systems, sysfs `type`, `modalias`, `devspec`, and `obppath`, module autoload aliases, hot add/remove MDESC events, successful vnet/vdisk driver probe, and `vio_set_intr` hypercall behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/vio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/viohs.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/viohs.c

## Purpose
Implements the VIO LDC handshake helper layer used by SPARC LDOM virtual devices to negotiate protocol version, attributes, descriptor rings, ready-to-exchange state, SIDs, and LDC port lifecycle.

## Important APIs, Types, And Functions
Exported APIs include `vio_ldc_send`, `vio_link_state_change`, `vio_control_pkt_engine`, `vio_conn_reset`, `vio_validate_sid`, `vio_send_sid`, `vio_ldc_alloc`, `vio_ldc_free`, `vio_port_up`, and `vio_driver_init`. Important internal functions include `send_version`, `start_handshake`, `handshake_failure`, `send_dreg`, `send_rdx`, `process_ver`, `process_attr`, `process_dreg`, `process_dunreg`, and `process_rdx`.

## Control Flow
When LDC reports link up, the helper initializes required TX/RX descriptor-ring state based on device class and sends the first version packet. Incoming control packets pass through `vio_control_pkt_engine`, which dispatches by `stype_env`: version negotiation ACKs/NACKs select a supported version; attribute handling calls driver ops; descriptor ring registration records peer cookies or acknowledges local TX rings; RDX exchange marks the handshake complete and calls `handshake_complete`. Reset tears down RX ring state, clears version and handshake state, and disconnects LDC.

## State And Persistence
State lives in `struct vio_driver_state`: `hs_state`, `dr_state`, negotiated `ver`, local/peer SIDs, LDC channel pointer, descriptor ring states, descriptor buffer allocation, timer, lock, driver ops, device class, and version table. Descriptor buffers are allocated on RX ring registration and freed on failure, unregister, reset, or LDC free.

## Dependencies And Integration Points
Depends on `asm/ldc.h` LDC channel operations, `asm/vio.h` packet layouts and constants, Linux timers/spinlocks/slab, and class-specific VIO drivers that implement attribute and completion callbacks.

## Risks And Edge Cases
Handshake state ordering is strict; out-of-order control packets force reset. `vio_ldc_send` spins with microsecond delays on `-EAGAIN`, so long stalls are bounded but possible. SID validation includes a Solaris disk-server workaround that intentionally treats disk clients differently. Descriptor-ring cookie counts must fit the stack union.

## Test Signals
Signals include LDC link-up/reset events, version ACK/NACK fallback, vnet/vdisk descriptor ring registration, RDX completion callbacks, invalid SID packet rejection, connection retry timer behavior, and cleanup of `desc_buf` across resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/viohs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/visemul.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/visemul.c

## Purpose
Emulates selected VIS instructions not implemented in hardware on Niagara-class SPARC64 CPUs, allowing user programs to execute supported VIS operations through the illegal-instruction trap path.

## Important APIs, Types, And Functions
The public entry is `vis_emul`. Helpers include `maybe_flush_windows`, `fetch_reg`, `store_reg`, FPU register accessors `fpd_regval`, `fpd_regaddr`, `fps_regval`, `fps_regaddr`, and operation groups `edge`, `array`, `bmask`, `bshuffle`, `pdist`, `pformat`, `pmul`, and `pcmp`. OPF constants define pack, expand, merge, multiply, compare, edge, array, byte-mask, and shuffle instructions.

## Control Flow
`vis_emul` verifies it is not in privileged state, records a perf emulation fault, refetches the instruction from user PC, saves and clears live FPU state, decodes the OPF field, dispatches to the matching emulator, and advances TPC/TNPC. Integer-register VIS operations flush user register windows and read/write `pt_regs` or stack-resident windows. FP-register operations read/write saved `fpustate` and `thread_info` GSR fields.

## State And Persistence
The code mutates user integer registers, user stack register windows, saved FPU register state, `thread_info()->gsr[0]`, and condition-code bits in `regs->tstate` for edge instructions. It has no global persistent state beyond static lookup tables.

## Dependencies And Integration Points
Called from `do_illegal_instruction` in `traps_64.c` for hypervisor systems when the opcode matches VIS. It depends on FPU save helpers, SPARC register-window layout, user memory accessors, perf software events, and 32-bit compat register handling.

## Risks And Edge Cases
The emulation only supports listed OPFs and returns `-EINVAL` for the rest. Register-window stores to user stack can fault but are not deeply recovered here. VIS arithmetic has many saturating, rounding, endian, and packed-lane semantics that must match hardware. Privileged execution is treated as a bug.

## Test Signals
Signals include user VIS instruction suites on hardware lacking the operations, illegal-instruction fallback for unsupported OPFs, compare/pack/multiply/edge arithmetic conformance against hardware, GSR mask behavior for `bmask`/`bshuffle`, and 32-bit process coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/visemul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/vmlinux.lds.S

## Purpose
Defines the SPARC kernel linker script for both 32-bit and 64-bit builds, controlling image format, entry point, fixed virtual/physical start addresses, section layout, patch-section collection, percpu layout, BSS, debug metadata, and discarded sections.

## Important APIs, Types, And Functions
Key linker symbols and sections include `_text`, `_etext`, `_sdata`, `_edata`, `__init_begin`, `__init_text_end`, `__init_end`, `_end`, `swapper_pg_dir`, `jiffies`, `.fixup`, exception table, TSB patch sections, Sun4v/LEON/POPC/PAUSE/M7/get_tick/pud/fast-window patch sections, `PERCPU_SECTION`, `BSS_SECTION`, `STABS_DEBUG`, `DWARF_DEBUG`, `MODINFO`, `ELF_DETAILS`, and `DISCARDS`.

## Control Flow
The linker, not runtime code, evaluates this file. It selects ELF32 or ELF64 output based on configuration, places head text and normal text at architecture-specific addresses, aligns read-only/data/init/percpu areas, emits start/end symbols for runtime patch iterators, and asserts that early SPARC64 assembler has not moved `swapper_tsb` away from its expected address.

## State And Persistence
The script determines persistent kernel image layout and the runtime symbol addresses consumed by boot, trap, patching, exception-table, init, module, percpu, and debug code.

## Dependencies And Integration Points
Depends on generic Linux linker-script macros, SPARC page/thread constants, early head assembly, patch emitters throughout SPARC assembly files, exception tables from faultable assembly, and runtime patching code that walks the emitted start/end symbols.

## Risks And Edge Cases
Small alignment or address changes can break early boot, MMU setup, trap-table location, or patch iteration. The SPARC64 `swapper_tsb` assertion protects a hard-coded early assembler dependency. Missing patch sections would leave platform-specific instructions unpatched.

## Test Signals
Signals include successful SPARC32/SPARC64 link, `vmlinux` symbol inspection, early boot through MMU setup, runtime patch application, exception-table fixups, module metadata presence, and failure of the explicit `swapper_tsb` assertion if early text grows too large.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/windows.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/windows.c

## Purpose
Provides C-level SPARC register-window management helpers for flushing user windows from CPU state and synchronizing per-thread saved window buffers back to the user stack.

## Important APIs, Types, And Functions
Exports `flush_user_windows`, `synchronize_user_stack`, and `try_to_clear_window_buffer`. Internal `shift_window_buffer` compacts saved-window arrays after a successful copy.

## Control Flow
`flush_user_windows` repeatedly executes `save` until `TI_UWINMASK` is clear, then restores back to the original window. `synchronize_user_stack` flushes hardware windows, walks saved windows in reverse, copies each to its recorded user stack pointer, and removes successful entries from the thread buffer. `try_to_clear_window_buffer` flushes windows, validates saved stack alignment, copies all saved windows, and sends `SIGILL` if any copy fails.

## State And Persistence
State is in `thread_info`: `uwinmask`, `w_saved`, `rwbuf_stkptrs`, and `reg_window`. Successful synchronization decreases or clears `w_saved` and mutates user stack memory.

## Dependencies And Integration Points
Used by signal setup/return, register-window trap fixups, ptrace-like user state synchronization, and SPARC low-level window assembly. Depends on `copy_to_user`, current thread info, and register-window layout.

## Risks And Edge Cases
User stack pointers may be unaligned or unmapped. `synchronize_user_stack` tolerates failed copies and leaves entries buffered; `try_to_clear_window_buffer` treats failure as fatal. The inline assembly assumes specific thread-info offsets and `%g6` current-thread convention.

## Test Signals
Signals include signal delivery and sigreturn with deep register windows, invalid user stack window faults, forced flush-window traps, 32-bit register-window layout checks, and `SIGILL` delivery from unrecoverable saved-window copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/windows.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/winfixup.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/winfixup.S

## Purpose
Handles SPARC64 register-window spill/fill fault fixups when user stack pointers are invalid or memory faults occur during low-level window operations.

## Important APIs, Types, And Functions
Important labels include `fill_fixup`, `spill_fixup`, `spill_fixup_mna`, `spill_fixup_dax`, `winfix_mna`, `fill_fixup_mna`, `winfix_dax`, and `fill_fixup_dax`. It calls `do_sparc64_fault`, `sun4v_do_mna`, `mem_address_unaligned`, `sun4v_data_access_exception`, and `spitfire_data_access_exception`.

## Control Flow
Fill fixups restore the faulting CWP, record fault code/address in thread info, build a normal trap frame via `etrap`, and call the page-fault handler. Spill fixups save the current window into the per-thread register-window buffer in 64-bit or 32-bit layout, increment `TI_WSAVED`, mark the window saved, and either retry privileged spills or enter the fault handler for user spills. MNA and DAX trampoline labels rewrite `%tnpc` so `done` lands at the correct fill fixup variant.

## State And Persistence
Mutates `thread_info` saved-window buffers, saved stack-pointer array, `TI_WSAVED`, `TI_FAULT_CODE`, and `TI_FAULT_ADDR`, plus privileged trap registers CWP/TNPC. Buffered windows persist until C code later syncs or clears them.

## Dependencies And Integration Points
Integrated with SPARC64 register-window spill/fill macros, `urtt_fill.S`, `traps_64.c`, page-fault handling, Sun4v platform detection, and thread-info offsets validated in `trap_init`.

## Risks And Edge Cases
The code cannot freely use trap globals because some contain fault metadata. Stack pointer low-bit and `_TIF_32BIT` checks choose 32-bit versus 64-bit save format. A wrong `saved`/`retry` decision can corrupt the window state or loop in trap context.

## Test Signals
Signals include faults while spilling/filling user windows, unaligned window stack pointers, Sun4v versus Spitfire MNA/DAX dispatch, 32-bit compat window saves, and later successful `synchronize_user_stack` of buffered windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/winfixup.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/wof.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/wof.S

## Purpose
Implements the SPARC32 register window overflow trap handler, spilling windows to kernel or user stack and buffering user windows when the user stack is invalid.

## Important APIs, Types, And Functions
Exports `spill_window_entry`, patch labels `spnwin_patch1`, `spnwin_patch2`, `spnwin_patch3`, 7-window patch templates, and `spwin_srmmu_stackchk`. It uses macros such as `LOAD_CURRENT`, `STORE_WINDOW`, `STORE_PT_ALL`, `SAVE_BOLIXED_USER_STACK`, and SRMMU/LEON MMU access patch macros.

## Control Flow
The handler computes the new WIM, determines whether the trap came from user or kernel mode, spills kernel-only windows directly, and handles active user windows by updating `TI_UWINMASK`. For user stack spills, it validates stack alignment and user address range, uses SRMMU no-fault probing around the stores, and either finishes the trap return or buffers the window and calls `window_overflow_fault` through a constructed `pt_regs` frame.

## State And Persistence
Mutates `%wim`, `TI_UWINMASK`, `TI_W_SAVED`, saved register-window buffers, saved stack pointers, and user stack memory. Boot-time patch labels persist to adapt masks and shifts for 7-window versus 8-window CPUs.

## Dependencies And Integration Points
Used by SPARC32 trap table `WINDOW_SPILL`, paired with `wuf.S` and `windows.c`, and depends on SRMMU/LEON MMU no-fault controls, thread-info layout, and C fault routine `window_overflow_fault`.

## Risks And Edge Cases
Register-window handlers run with traps disabled and cannot provoke nested faults casually. User stack addresses in kernel space must be rejected because no-fault probing could otherwise succeed incorrectly. Boot patching for window count must update all mask operations consistently.

## Test Signals
Signals include deep call stacks causing overflow from user and kernel, bogus or unaligned user stack pointers, LEON/Sun SRMMU variants, 7-window CPU boot patching, and recovery via `window_overflow_fault`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/wof.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/wuf.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/wuf.S

## Purpose
Implements the SPARC32 register window underflow trap handler, filling invalid windows from kernel or user stack and handling invalid user stacks by entering C fault recovery.

## Important APIs, Types, And Functions
Exports `fill_window_entry`, patch labels `fnwin_patch1`, `fnwin_patch2`, 7-window patch templates, and `srmmu_fwin_stackchk`. It uses `LOAD_WINDOW`, `STORE_PT_GLOBALS`, `STORE_PT_YREG`, `STORE_PT_INS`, `STORE_PT_PRIV`, `LOAD_CURRENT`, and SRMMU/LEON no-fault macros.

## Control Flow
The handler computes the next WIM, restores from trap window to the target invalid window, and branches by user/kernel origin. Kernel underflow simply loads from `%sp` and rotates back. User underflow validates stack alignment and address, temporarily enables MMU no-fault mode, attempts to load the window, checks fault status, and either finishes or constructs a `pt_regs` frame and calls `window_underflow_fault`.

## State And Persistence
Mutates `%wim`, register-window contents, `TI_UWINMASK`, `TI_W_SAVED`, and the trap frame built on the kernel stack for fault recovery. Patch labels persist for CPU window-count adaptation.

## Dependencies And Integration Points
Used by the SPARC32 trap table `WINDOW_FILL`, paired with `wof.S`, `windows.c`, SRMMU/LEON MMU accessors, and the C recovery path `window_underflow_fault`.

## Risks And Edge Cases
The invalid window has unusual register ownership; comments explicitly restrict which registers may be used before the load completes. User stack probing must restore MMU no-fault state and recover the expected window position on failure. Kernel over-restore is trusted, so kernel misuse can be fatal.

## Test Signals
Signals include deep returns causing underflow, user stack read faults, unaligned stack pointers, 7-window patch behavior, LEON/Sun MMU variants, and successful C recovery from `window_underflow_fault`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/wuf.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/GENbzero.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/GENbzero.S

## Purpose
Provides generic SPARC64 implementations of `memset`, `bzero`, and `clear_user`, plus a runtime patch helper that redirects generic symbol names to these optimized routines.

## Important APIs, Types, And Functions
Exports `GENmemset`, `GENbzero`, `GENclear_user`, and `generic_patch_bzero`. Internal labels include `GENbzero_from_clear_user`, `GENbzero_pre_loop`, `GENbzero_loop`, `GENbzero_medium`, `GENbzero_tiny`, `GENbzero_done`, and `GENbzero_return`. The `EX_ST` macro emits faultable stores and exception-table entries to `__retl_o1_asi`.

## Control Flow
`GENmemset` expands the byte pattern across a 64-bit word and falls into the zeroing core. `GENbzero` handles zero length, saves `%asi`, selects primary ASI, aligns to 8 and then 64 bytes, uses unrolled 64-byte `stxa` loops for large ranges, handles medium 8-byte chunks and tiny byte tails, restores `%asi`, and returns the original buffer. `GENclear_user` uses `ASI_AIUS` when called from user-clear context. `generic_patch_bzero` writes branch-always instructions at `memset`, `__bzero`, and `__clear_user`, followed by NOPs and instruction flushes.

## State And Persistence
The routines temporarily change `%asi` and restore it. Faultable user clears persist exception-table metadata. `generic_patch_bzero` permanently patches kernel text for the running image.

## Dependencies And Integration Points
Used by SPARC64 memory/string routines and clear-user paths. Depends on ASI constants, exception-table fixup `__retl_o1_asi`, writable/patchable early kernel text, and instruction-cache flush semantics.

## Risks And Edge Cases
Fault handling must return the expected uncleared byte count conventions through the shared fixup path. `%asi` preservation is mandatory. Runtime patch offsets must fit SPARC branch encoding and be flushed before execution. Partial stores before a user fault are normal for clear-user semantics but must be accounted for by callers.

## Test Signals
Signals include memset/bzero correctness across zero, tiny, unaligned, medium, and large buffers; clear_user fault injection; `%asi` preservation checks; and verification that patched `memset`, `__bzero`, and `__clear_user` branch to the generic routines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/GENbzero.S -->
