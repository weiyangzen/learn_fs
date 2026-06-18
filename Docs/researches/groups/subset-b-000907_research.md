# subset-b-000907 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/msr-smp.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/msr-smp.c

## Purpose
This file provides SMP-aware wrappers for reading and writing x86 model-specific registers (MSRs) on a specified CPU or CPU mask. It lets generic kernel and module code execute MSR operations on the target CPU, return values through shared or per-CPU buffers, and choose either raw or fault-tolerant MSR access paths.

## Important APIs, Types, and Functions
The exported one-CPU APIs are `rdmsr_on_cpu()`, `rdmsrq_on_cpu()`, `wrmsr_on_cpu()`, `wrmsrq_on_cpu()`, `rdmsr_safe_on_cpu()`, `rdmsrq_safe_on_cpu()`, `wrmsr_safe_on_cpu()`, `wrmsrq_safe_on_cpu()`, `rdmsr_safe_regs_on_cpu()`, and `wrmsr_safe_regs_on_cpu()`. Multi-CPU operations are `rdmsr_on_cpus()` and `wrmsr_on_cpus()`, which take a `struct msr __percpu *` result/input area. The local callback helpers use `struct msr_info`, `struct msr_info_completion`, `struct msr_regs_info`, `call_single_data_t`, `smp_call_function_single()`, `smp_call_function_single_async()`, and `smp_call_function_many()`.

## Control Flow
Single-CPU raw reads and writes zero a `struct msr_info`, fill the MSR number and optional value, then synchronously run `__rdmsr_on_cpu()` or `__wrmsr_on_cpu()` on the target CPU. The callbacks either use `this_cpu_ptr(rv->msrs)` for per-CPU arrays or `rv->reg` for scalar results. Multi-CPU calls pin the current CPU with `get_cpu()`, execute locally if the current CPU is in the mask, then call all CPUs in the mask with `smp_call_function_many()` before `put_cpu()`. Safe read uses an asynchronous CSD plus completion so the target CPU can complete the value and error path before the caller resumes.

## State and Persistence
The file has no persistent global state. It transiently shares stack-allocated request structures with remote CPU callbacks while waiting for completion. For mask operations, persistent data is caller-owned per-CPU `struct msr` storage.

## Dependencies and Integration Points
It depends on x86 MSR primitives in `asm/msr.h`, CPU masks, SMP call-function infrastructure, per-CPU accessors, preemption control, completions, and Linux symbol exports. It is used by CPU feature, microcode, performance, virtualization, and platform code that must touch CPU-local MSRs from a non-local context.

## Risks and Test Signals
Risks include invalid target CPUs, hotplug races if callers do not constrain CPU lifetime, using raw access on absent MSRs, writing dangerous MSR values, and assuming multi-CPU operations report per-CPU failures when the raw mask helpers do not. Test signals include successful remote MSR reads on online CPUs, correct propagation of `rdmsr_safe*` and `wrmsr_safe*` errors, CPU hotplug stress, per-CPU buffer contents matching target CPUs, and fault injection with unsupported MSR numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/msr-smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/msr.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/msr.c

## Purpose
This file contains common x86 MSR utility functions. It allocates per-CPU MSR buffers, implements read-modify-write bit helpers for 64-bit MSR fields, and exposes tracepoint bridge functions for MSR/RDPMC instrumentation.

## Important APIs, Types, and Functions
`msrs_alloc()` and `msrs_free()` allocate and release `struct msr __percpu` arrays. `msr_set_bit()` and `msr_clear_bit()` are KVM-exported helpers backed by `__flip_bit()`, `msr_read()`, and `msr_write()`. Tracepoint wrappers under `CONFIG_TRACEPOINTS` are `do_trace_write_msr()`, `do_trace_read_msr()`, and `do_trace_rdpmc()`, and the file instantiates `CREATE_TRACE_POINTS` for `asm/msr-trace.h`.

## Control Flow
The bit helpers validate the bit index, read the MSR with `rdmsrq_safe()`, modify the requested bit in a copy, skip writes when no change is needed, and write the new value with `wrmsrq_safe()`. They return a negative error, `0` for no hardware write, or positive success for an accepted write. Trace wrappers simply call the generated tracepoint functions with the MSR/PMC number, value, and failure flag.

## State and Persistence
Persistent state is limited to allocated per-CPU MSR buffers owned by callers and the tracepoint definitions registered by the tracing subsystem. The bit helpers do not cache MSR state.

## Dependencies and Integration Points
The file integrates with Linux per-CPU allocation, `asm/msr.h` safe MSR primitives, KVM symbol export policy, and x86 MSR tracepoints. KVM can use `msr_set_bit()`/`msr_clear_bit()` without depending on local implementation details.

## Risks and Test Signals
Risks include non-atomic read-modify-write if another CPU or firmware mutates the same MSR concurrently, unsupported MSRs returning errors, and feature code misreading the positive return as a bit value. Test signals include allocation failure handling, unsupported MSR reads/writes, set/clear idempotence, tracepoint visibility when enabled, and KVM module linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/msr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/pc-conf-reg.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/pc-conf-reg.c

## Purpose
This file defines the raw spinlock that serializes access to the legacy PC configuration register I/O window at ports `0x22` and `0x23`.

## Important APIs, Types, and Functions
The only object is `DEFINE_RAW_SPINLOCK(pc_conf_lock)`, declared through `asm/pc-conf-reg.h`. Users acquire this lock around indirect index/data port accesses.

## Control Flow
There is no executable control flow in this file. It supplies the single lock instance for other code paths that perform the actual in/out instructions.

## State and Persistence
`pc_conf_lock` is persistent global synchronization state. It protects an indirect hardware register namespace whose selected index can otherwise be corrupted by concurrent users.

## Dependencies and Integration Points
It depends on Linux raw spinlocks and the x86 `pc-conf-reg` interface. Integration points are CPU/chipset and MP-spec-era code that touches Cyrix or chipset configuration registers through ports `0x22` and `0x23`.

## Risks and Test Signals
Risks are mostly in users of the lock: missing locking can target the wrong indirect register, while sleeping locks would be invalid in low-level contexts. Test signals include successful build/link of all `pc_conf_lock` users and hardware tests on systems that still expose the port pair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/pc-conf-reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/putuser.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/putuser.S

## Purpose
This assembly file implements the out-of-line x86 `__put_user_*` helpers used by uaccess inline assembly to store 1, 2, 4, or 8 byte values into user memory while returning an error code through a nonstandard register ABI.

## Important APIs, Types, and Functions
Exported entry points are `__put_user_1`, `__put_user_2`, `__put_user_4`, `__put_user_8`, and nocheck variants `__put_user_nocheck_1`, `__put_user_nocheck_2`, `__put_user_nocheck_4`, and `__put_user_nocheck_8`. The shared failure path is `__put_user_handle_exception`. The `check_range` macro performs bounds checks on 32-bit and sign/canonicalization logic on 64-bit. The code uses `ASM_STAC`, `ASM_CLAC`, `ANNOTATE_NOENDBR`, `_ASM_EXTABLE_UA`, and x86 linkage macros.

## Control Flow
Checked helpers validate the user address range, enable SMAP user access with STAC, perform the store, clear access with CLAC, zero `%ecx`, and return. Nocheck variants skip the range check but still use STAC/CLAC and exception-table fixups. Any store fault jumps through the uaccess exception table to `__put_user_handle_exception`, which clears SMAP access and returns `-EFAULT` in `%ecx`.

## State and Persistence
The file has no persistent state. It temporarily mutates AC/SMap access state and writes caller-supplied data into user memory. The ABI preserves registers except for the documented error register and clobbers.

## Dependencies and Integration Points
It integrates with x86 uaccess macros, SMAP, exception tables, objtool/IBT annotations, kernel errno values, and 32/64-bit register naming macros. It is on a critical syscall and copy-to-user path.

## Risks and Test Signals
Risks include ABI drift with inline callers, missing CLAC on faults, incorrect range checks near `TASK_SIZE_MAX`, split 64-bit writes on i386, and exception-table label mistakes. Test signals include uaccess selftests, fault injection on invalid user pointers, SMAP-enabled boot tests, 32-bit and 64-bit builds, objtool validation, and syscall paths that use `put_user()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/putuser.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/retpoline.S -->
# sources/distributed-fs/ceph-client/arch/x86/lib/retpoline.S

## Purpose
This file supplies x86 indirect branch and return thunks for Spectre/Retbleed/SRSO/ITS mitigations. It contains compiler-visible thunk symbols, alternative instruction sequences selected by CPU feature bits, and special return-untraining sequences with strict alignment requirements.

## Important APIs, Types, and Functions
Generated symbols include `__x86_indirect_thunk_<reg>` for every general register, optional `__x86_indirect_call_thunk_<reg>` and `__x86_indirect_jump_thunk_<reg>` for call-depth tracking, optional `__x86_indirect_its_thunk_<reg>` and paranoid ITS thunks, `entry_untrain_ret`, `call_depth_return_thunk`, `its_return_thunk`, `srso_alias_untrain_ret`, `srso_alias_safe_ret`, `srso_return_thunk`, `retbleed_return_thunk`, and the compiler magic symbol `__x86_return_thunk`. Macros `POLINE`, `RETPOLINE`, `THUNK`, `CALL_THUNK`, `JUMP_THUNK`, and `ITS_THUNK` compose the thunks.

## Control Flow
The base thunk array emits one entry per register. Depending on alternatives, each thunk runs a classic retpoline, an LFENCE plus indirect jump, or a direct indirect jump when retpoline is not needed. RETHUNK code emits return thunks and untraining sequences: SRSO paths use aliasing or MOVABS-style safe returns, Retbleed paths use aligned byte sequences that intentionally decode differently when entered at different points, and call-depth tracking stuffs the return stack when the per-CPU depth counter reaches zero. `__x86_return_thunk` is a boot/module-init target expected to be patched by `apply_returns()`.

## State and Persistence
Runtime state is mostly code text and alternative-patched instruction bytes. Call-depth tracking also uses per-CPU `__x86_call_depth`. The file exports thunk symbols so modules and compiler-generated code can reference stable mitigation entry points.

## Dependencies and Integration Points
It depends on x86 alternative patching, CPU feature bits, objtool/unwind hints, IBT annotations, per-CPU assembly, compiler options such as `-mindirect-branch=thunk-extern` and `-mfunction-return=thunk-extern`, module symbol exports, and mitigation Kconfig choices. It is tightly integrated with boot-time return patching and entry code.

## Risks and Test Signals
Risks are high because alignment, symbol names, annotations, and byte layouts are mitigation contracts. A bad change can break speculation protections, unwinding, module linkage, objtool validation, or boot. Test signals include objtool success, absence of unpatched `__x86_return_thunk` warnings, CPU-feature alternative coverage, module loading with thunk references, mitigation selftests/boot logs, and performance/regression checks on affected Intel and AMD families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/retpoline.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/string_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/string_32.c

## Purpose
This file provides i386 hand-optimized implementations of selected C string and memory scanning primitives when the architecture selects the corresponding `__HAVE_ARCH_*` macros.

## Important APIs, Types, and Functions
Conditionally exported functions include `strcpy()`, `strncpy()`, `strcat()`, `strncat()`, `strcmp()`, `strncmp()`, `strchr()`, `strlen()`, `memchr()`, `memscan()`, and `strnlen()`. The implementations use x86 string instructions such as `lodsb`, `stosb`, `scasb`, `cmpsb`, and `repne`/`repe` loops, and disable fortify wrappers via `__NO_FORTIFY`.

## Control Flow
Each function is a compact inline-assembly loop around the conventional libc/kernel semantic. Copy and concatenate functions scan or copy until NUL or a count reaches zero. Compare functions return negative, zero, or positive via arithmetic on `%eax`. Search functions scan for a byte and return either the found address or NULL/end-like values according to the API.

## State and Persistence
There is no persistent state. The functions mutate only caller-provided buffers and register state described by asm constraints.

## Dependencies and Integration Points
The file integrates with the kernel string API, export symbols, i386 GCC inline-asm constraints, and build-time architecture feature macros. It is used by generic kernel code as a replacement for C implementations when enabled.

## Risks and Test Signals
Risks include subtle off-by-one behavior, missing memory clobbers, undefined overlap semantics matching standard string APIs, and compiler constraint drift on 32-bit builds. Test signals include lib/string tests, KUnit/string tests if enabled, 32-bit build coverage, boot smoke tests, and comparison against generic C implementations for edge cases such as empty strings and zero counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/string_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/strstr_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/strstr_32.c

## Purpose
This file implements the i386 architecture-specific `strstr()` routine using x86 string instructions.

## Important APIs, Types, and Functions
The sole exported API is `char *strstr(const char *cs, const char *ct)`. It uses inline assembly with `repne scasb` to measure/search the needle and `repe cmpsb` to test candidate positions.

## Control Flow
The assembly first computes the needle length, preserving the empty-needle case. It then repeatedly compares the needle against the current haystack position, returns the current position on match, advances one byte on mismatch, and stops with NULL when it reaches the haystack NUL terminator.

## State and Persistence
There is no persistent state. The function only reads the two input strings and returns a pointer into the haystack or NULL.

## Dependencies and Integration Points
It depends on the kernel string API, export symbols, and i386 inline-assembly register conventions. It replaces the generic implementation when the 32-bit architecture selects it.

## Risks and Test Signals
Risks include boundary mistakes around empty needles, haystack termination, and inline-asm clobber constraints. Test signals include string selftests comparing generic and architecture variants with empty, single-character, repeated-prefix, and missing-needle cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/strstr_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/usercopy.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/usercopy.c

## Purpose
This file implements `copy_from_user_nmi()`, an x86 user-copy helper that is safe in NMI context by disabling page faults and aborting on fault instead of sleeping or faulting in pages.

## Important APIs, Types, and Functions
The exported GPL API is `copy_from_user_nmi(void *to, const void __user *from, unsigned long n)`. It uses `__access_ok()`, `nmi_uaccess_okay()`, `pagefault_disable()`, `raw_copy_from_user()`, `pagefault_enable()`, and instrumentation hooks `instrument_copy_from_user_before()`/`after()`.

## Control Flow
The function first rejects out-of-range user pointers and architectures/states where NMI uaccess is not allowed. It disables page faults, emits copy instrumentation, performs the raw copy, emits completion instrumentation with the uncopied byte count, re-enables page faults, and returns the number of bytes not copied.

## State and Persistence
There is no persistent state. The function temporarily changes the current execution context's pagefault-disabled state and reads user memory into a kernel buffer.

## Dependencies and Integration Points
It integrates with x86 NMI fault handling, CR2 preservation rules, uaccess helpers, fault disabling, KASAN/KCSAN/usercopy instrumentation, and callers such as profiling, tracing, or diagnostics that may need best-effort user reads in NMI/IRQ-like contexts.

## Risks and Test Signals
Risks include using it when faults must be resolved, missing access checks, instrumentation mismatches, and architecture changes that make NMI uaccess unsafe. Test signals include invalid pointer returns, pagefault-disabled behavior, NMI/profiling stack sampling, and instrumentation/usercopy sanitizer coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/usercopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/usercopy_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/usercopy_32.c

## Purpose
This file implements 32-bit x86 low-level user memory copy and clear helpers, including generic string-instruction copies and optional Intel-tuned unrolled/non-temporal paths.

## Important APIs, Types, and Functions
Exported APIs include `clear_user()`, `__clear_user()`, `__copy_user_ll()`, and `copy_from_user_inatomic_nontemporal()`. Optional Intel helpers are `__copy_user_intel()` and `__copy_user_intel_nocache()`, with global `struct movsl_mask movsl_mask`. Core macros are `__do_clear_user()` and `__copy_user()`, both using exception table fixups with remaining-byte accounting.

## Control Flow
`clear_user()` checks `access_ok()` before zeroing; `__clear_user()` assumes the caller checked. The clear macro enables user access, zeros longwords with `rep stosl`, handles trailing bytes with `rep stosb`, and uses exception fixups to leave the uncleared count in the return variable. `__copy_user_ll()` begins nospec uaccess, chooses the generic or Intel path based on alignment/size heuristics, and ends uaccess. `copy_from_user_inatomic_nontemporal()` uses `user_access_begin()`, optionally selects non-temporal Intel copies for larger XMM2-capable transfers, then ends access.

## State and Persistence
Persistent state is optional `movsl_mask`, configured elsewhere for Intel copy heuristics. Runtime state is limited to AC/user-access windows, destination memory, and remaining byte counts.

## Dependencies and Integration Points
It depends on 32-bit uaccess infrastructure, SMAP access macros, exception-table types such as `EX_TYPE_UCOPY_LEN4`, CPU feature detection, `might_fault()`, and symbol exports. It underpins generic `copy_{to,from}_user()` and clear-user paths on i386.

## Risks and Test Signals
Risks include incorrect uncopied-byte accounting after faults, missing access window closure, stale CPU-specific copy heuristics, non-temporal copy ordering, and alignment bugs. Test signals include LKDTM/usercopy checks, invalid pointer fault tests, short-copy count validation, SMAP builds, 32-bit boot, and performance tests across Intel and non-Intel configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/usercopy_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/usercopy_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/lib/usercopy_64.c

## Purpose
This file supplies 64-bit x86 persistent-memory/cache-flush copy helpers when `CONFIG_ARCH_HAS_UACCESS_FLUSHCACHE` is enabled. It writes back cache lines with CLWB and provides non-temporal memcpy/copy-from-user variants for pmem durability paths.

## Important APIs, Types, and Functions
Key functions are `clean_cache_range()`, `arch_wb_cache_pmem()`, `copy_user_flushcache()`, and `__memcpy_flushcache()`. The implementation uses `boot_cpu_data.x86_clflush_size`, `clwb()`, `copy_to_nontemporal()`, `masked_user_access_begin()`, `user_access_end()`, `memcpy()`, `movnti`, `sfence` semantics inherited from users, and libnvdimm integration.

## Control Flow
`clean_cache_range()` rounds the start down to cache-line granularity and issues CLWB over the range. `arch_wb_cache_pmem()` is a direct exported wrapper. `copy_user_flushcache()` begins masked user access, copies from user to destination using non-temporal stores, ends access, then explicitly flushes edge regions when alignment or size forced cached copies. `__memcpy_flushcache()` copies and flushes an unaligned prefix, uses 32-byte, 8-byte, and 4-byte `movnti` loops for the aligned body, then cached-copies and flushes any tail.

## State and Persistence
There is no file-local persistent state. The observable persistence behavior is hardware cache writeback for pmem-durability users, with data written to caller-provided memory and cache lines flushed from CPU caches.

## Dependencies and Integration Points
It depends on x86 cache-line size discovery, CLWB support plumbing, non-temporal copy primitives, uaccess masking, highmem/libnvdimm headers, and pmem/DAX users that need explicit writeback. The functions are exported GPL symbols for persistence infrastructure.

## Risks and Test Signals
Risks include incorrect edge flushing for unaligned transfers, assuming CLWB availability through the Kconfig path, user-access faults during pmem copy, and durability bugs if callers omit required ordering barriers. Test signals include pmem/DAX tests, unaligned start/size cases, faulting user source copies, cacheline-size variation, and persistence validation across power-fail simulation where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/lib/usercopy_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/Makefile

## Purpose
This Makefile builds the wm-FPU-emu software x87 emulator for x86 systems that need math emulation. It collects C and assembly emulator objects and applies emulator-specific compiler/assembler flags.

## Important APIs, Types, and Functions
Build variables are `DEBUG`, `PARANOID`, `ccflags-y`, `asflags-y`, `C_OBJS`, `A_OBJS`, and `obj-y`. The optional `proto` target regenerates `fpu_proto.h` with `cproto`.

## Control Flow
Kbuild includes this Makefile when math emulation is enabled. It compiles the listed C files for decode, arithmetic, load/store, constants, conversion, comparison, and transcendental operations, plus assembly files for unsigned arithmetic, normalization, rounding, square root, shifts, and extended-significand math.

## State and Persistence
The Makefile has no runtime state. It persists build composition and default `PARANOID` checking policy into the compiled emulator objects.

## Dependencies and Integration Points
It depends on x86 kbuild, the `$(MATH_EMULATION)` flag, 32-bit assembler conventions, and the source files in the same directory. The object list is the integration map for the whole soft-FPU subsystem.

## Risks and Test Signals
Risks include missing an object from `obj-y`, stale generated prototypes, and mismatched flags between C and assembly. Test signals are successful math-emulation builds, absence of undefined emulator symbols, and runtime execution on no-FPU or forced-emulation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/control_w.h -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/control_w.h

## Purpose
This header defines x87 control-word bit masks used by both C and assembly emulator code, including exception masks, rounding control, and precision control.

## Important APIs, Types, and Functions
Key macros are `CW_RC`, `CW_PC`, `CW_Precision`, `CW_Underflow`, `CW_Overflow`, `CW_ZeroDiv`, `CW_Denormal`, `CW_Invalid`, `CW_Exceptions`, rounding modes `RC_RND`, `RC_DOWN`, `RC_UP`, `RC_CHOP`, precision modes `PR_24_BITS`, `PR_53_BITS`, `PR_64_BITS`, `PR_RESERVED_BITS`, and `FULL_PRECISION`. `_Const_()` adapts constants for assembler or C.

## Control Flow
There is no control flow. These constants drive branches and masking in arithmetic, load/store, and exception code.

## State and Persistence
The header defines how the persistent per-task `control_word` field is interpreted. It does not store state itself.

## Dependencies and Integration Points
It is included by emulator C and assembly files that need IEEE/x87 exception masks, rounding mode selection, and precision mode selection. It integrates closely with `exception.h`, `status_w.h`, and `fpu_system.h`.

## Risks and Test Signals
Risks include bit mismatches with hardware x87 semantics or assembler constant syntax. Test signals include correct behavior under all rounding modes, masked/unmasked exceptions, and save/restore of the control word through `fldcw`, `fstcw`, `fninit`, and regset APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/control_w.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/div_Xsig.S -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/div_Xsig.S

## Purpose
This assembly file divides 96-bit fixed-point `Xsig` quantities for transcendental polynomial code. It trades exact 96-bit division for an approximation intended to exceed normal 64-bit precision.

## Important APIs, Types, and Functions
The exported function is `div_Xsig(Xsig *a, const Xsig *b, Xsig *dest)`. Local storage tracks a four-word accumulator and three-word result. PARANOID builds can call `FPU_exception()` with internal codes `0x240` to `0x242` when arithmetic invariants fail.

## Control Flow
The routine halves the dividend to avoid overflow, computes the first two quotient words using augmented-divisor estimates and correction subtracts, then estimates the third word after accounting for the low divisor word. It writes the three-word result to `dest`. Error labels in PARANOID mode report logic failures and still return through the normal epilogue.

## State and Persistence
There is no persistent state in the normal build; temporaries live on the stack unless `NON_REENTRANT_FPU` selects static storage. The result mutates the caller-provided `Xsig`.

## Dependencies and Integration Points
It depends on the `Xsig` layout from `poly.h`, i386 calling conventions from `fpu_asm.h`/`fpu_emu.h`, and exception reporting. It is used by `poly_2xm1.c`, `poly_atan.c`, `poly_l2.c`, and `poly_tan.c`.

## Risks and Test Signals
Risks include divisor normalization assumptions, quotient correction mistakes, stack/static reentrancy choices, and precision loss affecting transcendental functions. Test signals include polynomial helper accuracy, PARANOID builds without internal exceptions, and comparison of `f2xm1`, `fpatan`, `fyl2x`, `fyl2xp1`, and `fptan` against hardware x87.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/div_Xsig.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/div_small.S -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/div_small.S

## Purpose
This assembly file implements a small helper to divide a 64-bit unsigned integer in place by a 32-bit unsigned denominator and return the remainder.

## Important APIs, Types, and Functions
The exported function is `FPU_div_small(unsigned long long *x, unsigned long y)`. It uses the i386 `divl` instruction twice, first for the high word and then for the low word.

## Control Flow
The function loads the high 32 bits, divides by `y` with zero high dividend, stores the high quotient, then divides the low 32 bits using the previous remainder in `%edx`, stores the low quotient, and returns the final remainder in `%eax`.

## State and Persistence
There is no global state. The 64-bit integer pointed to by `x` is overwritten with the quotient, and the remainder is returned.

## Dependencies and Integration Points
It depends on 32-bit x86 calling convention macros and is declared in `fpu_emu.h`. Other emulator conversion or rounding code can use it for decimal/integer scaling.

## Risks and Test Signals
Risks include divide-by-zero or quotient overflow if callers violate preconditions. Test signals include integer conversion tests, BCD load/store paths, and emulator builds with assembly helper linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/div_small.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/errors.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/errors.c

## Purpose
This file centralizes wm-FPU-emu exception handling, debug printing, NaN propagation, stack fault handling, divide-by-zero, overflow/underflow, and precision/denormal status updates.

## Important APIs, Types, and Functions
Important functions include `FPU_illegal()`, `FPU_printall()`, `FPU_exception()`, `real_1op_NaN()`, `real_2op_NaN()`, `arith_invalid()`, `FPU_divide_by_zero()`, `set_precision_flag()`, `set_precision_flag_up()`, `set_precision_flag_down()`, `denormal_operand()`, `arith_overflow()`, `arith_underflow()`, `FPU_stack_overflow()`, `FPU_stack_underflow()`, `FPU_stack_underflow_i()`, and `FPU_stack_underflow_pop()`. It uses exception name tables and internal error IDs to help diagnose PARANOID failures.

## Control Flow
`FPU_exception()` maps emulator exception bits into the partial status word, sets summary/backward bits for unmasked exceptions, and optionally prints diagnostics. NaN helpers distinguish quiet/signaling/unsupported NaNs, apply masked invalid-operation responses, and copy the selected quiet NaN result to the destination register. Arithmetic fault helpers update status, generate masked default results such as QNaN, infinity, or zero, and return tag values with `FPU_Exception` when unmasked. Stack helpers update top/tag state only for masked responses where x87 compatibility requires a value to be produced.

## State and Persistence
The file mutates per-task emulator state through `partial_status`, `control_word`, `top`, register tags, and register contents. It can send SIGILL/SIGFPE indirectly through `math_abort()` or deferred summary status observed by `math_emulate()`.

## Dependencies and Integration Points
It depends on Linux signals, uaccess-safe debug printing, emulator constants, status/control words, register constants, and `fpu_system.h` per-task macros. Almost every arithmetic, load/store, compare, and transcendental path calls these helpers for IEEE/x87-compatible edge cases.

## Risks and Test Signals
Risks include wrong mask semantics, incorrect C1 handling for precision/stack faults, NaN priority mistakes, and mismatches with 80486 behavior. Test signals include masked and unmasked exception tests, SIGFPE/SIGILL delivery, status/control word inspection, NaN propagation cases, stack overflow/underflow behavior, and PARANOID internal error absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/errors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/exception.h -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/exception.h

## Purpose
This header defines emulator exception and status-summary constants shared by C and assembly code.

## Important APIs, Types, and Functions
Macros include `FPU_BUSY`, `EX_ErrorSummary`, `EX_INTERNAL`, `EX_StackOver`, `EX_StackUnder`, `EX_Precision`, `EX_Underflow`, `EX_Overflow`, `EX_ZeroDiv`, `EX_Denormal`, `EX_Invalid`, `PRECISION_LOST_UP`, `PRECISION_LOST_DOWN`, and the `EXCEPTION(x)` wrapper that optionally logs file/line before calling `FPU_exception()`.

## Control Flow
The header has no runtime control flow beyond the `EXCEPTION()` macro expansion. It standardizes the exception code values consumed by the rest of the emulator.

## State and Persistence
It does not store state, but its bit definitions map directly onto persistent `partial_status` and control-word mask behavior.

## Dependencies and Integration Points
It includes `fpu_emu.h` when needed for status bit definitions, and is included by C and assembly arithmetic, polynomial, and decode files.

## Risks and Test Signals
Risks include bit-value drift from x87 status/control words and macro differences between assembler and C. Test signals are correct exception status bits after emulator operations and successful assembly preprocessing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/exception.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_arith.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_arith.c

## Purpose
This file implements register-to-register x87 arithmetic instruction handlers for add, multiply, subtract, divide, reverse variants, destination variants, and pop variants.

## Important APIs, Types, and Functions
Handlers include `fadd__()`, `fmul__()`, `fsub__()`, `fsubr_()`, `fdiv__()`, `fdivr_()`, `fadd_i()`, `fmul_i()`, `fsubri()`, `fsub_i()`, `fdivri()`, `fdiv_i()`, `faddp_()`, `fmulp_()`, `fsubrp()`, `fsubp_()`, `fdivrp()`, and `fdivp_()`. They dispatch to core helpers `FPU_add()`, `FPU_mul()`, `FPU_sub()`, and `FPU_div()` using flags such as `REV` and `DEST_RM`.

## Control Flow
Each handler reads `FPU_rm`, clears C1, calls the appropriate arithmetic helper with source/destination flags and `control_word`, and for `p` variants pops the x87 stack only when the operation did not report a negative error/exception result.

## State and Persistence
The handlers mutate per-task soft-FPU registers, tags, `top`, and status bits through lower-level arithmetic helpers. No file-local state is retained.

## Dependencies and Integration Points
It is called from the `st_instr_table` in `fpu_entry.c` for ModRM register opcodes. It depends on `fpu_system.h`, `fpu_emu.h`, `control_w.h`, and `status_w.h`.

## Risks and Test Signals
Risks include wrong source/destination flag selection for reversed and pop forms, popping after failed operations, and C1 status mismatches. Test signals include x87 arithmetic instruction suites covering all register forms and stack depth changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_arith.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_asm.h -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_asm.h

## Purpose
This header provides assembly-side definitions for wm-FPU-emu helper routines, including stack-frame parameter offsets and `FPU_REG` field offsets.

## Important APIs, Types, and Functions
Macros include `EXCEPTION`, `PARAM1` through `PARAM7`, `SIGL_OFFSET`, `EXP(x)`, `SIG(x)`, `SIGL(x)`, and `SIGH(x)`. It includes `linux/linkage.h` for symbol annotations.

## Control Flow
There is no runtime control flow. The macros let assembly helpers access C arguments and `FPU_REG` fields consistently.

## State and Persistence
It stores no state, but its offsets define how assembly reads and writes caller-provided emulator structures.

## Dependencies and Integration Points
It is included by emulator `.S` files through `fpu_emu.h`. It depends on 32-bit frame-pointer calling conventions used by these old helper routines.

## Risks and Test Signals
Risks include offset drift if `FPU_REG` layout or calling convention changes. Test signals include successful emulator assembly builds and correct arithmetic helper behavior under stack/register tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_aux.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_aux.c

## Purpose
This file implements auxiliary x87 instructions such as finit/fclex/fstsw, register load/exchange/store, conditional moves, free/pop variants, and soft-FPU state initialization.

## Important APIs, Types, and Functions
Important functions include `fpstate_init_soft()`, `finit()`, `finit_()`, `fstsw_()`, `fp_nop()`, `fld_i_()`, `fxch_i()`, `fcmovb()`, `fcmove()`, `fcmovbe()`, `fcmovu()`, `fcmovnb()`, `fcmovne()`, `fcmovnbe()`, `fcmovnu()`, `ffree_()`, `ffreep()`, `fst_i_()`, and `fstp_i()`. Dispatch tables include `finit_table`, `fstsw_table`, and `fp_nop_table`.

## Control Flow
`fpstate_init_soft()` zeros the soft state and installs the default control word, empty tag word, zero instruction/data addresses, and no-update flag. `finit_()`, `fstsw_()`, and `fp_nop()` index small tables by `FPU_rm`. Register stack helpers check empty tags, implement masked underflow responses, copy registers with `reg_copy()`, swap tags for `fxch`, and use EFLAGS condition bits for `fcmovcc`.

## State and Persistence
The file mutates persistent per-task emulator state: soft control/status/tag words, `ftop`, register stack slots, instruction/data address fields, EAX for `fstsw ax`, and `no_ip_update`. Conditional moves and exchanges update tag words along with register contents.

## Dependencies and Integration Points
It is invoked from `fpu_entry.c`'s register-opcode table and from FPU state setup paths. It depends on x86 task FPU state, EFLAGS, exception helpers, constants, and tag helpers.

## Risks and Test Signals
Risks include tag/register mismatch after swaps, incorrect default state, unsupported `fcmovcc` behavior on CPUs that should gate it, and wrong underflow priority. Test signals include `fninit`, `fnclex`, `fstsw`, `fld st(i)`, `fxch`, `ffree`, `fstp`, and conditional move instruction tests plus regset save/restore validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_emu.h -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_emu.h

## Purpose
This is the main wm-FPU-emu shared header. It defines the internal floating-point register representation, tag values, exponent/sign constants, instruction prefixes, address-mode structures, stack macros, sign/exponent helpers, and prototypes for assembly arithmetic helpers.

## Important APIs, Types, and Functions
Key types are `struct address`, `struct fpu__reg`/`FPU_REG`, `FUNC`, `FUNC_ST0`, `overrides`, and `fpu_addr_modes`. Important constants include exponent bounds, tag values `TAG_Valid`/`TAG_Zero`/`TAG_Special`/`TAG_Empty`, special classifications `TW_Denormal`/`TW_Infinity`/`TW_NaN`, prefix constants, mode constants `VM86`, `PM16`, and `SEG32`, plus flags `REV`, `DEST_RM`, and `LOADED`. Helper macros include `st(x)`, `push()`, `poppop()`, sign manipulation, exponent manipulation, and `significand()`. It declares assembly helpers such as `FPU_u_add()`, `FPU_u_sub()`, `FPU_u_mul()`, `FPU_u_div()`, `wm_sqrt()`, `FPU_shrx()`, `FPU_div_small()`, and `FPU_round()`.

## Control Flow
The header has no standalone control flow, but it shapes almost every emulator branch by standardizing stack indexing, tag checks, sign operations, and conversion between stored extended exponent and internal exponent formats.

## State and Persistence
It maps persistent per-task soft-FPU state through macros from `fpu_system.h`: register stack memory, tag word, top pointer, control word, status word, and instruction/data pointers. It stores no file-local state.

## Dependencies and Integration Points
It includes `fpu_system.h`, signal context UAPI, math emulator task structures, and generated `fpu_proto.h`. It is included by nearly every emulator C file and by assembly files through the assembler branch.

## Risks and Test Signals
Risks are broad: structure layout or macro errors affect all arithmetic, decode, and state save/restore paths. Test signals include full soft-FPU instruction coverage, build coverage for assembler/C modes, regset save/restore tests, and comparison with hardware x87 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_emu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_entry.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_entry.c

## Purpose
This file contains the main wm-FPU-emu entry point, instruction decode loop, address-mode handling, exception deferral behavior, and soft-FPU regset get/set functions.

## Important APIs, Types, and Functions
Public entry points are `math_emulate()`, `math_abort()`, `fpregs_soft_set()`, and `fpregs_soft_get()`. Static decode data includes `st_instr_table` and `type_table`. `valid_prefix()` parses FPU instruction prefixes. The file coordinates with `FPU_get_address()`, `FPU_get_address_16()`, `FPU_load_store()`, arithmetic tables, `FPU_exception()`, and signal delivery.

## Control Flow
`math_emulate()` records the trap context, derives default address mode from VM86, flat user mode, kernel mode, or LDT descriptor mode, parses prefixes, handles FWAIT and pending exception summary state, fetches ModRM, decodes memory versus register forms, checks segmented limits, loads memory operands when needed, handles NaN and denormal priority, dispatches arithmetic/load-store/register handlers, records instruction and operand addresses, and optionally looks ahead to emulate multiple FPU instructions unless tracing/reschedule prevents it. `math_abort()` restores the original EIP, sends a signal, and unwinds through the saved emulator stack. Regset set/get copy soft-FPU state to and from ptrace/core interfaces, rotate register order by `ftop`, and recompute tags on set.

## State and Persistence
The file mutates the current task's soft-FPU state: `FPU_info`, EIP/original EIP, control/status/tag words, top pointer, instruction and operand addresses, register stack, access limit, and no-update/lookahead flags. It also sends SIGFPE, SIGILL, or SIGSEGV through the current task.

## Dependencies and Integration Points
It integrates with x86 trap handling, user accessors, VM86 and LDT segmentation, FPU regset APIs, task FPU storage, scheduler reschedule checks, and all emulator operation tables. It is the boundary between the kernel's device-not-available/math fault path and the software x87 implementation.

## Risks and Test Signals
Risks include instruction decode errors, bad segment limit enforcement, incorrect exception priority, stale instruction pointer updates, non-reentrancy during user faults, and regset rotation/tag bugs. Test signals include forced math emulation across 16-bit, VM86, and flat modes where possible, ptrace/core dump FPU state checks, invalid instruction/fault signal tests, and comparison of decoded x87 instruction streams with hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_entry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_etc.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_etc.c

## Purpose
This file implements a small group of single-register x87 instructions: change sign, absolute value, test, and examine.

## Important APIs, Types, and Functions
The public dispatcher is `FPU_etc()`, using `fp_etc_table`. Static handlers are `fchs()`, `fabs()`, `ftst_()`, `fxam()`, and `FPU_ST0_illegal()`.

## Control Flow
`FPU_etc()` indexes the handler table with `FPU_rm` and passes `st(0)` plus its tag. `fchs()` toggles the sign bit and `fabs()` clears it when ST0 is not empty. `ftst_()` sets condition codes based on zero, sign, denormal, NaN, infinity, or empty cases and raises exceptions where required. `fxam()` classifies ST0 into x87 condition bits and includes the sign in C1.

## State and Persistence
The file mutates ST0 sign bits, condition-code bits in `partial_status`, and exception status. It has no file-local persistent state.

## Dependencies and Integration Points
It is dispatched from `fpu_entry.c` for `D9 E0..E7`-style opcodes. It depends on tag classification, status-word macros, exception helpers, and register constants.

## Risks and Test Signals
Risks include incorrect condition-code encodings, denormal exception priority, and 80486 compatibility quirks. Test signals include `fchs`, `fabs`, `ftst`, and `fxam` instruction tests across zero, finite, denormal, infinity, NaN, and empty-stack inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_etc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_proto.h -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_proto.h

## Purpose
This generated-style header declares the cross-file wm-FPU-emu functions used when not building prototypes. It is the glue that lets old C and assembly-oriented emulator files call each other without local forward declarations.

## Important APIs, Types, and Functions
The header declares functions from `errors.c`, `fpu_arith.c`, `fpu_aux.c`, `fpu_entry.c`, `fpu_etc.c`, `fpu_tags.c`, `fpu_trig.c`, `get_address.c`, `load_store.c`, polynomial files, arithmetic/register files not in this work item, and conversion/load-store helpers. It includes entry points such as `math_emulate()`, `FPU_exception()`, `FPU_add()`, `FPU_sub()`, `FPU_load_store()`, `poly_l2()`, and many `FPU_load_*`/`FPU_store_*` functions.

## Control Flow
There is no runtime control flow. Its declarations affect compile-time type checking and function linkage.

## State and Persistence
It stores no state, but the declarations expose functions that mutate the current task's soft-FPU state.

## Dependencies and Integration Points
It depends on prior definitions of `FPU_REG`, `fpu_addr_modes`, and related types from `fpu_emu.h`. The Makefile's `proto` target documents how to regenerate it with `cproto`.

## Risks and Test Signals
Risks include stale prototypes that hide ABI/type mismatches, especially for `asmlinkage`, `__user`, and tag-return conventions. Test signals include warning-free builds with stricter prototype checking and successful linkage of all emulator objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_system.h -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_system.h

## Purpose
This header provides kernel/system integration for the wm-FPU-emu: LDT descriptor access, segment descriptor helpers, per-task soft-FPU state macros, and user memory access wrappers.

## Important APIs, Types, and Functions
Important helpers include `FPU_get_ldt_descriptor()`, `seg_get_base()`, `seg_get_limit()`, `seg_get_granularity()`, `seg_expands_down()`, `seg_execute_only()`, and `seg_writable()`. State macros expose `I387`, `FPU_info`, segment/register fields, `FPU_lookahead`, `no_ip_update`, `FPU_rm`, `access_limit`, `partial_status`, `control_word`, `fpu_tag_word`, `registers`, `top`, `instruction_address`, and `operand_address`. Uaccess macros include `FPU_access_ok()`, `FPU_code_access_ok()`, `FPU_get_user()`, and `FPU_put_user()`.

## Control Flow
Descriptor helpers decode base, limit, granularity, and permissions from x86 descriptors. `FPU_get_ldt_descriptor()` conditionally locks the current mm LDT context and returns a descriptor or zero descriptor. Uaccess macros abort math emulation with SIGSEGV when access checks or get/put operations fail.

## State and Persistence
The header maps persistent current-task FPU emulator state but stores no state itself. `FPU_get_ldt_descriptor()` transiently locks the current mm context.

## Dependencies and Integration Points
It depends on scheduler/current task state, mm/LDT context, x86 descriptor definitions, uaccess, and signal abort behavior. It is included throughout the emulator for access to task state and memory.

## Risks and Test Signals
Risks include incorrect descriptor permission/limit logic, user memory aborts from the wrong EIP, and macro side effects. Test signals include segmented addressing tests, LDT-enabled workloads, VM86 paths, user fault injection, and regset consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_system.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_tags.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_tags.c

## Purpose
This file manages the x87 emulator tag word, stack top, special value classification, and register-copy helpers.

## Important APIs, Types, and Functions
Functions include `FPU_pop()`, `FPU_gettag0()`, `FPU_gettagi()`, `FPU_gettag()`, `FPU_settag0()`, `FPU_settagi()`, `FPU_settag()`, `FPU_Special()`, `isNaN()`, `FPU_empty_i()`, `FPU_stackoverflow()`, `FPU_copy_to_regi()`, `FPU_copy_to_reg1()`, and `FPU_copy_to_reg0()`.

## Control Flow
Tag accessors compute the physical register index from `top` plus logical stack offsets. `FPU_pop()` marks the current top empty and increments top. Special classification maps exponent/significand patterns to denormal, infinity, or NaN. Copy helpers copy a full `FPU_REG` and set the target tag in the same operation.

## State and Persistence
The file mutates persistent per-task `fpu_tag_word`, `top`, and register stack contents. There is no file-local state.

## Dependencies and Integration Points
It is used by nearly all emulator instruction handlers. It depends on `fpu_emu.h`, `fpu_system.h`, and exception constants for tag values and exponent interpretation.

## Risks and Test Signals
Risks include tag-word corruption, stack wrap mistakes, and misclassification of pseudo-denormals or unsupported NaNs. Test signals include stack push/pop instruction tests, `fxam`, save/restore tag-word tests, and edge values for zero, denormal, infinity, and NaN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_tags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_trig.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_trig.c

## Purpose
This file implements x87 transcendental and miscellaneous ST0/ST1 instructions such as `f2xm1`, `fptan`, `fxtract`, `fsqrt`, `fsin`, `fcos`, `fsincos`, `fprem`, `fyl2x`, `fpatan`, `fyl2xp1`, `fscale`, and stack pointer adjustments.

## Important APIs, Types, and Functions
Public dispatchers are `FPU_triga()` and `FPU_trigb()`, backed by `trig_table_a` and `trig_table_b`. Major static helpers include `trig_arg()`, `rem_kernel()`, `do_fprem()`, `convert_l2reg()`, `single_arg_error()`, `single_arg_2_error()`, `f2xm1()`, `fptan()`, `fxtract()`, `fsqrt_()`, `frndint_()`, `f_sin()`, `f_cos()`, `fsincos()`, `fyl2x()`, `fpatan()`, `fyl2xp1()`, and `fscale()`.

## Control Flow
The dispatchers call a handler selected by `FPU_rm`. Trigonometric handlers reduce arguments with `trig_arg()`, call polynomial helpers, adjust quadrant/sign, and set precision flags. Remainder instructions use `do_fprem()` and `rem_kernel()` to compute exact-ish remainders and quotient condition bits. Log/atan paths validate ST0/ST1 combinations, handle NaN/infinity/zero/denormal priority, call polynomial kernels, and pop ST0 when instruction semantics require it. `fscale()` rounds ST1 toward zero, adjusts ST0's exponent, and invokes normal rounding/exception handling.

## State and Persistence
The file heavily mutates ST0/ST1 register values, tags, top pointer, condition codes, precision/denormal/invalid/overflow/underflow status, and the control word temporarily for internal chopping operations. It restores saved control/status state around internal computations where hardware-visible flags should not leak.

## Dependencies and Integration Points
It depends on register constants, core arithmetic helpers, polynomial approximation files, fixed-point `Xsig` assembly helpers, exception/status/control logic, and tag helpers. It is reached from `fpu_entry.c` for `D9 E8..FF` and related opcode groups.

## Risks and Test Signals
Risks include argument reduction inaccuracies near large powers, quadrant/sign mistakes, exception priority mismatches, stack pop/push errors, and divergence from 80486 quirks. Test signals include transcendental instruction suites over finite/zero/denormal/infinity/NaN inputs, quotient condition bits for `fprem/fprem1`, comparison to hardware x87, and PARANOID internal error coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_trig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/get_address.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/get_address.c

## Purpose
This file decodes effective addresses for FPU memory operands in 32-bit, 16-bit, VM86, and segmented protected-mode addressing.

## Important APIs, Types, and Functions
Public functions are `FPU_get_address()` and `FPU_get_address_16()`. Static helpers and data include register-offset tables for `pt_regs`, VM86, and protected mode segment registers; `sib()` for SIB-byte decoding; `vm86_segment()`; and `pm_address()` for LDT descriptor base/limit/permission checks.

## Control Flow
`FPU_get_address()` decodes 32-bit ModRM/SIB/displacement forms, rejects illegal register-only FPU memory forms, enforces CS write protection in flat mode, records offset/selectors, and applies VM86 or protected-mode segment bases. `FPU_get_address_16()` handles 16-bit addressing combinations, defaulting BP-based forms to SS, masks offsets to 16 bits, then applies VM86 or protected-mode segment handling. `pm_address()` computes access limits for expand-up/down segments and rejects execute-only or non-writable write targets.

## State and Persistence
The file mutates `FPU_EIP` as it consumes displacement/SIB bytes, fills `struct address`, and updates global `access_limit` for later load/store bounds checks. It reads current task registers and LDT descriptors.

## Dependencies and Integration Points
It depends on user instruction-byte access, VM86 register layouts, LDT descriptor helpers from `fpu_system.h`, x86 segment semantics, and `math_abort()` for SIGSEGV/SIGILL-style failures. It is called by `math_emulate()` before memory load/store or reg/mem arithmetic.

## Risks and Test Signals
Risks include bad displacement sign extension, incorrect default segment selection, LDT race/permission mistakes, and EIP advancement errors. Test signals include FPU memory operand tests for all ModRM/SIB modes, 16-bit addressing, VM86 and LDT programs, and protected-mode segment limit violations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/get_address.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/load_store.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/load_store.c

## Purpose
This file interprets x87 memory load, store, integer conversion, environment, control-word, status-word, BCD, and extended-real instructions.

## Important APIs, Types, and Functions
The public dispatcher is `FPU_load_store(u_char type, fpu_addr_modes addr_modes, void __user *data_address)`. It uses `type_table`, `data_sizes_16`, `data_sizes_32`, the `pop_0()` macro, and load/store helpers such as `FPU_load_single()`, `FPU_load_double()`, `FPU_load_extended()`, integer load/store variants, `FPU_load_bcd()`, `FPU_store_bcd()`, `fldenv()`, `FPU_frstor()`, `fstenv()`, and `fsave()`.

## Control Flow
The dispatcher first validates segmented access limits using 16-bit or 32-bit size tables, then checks instruction class: no stack operand, ST0 required, push required, or illegal. Load forms reserve stack space, load user memory, handle NaNs for real loads, and copy data into ST0. Store forms require ST0, perform conversion, and pop only if the store succeeded. `fisttp` temporarily forces `RC_CHOP`. Environment/control/status instructions directly load/store emulator state and often return `1` to suppress later instruction-address fixups.

## State and Persistence
It mutates the FPU register stack, tags, top pointer, control word, partial status summary bits, saved environment fields, and user memory. It temporarily changes `control_word` for truncating integer stores.

## Dependencies and Integration Points
It depends on address decoding for `type`, segmented `access_limit`, uaccess wrappers, conversion routines from `reg_ld_str.c`, exception helpers, and `math_emulate()` for dispatch. It is the main bridge between decoded FPU memory operands and emulator arithmetic state.

## Risks and Test Signals
Risks include wrong data-size tables, popping after failed stores, control-word restoration bugs, access-limit mistakes, and mismatches for `fisttp`, `fldenv`, `frstor`, `fsave`, and BCD forms. Test signals include memory load/store instruction suites, invalid user pointer tests, control/status word round trips, environment save/restore tests, and integer conversion edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/load_store.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/mul_Xsig.S -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/mul_Xsig.S

## Purpose
This assembly file implements fixed-point multiplication helpers for 12-byte `Xsig` values used by polynomial approximations.

## Important APIs, Types, and Functions
Exported functions are `mul32_Xsig(Xsig *x, unsigned mult)`, `mul64_Xsig(Xsig *x, const unsigned long long *mult)`, and `mul_Xsig_Xsig(Xsig *dest, const Xsig *mult)`. All operate in place on the destination `Xsig`.

## Control Flow
Each function accumulates partial products with `mull`, `addl`, and `adcl` into stack temporaries, retaining the high 96 bits appropriate for fixed-point multiplication. The 32-bit variant multiplies by one word, the 64-bit variant by two words, and the full variant by the significant words of another `Xsig`.

## State and Persistence
There is no global state. The destination `Xsig` is overwritten with an unrounded, generally unnormalized product.

## Dependencies and Integration Points
It depends on `Xsig` word ordering and i386 frame-based calling conventions. It is called by polynomial files for `2^x-1`, atan, log2, sine/cosine, and tangent approximations.

## Risks and Test Signals
Risks include dropped carries, wrong word ordering, and accumulated low-bit error affecting transcendental accuracy. Test signals include polynomial accuracy checks, PARANOID emulator tests, and comparison to high-precision reference results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/mul_Xsig.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/poly.h -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/poly.h

## Purpose
This header defines the 12-byte extended-significand (`Xsig`) arithmetic interface used by emulator polynomial approximations for transcendental instructions.

## Important APIs, Types, and Functions
The key type is `Xsig { lsw, midw, msw }`. Declarations include `polynomial_Xsig()`, `mul32_Xsig()`, `mul64_Xsig()`, `mul_Xsig_Xsig()`, `shr_Xsig()`, `round_Xsig()`, `norm_Xsig()`, and `div_Xsig()`. Macros include `LL_MSW()`, `MK_XSIG()`, and `XSIG_LL()`. Inline helpers are `mul_32_32()`, `add_Xsig_Xsig()`, `add_two_Xsig()`, and `negate_Xsig()`.

## Control Flow
The inline helpers perform fixed-point multiplication high-word extraction, 96-bit addition with optional exponent increment on carry, and subtraction from 1.0-style negation. They are intended to compile inline for performance in polynomial loops.

## State and Persistence
There is no global state. Helpers mutate caller-provided `Xsig` accumulators and sometimes caller-provided exponent variables.

## Dependencies and Integration Points
It depends on x86 inline assembly and `asmlinkage` assembly helper implementations. It is included by all `poly_*.c` files and bridges C polynomial logic with low-level fixed-point arithmetic.

## Risks and Test Signals
Risks include aliasing assumptions in `XSIG_LL()`, inline assembly constraints, overflow not always checked, and endian/word-order dependence. Test signals include 32-bit builds, polynomial accuracy tests, and compiler variation testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/poly.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_2xm1.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_2xm1.c

## Purpose
This file computes the polynomial approximation for `2^x - 1`, used by the x87 `f2xm1` instruction.

## Important APIs, Types, and Functions
The public function is `poly_2xm1(u_char sign, FPU_REG *arg, FPU_REG *result)`. It uses coefficient table `lterms`, leading `hiterm`, and shift constants for quarter-domain identities. It calls `polynomial_Xsig()`, `mul_Xsig_Xsig()`, `shr_Xsig()`, `add_two_Xsig()`, `div_Xsig()`, `round_Xsig()`, and `FPU_round()`.

## Control Flow
The function requires `|arg| < 1`. It converts the argument significand into `Xsig`, reduces larger arguments by subtracting 0.25/0.5/0.75 slices, evaluates the polynomial plus leading term, applies the identity for shifted positive arguments, and for negative arguments computes `-f(x)/(1+f(x))`. It rounds the `Xsig` back into ST0 and sets the tag.

## State and Persistence
It mutates ST0/result register contents and tag, and may report internal exceptions in PARANOID builds. No file-local state persists.

## Dependencies and Integration Points
It is called by `fpu_trig.c`'s `f2xm1()` handler and depends on register constants, `FPU_round()`, and fixed-point helpers.

## Risks and Test Signals
Risks include domain violations, reduction identity mistakes, negative-argument division precision, and rounding flag mismatches. Test signals include `f2xm1` over negative/positive small values, near-domain-boundary inputs, and comparison to hardware/reference results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_2xm1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_atan.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_atan.c

## Purpose
This file computes arctangent approximations for `fpatan`, converting ST1/ST0 ratios into an angle with quadrant and sign adjustments.

## Important APIs, Types, and Functions
The public function is `poly_atan(FPU_REG *st0_ptr, u_char st0_tag, FPU_REG *st1_ptr, u_char st1_tag)`. It uses odd polynomial coefficient tables, `denomterm`, `fixedpterm`, and `pi_signif`. It calls `div_Xsig()`, `mul_Xsig_Xsig()`, `mul64_Xsig()`, `polynomial_Xsig()`, `add_Xsig_Xsig()`, `add_two_Xsig()`, `round_Xsig()`, and `FPU_round()`.

## Control Flow
The function compares operand magnitudes to decide whether to invert the ratio, divides significands to form the reduced argument, applies an atan identity when the argument is larger than `sqrt(2)-1`, evaluates rational polynomial terms, then adjusts by `pi/4`, `pi/2`, or `pi` depending on transformation, inversion, and original sign. The final angle is rounded into ST1 and the precision flag is set.

## State and Persistence
It mutates ST1 register contents and tag, and status precision bits. ST0 is later popped by the caller in `fpatan()`.

## Dependencies and Integration Points
It is called by `fpu_trig.c` after special-case handling for zeros, infinities, NaNs, and denormals. It depends on fixed-point `Xsig` helpers and x87 rounding semantics.

## Risks and Test Signals
Risks include quadrant errors, transformed/inverted boundary mistakes, sign preservation bugs, and polynomial precision loss. Test signals include `fpatan` quadrants, zero/infinity combinations, denormal-valid combinations, and comparisons with hardware x87.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_atan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_l2.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_l2.c

## Purpose
This file computes base-2 logarithm polynomial approximations for `fyl2x` and `fyl2xp1`.

## Important APIs, Types, and Functions
Public functions are `poly_l2(FPU_REG *st0_ptr, FPU_REG *st1_ptr, u_char st1_sign)` and `poly_l2p1(u_char s0, u_char s1, FPU_REG *r0, FPU_REG *r1, FPU_REG *d)`. Static `log2_kernel()` evaluates `log2(1+x)`. Coefficients are held in `logterms` and `leadterm`.

## Control Flow
`poly_l2()` reduces ST0 into a range around 1 using `sqrt(2)` thresholds, evaluates a log kernel, adds the integer exponent component, multiplies by ST1, rounds into ST1, and sets precision. `poly_l2p1()` handles `log2(1+x)` for small `x`, multiplies by ST1, rounds into the destination, and handles too-large or negative-domain inputs through invalid-operation behavior. `log2_kernel()` uses a transformed numerator/denominator, `div_Xsig()`, polynomial evaluation, and leading-term correction.

## State and Persistence
It mutates ST1/destination register contents, tags, and exception/precision status. It can signal underflow for very small results.

## Dependencies and Integration Points
It is called by `fpu_trig.c` handlers `fyl2x()` and `fyl2xp1()`. It depends on fixed-point helpers, register constants, control-word exception handling, and `FPU_round()`.

## Risks and Test Signals
Risks include domain handling for negative inputs, exponent recombination errors, underflow handling, and precision loss in the reduced kernel. Test signals include `fyl2x` and `fyl2xp1` across values near 1, near -1 for `log1p`, denormals, zeros, infinities, and comparison to hardware/reference results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_sin.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_sin.c

## Purpose
This file computes sine and cosine polynomial approximations for reduced x87 trigonometric arguments.

## Important APIs, Types, and Functions
Public functions are `poly_sine(FPU_REG *st0_ptr)` and `poly_cos(FPU_REG *st0_ptr)`. Coefficient tables include lower- and upper-range positive/negative polynomial terms. The functions use `Xsig` arithmetic, `mul64_Xsig()`, `mul_Xsig_Xsig()`, `polynomial_Xsig()`, `round_Xsig()`, and fixed `pi/2` correction constants.

## Control Flow
`poly_sine()` splits the domain around approximately `0.883091`, evaluates a direct sine polynomial for smaller arguments, or computes cosine of `pi/2 - x` with correction for larger arguments. `poly_cos()` splits around approximately `0.687705`, computes direct cosine for small arguments, or computes sine of `pi/2 - x` with extra fix-up. Both convert the final `Xsig` accumulator back into ST0 and preserve or set the appropriate sign.

## State and Persistence
The functions mutate ST0 contents and tag. PARANOID builds may raise internal exceptions for out-of-range results.

## Dependencies and Integration Points
They are called by `fpu_trig.c` after argument reduction and special-case handling. They depend on `poly.h`, register constants, and emulator rounding/copy helpers.

## Risks and Test Signals
Risks include domain split boundary errors, pi/2 approximation correction mistakes, result overflow checks, and sign handling. Test signals include `fsin`, `fcos`, and `fsincos` tests near 0, pi/4, pi/2, reduced quadrant boundaries, and comparison with hardware x87.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_sin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_tan.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_tan.c

## Purpose
This file computes tangent approximations for reduced x87 trigonometric arguments.

## Important APIs, Types, and Functions
The public function is `poly_tan(FPU_REG *st0_ptr)`. It uses odd/even numerator and denominator coefficient tables, `twothirds`, `Xsig` accumulators, and helpers `polynomial_Xsig()`, `mul_Xsig_Xsig()`, `mul64_Xsig()`, `div_Xsig()`, `add_two_Xsig()`, and `round_Xsig()`.

## Control Flow
The function splits the domain around `pi/4`. For larger arguments it computes `pi/2 - x`, evaluates tangent for the complement, applies a pi/2 approximation fix-up, and inverts the result. For smaller arguments it directly evaluates a rational polynomial and adds the correction to the original argument. The result is written back as a positive valid ST0 value; the caller applies final sign/quadrant handling.

## State and Persistence
It mutates ST0 significand, exponent, and tag. There is no file-local persistent state.

## Dependencies and Integration Points
It is called by `fpu_trig.c`'s `fptan()` after argument reduction and before sign adjustment. It depends on the fixed-point helper assembly and `FPU_settag0()`.

## Risks and Test Signals
Risks include near-`pi/2` inversion blow-up, special rounded complement case handling, correction-term precision, and exponent adjustment mistakes. Test signals include `fptan` near 0, pi/4, close to pi/2 after reduction, and comparisons to hardware/reference results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/poly_tan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/polynom_Xsig.S -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/polynom_Xsig.S

## Purpose
This assembly file evaluates fixed-point polynomials into a 12-byte `Xsig` accumulator using Horner-like multiplication at extended precision.

## Important APIs, Types, and Functions
The exported function is `polynomial_Xsig(Xsig *accum, const unsigned long long *x, const unsigned long long terms[], int n)`. Local stack slots hold a 96-bit sum, 96-bit product accumulator, and overflow flag.

## Control Flow
The function starts from `terms[n]`, then iterates backward through the coefficient table. Each iteration multiplies the current 96-bit sum by the 64-bit fixed-point `x`, compensates for a prior overflow bit, adds the next 64-bit term, records carry overflow for the next iteration, and finally adds the computed 96-bit sum into the caller's accumulator.

## State and Persistence
There is no global state. The caller-provided `accum` is incremented by the polynomial result.

## Dependencies and Integration Points
It depends on `Xsig` word order and i386 calling conventions. It is used by all polynomial approximation C files.

## Risks and Test Signals
Risks include coefficient indexing mistakes, carry propagation errors, unchecked final accumulator overflow, and inline caller assumptions about fixed-point scaling. Test signals include transcendental accuracy tests and standalone comparison of polynomial evaluation against high-precision reference arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/polynom_Xsig.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_add_sub.c -->
# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_add_sub.c

## Purpose
This file implements high-level add/subtract logic for emulator `FPU_REG` operands, handling sign, magnitude ordering, denormals, zeros, infinities, NaNs, destination selection, and x87 rounding/status behavior.

## Important APIs, Types, and Functions
Public functions are `FPU_add(FPU_REG const *b, u_char tagb, int deststnr, int control_w)` and `FPU_sub(int flags, int rm, int control_w)`. Static `add_sub_specials()` handles zeros, denormals, infinities, and invalid infinity-minus-infinity cases. Lower-level arithmetic is delegated to assembly helpers `FPU_u_add()` and `FPU_u_sub()`.

## Control Flow
`FPU_add()` compares tags. For two valid operands, same signs call unsigned add, opposite signs compare exponent/significand magnitude and call unsigned subtract in the correct order or produce signed zero based on rounding mode. Denormals are normalized after `denormal_operand()`. NaNs go through `real_2op_NaN()`. Special values fall into `add_sub_specials()`. `FPU_sub()` selects operands from ST0, ST(rm), or loaded memory data based on `REV`, `DEST_RM`, and `LOADED`; then applies similar magnitude/sign logic for subtraction and writes the chosen destination tag.

## State and Persistence
The file mutates destination FPU registers, tags, signs, and exception/status bits through helper calls. It preserves the original destination sign if a lower-level operation returns an error.

## Dependencies and Integration Points
It is called by register arithmetic handlers, memory arithmetic in `fpu_entry.c`, and other helpers needing addition/subtraction. It depends on constants, exception handling, denormal conversion, register tag helpers, and unsigned assembly arithmetic.

## Risks and Test Signals
Risks include magnitude comparison errors, wrong signed-zero result under `RC_DOWN`, flag misinterpretation for loaded/reversed/destination-register forms, and special-case divergence from x87. Test signals include exhaustive add/sub instruction forms, signed-zero tests under all rounding modes, NaN/infinity/denormal combinations, and comparison to hardware x87.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_add_sub.c -->
