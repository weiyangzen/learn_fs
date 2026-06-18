# Research: subset-b-000789

Grouped research for PowerPC single-step support, string/user-copy helpers, math emulation handlers, and Book3S MMU support in the Ceph client source mirror. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/sstep.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/sstep.c

## Purpose
This file implements PowerPC instruction analysis and software single-step emulation for instructions that cannot simply be executed while tracing, probing, or recovering from faults. It decodes branches, barriers, integer compute operations, load/store forms, cache operations, privileged MSR moves, and optional FP/VMX/VSX/prefixed Power10 forms into `struct instruction_op`, then either updates `pt_regs` directly or performs the required memory/register transfer.

## Important APIs, types, and functions
Externally visible APIs are `analyse_instr`, `emulate_update_regs`, `emulate_loadstore`, `emulate_dcbz`, and `emulate_step`; `analyse_instr` is exported GPL. Important helpers include effective-address builders (`dform_ea`, `dsform_ea`, `dqform_ea`, `xform_ea`, `mlsd_8lsd_ea`), access wrappers (`read_mem`, `write_mem`, `copy_mem_in`, `copy_mem_out`), FP/VMX/VSX transfer helpers, and arithmetic helpers for CR/XER updates.

## Control flow
`analyse_instr` first handles branches, system calls, barriers, and privileged operations, then decodes compute opcodes, and finally maps load/store opcode forms to `MKOP` type/size/update flags. Return `1` means `emulate_update_regs` can finish by editing `pt_regs`; return `0` means a later execution path must perform memory, cache, or privileged state work; return `-1` indicates unsupported feature state such as VSX unavailable. `emulate_step` calls the decoder, dispatches load/store or cache/MSR cases, refuses system calls and RFI-like operations, and advances NIP by instruction length after success.

## State and persistence behavior
The file mutates only live task/register state: `pt_regs` GPRs, CR, XER, LR, CTR, NIP, return MSR, DAR on faults, thread FP/vector save areas, and the PPC32 `TIF_EMULATE_STACK_STORE` flag for unsafe kernel stack update emulation. It performs user/kernel memory accesses through uaccess helpers and exception tables, sets reservations for larx/stcx emulation, and may change cache/TLB-visible state through cache operations and `dcbz`.

## Dependencies and integration points
It depends on `asm/sstep.h` operation encodings, `asm/disassemble.h` prefixed instruction helpers, CPU feature flags, uaccess scoped access APIs, FPU/vector save/restore helpers from assembly files, quadword atomic helpers, cache primitives, kprobe `NOKPROBE_SYMBOL`, and architecture exception return helpers. Consumers include kprobes, uprobes, ptrace/single-step handling, and the local `test_emulate_step` self-test.

## Risks and edge cases
Risk concentrates in instruction decoding parity with ISA revisions, 32-bit truncation, cross-endian loads/stores, update forms with illegal `ra`/`rd` overlap, kernel-mode FP/VMX state access, Power10 prefixed immediate sign extension, and reservation semantics for conditional stores. The code intentionally refuses to step `sc`, `scv`, `rfi`, and MSR writes clearing RI. Any new opcode support needs matching feature gating and test coverage.

## Test signals
`test_emulate_step.c` validates representative load/store, prefixed, FP/vector/VSX, and compute instructions against expected memory/register results. Its compute lane compares emulator output with actual execution via `exec_instr`, while load/store checks observe PASS/SKIP/FAIL messages for architecture and config feature combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/sstep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/string.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/string.S

## Purpose
This assembly file provides generic PowerPC implementations of `strncpy`, `strncmp`, and `memchr` for the kernel.

## Important APIs, types, and functions
It exports `_GLOBAL(strncpy)`, `_GLOBAL(strncmp)`, and `_GLOBAL(memchr)` with `EXPORT_SYMBOL`. The code uses `PPC_LCMPI`, counted loops through CTR, byte load/store update instructions, and `IFETCH_ALIGN_BYTES` alignment.

## Control flow
`strncpy` copies bytes until `n` is exhausted or a NUL is found, then zero-fills the remaining destination bytes. `strncmp` walks both strings until count expires, a NUL is seen, or bytes differ, returning the subtraction result. `memchr` scans a byte range and returns the matching address or zero.

## State and persistence behavior
The functions mutate only caller-provided destination memory for `strncpy`; all state is transient in registers and CTR. There are no exception table entries, so callers must provide valid kernel addresses.

## Dependencies and integration points
These are architecture string primitives linked into the PowerPC kernel and exported for other built-in or modular users.

## Risks and edge cases
Correctness depends on PPC condition-register and CTR branch forms. Boundary cases are zero length, exact NUL at the last byte, zero-fill behavior for `strncpy`, and unsigned byte comparison behavior in `strncmp`.

## Test signals
Signals are ordinary kernel string tests or boot/module users exercising exported symbols; no local self-test exists in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/string.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/string_32.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/string_32.S

## Purpose
This PPC32 assembly file implements `__arch_clear_user`, the low-level user-memory zeroing primitive after access checks have been done by callers.

## Important APIs, types, and functions
It exports `_GLOBAL(__arch_clear_user)`. The implementation uses word stores, byte stores, `dcbz` for complete cache lines, cache-line constants from `asm/cache.h`, and exception table fixups.

## Control flow
For very small ranges it byte-clears directly. Larger ranges align the destination, clear leading words, zero complete cache lines with `dcbz`, then finish trailing words and bytes. Exception fixups return either the original byte count or the remaining bytes after a fault.

## State and persistence behavior
The only persistent mutation is zeroing user memory. On fault, the return value reports uncleared bytes and the function stops through exception-table recovery.

## Dependencies and integration points
It is part of the PPC32 uaccess implementation and depends on prior `access_ok()` validation, cacheability assumptions for `dcbz`, and Linux exception table handling.

## Risks and edge cases
Risks include `dcbz` on non-cacheable memory, exact residual-byte accounting on faults, and alignment arithmetic across cache-line boundaries. The code assumes complete cache lines can safely be cleared with `dcbz`.

## Test signals
Signals come from usercopy/uaccess tests, fault-injection on user mappings, and runtime zeroing behavior in syscalls that clear user buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/string_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/string_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/string_64.S

## Purpose
This PPC64 assembly file implements the 64-bit `__arch_clear_user` primitive for zeroing user memory with optimized short, medium, and cache-line-sized paths.

## Important APIs, types, and functions
The exported `_GLOBAL_TOC(__arch_clear_user)` entry uses helper macros `err1`, `err2`, and `err3` to attach exception table entries to stores. It reads cache block size/log size from `ppc64_caches`.

## Control flow
The routine aligns the destination to 8 bytes, then chooses short clears, 32-byte medium clears, or a long path using `dcbz` after aligning to the data-cache block size. Fixup labels retry with byte stores or return the remaining byte count after a fault.

## State and persistence behavior
It writes zeros to user memory and returns zero on full success or the number of bytes not cleared. It uses register-only bookkeeping and has no durable state.

## Dependencies and integration points
This is used by PPC64 uaccess clear-user paths after access validation. It depends on valid cache metadata offsets, exception tables, and the architecture guarantee that `dcbz` can clear cacheable user memory.

## Risks and edge cases
Fault recovery must preserve correct residual counts across aligned stores, long `dcbz` loops, and fallback byte clearing. Wrong cache block metadata or non-cacheable destinations could make the optimized path unsafe.

## Test signals
Signals include kernel usercopy tests, copy/clear fault-injection, and architecture boot/runtime use of `clear_user`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/string_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/strlen_32.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/strlen_32.S

## Purpose
This PPC32 assembly file implements an optimized `strlen` using word-at-a-time zero-byte detection.

## Important APIs, types, and functions
It exports `_GLOBAL(strlen)`. Constants loaded into registers implement low magic `0x01010101` and high magic `0x80808080`; `cntlzw` identifies the first matching zero byte.

## Control flow
The function aligns back to a word boundary, masks any bytes before the original string as non-zero for misaligned inputs, loops over words until the zero-byte test fires, then computes the byte index of the first NUL and returns the distance from the original pointer.

## State and persistence behavior
No memory is modified. All state is transient in registers.

## Dependencies and integration points
This is the PPC32 kernel `strlen` primitive exported for string users. It depends on valid readable kernel string memory and PPC32 endian-sensitive word layout.

## Risks and edge cases
The algorithm has different least-zero-byte concerns on big-endian versus little-endian systems; the comments document a second test to identify the correct byte. Misaligned input handling must not falsely see bytes before the string as NUL.

## Test signals
Generic kernel string tests, boot-time string operations, and architecture self-tests provide coverage; no local test file accompanies it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/strlen_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/test-code-patching.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/test-code-patching.c

## Purpose
This late-init self-test validates PowerPC text and data patching helpers, especially branch encoding/translation and multi-instruction patching across page boundaries.

## Important APIs, types, and functions
Entry point `test_code_patching` runs `test_branch_iform`, `test_branch_bform`, `test_create_function_call`, `test_translate_branch`, `test_prefixed_patching`, `test_multi_instruction_patching`, and `test_data_patching`. It exercises `create_branch`, `create_cond_branch`, `translate_branch`, `patch_instruction`, `patch_instruction_site`, `patch_instructions`, `patch_uint`, `patch_ulong`, and `ppc_inst_*` helpers.

## Control flow
Each test builds temporary instruction buffers, writes branch or prefixed opcodes, patches code/data, then uses `check()` to emit a line-numbered error on mismatch. Range-limit tests intentionally expect errors for out-of-range or unaligned branch targets. The multi-instruction test allocates pages with `vzalloc` and checks repeated and memcpy patch modes within and across pages.

## State and persistence behavior
The self-test mutates a trampoline function, temporary vmalloc buffers, and stack arrays, then frees vmalloc allocations. It logs failures but does not persist state or abort boot.

## Dependencies and integration points
It integrates with `asm/text-patching.h`, PowerPC instruction wrappers, vmalloc, late initcalls, and prefixed instruction support on PPC64.

## Risks and edge cases
Important edge cases are branch reach limits, absolute versus relative addressing, link-bit preservation, condition flag masking, prefixed 64-bit instruction layout, page-crossing patch writes, and alignment requirements for `patch_ulong`.

## Test signals
Primary signal is absence of `code-patching: test failed at line ...` after the late initcall logs that self-tests are running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/test-code-patching.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/test_emulate_step.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/test_emulate_step.c

## Purpose
This late-init self-test validates the instruction analysis and emulation infrastructure implemented in `sstep.c`.

## Important APIs, types, and functions
It uses `emulate_step`, `analyse_instr`, `emulate_update_regs`, `patch_instruction_site`, and the assembly helper `exec_instr`. Test helpers include `init_pt_regs`, `run_tests_load_store`, `run_tests_compute`, `emulate_compute_instr`, and `execute_compute_instr`. `struct compute_test` describes mnemonic-specific subtests, feature gates, ignored registers, ignored CR/XER flags, and negative tests.

## Control flow
Load/store tests initialize registers and memory, emulate one instruction, and print PASS/SKIP/FAIL. They cover ordinary, prefixed, atomic, FP, Altivec, VSX, and Power10 paired vector forms depending on config and CPU features. Compute tests emulate a table of arithmetic/prefixed cases, patch the same instruction into `exec_instr`, execute it for real, and compare GPRs, LR, XER, and CR unless flags request an ignore.

## State and persistence behavior
The file creates temporary `pt_regs`, stack data, FP/vector unions, and a patched NOP site in `exec_instr`. It logs results only and does not persist state beyond the patched instruction site used during testing.

## Dependencies and integration points
It depends on PPC raw opcode macros, CPU feature detection, `asm/sstep.h`, `asm/text-patching.h`, prefixed instruction wrappers, and `test_emulate_step_exec_instr.S`.

## Risks and edge cases
The test is feature-sensitive and prints SKIP for unsupported ISA/config combinations. Some operations have hardware-defined undefined results, so individual GPR/CR/XER fields can be ignored. The `pstd` success condition uses `stepped == 1 || regs.gpr[5] == a`, which is weaker than the surrounding tests.

## Test signals
Boot logs from `Running instruction emulation self-tests ...` followed by PASS/SKIP/FAIL lines are the primary signal. Compute mismatches include exact expected and actual register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/test_emulate_step.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/test_emulate_step_exec_instr.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/test_emulate_step_exec_instr.S

## Purpose
This assembly helper executes one dynamically patched instruction against a supplied `pt_regs` image so C self-tests can compare real hardware behavior with software emulation.

## Important APIs, types, and functions
It exposes `_GLOBAL(exec_instr)` and a `patch_site` named `patch__exec_instr`. It uses register save/restore macros, `INT_FRAME_SIZE`, `GPR*`, `_LINK`, `_CCR`, and `_XER` offsets from `asm-offsets.h`.

## Control flow
The routine builds a stack frame, saves nonvolatile state, loads LR/CR/XER/GPRs from the input `pt_regs`, runs the patched instruction at an aligned site, then saves resulting registers back. An exception table maps faults at the test instruction to a `-EFAULT` return.

## State and persistence behavior
It mutates the caller-supplied `pt_regs` structure with post-execution state and preserves caller nonvolatile registers. The instruction slot is patched externally by the C test.

## Dependencies and integration points
It is tightly coupled to `test_emulate_step.c`, PowerPC code patching, exception tables, and the kernel `pt_regs` layout.

## Risks and edge cases
The helper intentionally does not restore stack pointer and thread pointer from the test image, so instructions modifying those would not be meaningfully tested. Fault behavior is collapsed to `-EFAULT`.

## Test signals
`execute_compute_instr` returns zero when this helper runs successfully; mismatches are reported by the C comparison loop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/test_emulate_step_exec_instr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/vmx-helper.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/vmx-helper.c

## Purpose
This file provides helpers for entering and leaving kernel Altivec/VMX regions used by optimized usercopy and memory operations.

## Important APIs, types, and functions
Exported usercopy APIs are `enter_vmx_usercopy` and `exit_vmx_usercopy`. Non-exported operation helpers are `enter_vmx_ops` and `exit_vmx_ops`. They call `enable_kernel_altivec`, `disable_kernel_altivec`, `pagefault_disable`, `pagefault_enable`, and preemption helpers.

## Control flow
Enter helpers return zero in interrupt context, otherwise disable preemption and enable kernel Altivec. The usercopy variant also disables page faults so faults fall back to non-VMX copying. Exit helpers disable Altivec and restore pagefault/preemption state; `exit_vmx_usercopy` schedules a near decrementer interrupt if preemption is needed.

## State and persistence behavior
The helpers temporarily change preemption state, page-fault handling, VMX ownership, and possibly the decrementer. They do not persist data.

## Dependencies and integration points
They integrate with PowerPC optimized copy routines, KUAP-sensitive usercopy, kexec copy paths with MMU off, and scheduler/preemption logic.

## Risks and edge cases
Calling schedule while KUAP is unlocked is unsafe, so `exit_vmx_usercopy` uses `preempt_enable_no_resched` and a decrementer nudge. Missing enter/exit pairing would leave VMX or fault/preempt state inconsistent.

## Test signals
Signals come from usercopy/memcpy correctness under VMX-enabled builds, fault fallback behavior, and absence of scheduler/KUAP assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/vmx-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/Makefile

## Purpose
This Makefile selects PowerPC floating-point and SPE math emulation objects based on kernel configuration.

## Important APIs, types, and functions
`math-emu-common-objs` includes dispatcher and hardware-unimplemented helpers. `CONFIG_MATH_EMULATION_FULL` adds full soft-float instruction handlers, loads/stores, FPSCR moves, and conversions. `CONFIG_SPE` adds `math_efp.o`.

## Control flow
Kbuild object lists conditionally add the common, full, and SPE object sets. It disables builtin `fabs` assumptions for `fabs.o` and `math.o`, removes warning flags by default, and re-adds them for extra warning builds.

## State and persistence behavior
No runtime state exists; the file controls build composition and compiler flags.

## Dependencies and integration points
It integrates with arch PowerPC Kconfig options and soft-fp handler sources in the same directory.

## Risks and edge cases
Duplicating `math.o` in full and common lists is intentional through object aggregation but should be watched during Kbuild changes. Compiler builtin optimization for `fabs` must remain disabled.

## Test signals
Build success under `CONFIG_MATH_EMULATION_HW_UNIMPLEMENTED`, `CONFIG_MATH_EMULATION_FULL`, and `CONFIG_SPE` is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fabs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fabs.c

## Purpose
Implements emulated `fabs` by clearing the sign bit of a double-precision FPR image.

## Important APIs, types, and functions
`int fabs(u32 *frD, u32 *frB)` copies the low word and masks `frB[0]` with `0x7fffffff`.

## Control flow
The handler performs a direct bit transform and returns zero; optional DEBUG logging dumps the result.

## State and persistence behavior
It writes the destination FPR image only and does not alter FPSCR.

## Dependencies and integration points
Called by `do_mathemu` for opcode `FABS`, using the thread FPR save area.

## Risks and edge cases
It preserves NaN payloads and the low word by design; endian assumptions follow the FPR word layout used by the math emulator.

## Test signals
Signals are correct sign clearing when `do_mathemu` dispatches `fabs` and no exception flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fabs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fadd.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fadd.c

## Purpose
Implements double-precision floating add for full math emulation.

## Important APIs, types, and functions
`int fadd(void *frD, void *frA, void *frB)` uses `FP_DECL_D`, `FP_UNPACK_DP`, `FP_ADD_D`, and `__FP_PACK_D`.

## Control flow
It unpacks source double values, performs soft-fp addition, packs the result into the destination FPR image, and returns `FP_CUR_EXCEPTIONS`.

## State and persistence behavior
The destination FPR image is updated; exception flags are accumulated in soft-fp state for `math.c` to record in FPSCR.

## Dependencies and integration points
Called by `do_mathemu` for `FADD` and depends on `asm/sfp-machine.h` and `math-emu/double.h`.

## Risks and edge cases
NaN propagation, rounding, overflow, underflow, and inexact behavior rely entirely on soft-fp macros.

## Test signals
Correct result bits and FPSCR exception updates through `do_mathemu` are the expected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fadd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fadds.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fadds.c

## Purpose
Implements single-precision result form of floating add while reading operands from double-format FPR images.

## Important APIs, types, and functions
`int fadds(void *frD, void *frA, void *frB)` uses double soft-fp unpack/add and `__FP_PACK_DS` to round/pack as single precision in the destination image.

## Control flow
Sources are unpacked as doubles, added, optionally debug-logged, then packed with single-precision result semantics.

## State and persistence behavior
It mutates the destination FPR image and returns soft-fp exceptions for FPSCR recording.

## Dependencies and integration points
Dispatched from `do_mathemu` for `FADDS`, requiring `double.h` and `single.h`.

## Risks and edge cases
The extra rounding to single precision is the key risk; exception and NaN semantics must match PowerPC instruction behavior.

## Test signals
Signals are result single precision bits in the FPR image and correct exception propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fadds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fcmpo.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fcmpo.c

## Purpose
Implements ordered double-precision floating compare and condition register update.

## Important APIs, types, and functions
`int fcmpo(u32 *ccr, int crfD, void *frA, void *frB)` uses `FP_CMP_D` and maps compare outcomes to PowerPC CR bits.

## Control flow
It unpacks both operands, raises `EFLAG_VXVC` if either is NaN, computes compare state, writes FPSCR FPCC bits, updates the requested CR field, and returns current exceptions.

## State and persistence behavior
It mutates `__FPU_FPSCR` comparison bits and the caller-provided CCR image.

## Dependencies and integration points
Dispatched by `do_mathemu` for `FCMPO`; exception recording happens later in `math.c`.

## Risks and edge cases
Ordered compare must signal invalid for NaN while preserving condition code mapping for less/greater/equal/unordered.

## Test signals
CR field bits, FPSCR FPCC bits, and invalid exception status are the observable signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fcmpo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fcmpu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fcmpu.c

## Purpose
Implements unordered double-precision floating compare.

## Important APIs, types, and functions
`int fcmpu(u32 *ccr, int crfD, void *frA, void *frB)` uses `FP_CMP_D`, updates FPSCR FPCC bits, and writes a CR field.

## Control flow
Operands are unpacked, compared, mapped through the local CR bit table, and written to FPSCR/CCR. Unlike ordered compare it returns zero and does not explicitly raise invalid on NaN.

## State and persistence behavior
Mutates `__FPU_FPSCR` FPCC bits and `*ccr`; no destination FPR is changed.

## Dependencies and integration points
Dispatched by `do_mathemu` for `FCMPU`.

## Risks and edge cases
NaN/unordered mapping must match PPC unordered compare semantics, with no ordered invalid exception.

## Test signals
Observed CR field and FPCC bits after emulated `fcmpu`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fcmpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fctiw.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fctiw.c

## Purpose
Implements floating convert to signed integer word with current rounding mode.

## Important APIs, types, and functions
`int fctiw(u32 *frD, void *frB)` unpacks a double and uses `FP_TO_INT_D(r, B, 32, 1)`.

## Control flow
The source is unpacked, converted to a 32-bit signed integer, and stored in `frD[1]`; the high word is not explicitly overwritten.

## State and persistence behavior
Only the destination FPR low word is written. Exceptions are tracked in soft-fp state but this function returns zero.

## Dependencies and integration points
Called by `do_mathemu` for `FCTIW`.

## Risks and edge cases
NaN, overflow, and inexact conversion behavior depends on soft-fp; returning zero may hide exception flags unless macros have side effects visible to caller context.

## Test signals
Expected integer word in `frD[1]` and correct FPSCR behavior in integrated tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fctiw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fctiwz.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fctiwz.c

## Purpose
Implements floating convert to signed integer word with rounding toward zero.

## Important APIs, types, and functions
`int fctiwz(u32 *frD, void *frB)` temporarily rewrites the soft-fp FPSCR rounding mode to `FP_RND_ZERO`.

## Control flow
It saves `__FPU_FPSCR`, forces round-to-zero, unpacks and converts the source double to a 32-bit signed integer, stores `frD[1]`, then restores FPSCR.

## State and persistence behavior
Destination FPR word is updated. FPSCR rounding mode is restored after conversion.

## Dependencies and integration points
Dispatched from `do_mathemu` for `FCTIWZ`.

## Risks and edge cases
Exception propagation across the temporary FPSCR save/restore is subtle; conversion edge cases include NaN and out-of-range values.

## Test signals
Signals are truncation behavior independent of current rounding mode and no persistent rounding-mode change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fctiwz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fdiv.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fdiv.c

## Purpose
Implements double-precision floating divide.

## Important APIs, types, and functions
`int fdiv(void *frD, void *frA, void *frB)` uses `FP_DIV_D` and explicitly sets PowerPC invalid/divide-by-zero exception classes.

## Control flow
It unpacks operands, detects `0/0`, `inf/inf`, and nonzero divided by zero, honors enabled divide-by-zero traps by returning before packing, then performs soft-fp division and packs a double result.

## State and persistence behavior
Destination FPR and soft-fp exception state are updated.

## Dependencies and integration points
Called for `FDIV` by `do_mathemu`; `record_exception` converts returned flags to FPSCR status.

## Risks and edge cases
Trap-before-result behavior for divide-by-zero and invalid operation classification must match ISA requirements.

## Test signals
Correct quotient bits plus FPSCR VXZDZ, VXIDI, ZX, and FEX behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fdiv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fdivs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fdivs.c

## Purpose
Implements single-precision result floating divide from double-format FPR operands.

## Important APIs, types, and functions
`int fdivs(void *frD, void *frA, void *frB)` mirrors `fdiv` but packs with `__FP_PACK_DS`.

## Control flow
It handles invalid `0/0` and `inf/inf`, handles divide-by-zero trap checks, performs double soft-fp division, then rounds/packs as single precision.

## State and persistence behavior
Destination FPR image and soft-fp exception flags are updated.

## Dependencies and integration points
Dispatched by `do_mathemu` for `FDIVS`.

## Risks and edge cases
Single-result rounding and exception ordering around divide-by-zero traps are the main risks.

## Test signals
Signals are single-precision quotient representation and correct FPSCR exception bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fdivs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmadd.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmadd.c

## Purpose
Implements double-precision fused-style multiply-add emulation for `frA * frC + frB`.

## Important APIs, types, and functions
`int fmadd(void *frD, void *frA, void *frB, void *frC)` uses soft-fp double declarations, `FP_MUL_D`, `FP_ADD_D`, and `__FP_PACK_D`.

## Control flow
Operands are unpacked, invalid multiply zero-by-infinity is flagged, intermediate `T=A*C` is computed, opposite-sign infinities between `T` and `B` raise `EFLAG_VXISI`, then `T+B` is packed.

## State and persistence behavior
Destination FPR image and exception flags are updated.

## Dependencies and integration points
Called by `do_mathemu` for `FMADD`.

## Risks and edge cases
The implementation uses separate multiply then add macros, so exact fused-rounding semantics depend on soft-fp macro behavior. Invalid infinity cases are explicitly handled.

## Test signals
Result bits and VXIMZ/VXISI exception status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmadd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmadds.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmadds.c

## Purpose
Implements single-precision result multiply-add for `frA * frC + frB`.

## Important APIs, types, and functions
`int fmadds(void *frD, void *frA, void *frB, void *frC)` mirrors `fmadd` and packs through `__FP_PACK_DS`.

## Control flow
It unpacks double operands, flags invalid zero/infinity multiply and infinity subtraction, computes multiply then add, and packs a single-precision result.

## State and persistence behavior
Destination FPR and soft-fp exception flags are updated.

## Dependencies and integration points
Dispatched for opcode `FMADDS`.

## Risks and edge cases
Single-result rounding, NaN propagation, and multiply-add exception ordering are sensitive.

## Test signals
Expected single result and FPSCR invalid/inexact/overflow flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmadds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmr.c

## Purpose
Implements floating move by copying a double-format FPR image.

## Important APIs, types, and functions
`int fmr(u32 *frD, u32 *frB)` copies both 32-bit words from source to destination.

## Control flow
There is no branching except optional DEBUG logging.

## State and persistence behavior
Only the destination FPR image is changed; FPSCR is unaffected.

## Dependencies and integration points
Called by `do_mathemu` for `FMR`.

## Risks and edge cases
It intentionally preserves all payload/sign/exponent bits, including NaNs and signed zeros.

## Test signals
Bit-identical destination FPR after emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmsub.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmsub.c

## Purpose
Implements double-precision multiply-subtract, effectively `frA * frC - frB`.

## Important APIs, types, and functions
`int fmsub(void *frD, void *frA, void *frB, void *frC)` uses double soft-fp math and packs with `__FP_PACK_D`.

## Control flow
It unpacks operands, flags invalid zero/infinity multiply, multiplies `A*C`, flips `B` sign unless `B` is NaN, detects opposite infinity invalid subtraction, adds, and packs the result.

## State and persistence behavior
Destination FPR and exception flags are updated.

## Dependencies and integration points
Dispatched from `math.c` for `FMSUB`.

## Risks and edge cases
NaN sign handling is intentionally skipped for NaN `B`; invalid infinity subtraction and rounding are sensitive.

## Test signals
Result bits and VXIMZ/VXISI exception flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmsub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmsubs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmsubs.c

## Purpose
Implements single-precision result multiply-subtract.

## Important APIs, types, and functions
`int fmsubs(void *frD, void *frA, void *frB, void *frC)` mirrors `fmsub` and packs via `__FP_PACK_DS`.

## Control flow
It computes `A*C`, flips non-NaN `B`, handles invalid special cases, adds, and rounds to a single-precision destination.

## State and persistence behavior
Destination FPR and soft-fp exception state are updated.

## Dependencies and integration points
Dispatched for `FMSUBS`.

## Risks and edge cases
Single rounding, NaN handling, and invalid infinity cases require close ISA parity.

## Test signals
Single result bits and FPSCR exception state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmsubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmul.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmul.c

## Purpose
Implements double-precision floating multiply.

## Important APIs, types, and functions
`int fmul(void *frD, void *frA, void *frB)` uses `FP_MUL_D` and `__FP_PACK_D`.

## Control flow
Sources are unpacked, invalid zero-times-infinity is flagged, soft-fp multiplication is performed, and the result is packed.

## State and persistence behavior
Destination FPR image and exception flags are updated.

## Dependencies and integration points
Dispatched by `math.c` for `FMUL`.

## Risks and edge cases
Invalid operation, NaN propagation, and rounding depend on soft-fp macros plus the explicit zero/infinity check.

## Test signals
Product bits and FPSCR exception status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmuls.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmuls.c

## Purpose
Implements single-precision result floating multiply.

## Important APIs, types, and functions
`int fmuls(void *frD, void *frA, void *frB)` uses double unpack/multiply and `__FP_PACK_DS`.

## Control flow
It unpacks operands, flags invalid zero/infinity multiply, multiplies, then rounds/packs as a single result.

## State and persistence behavior
Destination FPR and soft-fp exception state are updated.

## Dependencies and integration points
Dispatched for `FMULS`.

## Risks and edge cases
Single-precision result rounding and invalid exception flags are the main risks.

## Test signals
Single product representation and FPSCR flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmuls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnabs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnabs.c

## Purpose
Implements negative absolute value by forcing the double sign bit set.

## Important APIs, types, and functions
`int fnabs(u32 *frD, u32 *frB)` ORs `frB[0]` with `0x80000000` and copies `frB[1]`.

## Control flow
Straight-line bit manipulation with optional DEBUG logging.

## State and persistence behavior
Only destination FPR bits are changed; no exception status is generated.

## Dependencies and integration points
Dispatched by `do_mathemu` for `FNABS`.

## Risks and edge cases
Must preserve NaN payload and low word while setting only the sign bit.

## Test signals
Destination is bit-identical to source except sign set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnabs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fneg.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fneg.c

## Purpose
Implements floating negate by toggling the double sign bit.

## Important APIs, types, and functions
`int fneg(u32 *frD, u32 *frB)` XORs the high word with `0x80000000`.

## Control flow
Straight-line bit manipulation and optional DEBUG output.

## State and persistence behavior
Only the destination FPR image is updated; FPSCR is not touched.

## Dependencies and integration points
Dispatched for `FNEG`.

## Risks and edge cases
It must preserve NaN payloads and signed-zero payload bits other than sign.

## Test signals
Destination equals source with sign flipped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fneg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmadd.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmadd.c

## Purpose
Implements double-precision negative multiply-add, negating the non-NaN result of `frA * frC + frB`.

## Important APIs, types, and functions
`int fnmadd(void *frD, void *frA, void *frB, void *frC)` uses soft-fp multiply/add then flips `R_s` when the result is not NaN.

## Control flow
It unpacks operands, handles invalid zero/infinity multiply and infinity subtraction, computes multiply-add, conditionally negates the result sign, and packs a double.

## State and persistence behavior
Destination FPR and exception flags are updated.

## Dependencies and integration points
Dispatched for `FNMADD`.

## Risks and edge cases
Conditional result sign inversion must not alter NaN signs incorrectly; invalid special cases mirror `fmadd`.

## Test signals
Negated result bits and FPSCR invalid flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmadd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmadds.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmadds.c

## Purpose
Implements single-precision result negative multiply-add.

## Important APIs, types, and functions
`int fnmadds(void *frD, void *frA, void *frB, void *frC)` mirrors `fnmadd` and packs with `__FP_PACK_DS`.

## Control flow
The handler computes multiply-add, conditionally flips non-NaN result sign, and rounds/packs as single precision.

## State and persistence behavior
Destination FPR and exception flags are updated.

## Dependencies and integration points
Dispatched for `FNMADDS`.

## Risks and edge cases
Single-result rounding and NaN sign preservation are key edge cases.

## Test signals
Expected single negated result and exception flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmadds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmsub.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmsub.c

## Purpose
Implements double-precision negative multiply-subtract, negating the non-NaN result of `frA * frC - frB`.

## Important APIs, types, and functions
`int fnmsub(void *frD, void *frA, void *frB, void *frC)` uses double soft-fp multiply/add and sign manipulation.

## Control flow
It flags invalid zero/infinity multiply, multiplies `A*C`, flips non-NaN `B`, checks invalid infinity subtraction, adds, conditionally negates non-NaN result, and packs a double.

## State and persistence behavior
Destination FPR and exception flags are updated.

## Dependencies and integration points
Dispatched by `do_mathemu` for `FNMSUB`.

## Risks and edge cases
Correct ordering of B sign flip, invalid infinity checks, and final sign inversion is critical.

## Test signals
Result sign/value and VXIMZ/VXISI flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmsub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmsubs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmsubs.c

## Purpose
Implements single-precision result negative multiply-subtract.

## Important APIs, types, and functions
`int fnmsubs(void *frD, void *frA, void *frB, void *frC)` is the single-result counterpart to `fnmsub`.

## Control flow
It performs multiply, subtract via sign flip, invalid checks, final non-NaN sign inversion, and single-result packing.

## State and persistence behavior
Destination FPR image and soft-fp exception flags are updated.

## Dependencies and integration points
Dispatched for `FNMSUBS`.

## Risks and edge cases
Single rounding, NaN sign behavior, and invalid special-case ordering require careful parity with ISA semantics.

## Test signals
Single result bits and FPSCR exception state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmsubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fre.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fre.c

## Purpose
Provides a stub for `fre`, the floating reciprocal estimate instruction.

## Important APIs, types, and functions
`int fre(void *frD, void *frB)` returns zero without modifying operands.

## Control flow
The function is a no-op.

## State and persistence behavior
No state is changed.

## Dependencies and integration points
It is included in common math emulation objects for hardware-unimplemented instruction handling and dispatched by `math.c` for `FRE`.

## Risks and edge cases
As a stub, it does not produce a reciprocal estimate; correctness depends on configuration/dispatch using it only where this behavior is acceptable or later code handles it.

## Test signals
Build/link success is the main local signal; architectural correctness would require exercising `fre`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fre.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fres.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fres.c

## Purpose
Provides a stub for `fres`, the single-precision reciprocal estimate instruction.

## Important APIs, types, and functions
`int fres(void *frD, void *frB)` returns zero.

## Control flow
No operation is performed.

## State and persistence behavior
No FPR or FPSCR state is changed.

## Dependencies and integration points
Optionally included for full math emulation and dispatched for `FRES`.

## Risks and edge cases
The stub does not emulate estimate semantics, so it is only safe if callers tolerate no-op behavior or this path is not expected on target systems.

## Test signals
Build/link coverage; ISA-level tests would expose the missing result update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fres.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/frsp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/frsp.c

## Purpose
Implements `frsp`, rounding a double-format FPR value to single precision and storing it back as a double-format image.

## Important APIs, types, and functions
`int frsp(void *frD, void *frB)` uses double unpack, conversion to single (`FP_CONV`), canonical packing, raw single packing, and re-unpacking/packing to double layout.

## Control flow
The handler converts the input double to a single representation, handles exceptions/traps, then stores the rounded result in the destination FPR image.

## State and persistence behavior
Destination FPR is updated and soft-fp exceptions are returned for FPSCR recording.

## Dependencies and integration points
Dispatched for `FRSP`, requiring `double.h` and `single.h`.

## Risks and edge cases
NaN, overflow, inexact, and trap-enabled exception cases need correct pack-suppression semantics.

## Test signals
Result equals single-rounded value in FPR format and FPSCR exception bits reflect conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/frsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/frsqrte.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/frsqrte.c

## Purpose
Provides a stub for double reciprocal square-root estimate.

## Important APIs, types, and functions
`int frsqrte(void *frD, void *frB)` returns zero without updating the destination.

## Control flow
No operation is performed.

## State and persistence behavior
No state is changed.

## Dependencies and integration points
Dispatched for `FRSQRTE` from `math.c`.

## Risks and edge cases
The estimate result is not implemented; systems relying on software emulation of this instruction would observe an unchanged destination.

## Test signals
Build/link success only; instruction-level tests would identify functional absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/frsqrte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/frsqrtes.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/frsqrtes.c

## Purpose
Provides a stub for single reciprocal square-root estimate.

## Important APIs, types, and functions
`int frsqrtes(void *frD, void *frB)` returns zero.

## Control flow
The function is a no-op.

## State and persistence behavior
No state is changed.

## Dependencies and integration points
Included in common math emulation objects and dispatched for `FRSQRTES`.

## Risks and edge cases
It lacks architectural estimate behavior, so correctness depends on this path being unused or acceptable for the configured target.

## Test signals
Build/link coverage; functional tests for `frsqrtes` would fail to see a result change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/frsqrtes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsel.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsel.c

## Purpose
Implements `fsel`, selecting between two floating operands based on the sign/class of `frA`.

## Important APIs, types, and functions
`int fsel(void *frD, void *frA, void *frB, void *frC)` unpacks `frA` and copies either `frC` or `frB` into `frD`.

## Control flow
The selector operand is unpacked. If `A` is NaN or non-negative, `frC` is chosen; otherwise `frB` is chosen. The selected double image is copied directly.

## State and persistence behavior
Destination FPR image is replaced; FPSCR exceptions are not generated.

## Dependencies and integration points
Dispatched for `FSEL`.

## Risks and edge cases
NaN selection behavior and signed-zero treatment must match PowerPC `fsel` semantics.

## Test signals
Destination equals the expected source operand for negative, zero, positive, and NaN selectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsqrt.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsqrt.c

## Purpose
Implements double-precision square root.

## Important APIs, types, and functions
`int fsqrt(void *frD, void *frB)` uses `FP_SQRT_D` and `__FP_PACK_D`.

## Control flow
It unpacks the source double, flags `EFLAG_VXSQRT` for negative nonzero/non-NaN inputs, computes the soft-fp square root, and packs the result.

## State and persistence behavior
Destination FPR and soft-fp exception flags are updated.

## Dependencies and integration points
Dispatched for `FSQRT`.

## Risks and edge cases
Negative zero, negative finite, NaN, and trap-enabled invalid cases require exact classification.

## Test signals
Square-root result and FPSCR invalid square-root flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsqrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsqrts.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsqrts.c

## Purpose
Implements single-precision result square root from a double-format FPR source.

## Important APIs, types, and functions
`int fsqrts(void *frD, void *frB)` mirrors `fsqrt` but packs with `__FP_PACK_DS`.

## Control flow
The handler unpacks, flags invalid negative square-root inputs, computes square root, and rounds/packs as single precision.

## State and persistence behavior
Destination FPR and exception flags are updated.

## Dependencies and integration points
Dispatched for `FSQRTS`.

## Risks and edge cases
Single-result rounding and negative input classification are the main concerns.

## Test signals
Single sqrt result and VXSQRT/FEX behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsqrts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsub.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsub.c

## Purpose
Implements double-precision floating subtract.

## Important APIs, types, and functions
`int fsub(void *frD, void *frA, void *frB)` uses `FP_SUB_D` and `__FP_PACK_D`.

## Control flow
Source operands are unpacked, soft-fp subtraction is performed, and the double result is packed.

## State and persistence behavior
Destination FPR image and soft-fp exception state are updated.

## Dependencies and integration points
Dispatched for `FSUB`.

## Risks and edge cases
Rounding, cancellation, NaNs, infinities, underflow, and inexact status depend on soft-fp macros.

## Test signals
Subtract result and FPSCR exception status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsubs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsubs.c

## Purpose
Implements single-precision result floating subtract.

## Important APIs, types, and functions
`int fsubs(void *frD, void *frA, void *frB)` uses double unpack/subtract and `__FP_PACK_DS`.

## Control flow
It unpacks source FPRs, subtracts through soft-fp, then rounds/packs to single precision.

## State and persistence behavior
Destination FPR and exception flags are updated.

## Dependencies and integration points
Dispatched for `FSUBS`.

## Risks and edge cases
Single-result rounding, cancellation, signed zero, NaN propagation, and exceptions.

## Test signals
Expected single subtract result and FPSCR flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/lfd.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/lfd.c

## Purpose
Implements emulated double-precision floating load from user memory.

## Important APIs, types, and functions
`int lfd(void *frD, void *ea)` calls `copy_from_user(frD, ea, sizeof(double))`.

## Control flow
The function copies eight bytes from the effective address into the destination FPR image or returns `-EFAULT`.

## State and persistence behavior
Destination FPR image is updated on success; no FPSCR state changes.

## Dependencies and integration points
Used by `do_mathemu` for D-form and X-form `lfd` instructions.

## Risks and edge cases
It relies on caller-computed effective addresses and uaccess fault handling; endian representation is raw memory order.

## Test signals
Correct FPR bytes after load and `-EFAULT` on inaccessible user addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/lfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/lfs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/lfs.c

## Purpose
Implements emulated single-precision floating load, widening the loaded float into a double-format FPR image.

## Important APIs, types, and functions
`int lfs(void *frD, void *ea)` copies a `float` from user memory, unpacks it with `FP_UNPACK_S`, converts with `FP_CONV(D, S, ...)`, and packs a double.

## Control flow
It reads user memory, converts single to double using soft-fp, preserves NaN exponent handling through a raw pack path, and returns zero or `-EFAULT`.

## State and persistence behavior
Destination FPR image is updated; FPSCR exception return is zero.

## Dependencies and integration points
Dispatched for `LFS`, `LFSU`, `LFSX`, and `LFSUX` by `math.c`.

## Risks and edge cases
NaN conversion handling is special-cased; user access faults must not update a partial destination.

## Test signals
Correct double-format FPR after loading a float and fault return on bad addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/lfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/math.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/math.c

## Purpose
This is the main classic FPU math-emulation dispatcher for PowerPC. It fetches a faulting instruction, decodes it, calls the appropriate operation handler, updates FPSCR/CR/register state, and advances NIP.

## Important APIs, types, and functions
Externally visible entry point is `int do_mathemu(struct pt_regs *regs)`. Static `record_exception` maps soft-fp exception flags to FPSCR status, summary, and enabled-exception bits. The file declares handler prototypes through `FLOATFUNC` and defines opcode/type constants for D, DU, X, XE, XEU, arithmetic, compare, and FPSCR operations.

## Control flow
`do_mathemu` fetches the 32-bit instruction from user NIP, selects a function pointer and operand layout by primary/minor opcode, computes FPR and effective-address operands, flushes live FP state to `thread_struct`, invokes the handler, mirrors FPSCR condition bits to CR1 when Rc is set, records exceptions, handles update-form base register writes, and advances NIP by four. Illegal or unknown opcodes return `-ENOSYS`; user fetch faults return `-EFAULT`; enabled FP exceptions return `1`.

## State and persistence behavior
It mutates `current->thread.TS_FPR`, `regs->ccr`, update-form GPRs, `regs->nip`, and global per-thread soft-fp FPSCR state. Memory load/store handlers can copy to/from user addresses.

## Dependencies and integration points
It integrates with exception handling for unavailable/unimplemented FP instructions, soft-fp headers, `asm/sfp-machine.h`, `flush_fp_to_thread`, and all per-instruction handler files in this directory.

## Risks and edge cases
Risks include exact opcode decoding, update-form legality, using raw `void *` operands for integer immediates, exception enable semantics, and keeping hardware FP state coherent with saved thread state. It only handles 32-bit classic FPU instructions, not prefixed or VSX forms.

## Test signals
Signals are successful emulation of FP unavailable traps, correct NIP advancement, expected FPSCR/CR state, and `-ENOSYS` for illegal instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/math.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/math_efp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/math_efp.c

## Purpose
This file emulates e500 SPE embedded floating-point instructions to provide IEEE-754 compliant behavior and rounding fixes.

## Important APIs, types, and functions
Public handlers are `do_spe_mathemu(struct pt_regs *regs)` and `speround_handler(struct pt_regs *regs)`. `insn_type` classifies SPE opcodes into operand layouts. `spe_mathemu_init` detects e500 CPU A005 erratum revisions. Important state includes `current->thread.evr`, GPR halves, `SPEFSCR`, `spefscr_last`, and `fpexc_mode`.

## Control flow
`do_spe_mathemu` fetches the instruction, validates EFAPU primary opcode, decodes function/source class, gathers operand halves from EVR/GPR pairs, loads SPEFSCR into soft-fp FPSCR, dispatches SPFP, DPFP, or vector single operations, updates CR fields for compares, writes destination EVR/GPR, updates sticky exception state, and returns `1` when enabled software FP exceptions should trap. Illegal opcodes may reissue on affected e500 erratum CPUs. `speround_handler` adjusts inexact results for round-to-plus-infinity or round-to-minus-infinity modes when hardware handled only nearest/zero.

## State and persistence behavior
It mutates GPRs, EVRs, CR fields, SPEFSCR SPR, per-thread sticky SPEFSCR shadow, and NIP indirectly via caller behavior. It does not write user memory.

## Dependencies and integration points
Integrated with BookE/e500 SPE exception handling, Linux `prctl` FP exception modes, soft-fp single/double macros, PVR detection, and module init.

## Risks and edge cases
Edge cases include vector lane exception aggregation, sign recovery for zero conversion results, NaN invalid handling, sticky bit preservation, e500 A005 reissue behavior, and correct trapping under `PR_FP_EXC_SW_ENABLE`.

## Test signals
Signals include SPE instruction trap handling returning 0/1/-ENOSYS appropriately, correct EVR/GPR result halves, SPEFSCR sticky bits, and rounding-mode behavior for inexact results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/math_efp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mcrfs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mcrfs.c

## Purpose
Implements move from FPSCR field to condition register field.

## Important APIs, types, and functions
`int mcrfs(u32 *ccr, u32 crfD, u32 crfS)` extracts a 4-bit FPSCR field, clears selected FPSCR exception bits, and writes a CR field.

## Control flow
It computes the FPSCR source mask, uses a special clear mask for field zero, moves the field to `*ccr`, and returns zero.

## State and persistence behavior
Mutates `__FPU_FPSCR` and caller CCR image.

## Dependencies and integration points
Dispatched by `do_mathemu` for `MCRFS`.

## Risks and edge cases
Source field zero clearing differs from other fields; CR field bit placement must be correct.

## Test signals
CR destination field matches source FPSCR field and expected sticky bits are cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mcrfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mffs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mffs.c

## Purpose
Implements move from FPSCR to floating register.

## Important APIs, types, and functions
`int mffs(u32 *frD)` writes `__FPU_FPSCR` into `frD[1]`.

## Control flow
Straight-line copy with optional DEBUG logging.

## State and persistence behavior
Destination FPR low word is updated; FPSCR is not changed.

## Dependencies and integration points
Dispatched by `do_mathemu` for `MFFS`.

## Risks and edge cases
Upper word handling is not explicit; the emulator expects the FPSCR value in the low word of the FPR image.

## Test signals
Destination FPR contains the current FPSCR low word.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mffs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsb0.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsb0.c

## Purpose
Implements clear FPSCR bit instruction.

## Important APIs, types, and functions
`int mtfsb0(int crbD)` clears bit `31-crbD` in `__FPU_FPSCR` except for reserved bits 1 and 2.

## Control flow
One conditional mask operation plus optional DEBUG logging.

## State and persistence behavior
Mutates `__FPU_FPSCR`.

## Dependencies and integration points
Dispatched for `MTFSB0`.

## Risks and edge cases
Reserved bit protection for bits 1 and 2 must match architecture semantics.

## Test signals
Expected FPSCR bit clears and reserved bits unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsb0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsb1.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsb1.c

## Purpose
Implements set FPSCR bit instruction.

## Important APIs, types, and functions
`int mtfsb1(int crbD)` sets bit `31-crbD` in `__FPU_FPSCR` except for reserved bits 1 and 2.

## Control flow
One conditional OR operation plus optional DEBUG logging.

## State and persistence behavior
Mutates `__FPU_FPSCR`.

## Dependencies and integration points
Dispatched for `MTFSB1`.

## Risks and edge cases
Reserved bit handling and later FEX/VX summary recomputation are external to this file.

## Test signals
Expected FPSCR bit sets and reserved bits unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsb1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsf.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsf.c

## Purpose
Implements move to FPSCR fields from an FPR image.

## Important APIs, types, and functions
`int mtfsf(unsigned int FM, u32 *frB)` computes a field mask from `FM`, merges `frB[1]` into `__FPU_FPSCR`, clears summary bits, and recomputes VX/FEX summaries.

## Control flow
Fast paths handle `FM == 1` and `FM == 0xff`; otherwise the mask is expanded nibble-by-nibble. The resulting FPSCR preserves unmasked fields and derives summary bits from detailed exception/status and enable bits.

## State and persistence behavior
Mutates `__FPU_FPSCR`.

## Dependencies and integration points
Dispatched for `MTFSF`, with exception summary semantics consumed by later FP emulation.

## Risks and edge cases
Mask expansion and summary-bit recomputation are subtle; wrong bit order changes user-visible FPSCR fields.

## Test signals
Field-selective FPSCR updates, VX/FEX summary correctness, and reserved bit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsfi.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsfi.c

## Purpose
Implements move immediate to FPSCR field.

## Important APIs, types, and functions
`int mtfsfi(unsigned int crfD, unsigned int IMM)` writes a 4-bit immediate into one FPSCR field, using a special mask for field zero.

## Control flow
It clears the selected field bits and ORs in `IMM & 0xf` at the correct field position.

## State and persistence behavior
Mutates `__FPU_FPSCR`.

## Dependencies and integration points
Dispatched by `do_mathemu` for `MTFSFI`.

## Risks and edge cases
Field zero masking differs from the general `0xf` mask.

## Test signals
FPSCR selected field equals immediate while other fields remain unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mtfsfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfd.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfd.c

## Purpose
Implements emulated double-precision floating store to user memory.

## Important APIs, types, and functions
`int stfd(void *frS, void *ea)` calls `copy_to_user(ea, frS, sizeof(double))`.

## Control flow
It copies eight bytes from the source FPR image to the effective user address or returns `-EFAULT`.

## State and persistence behavior
Mutates user memory on success; no FPSCR state changes.

## Dependencies and integration points
Dispatched for `STFD`, `STFDU`, `STFDX`, and `STFDUX`.

## Risks and edge cases
Fault handling and update-form base register writes are handled by `math.c`; raw endian memory representation is preserved.

## Test signals
Correct user memory bytes and `-EFAULT` on invalid destinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfiwx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfiwx.c

## Purpose
Implements store floating-point as integer word indexed.

## Important APIs, types, and functions
`int stfiwx(u32 *frS, void *ea)` copies `frS[1]` to user memory.

## Control flow
The handler performs a 32-bit `copy_to_user` and returns zero or `-EFAULT`.

## State and persistence behavior
Mutates user memory only.

## Dependencies and integration points
Dispatched by `do_mathemu` for `STFIWX`.

## Risks and edge cases
Correct low-word selection depends on the emulator FPR image layout.

## Test signals
User memory receives the expected integer word from the FPR image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfiwx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfs.c

## Purpose
Implements emulated single-precision floating store, narrowing a double-format FPR image to a float in user memory.

## Important APIs, types, and functions
`int stfs(void *frS, void *ea)` uses `FP_UNPACK_DP`, `FP_CONV(S, D, ...)`, `_FP_PACK_CANONICAL`, `_FP_PACK_RAW_1_P`, and `copy_to_user`.

## Control flow
The source double is converted to single precision. If there are no trapping exceptions, the raw float is copied to user memory; otherwise the store is suppressed and exception flags are returned.

## State and persistence behavior
User memory is changed on successful non-trapping conversion. FPSCR changes are recorded by caller from returned exceptions.

## Dependencies and integration points
Dispatched for `STFS`, `STFSU`, `STFSX`, and `STFSUX`.

## Risks and edge cases
Trap-enabled exceptions must prevent memory writes. Narrowing conversion, NaN packing, and user faults are key risks.

## Test signals
Expected float bytes in user memory and correct exception/fault returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/stfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/udivmodti4.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/udivmodti4.c

## Purpose
Implements a two-word unsigned division/remainder helper for soft-fp 128-bit style arithmetic.

## Important APIs, types, and functions
`void _fp_udivmodti4(_FP_W_TYPE q[2], _FP_W_TYPE r[2], _FP_W_TYPE n1, _FP_W_TYPE n0, _FP_W_TYPE d1, _FP_W_TYPE d0)` computes quotient and remainder using soft-fp word macros such as `udiv_qrnnd`, `umul_ppmm`, `sub_ddmmss`, and `__FP_CLZ`.

## Control flow
The routine handles one-word denominators separately from two-word denominators, normalizes when required, computes high/low quotient words, corrects overestimates, and writes quotient/remainder arrays. A zero divisor intentionally triggers division by zero.

## State and persistence behavior
Only the output arrays are written; all arithmetic state is local.

## Dependencies and integration points
Used by soft-fp support code for wide division where compiler runtime helpers are unavailable or unsuitable in-kernel.

## Risks and edge cases
Normalization shift counts, quotient correction, zero denominator behavior, and word-size assumptions are critical. The code derives from libgcc and must stay aligned with soft-fp word macro semantics.

## Test signals
Soft-fp operations requiring wide division should produce exact quotient/remainder bits across normalized and unnormalized cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/udivmodti4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/Makefile

## Purpose
This Makefile selects the architecture-specific PowerPC memory-management objects.

## Important APIs, types, and functions
The base `obj-y` list builds faults, memory init, page tables, access helpers, page attributes, ioremap, context, DRMEM, and cache flush support. Conditional directories include `nohash/`, `book3s32/`, `book3s64/`, `ptdump/`, and `kasan/`.

## Control flow
Kbuild adds objects by `BITS` and feature configs such as `CONFIG_PPC_MMU_NOHASH`, `CONFIG_PPC_BOOK3S_32`, `CONFIG_PPC_BOOK3S_64`, NUMA, hugetlb, noncoherent cache, coprocessor base, PTDUMP, and KASAN.

## State and persistence behavior
No runtime state exists; it controls build composition.

## Dependencies and integration points
It is the top-level PowerPC MM build integration point under `arch/powerpc/mm`.

## Risks and edge cases
Incorrect conditional selection can omit platform-critical MMU code or include incompatible hash/nohash implementations.

## Test signals
Build matrix success across 32/64-bit, Book3S, nohash, KASAN, NUMA, and hugetlb configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/Makefile

## Purpose
This Makefile selects 32-bit Book3S MMU objects.

## Important APIs, types, and functions
It always builds `mmu.o` and `mmu_context.o`, adds `nohash_low.o` for 603, `hash_low.o` and `tlb.o` for 604-style hash MMUs, and `kuap.o` when KUAP is enabled.

## Control flow
Kbuild conditionals map CPU/MMU feature configs to assembly support files. KASAN builds disable sanitization for `mmu.o` and add `DISABLE_BRANCH_PROFILING`.

## State and persistence behavior
No runtime state; this is build metadata.

## Dependencies and integration points
It integrates Book3S32 hash/nohash MMU code into the PowerPC MM build.

## Risks and edge cases
Instrumentation is deliberately suppressed for early/low-level MMU code; changing that can break boot or real-mode paths.

## Test signals
Successful builds for 603, 604, KUAP, and KASAN combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/hash_low.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/hash_low.S

## Purpose
This assembly file implements low-level 32-bit Book3S hash MMU operations: handling hash misses, inserting HPTEs, and flushing hash table entries.

## Important APIs, types, and functions
It defines `_GLOBAL(hash_page)`, `_GLOBAL(add_hash_page)`, `_GLOBAL(create_hpte)`, and `_GLOBAL(flush_hash_pages)`, exporting `flush_hash_pages`. It uses patch sites `patch__hash_page_*` and `patch__flush_hash_*`, `_PAGE_HASHPTE`, `_PAGE_ACCESSED`, `_PAGE_DIRTY`, PTE flags, VSID hashing, `mmu_hash_lock`, `tlbie`, and `TLBSYNC`.

## Control flow
`hash_page` runs on ISI/DSI hash misses, locates the Linux PTE, verifies requested permissions (including KUAP restrictions), atomically sets accessed/dirty/has-HPTE bits, computes the segment VSID, inserts an HPTE, releases the SMP hash lock, and returns through `fast_hash_page_return`. `add_hash_page` preloads an HPTE for a PTE by disabling interrupts/data translation, taking the hash lock, setting `_PAGE_HASHPTE`, and calling `create_hpte`. `create_hpte` converts Linux PTE flags to PPC HPTE words, searches primary and secondary PTEGs for matching or empty slots, and evicts a rotating primary slot if full. `flush_hash_pages` clears `_PAGE_HASHPTE`, invalidates matching primary/secondary HPTEs, executes `tlbie`, and handles ranges.

## State and persistence behavior
It mutates Linux PTE flags, the hardware hash table, TLB state, `next_slot`, and `mmu_hash_lock`. It temporarily disables interrupts and data relocation in selected paths.

## Dependencies and integration points
Called from exception handlers, `book3s32/mmu.c` hash preloading, and `book3s32/tlb.c` flush wrappers. It depends on early/runtime hash table patching by `MMU_init_hw_patch`.

## Risks and edge cases
Risks include SMP races between PTE and HPTE updates, stale TLB entries, 64-bit PTE upper-word dependencies, KUAP permission filtering, hash table full eviction, and correctness while data relocation is disabled.

## Test signals
Signals include successful page fault resolution, correct permission faults, stable SMP operation, TLB flush correctness, and absence of hash-table corruption under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/hash_low.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/kuap.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/kuap.c

## Purpose
This file enables or disables Kernel Userspace Access Protection for Book3S32 segment registers.

## Important APIs, types, and functions
`void setup_kuap(bool disabled)` updates segment register KS state and CPU MMU feature flags.

## Control flow
When KUAP is enabled, it sets `SR_KS` in current user segments, synchronizes with `isync`, and updates `init_mm.context.sr0` and `current->thread.sr0`. On non-boot CPUs it returns after local setup; on the boot CPU it either clears `MMU_FTR_KUAP` when disabled or logs activation.

## State and persistence behavior
It mutates segment registers, initial/current thread segment context, and `cur_cpu_spec->mmu_features`.

## Dependencies and integration points
Used during PowerPC KUAP setup and interacts with hash fault permission filtering in `hash_low.S`.

## Risks and edge cases
Segment register synchronization is required after updates. Boot CPU versus secondary CPU behavior must avoid global feature churn on secondary bring-up.

## Test signals
Signals include activation log, enforced blocked kernel user access when KUAP is enabled, and no KUAP feature when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/kuap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/mmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/mmu.c

## Purpose
This file initializes and manages Book3S32 block address translations and hash table setup.

## Important APIs, types, and functions
Key APIs include `v_block_mapped`, `p_block_mapped`, `find_free_bat`, `bat_block_size`, `mmu_mapin_ram`, `mmu_mark_initmem_nx`, `mmu_mark_rodata_ro`, `setbat`, `__update_mmu_cache`, `MMU_init_hw`, `MMU_init_hw_patch`, `setup_initial_memory_limit`, and `print_system_hash_info`. Important state includes `early_hash`, `Hash`, `Hash_size`, `Hash_mask`, `_SDR1`, `BATS`, `bat_addrs`, and `mmu_hash_lock`.

## Control flow
Boot starts with an early hash table, maps kernel RAM with BATs where possible, later allocates a suitably sized hash table from memblock, computes SDR1/hash masks, and patches low-level assembly hash helpers with actual table base/mask values. Runtime page-fault completion calls `__update_mmu_cache`, which preloads HPTEs only for young user PTEs following instruction/data storage faults.

## State and persistence behavior
It persists BAT register images, BAT range metadata, SDR1/hash metadata, and assembly patch constants. It also changes segment NX bits and BAT permissions for strict RWX/RODATA transitions.

## Dependencies and integration points
Integrated with memblock, machine progress callbacks, text patching, `hash_low.S`, TLB/cache behavior, strict kernel RWX, debug pagealloc/KFENCE, and execmem module ranges.

## Risks and edge cases
BAT block sizing must honor alignment and 128 KiB minimum. Strict RWX mapping can leave some RW data executable if BAT granularity is too coarse. Hash table patching must happen after no KASAN instrumentation can be triggered.

## Test signals
Boot logs for hash size, stable early boot mapping, successful page faults/hash preloads, strict RWX behavior, and correct block mapping lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/mmu_context.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/mmu_context.c

## Purpose
This file manages Book3S32 address-space context IDs and segment register switching.

## Important APIs, types, and functions
It defines `abatron_pteptrs`, `__init_new_context`, `init_new_context`, `__destroy_context`, `destroy_context`, `mmu_context_init`, and `switch_mmu_context`. Static state is `next_mmu_context` and `context_map`.

## Control flow
Context allocation scans a bitmap of 32768 possible contexts, reserves context zero for the kernel, assigns `mm->context.id` and `sr0`, sets KUEP/KUAP segment bits, and clears context bits on destroy under preempt disable. Switching updates user segment registers, optional BDI debug PTE pointers, SDR1 for nohash CPUs, and wraps with barriers/isync.

## State and persistence behavior
It persists context allocation bitmap state, each mm's context ID and segment base, debug PTE pointers, and SDR1 on nohash context switches.

## Dependencies and integration points
Integrated with fork/exec/mm teardown, scheduler context switch, segment register helpers, KUAP/KUEP, BDI debug support, and nohash/hash MMU feature detection.

## Risks and edge cases
Context bitmap exhaustion/wrap, missing preempt disable on destroy, invalid `NO_CONTEXT` switches, and segment-register synchronization are key risks.

## Test signals
Stable process creation/destruction, no context ID leaks, correct per-process address spaces, and no panic in `switch_mmu_context`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/mmu_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/nohash_low.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/nohash_low.S

## Purpose
This assembly file implements low-level TLB invalidation for 603/603e nohash Book3S32 CPUs.

## Important APIs, types, and functions
It defines `_GLOBAL(_tlbie)` on SMP and `_GLOBAL(_tlbia)` for full TLB invalidation. It uses `mmu_hash_lock`, `tlbie`, `TLBSYNC`, MSR EE/DR manipulation, and `TASK_CPU`.

## Control flow
`_tlbie` takes a physical lock with data relocation disabled, invalidates one address, synchronizes, releases the lock, restores MSR, and returns. `_tlbia` invalidates 32 page-sized entries starting at `KERNELBASE`, with SMP locking/synchronization when configured.

## State and persistence behavior
It changes hardware TLB state and temporarily changes MSR EE/DR. On SMP it mutates `mmu_hash_lock`.

## Dependencies and integration points
Called by nohash TLB flush code for 603-style processors.

## Risks and edge cases
The code must run safely with data relocation disabled and avoid SMP races. Full invalidation count/address range is processor-specific.

## Test signals
Stable TLB shootdowns, no stale translations after unmap, and correct SMP locking behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/nohash_low.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/tlb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/tlb.c

## Purpose
This file provides C TLB/hash flush wrappers for Book3S32 hash MMUs.

## Important APIs, types, and functions
Exported functions are `hash__flush_range`, `hash__flush_tlb_mm`, `hash__flush_tlb_page`, and `hash__flush_gather`.

## Control flow
Range flush aligns start/end to pages, walks PMD spans, and calls `flush_hash_pages` for present PMDs. Full-mm flush iterates VMAs. Page flush picks the VMA mm or `init_mm` for kernel addresses. Gather flush chooses full-mm/range based on `mmu_gather` flags.

## State and persistence behavior
It does not directly mutate PTEs; it delegates HPTE/TLB state mutation to `flush_hash_pages`.

## Dependencies and integration points
Integrated with Linux TLB gather/unmap paths, VMA iteration, PMD lookup, and `hash_low.S`.

## Risks and edge cases
Correct end-address rounding, VMA iteration locking assumptions, kernel versus user mm selection, and PMD count calculation are important.

## Test signals
No stale mappings after unmap/mprotect/exit, correct full-mm flush during dup/exit, and stable hash-table state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/Makefile

## Purpose
This Makefile selects 64-bit Book3S MMU objects for hash, radix, hugepage, IOMMU, and memory protection-key support.

## Important APIs, types, and functions
Always-built objects are `mmu_context.o`, `pgtable.o`, and `trace.o`. Hash MMU builds add hash page table, utilities, TLB, SLB, slice, native/hash page-size helpers, hugepage, and subpage protection objects. Radix builds add radix page table/TLB/hugepage objects.

## Control flow
Kbuild conditionally adds objects based on `CONFIG_PPC_64S_HASH_MMU`, page size, transparent hugepage, radix MMU, hugetlb, SPAPR TCE IOMMU, and pkeys. It disables ftrace/KASAN/KCOV instrumentation for sensitive low-level paths.

## State and persistence behavior
No runtime state; controls build composition and instrumentation.

## Dependencies and integration points
Top-level integration for Book3S64 hash/radix MM subsystems.

## Risks and edge cases
Instrumentation exclusions protect real-mode/SLB paths; removing them can break low-level faults. Wrong page-size object selection can break hash insertion.

## Test signals
Build success across hash/radix, 4K/64K, THP, hugetlb, pkeys, and KASAN/KCOV combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_4k.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_4k.c

## Purpose
This file implements 4 KiB hash page insertion/update for 64-bit Book3S hash MMUs.

## Important APIs, types, and functions
`int __hash_page_4K(...)` is the central function. It uses `pte_xchg`, `check_pte_access`, `htab_convert_pte_flags`, `__real_pte`, `hash_page_do_lazy_icache`, `hpt_vpn`, `pte_get_hash_gslot`, `mmu_hash_ops.hpte_updatepp`, `hpt_hash`, `mmu_hash_ops.hpte_insert`, `mmu_hash_ops.hpte_remove`, `pte_set_hidx`, `stress_hpt`, and `hpt_do_stress`.

## Control flow
The function atomically locks the Linux PTE with `H_PAGE_BUSY`, verifies access permissions, sets accessed/dirty as needed, converts PTE flags to HPTE flags, and tries to update an existing HPTE if `H_PAGE_HASHPTE` is set. If no valid HPTE remains, it computes VPN/hash, tries primary insertion, then secondary insertion, evicts a random-ish primary/secondary group when both are full, and retries. Hypervisor insertion failure restores the old PTE and returns `-1`; permission miss returns `1`; busy PTE returns `0` for retry.

## State and persistence behavior
It mutates the PTE busy/accessed/dirty/hash-index bits, inserts/updates/removes HPTEs through `mmu_hash_ops`, may perform lazy icache state changes, and optionally triggers hash stress behavior.

## Dependencies and integration points
Integrated with Book3S64 hash page fault handling for 4K pages, page-table flag conversion, MMU hash operation backend, lazy icache coherency, and stress/debug infrastructure.

## Risks and edge cases
Risks include leaving `H_PAGE_BUSY` set on unusual exits, stale HPTE index data, races with concurrent faults/unmaps, hypervisor failure recovery, primary/secondary full-group eviction choice, and correct dirty/access permission handling.

## Test signals
Signals include successful hash faults, correct permission faults, no PTE busy hangs, expected HPTE insertion/update behavior, and stress-hash robustness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_4k.c -->
