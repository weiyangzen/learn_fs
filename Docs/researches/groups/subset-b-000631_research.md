# subset-b-000631 research

Grouped research for ARC Linux kernel support files under `sources/distributed-fs/ceph-client/arch/arc`. Each section is bounded for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/stacktrace.c

Purpose: provides ARC stack trace APIs as thin wrappers around the DWARF2 unwinder. It feeds panic/oops stack printing, scheduler `show_stack()`, wait-channel discovery, and `CONFIG_STACKTRACE` capture.

Important APIs/functions: `arc_unwind_core()` is the iterator used by all consumers. `seed_unwind_frame_info()` seeds `struct unwind_frame_info` from explicit `pt_regs`, current live registers, or a sleeping task saved in `__switch_to`. Public entry points are `show_stacktrace()`, `show_stack()`, `__get_wchan()`, `save_stack_trace_tsk()`, and `save_stack_trace()`.

Control flow: the seed path selects synchronous current-task unwind, asynchronous exception unwind, or sleeping-task unwind. `arc_unwind_core()` repeatedly reads `UNW_PC()`, validates that it is kernel text, invokes a callback, calls `arc_unwind()`, then advances return state from `blink`. Callback variants print symbols, collect stack entries, skip scheduler frames, or stop on the first non-scheduler frame.

State and persistence: no durable state is owned here. It reads task thread saved FP/SP/BLINK, live ARC registers, and caller-provided stack trace buffers. The loop guard stops after 128 frames to avoid unwinder loops.

Dependencies and integration: depends on `CONFIG_ARC_DW2_UNWIND`, `asm/unwind.h`, kallsyms, scheduler helpers, and ARC `switch_to` layout macros. Exported symbols are consumed by kernel diagnostics and generic stacktrace users.

Risks: sleeping-task unwinding assumes the task is not running and that `__switch_to` saved-register layout matches the compensating SP adjustment. Without DWARF unwind support, only a warning is emitted and traces are empty. Bad unwind metadata can truncate or loop until the guard trips.

Test signals: useful checks are panic/oops stack output, `/proc/<pid>/stack`, `__get_wchan()` on sleeping tasks, `CONFIG_STACKTRACE` users, and builds with and without `CONFIG_ARC_DW2_UNWIND`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/sys.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/sys.c

Purpose: defines the ARC syscall dispatch table.

Important APIs/functions: `sys_call_table[NR_syscalls]` is initialized to `sys_ni_syscall` for every slot, then populated by including `asm/syscall_table_32.h`. Local defines map `sys_clone`, `sys_clone3`, and `sys_mmap2` to ARC wrapper or pgoff implementations.

Control flow: there is no runtime control flow in this file beyond table lookup performed by the syscall entry path elsewhere. The preprocessor expands syscall table macros into designated initializers.

State and persistence: the syscall table is static kernel data. It persists for the kernel lifetime and controls every userspace syscall dispatch on this architecture.

Dependencies and integration: depends on Linux syscall headers, ARC syscall wrappers, `NR_syscalls`, and generated or maintained `asm/syscall_table_32.h`. Integrates directly with low-level ARC syscall entry code.

Risks: wrong macro aliases route syscalls to the wrong ABI wrapper. Missing table entries fall back to `sys_ni_syscall`, which is safe but visible as unimplemented syscall behavior. ABI drift between syscall numbers and `asm/syscall_table_32.h` is the main compatibility risk.

Test signals: syscall ABI selftests, clone/clone3 process creation tests, `mmap2` tests, and audit/strace checks that expected syscall numbers dispatch correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/traps.c

Purpose: handles ARC non-MMU exceptions and trap families that do not belong to the page fault fast path.

Important APIs/functions: `die()` emits kernel diagnostics and halts with `flag 1`. `unhandled_exception()` converts user faults to signals and kernel faults to exception-table fixups or fatal oops. Macro-generated handlers include privilege, extension, instruction, memory, breakpoint, misaligned, and trap5 errors. Specialized handlers are `do_misaligned_access()`, `do_machine_check_fault()`, `do_non_swi_trap()`, `do_insterror_or_kprobe()`, and `abort()`.

Control flow: generic exceptions call `unhandled_exception()`. User mode sets `current->thread.fault_address` and calls `force_sig_fault()`. Kernel mode first tries `fixup_exception()` for `copy_to_user()`/`copy_from_user()` style fixups, otherwise calls `die()`. Misaligned access tries software emulation before falling back to SIGBUS. Trap parameters route to GDB breakpoints, kprobes, kgdb, GCC trap5, or no-op default.

State and persistence: updates per-task `thread.fault_address`; otherwise no persistent state. Fatal kernel path terminates execution.

Dependencies and integration: integrates with signal delivery, kprobes/kgdb notifier paths, exception-table fixups, unaligned emulation in `unaligned.c`, and diagnostics in `troubleshoot.c`.

Risks: incorrect classification can either kill user tasks unnecessarily or miss fatal kernel faults. Kprobe and kgdb trap parameter handling must match low-level trap encoding. The fatal halt path is architecture-specific and intentionally unrecoverable.

Test signals: userspace illegal instruction and misaligned access tests, kprobe/kgdb breakpoint tests, uaccess exception-table tests, and kernel oops diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/troubleshoot.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/troubleshoot.c

Purpose: formats ARC register, exception, VMA, executable path, and stack-trace diagnostics for oops and fault reporting.

Important APIs/functions: `show_regs()` is the generic register dump entry point. `show_kernel_fault_diag()` records the fault address, prints the fault text, dumps registers, and prints a stack trace for kernel-mode faults. Helpers print scratch and callee-saved registers, executable path, faulting VMA, and verbose ECR decoding.

Control flow: `show_regs()` temporarily enables preemption because some diagnostic helpers may sleep, prints task path and generic debug info, decodes ECR, optionally looks up the user VMA for `regs->ret`, then prints ECR/EFA/ERET/status bits and registers. It restores preemption-disabled state before returning.

State and persistence: writes `current->thread.fault_address` in `show_kernel_fault_diag()`. It reads `current->active_mm`, current task executable file, VMA metadata, `callee_reg`, and `pt_regs`. There is no durable owned state.

Dependencies and integration: depends on proc/file/mm helpers, `asm/arcregs.h`, scheduler debug, ARC status/ECR bit definitions, and `show_stacktrace()` from `stacktrace.c`.

Risks: diagnostics run in fragile exception contexts; sleeping helpers are guarded by explicit preemption enable/disable but still rely on caller context being acceptable. VMA lookup uses the current active mm and may not reflect the faulting task in unusual contexts. Formatting must match ARC register layout.

Test signals: forced user page faults, kernel oopses, instruction fetch faults, misaligned/protection faults, and verifying output includes ECR/EFA/ERET/status/registers/path/VMA where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/troubleshoot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/unaligned.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/unaligned.c

Purpose: emulates selected user-mode unaligned ARC load/store instructions when `CONFIG_ARC_EMUL_UNALIGNED` is enabled.

Important APIs/functions: `misaligned_fixup()` is called by trap handling. `fixup_load()` and `fixup_store()` perform register writeback and byte-wise memory access. Inline assembly macros implement exception-table guarded unaligned 8/16/32-bit loads and stores, with endian-specific byte ordering.

Control flow: `misaligned_fixup()` rejects kernel-mode faults and disabled emulation, logs according to sysctl knobs, disassembles the faulting instruction with `disasm_instr()`, rejects unsupported byte/invalid forms, then dispatches to load or store fixup. On success it advances `regs->ret`, handles delay-slot state and zero-overhead-loop wraparound, and emits a perf alignment fault event.

State and persistence: global `unaligned_enabled` and `no_unaligned_warning` are read-mostly sysctl-controlled policy state. Per-fault state lives in `struct disasm_state`, `pt_regs`, and optional `callee_regs`; register and instruction pointer state are modified to make the emulated instruction appear complete.

Dependencies and integration: integrates with trap code, ARC disassembler/register access helpers, exception tables, perf software events, uaccess-style fixups, and endian/ISA configuration.

Risks: instruction decoding must exactly match hardware semantics, especially address writeback, delay slots, sign extension, and loop registers. Store fixup writeback has a suspicious branch where `state->aa == 2` is checked before a nested `state->aa == 3` case, so maintenance should be careful around writeback modes. Emulation hides user bugs and can degrade performance.

Test signals: userspace unaligned halfword/word load/store tests across endian builds, sysctl enable/disable behavior, delay-slot and zero-overhead-loop cases, perf alignment fault counters, and faulting user pages during emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/unaligned.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/unaligned.h -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/unaligned.h

Purpose: declares or stubs the ARC unaligned access emulation entry point.

Important APIs/types/functions: forward-declares `struct pt_regs` and `struct callee_regs`; declares `misaligned_fixup()` when `CONFIG_ARC_EMUL_UNALIGNED` is enabled; otherwise provides an inline implementation returning `1` to indicate the fault was not fixed.

Control flow: callers can unconditionally call `misaligned_fixup()` and branch on a nonzero failure result. The header collapses the disabled configuration to a compile-time no-fixup path.

State and persistence: no state.

Dependencies and integration: included by trap handling and implemented by `unaligned.c`. Its return convention is part of `do_misaligned_access()` behavior.

Risks: any change to return semantics must be coordinated with `traps.c`, where nonzero means deliver normal misaligned error handling. Forward declarations must stay consistent with ARC register structures.

Test signals: build coverage with `CONFIG_ARC_EMUL_UNALIGNED=y` and `n`, plus misaligned access tests that verify the disabled path signals rather than emulates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/unaligned.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/unwind.c -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/unwind.c

Purpose: implements ARC kernel stack unwinding from DWARF2 `.eh_frame` metadata, with a compact generated header table for fast FDE lookup and optional module unwind tables.

Important APIs/types/functions: key types are `struct unwind_table`, `struct unwind_state`, `struct unwind_item`, and CIE/FDE header entries. Public APIs are `arc_unwind_init()`, `unwind_add_table()`, `unwind_remove_table()`, and exported `arc_unwind()`. Helpers parse LEB128, encoded pointers, CIE/FDE relationships, FDE pointer type, and DWARF CFA instructions.

Control flow: boot initializes `root_table` from linker-provided `__start_unwind`/`__end_unwind`, then builds a sorted FDE header with `init_unwind_hdr()`. `arc_unwind()` finds the table covering the current PC, binary-searches the header for an FDE, validates its CIE, parses CIE/FDE CFI up to the target PC, computes CFA, and applies register recovery rules from memory/register/value sources. If DWARF lookup fails and frame pointers are configured, it attempts a frame-pointer fallback.

State and persistence: `root_table` persists for kernel text, while module tables are linked through `root_table.link` and `last_table`. Header storage is allocated with memblock at boot or kmalloc for modules. The active unwind modifies caller-provided `struct unwind_frame_info`.

Dependencies and integration: consumes linker sections emitted by `vmlinux.lds.S`, module memory metadata, stop-machine-era module synchronization assumptions, `__get_user()` for safe stack reads, `sort()`, and ARC unwind register metadata from `asm/unwind.h`. Used by `stacktrace.c`.

Risks: malformed or unsupported CFI panics during header construction or returns unwind errors at runtime. Module removal synchronization is marked `XXX: SMP`, so lifetime assumptions are important. Stack bounds and alignment checks protect memory reads but can truncate traces. Unsupported DWARF opcodes or expression-based CFA rules fail unwinding.

Test signals: oops and `dump_stack()` traces, module load/unload with stack traces through module text/init text, corrupted or absent `.eh_frame` handling, frame-pointer fallback builds, and deep-call unwinding through leaf and non-leaf functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/unwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/arc/kernel/vmlinux.lds.S

Purpose: linker script for ARC kernel image layout.

Important sections/symbols: sets `OUTPUT_ARCH(arc)` and `ENTRY(res_service)`, defines endian-specific `jiffies`, places vector table at `CONFIG_LINUX_LINK_BASE`, handles optional ICCM/DCCM ARC fast sections, lays out init RAMFS/text/data/arch info/percpu, normal text/data/BSS/RO data, exception tables, unwind `.eh_frame`, debug/discard sections, and extension maps.

Control flow: not executable code, but controls boot-time and runtime address layout. Init sections precede main text to reduce relocation displacement. `.fixup` and exception tables are placed with text, while `.eh_frame` is either preserved with `__start_unwind`/`__end_unwind` or discarded depending on `CONFIG_ARC_DW2_UNWIND`.

State and persistence: defines persistent kernel image symbols such as `_text`, `_stext`, `_etext`, `_sdata`, `_edata`, `_end`, `__init_begin`, `__init_end`, `__arch_info_begin/end`, and optional DCCM/ICCM bounds.

Dependencies and integration: integrates with generic linker macros from `asm-generic/vmlinux.lds.h`, ARC cache/page/thread headers, unwind code, exception-table fixups, boot/init memory setup, and architecture-specific tightly coupled memory support.

Risks: layout mistakes can break vectors, relocation range, init freeing, unwind table discovery, exception fixups, or tightly coupled memory alignment. Discarding debug/unwind sections under the wrong configuration removes required runtime metadata.

Test signals: successful link/boot, correct vector base, exception-table fixup tests, `CONFIG_ARC_DW2_UNWIND` stack traces, init section freeing, and builds with ICCM/DCCM/endian variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/arc/lib/Makefile

Purpose: selects ARC assembly implementations for core string and memory primitives.

Important entries: always builds ARC700-compatible `strchr-700.o`, `strcpy-700.o`, `strlen.o`, and `memcmp.o`. ARCompact adds `memcpy-700.o`, `memset.o`, and `strcmp.o`. ARCv2 adds `memset-archs.o` and `strcmp-archs.o`, plus either `memcpy-archs-unaligned.o` or `memcpy-archs.o` depending on `CONFIG_ARC_USE_UNALIGNED_MEM_ACCESS`.

Control flow: build-time selection only; object choice determines which exported C library symbols satisfy kernel calls.

State and persistence: no runtime state.

Dependencies and integration: integrates with kernel lib symbol resolution and ISA configuration. The selected files must match CPU alignment capabilities, zero-overhead-loop behavior, endian support, and optional 64-bit load/store support.

Risks: wrong object selection can cause illegal instructions or bad alignment behavior on a target CPU. Because these routines implement ubiquitous primitives, defects have whole-kernel blast radius.

Test signals: architecture builds for ARCompact/ARCv2, boot smoke tests, string/memory KUnit or lib tests, unaligned-copy stress, and endian build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/memcmp.S -->
# sources/distributed-fs/ceph-client/arch/arc/lib/memcmp.S

Purpose: optimized ARC assembly implementation of `memcmp()`.

Important APIs/functions: exports `memcmp` via `ENTRY_CFI(memcmp)`. Uses endian-specific register roles and comparison extraction logic.

Control flow: checks combined alignment and length to choose wordwise or bytewise path. Wordwise path loads paired words, uses zero-overhead loops, compares even/odd words, then isolates the first differing byte. Bytewise path handles unaligned or short buffers. ARCv2 has special loop placement because a branch cannot be the last instruction in a zero-overhead loop.

State and persistence: no persistent state; clobbers scratch registers per ABI and returns comparison result in `r0`.

Dependencies and integration: used by generic kernel code through lib linkage. Depends on ARC instructions such as `lpne`, `norm`, `bmsk`, endian macros, and CFI linkage macros.

Risks: first-difference selection is subtle and endian-specific. Off-by-one length handling or loop scheduling mistakes would corrupt sorting/comparison semantics. Zero-length and unaligned inputs are important edge cases.

Test signals: memcmp tests for equal, first/last-byte difference, every length around 0-16, unaligned source pairs, endian variants, and ARCv2 zero-overhead-loop builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/memcmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/memcpy-700.S -->
# sources/distributed-fs/ceph-client/arch/arc/lib/memcpy-700.S

Purpose: ARCompact/ARC700 optimized `memcpy()`.

Important APIs/functions: exports `memcpy` through `ENTRY_CFI(memcpy)`.

Control flow: tests source/destination alignment and length. Aligned copies load/store words in a zero-overhead loop, with special handling for a 4-byte chunk and final partial word using endian-specific masking. Unaligned or small cases fall back to bytewise copy using load/store byte loops.

State and persistence: no persistent state; returns original destination in `r0` while copying through `r5`.

Dependencies and integration: selected by `arch/arc/lib/Makefile` for `CONFIG_ISA_ARCOMPACT`. Relies on ARC700 instruction scheduling, delay slots, auto-increment addressing, and endian-aware final masking.

Risks: `memcpy()` does not guarantee overlap safety; callers must use `memmove()` for overlapping ranges. Partial final word logic can accidentally touch bytes outside the range if masks are wrong. Alignment detection drives correctness and performance.

Test signals: copy tests across small lengths, aligned/unaligned src/dst combinations, final byte counts 1-7, endian builds, and overlap-negative tests confirming callers do not misuse `memcpy()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/memcpy-700.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/memcpy-archs-unaligned.S -->
# sources/distributed-fs/ceph-client/arch/arc/lib/memcpy-archs-unaligned.S

Purpose: ARCv2 `memcpy()` optimized for CPUs/configurations where unaligned memory accesses are permitted.

Important APIs/functions: exports `memcpy`. Macro `LOADX`/`STOREX` selects 64-bit `ldd/std` when `CONFIG_ARC_HAS_LL64` is present, otherwise 32-bit loads/stores.

Control flow: copies 32 or 64 byte blocks in an unrolled zero-overhead loop, then copies the remaining bytes one at a time. It avoids alignment prologue because the selected configuration permits unaligned accesses.

State and persistence: no persistent state; `r0` remains destination return value and `r3` walks the destination.

Dependencies and integration: selected for ARCv2 when `CONFIG_ARC_USE_UNALIGNED_MEM_ACCESS` is enabled. Depends on ARCv2 load/store behavior, optional LL64, and kernel lib linkage.

Risks: illegal or slow unaligned hardware behavior would make this unsafe if selected for the wrong CPU. It is not overlap-safe. Large unrolled operations need correct block-size constants for LL64 and non-LL64 variants.

Test signals: unaligned source and destination copy tests, LL64 and non-LL64 builds, small tails 0-31 bytes, long copies, and hardware/platform smoke tests for unaligned access support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/memcpy-archs-unaligned.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/memcpy-archs.S -->
# sources/distributed-fs/ceph-client/arch/arc/lib/memcpy-archs.S

Purpose: ARCv2 `memcpy()` for configurations that cannot rely on unaligned memory access.

Important APIs/functions: exports `memcpy`; defines endian-specific shift/merge/extract macros and LL64-aware `LOADX`/`STOREX`.

Control flow: handles zero and small sizes, byte-copies until destination is word-aligned, then chooses source-aligned fast copy or one of three source-unaligned reconstruction paths. Unaligned source offsets 1, 2, and 3 are rebuilt with shifted adjacent words; tails are copied bytewise.

State and persistence: no persistent state; uses scratch registers to hold merged source words and returns destination in `r0`.

Dependencies and integration: selected for ARCv2 when unaligned access is not enabled. Depends on endian macros, optional LL64, zero-overhead loops, and kernel lib symbol linkage.

Risks: byte reconstruction is high-risk for endian and off-by-one errors, especially around small lengths after alignment prologue. Source/destination overlap is not supported. Incorrect tail handling can undercopy or overcopy.

Test signals: exhaustive small-size copy tests, all source alignment offsets, destination alignment transitions, endian builds, LL64 builds, and randomized buffer comparisons against a reference implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/memcpy-archs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/memset-archs.S -->
# sources/distributed-fs/ceph-client/arch/arc/lib/memset-archs.S

Purpose: ARCv2 optimized `memset()` and `memzero()`.

Important APIs/functions: exports `memset` and `memzero`. Optional `PREALLOC_INSTR`/`PREFETCHW_INSTR` macros emit cache preallocation/prefetch only for 64-byte L1 cache line configurations. LL64 controls 64-bit stores.

Control flow: zero-length returns immediately. Short lengths use byte stores. Longer ranges prefetch, byte-fill until destination alignment, replicate the byte into a word, then write 64-byte and 32-byte unrolled chunks before byte tail. `memzero()` remaps arguments and tail-calls `memset`.

State and persistence: no persistent state; returns original destination.

Dependencies and integration: selected for ARCv2. Depends on `L1_CACHE_SHIFT`, optional `CONFIG_ARC_HAS_LL64`, and safe use of prefetch/prealloc within the target range.

Risks: preallocation is only valid for line sizes explicitly handled; emitting it for other line sizes could touch outside the memset range. Tail and alignment logic must preserve return value and avoid overstore.

Test signals: memset tests over lengths 0-128+, all destination alignments, values beyond 0x7f, LL64/non-LL64 builds, cache-line-size variants, and `memzero()` equivalence tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/memset-archs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/memset.S -->
# sources/distributed-fs/ceph-client/arch/arc/lib/memset.S

Purpose: ARCompact/ARC700 `memset()` and `memzero()`.

Important APIs/functions: exports `memset` and `memzero`; `SMALL` controls the bytewise tiny path threshold.

Control flow: computes alignment from destination and length. Aligned path expands the byte to a word and stores words in a zero-overhead loop. Unaligned larger ranges fix up the start/end using byte/halfword stores, then enter the aligned loop. Tiny ranges byte-store directly. `memzero()` converts `(mem, size)` to `memset(mem, 0, size)` and branches.

State and persistence: no persistent state; returns the original destination pointer.

Dependencies and integration: selected for `CONFIG_ISA_ARCOMPACT`. Uses ARC short instructions, auto-increment stores, zero-overhead loops, and CFI linkage.

Risks: alignment fixups write around range edges and must not overrun. `SMALL` must remain large enough for the alignment strategy. Endian-independent byte replication must keep only low byte of value.

Test signals: every small length around the threshold, all destination alignments, nonzero byte values, large lengths, and `memzero()` call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/memset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/strchr-700.S -->
# sources/distributed-fs/ceph-client/arch/arc/lib/strchr-700.S

Purpose: ARC700 optimized `strchr()`.

Important APIs/functions: exports `strchr`, taking string pointer in `r0` and target char in `r1`, returning pointer or NULL in `r0`.

Control flow: normalizes the target byte into a repeated word, handles initial unaligned bytes, then scans words using branch-light zero-byte and matching-byte detection. When either NUL or target is found, endian-specific logic computes the first relevant byte offset and returns either its address or NULL if NUL came first.

State and persistence: no persistent state.

Dependencies and integration: always included by the ARC lib Makefile. Uses ARC word operations, `norm`, `ror`, endian-specific bit math, and careful code alignment for branch prediction.

Risks: simultaneous target/NUL detection must choose the earliest byte. Endian-specific bit tricks are easy to break. It can read aligned words containing bytes beyond the terminating NUL, so it relies on normal architecture tolerance for word-at-a-time string scanning.

Test signals: searches for present/absent characters at every offset, target `'\0'`, unaligned string starts, strings shorter than one word, and endian coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/strchr-700.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/strcmp-archs.S -->
# sources/distributed-fs/ceph-client/arch/arc/lib/strcmp-archs.S

Purpose: ARCv2 optimized `strcmp()`.

Important APIs/functions: exports `strcmp`.

Control flow: if either pointer is not halfword/word aligned, falls back to a byte loop. The aligned path loads words, detects NUL in the first string with a repeated-byte mask, compares whole words, and on mismatch or NUL isolates the relevant byte to return -1, 0, or 1 style ordering. Big-endian paths swizzle words before comparison.

State and persistence: no persistent state.

Dependencies and integration: selected for ARCv2. Depends on ARCv2 `ffs`, `swape`, branch hints, and endian conditionals.

Risks: return value need only indicate ordering, but must match C semantics. NUL detection and word mismatch interaction are subtle, especially on big endian and when one string terminates inside the compared word.

Test signals: equal strings, prefix cases, first difference at each byte position, unaligned pointers, strings containing high-bit bytes, and endian variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/strcmp-archs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/strcmp.S -->
# sources/distributed-fs/ceph-client/arch/arc/lib/strcmp.S

Purpose: ARCompact/ARC700 optimized `strcmp()`.

Important APIs/functions: exports `strcmp`.

Control flow: unaligned pointers use a byte loop. Aligned pointers use word loads and a repeated `0x01010101` zero-detection trick to scan until either a NUL or mismatch. Little-endian and big-endian paths then mask or adjust the first significant byte and return ordering.

State and persistence: no persistent state.

Dependencies and integration: selected for `CONFIG_ISA_ARCOMPACT`. Uses ARC700 scheduling assumptions, `norm`, `ror`, byte masks, and endian macros.

Risks: the big-endian path compensates for zero-detection carry propagation; careless edits could misorder bytes around `0x00`/`0x01`. Word-at-a-time reads require valid accessible memory past short strings within normal alignment expectations.

Test signals: prefix/equal/different strings, mismatch before and after NUL, high-bit bytes, all alignments, and big-endian-specific zero/carry cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/strcmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/strcpy-700.S -->
# sources/distributed-fs/ceph-client/arch/arc/lib/strcpy-700.S

Purpose: ARC700 optimized `strcpy()`.

Important APIs/functions: exports `strcpy`, preserving the original destination in `r0`.

Control flow: aligned source/destination uses word-at-a-time copy with NUL detection. It handles source 4-byte versus 8-byte alignment to allow limited read-ahead without crossing unwanted cache lines. Once a word containing NUL is found, it stores bytes until the terminator. Unaligned cases use a byte loop.

State and persistence: no persistent state.

Dependencies and integration: always built in ARC lib. Depends on ARC zero-byte detection, endian-specific byte extraction, auto-increment stores, and ABI return convention.

Risks: `strcpy()` requires sufficient destination space and non-overlap. Word-at-a-time read-ahead must not access invalid memory in corner cases. Byte termination handling must store the NUL exactly once.

Test signals: empty strings, strings of every length around word boundaries, all source/destination alignments, endian builds, and destination content checks immediately after NUL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/strcpy-700.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/strlen.S -->
# sources/distributed-fs/ceph-client/arch/arc/lib/strlen.S

Purpose: optimized ARC `strlen()`.

Important APIs/functions: exports `strlen`.

Control flow: aligns the effective scan window around the input address, performs early detection across the first two loaded words with masks adjusted for the starting offset, then loops loading pairs of words until a zero byte is detected. Endian-specific logic converts the zero-byte mask into the byte count returned in `r0`.

State and persistence: no persistent state.

Dependencies and integration: always built in ARC lib. Uses word-at-a-time zero-byte detection, `norm`, `ror`, endian-specific masking, and ARC load scheduling.

Risks: initial unaligned address handling is subtle and may read before/around the string's first byte depending on aligned base computation. Length calculation must account for endian and early-end paths. Normal C string preconditions still apply.

Test signals: lengths 0 through multiple word boundaries, all pointer alignments, page-boundary strings where accessible padding matters, and endian coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/lib/strlen.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/arc/mm/Makefile

Purpose: selects ARC memory-management implementation objects.

Important entries: always builds `extable.o`, `ioremap.o`, `dma.o`, `fault.o`, `init.o`, `tlb.o`, `tlbex.o`, `cache.o`, and `mmap.o`; adds `highmem.o` when `CONFIG_HIGHMEM` is enabled.

Control flow: build-time only. The selected objects provide page fault handling, TLB refill/flush, cache maintenance, DMA coherency, I/O remapping, memory boot setup, mmap policy, and optional highmem kmap setup.

State and persistence: no runtime state.

Dependencies and integration: tied to ARC MMU, cache, and memory-map Kconfig options. `tlbex.o` provides assembly exception entry points consumed by low-level vector code.

Risks: omitting an object breaks required architecture hooks. Optional highmem must be built only when the generic highmem infrastructure expects ARC kmap setup.

Test signals: architecture build matrix with and without `CONFIG_HIGHMEM`, boot, page fault, TLB, DMA, and ioremap smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/cache.c -->
# sources/distributed-fs/ceph-client/arch/arc/mm/cache.c

Purpose: implements ARC cache discovery, cache maintenance, DMA cache hooks, I-cache/D-cache synchronization, user cacheflush syscall, SLC and IOC setup.

Important APIs/functions: exposes cache geometry reporting through `arc_cache_mumbojumbo()`, runtime init via `arc_cache_init()`, DMA cache functions `dma_cache_wback_inv()`, `dma_cache_inv()`, `dma_cache_wback()`, icache sync APIs `flush_icache_range()`, `__sync_icache_dcache()`, `__inv_icache_pages()`, `__flush_dcache_pages()`, `flush_cache_all()`, and page helpers `copy_user_highpage()`/`clear_user_page()`.

Control flow: boot reads BCRs into `ic_info`, `dc_info`, `slc_info`, detects IOC and peripheral aperture, validates line sizes, chooses I-cache line-loop implementation, configures IOC if available/enabled, and assigns DMA cache function pointers to L1-only or SLC-aware implementations. Runtime cache ops choose entire, region, or line operations; D-cache ops bracket hardware commands with IRQ disable and status polling; SLC ops serialize with a spinlock.

State and persistence: persistent state includes cache geometry structs, `l2_line_sz`, `ioc_exists`, policy globals `slc_enable`/`ioc_enable`, peripheral aperture `perip_base`/`perip_end`, `_cache_line_loop_ic_fn`, and DMA cache function pointers. Page/folio `PG_dc_clean` tracks delayed D-cache cleanliness for executable mappings.

Dependencies and integration: depends on ARC aux registers, PAE40 state, SLC/IOC registers, `arc_get_mem_sz()`, DMA mapping hooks in `dma.c`, TLB/MMU init, SMP I-cache invalidation, vmalloc-to-physical translation, and the `cacheflush` syscall.

Risks: cache maintenance is hardware-sensitive. Wrong line size, PAE high-tag handling, region end semantics, SLC serialization, or IOC aperture setup can cause data corruption. `cacheflush` currently flushes all caches, which is correct but expensive. IOC is disabled with highmem/PAE constraints.

Test signals: boot cache capability logs, DMA coherency tests with coherent and noncoherent devices, module/kprobe code patching, userspace JIT cacheflush, SMP icache invalidation, highmem/PAE builds, and SLC/IOC platform tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/dma.c -->
# sources/distributed-fs/ceph-client/arch/arc/mm/dma.c

Purpose: supplies ARC architecture hooks for generic noncoherent DMA mapping.

Important APIs/functions: `arch_dma_prep_coherent()` evicts cache lines for pages becoming coherent DMA memory. `arch_sync_dma_for_device()` and `arch_sync_dma_for_cpu()` perform direction-specific cache maintenance. `arch_setup_dma_ops()` marks devices DMA-coherent when ARCv2 IOC is enabled and the device is declared coherent.

Control flow: prepare-coherent always writeback-invalidates the backing page. Device sync writes back for `DMA_TO_DEVICE`, invalidates for `DMA_FROM_DEVICE`, and writeback-invalidates for bidirectional. CPU sync invalidates for inbound/bidirectional traffic to cover speculative CPU prefetch. Setup logs coherent/noncoherent mode and toggles `dev->dma_coherent` for IOC-backed devices.

State and persistence: modifies `dev->dma_coherent`; otherwise uses cache state and function pointers owned by `cache.c`.

Dependencies and integration: depends on `dma_cache_*()` from cache code, generic `dma-map-ops`, ARC IOC policy `ioc_enable`, and device tree coherent property passed as `coherent`.

Risks: wrong direction handling can expose stale data or drop dirty CPU data. IOC aperture limitations mean marking a device coherent is only safe when hardware truly snoops the relevant memory. Highmem constraints are coordinated in cache discovery.

Test signals: DMA API debug, network/storage DMA tests, coherent versus noncoherent device tree variants, bidirectional buffer tests, and highmem/IOC platform coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/extable.c -->
# sources/distributed-fs/ceph-client/arch/arc/mm/extable.c

Purpose: implements ARC exception-table fixup lookup.

Important APIs/functions: `fixup_exception(struct pt_regs *regs)` searches exception tables for the current instruction pointer and, if found, rewrites `regs->ret` to the fixup address.

Control flow: called from fault/trap paths before declaring kernel faults fatal. A found entry returns `1`; no entry returns `0`.

State and persistence: no owned state; mutates `pt_regs` to redirect execution to fixup code.

Dependencies and integration: depends on generic exception-table search, ARC `instruction_pointer()` semantics, and `.fixup`/`__ex_table` placement from linker and inline assembly.

Risks: incorrect instruction pointer or fixup address causes bad recovery from uaccess faults. Missing exception table entries turn recoverable user-copy faults into oopses.

Test signals: `copy_to_user()`/`copy_from_user()` fault injection, unaligned emulation guarded byte accesses, and kernel fault tests that should recover via exception tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/extable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/arc/mm/fault.c

Purpose: handles ARC page faults for TLB misses and protection violations that cannot be satisfied by the assembly fast path.

Important APIs/functions: `do_page_fault()` is the main exception entry. `handle_kernel_vaddr_fault()` synchronizes a task page table with the kernel reference page table for vmalloc/pkmap/fixmap addresses.

Control flow: kernel vmalloc faults copy top-level page-table entries without taking normal locks. Other faults reject interrupt/no-mm contexts, decode write/exec from ECR, set generic fault flags, locate and validate the VMA, call `handle_mm_fault()`, handle signal/retry/completed cases, and deliver SIGSEGV/SIGBUS or call `die()` if unrecoverable in kernel. Kernel no-context faults try `fixup_exception()` before oops.

State and persistence: updates `current->thread.fault_address` on user signal delivery. Page tables and VM fault state are modified by generic mm. It reads ECR cause/vector from `pt_regs`.

Dependencies and integration: integrates with `tlbex.S` slow path, generic mm fault handling, perf page fault events, exception-table fixups, and diagnostics in traps/troubleshoot.

Risks: lock handling around `lock_mm_and_find_vma()` and `VM_FAULT_COMPLETED/RETRY` must remain correct. Permission decoding from ARC ECR must match hardware. Kernel vmalloc fault synchronization cannot sleep or take broad locks.

Test signals: user read/write/exec faults, COW and stack growth, vmalloc/module access faults, uaccess fixups, OOM/SIGBUS paths, and perf page fault counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/highmem.c -->
# sources/distributed-fs/ceph-client/arch/arc/mm/highmem.c

Purpose: initializes ARC highmem permanent and temporary mapping page tables.

Important APIs/functions: `kmap_init()` validates address-space constraints and allocates page tables for `PKMAP_BASE` and `FIXMAP_BASE`. `alloc_kmap_pgtable()` allocates a low memory PTE page with memblock and installs it into the kernel PMD.

Control flow: during memory setup, `kmap_init()` checks that vmalloc/fixmap/pkmap fit below `PAGE_OFFSET`, that `LAST_PKMAP` and `FIX_KMAP_SLOTS` fit in one PTE page, then creates dedicated page tables.

State and persistence: initializes global `pkmap_page_table` and kernel page-table entries in `init_mm`. Allocated PTE pages persist for kernel lifetime.

Dependencies and integration: depends on generic highmem/pkmap/fixmap infrastructure, ARC memory layout constants, memblock, page-table allocation helpers, and TLB flushing expectations.

Risks: ARC shares the 0x7z-0x8z kernel virtual range between vmalloc and kmap; mis-sized regions can overlap. The generic pkmap code assumes a single `pkmap_page_table`, limiting concurrent permanent maps.

Test signals: highmem boot, kmap/kmap_local stress, fixmap use, vmalloc coexistence, multi-CPU kmap slots, and build-time assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/highmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/arc/mm/init.c

Purpose: performs ARC memory discovery, memblock setup, zone limits, initrd/reserved-memory handling, and highmem PFN validation.

Important APIs/functions: `arc_get_mem_sz()`, early parameter `setup_mem_sz()`, `early_init_dt_add_memory_arch()`, `arch_zone_limits_init()`, `setup_arch_memory()`, `arch_mm_preinit()`, and highmem `pfn_valid()`.

Control flow: DT memory parsing records the first lowmem bank at `CONFIG_LINUX_RAM_BASE`; additional banks become highmem when configured. `setup_arch_memory()` initializes `init_mm`, low PFN bounds, reserves kernel/initrd/FDT memory, scans reserved memory, dumps memblock state, computes highmem PFNs, sets `arch_pfn_offset`, and calls `kmap_init()`. `arch_mm_preinit()` frees highmem reservation for normal use and validates page-table page sizing.

State and persistence: owns `swapper_pg_dir`, `low_mem_sz`, highmem bounds, `high_mem_start/high_mem_sz`, and exported `arch_pfn_offset`. Memblock reservations determine early allocator state.

Dependencies and integration: depends on DT memory callbacks, memblock, initrd, reserved-memory scanning, ARC section symbols, highmem kmap setup, and generic zone setup.

Risks: DT base must match `CONFIG_LINUX_RAM_BASE` for lowmem. Highmem without PAE has noncontiguous physical address assumptions; `pfn_valid()` masks holes. Incorrect memblock reservations can overwrite kernel/initrd/FDT or allocate `mem_map` in unreachable highmem.

Test signals: boot with DT memory, `mem=` override, initrd boot, highmem and PAE variants, `/proc/iomem`/zone sizing, and sparse/hole PFN validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/ioremap.c -->
# sources/distributed-fs/ceph-client/arch/arc/mm/ioremap.c

Purpose: implements ARC I/O remapping policy.

Important APIs/functions: `ioremap()`, `ioremap_prot()`, `iounmap()`, and helper `arc_uncached_addr_space()`.

Control flow: `ioremap()` returns a direct cast for physical addresses that already live in ARC hardware uncached space; otherwise it creates a noncached generic MMU mapping. `ioremap_prot()` always goes through the MMU but forces noncached attributes while preserving caller access-control intent. `iounmap()` skips direct uncached addresses and delegates mapped addresses to `generic_iounmap()`.

State and persistence: no owned state. It reads `perip_base`/`perip_end` from cache discovery and ARCompact `ARC_UNCACHED_ADDR_SPACE`.

Dependencies and integration: integrates with generic ioremap/vmalloc mappings, cache code peripheral aperture discovery, ARC ISA distinctions, and driver I/O resource mapping.

Risks: direct-cast optimization assumes the uncached region is within 32-bit addressable space. Incorrect peripheral aperture detection can skip required MMU mappings or unmap direct addresses. `ioremap_prot()` intentionally bypasses the direct optimization for access-control use cases.

Test signals: driver MMIO mapping on ARCompact and ARCv2, peripheral aperture logs, iounmap of direct versus vmalloc mappings, and access permission tests with `ioremap_prot()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/ioremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/mmap.c -->
# sources/distributed-fs/ceph-client/arch/arc/mm/mmap.c

Purpose: provides ARC-specific mmap placement and page protection mapping.

Important APIs/functions: `arch_get_unmapped_area()` enforces shared mapping alignment for VIPT cache alias avoidance. `protection_map` maps Linux `VM_*` access combinations to ARC user PTE protections and is exported through `DECLARE_VM_GET_PAGE_PROT`.

Control flow: fixed mappings are accepted only if shared mappings satisfy `SHMLBA` alignment relative to file offset. Non-fixed requests validate size, try a caller-specified aligned address if available, then call `vm_unmapped_area()` with `align_offset = pgoff << PAGE_SHIFT`.

State and persistence: no persistent state; reads `current->mm` and VMA layout.

Dependencies and integration: depends on generic mmap helpers, ARC cache aliasing constraints, and ARC PTE protection definitions.

Risks: wrong alignment can cause VIPT aliasing coherency bugs for shared mappings. Protection map choices intentionally make private writable mappings read-only until fault/COW handling; changing them affects mm semantics.

Test signals: mmap alignment tests for `MAP_SHARED`, `MAP_FIXED` rejection, randomized mmap placement, executable/writable protection checks, and cache aliasing stress on VIPT systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/tlb.c -->
# sources/distributed-fs/ceph-client/arch/arc/mm/tlb.c

Purpose: manages ARC MMU/TLB flush, insertion, diagnostics, feature discovery, and initialization for MMUv3/MMUv4.

Important APIs/functions: TLB flush APIs include `local_flush_tlb_all()`, `local_flush_tlb_mm()`, `local_flush_tlb_range()`, `local_flush_tlb_page()`, kernel-range flushes, SMP wrappers, and THP PMD flushes. Insertion/update paths are `create_tlb()`, `update_mmu_cache_range()`, and `update_mmu_cache_pmd()`. Init/reporting APIs are `arc_mmu_mumbojumbo()`, `pae40_exist_but_not_enab()`, `arc_mmu_init()`, and duplicate handler `do_tlb_overlap_fault()`.

Control flow: MMUv3 lookup/probe/write and MMUv4 delete/insert paths differ behind helpers. Large flushes prefer ASID rollover or full flush; smaller ranges erase entries one by one under IRQ disable. Page-fault completion pre-installs TLB entries for the current mm and flushes D/I cache for executable pages with dirty kernel mappings. Boot decodes MMU BCRs, validates page and superpage sizes, enables ASID 0, and caches the kernel PGD.

State and persistence: per-CPU `asid_cache`, global `mmuinfo`, and debug knob `dup_pd_silent` persist. It mutates hardware aux registers, TLB entries, PTE accessed/dirty/present bits, and folio `PG_dc_clean`.

Dependencies and integration: integrates with `tlbex.S` fast refill, `fault.c`, MMU context code, cache maintenance, THP, SMP IPIs, PAE40, and ARC aux registers.

Risks: ASID and IRQ ordering are critical; checking ASID and erasing entries must be atomic with respect to context switches/interrupts. PAE40 high descriptor writes must match hardware. Preinstalling TLB entries assumes `current->active_mm == vma->vm_mm`. Duplicate TLB recovery scans hardware sets and should remain conservative.

Test signals: fork/exit/munmap flush behavior, SMP TLB shootdowns, THP faults/flushes, executable page cache coherency, PAE40 builds, duplicate TLB fault recovery, and MMU feature mismatch boot panics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/tlbex.S -->
# sources/distributed-fs/ceph-client/arch/arc/mm/tlbex.S

Purpose: assembly fast-path handlers for ARC instruction and data TLB misses.

Important macros/entry points: `EV_TLBMissI` and `EV_TLBMissD` are exception entries. `TLBMISS_FREEUP_REGS`/`TLBMISS_RESTORE_REGS` save scratch registers using ARCompact global/per-CPU storage or ARCv2 stack slots. `LOAD_FAULT_PTE` walks the current page tables. `CONV_PTE_TO_TLB` converts Linux PTE bits to ARC PD0/PD1(/PD1HI). `COMMIT_ENTRY_TO_MMU` writes the hardware TLB.

Control flow: on TLB miss, the handler saves minimal registers, reads fault address, locates current PGD, walks configured page-table levels, handles THP PMD entries, validates permissions for instruction or data access, sets accessed/dirty bits, converts PTE to TLB descriptors, commits the entry, restores registers, and returns with `rtie`. Missing page tables or permission failures branch to `do_slow_path_pf`, restore registers, and enter the normal exception prologue for `do_page_fault()`.

State and persistence: mutates PTE accessed/dirty bits and hardware TLB entries. ARCompact uses `ex_saved_reg1` scratch storage; ARCv2 uses stack. It reads current PGD from `ARC_REG_SCRATCH_DATA0` on ARCv2.

Dependencies and integration: tightly coupled with page-table bit layout, MMU context setup, low-level exception vectors, `fault.c`, `tlb.c`, THP, PAE40 PTE size, and ARC aux register definitions.

Risks: this is latency-critical and register-fragile. Any mismatch in PTE bit definitions, page-table level shifts, scratch register protocol, or ECR cause decoding can corrupt TLB state or fault recursively. SMP ARCompact scratch storage must remain per-CPU and cache-line separated.

Test signals: instruction/data TLB miss boot coverage, user read/write/execute faults, vmalloc faults that go slow path, THP mappings, PAE40 builds, SMP stress, and low-level exception return correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/mm/tlbex.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/net/Makefile -->
# sources/distributed-fs/ceph-client/arch/arc/net/Makefile

Purpose: selects ARC networking architecture objects for eBPF JIT support.

Important entries: when `CONFIG_ISA_ARCV2=y`, `CONFIG_BPF_JIT` builds `bpf_jit_core.o` and `bpf_jit_arcv2.o`.

Control flow: build-time only. It restricts this JIT backend to ARCv2.

State and persistence: no runtime state.

Dependencies and integration: integrates with generic BPF JIT core and the ARCv2 backend defined by `bpf_jit.h`/`bpf_jit_arcv2.c`.

Risks: enabling the backend for non-ARCv2 would emit unsupported instructions. Disabling it falls back to the interpreter or generic behavior depending on kernel configuration.

Test signals: build matrix for ARCv2 with `CONFIG_BPF_JIT=y/n`, ARCompact builds confirming no backend object is selected, and BPF selftests on ARCv2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/net/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/net/bpf_jit.h -->
# sources/distributed-fs/ceph-client/arch/arc/net/bpf_jit.h

Purpose: declares the backend contract between ARC BPF JIT core logic and architecture-specific instruction emitters.

Important APIs/types/functions: defines `ARC_ADDR`, temporary JIT register index `JIT_REG_TMP`, safe buffer advancement macro `BUF()`, backend emitter prototypes for moves, loads/stores, arithmetic, bitwise ops, shifts, frame handling, jumps, calls, return marshalling, and byte swapping. Defines `enum ARC_CC` for backend-independent ARC jump conditions.

Control flow: no executable control flow. The prototypes encode a two-pass JIT model where emitters can be called with `buf == NULL` to compute lengths and with a real buffer to emit bytes. `BUF()` preserves NULL during dry runs.

State and persistence: no owned state.

Dependencies and integration: included by ARC BPF JIT core and ARCv2 backend. Depends on Linux BPF register definitions and filter infrastructure.

Risks: length-return contracts are critical; divergent lengths between dry run and emit pass corrupt branch offsets and code layout. `enum ARC_CC` order is used by array sizing/indexing in the backend and must not be changed casually.

Test signals: BPF JIT dry-run/emission consistency, branch offset selftests, all ALU/memory/call op translations, and compile coverage for debug mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/net/bpf_jit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/net/bpf_jit_arcv2.c -->
# sources/distributed-fs/ceph-client/arch/arc/net/bpf_jit_arcv2.c

Purpose: implements the ARCv2 backend for translating eBPF operations into ARC machine instructions.

Important APIs/functions: low-level `arc_*` emitters encode ARC moves, loads/stores, ALU, shifts, branches, calls, and returns. BPF-facing functions implement `zext()`, `mov_*`, `load_r()`, `store_*`, arithmetic/bitwise/shift operations, `gen_swap()`, register usage analysis through `mask_for_used_regs()`, frame prologue/epilogue, 32/64-bit jump check/generation, and `gen_func_call()`.

Control flow: emitters support dry-run length calculation and real emission through `buf` checks. Register mapping assigns BPF register pairs to ARC register pairs, preserving ABI argument/return constraints. Memory accesses use `adjust_mem_access()` to materialize large offsets in a temporary register. 64-bit ALU is composed from 32-bit operations with carry/borrow or temporary registers. Prologue saves used callee-saved registers, optional FP, and BLINK; epilogue restores them and moves BPF return value to ARC ABI return registers. Jump generation first validates displacement ranges, then emits 32-bit compare/tst plus branch or multi-branch 64-bit comparison templates.

State and persistence: no global mutable state. Translation state is implicit in emitted buffer position, returned lengths, register mapping, usage mask, and frame size provided by the caller.

Dependencies and integration: compiled only for ARCv2 BPF JIT. Depends on `bpf_jit.h`, Linux BPF instruction semantics, ARCv2 ABI, branch displacement encoding, endian configuration, and the generic BPF JIT core that sequences passes and final code allocation.

Risks: length stability is the core safety invariant; immediate moves for relocations and function calls use fixed-size forms to avoid pass divergence. Branch displacement checks must match emitted templates. 64-bit signed/unsigned comparisons and shifts are subtle because ARC is 32-bit. External calls must marshal BPF arg5 onto the stack and move return registers correctly. Division/modulo immediate zero returns no code and relies on higher-level BPF validation semantics.

Test signals: kernel BPF selftests, JIT versus interpreter result comparison for ALU64/ALU32, signed and unsigned jumps, far/near branch boundaries, memory offsets outside S9, endian swap operations, helper calls with five arguments, prologue/epilogue register preservation, and dry-run/emitted-size assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/net/bpf_jit_arcv2.c -->
