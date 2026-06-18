# Group Research: group_1185_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_arch_m68k_hardfloat_u_848080f7e030

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/unordsf2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/unordsf2.S

This m68k hard-float assembly file defines `__unorddf2`, a libgcc-style unordered comparison helper for double-precision values. It loads two stack-passed doubles into the 68881-compatible FPU, performs `fcmpd`, and returns `0` when the comparison branches on unordered/ordered condition label `Lbor`, otherwise `1`.

Its integration point is compiler-emitted floating-point comparison support in libc/libgcc compatibility code. The key risk is ABI exactness: stack offsets, FPU condition-code interpretation, and the mismatch between the filename’s `sf` spelling and the exported `__unorddf2` symbol are all intentional historical port details.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/unordsf2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/net/Makefile.inc

This make include adds m68k assembly byte-order conversion sources: `htonl.S`, `htons.S`, `ntohl.S`, and `ntohs.S`. It is consumed by the libc architecture build to select machine-specific network-order routines.

The file contains no logic beyond source selection, so the main dependency is the existence and correctness of the named assembly files in the same architecture tree.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/quad/ashldi3.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/quad/ashldi3.S

This file implements `__ashldi3`, the 64-bit arithmetic left-shift helper for m68k. It loads a 64-bit value as high word in `%d0` and low word in `%d1`, handles shifts below and above 32 bits, combines cross-word bits, clears the low half when needed, and restores scratch registers before returning.

It is compiler runtime glue for targets where 64-bit shifts require helper calls. Correctness depends on the m68k calling convention, callee-saved scratch preservation through `moveml`, and the assumption that the shift count is in the valid compiler-generated range.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/quad/ashldi3.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/quad/ashrdi3.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/quad/ashrdi3.S

This file implements `__ashrdi3`, the signed 64-bit arithmetic right-shift helper for m68k. It shifts the high and low 32-bit halves across `%d0/%d1`, sign-extends the high word for shifts of 32 bits or more, and preserves temporary data registers.

It is used by compiler-generated signed `long long` shifts. The important behavior is sign propagation via arithmetic shifts and `smi/extbl`, which distinguishes it from the logical right-shift helper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/quad/ashrdi3.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/quad/lshrdi3.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/quad/lshrdi3.S

This file implements `__lshrdi3`, the unsigned/logical 64-bit right-shift helper for m68k. It moves bits from the high half into the low half for shifts under 32 and clears the high half for shifts of 32 or more.

It backs compiler-emitted unsigned `long long` shifts. The key distinction from `__ashrdi3` is zero-fill behavior, so regressions here would affect unsigned arithmetic and bit-manipulation code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/quad/lshrdi3.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/softfloat/m68k-gcc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/softfloat/m68k-gcc.h

This header adapts John Hauser SoftFloat types to NetBSD/m68k GCC. It derives `BIGENDIAN` or `LITTLEENDIAN` from `<machine/endian.h>`, enables `BITS64`, defines SoftFloat integer aliases such as `flag`, `bits32`, `bits64`, and supplies `LIT64` and `INLINE`.

It also defines `FLOAT64_DEMANGLE` and `FLOAT64_MANGLE` as identity macros for this port. The header is a low-level ABI contract for all m68k softfloat sources; type width changes would cascade into every declared SoftFloat operation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/softfloat/m68k-gcc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/softfloat/milieu.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/softfloat/milieu.h

This SoftFloat environment header includes `m68k-gcc.h` and defines boolean constants `FALSE` and `TRUE`. Most of the file is the upstream SoftFloat license and integration notice.

Its purpose is to provide common integer, endian, and boolean definitions before the architecture’s `softfloat.h` API declarations. There is no runtime logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/softfloat/milieu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/softfloat/softfloat.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/softfloat/softfloat.h

This header declares the m68k SoftFloat public API and type layout. It enables `FLOATX80` except on ColdFire, leaves `FLOAT128` disabled, defines `float32`, `float64`, and a packed m68k `floatx80` layout with `X80SHIFT` and `X80M68K`.

It exposes global rounding, tininess, exception-flag, exception-mask, and extended-precision state, mapped to NetBSD `<machine/ieeefp.h>` constants. It declares integer conversion, float32/float64 arithmetic, comparisons, NaN predicates, floatx80 conversions/operations/comparisons, and conditional float128 operations.

This file is consumed by the architecture softfloat implementation and GCC compatibility paths. The most sensitive details are the m68k extended-precision memory layout and conditional declarations under `SOFTFLOAT_FOR_GCC` / `SOFTFLOATM68K_FOR_GCC`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/softfloat/softfloat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/stdlib/Makefile.inc

This make include adds m68k assembly implementations of `abs.S` and `llabs.S` to libc’s stdlib build. It is a source-selection file only.

The integration risk is build coverage: removing these entries would fall back to generic code or leave expected m68k symbols unbuilt.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/stdlib/abs.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/stdlib/abs.S

This assembly file implements both `labs` and `abs`, with `labs` falling through into the `abs` entry. It loads the 32-bit argument from the stack into `%d0`, branches if nonnegative, otherwise negates it, and returns.

It is a compact machine-specific stdlib routine. Like standard C `abs`, the most negative two’s-complement value remains an overflow edge case; this file does not add special handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/stdlib/abs.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/stdlib/llabs.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/stdlib/llabs.S

This file implements `_llabs` and weak aliases `llabs` and `imaxabs`. It loads a 64-bit signed integer into `%d0/%d1`, checks the sign in the high word, and if negative performs a two-word negation using `negl` and `negxl`.

It provides compiler/stdlib ABI support for `long long` and `intmax_t` absolute values on m68k. The implementation depends on m68k extended carry behavior for correct 64-bit negation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/stdlib/llabs.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/string/Makefile.inc

This make include selects m68k assembly implementations for common string and memory functions: compare, copy, zero, set, concatenate, length, bounded string operations, byte search, byte swap, and move/copy variants. It includes both historical BSD routines and C-library entry points such as `memcpy`, `memccpy`, `memmove`, `strchr`, and `strrchr`.

The file is important build metadata for libc performance and symbol coverage. Any mismatch between listed sources and available assembly files would surface as build or missing-symbol failures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/string/memccpy.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/string/memccpy.S

This assembly file implements `memccpy`. It copies bytes from source to destination until the requested count is exhausted or the terminator byte is copied, returning the destination pointer just past the copied terminator or `NULL` if no terminator is found.

It has separate paths for NUL and non-NUL terminators, uses `%d2` as a saved scratch register in the non-NUL path, and has ColdFire-specific loop handling where `dbcc` is unavailable or unsuitable. ABI-sensitive return handling includes an `__SVR4_ABI__` path that mirrors the pointer return into `%a0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/string/memccpy.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/string/swab.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/string/swab.S

This file implements `swab`, copying pairs of bytes from source to destination with each pair swapped. It converts the byte count to a word count, ignores any odd trailing byte, then loops over word-sized swaps.

On ordinary m68k it loads a word, rotates it by 8 bits, and stores it; on ColdFire it performs two byte loads/stores manually. The semantics are the traditional BSD/POSIX `swab` behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/string/swab.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__clone.S

This file implements the m68k `__clone` wrapper and weak `clone` alias. It validates that the function pointer and stack pointer are non-NULL, prepares the child stack with the argument and fake syscall frame, invokes the `__clone` system call, and distinguishes parent from child by the returned value.

In the child path it calls the supplied function and then calls `_exit` with that return value. On invalid inputs or syscall failure it routes through `CERROR`, making this wrapper both ABI glue and error-policy enforcement.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__m68k_read_tp.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__m68k_read_tp.S

This tiny wrapper defines `__m68k_read_tp`. It invokes the `_lwp_getprivate` syscall and returns the result in both `%d0` and `%a0`.

It is a machine-specific thread-pointer accessor for m68k TLS/runtime code. There is no explicit error path, reflecting the expectation that reading the private LWP value is a non-failing primitive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__m68k_read_tp.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__mmap.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__mmap.S

This file defines the internal `__mmap` syscall wrapper around kernel `mmap`. It uses `_SYSCALL(__mmap,mmap)`, then returns directly, copying `%d0` to `%a0` for the SVR4 ABI variant.

It is simple syscall ABI glue. The only behavioral detail beyond standard error handling is the pointer-return register accommodation under `__SVR4_ABI__`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__mmap.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__sigtramp2.S

This file implements the m68k signal trampoline entry `__sigtramp_siginfo_2`. It includes DWARF CFI metadata describing how general registers and signal return PCs are recoverable from the `ucontext_t` placed on the signal frame.

At runtime the trampoline loads the ucontext pointer from the signal frame, places it into the syscall argument slot, calls `setcontext`, and if that fails calls `exit` with the error code. Correctness is critical for signal return, unwinding through signal frames, debuggers, and exception handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__syscall.S

This file builds `__syscall` with the generic `RSYSCALL` macro from m68k `SYS.h`. It supplies the internal variadic syscall entry point used for direct syscall-number based calls.

Its behavior is inherited from the macro definitions: perform the trap, branch to `CERROR` on carry/error, and return syscall results otherwise.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__vfork14.S

This file implements the m68k `__vfork14` wrapper. Because parent and child temporarily share the stack, it removes the return address before the syscall and later jumps to it instead of using a normal `rts`.

On success it converts the kernel’s parent/child indicator in `%d1` into standard `vfork` return semantics: parent gets child PID, child gets zero. On error it stores errno through either `__errno` or global `errno`, returns `-1`, and jumps back to the saved return address.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/_lwp_getprivate.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/_lwp_getprivate.S

This file defines the public `_lwp_getprivate` syscall wrapper. It invokes `SYSCALL(_lwp_getprivate)` and returns, with an SVR4 ABI path copying the pointer result from `%d0` into `%a0`.

It is used directly and by `__m68k_read_tp` for thread-private data access. Its behavior is otherwise standard m68k libc syscall wrapping.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/_lwp_getprivate.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/brk.S

This file implements `_brk` with weak public alias `brk`. It clamps the requested break to at least `__minbrk`, invokes the kernel `break` syscall, updates hidden `__curbrk` on success, and returns zero.

It defines `__minbrk` initialized to `_end`; `__curbrk` is declared external/hidden and updated here. The important contract is keeping libc’s tracked program break synchronized with successful kernel changes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/cerror.S

This file defines the m68k syscall error handler `CERROR`. It writes the kernel error value from `%d0` into thread-local `errno` through `__errno` in reentrant builds, or global `errno` otherwise, then returns `-1` in `%d0` and `%d1`.

It also handles PIC and SVR4 ABI details. Almost every m68k syscall wrapper depends on this path for consistent errno and return-value semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/fork.S

This file implements internal `__fork` around the kernel `fork` syscall. After a successful syscall it transforms the kernel’s parent/child indicator in `%d1` so the child returns zero and the parent returns the child PID.

Errors are handled by the `_SYSCALL` macro through `CERROR`. This is pure fork ABI adaptation for libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/getcontext.S

This file implements `_getcontext` with weak public alias `getcontext`. It calls the kernel `getcontext` syscall, then adjusts the saved user context so resuming it returns to the caller after the syscall wrapper with return value zero.

It updates `UC_MCONTEXT_SP`, `UC_MCONTEXT_PC`, and `UC_MCONTEXT_D0` using offsets from `assym.h`. This is sensitive to ucontext layout and m68k return-address conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/mremap.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/mremap.S

This file defines the `mremap` syscall wrapper. It performs the standard m68k `SYSCALL(mremap)` sequence and copies the pointer return to `%a0` when building for `__SVR4_ABI__`.

The file contains no extra validation or policy. Its purpose is only architecture-specific syscall and pointer-return ABI glue.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/mremap.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/pipe.S

This file implements `_pipe` with weak public alias `pipe`. After the kernel returns two file descriptors in `%d0` and `%d1`, it stores them into the user-provided `int[2]`, clears `%d0`, and returns zero.

It is a classic BSD syscall adaptation where multiple register return values are converted into the C API’s output array. Failure handling is provided by `_SYSCALL`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/ptrace.S

This file implements `ptrace` with special errno pre-clearing. Before issuing the syscall it sets thread-local or global `errno` to zero, then performs the `ptrace` trap and branches to `CERROR` on failure.

The pre-clear matters because `ptrace` can legitimately return `-1` as data on success, so callers distinguish success from failure by checking errno. The implementation carries PIC and reentrant errno handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/sbrk.S

This file implements `_sbrk` with weak public alias `sbrk`. It defines hidden `__curbrk` initialized to `_end`, adds the requested increment to the current break, calls the kernel `break` syscall, updates `__curbrk` on success, and returns the old break.

It is tightly coupled to `brk.S` through shared program-break state. Overflow and address validity are left to arithmetic/kernel behavior; libc’s responsibility here is maintaining the cached break on successful calls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/shmat.S

This file defines the `shmat` syscall wrapper. It performs the standard m68k syscall sequence and, for SVR4 ABI builds, mirrors the returned attached address into `%a0`.

The wrapper contains no local validation. Its role is preserving pointer-return ABI details for System V shared memory attachment.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/syscall.S

This file implements `_syscall` and weak alias `syscall`, the generic runtime syscall entry point. It clears `%d0`, executes `trap #0`, branches to `CERROR` on carry/error, and otherwise returns the kernel result.

Unlike named syscall wrappers, the syscall number is supplied by the caller using the generic convention. This is low-level ABI glue for code that invokes arbitrary syscall numbers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/Makefile.inc

This make include configures top-level MIPS libc architecture sources. It adds `__sigtramp2.S`, includes the current directory for generated headers, supplies `assym.h` CPP flags, and conditionally includes softfloat support when `MKSOFTFLOAT` is enabled.

For softfloat MIPS builds it adds IEEE754 unsigned conversion helpers, with extra long-double/quad helpers for MIPS64 non-o32 ABIs. The file is build-policy glue keyed to `MACHINE_MIPS64`, `CPUFLAGS`, and ABI selection.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/SYS.h

This header defines the MIPS libc syscall wrapper macros. It includes syscall numbers and MIPS assembly helpers, emits `.abicalls` and GP setup/restore behavior for PIC ABIs, and defines `SYSTRAP`, `RSYSCALL`, `WSYSCALL`, `PSEUDO`, and `PSEUDO_NOERROR`.

The generated wrappers use `v0` for syscall number/results and `a3` as the kernel error indicator, tail-calling `__cerror` when needed. This header is the core ABI contract for nearly every MIPS syscall assembly file in this group.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/gdtoa/Makefile.inc

This make include adds `strtof.c` for MIPS gdtoa support. On MIPS64 non-o32 builds it also adds `strtold_pQ.c` and `strtopQ.c` to support quad/long-double parsing.

The build logic mirrors the architecture’s long-double availability. It has no runtime logic, but incorrect ABI conditionals would include incompatible conversion code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/gdtoa/arith.h

This gdtoa configuration header includes `<machine/endian.h>` and defines either `IEEE_BIG_ENDIAN` or `IEEE_LITTLE_ENDIAN` based on `BYTE_ORDER`. It tells David Gay dtoa/gdtoa code how floating-point words are arranged on MIPS.

Its correctness is essential for decimal/binary floating conversion. There are no functions or state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/gdtoa/gd_qnan.h

This header defines canonical quiet-NaN bit patterns for MIPS gdtoa output. It sets `f_QNAN` and endian-dependent word ordering for double and long-double/quad patterns.

The constants are consumed by gdtoa conversion code when it needs to synthesize NaNs. The main risk is word-order mismatch, especially because MIPS supports both big- and little-endian configurations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/net/Makefile.inc

This make include intentionally adds no real network byte-order sources, noting that `hton*` and `ntoh*` are provided by generated byte-swap assembly elsewhere. It instead lists lint stubs `Lint_htonl.c`, `Lint_htons.c`, `Lint_ntohl.c`, and `Lint_ntohs.c`, adds them to lint and dependency sources, and cleans them.

Its role is build-system compatibility for lint while avoiding duplicate object implementations. The empty `SRCS+=` line is intentional.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/softfloat/milieu.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/softfloat/milieu.h

This SoftFloat environment header includes `mips-gcc.h` and defines `FALSE` and `TRUE`. It carries the upstream SoftFloat license text and provides shared compile-time types and booleans.

It has no executable logic. It is included before the MIPS softfloat declarations and implementation sources.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/softfloat/milieu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/softfloat/mips-gcc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/softfloat/mips-gcc.h

This header adapts SoftFloat’s integer and endian assumptions for MIPS GCC. It chooses `BIGENDIAN` via `__MIPSEB__` and `LITTLEENDIAN` otherwise, enables `BITS64`, defines SoftFloat integer aliases and exact-width bit types, and supplies `LIT64` plus `INLINE`.

It documents MIPS floating-point word-order oddities and defines identity `FLOAT64_DEMANGLE` / `FLOAT64_MANGLE` only under `SOFTFLOAT_FOR_GCC`. This conditional matters for compiler-helper builds versus libc softfloat builds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/softfloat/mips-gcc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/softfloat/softfloat.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/softfloat/softfloat.h

This header declares the MIPS SoftFloat API. It leaves `FLOATX80` disabled, enables `FLOAT128` for `__mips_n32` and `__mips_n64`, defines `float32`, `float64`, optional `floatx80`, and `float128`, and maps rounding/exception state to NetBSD machine IEEE FP types.

It declares conversion and arithmetic routines for float32, float64, optional extended precision, and optional float128. Several declarations are conditional for `SOFTFLOAT_FOR_GCC` and `SOFTFLOAT_NEED_FIXUNS`, because some integer conversions are supplied by libgcc instead.

This header is both a libc API contract and compiler-runtime interface. ABI selection controls whether quad precision exists, making the MIPS64/o32 distinction important.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/softfloat/softfloat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/stdlib/Makefile.inc

This file only contains the NetBSD RCS identifier comment and adds no MIPS-specific stdlib sources. It is a placeholder include in the architecture build hierarchy.

Its presence keeps the build structure uniform across architectures. There is no behavior to test.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/string/Makefile.inc

This make include selects MIPS string routines. It builds `bcmp.S` and `bzero.S`; for MIPS64 it maps several object targets to generic C sources such as `bcopy.c`, `memcmp.c`, and `memmove.c`, while non-MIPS64 adds `memcmp.S`, `bcopy.S`, and `memmove.S`.

The file encodes ABI/performance tradeoffs between assembly and generic C implementations. Incorrect conditionals could select assembly that is not valid for a given MIPS ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/string/bcmp.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/string/bcmp.S

This file implements `bcmp(s1, s2, n)` for MIPS. It quickly handles small byte counts, aligns when possible, compares aligned words in a loop, and has an unaligned path using endian-aware `LWHI`/`LWLO` partial-word loads.

It returns zero for equality and one for mismatch. The implementation is performance-oriented but depends on careful address alignment, byte-order macros, and MIPS branch-delay-slot scheduling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/string/bcmp.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/string/bzero.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/string/bzero.S

This file implements MIPS `bzero`. It handles small lengths bytewise, aligns the destination to register width, clears whole words using `REG_S`, then clears trailing bytes.

For 32-bit register builds it uses `SWHI` to clear initial unaligned bytes; for 64-bit it constructs masks to partially clear an unaligned word. Correctness depends on `SZREG`, endian-specific mask direction, and avoiding writes outside the requested range.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/string/bzero.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__clone.S

This file implements MIPS `__clone` and weak `clone`. It validates function and stack arguments, places the function pointer and argument on the child stack, invokes the `__clone` syscall with `(flags, stack)`, and separates parent from child using the kernel secondary return value.

The child reloads the function and argument from its stack, sets a terminating frame, calls the function, then tail-calls `_exit` with the function’s return value. The wrapper is sensitive to MIPS call frames, GP preservation, and PIC return mechanics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__sigtramp2.S

This file implements the MIPS `__sigtramp_siginfo_2` signal-return trampoline. It emits DWARF CFI for the saved general registers, MDHI/MDLO, and signal-return PC within the signal frame’s ucontext.

At runtime it computes the ucontext address after `siginfo_t`, calls `setcontext`, then calls `exit` with the error code if restoration fails. This file is essential for signal return correctness and stack unwinding across signal handlers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__syscall.S

This file defines `__syscall` through `RSYSCALL(__syscall)`. For non-o32 MIPS ABIs it also aliases `_syscall` and weak `syscall` to `__syscall`; o32 has a separate `syscall.S`.

It is generic syscall-number dispatch glue. Its detailed trap/error behavior comes from `SYS.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__vfork14.S

This file implements MIPS `__vfork14`. It loads the syscall number, executes `syscall`, routes errors to `__cerror`, and on success converts the kernel’s parent/child flag in `v1` into standard return values.

The parent receives the child PID in `v0`; the child returns zero. PIC setup and return are handled through the MIPS syscall macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/brk.S

This file implements `_brk` with weak alias `brk`. It loads `__minbrk`, clamps the requested break upward if necessary, invokes the kernel `break` syscall, updates `__curbrk` on success, returns zero, and tail-calls `__cerror` on failure.

It initializes `__minbrk` to `_end` in data. Its behavior matches other ports’ program-break tracking but uses MIPS PIC and register conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/cerror.S

This file defines MIPS `__cerror`, the common syscall error return path. In reentrant builds it saves return state, calls `__errno`, writes the saved error value, restores GP/RA as needed, and returns `-1` in both `v0` and `v1`.

In non-reentrant builds it stores the error directly in global `errno`. This routine is central to MIPS syscall wrappers and is especially sensitive to PIC GP setup for o32/n32/n64.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/fork.S

This file implements MIPS `__fork`. It issues the `fork` syscall, branches to `__cerror` if `a3` indicates failure, and uses `v1` to distinguish parent from child.

On child return it sets `v0` to zero; in the parent it leaves the child PID in `v0`. This is standard fork ABI adaptation for MIPS libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/getcontext.S

This file implements `_getcontext` and weak alias `getcontext`. After a successful kernel `getcontext`, it forces the saved `v0` return register in the ucontext to zero and stores the current return address as the saved EPC; for non-o32 it also stores the saved GP from PIC setup.

It uses offsets from `assym.h` and `<machine/mcontext.h>`. The wrapper is required so a later `setcontext` resumes as if `getcontext` returned zero.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/pipe.S

This file implements `_pipe` with weak alias `pipe`. It invokes the `pipe` syscall, stores returned descriptors from `v0` and `v1` into the user `int[2]` pointed to by `a0`, returns zero on success, and tail-calls `__cerror` on failure.

It converts the kernel’s multiple-register return convention into the C API’s output-buffer convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/ptrace.S

This file implements MIPS `ptrace`. It clears global `errno` before making the syscall, because `ptrace` can return `-1` successfully, then traps and uses `a3` to branch to `__cerror` on failure.

A comment marks the non-reentrant direct `errno` store as “BOGUS,” reflecting that this assembly path does not use `__errno`. This routine is semantically important for callers that inspect errno after `ptrace`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/sbrk.S

This file implements `_sbrk` with weak alias `sbrk`. It defines `__curbrk` initialized to `_end`, adds the requested increment to the cached break, calls the kernel `break` syscall, stores the new break on success, and returns the old break.

It is paired with `brk.S` through shared `__curbrk` state. Correctness depends on preserving the old value while issuing the syscall and updating only after success.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/shmat.S

This file defines `shmat` via `RSYSCALL(shmat)`. It has no custom code beyond including `SYS.h`.

The wrapper uses standard MIPS syscall/error semantics from the macro layer. It exists because shared memory attachment needs an architecture-visible syscall entry.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/syscall.S

This file provides the o32 MIPS `syscall` / `_syscall` wrapper when `__mips_o32` is defined. It is built via `WSYSCALL(syscall,_syscall)`, which creates a weak public alias and a strong internal implementation.

For non-o32 ABIs, `__syscall.S` provides the aliases instead. The split reflects ABI-specific syscall argument and symbol conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/Makefile.inc

This make include configures OpenRISC/or1k libc architecture sources. It adds `__sigtramp2.S` and `mulsi3.S`, includes the architecture directory, and generates `sysassym.h` from installed syscall headers using `syscallargs.awk` and `genassym`.

`sysassym.h` supplies syscall argument counts used by `SYS.h` to load stack arguments for syscalls with more than six register arguments. SoftFloat support is conditionally included when enabled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/SYS.h

This header defines or1k syscall wrapper macros. It loads syscall numbers into `r13`, uses `l.sys 0`, treats the branch flag as the error indicator, and supplies `_SYSCALL`, `PSEUDO`, `RSYSCALL`, and `WSYSCALL`.

It also uses generated `NSYSARGS_*` macros to load seventh and eighth syscall arguments from the stack into `r11` and `r12` before trapping. This generated-argument-count dependency is specific and important for correct syscall marshalling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/gdtoa/Makefile.inc

This make include adds `strtof.c` for or1k gdtoa support. It contains no ABI conditionals or local logic.

The selected source provides single-precision string-to-float conversion support for the architecture’s libc build.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/gdtoa/arith.h

This gdtoa configuration header declares `IEEE_BIG_ENDIAN` unconditionally for or1k. It tells gdtoa code to use big-endian floating-point word ordering.

There are no functions or state. Its correctness depends on the port’s ABI remaining big-endian for the supported configuration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/gdtoa/gd_qnan.h

This header defines or1k gdtoa quiet-NaN constants. It sets the single-precision NaN to `0x7fc00000` and the big-endian double words to `0x7ff80000, 0x0`.

It is used when gdtoa conversion code must synthesize NaNs. The constants match the architecture’s declared big-endian IEEE layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/net/Makefile.inc

This make include adds C implementations of byte-order conversion functions: `htonl.c`, `htons.c`, `ntohl.c`, and `ntohs.c`. It has no local logic.

The file selects generic/simple C conversion sources for or1k rather than assembly. Build correctness depends on those sources matching or1k endian behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/softfloat/milieu.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/softfloat/milieu.h

This SoftFloat environment header includes `or1k-gcc.h` and defines `FALSE` and `TRUE`. It carries the upstream SoftFloat license and contains no executable code.

It supplies the basic type/endian environment for or1k softfloat implementation files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/softfloat/milieu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/softfloat/or1k-gcc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/softfloat/or1k-gcc.h

This header adapts SoftFloat integer types and endian macros to or1k GCC. It derives `BIGENDIAN`/`LITTLEENDIAN` from `<machine/endian.h>`, enables `BITS64`, defines SoftFloat integer aliases and exact-width bit types, and supplies `LIT64` and `INLINE`.

It defines float64 mangle/demangle macros as identity operations. This file is architecture configuration rather than runtime logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/softfloat/or1k-gcc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/softfloat/softfloat.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/softfloat/softfloat.h

This header declares the or1k SoftFloat API. Both `FLOATX80` and `FLOAT128` are disabled, while `float32` and `float64` are always defined and mapped to integer storage types.

It declares softfloat rounding, tininess, exception state, integer conversion, float32/float64 arithmetic/comparison/conversion routines, and conditional prototypes for disabled extended/quad blocks. It is mostly identical to other non-extended ports and acts as the compile-time contract between libc softfloat sources and or1k callers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/softfloat/softfloat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/stdlib/Makefile.inc

This file contains only an RCS identifier comment and adds no or1k-specific stdlib sources. It is a placeholder in the architecture build tree.

There is no runtime behavior or source-selection logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/string/Makefile.inc

This make include selects or1k string/memory implementations. In debug builds it maps object targets to generic C sources for easier debugging; otherwise it builds assembly versions of `memcmp.S`, `bcopy.S`, and `memmove.S`.

The conditional source mapping affects performance and debuggability. It must keep object names aligned with libc’s expected string routine symbols.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__clone.S

This file implements or1k `__clone` and weak `clone`. It checks that function and stack arguments are non-NULL, saves the function pointer, rearranges arguments for the kernel `__clone(flags, stack)` syscall, and branches to `__cerror` on invalid input or syscall error.

The parent returns normally; the child calls the saved function with the supplied argument and then calls `_exit`. PIC builds set up the GOT before calling `_exit`, since that path does not return.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__sigtramp2.S

This file implements the or1k signal trampoline `__sigtramp_siginfo_2`. It uses the ucontext pointer preserved in `r14`, moves it to the first argument register, calls `setcontext`, and if that fails calls `exit`.

Unlike some other ports in this group, it does not include extensive DWARF CFI metadata. Its runtime role is still critical: returning from signal handlers by restoring the saved machine context.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__syscall.S

This file implements or1k `__syscall`, `_syscall`, and weak `syscall`. It takes the syscall number from `r3`, shifts up to five register arguments down into the kernel’s expected registers, loads additional arguments from the stack into `r8`, `r11`, and `r12`, executes `l.sys 0`, and branches to `__cerror` on failure.

The file is the generic syscall-number entry point. Its argument shuffling is the main semantic content.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__vfork14.S

This file implements or1k `__vfork14`. It uses the standard syscall macro, then adjusts the secondary return register `r12` so the child returns zero and the parent returns the child PID in `r11`.

It is the vfork-specific parent/child return-value adapter. Failure handling is inherited from `SYSCALL(__vfork14)`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/brk.S

This file implements `_brk` with weak alias `brk` for or1k. It defines hidden `__minbrk` and `__curbrk` initialized to `_end`, clamps the requested break to at least `__minbrk`, invokes the kernel `break` syscall, updates `__curbrk`, and returns zero.

It includes PIC and non-PIC address materialization paths. The file’s correctness depends on preserving the clamped new break across the syscall and storing it at the correct data offset.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/cerror.S

This file defines or1k `__cerror`, the shared syscall error handler. In reentrant builds it saves registers and calls `__errno`; in non-reentrant builds it locates global `errno` directly, with PIC and non-PIC address paths.

It stores the error value, then returns `-1` in both `r11` and `r12`. All or1k syscall wrappers depend on this for consistent errno semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/fork.S

This file implements or1k `__fork`. After `_SYSCALL(__fork,fork)` succeeds, it transforms the kernel’s parent/child flag in `r12` so the child returns zero and the parent returns the child PID in `r11`.

It is minimal fork ABI glue, relying on the syscall macro for trap and error handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/getcontext.S

This file implements `_getcontext` with weak alias `getcontext`. It calls the kernel `getcontext` syscall, then stores the current link register into the saved PC slot and stores zero into the saved return-value register slot.

The offsets come from `assym.h`. This ensures that resuming the captured context behaves as if `getcontext` returned zero.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/pipe.S

This file implements `_pipe` with weak alias `pipe`. It saves the caller’s output pointer, invokes the kernel `pipe` syscall, stores returned descriptors from `r11` and `r12` into the two integers, clears `r11`, and returns zero.

It converts the kernel’s multiple-register return convention into the C API’s array convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/ptrace.S

This file implements or1k `ptrace` with errno pre-clearing. Reentrant builds save call registers and use `__errno`; non-reentrant builds locate global `errno`, then the wrapper clears it before issuing the `ptrace` syscall.

The pre-clear is needed because `ptrace` may legitimately return `-1` on success. The file is sensitive to PIC register setup and has a typo-like `lwz` instruction spelling in the PIC non-reentrant path as written, which would be build-toolchain dependent.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/sbrk.S

This file implements `_sbrk` with weak alias `sbrk`. It loads hidden `__curbrk`, adds the requested increment, calls the kernel `break` syscall, updates `__curbrk` with the new break, and returns the old break in `r11`.

It has PIC and non-PIC symbol-address paths. It is paired with `brk.S` and relies on updating cached break state only after successful syscalls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/shmat.S

This file defines `shmat` through `RSYSCALL(shmat)`. It contains no custom code beyond the macro-based syscall wrapper.

Its behavior is standard or1k trap and `__cerror` handling from `SYS.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/syscall.S

This file contains only a comment saying `syscall` is aliased to `__syscall`. The actual implementation and aliases live in `__syscall.S`.

Its purpose is to occupy the expected source path without adding duplicate code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/syscallargs.awk -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/syscallargs.awk

This AWK script generates assembly constants for or1k syscall argument counts. It reads syscall number definitions and `check_syscall_args...` records from syscall headers, maps each syscall name to either zero or `sizeof(struct sys_*_args) / sizeof(register_t)`, and emits `define NSYSARGS_<name> <count>` lines.

The output also includes required headers for `genassym`. `SYS.h` uses these generated `NSYSARGS_*` constants to decide whether to load seventh and eighth syscall arguments from the user stack.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/syscallargs.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/Makefile.inc

This make include configures 32-bit PowerPC libc architecture sources. It adds `__sigtramp2.S` and `powerpc_initfini.c`, includes the architecture directory, and conditionally includes softfloat support when `MKSOFTFLOAT` is enabled.

The important integration point is `powerpc_initfini.c`, which provides cache-line data used by optimized memory routines. Source selection here affects both syscall/signal ABI code and string routine performance.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/SYS.h

This header defines 32-bit PowerPC syscall wrapper macros. It loads syscall numbers into `%r0`, executes `sc`, uses summary overflow (`bso` / `bnslr`) to detect errors, and branches to `__cerror`.

It supplies `_SYSCALL`, `PSEUDO`, `RSYSCALL`, and `WSYSCALL` forms for generated and hand-written wrappers. This is the shared ABI layer for the PowerPC syscall files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/gdtoa/Makefile.inc

This make include adds `strtof.c` for PowerPC gdtoa support. It contains no conditionals.

The selected source provides single-precision decimal-to-binary conversion for this architecture’s libc build.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/gdtoa/arith.h

This gdtoa configuration header defines `IEEE_BIG_ENDIAN` for PowerPC. It informs gdtoa code that floating-point words are big-endian.

There is no executable logic. The file is an architecture constant header.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/gdtoa/gd_qnan.h

This header defines PowerPC gdtoa quiet-NaN bit patterns. It sets single precision to `0x7fc00000` and big-endian double words to `0x7ff80000, 0x0`.

These constants are used when gdtoa must synthesize NaN values. They assume big-endian IEEE layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/misc/powerpc_initfini.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/misc/powerpc_initfini.c

This C file defines hidden global `_libc_powerpc_cache_info` and a constructor `_libc_cache_info_init`. At load time, the constructor calls `sysctl` with `CTL_MACHDEP, CPU_CACHEINFO` to populate cache-size/line-size information, guarded by a static `initialized` flag.

The cached data is used by optimized PowerPC routines such as `bzero.S` / `memset` to choose cache-block operations. Failure to retrieve sysctl data is tolerated; consumers must handle zero/unknown cache info.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/misc/powerpc_initfini.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/net/Makefile.inc

This make include adds C byte-order conversion implementations: `htonl.c`, `htons.c`, `ntohl.c`, and `ntohs.c`. It has no additional logic.

It selects architecture-local network conversion sources for PowerPC libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/softfloat/milieu.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/softfloat/milieu.h

This SoftFloat environment header includes `powerpc-gcc.h` and defines boolean constants `FALSE` and `TRUE`. It is otherwise upstream SoftFloat licensing and setup commentary.

It provides the type/endian environment used by the PowerPC softfloat declarations and implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/softfloat/milieu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/softfloat/powerpc-gcc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/softfloat/powerpc-gcc.h

This header maps SoftFloat’s integer and endian configuration to PowerPC GCC. It derives endian macros from `<machine/endian.h>`, enables 64-bit integer support, defines SoftFloat convenience and exact-width integer types, and supplies `LIT64` and `INLINE`.

It defines float64 mangle/demangle as identity operations. The file contains no runtime code but is foundational for softfloat type consistency.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/softfloat/powerpc-gcc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/softfloat/softfloat.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/softfloat/softfloat.h

This header declares the PowerPC SoftFloat API. It leaves `FLOATX80` and `FLOAT128` disabled, defines `float32` and `float64`, maps rounding and exception state to NetBSD IEEE FP constants, and declares conversion, arithmetic, comparison, and NaN-test routines.

The optional extended/quad blocks are present but inactive unless macros are changed. This file is nearly the same contract as or1k softfloat, adapted through `powerpc-gcc.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/softfloat/softfloat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/stdlib/Makefile.inc

This file contains only the NetBSD RCS identifier comment and adds no PowerPC-specific stdlib sources. It is a build hierarchy placeholder.

There is no runtime or source-selection behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/string/Makefile.inc

This make include selects PowerPC string routines. It adds `bzero.S`, `ffs.S`, and `strlen.S`, and marks `memset.S` as not used.

The `bzero.S` source also defines `memset`, so suppressing a separate `memset.S` avoids duplicate symbol implementations. This file is source-selection glue for optimized string routines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/string/bzero.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/string/bzero.S

This file implements PowerPC `bzero` and `memset`. `bzero` sets the fill value to zero and branches into the shared fill path; `memset` expands the byte fill value across a word and uses simple or cache-aware loops.

For zero fills, non-kernel builds read `_libc_powerpc_cache_info` to obtain data-cache line size and can use `dcbz` to clear cache blocks efficiently. The fallback path aligns to word boundaries, fills words, then clears remaining bytes. Correctness depends on preserving the original destination pointer for `memset` return and safely handling unknown cache info.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/string/bzero.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__clone.S

This file implements PowerPC `__clone` and weak `clone`. It validates function and stack arguments, saves the function pointer, rearranges syscall arguments to `(flags, stack)`, invokes `__clone`, and on error branches to `__cerror`.

The parent returns directly; the child moves the saved function pointer into LR, calls it with the supplied argument, and calls `_exit` with the result. PIC builds set up the TOC before calling `_exit`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__sigtramp2.S

This file implements PowerPC `__sigtramp_siginfo_2` and detailed DWARF CFI for signal-frame unwinding. It describes GPRs, FPR/AltiVec DWARF numbering notes, LR, CTR, CR2, XER, and the signal-return PC using offsets into the saved ucontext.

The runtime trampoline moves the ucontext pointer from `%r30` into `%r3`, calls `setcontext`, and if that fails calls `exit`. It is critical for correct signal return and debugger/unwinder behavior on PowerPC.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__syscall.S

This file implements PowerPC `__syscall`, `_syscall`, and weak `syscall`. It moves the caller-supplied syscall number from `%r3` to `%r0`, shifts register arguments down, loads the final stack argument, executes `sc`, and branches to error handling if summary overflow is set.

It is the generic syscall-number entry for PowerPC. The argument shifting is the key ABI-specific behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__vfork14.S

This file implements PowerPC `__vfork14`. After the syscall, it adjusts `%r4` from the kernel parent/child flag and masks `%r3` so the child returns zero while the parent returns the child PID.

It is minimal vfork return-value adaptation. Error handling is provided by the `SYSCALL` macro.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/brk.S

This file implements `_brk` with weak alias `brk`. It defines hidden `__minbrk` and `__curbrk` initialized to `_end`, locates `__minbrk` through PIC or absolute addressing, clamps the requested break, invokes `break`, updates `__curbrk`, and returns zero.

It optionally uses `isel` when available for the clamp. The main contract is synchronizing libc’s cached break state with the kernel only after successful calls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/cerror.S

This file defines PowerPC `__cerror`. In reentrant builds it saves LR and callee-saved registers, calls `__errno`, stores the error value, restores state, and returns `-1` in `%r3` and `%r4`.

In non-reentrant builds it stores directly into global `errno`, with PIC and non-PIC paths. It is the shared error handler for PowerPC syscall wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/fork.S

This file implements PowerPC `__fork`. It invokes the `fork` syscall and converts the kernel’s `%r4` parent/child flag so the child returns zero and the parent returns the child PID in `%r3`.

It relies on `_SYSCALL` for trap and error handling. There is no extra state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/getcontext.S

This file implements `_getcontext` and weak `getcontext`. It saves the ucontext pointer, calls the kernel `getcontext`, stores the current LR into the saved PC slot, stores zero as the saved `%r3` return value, and returns.

It uses `assym.h` offsets such as `UC_GREGS_PC` and `UC_GREGS_R3`. This wrapper fixes the captured context so resuming it reports a successful `getcontext`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/pipe.S

This file implements `_pipe` with weak alias `pipe`. It saves the output pointer, invokes the `pipe` syscall, stores returned descriptors from `%r3` and `%r4`, returns zero, and branches to `__cerror` on failure.

It adapts multiple register returns into the C `int fildes[2]` API.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/ptrace.S

This file implements PowerPC `ptrace` with errno pre-clearing. Reentrant builds save call arguments, call `__errno`, clear errno, restore arguments, then issue the syscall; non-reentrant builds clear global `errno` directly.

The pre-clear is required because `ptrace` can return `-1` on success. The implementation includes PIC TOC setup and careful stack frame offsets for the saved arguments.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/sbrk.S

This file implements `_sbrk` with weak alias `sbrk`. It loads hidden `__curbrk`, adds the requested increment, calls kernel `break`, stores the new break on success, and returns the old break.

It has PIC and non-PIC addressing paths. It is paired with `brk.S` and shares the same cached break invariant.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/shmat.S

This file defines `shmat` through `RSYSCALL(shmat)`. It has no local logic beyond macro expansion.

The resulting wrapper uses the standard PowerPC syscall and `__cerror` behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/syscall.S

This file contains only a comment that `syscall` is aliased to `__syscall`. The implementation and aliases live in `__syscall.S`.

It prevents duplicate implementation while preserving the expected source layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/Makefile.inc

This make include configures PowerPC64 libc architecture sources. It clears `KMINCLUDES` and `KMSRCS`, adds the architecture directory to CPP flags, and adds `__sigtramp2.S`.

It does not include softfloat or miscellaneous cache initialization sources. The file is straightforward build selection for the 64-bit port.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/SYS.h

This header defines PowerPC64 syscall wrapper macros. Unlike 32-bit PowerPC, it inlines the `__cerror` behavior in `_DO_CERROR()` because branching to `__cerror` is unreliable with the PowerPC64 ABI.

The macros load syscall numbers into `%r0`, execute `sc`, use summary overflow to detect errors, and either return or inline errno storage and `-1` returns. Reentrant builds call `__errno`; non-reentrant builds store through TOC-addressed `errno`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/gdtoa/Makefile.inc

This make include adds `strtof.c` for PowerPC64 gdtoa support. It has no conditionals or extra logic.

It selects single-precision decimal conversion support for the architecture.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/gdtoa/arith.h

This gdtoa configuration header defines `IEEE_BIG_ENDIAN` for PowerPC64. It declares the floating-point word ordering expected by gdtoa.

There is no executable code or state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/gdtoa/gd_qnan.h

This header defines PowerPC64 gdtoa quiet-NaN constants. It sets the single-precision pattern to `0x7fc00000` and double words to `0x7ff80000, 0x0`.

The constants match the architecture’s big-endian IEEE layout and are used by conversion code that synthesizes NaN values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/net/Makefile.inc

This make include adds C byte-order conversion sources: `htonl.c`, `htons.c`, `ntohl.c`, and `ntohs.c`. It is source-selection metadata only.

These sources provide network byte-order APIs for PowerPC64 libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/stdlib/Makefile.inc

This file contains only the NetBSD RCS identifier and adds no PowerPC64-specific stdlib sources. It is a placeholder include.

There is no runtime behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/string/Makefile.inc

This make include adds PowerPC64 string assembly sources `bzero.S`, `ffs.S`, and `strlen.S`, while marking `memset.S` as not used. The local `bzero.S` provides both `bzero` and `memset`.

It is build metadata preventing duplicate `memset` objects while selecting optimized routines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/string/bzero.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/string/bzero.S

This file implements PowerPC64 `bzero` and `memset`. `bzero` maps to `memset` with fill value zero; `memset` uses a byte loop for short or unaligned cases, constructs a repeated 64-bit fill word, and uses unrolled `std` stores for larger aligned spans.

It returns the original destination pointer for `memset`. Unlike the 32-bit PowerPC version, it does not use cache-line `dcbz`; it optimizes through 8-byte and 32-byte store loops.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/string/bzero.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/Makefile.inc

This make include adds PowerPC64 syscall-directory sources `__sigaction14_sigtramp.c` and `__sigtramp2.S`. It is narrow build metadata for signal handling support.

The explicit inclusion suggests signal trampoline handling differs enough from the top-level architecture include to need sys-directory source selection.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__clone.S

This file implements PowerPC64 `__clone` and weak `clone`. It validates function and stack pointers, saves the function pointer, rearranges arguments for the kernel `__clone(flags, stack)` call, and uses inline syscall error handling via `BRANCH_TO_CERROR()`.

The parent returns normally; the child calls the function with the argument and then calls `_exit`. The code mirrors the 32-bit PowerPC logic but uses PowerPC64 ABI support from `SYS.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__sigtramp2.S

This file implements the PowerPC64 signal trampoline `__sigtramp_siginfo_2`. The kernel enters with `%r30` pointing to the ucontext, so the trampoline moves `%r30` to `%r3`, invokes `setcontext`, and invokes `exit` if restoration fails.

Unlike 32-bit PowerPC’s version, this file does not include extensive `.cfi` unwind metadata. Its runtime role remains signal context restoration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__syscall.S

This file implements PowerPC64 `__syscall`, `_syscall`, and weak `syscall`. It moves the syscall number into `%r0`, shifts arguments down through `%r10`, loads the final stack argument, executes `sc`, and uses inline error handling on failure.

It is the generic syscall-number entry for PowerPC64. The argument shuffle matches the 64-bit PowerPC calling convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__vfork14.S

This file implements PowerPC64 `__vfork14`. After the syscall, it adjusts `%r4` from the kernel parent/child indicator and masks `%r3` so the child returns zero and the parent returns the child PID.

It is minimal vfork return-value glue using PowerPC64 syscall macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/brk.S

This file implements `_brk` with weak alias `brk` for PowerPC64. It defines hidden 64-bit `__minbrk` and `__curbrk` initialized to `_end`, locates them via TOC addressing, clamps the requested break, invokes `break`, updates `__curbrk`, and returns zero.

The implementation mirrors PowerPC’s `brk` but uses `.quad` data and PowerPC64 addressing/inline error handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/cerror.S

This file contains a disabled `#if 0` implementation of `__cerror` and a comment explaining that syscall stubs now inline this logic. No active code is assembled from the file.

It remains as reference/fallback source for possible future changes. Actual PowerPC64 syscall error behavior is in `SYS.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/fork.S

This file implements PowerPC64 `__fork`. It calls the `fork` syscall and adjusts `%r4`/`%r3` so the child returns zero and the parent returns the child PID.

It is the same return-value transformation pattern used by the PowerPC vfork/fork wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/getcontext.S

This file implements `_getcontext` with weak alias `getcontext` for PowerPC64. It calls the kernel `getcontext`, then stores LR into the saved PC field and zero into the saved `%r3` return-value field.

It uses offsets from `assym.h` and the PowerPC64 syscall macro layer. The adjustment ensures a restored context resumes as a successful `getcontext` return.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/pipe.S

This file implements `_pipe` with weak alias `pipe`. It saves the output pointer, invokes `pipe`, stores file descriptors from `%r3` and `%r4`, returns zero, and uses inline error handling on failure.

It adapts the kernel’s two-register result to the C API’s output array.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/ptrace.S

This file implements PowerPC64 `ptrace` with errno pre-clearing. Reentrant builds save LR and arguments, call `__errno`, clear it, restore arguments, and then trap; non-reentrant builds clear TOC-addressed global `errno`.

After the syscall it returns on success or enters inline error handling on failure. The pre-clear is required for successful `ptrace` calls that return `-1`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/sbrk.S

This file implements `_sbrk` with weak alias `sbrk`. It loads `__curbrk` through TOC addressing, adds the increment, calls `break`, stores the new break on success, and returns the old break.

It is the PowerPC64 cached-program-break wrapper paired with `brk.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/shmat.S

This file defines `shmat` through `RSYSCALL(shmat)`. It contains no local logic beyond the PowerPC64 syscall macro expansion.

It uses inline error handling from `SYS.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/syscall.S

This file contains only a comment that `syscall` is aliased to `__syscall`. The implementation lives in `__syscall.S`.

It is a placeholder preventing duplicate generic syscall code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/Makefile.inc

This make include configures RISC-V libc architecture sources. It adds `__sigtramp2.S`, includes the architecture directory, and conditionally includes softfloat support when `MKSOFTFLOAT` is enabled.

There are no local string or stdlib additions here. It is straightforward architecture source-selection metadata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/SYS.h

This header defines RISC-V libc syscall wrapper macros. `SYSTRAP` loads the syscall number into `t6` and executes `ecall`; normal wrappers then tail-call `__cerror` on the error path and `ret` on success.

`SYSTRAP_NOERROR` pads with `nop`s to match the size of the normal error jump sequence, preserving layout expectations. The header supplies `RSYSCALL`, `WSYSCALL`, `PSEUDO`, and no-error variants used by the RISC-V syscall files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/gdtoa/Makefile.inc

This make include adds RISC-V gdtoa sources `strtof.c`, `strtold_pQ.c`, and `strtopQ.c`. That means the port builds both single-precision and quad/long-double parsing support.

There is no conditional logic in this file. It assumes the RISC-V libc ABI uses the relevant long-double conversion support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/gdtoa/arith.h

This gdtoa configuration header defines `IEEE_LITTLE_ENDIAN` for RISC-V. It tells conversion code the floating-point word layout.

It has no runtime logic. The constant matches the supported NetBSD RISC-V endian configuration here.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/gdtoa/gd_qnan.h

This header defines canonical quiet-NaN patterns for RISC-V gdtoa. Comments cite the RISC-V ISA canonical NaN rule: positive sign and only the quiet bit set in the significand.

It defines single, double, and long-double/quad word patterns in little-endian order. These constants are used when conversion code synthesizes NaN values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/net/Makefile.inc

This file contains only an RCS identifier comment and adds no RISC-V-specific network conversion sources. It is a placeholder include.

Network byte-order implementations must come from shared/generic libc sources for this port.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/stdlib/Makefile.inc

This file contains only an RCS identifier comment and adds no RISC-V-specific stdlib sources. It is a build tree placeholder.

There is no local behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/string/Makefile.inc

This file contains only an RCS identifier comment and adds no RISC-V-specific string sources. Generic string implementations are used unless selected elsewhere.

It has no logic or runtime impact beyond being an included placeholder.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__clone.S

This file implements RISC-V `__clone` and weak `clone`. It validates function and stack pointers, reserves space on the child stack, stores the function pointer and argument there, calls kernel `__clone(flags, stack)`, and distinguishes parent from child using the secondary return value.

In the child it loads the function and argument from the new stack, stores zero in the saved return-address frame slot, calls the function, and tail-calls `_exit` with the result. The wrapper is sensitive to RISC-V stack frame layout and register calling convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__sigtramp2.S

This file implements RISC-V `__sigtramp_siginfo_2` and DWARF signal-frame CFI. It describes all general-purpose registers and a signal-return pseudo-register using offsets into the ucontext located after `siginfo_t` on the stack.

The runtime trampoline computes the ucontext address as `sp + SIGINFO_SIZE`, calls `setcontext` through the no-error syscall path, and calls `exit` if signal return fails. It is critical for signal return and stack unwinding.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__syscall.S

This file implements RISC-V `__syscall`, with strong `_syscall` and weak `syscall` aliases. It invokes the kernel `__syscall` entry using the generic `SYSTRAP` macro, jumps to `__cerror` on error, and returns on success.

Unlike some other architectures, no local argument shuffling is present here. The kernel ABI handles the generic syscall convention through the `__syscall` number.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__vfork14.S

This file implements RISC-V `__vfork14`. It performs the syscall, jumps to `__cerror` on failure, then adjusts `a1` and masks `a0` so the child returns zero and the parent returns the child PID.

The wrapper mirrors `fork.S` return-value logic but uses the `__vfork14` syscall number.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/brk.S

This file implements `_brk` with weak alias `brk`. It defines hidden `__minbrk` and `__curbrk` initialized to `_end`, clamps the requested break with an unsigned comparison, calls the `break` syscall, stores the new break into `__curbrk` on success, returns zero, and jumps to `__cerror` on failure.

It uses RISC-V `lla` and pointer-width macros for symbol and data access. The cached break update is the key libc-side state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/cerror.S

This file defines protected RISC-V `__cerror`. In reentrant builds it saves `ra` and the error value, calls `__errno`, writes errno, restores state, and returns `-1` in `a0` and `a1`.

In non-reentrant builds it uses PC-relative addressing to store the error into global `errno`. This is the shared error path for all RISC-V syscall wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/fork.S

This file implements RISC-V `__fork`. It issues the `fork` syscall, jumps to `__cerror` on failure, then converts the kernel’s `a1` parent/child indicator so the child returns zero and the parent returns the child PID in `a0`.

It is standard fork return-value adaptation for RISC-V libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/getcontext.S

This file implements `_getcontext` with weak alias `getcontext`. It saves the ucontext pointer, calls the kernel `getcontext`, then stores zero into the saved return-value slot and `ra` into the saved PC slot.

The offsets come from `assym.h`. This ensures a restored context resumes as though `getcontext` returned successfully with zero.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/pipe.S

This file implements `_pipe` with weak alias `pipe`. It saves the output pointer in `a2`, invokes the kernel `pipe` syscall, stores descriptors from `a0` and `a1` into the two integer slots, returns zero, and jumps to `__cerror` on failure.

It adapts the RISC-V register-return convention to the C `pipe(int[2])` API.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/ptrace.S

This file implements RISC-V `ptrace` with errno pre-clearing. Reentrant builds save arguments and return address, call `__errno`, clear errno, restore arguments, then invoke the syscall; non-reentrant builds clear global `errno` via PC-relative addressing.

The pre-clear allows callers to distinguish successful `-1` returns from errors. On syscall failure, the wrapper jumps to `__cerror`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/sbrk.S

This file implements `_sbrk` with weak alias `sbrk`. It loads `__curbrk`, adds the requested increment, saves the new break, calls kernel `break`, stores the new value on success, and returns the old break.

It is the RISC-V cached program-break wrapper. Like the other ports, it updates state only on successful kernel acceptance.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/shmat.S

This file defines `shmat` through `RSYSCALL(shmat)`. It has no local logic beyond the syscall macro.

The generated wrapper uses RISC-V `ecall` and `__cerror` semantics from `SYS.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/syscall.S

This file contains only a comment that `__syscall` does all generic syscall work. The actual implementation and aliases live in `__syscall.S`.

It is a placeholder source in the syscall directory.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/Makefile.inc

This make include configures SH3 libc architecture sources. It adds `__sigtramp2.S`, includes the architecture directory, and when softfloat is enabled defines `SOFTFLOAT` and includes the shared softfloat build rules.

A commented `SOFTFLOAT_NEED_FIXUNS` hint shows a possible port-specific conversion need. The file is build configuration only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/SYS.h

This header defines SH3 syscall wrapper macros. `SYSTRAP` loads a syscall number from an inline literal into `r0` and uses `trapa #0x80`; wrappers branch to a local `JUMP_CERROR` block on failure.

It supports PIC and non-PIC paths for jumping to `cerror`, and defines `PSEUDO`, `RSYSCALL`, and `WSYSCALL` macro families. It is the common syscall ABI layer for SH3 assembly wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/gdtoa/Makefile.inc

This make include adds `strtof.c` for SH3 gdtoa support. It has no extra conditionals.

It selects single-precision decimal conversion code for this architecture’s libc build.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/gdtoa/arith.h

This gdtoa configuration header includes `<machine/endian.h>` and defines `IEEE_BIG_ENDIAN` or `IEEE_LITTLE_ENDIAN` based on `BYTE_ORDER`. SH3 supports endian variation, so gdtoa must be configured at compile time.

There is no runtime behavior. The file controls floating-point word interpretation in conversion code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/gdtoa/gd_qnan.h

This header defines SH3 gdtoa quiet-NaN constants. It sets `f_QNAN` to `0x7fa00000` and chooses double-word order based on `BYTE_ORDER`.

These constants are used by gdtoa when generating NaN values. The endian conditional is the important architecture-specific detail.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/Makefile.inc

This make include adds SH3 network byte-order conversion sources: `htonl.c`, `htons.c`, `ntohl.c`, and `ntohs.c`. It is source-selection metadata.

The listed C files contain SH inline assembly for little-endian byte swaps where needed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/htonl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/htonl.c

This C file implements `htonl` for little-endian SH3 builds only. It uses inline assembly `swap.b`, `swap.w`, and `swap.b` to reverse byte order of a 32-bit value, returning the network-order result.

On big-endian builds the function body is not compiled from this file, implying a generic identity or alternate implementation is used elsewhere. The file’s core dependency is SH swap instruction semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/htonl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/htons.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/htons.c

This C file implements `htons` for little-endian SH3 builds only. It uses inline assembly `swap.b` to swap the two bytes of a 16-bit value and returns the network-order result.

On big-endian builds this function is not emitted from this file. Correctness depends on compiler support for the SH inline assembly constraint and byte-swap instruction.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/htons.c -->