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
