# Group Research: group_1186_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_arch_sh3_net_ntohl_c__70df72f54eea

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/ntohl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/ntohl.c

## Summary
Implements the SH3 little-endian `ntohl()` conversion.

## Key Details
- Compiled only when `BYTE_ORDER == LITTLE_ENDIAN`.
- Uses SH `swap.b`, `swap.w`, `swap.b` inline assembly to reverse a 32-bit word.
- Returns a `u_int32_t` network-to-host conversion result.

## Notes
Big-endian SH3 builds do not define a function here, relying on generic/no-op handling elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/ntohl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/ntohs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/ntohs.c

## Summary
Implements the SH3 little-endian `ntohs()` conversion.

## Key Details
- Compiled only for little-endian targets.
- Uses one `swap.b` instruction to reverse the two bytes of a 16-bit value.
- Returns a `u_int16_t`.

## Notes
The function is absent for big-endian builds because network byte order already matches host order.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/ntohs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/softfloat/milieu.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/softfloat/milieu.h

## Summary
Provides the SH3 SoftFloat environment header.

## Key Details
- Includes `sh3-gcc.h` for endian macros, integer typedefs, and inline/literal helpers.
- Defines SoftFloat Boolean literals `FALSE` and `TRUE`.
- Carries the upstream SoftFloat Release 2a provenance and derivative-use notice.

## Notes
This is a small portability layer consumed by the architecture-local SoftFloat implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/softfloat/milieu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/softfloat/sh3-gcc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/softfloat/sh3-gcc.h

## Summary
Defines SH3 GCC-specific SoftFloat integer and compiler settings.

## Key Details
- Maps `<machine/endian.h>` to `BIGENDIAN` or `LITTLEENDIAN`.
- Enables `BITS64`.
- Defines SoftFloat convenience integer types such as `flag`, `uint32`, `bits64`, and signed counterparts.
- Defines `LIT64(a)` as a `long long` literal suffix helper.
- Defines `INLINE` as `static inline`.
- Leaves `FLOAT64_DEMANGLE` and `FLOAT64_MANGLE` as identity macros.

## Notes
The typedefs are tuned for SH3/GCC assumptions rather than strict fixed-width standard typedefs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/softfloat/sh3-gcc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/softfloat/softfloat.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/softfloat/softfloat.h

## Summary
Declares the SH3 SoftFloat public API for software IEEE floating-point operations.

## Key Details
- Defines `float32` and `float64` storage types.
- Leaves `FLOATX80` and `FLOAT128` disabled by default.
- Exposes rounding mode and exception state through NetBSD `<machine/ieeefp.h>` types.
- Declares conversions among integer, single, and double precision formats.
- Optionally declares extended and quadruple precision APIs if their feature macros are enabled.
- Omits selected libgcc-provided 64-bit conversion declarations under `SOFTFLOAT_FOR_GCC`.

## Notes
This header is a declaration layer only; it depends on matching SoftFloat implementation files and `milieu.h` typedefs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/softfloat/softfloat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/stdlib/Makefile.inc

## Summary
Empty SH3 stdlib architecture fragment.

## Key Details
- Contains only the NetBSD revision comment.
- Adds no sources or build flags.

## Notes
SH3 stdlib uses shared libc defaults for this subdirectory.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/string/Makefile.inc

## Summary
Lists SH3 architecture-specific string routines.

## Key Details
- Adds `bcopy.S`, `bzero.S`, `ffs.S`, `memset.S`, `memcpy.S`, and `memmove.S` to libc.
- The local `bcopy.S` and `bzero.S` are wrapper includes around the copy/set implementations.

## Notes
This fragment selects assembly-backed string primitives for SH3.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/string/bcopy.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/string/bcopy.S

## Summary
Builds SH3 `bcopy` from the common local `memcpy.S` source.

## Key Details
- Defines `BCOPY`.
- Includes `memcpy.S`.

## Notes
Behavior is controlled by preprocessor paths inside `memcpy.S`; this file is only a selector wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/string/bcopy.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/string/bzero.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/string/bzero.S

## Summary
Builds SH3 `bzero` from the common local `memset.S` source.

## Key Details
- Defines `BZERO`.
- Includes `memset.S`.

## Notes
The actual zeroing implementation is in `memset.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/string/bzero.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__clone.S

## Summary
Implements SH3 `__clone()` and weak `clone` alias.

## Key Details
- Validates that the function pointer and stack pointer are non-null.
- Issues the `SYS___clone` trap with arguments rearranged as `(flags, stack)`.
- In the child, calls the supplied function with `arg`, then calls `_exit()` with its return value.
- Uses `JUMP_CERROR` on syscall failure or invalid input.
- Handles PIC and non-PIC `_exit` dispatch.

## Notes
Correct register preservation matters because the child entry point and argument are carried across the trap boundary.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__sigtramp2.S

## Summary
Defines the SH3 signal trampoline used for returning from signal handlers.

## Key Details
- Entry symbol is `__sigtramp_siginfo_2`.
- Expects the stack pointer to address the saved `ucontext_t`.
- Calls `setcontext` using the ucontext pointer.
- If `setcontext` returns, exits with the returned error value.
- Provides DWARF CFI for signal-frame unwinding, mapping SH general and special registers to ucontext offsets.

## Notes
The file documents SH-specific stack ordering where `ucontext_t` is placed before `siginfo`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__syscall.S

## Summary
Provides the SH3 `__syscall` raw syscall entry.

## Key Details
- Includes `SYS.h`.
- Expands `RSYSCALL(__syscall)`.

## Notes
All trap mechanics and error handling come from the SH3 syscall macro layer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__vfork14.S

## Summary
Implements SH3 `__vfork14()`.

## Key Details
- Invokes `SYS___vfork14` through `trapa #0x80`.
- Uses the second return register to distinguish parent from child.
- Returns child pid in the parent and zero in the child.
- Jumps to `cerror` on trap failure.

## Notes
The return-value adjustment mirrors SH3 `fork.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/brk.S

## Summary
Implements SH3 `_brk()` with weak public `brk` alias.

## Key Details
- Defines `__minbrk` initialized to `_end`.
- Clamps requested break below `__minbrk` up to `__minbrk`.
- Calls `SYS_break`.
- On success, updates `curbrk` and returns zero.
- Supports PIC and non-PIC access to `__minbrk` and `curbrk`.

## Notes
`curbrk` is shared with `sbrk.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/cerror.S

## Summary
Implements SH3 libc syscall error handling.

## Key Details
- Stores the syscall error number into thread-local `__errno()` for `_REENTRANT` builds.
- Stores into global `errno` for non-reentrant builds.
- Returns `-1` in both `r0` and `r1`.
- Supports PIC and non-PIC global access.

## Notes
All SH3 syscall wrappers that use `JUMP_CERROR` depend on this return convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/fork.S

## Summary
Implements SH3 `__fork()`.

## Key Details
- Invokes `SYS_fork`.
- Uses `r1` to distinguish parent from child.
- Returns zero in the child and the child pid in the parent.
- Dispatches to `cerror` on failure.

## Notes
The function directly uses `trapa #0x80` rather than the generic macro wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/getcontext.S

## Summary
Implements SH3 `_getcontext()` with weak `getcontext` alias.

## Key Details
- Uses `_SYSCALL(_getcontext,getcontext)`.
- Saves procedure register `pr` into the ucontext saved PC slot.
- Writes zero into the saved return-value location so restored contexts return zero.

## Notes
The offsets are architecture ABI constants encoded directly in the assembly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/pipe.S

## Summary
Implements SH3 `_pipe()` with weak public `pipe` alias.

## Key Details
- Uses `_SYSCALL(_pipe,pipe)`.
- Stores returned file descriptors from `r0` and `r1` into the caller-provided array.
- Returns zero on success.

## Notes
Error handling is inherited from `_SYSCALL`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/ptrace.S

## Summary
Implements SH3 `ptrace()` with errno pre-clear semantics.

## Key Details
- Clears `errno` before invoking `SYS_ptrace`.
- Preserves syscall arguments while locating `errno` in reentrant builds.
- Supports PIC and non-PIC errno access.
- Jumps to `cerror` if the trap reports failure.

## Notes
Pre-clearing errno is needed because successful `ptrace` calls can legitimately return `-1`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/sbrk.S

## Summary
Implements SH3 `_sbrk()` with weak public `sbrk` alias.

## Key Details
- Defines `curbrk` initialized to `_end`.
- Computes the requested new break as `curbrk + increment`.
- Calls `SYS_break`.
- On success, returns the old break and updates `curbrk`.
- Supports PIC and non-PIC addressing.

## Notes
The code does not special-case zero increments; it still goes through the break syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/shmat.S

## Summary
Provides SH3 `shmat()` as a regular syscall wrapper.

## Key Details
- Includes `SYS.h`.
- Expands `RSYSCALL(shmat)`.

## Notes
No local ABI adjustment is needed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/syscall.S

## Summary
Provides SH3 `syscall()` and internal `_syscall` wrapper.

## Key Details
- Uses `WSYSCALL(syscall,_syscall)`.
- The weak/public alias behavior is defined by `SYS.h`.

## Notes
This is the generic raw syscall interface for callers supplying a syscall number.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/Makefile.inc

## Summary
Top-level SPARC libc architecture build fragment.

## Key Details
- Adds `__sigtramp2.S`.
- Adds an include path for generated `assym.h`.
- For non-sparc64 SPARC builds, generates division and remainder assembly files from `gen/divrem.m4`.
- Generated files are `rem.S`, `sdiv.S`, `udiv.S`, and `urem.S`.
- Cleans generated outputs.

## Notes
The generated signed division object is named `sdiv.o` to avoid colliding with the ANSI C `div` function.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/SYS.h

## Summary
Defines SPARC syscall assembly macros for libc.

## Key Details
- Includes machine assembly, syscall numbers, and trap constants.
- Defines `CERROR` and `CURBRK` symbol naming for ELF and non-ELF.
- Provides PIC-aware `CALL()` and `ERROR()` helpers.
- Defines `_SYSCALL`, `SYSCALL`, `RSYSCALL`, `PSEUDO`, `WSYSCALL`, and no-error variants.
- Uses `ST_SYSCALL`, `%g1` for syscall number, and `SYSCALL_G5RFLAG` for optimized return handling.

## Notes
This file centralizes the SPARC syscall ABI contract used by all SPARC syscall stubs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/gdtoa/Makefile.inc

## Summary
SPARC gdtoa build fragment.

## Key Details
- Adds `strtof.c`.

## Notes
SPARC uses the shared gdtoa sources with architecture-local arithmetic settings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/gdtoa/arith.h

## Summary
Declares SPARC gdtoa arithmetic byte order.

## Key Details
- Defines `IEEE_BIG_ENDIAN`.

## Notes
This configures gdtoa for big-endian IEEE floating-point layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/gdtoa/gd_qnan.h

## Summary
Defines SPARC gdtoa quiet NaN bit patterns.

## Key Details
- Defines single precision `f_QNAN`.
- Defines double precision high and low words `d_QNAN0` and `d_QNAN1`.

## Notes
The constants follow big-endian word ordering.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/net/Makefile.inc

## Summary
SPARC network byte-order build fragment.

## Key Details
- Adds assembly sources `htonl.S`, `htons.S`, `ntohl.S`, and `ntohs.S`.

## Notes
SPARC uses architecture-specific assembly for host/network conversion routines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/stdlib/Makefile.inc

## Summary
SPARC stdlib build fragment.

## Key Details
- Adds `llabs.S`.
- Marks `imaxabs.S` as not sourced.

## Notes
`llabs.S` also supplies `imaxabs` through weak aliasing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/stdlib/llabs.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/stdlib/llabs.S

## Summary
Implements SPARC `llabs()` and aliases `imaxabs()`.

## Key Details
- Tests the high 32-bit word of the 64-bit argument.
- If negative, subtracts low and high halves from zero using carry propagation.
- Returns the absolute value in `%o0:%o1`.
- Provides weak aliases for `llabs` and `imaxabs` when supported.

## Notes
The implementation handles a 64-bit integer split across SPARC 32-bit argument registers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/stdlib/llabs.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/string/Makefile.inc

## Summary
SPARC string routine build fragment.

## Key Details
- Adds `bzero.S`, `ffs.S`, `memset.S`, and `strlen.S`.

## Notes
Other string routines come from shared libc sources or other architecture defaults.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__clone.S

## Summary
Implements SPARC `__clone()` and weak `clone` alias.

## Key Details
- Validates non-null function and stack arguments.
- Allocates a caller frame on the child stack and stores function and argument there.
- Calls `SYS___clone` with `(flags, stack)`.
- Parent returns the syscall result.
- Child retrieves the saved function and argument, calls it, then exits via `_exit`.
- Invalid inputs return `EINVAL` through `cerror`.

## Notes
The frame allocation is required by the SPARC register-window ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__sigtramp2.S

## Summary
SPARC signal trampoline for siginfo-style signal returns.

## Key Details
- Entry symbol is `__sigtramp_siginfo_2`.
- Computes the `ucontext_t` address from the stack frame, `siginfo_t`, and fixed sizes.
- Calls `setcontext`.
- Calls `exit` if `setcontext` fails.

## Notes
The stack offsets reflect the 32-bit SPARC frame layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__syscall.S

## Summary
Provides SPARC `__syscall`.

## Key Details
- Includes `SYS.h`.
- Expands `RSYSCALL(__syscall)`.

## Notes
Used for raw system calls that need the `__syscall` entry point.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__vfork14.S

## Summary
Implements SPARC `__vfork14()`.

## Key Details
- Uses `SYSCALL(__vfork14)`.
- Converts the kernel's parent/child flag in `%o1` into a return mask.
- Returns zero in the child and child pid in the parent.

## Notes
This mirrors the SPARC `fork` return-value convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/brk.S

## Summary
Implements SPARC `_brk()` with weak `brk` alias.

## Key Details
- Defines `__minbrk` initialized to `_end`.
- Clamps requests below the minimum break.
- Calls `SYS_break`.
- On success, updates `CURBRK` and returns zero.
- Contains PIC and non-PIC code paths.

## Notes
The stored current break symbol comes from `SYS.h` as `CURBRK`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/cerror.S

## Summary
Implements SPARC libc syscall error handling.

## Key Details
- Reentrant builds call `__errno()` and store the error into thread-local errno.
- Non-reentrant builds store the error into global `errno`.
- Returns `-1` in `%o0` and `%o1`.
- Handles PIC and non-PIC global access.

## Notes
SPARC syscall macros branch here through the `ERROR()` macro.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/fork.S

## Summary
Implements SPARC `__fork()`.

## Key Details
- Uses `_SYSCALL(__fork,fork)`.
- Decrements `%o1` to form a parent/child mask.
- Returns zero in child, pid in parent.

## Notes
The parent/child return convention is the same as `__vfork14.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/getcontext.S

## Summary
Implements SPARC `_getcontext()` with weak `getcontext` alias.

## Key Details
- Saves the ucontext pointer before the syscall.
- Calls `SYS_getcontext`.
- Clears the saved `%o0` register in the mcontext.
- Stores return PC and next PC into the saved context.

## Notes
The file writes fixed mcontext offsets for 32-bit SPARC general registers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/pipe.S

## Summary
Implements SPARC `_pipe()` with weak `pipe` alias.

## Key Details
- Saves the user file-descriptor array pointer.
- Calls `SYS_pipe`.
- Stores returned descriptors from `%o0` and `%o1`.
- Returns zero on success.

## Notes
Errors dispatch to the shared `ERROR()` path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/ptrace.S

## Summary
Implements SPARC `ptrace()` with errno pre-clear behavior.

## Key Details
- Clears errno before invoking `SYS_ptrace`.
- Uses `__errno()` in reentrant builds.
- Uses global `errno` in non-reentrant builds, with PIC support.
- Returns normally on success or branches to `ERROR()` on failure.

## Notes
Pre-clearing errno handles successful `ptrace` calls that return `-1`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/sbrk.S

## Summary
Implements SPARC `_sbrk()` with weak `sbrk` alias.

## Key Details
- Defines `CURBRK` initialized to `_end`.
- Computes new break as old break plus increment.
- Calls `SYS_break`.
- Returns the old break and updates `CURBRK` on success.
- Supports PIC and non-PIC addressing.

## Notes
Failure uses shared syscall error handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/shmat.S

## Summary
Provides SPARC `shmat()` syscall wrapper.

## Key Details
- Includes `SYS.h`.
- Expands `RSYSCALL(shmat)`.

## Notes
No architecture-specific result reshaping is needed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/syscall.S

## Summary
Provides SPARC `syscall()` and `_syscall`.

## Key Details
- Uses `WSYSCALL(syscall,_syscall)`.
- Defers trap and error behavior to the macro definitions in `SYS.h`.

## Notes
This is the public raw syscall entry for SPARC libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/Makefile.inc

## Summary
Top-level SPARC64 libc architecture build fragment.

## Key Details
- Adds `__sigtramp2.S`.
- Adds assembler flag `-Wa,-Av9a` for files using v9a extensions.
- Adds `softfloat` to `.PATH` and builds `qp.c`.
- Defines `SOFTFLOATSPARC64_FOR_GCC`, `EXCEPTIONS_WITH_SOFTFLOAT`, and `SOFTFLOAT_NEED_FIXUNS`.
- Includes shared SoftFloat build rules unless `MKSOFTFLOAT == no`.
- When not using shared rules, builds `softfloat-wrapper.c` and adds include paths for softfloat sources.

## Notes
This fragment wires SPARC64 quad-precision support into libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/SYS.h

## Summary
Defines SPARC64 syscall assembly macros for libc.

## Key Details
- Includes machine assembly, syscall numbers, and trap constants.
- Provides PIC-level-specific `JUMP()` to reach `__cerror`.
- Defines syscall wrapper families: `_SYSCALL`, `SYSCALL`, `RSYSCALL`, `PSEUDO`, `WSYSCALL`, and no-error variants.
- Uses `ST_SYSCALL` and `SYSCALL_G5RFLAG`.
- Declares `__cerror`.

## Notes
This is the macro foundation for SPARC64 syscall wrapper files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/gdtoa/Makefile.inc

## Summary
SPARC64 gdtoa build fragment.

## Key Details
- Adds `strtof.c`, `strtold_pQ.c`, and `strtopQ.c`.

## Notes
The selected long-double conversion files reflect SPARC64 quad-precision format.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/gdtoa/arith.h

## Summary
Declares SPARC64 gdtoa arithmetic byte order.

## Key Details
- Defines `IEEE_BIG_ENDIAN`.

## Notes
Used by gdtoa to interpret floating-point word layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/gdtoa/gd_qnan.h

## Summary
Defines SPARC64 gdtoa quiet NaN constants.

## Key Details
- Defines single and double precision quiet NaN words.
- Defines four long-double quiet NaN words for quad precision.

## Notes
Constants are arranged for big-endian SPARC64 floating-point layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/net/Makefile.inc

## Summary
SPARC64 network byte-order build fragment.

## Key Details
- Adds `htonl.S`, `htons.S`, `ntohl.S`, and `ntohs.S`.

## Notes
Uses architecture-specific assembly implementations for byte-order functions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/milieu.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/milieu.h

## Summary
SPARC64 SoftFloat environment header.

## Key Details
- Includes `sparc64-gcc.h`.
- Defines `FALSE` and `TRUE`.
- Carries upstream SoftFloat Release 2a provenance and derivative-use text.

## Notes
This is the architecture-local portability header consumed by SPARC64 SoftFloat code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/milieu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/qp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/qp.c

## Summary
Implements SPARC64 `_Qp*` quad-precision helper entry points on top of SoftFloat `float128`.

## Key Details
- Provides arithmetic helpers such as `_Qp_add`, `_Qp_sub`, `_Qp_mul`, `_Qp_div`, and `_Qp_sqrt`.
- Provides comparison helpers returning SPARC quad ABI comparison values or Boolean results.
- Converts between quad and `float`, `double`, signed integers, unsigned integers, `long`, and `unsigned long`.
- Uses `memcpy` to move bit representations between C floating types and SoftFloat integer storage.
- Implements `_Qp_neg` as subtraction from a static zero value.
- Handles unsigned 64-bit to quad conversion manually when the high bit is set.

## Notes
The file bridges compiler/runtime quad-precision ABI symbols to the software `float128` implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/qp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/softfloat-qp.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/softfloat-qp.h

## Summary
Renames SoftFloat symbols for SPARC64 quad-precision libc use.

## Key Details
- Under `SOFTFLOATSPARC64_FOR_GCC`, maps common SoftFloat global names to `_softfloat_*` names.
- Renames single, double, and quad operations to avoid exporting unintended user-visible names.
- Defines `SOFTFLOAT_FOR_GCC` after namespace renaming when needed.
- Ensures `FLOAT128` code can be compiled while keeping SoftFloat internals out of the normal libc namespace.

## Notes
This is primarily a namespace isolation header for building SPARC64 quad support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/softfloat-qp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/softfloat-wrapper.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/softfloat-wrapper.c

## Summary
Wrapper source for building shared SoftFloat code in the SPARC64 architecture directory.

## Key Details
- Contains only `#include <softfloat.c>`.

## Notes
Used when direct use of `softfloat.c` is inconvenient because of `.PATH` interactions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/softfloat-wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/softfloat.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/softfloat.h

## Summary
Declares the SPARC64 SoftFloat API with quadruple precision enabled.

## Key Details
- Defines `FLOAT128`; leaves `FLOATX80` disabled.
- Includes `softfloat-qp.h` before `<machine/ieeefp.h>` for symbol remapping.
- Defines `float32`, `float64`, and `float128`.
- Declares rounding mode, exception flags, and `float_raise`.
- Declares conversions and operations for single, double, and quad precision.
- Includes unsigned conversion declarations needed by GCC/libc support.

## Notes
Compared with SH3, this header enables quad precision and exposes more conversion routines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/softfloat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/sparc64-gcc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/sparc64-gcc.h

## Summary
Defines SPARC64 GCC-specific SoftFloat portability types.

## Key Details
- Maps machine byte order to `BIGENDIAN` or `LITTLEENDIAN`.
- Enables `BITS64`.
- Defines SoftFloat convenience and exact-width integer typedefs.
- Defines `LIT64(a)` as a `long long` literal helper.
- Defines `INLINE` as `static inline`.
- Leaves float64 mangle/demangle macros as identity transforms.

## Notes
The `uint8` and `int8` convenience typedefs are `int`, matching SoftFloat's portability model.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/sparc64-gcc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/stdlib/Makefile.inc

## Summary
Empty SPARC64 stdlib architecture fragment.

## Key Details
- Contains only the NetBSD revision comment.
- Adds no sources.

## Notes
SPARC64 stdlib mostly uses shared sources, except files selected elsewhere in this group.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/stdlib/abs.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/stdlib/abs.S

## Summary
Implements SPARC64 `abs()`.

## Key Details
- Computes the negated candidate in `%o1`.
- Uses conditional move `movrlz` to return the negated value only when the input is negative.
- Returns through `retl`.

## Notes
This is a compact v9a-style branch-minimized implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/stdlib/abs.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/string/Makefile.inc

## Summary
SPARC64 string routine build fragment.

## Key Details
- Adds `ffs.S`, `memcpy.S`, `memset.S`, and `strlen.S`.
- Marks `bcopy.S` and `bzero.S` as not sourced.

## Notes
This selects SPARC64-specific primitives while excluding older aliases.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__clone.S

## Summary
Implements SPARC64 `__clone()` and weak `clone` alias.

## Key Details
- Validates function and stack pointers.
- Allocates a 64-bit SPARC caller frame on the child stack, accounting for stack bias.
- Stores function pointer and argument into the child frame.
- Calls `SYS___clone` with `(flags, stack)`.
- Parent returns normally; child calls the function then exits.
- Uses `EINVAL` through `ERROR()` for invalid inputs.

## Notes
The implementation is SPARC64 ABI-specific because of register windows, frame size, and stack bias.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__sigtramp2.S

## Summary
SPARC64 siginfo signal trampoline.

## Key Details
- Entry symbol is `__sigtramp_siginfo_2`.
- Uses `BIAS` and `CC64FSZ` to locate `ucontext_t` after the frame and `siginfo_t`.
- Calls `setcontext`.
- Calls `exit` if returning from `setcontext`.

## Notes
The stack offsets are specific to 64-bit SPARC frame layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__syscall.S

## Summary
Provides SPARC64 `__syscall`.

## Key Details
- Includes machine assembly support and `SYS.h`.
- Expands `RSYSCALL(__syscall)`.

## Notes
This is a minimal raw syscall wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__vfork14.S

## Summary
Implements SPARC64 `__vfork14()`.

## Key Details
- Uses `SYSCALL(__vfork14)`.
- Converts `%o1` parent/child flag into a return mask.
- Returns zero in the child and child pid in the parent.

## Notes
Matches SPARC-family fork return handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/brk.S

## Summary
Implements SPARC64 `_brk()` with weak `brk` alias.

## Key Details
- Defines 64-bit `__minbrk` initialized to `_end`.
- Clamps requested break below `__minbrk`.
- Calls `SYS_break`.
- Updates `__curbrk` on success and returns zero.
- Provides code paths for PIC level 2, PIC level 1, and non-PIC.

## Notes
Uses 64-bit loads/stores and SPARC64 conditional moves.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/cerror.S

## Summary
Implements SPARC64 syscall error handling.

## Key Details
- Reentrant builds call `__errno()` and store the error.
- Non-reentrant builds write global `errno`.
- Supports multiple PIC levels and non-PIC addressing.
- Returns `-1` in both return registers.

## Notes
Entry symbol is `__cerror`, which SPARC64 `SYS.h` targets via `ERROR()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/fork.S

## Summary
Implements SPARC64 `__fork()`.

## Key Details
- Uses `_SYSCALL(__fork,fork)`.
- Decrements `%o1` to distinguish child from parent.
- Returns zero in child, pid in parent.

## Notes
The implementation is nearly identical to 32-bit SPARC with SPARC64 syntax.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/getcontext.S

## Summary
Implements SPARC64 `_getcontext()` with weak `getcontext` alias.

## Key Details
- Saves the ucontext pointer.
- Calls `SYS_getcontext`.
- Clears saved `%o0`.
- Stores return PC and next PC into 64-bit mcontext slots.

## Notes
Uses 64-bit register slots and SPARC return-address conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/pipe.S

## Summary
Implements SPARC64 `_pipe()` with weak `pipe` alias.

## Key Details
- Saves pointer to the user descriptor array.
- Calls `SYS_pipe`.
- Stores descriptors from `%o0` and `%o1`.
- Returns zero on success.

## Notes
The descriptor array stores 32-bit ints even on the 64-bit ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/ptrace.S

## Summary
Implements SPARC64 `ptrace()`.

## Key Details
- Calls `__errno()` and clears errno before invoking `SYS_ptrace`.
- Uses a save/restore window around the errno call.
- Returns on success, otherwise dispatches to `ERROR()`.

## Notes
Unlike some other ports, this version always calls `__errno()` rather than a non-reentrant global path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/sbrk.S

## Summary
Implements SPARC64 `_sbrk()` with weak `sbrk` alias.

## Key Details
- Defines 64-bit `__curbrk` initialized to `_end`.
- Computes new break from old break plus increment.
- Calls `SYS_break`.
- Returns old break and updates `__curbrk` on success.
- Supports PIC level 2, PIC level 1, and non-PIC modes.

## Notes
All break bookkeeping is 64-bit.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/shmat.S

## Summary
Provides SPARC64 `shmat()` syscall wrapper.

## Key Details
- Includes `SYS.h`.
- Expands `RSYSCALL(shmat)`.

## Notes
No local result conversion is required.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/syscall.S

## Summary
Provides SPARC64 `syscall()` and `_syscall`.

## Key Details
- Uses `WSYSCALL(syscall,_syscall)`.
- Relies on `SYS.h` for weak alias, trap, and error handling.

## Notes
This is the raw syscall dispatch entry for SPARC64 libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/DEFS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/DEFS.h

## Summary
Minimal VAX assembly definitions header.

## Key Details
- Includes `<machine/asm.h>`.

## Notes
Used by VAX string assembly files for entry and symbol macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/DEFS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/Makefile.inc

## Summary
Top-level VAX libc architecture build fragment.

## Key Details
- Adds `__longjmp14.c` and `__sigtramp3.S`.
- Adds current directory to `CPPFLAGS`.
- Defines `__LIBC12_SOURCE__` for `assym.h` generation.

## Notes
The signal trampoline version is `3` on VAX.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/SYS.h

## Summary
Defines VAX syscall wrapper macros.

## Key Details
- Uses `chmk` through `SYSTRAP(x)`.
- Defines `CERROR` as `__cerror` and `CURBRK` as `__curbrk`.
- Provides syscall, pseudo-call, raw syscall, weak syscall, and no-error macro variants.
- Tests the carry condition to detect syscall failure.
- Emits a local error branch that jumps into `CERROR+2`.

## Notes
The `CERROR+2` convention is part of the VAX error trampoline layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/gdtoa/Makefile.inc

## Summary
VAX gdtoa build fragment.

## Key Details
- Adds `strtof_vaxf.c`.

## Notes
VAX uses a non-IEEE VAX F floating format conversion source.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/gdtoa/arith.h

## Summary
Defines gdtoa arithmetic settings for VAX.

## Key Details
- Defines `VAX`.
- Defines `NO_HEX_FP`.

## Notes
The file disables hexadecimal floating constants for this gdtoa target.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/gdtoa/gd_qnan.h

## Summary
Documents VAX quiet NaN handling for gdtoa.

## Key Details
- Contains no NaN constants.
- Notes that VAX floating point has no NaN.

## Notes
Consumers must not expect IEEE NaN bit patterns on this architecture.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/net/Makefile.inc

## Summary
VAX network byte-order build fragment.

## Key Details
- Adds no local sources.
- Comment says `ntoh*` and `hton*` are provided by `../gen/byte_swap_*`.

## Notes
The empty `SRCS+=` is intentional.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/stdlib/Makefile.inc

## Summary
VAX stdlib build fragment.

## Key Details
- Adds `erand48.c`.
- Marks `erand48_ieee754.c` as not sourced.

## Notes
VAX requires a non-IEEE754 random floating conversion path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/Makefile.inc

## Summary
VAX string routine build fragment.

## Key Details
- Adds `bcmp.S`, `bcopy.S`, `bzero.S`, `ffs.S`, and `memcmp.S`.
- Also adds `memcpy.S`, `memmove.S`, and `memset.S`.

## Notes
The listed assembly routines provide VAX-tuned memory and string primitives.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/bcmp.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/bcmp.S

## Summary
Implements VAX `bcmp()`.

## Key Details
- Compares data in 32-bit word chunks first.
- Handles the remaining one to three bytes byte-by-byte.
- Returns zero for equality and nonzero for inequality.
- Avoids `cmpc3` because it is not portable across all VAX systems.

## Notes
The comment notes this manual approach is still faster than generic C on a MicroVAX II.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/bcmp.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/bcopy.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/bcopy.S

## Summary
Implements VAX `bcopy()`.

## Key Details
- Detects source and destination ordering to choose forward or backward copying for overlap safety.
- Uses VAX `movc3`.
- Splits large copies into chunks no larger than 65535 bytes.
- Returns without work when source and destination are equal.

## Notes
The chunking reflects `movc3` length operand limits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/bcopy.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/bzero.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/bzero.S

## Summary
Implements VAX `bzero()`.

## Key Details
- Uses VAX `movc5` to fill memory with zero bytes.
- Splits large zeroing requests into chunks no larger than 65535 bytes.
- Returns after clearing the final chunk.

## Notes
Like `bcopy`, it handles VAX string-instruction length limits explicitly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/bzero.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/ffs.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/ffs.S

## Summary
Implements VAX `ffs()`.

## Key Details
- Uses the VAX `ffs` instruction over 32 bits.
- Converts the instruction's zero-based bit index to the C one-based result.
- Returns zero when no bit is set.

## Notes
The no-bit case is handled by setting `-1` then incrementing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/ffs.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/index.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/index.S

## Summary
Implements VAX `index()`.

## Key Details
- Searches for the first occurrence of a character in a NUL-terminated string.
- Special-cases search for `'\0'`.
- Returns pointer to match or zero if not found.

## Notes
This is the historical BSD name corresponding to `strchr`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/index.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/memcmp.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/memcmp.S

## Summary
Implements VAX `memcmp()`.

## Key Details
- Compares 32-bit words first.
- Backs up and compares bytes when a word differs.
- Handles trailing bytes after word comparison.
- Returns the unsigned byte difference for the first differing byte, or zero for equality.

## Notes
The fallback from word mismatch preserves standard `memcmp` byte-order semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/string/memcmp.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__clone.S

## Summary
Implements VAX `__clone()` and weak `clone` alias.

## Key Details
- Validates non-null function and stack arguments.
- Rewrites the argument list for the kernel's expected `(flags, stack)` arguments.
- Calls `SYS___clone` via `chmk`.
- Child calls the function with `arg`, then `_exit()` with the return value.
- Invalid inputs return `EINVAL` through `CERROR`.

## Notes
The file warns that modifying the call argument list does not work for `callg` with a read-only argument list.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__sigtramp3.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__sigtramp3.S

## Summary
Defines the VAX siginfo signal trampoline.

## Key Details
- Entry symbol is `__sigtramp_siginfo_3`.
- Uses the VAX `CALLG` argument-list convention to call the signal handler.
- Adjusts `%ap` to point at the `ucontext_t` argument.
- Calls `setcontext` to return from the signal.
- Contains disabled CFI annotations documenting register offsets.

## Notes
The file documents that VAX DWARF register numbers match `_REG_*` constants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__sigtramp3.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__syscall.S

## Summary
Implements VAX `__syscall()`.

## Key Details
- Loads syscall number from the first argument.
- Adjusts `%ap` to skip the first two argument-list entries used by `__syscall`.
- Reduces the VAX argument count by two.
- Executes `chmk` with the requested syscall number.
- Returns on success or jumps to `CERROR+2` on carry set.

## Notes
This differs from `syscall.S`, which skips only one argument.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__vfork14.S

## Summary
Implements VAX `__vfork14()`.

## Key Details
- Saves the caller return address before altering the stack frame.
- Returns out of the current frame before issuing the `vfork` trap.
- Calls `SYS___vfork14`.
- Returns zero in child and pid in parent.
- Handles errors inline, with reentrant and non-reentrant errno paths.

## Notes
The stack-return trick is required because parent and child cannot both safely `ret` from the same VAX frame after `vfork`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/brk.S

## Summary
Implements VAX `_brk()` with weak `brk` alias.

## Key Details
- Uses hidden `__minbrk` and `__curbrk`.
- Clamps requested break below `__minbrk`.
- Calls `SYS_break`.
- Updates `__curbrk` and returns zero on success.
- Jumps to `CERROR+2` on failure.

## Notes
The current and minimum break symbols are hidden libc internals.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/cerror.S

## Summary
Implements VAX syscall error handling.

## Key Details
- Entry symbol is `__cerror`.
- Reentrant builds call `__errno()` and store the saved error.
- Non-reentrant builds store into global `errno`.
- Returns `-1` in `%r0` and `%r1`.

## Notes
Many VAX wrappers jump to `CERROR+2`, entering after the no-op prefix expected by `SYS.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/execl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/execl.S

## Summary
Implements VAX `_execl()` with weak `execl` alias.

## Key Details
- Builds an `argv` vector pointer from the caller's variadic arguments.
- Pushes path and argv pointer.
- Calls `execv`.
- Returns only if `execv` fails.

## Notes
This is an assembly variadic wrapper around the common `execv` implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/execl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/execle.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/execle.S

## Summary
Implements VAX `_execle()` with weak `execle` alias.

## Key Details
- Reads the VAX argument count from the call frame.
- Pushes the final argument as `envp`.
- Pushes the variadic argument vector and path.
- Calls `execve`.

## Notes
The implementation depends on VAX call-frame argument-count metadata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/execle.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/execlp.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/execlp.S

## Summary
Implements VAX `_execlp()` with weak `execlp` alias.

## Key Details
- Builds an `argv` vector pointer from variadic arguments.
- Pushes path and argv pointer.
- Calls `execvp`.

## Notes
This is the PATH-searching counterpart to `execl.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/execlp.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/fork.S

## Summary
Implements VAX `__fork()`.

## Key Details
- Uses `_SYSCALL(__fork,fork)`.
- Tests `%r1` to distinguish parent from child.
- Clears `%r0` in the child.
- Returns pid in parent, zero in child.

## Notes
The kernel places the parent/child flag in `%r1`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/getcontext.S

## Summary
Implements VAX `_getcontext()` with weak `getcontext` alias.

## Key Details
- Calls `SYS_getcontext`.
- Rewrites the caller frame so execution resumes at local label `2`.
- Updates saved AP, SP, FP, and PC fields in the ucontext.
- Clears `%r0` before returning to the original caller.

## Notes
The implementation avoids using `%r4` and `%r5` because they are needed by pthread switch code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/pipe.S

## Summary
Implements VAX `_pipe()` with weak `pipe` alias.

## Key Details
- Uses `_SYSCALL(_pipe,pipe)`.
- Stores returned descriptors from `%r0` and `%r1` into the caller array.
- Returns zero on success.

## Notes
The descriptor pointer is the first user argument.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/ptrace.S

## Summary
Implements VAX `ptrace()` with errno pre-clear behavior.

## Key Details
- Clears thread-local or global errno before the syscall.
- Calls `SYS_ptrace`.
- Returns on success.
- Jumps to `CERROR+2` on carry-set failure.

## Notes
Pre-clearing errno permits callers to disambiguate a valid `-1` result from failure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/sbrk.S

## Summary
Implements VAX `_sbrk()` with weak `sbrk` alias.

## Key Details
- Defines hidden `__minbrk` and `__curbrk` initialized to `_end`.
- Constructs a temporary argument list for `SYS_break`.
- Calls `break` with `__curbrk + increment`.
- Returns the old break and updates `__curbrk` on success.
- Jumps to `CERROR+2` on failure.

## Notes
The wrapper manually rewrites `%ap` to call the kernel with the synthetic argument list.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/shmat.S

## Summary
Provides VAX `shmat()` syscall wrapper.

## Key Details
- Includes `SYS.h`.
- Expands `RSYSCALL(shmat)`.

## Notes
The wrapper uses the standard VAX syscall macro path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/syscall.S

## Summary
Implements VAX `_syscall()` and weak `syscall` alias.

## Key Details
- Loads the syscall number from the first argument.
- Adjusts the argument list to skip that syscall-number argument.
- Reduces the argument count by one.
- Executes `chmk` with the requested syscall number.
- Jumps to `CERROR+2` on failure.

## Notes
This is the normal raw syscall interface; `__syscall.S` has different argument-list adjustment.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/Makefile.inc

## Summary
Top-level x86_64 libc architecture build fragment.

## Key Details
- Adds `__sigtramp2.S` unless building for `RUMPRUN`.
- Adds current directory to `CPPFLAGS`.

## Notes
The signal trampoline is excluded for rumprun builds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/SYS.h

## Summary
Defines x86_64 syscall wrapper macros.

## Key Details
- Uses `syscall` instruction with syscall number in `%eax`.
- Moves `%rcx` to `%r10` before syscall to match the kernel ABI.
- Defines `CERROR` as `__cerror` and `CURBRK` as `__curbrk`.
- Provides syscall, pseudo-call, raw syscall, weak syscall, and no-error macro variants.
- Uses carry flag to detect syscall errors and jump to `__cerror`.

## Notes
This header centralizes the x86_64 userspace-to-kernel syscall ABI for libc assembly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/gdtoa/Makefile.inc

## Summary
x86_64 gdtoa build fragment.

## Key Details
- Adds `strtof.c`, `strtold_px.c`, and `strtopx.c`.

## Notes
The selected long-double sources match the x86 extended-precision format.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/gdtoa/arith.h

## Summary
Declares x86_64 gdtoa arithmetic byte order.

## Key Details
- Defines `IEEE_LITTLE_ENDIAN`.

## Notes
Used by gdtoa conversion code for word ordering.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/gdtoa/gd_qnan.h

## Summary
Defines x86_64 gdtoa quiet NaN bit patterns.

## Key Details
- Defines single and double precision quiet NaN words.
- Defines x87 long-double quiet NaN words.
- Defines `ldus_*` words for unpacked/significand ordering.
- Notes that AMD64 ABI long double has six bytes of tail padding.

## Notes
The constants reflect little-endian IEEE and x87 extended layouts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/net/Makefile.inc

## Summary
x86_64 network byte-order build fragment.

## Key Details
- Adds no object sources locally because byte-swap functions come from `../gen/byte_swap_*.S`.
- Adds lint stubs `Lint_htonl.c`, `Lint_htons.c`, `Lint_ntohl.c`, and `Lint_ntohs.c`.
- Adds these generated lint files to `LSRCS`, `DPSRCS`, and `CLEANFILES`.

## Notes
The fragment exists mostly to keep lint coverage aligned with assembler-provided functions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/Makefile.inc

## Summary
x86_64 stdlib build fragment.

## Key Details
- Adds assembly sources `abs.S`, `div.S`, `labs.S`, and `ldiv.S`.
- Marks `llabs.S`, `imaxabs.S`, and `imaxdiv.S` as not sourced.

## Notes
`labs.S` supplies weak aliases for `llabs` and `imaxabs`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/abs.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/abs.S

## Summary
Implements x86_64 `abs()`.

## Key Details
- Moves 32-bit input from `%edi` to `%eax`.
- Tests sign and negates if negative.
- Returns the absolute value in `%eax`.

## Notes
The `INT_MIN` overflow behavior follows normal two's-complement C library semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/abs.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/div.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/div.S

## Summary
Implements x86_64 `div()` for signed int division.

## Key Details
- Places numerator in `%eax`.
- Uses `cltd` and `idivl %esi`.
- Packs quotient and remainder into `%rax` by shifting `%rdx` and ORing.
- Returns the ABI `div_t` aggregate in registers.

## Notes
This source is public domain.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/div.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/labs.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/labs.S

## Summary
Implements x86_64 `labs()` and `llabs()` family aliases.

## Key Details
- Provides weak aliases for `imaxabs`, `llabs`, and `labs`.
- Tests 64-bit input sign and negates if negative.
- Returns absolute value in `%rax`.

## Notes
On NetBSD x86_64, `long`, `long long`, and `intmax_t` share this implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/labs.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/ldiv.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/ldiv.S

## Summary
Implements x86_64 `ldiv()`.

## Key Details
- Provides weak alias from `ldiv` to `_ldiv` when supported.
- Uses `cqto` and `idivq`.
- Returns quotient and remainder according to the x86_64 aggregate return ABI.

## Notes
The file notes the code was copied from GCC 3.0 output.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/stdlib/ldiv.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/string/Makefile.inc

## Summary
x86_64 string routine build fragment.

## Key Details
- Adds assembly implementations for `bcopy`, `ffs`, `memchr`, `memcpy`, `memmove`, `memset`, `strcat`, `strchr`, `strcmp`, `strcpy`, `strlen`, `strncmp`, `strrchr`, and `swab`.
- Marks `bzero.c` as not sourced.

## Notes
This fragment selects a broad set of x86_64 assembly string primitives.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/string/strncmp.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/string/strncmp.S

## Summary
Implements x86_64 `strncmp()`.

## Key Details
- Returns zero immediately when count reaches zero.
- Compares bytes using an eight-times-unrolled loop.
- Stops on NUL or mismatch.
- Returns unsigned byte difference between the first differing characters.

## Notes
The unroll factor is explicitly chosen as a balance between speed and instruction-cache footprint.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/string/strncmp.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/string/swab.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/string/swab.S

## Summary
Implements x86_64 `swab()`.

## Key Details
- Swaps source and destination registers to use string instructions.
- Clears direction flag.
- Converts byte count to word count.
- Handles an initial group of one to seven words.
- Copies the rest eight words at a time, swapping the two bytes of each word.

## Notes
Odd trailing bytes are ignored because `swab` operates on byte pairs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/string/swab.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__clone.S

## Summary
Implements x86_64 `__clone()` and weak `clone` alias.

## Key Details
- Saves `%r12` and `%r13` for function and argument.
- Validates non-null function and stack pointers.
- Rearranges arguments for the kernel's `__clone` syscall.
- Pushes a dummy return address before the syscall.
- Parent restores stack/registers and returns.
- Child calls the supplied function with `arg`, then `_exit()` with the result.
- Invalid inputs return `EINVAL` through the syscall error path.

## Notes
The file uses `PIC_PLT(_exit)` and has a recent revision timestamp.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__sigtramp2.S

## Summary
x86_64 siginfo signal trampoline.

## Key Details
- Entry symbol is `__sigtramp_siginfo_2`.
- Provides DWARF CFI for signal-frame unwinding from `ucontext_t` register offsets.
- Uses `%r15` as the ucontext pointer.
- Calls `setcontext` directly by syscall.
- If returning, calls `exit(-1)` by syscall.

## Notes
The file includes a one-byte padding `nop` so unwind lookup at return-PC-minus-one lands inside the trampoline region.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__syscall.S

## Summary
Provides x86_64 `__syscall`.

## Key Details
- Includes `SYS.h`.
- Expands `RSYSCALL(__syscall)`.

## Notes
Raw trap behavior is defined in the x86_64 syscall macro layer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__vfork14.S

## Summary
Implements x86_64 `__vfork14()`.

## Key Details
- Pops the caller return address into `%r9` before syscall.
- Calls `SYS___vfork14`.
- Uses `%edx` parent/child flag to return zero in the child and pid in the parent.
- Jumps directly to saved return address on success.
- Restores the return address before dispatching to error handling on failure.

## Notes
Avoiding an ordinary return frame is important for vfork stack sharing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/brk.S

## Summary
Implements x86_64 `_brk()` with weak `brk` alias.

## Key Details
- Defines `__minbrk` initialized to `_end`.
- Clamps requested break below `__minbrk`.
- Calls `SYS_break`.
- Updates `CURBRK` on success and returns zero.
- Provides PIC and non-PIC code paths.

## Notes
This wrapper uses the x86_64 `syscall` instruction through `SYSTRAP`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/cerror.S

## Summary
Implements x86_64 syscall error handling.

## Key Details
- Entry symbol is `__cerror`.
- Saves the error value in `%r12d` across the call to `__errno()`.
- Stores the error into thread-local errno.
- Returns `-1` in `%rax`.

## Notes
This implementation always uses `__errno()` rather than a non-reentrant global errno path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/fork.S

## Summary
Implements x86_64 `__fork()`.

## Key Details
- Uses `_SYSCALL(__fork,fork)`.
- Decrements `%edx`, the kernel parent/child flag.
- Masks `%eax` so the child sees zero and the parent sees child pid.

## Notes
The file follows the common BSD fork dual-return convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/getcontext.S

## Summary
Implements x86_64 `_getcontext()` with weak `getcontext` alias.

## Key Details
- Calls `SYS_getcontext`.
- Stores the caller return address as saved RIP.
- Stores caller stack pointer after the return address as saved user RSP.
- Stores zero into the saved RAX register.
- Returns zero.

## Notes
The source hard-codes offsets for `uc_mcontext`, `_REG_RAX`, `_REG_RIP`, and `_REG_URSP`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/pipe.S

## Summary
Implements x86_64 `_pipe()` with weak `pipe` alias.

## Key Details
- Uses `_SYSCALL(_pipe,pipe)`.
- Stores returned descriptors from `%eax` and `%edx` into the user array.
- Returns zero on success.

## Notes
Descriptor storage uses 32-bit writes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/ptrace.S

## Summary
Implements x86_64 `ptrace()`.

## Key Details
- Saves all four syscall arguments.
- Calls `__errno()` before the syscall.
- Restores arguments and invokes `SYS_ptrace`.
- Dispatches to `__cerror` on carry-set failure.

## Notes
Although the comment says errno is set to zero, the code only calls `__errno()` and restores arguments; it does not visibly store zero in the shown assembly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/sbrk.S

## Summary
Implements x86_64 `_sbrk()` with weak `sbrk` alias.

## Key Details
- Defines `CURBRK` initialized to `_end`.
- Returns current break immediately for zero increment.
- For nonzero increment, computes new break and calls `SYS_break`.
- Returns old break and updates `CURBRK` on success.
- Provides PIC and non-PIC code paths.

## Notes
The non-PIC path saves the increment in `%rsi` to update `CURBRK` after the syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/shmat.S

## Summary
Provides x86_64 `shmat()` syscall wrapper.

## Key Details
- Includes `SYS.h`.
- Expands `RSYSCALL(shmat)`.

## Notes
Uses the standard x86_64 syscall macro path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/syscall.S

## Summary
Provides x86_64 `syscall()` and `_syscall`.

## Key Details
- Uses `WSYSCALL(syscall,_syscall)`.
- Relies on `SYS.h` for aliasing, trap setup, and error handling.

## Notes
This is the public raw syscall entry point.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/atomic/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/atomic/Makefile.inc

## Summary
Build and manual-page fragment for libc atomic operations.

## Key Details
- Adds `${.CURDIR}/atomic` to `.PATH`.
- Registers manuals for atomic add, and, compare-and-swap, decrement, increment, or, swap, generic atomic ops, and memory barriers.
- Defines extensive `MLINKS` for width-specific, type-specific, no-interlock, and new-value-returning atomic APIs.
- Adds aliases such as `atomic.3` to `atomic_ops.3` and `membar.3` to `membar_ops.3`.

## Notes
This fragment is documentation-oriented; it does not list implementation sources in the shown file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/atomic/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/cdb/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/cdb/Makefile.inc

## Summary
Build fragment for libc constant database reader/writer support.

## Key Details
- Adds local `cdb` and common libc `cdb` directories to `.PATH`.
- Builds `cdbr.c` and `cdbw.c`.
- Installs manuals `cdbr.3`, `cdbw.3`, and `cdb.5`.
- Adds manual links for reader APIs such as `cdbr_open`, `cdbr_get`, and `cdbr_close`.
- Adds manual links for writer APIs such as `cdbw_open`, `cdbw_put`, `cdbw_output`, and `cdbw_close`.
- Adds lint suppressions for `cdbw.c` and disables `calloc` transposed-argument warnings for that file.

## Notes
The comment says the lint workaround should eventually be fixed in the code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/cdb/Makefile.inc -->