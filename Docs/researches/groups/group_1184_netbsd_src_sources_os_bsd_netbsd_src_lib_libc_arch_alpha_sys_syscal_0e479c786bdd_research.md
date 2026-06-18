# Group Research: group_1184_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_arch_alpha_sys_syscal_0e479c786bdd

Scope: NetBSD libc architecture-specific assembly, floating-point, string, gdtoa, and syscall support files under `sources/os/bsd/netbsd-src`, which is included by `Docs/research_subset_a.md`.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/syscall.S

This Alpha syscall wrapper includes `SYS.h` and defines the public `syscall` interface as a weak alias to `_syscall` using `WSYSCALL(syscall,_syscall)`. It delegates all trap and error-return mechanics to the Alpha syscall macro layer.

Integration risk is entirely ABI-level: changes must preserve the alias relationship and the generic syscall calling convention expected by libc callers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/Makefile.inc

This ARM libc make fragment adds `__aeabi_read_tp.S` and `__sigtramp2.S` outside rump builds, forces ARM mode for non-earmv7 builds, adds local include search, and includes `arm_initfini.c` for EABI ARM variants. It chooses either softfloat support or VFP hardfloat sources such as `fpgetround.c`, `fpgetsticky.S`, and `fabs_ieee754.S`.

The key dependency is build-configuration correctness: `MKSOFTFLOAT`, `LIBC_MACHINE_ARCH`, and `RUMPRUN` decide whether libc exports softfloat helpers, VFP FP environment accessors, and runtime ARM initialization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/SYS.h

This header defines ARM syscall assembly macros for libc, including `SYSTRAP`, `SYSCALL`, `PSEUDO`, `RSYSCALL`, and `WSYSCALL`. It handles both ARM and Thumb encodings, emits NetBSD SVC traps, and branches to hidden `__cerror` on carry-set syscall failure.

This is the central ABI contract for ARM syscall stubs. Risks are trap-number encoding, Thumb fallback paths, carry-flag error handling, and preservation of return registers across pseudo-syscall wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/gdtoa/Makefile.inc

This gdtoa make fragment adds `strtof.c` for ARM. It relies on shared gdtoa code plus ARM-specific arithmetic and NaN-format headers.

The file is build plumbing only; correctness depends on pairing the generic conversion source with the local endian and quiet-NaN definitions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/gdtoa/arith.h

This header includes `<machine/endian.h>` and maps the platform byte order to gdtoa’s `IEEE_BIG_ENDIAN` or `IEEE_LITTLE_ENDIAN` macros. It lets generic decimal/binary conversion code know ARM’s active object endianness.

The risk is endian macro drift: gdtoa’s layout assumptions must match the target ABI, especially for mixed ARM endian configurations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/gdtoa/gd_qnan.h

This header defines ARM quiet-NaN bit patterns for gdtoa: `f_QNAN` for float and `d_QNAN0`/`d_QNAN1` for double, selected by byte order. Big-endian stores the high quiet-NaN word first, while little-endian reverses the double words.

The integration point is string-to-floating conversion and NaN construction. Any edits must preserve IEEE representation and word ordering.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fabs_ieee754.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fabs_ieee754.S

This VFP assembly file defines `fabsl` and `fabs` entry points and implements absolute value with `vabs.f64 d0, d0`. It returns directly through the ARM assembler macro layer.

It is intentionally minimal hardfloat ABI code. Correctness depends on VFP register calling convention and the file being built only when hardfloat/VFP support is enabled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fabs_ieee754.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpgetmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpgetmask.S

This VFP-only routine implements `fpgetmask`/`_fpgetmask`. It reads `fpscr`, shifts exception-enable bits down from their FPSCR position, masks them with `VFP_FPSCR_CSUM`, and returns the current FP exception enable mask.

The file rejects obsolete FPA builds with a preprocessor error. Risk lies in FPSCR bit mapping and the weak-alias export used by libc namespace handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpgetmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpgetround.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpgetround.c

This C routine implements `fpgetround` by reading VFP `fpscr` with inline assembly and extracting `VFP_FPSCR_RMODE`. Compile-time assertions verify the FPSCR rounding encodings match NetBSD’s `FP_RN`, `FP_RP`, `FP_RM`, and `FP_RZ`.

It is a libc FP environment accessor. The main risk is keeping `<arm/vfpreg.h>` bit definitions aligned with `<ieeefp.h>` public enum values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpgetround.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpgetsticky.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpgetsticky.S

This VFP-only routine implements `fpgetsticky`/`_fpgetsticky`. It reads `fpscr`, masks `VFP_FPSCR_CSUM`, and returns the cumulative floating-point exception flags.

It is low-level FP state access. Correctness depends on using the cumulative-status field, not the exception-enable field used by `fpgetmask`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpgetsticky.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpsetmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpsetmask.S

This routine implements `fpsetmask`/`_fpsetmask` for VFP. It returns the old exception enable mask, clears `VFP_FPSCR_ESUM` in FPSCR, installs the new requested mask shifted into enable-bit position, and writes FPSCR back.

Risk is bit-position translation between public `fp_except` values and FPSCR enable fields. It must preserve unrelated FPSCR state while changing only exception masks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpsetmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpsetround.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpsetround.c

This routine implements `fpsetround` by reading VFP FPSCR, extracting the old rounding mode, toggling only the rounding-mode bits to the requested `fp_rnd`, writing FPSCR, and returning the old mode. Compile-time assertions verify public and hardware rounding constants line up.

It is sensitive to exact bitfield updates. Incorrect masking would corrupt exception or status bits outside the rounding-mode field.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpsetround.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpsetsticky.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpsetsticky.S

This VFP routine implements `fpsetsticky`/`_fpsetsticky`. It reads FPSCR, returns the old cumulative exception flags, replaces only the `VFP_FPSCR_CSUM` bits with the requested flags, and writes FPSCR back.

Its correctness depends on treating sticky flags separately from exception masks and preserving all unrelated FPSCR bits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpsetsticky.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/misc/arm_initfini.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/misc/arm_initfini.c

This constructor initializes ARM libc runtime capability flags. It queries `machdep` sysctl nodes for `fpu_present` and, when the compiler lacks architectural integer divide support, `hwdiv_present`, storing results in hidden libc globals.

This supports AAPCS-sensitive code such as setjmp/longjmp and helper selection. Risk is early-startup behavior: failures deliberately leave defaults unchanged, and repeated constructor calls are suppressed by `_libc_aapcs_initialized`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/misc/arm_initfini.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/net/Makefile.inc

This make fragment documents that ARM `hton*` and `nto*` routines are provided by generated byte-swap assembly in `../gen`, and adds no local sources. `SRCS+=` is intentionally empty.

It is a build placeholder. The risk is assuming missing local files mean missing network byte-order functions; they are supplied elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpeq.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpeq.c

This ARM EABI softfloat helper implements `__aeabi_dcmpeq(float64, float64)`. It returns `float64_eq(a, b)` from the local SoftFloat interface.

It is compiler ABI glue. NaN behavior is delegated to SoftFloat’s equality routine and must match AEABI comparison expectations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpeq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpge.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpge.c

This helper implements `__aeabi_dcmpge` for double-precision SoftFloat values. It returns true when `a` is not less than `b` and both operands compare equal to themselves, excluding unordered NaN inputs.

The explicit self-comparisons are important AEABI NaN handling. Removing them would turn unordered cases into ordered greater-or-equal results.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpgt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpgt.c

This helper implements `__aeabi_dcmpgt` for double-precision SoftFloat values. It returns true when `a` is not less-or-equal to `b` and both operands are ordered.

Its main invariant is unordered handling: NaNs must not produce true greater-than results.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpgt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmple.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmple.c

This helper implements `__aeabi_dcmple(float64, float64)` by returning `float64_le(a, b)`. It is a direct AEABI wrapper around SoftFloat’s double less-or-equal comparison.

Correctness depends on SoftFloat’s signaling and quiet NaN behavior matching the ARM EABI requirements.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmple.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmplt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmplt.c

This helper implements `__aeabi_dcmplt(float64, float64)` as `float64_lt(a, b)`. It is direct compiler support for double less-than comparisons under ARM softfloat.

The file is simple but ABI-facing: symbol spelling and SoftFloat type layout must remain stable.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmplt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpun.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpun.c

This helper implements unordered double comparison for AEABI. It returns true when either operand is NaN, detected by comparing each operand with itself using `float64_eq`.

The code intentionally performs both self-comparisons so signaling NaNs in either operand are processed. That behavior is part of the floating-point exception contract.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_dcmpun.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpeq.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpeq.c

This ARM EABI softfloat helper implements `__aeabi_fcmpeq(float32, float32)`. It returns `float32_eq(a, b)` from the local SoftFloat interface.

It is compiler ABI support for single-precision equality. Symbol name and SoftFloat representation are the important integration points.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpeq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpge.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpge.c

This helper implements `__aeabi_fcmpge` for single-precision SoftFloat values. It returns true when `a` is not less than `b` and both operands are ordered.

The self-comparison checks are required to avoid treating NaNs as greater-or-equal.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpgt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpgt.c

This helper implements `__aeabi_fcmpgt` for single-precision SoftFloat values. It returns true when `a` is not less-or-equal to `b` and neither operand is NaN.

The implementation mirrors the double version and is sensitive to AEABI ordered-comparison semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpgt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmple.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmple.c

This helper implements `__aeabi_fcmple(float32, float32)` by returning `float32_le(a, b)`. It is a thin wrapper around the single-precision SoftFloat comparator.

Its role is compiler-emitted comparison support; behavior depends on the underlying SoftFloat comparison routine.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmple.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmplt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmplt.c

This helper implements `__aeabi_fcmplt(float32, float32)` as `float32_lt(a, b)`. It supports compiler-generated ARM softfloat single less-than comparisons.

The main risk is ABI symbol compatibility, not local algorithm complexity.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmplt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpun.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpun.c

This helper implements unordered single-precision comparison for AEABI. It returns true when either operand is NaN, using `!float32_eq(x, x)` tests on both operands.

Both comparisons are intentionally evaluated to account for signaling NaNs. This is a small but semantically important exception-handling detail.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/__aeabi_fcmpun.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/arm-gcc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/arm-gcc.h

This SoftFloat platform header selects ARM endianness, enables 64-bit integer support, defines SoftFloat integer typedefs, `LIT64`, and `INLINE`. It also defines `FLOAT64_DEMANGLE`/`FLOAT64_MANGLE` for `SOFTFLOAT_FOR_GCC`, accounting for legacy ARM FPA double word ordering versus VFP and big-endian layouts.

The file is foundational type and ABI glue for ARM SoftFloat. Incorrect typedef widths or double-word mangling would corrupt all softfloat helper behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/arm-gcc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/milieu.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/milieu.h

This SoftFloat milieu header includes `arm-gcc.h` and defines boolean constants `FALSE` and `TRUE`. It carries the SoftFloat Release 2a notice and acts as the common local environment header.

It is small but required by the AEABI comparison helpers and SoftFloat headers. Its main dependency is the ARM-specific integer and endian definitions in `arm-gcc.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/milieu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/softfloat.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/softfloat.h

This header declares the ARM-local SoftFloat API and types: `float32`, `float64`, optional `floatx80` and `float128`, rounding-mode globals, exception flags, and conversion/arithmetic/comparison function prototypes. It maps SoftFloat rounding and exception constants to NetBSD `<machine/ieeefp.h>` values.

It is the contract between compiler ABI wrappers and the shared SoftFloat implementation. Risk concentrates in public enum mapping, conditional `SOFTFLOAT_FOR_GCC` declarations, and optional extended-format guards.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/softfloat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/stdlib/Makefile.inc

This ARM stdlib make fragment contains only the NetBSD revision line and adds no local stdlib sources. ARM stdlib support is therefore inherited from common libc or other architecture-neutral code.

The file’s significance is negative build information: there are no ARM-specific stdlib assembly additions here.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/Makefile.inc

This make fragment assembles ARM string routines, including memory functions, `ffs`, `bcopy`, `bzero`, `strcat`, `strcpy`, `strlcpy`, `strncpy`, and conditionally ARMv7 versus non-ARMv7 versions of comparison/length/search functions. It forces `-marm` for listed assembly sources and finally adds `strlcat.S`.

The key build concern is architecture selection: ARMv7 source ordering differs, and all assembly objects depend on this make fragment for rebuild tracking.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/bcopy.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/bcopy.S

This file defines `_BCOPY` and includes `memmove.S`, reusing the ARM memmove implementation to provide `bcopy` semantics. It contains no independent copy loop.

Correctness depends on `memmove.S` honoring the `bcopy` argument order and conditional assembly controlled by `_BCOPY`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/bcopy.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/bzero.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/bzero.S

This file defines `_BZERO` and includes `memset.S` after including `<machine/asm.h>`. It reuses the ARM memset implementation to provide `bzero`.

The important dependency is conditional assembly in `memset.S`: `_BZERO` must select zero-fill semantics and the `bzero(dst, len)` ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/bzero.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/strncat_naive.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/strncat_naive.S

This ARM assembly file implements `strncat`. It returns immediately for zero count, scans the destination to its terminating NUL, copies up to `n` source bytes, stops early on source NUL, and appends a terminating NUL when the count is exhausted.

The implementation is intentionally simple byte-at-a-time code. ABI risk lies in preserving the original destination pointer in `r0` as the return value.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/strncat_naive.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__aeabi_read_tp.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__aeabi_read_tp.S

This file implements the ARM EABI `__aeabi_read_tp` thread-pointer helper. It reads CP15 thread ID register `c13,c0,3` into `r0`; on older ARM architectures, if the register is zero, it falls back to the `_lwp_getprivate` syscall while preserving `r1`.

The helper has strict AAPCS clobber limits. Register preservation and the non-failing syscall fallback are the important correctness points.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__aeabi_read_tp.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__clone.S

This ARM `__clone` implementation validates non-null function and stack pointers, pushes the function and argument onto the child stack, calls the `__clone` syscall with `(flags, stack)`, and distinguishes parent from child using fork-like `r1`. The child pops the function and argument, calls the function, and exits with its return value.

The function is ABI-sensitive for stack layout, Thumb versus ARM instruction variants, and error handling. Null arguments are converted to `EINVAL` through `__cerror`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__sigtramp2.S

This ARM signal trampoline provides DWARF CFI for signal unwinding, describes saved register offsets in `ucontext`, and defines `__sigtramp_siginfo_2`. The trampoline passes the `ucontext` pointer from `r5` to `setcontext`, then calls `exit` with the error code if context restoration returns.

Correctness is tied to kernel signal-frame layout and unwind metadata. The explicit pre-entry `nop` supports unwinder lookup at return-PC-minus-one.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__syscall.S

This file defines the ARM `__syscall` entry by invoking `RSYSCALL(__syscall)` from `SYS.h`. It is the libc wrapper for the quad-aligned syscall-number variant.

The behavior is inherited from the ARM syscall macro layer, including SVC trap generation and `__cerror` handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__vfork14.S

This ARM `__vfork14` wrapper saves `lr` in `r2`, invokes the syscall, handles errors, and normalizes fork-style returns so the child returns zero and the parent returns the child pid. It uses `r1` as the parent/child discriminator.

The code cannot rely on ordinary stack preservation across `vfork`; register choice and return-address preservation are critical.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/brk.S

This ARM `_brk` implementation defines hidden `__minbrk` initialized to `_end`, clamps requested break values below that minimum, invokes the `break` syscall, updates `__curbrk`, and returns zero on success. It supports PIC relocation for the global pointers.

This is heap-boundary state management for libc. Risks include minimum-break clamping, `__curbrk` synchronization, and preserving the requested new break across the syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/cerror.S

This file implements ARM `__cerror`, storing the syscall error number in thread-local `errno` via `__errno` for reentrant builds or global `errno` otherwise. It returns `-1` in both `r0` and `r1`.

It is the shared error path for ARM syscall stubs. Correctness depends on PIC/GOT handling, Thumb return paths, unwind annotations, and preserving the required `-1LL` return convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/fork.S

This file implements `__fork` through the `fork` syscall macro. After the trap it adjusts `r1` so the parent keeps the child pid and the child returns zero.

The wrapper is a small but ABI-critical normalization layer over the kernel’s fork return convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/getcontext.S

This ARM `_getcontext` wrapper saves the argument pointer, performs the `getcontext` syscall, writes the caller return address into the saved PC field, sets saved `r0` to zero, and returns zero. It has a placeholder comment noting softfloat state concerns.

The file depends on `assym.h` ucontext offsets. Any layout change must be reflected here to keep resumed contexts correct.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/pipe.S

This ARM `_pipe` wrapper saves the user `int fd[2]` pointer, invokes the `pipe` syscall, stores returned descriptors from `r0` and `r1`, and returns zero on success. It weak-aliases public `pipe` to `_pipe`.

Its correctness depends on the kernel returning the two descriptors in registers and on preserving the destination pointer across the trap.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/ptrace.S

This ARM `ptrace` wrapper clears `errno` before invoking the syscall, using `__errno` in reentrant builds and global/PIC `errno` otherwise. It then performs the `ptrace` syscall and routes failures to `__cerror`.

The pre-clear is needed because `ptrace` can legitimately return `-1` as data. Register save/restore around `__errno` is the main local ABI risk.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/sbrk.S

This ARM `_sbrk` maintains hidden `__curbrk`, computes the requested new break as current plus increment, invokes the `break` syscall, updates `__curbrk`, and returns the old break. It supports PIC-relative addressing for the state variable.

The key behavior is returning the previous break, not the new one. Overflow and `__curbrk` consistency are the sensitive points.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/shmat.S

This file defines the ARM `shmat` syscall wrapper using `RSYSCALL(shmat)`. All trap and error behavior is inherited from `SYS.h`.

It is a thin libc syscall stub with no local argument reshaping.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/syscall.S

This ARM file exposes the generic `syscall` interface as a weak alias to `_syscall` through `WSYSCALL(syscall,_syscall)`. It includes `SYS.h` for the actual syscall macro implementation.

The file’s only behavior is symbol binding plus standard syscall error handling from the macro layer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/DEFS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/DEFS.h

This HPPA definitions header includes `<machine/asm.h>`. It provides the architecture assembler macro environment to files that include `DEFS.h`.

It is purely a compatibility include shim; correctness depends on the machine header providing the expected assembler macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/DEFS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/Makefile.inc

This HPPA libc make fragment adds `__sigtramp2.S`, adds `bcopy.c`, and appends `-I.` to `CPPFLAGS`. It also carries an OpenBSD provenance comment.

The important build behavior is that signal trampoline support is architecture-local, while `bcopy` is supplied as C rather than the local assembly string set.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/SYS.h

This header defines HPPA libc syscall macros around `SYSCALLGATE`, including `SYSCALL`, `PSEUDO`, `PSEUDO_NOERROR`, `RSYSCALL`, and `WSYSCALL`. It stores and restores `%rp`, places syscall numbers in `%t1`, and branches to hidden `__cerror` on error.

This is the core syscall ABI layer for HPPA. Delay-slot restoration of `%rp` and frame offsets from `<machine/frame.h>` are especially sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/gdtoa/Makefile.inc

This HPPA gdtoa make fragment adds `strtof.c`. It relies on HPPA-specific arithmetic and NaN headers to describe floating-point layout.

The file is build plumbing only; the local format headers carry the conversion-sensitive behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/gdtoa/arith.h

This gdtoa arithmetic header declares `IEEE_BIG_ENDIAN` for HPPA. It informs generic conversion code that floating-point words use big-endian layout.

The file is tiny but important for correct decimal conversion and NaN word ordering.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/gdtoa/gd_qnan.h

This header defines HPPA quiet-NaN patterns for float, double, and, under `_LP64`, long double words. HPPA uses `f_QNAN 0x7fa00000` and big-endian double word ordering.

The unusual float quiet-NaN payload differs from several other architectures, so generic replacement would be risky.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/net/Makefile.inc

This HPPA network make fragment adds C sources for byte-order conversion: `ntohl.c`, `ntohs.c`, `htons.c`, and `htonl.c`. Unlike some architectures, it does not point to generated byte-swap assembly here.

The file affects which libc network conversion implementations are compiled for HPPA.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/stdlib/Makefile.inc

This HPPA stdlib make fragment contains only the revision line and adds no architecture-specific sources. HPPA stdlib behavior is inherited from common libc code.

Its significance is that there are no local stdlib assembly overrides in this file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/Makefile.inc

This HPPA string make fragment adds `bcmp.S`, `bzero.S`, and `ffs.S`. It comments out `strlcpy.S`, noting NetBSD does not currently let architectures supply that file and that this version was untested.

This directly explains why `strlcpy.S` exists in the tree but is not enabled by the make fragment.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/bcmp.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/bcmp.S

This HPPA assembly implements `bcmp(src, dst, count)`. It loops byte-by-byte using post-incrementing loads, exits on count exhaustion or mismatch, and returns the byte difference in `%ret0`.

The routine is simple but ABI-sensitive for argument registers and branch delay behavior. It returns zero only when all compared bytes match.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/bcmp.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/bzero.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/bzero.S

This HPPA assembly implements `bzero(dst, count)`. It chooses byte stores for small counts and optimized word/block clearing for larger ranges using HPPA store-bytes and store-word instructions, then handles unaligned cleanup bytes.

The implementation relies on HPPA alignment and store semantics. Edge cases are zero or tiny counts and final partial-word cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/bzero.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/ffs.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/ffs.S

This HPPA assembly implements `ffs`. It returns zero for input zero, otherwise performs a binary-search style sequence over low 16, 8, 4, 2, and 1-bit groups to compute the one-based position.

The comments describe bit numbering in HPPA/VAX-style terms. Correctness depends on preserving NetBSD `ffs` semantics despite architecture-specific bit extraction instructions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/ffs.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/strlcpy.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/strlcpy.S

This HPPA assembly implements `_strlcpy` and weakly aliases `strlcpy` to it. It copies until NUL or destination capacity, always NUL-terminates when capacity permits, then scans the remainder of the source to return the full source length.

The local makefile comments state this file is not currently enabled. If enabled, return length and zero-size destination behavior are the critical compatibility points.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/strlcpy.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__clone.S

This HPPA `__clone` validates function and stack pointers, builds a child-stack frame containing function and argument, calls the `__clone` syscall with flags and stack, returns directly in the parent, and in the child reloads the function and argument, calls through `$$dyncall`, then exits with the function result.

The file is sensitive to HPPA frame layout, `%r19` linkage handling, and the parent/child discriminator returned in `%ret1`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__sigtramp2.S

This HPPA signal trampoline supplies CFI for signal-frame unwinding, handles the HPPA PLABEL form of signal-handler addresses, calls the handler, then invokes `setcontext` with the saved `ucontext`. If `setcontext` returns, it calls `exit` with the returned error.

Correctness is tied to the kernel signal frame, HPPA PLABEL/linkage conventions, and the DWARF alternate return column used for signal return unwinding.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__syscall.S

This HPPA file includes `SYS.h` and defines `__syscall` via `RSYSCALL(__syscall)`. It relies entirely on the HPPA syscall macro layer for trap and error handling.

It is a thin wrapper for the special libc `__syscall` entry point.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__vfork14.S

This HPPA `__vfork14` wrapper avoids stack saves because the child can disturb the parent stack. It saves `%rp` in `%t4`, relies on kernel preservation of that register, invokes `SYS___vfork14`, restores `%rp`, and normalizes parent/child return values.

The file documents a special kernel/libc contract: syscall entry code preserves `%t4` specifically for this wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/brk.S

This HPPA `_brk` defines `__minbrk` initialized to `_end`, clamps requested break below that minimum, saves the requested break in the frame, invokes `break`, and updates hidden `__curbrk`. It handles PIC and non-PIC addressing separately.

The main integration concern is frame usage around the syscall and correct storage of the new break value on success.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/cerror.S

This HPPA `__cerror` stores the error number from `%t1` into thread-local `errno` via `__errno` for reentrant builds, or into global/PIC `errno` otherwise. It returns `-1` in both `%ret0` and `%ret1`.

This is the common syscall error target from `SYS.h`. `%rp`, `%r19`, and frame-slot preservation matter in the reentrant path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/fork.S

This HPPA `__fork` wrapper invokes the `fork` syscall and adjusts `%ret1` so the child returns zero while the parent keeps the child pid. It mirrors the usual BSD fork return normalization.

Correctness depends on the kernel returning parent/child state in `%ret1`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/getcontext.S

This HPPA `_getcontext` wrapper invokes `getcontext`, then stores `%rp` and `%rp + 4` into the saved PCOQ head/tail slots and stores zero in the saved return register slot. It weak-aliases `getcontext` to `_getcontext`.

It depends on `assym.h` ucontext offsets and HPPA’s split program-counter queue representation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/pipe.S

This HPPA `_pipe` wrapper saves the user descriptor array pointer, invokes `pipe`, stores returned descriptors from `%ret0` and `%ret1`, and returns zero. It provides a weak alias from `pipe` to `_pipe`.

The ABI dependency is the two-register return convention for pipe descriptors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/ptrace.S

This HPPA `ptrace` wrapper first calls `__cerror` with error zero to clear `errno`, while saving all syscall arguments and linkage state in a stack frame. It then restores arguments, performs the `ptrace` syscall, and returns through the normal syscall path.

The pre-clear handles legitimate `-1` ptrace results. Frame layout and `%r19` restoration are the important local hazards.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/sbrk.S

This HPPA `_sbrk` defines hidden `__curbrk`, computes the new break from the current break plus increment, invokes `break`, returns the old break, and stores the new break on success. It has PIC and non-PIC address paths.

The key invariant is `sbrk(0)` returning the current break without changing it, while nonzero increments update `__curbrk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/shmat.S

This HPPA file defines `shmat` via `RSYSCALL(shmat)`. It uses the standard HPPA syscall macro path.

There is no local argument reshaping or special return handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/syscall.S

This HPPA file exposes `syscall` as a weak alias to `_syscall` with `WSYSCALL(syscall,_syscall)`. The actual trap mechanics come from `SYS.h`.

It is symbol and macro plumbing for the generic libc syscall entry.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/Makefile.inc

This i386 libc make fragment adds `__sigtramp2.S` outside rump builds and adds `-I.` to `CPPFLAGS`. It has no other local source selection.

The file mainly controls whether the i386 signal trampoline is included in libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/SYS.h

This i386 syscall macro header defines trap macros using `int $0x80` or `sysenter` under `I686_LIBC`, error routing to `__cerror`, and standard `PSEUDO`, `RSYSCALL`, and `WSYSCALL` wrappers. It also handles PIC jumps to `__cerror`.

This is central i386 libc ABI code. Stack layout, `%eax` syscall numbers, carry-flag error returns, and optional `sysenter` register setup are the key risks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/gdtoa/Makefile.inc

This i386 gdtoa make fragment adds `strtof.c`, `strtold_px.c`, and `strtopx.c`. It enables both ordinary float conversion and x87 extended-precision conversion support.

The dependency is i386’s 80-bit long double ABI, reflected by companion gdtoa headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/gdtoa/arith.h

This gdtoa arithmetic header defines `IEEE_LITTLE_ENDIAN` for i386. It informs generic conversion code of i386 floating-point word ordering.

It is required for correct float/double and extended conversion data layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/gdtoa/gd_qnan.h

This header defines quiet-NaN patterns for i386 float, double, and 80-bit long double storage units. It notes that two bytes of tail padding follow per the i386 ABI.

The long-double layout details are the main risk. Generic NaN definitions would not capture i386 x87 ABI padding and word ordering.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/net/Makefile.inc

This i386 network make fragment adds no actual `hton*`/`nto*` sources because generated byte-swap assembly provides them. It does add lint stub sources such as `Lint_htonl.c` and tracks them in `LSRCS`, `DPSRCS`, and `CLEANFILES`.

This preserves lint/build metadata even though runtime implementations are elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/Makefile.inc

This i386 stdlib make fragment adds assembly implementations for `abs`, `div`, `labs`, `ldiv`, and `llabs`, and explicitly lists `imaxabs.S` under `NO_SRCS`. `imaxabs` is handled through aliasing in `llabs.S`.

The file selects small i386 assembly overrides for common integer stdlib routines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/abs.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/abs.S

This i386 assembly implements `abs(int)`. It loads the stack argument into `%eax`, tests the sign, negates if negative, and returns.

It relies on normal i386 cdecl argument layout and leaves overflow behavior for `INT_MIN` as the machine instruction naturally produces.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/abs.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/div.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/div.S

This i386 assembly implements `div`. It uses a hidden structure-return pointer in `%ebx`, performs signed division with `cdq` and `idiv`, stores quotient and remainder into the result object, returns the result pointer, and uses `ret $4`.

The calling convention is the key point: this is not a plain two-argument scalar return but a struct-return ABI implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/div.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/labs.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/labs.S

This i386 assembly implements `labs(long)` identically to `abs` for 32-bit long. It loads the argument, tests sign, negates if negative, and returns in `%eax`.

The file exists because `long` is 32-bit on i386 and can share the same machine sequence as `abs`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/labs.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/ldiv.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/ldiv.S

This i386 assembly implements `ldiv` using the same structure-return convention and signed `idiv` sequence as `div`. It stores quotient and remainder into the caller-provided result object.

Because i386 `long` is 32-bit, `ldiv` mirrors `div` at the instruction level.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/ldiv.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/llabs.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/llabs.S

This i386 assembly implements 64-bit `llabs` and aliases `imaxabs` to it. It loads the high word into `%edx` and low word into `%eax`, checks the sign bit in `%edx`, and performs two-word negation when negative.

The two-register 64-bit return ABI is the main dependency. Alias handling differs depending on `WEAK_ALIAS`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/llabs.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/Makefile.inc

This make fragment adds i386 assembly string and memory routines including `bcopy`, `bzero`, `ffs`, `memchr`, `memcpy`, `memmove`, `memset`, `strcat`, `strchr`, `strcmp`, `strcpy`, `strlen`, `strncmp`, `strrchr`, and `swab`.

It is the source selection point for i386 optimized string routines. Some wrappers include shared assembly files under compatibility macro names.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/bcmp.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/bcmp.S

This i386 assembly implements `bcmp`. It saves `%edi` and `%esi`, compares full words with `repe cmpsl`, then compares remaining bytes with `repe cmpsb`, returning zero for equality and one for any mismatch.

The routine deliberately returns boolean mismatch, not a byte difference like `memcmp`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/bcmp.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/bcopy.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/bcopy.S

This file defines `BCOPY` and includes `memcpy.S`, reusing shared i386 copy assembly to build `bcopy`. The macro selects compatibility behavior in the included implementation.

Correctness depends on the included file adapting argument order and overlap semantics as required by `bcopy`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/bcopy.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/bzero.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/bzero.S

This file defines `BZERO` and includes `memset.S`. It reuses the i386 memset assembly to provide `bzero`.

The build relies on conditional code in `memset.S` to set the fill byte to zero and expose the `bzero` ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/bzero.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/index.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/index.S

This compatibility wrapper defines `INDEX` and includes `strchr.S`. It provides the historical `index` function through the shared character-search implementation.

The only local behavior is macro selection of symbol naming and calling semantics in `strchr.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/index.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/rindex.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/rindex.S

This compatibility wrapper defines `RINDEX` and includes `strrchr.S`. It provides the historical `rindex` interface using the shared reverse character-search implementation.

Correctness is delegated to `strrchr.S` and its conditional symbol selection.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/rindex.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/strncmp.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/strncmp.S

This i386 assembly implements `strncmp` with an eight-way unrolled byte loop. It stops on count exhaustion, NUL, or mismatch, and returns the unsigned byte difference for mismatches or zero for equality.

The unsigned comparison path using `movzbl` is essential for C string comparison semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/strncmp.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/swab.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/swab.S

This i386 assembly implements `swab`, swapping adjacent bytes while copying from source to destination. It processes an initial remainder of one to seven words, then unrolls the main loop eight 16-bit words at a time using `lodsw`, `rorw $8`, and `stosw`.

It ignores a trailing odd byte by shifting the count right by one, matching `swab` semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/swab.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__clone.S

This i386 `__clone` validates non-null function and stack pointers, builds the child stack with the function argument, invokes the `__clone` syscall with flags and stack, returns in the parent, and in the child calls the function then `_exit` with its return value. Null input returns `EINVAL` through the syscall error path.

The code is stack-layout sensitive and preserves `%ebp` around the operation. It also has PIC handling for `_exit`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__sigtramp2.S

This i386 signal trampoline provides CFI for signal-frame unwinding and defines `__sigtramp_siginfo_2`. It computes the `ucontext` address on the stack, places it in the argument slot for `setcontext`, invokes `setcontext`, and exits with `-1` if restoration returns.

The fixed offsets and CFI register mappings are tied to NetBSD’s i386 signal-frame layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__syscall.S

This i386 `__syscall` wrapper pops the return address, syscall number, and quad-alignment junk word from the stack, restores a consistent frame, performs `int $0x80`, and routes carry-set failures to `__cerror`. It preserves stack consistency by pushing the return address back twice.

The file exists for the special `__syscall` ABI where the syscall number is passed as a 64-bit-aligned quantity.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__vfork14.S

This i386 `__vfork14` wrapper pops the return address into `%ecx`, invokes `OSYSTRAP(__vfork14)` without clobbering it, normalizes child return to zero by decrementing `%edx` and ANDing `%eax`, and jumps back through `%ecx`. On error it restores the return address and branches to `__cerror`.

Avoiding normal stack use is important because `vfork` shares the address space and stack until exec or exit.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/brk.S

This i386 `_brk` defines `__minbrk`, clamps requested breaks below `_end`, invokes the `break` syscall using `OSYSTRAP`, updates `__curbrk`/`CURBRK`, and returns zero on success. It has separate PIC and non-PIC paths.

The wrapper must avoid clobbering `%ecx`, which holds the requested break across the trap.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/cerror.S

This i386 `__cerror` pushes the error code in `%eax`, calls `__errno`, stores the error into the returned errno slot, then returns `-1` in both `%eax` and `%edx`. It uses PIC prologue/epilogue around the call and marks `CERROR` protected.

This is the common i386 syscall error return path. The dual-register `-1` supports functions returning 64-bit values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/fork.S

This i386 `__fork` wrapper invokes the `fork` syscall and then normalizes the return convention: `%edx` indicates parent versus child, and `%eax` is masked so the child returns zero.

It is a compact fork ABI adapter over the kernel’s two-register return convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/getcontext.S

This i386 `_getcontext` wrapper invokes `getcontext`, then updates the saved `%eip`, `%esp`, and return-value register in the target `ucontext` so later restoration resumes as if `getcontext` returned zero. It weak-aliases public `getcontext`.

The hardcoded offsets reflect the i386 `ucontext_t` layout. They are the main maintenance hazard.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/pipe.S

This i386 `_pipe` wrapper invokes the `pipe` syscall, stores `%eax` and `%edx` into the caller’s descriptor array, and returns zero. It weak-aliases `pipe` to `_pipe`.

The code depends on the kernel returning the two file descriptors in `%eax` and `%edx`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/ptrace.S

This i386 `ptrace` wrapper calls `__errno`, clears `errno` to zero, performs the `ptrace` syscall, and sends carry-set failures to `__cerror`. Clearing `errno` is necessary because successful `ptrace` may return `-1`.

The file is sensitive to PIC call setup and preserving syscall arguments across the errno clear path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/sbrk.S

This i386 `_sbrk` maintains `CURBRK`, returns the current break immediately for zero increment, otherwise computes and requests a new break, updates `CURBRK`, and returns the old break. It has PIC and non-PIC implementations.

The critical behavior is preserving the old break as the return value while updating the global only after syscall success.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/shmat.S

This i386 file defines `shmat` via `RSYSCALL(shmat)`. The syscall and error behavior are inherited from `SYS.h`.

There is no local special-case argument or return handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/syscall.S

This i386 `_syscall` wrapper pops the return address and syscall number, performs `int $0x80`, restores a consistent stack frame, and returns or branches to `__cerror`. It weak-aliases public `syscall` to `_syscall`.

It is distinct from `__syscall.S` because it handles the ordinary syscall-number stack layout rather than the quad-aligned variant.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/Makefile.inc

This IA-64 make fragment adds `__sigtramp2.S`. It contains no conditional logic or other source additions.

The file is simple build inclusion for IA-64 signal trampoline support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/SYS.h

This IA-64 syscall macro header defines return, syscall, pseudo-syscall, and weak-syscall wrappers around `CALLSYS_NOERROR` and `CALLSYS_ERROR`. It branches to `__cerror` when `r10` indicates an error and uses IA-64 entry macros with placeholder argument counts.

The file is the IA-64 syscall ABI abstraction. It assumes lower-level macros define the actual kernel call sequence.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/gdtoa/Makefile.inc

This IA-64 gdtoa make fragment adds `strtof.c`. It relies on IA-64-specific layout headers for arithmetic and quiet-NaN definitions.

The file is build plumbing for generic gdtoa conversion on IA-64.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/gdtoa/arith.h

This IA-64 gdtoa arithmetic header defines `IEEE_LITTLE_ENDIAN` and, when `_IEEE_FP` is not defined, `Sudden_Underflow`. It communicates IA-64 floating-point layout and underflow behavior to gdtoa.

The `Sudden_Underflow` conditional is the notable architecture-specific conversion behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/gdtoa/gd_qnan.h

This header defines IA-64 quiet-NaN patterns for float and little-endian double word storage. It uses the common `f_QNAN 0x7fc00000` and double words `0x0`, `0x7ff80000`.

It is used by gdtoa for NaN construction during string conversion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/net/Makefile.inc

This IA-64 network make fragment is an explicit stub and adds no sources. It contains only a revision line and `XXX: Stub` comment.

This indicates IA-64 has no local net byte-order implementation selected here.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/stdlib/Makefile.inc

This IA-64 stdlib make fragment contains only the revision line and no source additions. IA-64 stdlib routines are provided by common libc or other build paths.

It is a no-op architecture make fragment.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/string/Makefile.inc

This IA-64 string make fragment contains only a revision line and blank content. It adds no architecture-specific string assembly or C sources.

This means IA-64 string routines are inherited from shared libc implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/__clone.S

This IA-64 `__clone` file is an unimplemented stub. It declares the `clone` weak alias when enabled, defines `__clone`, and executes `break.i 1` with comments noting implementation is still needed.

The file is intentionally nonfunctional as a syscall wrapper. Any user of clone on this port would hit the break instruction.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/__sigtramp2.S

This IA-64 signal trampoline is marked as needing signal-handling fixes. It defines `__sigtramp_siginfo_2`, calls `exit` through `CALLSYS_NOERROR(exit)`, and has comments about needing the `ucontext` pointer and `setcontext`.

It is a placeholder rather than a complete trampoline. Signal return behavior is not implemented here.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/__syscall.S

This IA-64 file includes `SYS.h` and defines `__syscall` via `RSYSCALL(__syscall)`. It uses the standard macro path for trap and error behavior.

It is a thin wrapper for the special libc `__syscall` entry.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/__vfork14.S

This IA-64 `__vfork14` wrapper invokes `SYSCALL(__vfork14)`, returns with `RET`, and comments that child/parent return values need attention. Unlike other architectures in this group, it does not normalize the child return value.

The file appears incomplete or minimally ported. Return semantics are explicitly flagged by the source comment.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/brk.S

This IA-64 `_brk` defines `__minbrk`, clamps the requested break below `_end`, stores the request on stack, invokes `break`, updates imported `__curbrk`, and returns zero. It uses IA-64 GP-relative `@ltoff` addressing.

The wrapper is functional heap-boundary management. Risks include stack spill use and correct global-pointer addressing for `__minbrk` and `__curbrk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/cerror.S

This IA-64 `__cerror` saves `ar.pfs`, `rp`, and the error code, calls `__errno`, stores the error, restores saved state, and returns `-1` in `ret0`. It uses IA-64 register stack conventions.

The file is the IA-64 syscall error handler. Preserving `ar.pfs` and `rp` is essential.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/fork.S

This IA-64 `__fork` wrapper calls `CALLSYS_ERROR(fork)` and returns. A comment notes that child return value handling is still needed.

Unlike mature ports, this file does not normalize parent/child fork returns locally.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/getcontext.S

This IA-64 file is only a stub comment and revision line. It contains no implementation of `getcontext`.

Any getcontext support for IA-64 must come from elsewhere or remains absent for this path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/pipe.S

This IA-64 `_pipe` wrapper saves the descriptor array pointer, calls `pipe`, stores `ret0` and `ret1` as two 32-bit descriptors, returns zero, and weak-aliases `pipe` to `_pipe`. A comment notes parameter passing should be revisited.

The implementation assumes the kernel returns both descriptors in IA-64 return registers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/ptrace.S

This IA-64 `ptrace` file is an unimplemented stub. The `ptrace` entry executes `break.i 1` and comments say implementation is needed.

It is not a functional ptrace syscall wrapper on this path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/sbrk.S

This IA-64 `_sbrk` defines `__curbrk`, returns the current break immediately for zero increment, otherwise computes the new break, invokes `break`, returns the old break, and updates `__curbrk`. It uses IA-64 GP-relative loads.

The behavior matches standard `sbrk`: return old break and update only after successful kernel break change.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/shmat.S

This IA-64 file defines `shmat` through `RSYSCALL(shmat)`. It relies on the IA-64 syscall macro layer for trap and error behavior.

There is no local argument adaptation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/syscall.S

This IA-64 file exposes `syscall` as a weak alias to `_syscall` using `WSYSCALL(syscall,_syscall)`. Behavior is inherited from `SYS.h`.

It is symbol-binding plumbing for the generic syscall entry.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/DEFS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/DEFS.h

This m68k definitions header includes `<machine/asm.h>`. It provides assembler macro definitions to older m68k libc assembly files.

The file is a compatibility include shim with no independent logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/DEFS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/Makefile.inc

This m68k libc make fragment adds signal, thread-pointer, mmap, and selected syscall assembly sources, adds local include search, and chooses softfloat or hardfloat support based on `MKSOFTFLOAT`, `MKLIBCSOFTFLOAT`, `SOFTFLOAT_BITS`, and `MACHINE_ARCH`. For hardfloat non-m68000 builds, it includes `hardfloat/Makefile.inc`.

This file is the architecture’s floating-point build switch. It decides whether libc uses shared SoftFloat, m68k softfloat environment glue, or 68881-style hardfloat helper assembly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/SYS.h

This m68k syscall macro header defines `SYSTRAP` as loading `SYS_x` into `%d0` and executing `trap #0`, plus standard syscall, pseudo-syscall, raw-syscall, and weak-syscall wrappers. Errors branch on carry set to hidden `__cerror`.

It is the central m68k libc syscall ABI layer. Trap encoding, `%d0` syscall number use, and carry-flag error handling are critical.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/gdtoa/Makefile.inc

This m68k gdtoa make fragment always adds `strtof.c`. For `m68k` after normalizing `m68ksf` to `m68k`, it also adds `strtold_pxL.c` and `strtopxL.c` for extended long-double conversion.

The conditional reflects m68k long-double support differences between architecture variants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/gdtoa/arith.h

This gdtoa arithmetic header defines `IEEE_BIG_ENDIAN` for m68k. It informs generic conversion code of the architecture’s floating-point word order.

It is required for correct binary/decimal conversion layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/gdtoa/gd_qnan.h

This header defines m68k quiet-NaN patterns for float and double, plus extended long double words when not building for `__mc68010__`. It uses big-endian double word ordering.

The conditional extended format is the key architecture-specific detail for gdtoa.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/Makefile.inc

This m68k hardfloat make fragment adds `modf`, FP environment accessors, compiler floating-point arithmetic/conversion helpers, unsigned conversion helpers, and comparison helpers for single and double precision. It is included only when hardfloat support is selected for capable m68k targets.

The file makes 68881-compatible FPU routines available even to softfloat programs in some configurations, as noted by its comments.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/adddf3.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/adddf3.S

This m68k hardfloat helper implements `__adddf3` for double addition. It loads the first stack-passed double into `%fp0`, adds the second, and for non-SVR4 ABI stores the double result through the stack into `%d0/%d1`.

It is compiler runtime support. ABI differences in floating-point return registers versus integer register pairs are the key risk.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/adddf3.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/addsf3.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/addsf3.S

This m68k hardfloat helper implements `__addsf3` for single-precision addition. It loads the first float into `%fp0`, adds the second, and for non-SVR4 ABI moves the result to `%d0`.

It is compiler-emitted arithmetic support and depends on 68881/ColdFire-compatible FPU instruction behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/addsf3.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/cmpdf2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/cmpdf2.S

This helper implements `__cmpdf2` for double comparison, returning `1` for greater-than, `-1` for less-than, and `0` for equality. It uses FPU compare instructions and has a ColdFire-specific equality path.

The return convention is libgcc-compatible. FPU condition-code interpretation is the important correctness point.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/cmpdf2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/cmpsf2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/cmpsf2.S

This helper implements `__cmpsf2` for single-precision comparison, returning `1`, `-1`, or `0` for greater, less, or equal. It mirrors the double version using `fmoves`/`fcmps`.

Correctness depends on m68k FPU compare flags and the ColdFire-specific fallback branch sequence.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/cmpsf2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/divdf3.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/divdf3.S

This helper implements `__divdf3` for double division. It loads the dividend into `%fp0`, divides by the second stack-passed double, and returns the result through `%d0/%d1` for non-SVR4 ABI.

It is a direct compiler runtime FPU wrapper. Stack offsets and return ABI are the main risks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/divdf3.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/divsf3.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/divsf3.S

This helper implements `__divsf3` for single-precision division. It uses `fmoves` and `fdivs`, returning the result in `%d0` for non-SVR4 ABI.

The file is small compiler support code and must preserve exact argument offsets.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/divsf3.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/extendsfdf2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/extendsfdf2.S

This helper implements `__extendsfdf2`, converting single precision to double. It loads a stack float into `%fp0` and, for non-SVR4 ABI, writes the double result into `%d0/%d1`.

It is compiler conversion support. Return convention differences are the main maintenance issue.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/extendsfdf2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fixdfsi.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fixdfsi.S

This helper implements `__fixdfsi`, converting double to signed int. It truncates the stack-passed double toward zero with `fintrzd` and moves the long result to `%d0`.

It is compiler conversion support and depends on FPU truncation semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fixdfsi.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fixunsdfsi.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fixunsdfsi.S

This helper implements `__fixunsdfsi`, converting double to unsigned int. It truncates toward zero, compares against `2147483648.0`, and for large values subtracts that constant and sets bit 31 in the integer result; ColdFire uses a literal in `.rodata`.

The split path handles unsigned conversion using signed FPU-to-long operations. Boundary handling around 2^31 is the critical point.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fixunsdfsi.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fixunssfsi.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fixunssfsi.S

This helper implements `__fixunssfsi`, converting single precision to unsigned int. It uses the same 2^31 split strategy as the double version, with ColdFire-specific constant loading.

It is sensitive to the exact comparison and subtract sequence used to synthesize unsigned results.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fixunssfsi.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/floatsidf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/floatsidf.S

This helper implements `__floatsidf`, converting signed int to double. It loads the stack integer into `%fp0` with `fmovel` and returns a double through `%d0/%d1` for non-SVR4 ABI.

It is direct compiler conversion support with return ABI sensitivity.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/floatsidf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/floatunsidf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/floatunsidf.S

This helper implements `__floatunsidf`, converting unsigned int to double. It checks the sign bit, clears bit 31 for high values, converts the remainder, and adds `2147483648.0` back in floating point, with ColdFire using a literal constant.

The code handles unsigned values that signed `fmovel` cannot represent directly. ABI-specific double return handling is also important.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/floatunsidf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/floatunsisf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/floatunsisf.S

This helper implements `__floatunsisf`, converting unsigned int to single precision. It uses the same bit-31 split and 2^31 addback strategy as `floatunsidf`, returning `%d0` under non-SVR4 ABI.

The source comment’s lint stub says `double`, but the implementation and filename are single-precision. The instruction sequence is the reliable source of behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/floatunsisf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/flt_rounds.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/flt_rounds.c

This C file implements `__flt_rounds` for m68k hardfloat. It reads FPCR with inline assembly, extracts `FPCR_ROUND`, XORs the result with `1`, and returns the C `FLT_ROUNDS` encoding.

The mapping between m68k FPCR rounding bits and C library `FLT_ROUNDS` values is the important detail.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/flt_rounds.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpgetmask.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpgetmask.c

This file implements `_fpgetmask` with a weak alias to `fpgetmask`. It reads FPCR and extracts `FPCR_EXCP2` as the current floating-point exception mask.

It is an FP environment accessor. Correctness depends on `<m68k/fpreg.h>` bitfield definitions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpgetmask.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpgetround.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpgetround.c

This file implements `_fpgetround` with a weak alias to `fpgetround`. It reads FPCR and returns the extracted `FPCR_ROUND` field.

It exposes the m68k FPU rounding mode through NetBSD’s `ieeefp.h` API.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpgetround.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpgetsticky.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpgetsticky.c

This file implements `_fpgetsticky` with a weak alias to `fpgetsticky`. It reads FPSR and extracts accumulated exception bits from `FPSR_AEX`.

It deliberately reads FPSR rather than FPCR because sticky flags live in the status register.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpgetsticky.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpsetmask.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpsetmask.c

This file implements `_fpsetmask` with a weak alias to `fpsetmask`. It reads FPCR, replaces the `FPCR_EXCP2` exception-mask field with the requested value, writes FPCR, and returns the old mask.

The masking must preserve all non-exception FPCR fields, especially rounding mode.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpsetmask.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpsetround.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpsetround.c

This file implements `_fpsetround` with a weak alias to `fpsetround`. It reads FPCR, replaces only the `FPCR_ROUND` field, writes FPCR, and returns the old rounding mode.

The routine is straightforward FP environment state mutation and must not disturb exception-enable bits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpsetround.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpsetsticky.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpsetsticky.c

This file implements `_fpsetsticky` with a weak alias to `fpsetsticky`. It reads FPSR, replaces the `FPSR_AEX` accumulated-exception field, writes FPSR, and returns the old sticky flags.

The key distinction is writing status-register sticky flags, not FPCR mask or rounding fields.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpsetsticky.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ldexp_881.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ldexp_881.c

This m68k hardfloat C file implements `ldexp(value, exp)` using inline FPU `fscalel` to compute `value * 2^exp`. It returns the scaled double result.

It is a 68881-style optimized implementation. Behavior depends on FPU scaling semantics rather than manual exponent manipulation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ldexp_881.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ledf2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ledf2.S

This helper implements `__ledf2` and strongly aliases `__gtdf2` to it. It compares two doubles and returns `0` when `a > b`, otherwise `1`, matching libgcc’s encoded less/equal helper convention.

The non-obvious return convention is the main risk; it is not a direct boolean `a <= b`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ledf2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/lesf2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/lesf2.S

This helper implements `__lesf2` and strongly aliases `__gtsf2` to it. It compares two floats and returns `0` for greater-than, otherwise `1`, matching libgcc comparison-helper encoding.

The helper’s encoded return values are compiler ABI details and should not be simplified as ordinary predicates.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/lesf2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ltdf2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ltdf2.S

This helper implements `__ltdf2` and strongly aliases `__gedf2` to it. It compares doubles and returns `-1` when `a < b`, otherwise `0`.

The function follows libgcc helper conventions for relational comparisons, not a C boolean API.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ltdf2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ltsf2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ltsf2.S

This helper implements `__ltsf2` and strongly aliases `__gesf2` to it. It compares floats and returns `-1` for less-than, otherwise `0`.

Its behavior is compiler runtime comparison encoding and depends on FPU branch conditions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ltsf2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/modf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/modf.S

This m68k assembly implements `modf`. It loads the input double, stores the integral part through the caller’s pointer after truncating toward zero, subtracts that integral part from the original, and returns the fractional part.

The implementation uses `fintrzx` or ColdFire `fintrzd` and must handle ABI-specific double return placement.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/modf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/muldf3.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/muldf3.S

This helper implements `__muldf3` for double multiplication. It loads the first double into `%fp0`, multiplies by the second stack-passed double, and returns the result through `%d0/%d1` under non-SVR4 ABI.

It is direct compiler arithmetic support and is sensitive to stack offsets and return ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/muldf3.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/mulsf3.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/mulsf3.S

This helper implements `__mulsf3` for single-precision multiplication. It loads, multiplies with `fmuls`, and returns `%d0` under non-SVR4 ABI.

It is compiler-emitted arithmetic support for hardfloat m68k.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/mulsf3.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/nedf2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/nedf2.S

This helper implements `__nedf2` and strongly aliases `__eqdf2` to it. It compares two doubles and returns `0` when equal, otherwise `1`.

The source comment says “single” but the instructions use double operations. The double instruction sequence defines the actual behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/nedf2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/nesf2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/nesf2.S

This helper implements `__nesf2` and strongly aliases `__eqsf2` to it. It compares two floats and returns `0` for equality, otherwise `1`.

It is compiler comparison support; FPU equality branch behavior controls NaN and ordered comparison results.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/nesf2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/subdf3.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/subdf3.S

This helper implements `__subdf3` for double subtraction. It loads the first stack-passed double, subtracts the second, and returns the double result through `%d0/%d1` for non-SVR4 ABI.

It is a direct FPU-backed libgcc compatibility routine.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/subdf3.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/subsf3.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/subsf3.S

This helper implements `__subsf3` for single-precision subtraction. It uses `fmoves` and `fsubs`, returning `%d0` under non-SVR4 ABI.

The routine is compiler arithmetic support and has no local branching beyond ABI return handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/subsf3.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/truncdfsf2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/truncdfsf2.S

This helper implements `__truncdfsf2`, converting double to single precision. It loads the double into `%fp0` and, for non-SVR4 ABI, moves the single result into `%d0`.

It is compiler conversion support and depends on the FPU’s rounding behavior for narrowing conversion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/truncdfsf2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/unorddf2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/unorddf2.S

Despite the filename, this file defines `__unordsf2` and uses single-precision `fmoves`/`fcmps`. It returns `0` on the FPU “ordered or unordered” branch target path named `Lbor`, and `1` otherwise, following the local libgcc-helper convention in the source.

The name/content mismatch is the important finding. Any cleanup must first reconcile this file with the hardfloat makefile entries for `unordsf2.S` and `unorddf2.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/unorddf2.S -->