# Research: subset-b-000761

Grouped research for PA-RISC lib and math-emulation files under `sources/distributed-fs/ceph-client/arch/parisc`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/iomap.c -->
# sources/distributed-fs/ceph-client/arch/parisc/lib/iomap.c

Purpose: implements PA-RISC `iomap` accessors for generic drivers that use `ioread*`, `iowrite*`, repeat I/O, `ioport_map`, `ioport_unmap`, and `pci_iounmap`. It separates directly dereferenceable I/O memory from encoded indirect addresses by testing the top address bit and selecting an operation table region.

Important APIs/types/functions: `struct iomap_ops` contains function pointers for byte/word/dword and 64-bit reads/writes plus repeat operations. `ioport_ops` maps encoded port addresses through `inb/inw/inl`, `outb/outw/outl`, and `ins*/outs*`; `iomem_ops` maps legacy memory I/O through `read*`, `write*`, and raw big-endian forms. Exported symbols are the public integration surface.

Control flow: each exported accessor checks `INDIRECT_ADDR(addr)`. Indirect addresses dispatch through `iomap_ops[ADDR_TO_REGION(addr)]`; direct addresses are loaded/stored in place with little-endian conversion for non-`be` variants. Repeat forms loop over fixed-width elements for direct memory and delegate to port/memory repeat callbacks for indirect space. `ioport_map()` builds a region-8 encoded pointer; unmap functions call `iounmap()` only for non-indirect mappings.

State and dependencies: no persistent state beyond the static `iomap_ops[8]` dispatch table. Depends on PA-RISC address-region layout, `asm/io.h`, PCI optional build state, and 32-bit versus 64-bit address constants.

Risks: only regions 0 and 7 are populated, so an encoded pointer in another region would dereference a null ops table. Correctness is highly dependent on endian expectations, raw accessors, and address encoding. Repeat direct paths do not include explicit barriers beyond the underlying memory operations.

Test signals: PA-RISC build coverage for 32/64-bit, driver smoke tests using port and memory BAR access, endian-sensitive MMIO register tests, and PCI unmap tests for both encoded ports and true `ioremap()` pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/iomap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/lusercopy.S -->
# sources/distributed-fs/ceph-client/arch/parisc/lib/lusercopy.S

Purpose: provides low-level PA-RISC user access routines: `lclear_user()` and `pa_memcpy()`. The code is assembly because it must use space-register-qualified loads/stores, recover from access faults through exception table entries, and optimize common aligned copies.

Important APIs/types/functions: `lclear_user(to, n)` zeroes user memory in space register 3 and returns bytes not cleared. `pa_memcpy(dst, src, len)` copies between spaces already installed in `sr1` and `sr2`; C wrappers in `memcpy.c` set those registers for user or kernel copies.

Control flow: `lclear_user` is a byte loop with an exception fixup that returns the remaining count. `pa_memcpy` chooses a byte path for short copies, aligned 64-bit or 32-bit unrolled loops when source and destination alignment matches, and a destination-aligned unaligned-source path that combines adjacent words with `shrpw`. Faulting loads/stores branch to fixups that compute the uncopied byte count. Some doubleword/word load faults store the already loaded partial data before returning.

State and dependencies: no memory state outside the copied buffers and no persistence. It depends on PA-RISC calling conventions, temporary register aliases, `ASM_EXCEPTIONTABLE_ENTRY`, and caller-provided source/destination space registers.

Risks: tiny register or fixup mistakes can corrupt user memory or report the wrong residual byte count. Overlap semantics are memcpy-like, not memmove-like. Exception-table coverage must exactly match every faulting memory instruction. 64-bit and 32-bit paths diverge under `CONFIG_64BIT`.

Test signals: usercopy fault-injection tests, partial-copy residual checks across page boundaries, alignment matrix tests for source/destination offsets and lengths, KASAN/usercopy hardening tests, and PA-RISC boot or syscall workloads that stress `copy_to_user` and `copy_from_user`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/lusercopy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/memcpy.c -->
# sources/distributed-fs/ceph-client/arch/parisc/lib/memcpy.c

Purpose: wraps the assembly `pa_memcpy()` routine for kernel `memcpy()` and raw user-copy primitives on PA-RISC, setting the correct source and destination space registers before entering assembly.

Important APIs/types/functions: `raw_copy_to_user()`, `raw_copy_from_user()`, exported `memcpy()`, and `copy_from_kernel_nofault_allowed()`. `get_user_space()` reads `SR_USER`; `get_kernel_space()` uses `SR_KERNEL`; `pa_memcpy()` returns bytes not transferred.

Control flow: `raw_copy_to_user()` sets source space to kernel and destination space to user, then delegates all copying and fault residual computation to `pa_memcpy()`. `raw_copy_from_user()` first probes each page of the requested user range with `prober_user()` and shortens the copy length at the first inaccessible page; it then returns the bytes skipped by pre-probe plus the assembly residual. `memcpy()` sets both temporary spaces to kernel and ignores the residual because kernel-to-kernel faults are not expected. `copy_from_kernel_nofault_allowed()` rejects only null-page sources.

State and dependencies: mutates PA-RISC temporary space registers around the copy; otherwise no persistence. Depends on `linux/uaccess.h`, `linux/mm.h`, `PAGE_SIZE`, `PAGE_ALIGN_DOWN`, and the assembly routine in `lusercopy.S`.

Risks: the pre-probe loop is page-granular and depends on correct wrap-free `start + len` arithmetic. Space register setup must match `pa_memcpy` assumptions. `memcpy()` has no overlap guarantees. The nofault allow-list is intentionally minimal and leaves I/O-space filtering as a comment.

Test signals: usercopy API tests, page-boundary permission failures, fault-injection around the first inaccessible page, kernel memcpy alignment tests, and nofault read tests for null-page rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/memset.c -->
# sources/distributed-fs/ceph-client/arch/parisc/lib/memset.c

Purpose: supplies PA-RISC `memset()` using word-sized stores after aligning the destination. The implementation is derived from classic libc-style logic and is independent of user access handling.

Important APIs/types/functions: `memset(void *dstpp, int sc, size_t len)` is the only function. `op_t` is `unsigned long`; `OPSIZ` follows `BITS_PER_LONG / 8`, so the bulk store width changes between 32-bit and 64-bit kernels.

Control flow: for lengths at least 8 bytes, it builds a repeated-byte word `cccc`, byte-fills until destination alignment matches `OPSIZ`, stores eight `op_t` words per loop, then one `op_t` per loop for the remaining word count. A final byte loop writes trailing bytes. It returns the original destination pointer.

State and dependencies: no persistent state. Depends on `<linux/types.h>`, `<asm/string.h>`, and `BITS_PER_LONG`. It writes only the caller-specified memory range.

Risks: assumes normal kernel memory, so it is not suitable for user-space faulting access or MMIO ordering. Pointer arithmetic is performed through `long int dstp`; this matches PA-RISC kernel assumptions but would be questionable as generic portable C. Store alignment and `op_t` aliasing are intentionally low-level.

Test signals: generic kernel string/memory selftests, boot-time memory initialization checks, byte-pattern tests at all alignments and lengths around `OPSIZ * 8`, and 32-bit/64-bit PA-RISC builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/memset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/ucmpdi2.c -->
# sources/distributed-fs/ceph-client/arch/parisc/lib/ucmpdi2.c

Purpose: implements the libgcc helper `__ucmpdi2()` for unsigned 64-bit comparison on PA-RISC configurations where the compiler may emit calls instead of inline code.

Important APIs/types/functions: `union ull_union` overlays an `unsigned long long` with two 32-bit words named `high` and `low`. `word_type __ucmpdi2(unsigned long long a, unsigned long long b)` returns libgcc comparison codes: `0` when `a < b`, `1` when equal, and `2` when `a > b`.

Control flow: both inputs are split into high and low words. The function compares high words first and returns immediately on a difference; low words are compared only when high words match. Equality returns `1`.

State and dependencies: no state or persistence. Depends on `linux/libgcc.h` for `word_type` and on the architecture's word ordering matching the union field interpretation used here.

Risks: the union layout is endian-sensitive. It is correct only if `ui.high` maps to the most significant 32 bits for the target ABI. Because this is a compiler helper, any ABI mismatch can surface as broad arithmetic misbehavior rather than a local failure.

Test signals: compiler-generated 64-bit unsigned comparison tests, libgcc helper ABI tests, both endian/ABI build coverage for PA-RISC, and kernel code paths that compare `u64` values on 32-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/ucmpdi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/Makefile -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/Makefile

Purpose: defines the PA-RISC floating-point emulation object list and compiler flags. It builds the dispatcher, exception decoder, denormal support, double/single arithmetic, fused operations, conversions, and comparison helpers.

Important APIs/types/functions: `ccflags-y` suppresses warnings expected from old PA-RISC math-emulation code, including implicit declarations, old-style definitions, and missing prototypes. `obj-y` always includes `frnd.o`, `driver.o`, `decode_exc.o`, `fpudispatch.o`, `denormal.o`, arithmetic objects, conversion objects, and compare objects. `obj-$(CONFIG_MATH_EMULATION)` adds `unimplemented-math-emulation.o`.

Control flow: Kbuild consumes the object variables. `CFLAGS_REMOVE_fpudispatch.o = -Wimplicit-fallthrough` relaxes one warning setting for the large dispatcher.

State and dependencies: no runtime state. Depends on PA-RISC arch Kbuild and `CONFIG_MATH_EMULATION`.

Risks: the warning suppressions can hide real type/prototype regressions. The comment says full math emulation is needed only for very old or stripped-down CPUs and not currently supported, so build-time inclusion may not imply a fully supported runtime configuration.

Test signals: PA-RISC allmodconfig/defconfig builds with and without `CONFIG_MATH_EMULATION`, warning-budget checks after changing prototypes, and boot tests on hardware or emulators that enter the FPU exception path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/cnv_float.h -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/cnv_float.h

Purpose: provides macro primitives for conversions among single/double floating-point and signed/unsigned fixed-point formats. It is a shared dependency for `fcnv*` files.

Important APIs/types/functions: macros cover exponent rebiasing (`Sgl_to_dbl_exponent`, `Dbl_to_sgl_exponent`), mantissa extraction/deposition, inexact tests, round-to-nearest rules, integer construction (`Int_from_*`, `Dint_from_*`, `Duint_from_*`), two-word integer arithmetic, and `Find_ms_one_bit()`.

Control flow: there are no functions; callers expand macros inline. Conversion files first classify ranges, then use these macros to shift mantissas into destination integer or float layouts, compute guard/sticky/odd bits, round according to `Rounding_mode()`, and set destination words.

State and dependencies: mutates macro arguments and uses `Fpustatus_register` via rounding-mode/status macros from `float.h`. Depends heavily on `sgl_float.h`, `dbl_float.h`, bitfield helpers from `fpbits.h`, and C integer widths.

Risks: many macros evaluate and mutate arguments multiple times and require caller-provided temporaries. Several shift expressions depend on ranges being prevalidated by callers. Parentheses are sparse because this is legacy macro code, making it easy to introduce precedence bugs.

Test signals: exhaustive boundary tests around `SGL_FX_MAX_EXP`, `DBL_FX_MAX_EXP`, zero, denormals, NaNs, infinities, half-ulp tie cases, negative-to-unsigned conversions, and every rounding mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/cnv_float.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dbl_float.h -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dbl_float.h

Purpose: defines the double-precision and double-extended word-manipulation macro layer used by PA-RISC floating-point emulation.

Important APIs/types/functions: macros classify and mutate double fields (`Dbl_isnan`, `Dbl_isinfinity`, `Dbl_setoverflow`, `Dbl_denormalize`), perform two-word shifts, addition/subtraction, normalization, copy-to/from pointer operations, and construct NaNs, infinities, zeros, largest finite values, and wrapped exponents. The `Dblext_*` macros support fused multiply-add extended mantissas.

Control flow: callers operate on pairs of 32-bit words. Arithmetic files use these macros to clear sign/exponent and set the hidden bit, align operands into extension words, normalize by byte/nibble/bit scanning, round with guard/sticky bits, and write results back.

State and dependencies: no standalone storage, but macros mutate passed lvalues and consult `Rounding_mode()` through `float.h`. Depends on raw field macros from `float.h` and `Shiftdouble`/`Variable_shift_double` helpers from PA-RISC headers.

Risks: macro side effects are extensive and easy to misuse. Some double-extended macros contain suspicious copy/identifier patterns inherited from legacy code, so fused paths need focused validation. Shift counts are assumed prebounded. NaN signaling polarity is PA-RISC-specific and should not be generalized blindly.

Test signals: double arithmetic conformance tests, denormal and underflow trap tests, NaN quieting/signaling tests, overflow rounding-mode tests, and fused-operation tests if `Dblext_*` callers are changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dbl_float.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/decode_exc.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/decode_exc.c

Purpose: decodes queued PA-RISC FPU exception registers, completes unimplemented instructions through `fpudispatch()`, and returns Linux signal/code encodings when a real trap remains.

Important APIs/types/functions: `decode_fpu(unsigned int Fpu_register[], unsigned int trap_counts[])` is the external interface. Local macros map `Fpu_register[0]` to the FPU status word, extract exception type/instruction fields, address single/double/quad registers, and construct `SIGNALCODE(signal, code)`.

Control flow: it saves accrued status flags, clears the architectural flag field for processing, rejects reserved operations when the T-bit is clear, then scans exception registers 1 through 7. Unimplemented exceptions are cleared and emulated through `fpudispatch`; new emulation exceptions are written back into the queue. Underflow and overflow are either reported as traps or converted to default results and flags when traps are disabled. Invalid, divide-by-zero, and inexact become `SIGFPE` codes; unknown exceptions become `SIGILL`.

State and dependencies: mutates the passed FPU register image, exception registers, T-bit, status flags, and target result registers. Depends on `float.h`, `sgl_float.h`, `dbl_float.h`, `cnv_float.h`, `denormal.c`, `fpudispatch`, Linux signal constants, and `printk`.

Risks: exception queue mutation order is delicate. Trap-disabled underflow/overflow must match hardware default-result rules. `trap_counts` is effectively unused despite being passed. Status flag preservation is a compatibility-sensitive area.

Test signals: FPU exception tests for each enabled/disabled trap, queued multiple exceptions, unimplemented instruction emulation, denormalized default results, signal delivery codes, and status-word bit preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/decode_exc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/denormal.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/denormal.c

Purpose: converts wrapped underflow results into denormalized single or double values when underflow traps are disabled, applying the requested rounding mode and reporting whether the result is inexact.

Important APIs/types/functions: `sgl_denormalize(unsigned int *sgl_opnd, boolean *inexactflag, int rmode)` and `dbl_denormalize(unsigned int *dbl_opndp1, unsigned int *dbl_opndp2, boolean *inexactflag, int rmode)`.

Control flow: each function copies the operand words, derives the true underflow exponent by subtracting `SGL_WRAP` or `DBL_WRAP`, saves the sign, and calls the corresponding macro denormalizer to shift the significand and produce guard/sticky/inexact state. If inexact, it rounds for `ROUNDPLUS`, `ROUNDMINUS`, or `ROUNDNEAREST`, restores the sign, writes the result words back, and updates `*inexactflag`.

State and dependencies: only mutates pointed-to operands and inexact flag. Depends on `float.h`, `sgl_float.h`, `dbl_float.h`, and PA-RISC shift/bit macros.

Risks: correctness hinges on the wrapped exponent convention used by trap paths. Rounding after denormalization can cross back into normal range, so guard/sticky logic must match hardware. The functions do not validate operand class; callers must pass wrapped underflow results.

Test signals: underflow tests with traps disabled across all rounding modes, exact versus inexact denormal results, sign preservation for positive/negative tiny values, and comparisons against hardware or high-precision software references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/denormal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfadd.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfadd.c

Purpose: implements double-precision floating-point addition for the emulator.

Important APIs/types/functions: `dbl_fadd(dbl_floating_point *leftptr, dbl_floating_point *rightptr, dbl_floating_point *dstptr, unsigned int *status)` returns `NOEXCEPTION` or an exception mask. It uses `Dbl_*` macros for classification, alignment, arithmetic, normalization, and status updates.

Control flow: operands are copied into two-word locals. The function first handles NaNs, signaling NaNs, infinities, and invalid opposite-signed infinity addition. It orders finite operands by magnitude, handles zero and denormal fast paths, then aligns the smaller operand into an extension word. Opposite signs trigger subtraction and possible left normalization; same signs trigger addition and possible right prenormalization. Rounding uses extension bits and the current rounding mode. Overflow and underflow trap settings determine whether wrapped results or default finite/infinite values are returned.

State and dependencies: mutates only destination and `*status` flags through macros such as `Set_invalidflag`, `Set_overflowflag`, and `Set_inexactflag`. Depends on `float.h` and `dbl_float.h`.

Risks: add/sub sign selection is encoded through the signed value of an XOR result, making regressions subtle. Denormal exactness and signed-zero selection are rounding-mode-sensitive. A missing `break` after `ROUNDMINUS` intentionally falls through to truncate behavior but should be treated carefully.

Test signals: IEEE-754 addition vectors covering NaNs, infinities, signed zeros, denormals, cancellation, overflow, all rounding modes, underflow traps, and inexact traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfadd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfcmp.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfcmp.c

Purpose: implements double-precision floating-point compare and writes the PA-RISC status C-bit according to the supplied condition predicate.

Important APIs/types/functions: `dbl_fcmp(dbl_floating_point *leftptr, dbl_floating_point *rightptr, unsigned int cond, unsigned int *status)`. Condition-field helpers from `float.h` extract unordered, equal, less-than, greater-than, and exception predicate bits.

Control flow: the function copies operands, handles NaN cases first, and raises invalid when a signaling NaN is present or when the condition requires an exception on unordered compare. Otherwise NaNs set C-bit from `Unordered(cond)`. Non-NaN comparisons handle opposite signs, the special equality of positive and negative zero, same-sign equality, positive magnitude ordering, and reversed negative ordering.

State and dependencies: mutates the C-bit and invalid flag in `*status`; no other persistence. Depends on `float.h` and `dbl_float.h`.

Risks: PA-RISC condition predicates are encoded in `cond`; testing only numeric compare results is insufficient. Signaling NaN detection and quiet NaN unordered behavior must match the architecture. Negative ordering is intentionally reversed and easy to break with refactors.

Test signals: compare matrices for all relation predicates, signed zeros, positive and negative finite values, infinities, quiet NaNs, signaling NaNs, invalid-trap enabled/disabled, and C-bit results for unordered conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfcmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfdiv.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfdiv.c

Purpose: implements double-precision floating-point division using two-word integer operations.

Important APIs/types/functions: `dbl_fdiv(dbl_floating_point *srcptr1, dbl_floating_point *srcptr2, dbl_floating_point *dstptr, unsigned int *status)`.

Control flow: result sign is established from operand signs. The function handles NaNs, infinities, invalid `inf/inf` and `0/0`, divisor infinity, and divide-by-zero. Finite operands are normalized, with denormal exponents adjusted. The mantissa division uses a non-restoring algorithm: subtract divisor from dividend, iterate through quotient bits with left shifts and add/subtract correction, derive guard/sticky state, round, then handle overflow/underflow and status flags.

State and dependencies: writes destination and status flags only. Depends on `float.h`, `dbl_float.h`, rounding-mode macros, and two-word add/subtract helpers.

Risks: non-restoring division is sensitive to sign-bit interpretation of the partial remainder. Underflow handling repeats tiny-result logic and must remain consistent with multiply. Division-by-zero and invalid-zero cases have different trap/flag behavior. Quotient normalization around hidden-bit absence is a common boundary risk.

Test signals: division by zero, zero by zero, infinity combinations, denormal divisors/dividends, quotient just below/above one, all rounding modes, overflow/underflow traps, and high-precision reference comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfdiv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfmpy.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfmpy.c

Purpose: implements double-precision floating-point multiplication.

Important APIs/types/functions: `dbl_fmpy(dbl_floating_point *srcptr1, dbl_floating_point *srcptr2, dbl_floating_point *dstptr, unsigned int *status)`.

Control flow: the result sign is computed first. The function handles NaNs, signaling NaNs, infinities, invalid infinity-times-zero, and zeros. It forms the destination exponent by adding source exponents and subtracting bias, normalizes denormal operands, then multiplies mantissas by inspecting four bits of one operand per loop and accumulating shifted versions of the other operand. After normalization, it derives guard/sticky/inexact bits, rounds, detects overflow, and handles underflow by either returning a wrapped trap result or denormalizing and setting flags.

State and dependencies: writes destination and status flags. Depends on `float.h`, `dbl_float.h`, `Twoword_add`, normalization macros, and rounding-mode state.

Risks: the nibble-at-a-time multiply must maintain sticky bits for discarded product bits. Underflow tiny detection speculatively increments/decrements the mantissa and is easy to desynchronize from rounding rules. Infinity/zero invalid handling has to preserve NaN payload behavior where possible.

Test signals: multiplication vectors for signed zeros, infinities, NaNs, denormals, exact products, half-ulp ties, overflow/underflow boundaries, and all rounding/trap modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfmpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfrem.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfrem.c

Purpose: implements double-precision floating-point remainder.

Important APIs/types/functions: `dbl_frem(dbl_floating_point *srcptr1, dbl_floating_point *srcptr2, dbl_floating_point *dstptr, unsigned int *status)`.

Control flow: special cases handle NaNs, signaling NaNs, invalid first-operand infinity, divisor infinity, and zero divisor. Finite operands are normalized, preserving the dividend sign as the result sign. If the dividend magnitude is less than the divisor, it either returns the dividend or `dividend - divisor` for the greater-than-half case. Otherwise it repeatedly subtracts the divisor while left-shifting the dividend mantissa, performs a final subtract and tie decision, possibly flips the result sign, normalizes the remainder, and denormalizes on underflow.

State and dependencies: writes destination and status flags, but remainder is exact and does not set inexact. Depends on `float.h` and `dbl_float.h`.

Risks: tie-to-even style sign correction is encoded with `roundup` and exact half comparisons. The iterative subtract loop can be expensive for large exponent differences. Underflow handling assumes exactness and does not use guard/sticky rounding.

Test signals: `fmod`/remainder-style conformance cases, divisor zero, infinities, NaNs, exact half-divisor ties, denormal operands, signed-zero results, and underflow trap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfrem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfsqrt.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfsqrt.c

Purpose: implements double-precision square root.

Important APIs/types/functions: `dbl_fsqrt(dbl_floating_point *srcptr, unsigned int *_nullptr, dbl_floating_point *dstptr, unsigned int *status)`.

Control flow: the function handles NaNs, signaling NaNs, positive infinity, zero, and invalid negative inputs. Finite positive operands are normalized; odd/even exponent parity determines a pre-shift. The core square-root algorithm builds result bits using a trial sum (`result + newbit`), subtracting from the shifted source when the trial fits and shifting `newbit` down otherwise. Remaining source bits mark inexactness; rounding then handles plus and nearest modes before final exponent rebiasing.

State and dependencies: writes destination and status flags. Depends on `float.h`, `dbl_float.h`, and current rounding mode.

Risks: the algorithm comments are incomplete and include “Trust me, it works,” so maintainers need reference tests before changing it. Negative zero is returned unchanged through the zero path, while negative nonzero is invalid. Inexact handling treats sticky as always true after remainder remains, which must match the bit-generation algorithm.

Test signals: square roots of zero, negative zero, negative finite, positive infinity, NaNs, perfect squares, values just between representable roots, denormals, all rounding modes, and inexact trap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfsqrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfsub.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfsub.c

Purpose: implements double-precision floating-point subtraction. It is structurally parallel to `dfadd.c`, with sign logic adjusted for subtract semantics.

Important APIs/types/functions: `int dbl_fsub(dbl_floating_point *leftptr, dbl_floating_point *rightptr, dbl_floating_point *dstptr, unsigned int *status)`.

Control flow: operands are copied, NaNs and infinities are processed first, and same-signed infinity subtraction is invalid. Right infinity is returned with inverted sign. Finite operands are ordered by magnitude; if the right operand has larger magnitude, operands are swapped and the result sign is inverted. Denormal and zero cases are handled before the general path. The smaller magnitude is aligned into an extension word. Same signs perform subtraction; opposite signs add magnitudes. The result is normalized, rounded, and checked for overflow or underflow.

State and dependencies: writes destination and `*status` through macros. Depends on `float.h` and `dbl_float.h`.

Risks: differs from addition mainly by tests such as `save == 0` versus `save != 0` and `save >= 0` versus `< 0`; copy/paste fixes must preserve those inversions. Signed-zero behavior depends on rounding mode. The `ROUNDMINUS` switch fallthrough is legacy behavior and should be reviewed only with tests.

Test signals: subtraction cancellation, signed zeros, same/opposite infinities, NaNs, denormals, magnitude swaps, overflow/underflow traps, inexact traps, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/dfsub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/driver.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/driver.c

Purpose: connects the Linux PA-RISC floating-point exception path to the software emulator.

Important APIs/types/functions: `int handle_fpe(struct pt_regs *regs)` copies the saved floating-point register file, invokes `decode_fpu()`, writes modified registers back, and sends a Unix signal if required. Local macros decode instruction bit fields but are largely unused in this file.

Control flow: `handle_fpe()` copies `regs->fr` into a 36-entry local `frcopy` because the emulator expects extra scratch/type entries. It saves the original status word for optional debug output, calls `decode_fpu(frcopy, 0x666)`, copies the emulated register image back to `regs->fr`, and if a signal code is returned, clears the floating-point trap bit for `SIGFPE` before calling `force_sig_fault()` at the current instruction address.

State and dependencies: mutates the interrupted task's floating-point registers and may deliver a signal. Depends on `pt_regs`, `linux/sched/signal.h`, `math-emu.h`, `decode_fpu`, and debug-only `printbinary`.

Risks: register image sizing and layout must match both kernel save state and emulator expectations. Passing `0x666` as `trap_counts` relies on `decode_fpu` not dereferencing it meaningfully. Trap-bit clearing is necessary to avoid recursive user signal-handler traps.

Test signals: user programs that execute unsupported FPU instructions, signal delivery tests for `SIGFPE` and `SIGILL`, register preservation tests, and debug-disabled build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvff.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvff.c

Purpose: implements floating-point format conversions between single and double precision.

Important APIs/types/functions: `sgl_to_dbl_fcnvff()` and `dbl_to_sgl_fcnvff()`. They use conversion macros from `cnv_float.h`, single/double field macros, and status/rounding helpers.

Control flow: single-to-double is mostly exact: it handles infinity, NaN quieting, zero, denormal normalization, exponent rebiasing, and mantissa expansion. Double-to-single handles infinity/NaN, computes the destination exponent, chooses normal or denormalized conversion, derives inexact/guard/sticky/odd bits, rounds according to the current mode, handles mantissa overflow, and then performs overflow/underflow trap or default-result processing.

State and dependencies: writes the destination and status flags. Depends on `float.h`, `sgl_float.h`, `dbl_float.h`, and `cnv_float.h`.

Risks: double-to-single is lossy and contains most of the risk: denormalized conversion, tiny detection, wrapped trap exponent checks, and NaN payload truncation. Single-to-double should be exact except signaling NaN quieting, so any inexact flag there would be suspicious.

Test signals: all single/double class conversions, signaling and quiet NaNs, denormal single to normal double, double values near single overflow/underflow thresholds, tie-to-even cases, all rounding modes, and enabled overflow/underflow/inexact traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfu.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfu.c

Purpose: implements rounded conversions from floating-point values to unsigned fixed-point integers.

Important APIs/types/functions: `sgl_to_sgl_fcnvfu`, `sgl_to_dbl_fcnvfu`, `dbl_to_sgl_fcnvfu`, and `dbl_to_dbl_fcnvfu`. Destination types are 32-bit unsigned or `dbl_unsigned`.

Control flow: each function computes unbiased source exponent, checks overflow against the destination integer width, rejects negative values as invalid, builds an integer mantissa when exponent is nonnegative, and otherwise starts from zero for magnitudes below one. Inexact cases round according to current mode: plus increments positive results, minus rejects negative fractional values, and nearest handles half-ulp ties. Disabled invalid traps write saturated all-ones for positive overflow and zero for negative invalid inputs.

State and dependencies: writes output and status flags. Depends on `cnv_float.h` integer construction/rounding macros plus `float.h`, `sgl_float.h`, and `dbl_float.h`.

Risks: unsigned conversion of negative values is a major edge surface and sometimes clears `inexact` when invalid is raised. Rounding can overflow a 32-bit unsigned destination after an initially in-range double-to-single conversion. NaNs and infinities flow through exponent overflow paths rather than a separate class decoder.

Test signals: negative finite values, negative fractions by rounding mode, NaNs/infinities, positive overflow saturation, `UINT_MAX` boundaries, `2^32` and `2^64` edges, half-way fractions, and invalid/inexact trap combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfut.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfut.c

Purpose: implements truncating conversions from floating-point values to unsigned fixed-point integers.

Important APIs/types/functions: `sgl_to_sgl_fcnvfut`, `sgl_to_dbl_fcnvfut`, `dbl_to_sgl_fcnvfut`, and `dbl_to_dbl_fcnvfut`.

Control flow: the functions mirror `fcnvfu.c` but omit rounding increments. They check exponent overflow, reject negative values as invalid, convert nonnegative values by shifting mantissas into 32-bit or 64-bit unsigned destinations, and return zero for magnitudes below one. Inexact is still reported when fractional bits are discarded or a nonzero magnitude truncates to zero.

State and dependencies: writes destination and flags. Depends on the same conversion macros and status helpers as `fcnvfu.c`.

Risks: because truncation does not round, inexact status is the only indication of discarded data. Negative source values are treated as invalid even when truncation would otherwise move toward zero. NaN/infinity handling is implicit through exponent overflow checks and saturation/zero behavior.

Test signals: fractional positive values that truncate to zero, positive integer boundaries, negative values of all magnitudes, NaNs/infinities, unsigned max boundaries, inexact trap enabled/disabled, and invalid trap enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfut.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfx.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfx.c

Purpose: implements rounded conversions from floating-point values to signed fixed-point integers.

Important APIs/types/functions: `sgl_to_sgl_fcnvfx`, `sgl_to_dbl_fcnvfx`, `dbl_to_sgl_fcnvfx`, and `dbl_to_dbl_fcnvfx`. Destinations are 32-bit signed or two-word `dbl_integer`.

Control flow: each path computes the unbiased exponent, checks overflow while allowing the exact minimum signed integer as a special case, shifts the normalized mantissa into integer form for nonnegative exponents, applies sign by negation or two-word two's complement, and rounds inexact cases according to the current mode. Magnitudes below one start at zero and can round to +/-1. Overflow with traps disabled saturates to max positive or min negative.

State and dependencies: writes destination and status flags. Depends on `cnv_float.h` signed integer macros, `float.h`, `sgl_float.h`, and `dbl_float.h`.

Risks: exact `MININT` is a special exception to normal overflow handling. Rounding after conversion can overflow a 32-bit result and must raise invalid. Signed two-word increment/decrement behavior must preserve carries/borrows. NaNs/infinities are handled by exponent overflow paths.

Test signals: signed min/max boundaries, exact minint, just-out-of-range values, positive and negative fractions around 0.5, NaNs/infinities, all rounding modes, and invalid/inexact trap combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfxt.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfxt.c

Purpose: implements truncating conversions from floating-point values to signed fixed-point integers.

Important APIs/types/functions: `sgl_to_sgl_fcnvfxt`, `sgl_to_dbl_fcnvfxt`, `dbl_to_sgl_fcnvfxt`, and `dbl_to_dbl_fcnvfxt`.

Control flow: the functions follow the signed conversion structure of `fcnvfx.c` but omit all rounding-mode increments/decrements. Overflow checks saturate or return exact minimum signed integer where allowed. Nonnegative exponents convert shifted mantissas and apply sign; negative exponents write zero. Discarded fractional data sets inexact or returns an inexact exception if enabled.

State and dependencies: writes destination and flags. Depends on `float.h`, `sgl_float.h`, `dbl_float.h`, and `cnv_float.h`.

Risks: truncation toward zero differs from rounding-mode conversion, so callers must dispatch the correct opcode. Inexact still matters even when the numeric result is zero. Exact minimum integer and disabled invalid traps remain architecture-sensitive. NaN/infinity behavior is implicit via exponent overflow handling.

Test signals: truncation of positive/negative fractions, signed min/max boundaries, exact minimum integer, NaNs/infinities, inexact trap tests, invalid trap tests, and comparison with rounded `fcnvfx` for all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvfxt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvuf.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvuf.c

Purpose: implements unsigned fixed-point to floating-point conversions.

Important APIs/types/functions: `sgl_to_sgl_fcnvuf`, `sgl_to_dbl_fcnvuf`, `dbl_to_sgl_fcnvuf`, and `dbl_to_dbl_fcnvuf`. Sources are 32-bit unsigned or `dbl_unsigned`; destinations are single or double floats.

Control flow: zero returns signed-positive zero. Nonzero sources use `Find_ms_one_bit()` to locate the most significant one bit, left-justify the integer, set mantissa and biased exponent, and then round only when the destination precision cannot hold all source bits. Single-destination conversions can be inexact; double-destination from 32-bit unsigned is exact, while 64-bit unsigned to double may be inexact.

State and dependencies: writes destination and status flags. Depends on unsigned conversion macros in `cnv_float.h` and field macros from single/double headers.

Risks: normalization depends on `Find_ms_one_bit()` returning the legacy position convention. Shift expressions around `dst_exponent` are range-sensitive. Unsigned-to-float never creates negative results, so `ROUNDMINUS` intentionally does not increment.

Test signals: zero, powers of two, `UINT_MAX`, `ULLONG_MAX`, values just above single/double precision limits, all rounding modes, and inexact trap behavior for lossy conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvxf.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvxf.c

Purpose: implements signed fixed-point to floating-point conversions.

Important APIs/types/functions: `sgl_to_sgl_fcnvxf`, `sgl_to_dbl_fcnvxf`, `dbl_to_sgl_fcnvxf`, and `dbl_to_dbl_fcnvxf`. Sources are 32-bit signed or two-word `dbl_integer`; destinations are single or double floats.

Control flow: each function determines the source sign, converts negative inputs to magnitude with `Int_negate` or `Dint_negate`, returns positive zero for zero inputs, normalizes the magnitude by finding the most significant one bit, deposits mantissa and exponent fields, and rounds if low bits are lost. Rounding plus and minus are sign-aware; nearest uses the conversion helper tie rules.

State and dependencies: writes destination and status flags. Depends on signed conversion macros in `cnv_float.h`, single/double field macros, and current rounding mode.

Risks: negating the most negative signed integer must preserve the intended magnitude in two's-complement arithmetic. 64-bit signed to single/double paths have complex shifts when the high word is zero versus nonzero. Inexact flagging must occur after destination is written when traps are raised.

Test signals: zero, negative zero absence for integer input, `INT_MIN`, `LONG_LONG_MIN`, max signed values, powers of two, precision-loss cases, all rounding modes, and inexact traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fcnvxf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/float.h -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/float.h

Purpose: defines the core PA-RISC floating-point emulation data model: raw bit fields for single, double, quad, extended mantissas, fixed-point helper types, format constants, status register bits, exception encodings, condition fields, and operation codes.

Important APIs/types/functions: single macros (`Ssign`, `Sexponent`, `Smantissa`), double macros (`Dsign`, `Dexponent`, `Dmantissap1/2`), deposit/test variants, `sgl_floating_point`, `dbl_floating_point`, `dbl_integer`, `dbl_unsigned`, rounding mode constants, exception masks, `Fpustatus_register` helpers, and operation encodings such as `FADD`, `FDIV`, `FCNVFX`, and `FCMP`.

Control flow: there are no functions. Other files include this header to inspect and mutate raw 32-bit words and status bits. Status macros assume a local variable or pointer named `status` and map `Fpustatus_register` to `*status` unless a file overrides it.

State and dependencies: no storage, but macros mutate caller lvalues and `*status`. Depends on `fpbits.h`, `hppa.h`, and `fpu.h` with `LOCORE` set to get FPU capability flags without C PDC structures.

Risks: this header is the central contract; any bit-position error breaks the emulator globally. Macros are not type-safe and often rely on caller naming conventions. Quad support is skeletal. Status/trap bit encodings must match PA-RISC architecture and Linux signal translation.

Test signals: build coverage of every math-emu file, bitfield extraction/deposit unit tests, status flag/trap enable tests, operation decoder tests, and cross-checks against hardware FPU behavior for representative classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/float.h -->
