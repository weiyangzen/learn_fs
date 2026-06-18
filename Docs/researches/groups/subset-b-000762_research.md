# Research: subset-b-000762

This grouped report covers the requested PA-RISC math-emulation, memory-management, and network build files. Each section is source-tree aligned and wrapped for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fmpyfadd.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fmpyfadd.c

Purpose: implements PA-RISC fused multiply-add emulation for double and single precision: `dbl_fmpyfadd`, `dbl_fmpynfadd`, `sgl_fmpyfadd`, and `sgl_fmpynfadd`. The non-negated forms compute `(src1 * src2) + src3`; the negated forms flip the product sign before adding.

Important APIs and types: the entry points take `dbl_floating_point` or `sgl_floating_point` pointers plus an FP status word pointer. They rely heavily on `float.h`, `sgl_float.h`, and `dbl_float.h` macros for IEEE fields, hidden bits, extended intermediates, trap tests, rounding mode, and exception flag updates.

Control flow: each routine copies operands into integer words, precomputes the product sign and exponent, handles NaNs, infinities, zero products, and denormals, multiplies significands into an extended exact accumulator, aligns the addend, chooses add versus subtract by sign, normalizes cancellation or overflow, rounds once, then writes the destination and exception status. The double path uses four-word `Dblext` temporaries; the single path uses two-word `Sglext` temporaries.

State and persistence: no persistent state is stored locally, but the routines mutate the pointed status register through macros such as `Set_invalidflag`, `Set_overflowflag`, `Set_underflowflag`, and `Set_inexactflag`. Destination memory is written only after a result or trap-wrapped result is known.

Dependencies and integration: `fpudispatch.c` calls these functions from major opcode `0x2e` decode. Correctness depends on bit-level helper macros, PA-RISC exception codes such as `OPC_2E_INVALIDEXCEPTION`, and the register image layout used by the FPU trap handler.

Risks: the file contains four large near-duplicate K&R-style bodies, making fixes easy to miss in one precision or sign variant. Rounding fallthrough from `ROUNDMINUS` to `ROUNDZERO` is intentional but fragile. Corner cases include signed zero selection, invalid infinity subtraction, denormal underflow traps, and exact cancellation.

Test signals: exercise NaN precedence, signaling NaNs with traps enabled and disabled, `inf * 0`, product infinity plus opposite infinity, addend zero, denormal operands, all rounding modes, overflow and underflow trap wrapping, inexact traps, and cancellation to signed zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fmpyfadd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fpbits.h -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fpbits.h

Purpose: provides portable bitfield extraction, signed extraction, masking, and deposit macros for the PA-RISC floating-point emulator. It abstracts the emulator's convention that bit 0 is the most significant bit of a 32-bit word.

Important APIs and types: `HOSTWDSZ` defaults to 32. `Bitfield_extract(start, length, object)` returns an unsigned field; `Bitfield_signed_extract` sign-extends; `Bitfield_mask` isolates a field in place; `Bitfield_deposit` clears and inserts a value into a field.

Control flow: this is macro-only code. All behavior expands inline at call sites in `float.h` and related format-specific headers. The macros compute shifts from `HOSTWDSZ`, `start`, and `length`, then combine masks and shifted values.

State and persistence: no runtime state is maintained. The only persistent contract is the source-level preprocessor API, which affects every floating-point field accessor compiled from the emulator headers.

Dependencies and integration: included indirectly by format helpers that name sign, exponent, mantissa, condition, and status fields. The file assumes unsigned arithmetic and a word size at least large enough for the requested fields.

Risks: macro arguments may be evaluated more than once in `Bitfield_deposit` via `object`, so callers must avoid side effects. Invalid `length` or `start` values can produce undefined shifts. The macros encode a PA-RISC bit numbering convention that differs from normal little-endian mental models.

Test signals: compile-time and unit-level checks should verify extraction and deposit for sign, exponent, mantissa, condition fields, all-zero and all-one masks, signed high-bit fields, and host builds that override `HOSTWDSZ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fpbits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fpu.h -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fpu.h

Purpose: defines PA-RISC FPU capability flags and the emulator version field used by the floating-point instruction dispatcher.

Important APIs and types: flags include `PA83_FPU_FLAG`, `PA89_FPU_FLAG`, `PA2_0_FPU_FLAG`, `TIMEX_EXTEN_FLAG`, `ROLEX_EXTEN_FLAG`, `COPR_FP`, and `SFU_MPY_DIVIDE`. `EM_FPU_TYPE_OFFSET` gives the register-image offset where dispatch stores FPU type flags, and `EMULATION_VERSION` is returned for the `COPR,0,0` instruction.

Control flow: macro-only header. Runtime use is in `fpudispatch.c`, where `parisc_linux_get_fpu_type()` fills the type flag slot from `boot_cpu_data.cpu_type`, then decode logic gates PA1.1, PA2.0, Timex, and Rolex instruction forms.

State and persistence: this file declares constants only. Persistent state exists in the emulated FP register array at `EM_FPU_TYPE_OFFSET`, not in the header.

Dependencies and integration: uses firmware model key names for potential Timex and Rolex differentiation. `fpudispatch.c` depends on these flags for compare queue updates, fused/multi-op availability, and source-register decoding.

Risks: incorrect flag assignment changes instruction legality and status update semantics. The offset is expressed in bytes and later converted to a `u_int` index, so structure-layout drift in the register image is risky.

Test signals: validate emulator version reporting, CPU-type-to-flag mapping for pcxs, pcxt, pcxt_, and pcxu-or-newer, plus decode behavior for PA2.0-only conversions and Timex/Rolex FMPYCFXT paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fpudispatch.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fpudispatch.c

Purpose: decodes trapped PA-RISC floating-point instructions and dispatches them to the appropriate software emulation routine. It is the integration hub between trap handling, the FP register image, and arithmetic helpers.

Important APIs and functions: public entry points are `fpudispatch(ir, excp_code, holder, fpregs)` for hardware unimplemented exceptions and `emfpudispatch(ir, dummy1, dummy2, fpregs)` for full coprocessor emulation. Static decoders handle major opcodes `0x0c`, `0x0e`, `0x06`, `0x26`, and `0x2e`; `update_status_cbit()` updates compare status or compare queue bits.

Control flow: the dispatcher derives class and subop fields, considering PA1.1 versus PA2.0 subop layouts. Major decoders compute register offsets, map source `fr0` to a constant zero slot, reject illegal destination `fr0`, align double registers, then call conversion, compare, add, subtract, multiply, divide, remainder, sqrt, round, fused, or multi-op helpers.

State and persistence: it updates `fpregs[0]` as the FP status register and stores results directly into `fpregs`. It also writes `fpregs[FPU_TYPE_FLAG_POS]` from CPU type for Linux callers.

Dependencies and integration: called by `decode_exc.c` and trap paths behind `handle_fpe()`. Depends on `float.h`, arithmetic files, Linux `boot_cpu_data`, and PA-RISC register encodings.

Risks: decode field positions are dense and architecture-specific. Misaligned double or right-half register handling can corrupt adjacent register slots. Several unsupported paths use `BUG()` after nominally unreachable switch cases; fuzzed instruction streams must return unimplemented exceptions before reaching them.

Test signals: use instruction-encoding tests for every major opcode, source zero mapping, destination zero rejection, PA1.1 versus PA2.0 compare status, Timex/Rolex special cases, fused op `0x2e`, and crashme-style malformed double register operands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/fpudispatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/frnd.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/frnd.c

Purpose: implements floating-point round-to-integer for single and double precision via `sgl_frnd` and `dbl_frnd`. Quad precision is documented as unimplemented elsewhere.

Important APIs and types: both functions accept a source pointer, unused null pointer, destination pointer, and FP status pointer. They use `Sgl_*`, `Dbl_*`, and conversion helper macros from `cnv_float.h` to inspect inexact, round, and sticky bits.

Control flow: each routine first returns infinities and quiet NaNs, quieting signaling NaNs or trapping invalid if configured. If the unbiased exponent already covers all fraction bits, it returns the input unchanged. Otherwise it shifts the significand down to an integer, checks discarded bits, rounds according to the current mode, shifts back, and rebuilds the exponent. Values with absolute value below one become signed zero or signed one depending on rounding mode and half-way rules.

State and persistence: no persistent local state. The destination receives the rounded FP encoding; `Set_invalidflag` and `Set_inexactflag` may mutate the status register unless traps return early.

Dependencies and integration: called from `fpudispatch.c` class 0 `FRND`/`FRMD` decode for single and double formats. Depends on the same status/trap conventions as other math-emu routines.

Risks: half-way handling for `ROUNDNEAREST` depends on correct sticky-bit macros, and negative near-zero values rely on preserving the sign while zeroing exponent/mantissa. Large exponents must avoid unnecessary shifts.

Test signals: cover positive and negative fractions below one, exact integers, half-way cases, odd/even ties, all rounding modes, signaling NaNs, quiet NaNs, infinities, and inexact trap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/frnd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/hppa.h -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/hppa.h

Purpose: supplies low-level double-word shift macros used by PA-RISC floating-point emulation headers.

Important APIs: `Shiftdouble(left, right, amount, dest)` handles constant shifts between two 32-bit words. `Variableshiftdouble` and `Variable_shift_double` handle variable shifts below 32 bits; the former masks the left operand's high bit, while the latter uses the raw left word.

Control flow: macro-only, expanding into one assignment or a small `if` sequence. These helpers are used to move bits between significand words, extension words, and guard/sticky accumulators during normalization, alignment, rounding, and denormalization.

State and persistence: no state is retained. The macros mutate only the destination expression supplied by callers.

Dependencies and integration: included by `float.h` or format-specific headers. `sgl_float.h`, `dbl_float.h`, arithmetic routines, and fused multiply-add code depend on these macros for exact cross-word shifts.

Risks: callers must honor the documented shift ranges; zero or 32 in the wrong macro can produce undefined behavior. Because these are macros, side-effect arguments can be dangerous. `Variableshiftdouble` and `Variable_shift_double` differ subtly in high-bit treatment.

Test signals: verify all supported shift amounts for representative pairs, especially amount 1, 4, 8, 24, 28, 31, and variable amount zero. Compare results against a 64-bit reference model in normalization and right-alignment cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/hppa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/math-emu.h -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/math-emu.h

Purpose: exposes the PA-RISC floating-point exception handler entry point to the rest of the architecture code.

Important API: `extern int handle_fpe(struct pt_regs *regs);` declares the handler that receives trap register state and coordinates floating-point emulation.

Control flow: this header has no executable logic. It includes `<asm/ptrace.h>` so the declaration can name `struct pt_regs`. Kernel trap code includes it before calling `handle_fpe()` for FP assist and emulation traps.

State and persistence: no state. The persistent contract is the function signature shared between `arch/parisc/kernel/traps.c` and `arch/parisc/math-emu/driver.c`.

Dependencies and integration: links the math-emulation directory to the architecture trap layer. `driver.c` supplies the implementation, which then reaches `decode_exc.c` and `fpudispatch.c`.

Risks: signature drift would break the trap integration. Because the handler receives mutable register state, callers and implementation must agree on PA-RISC `pt_regs` layout and trap return semantics.

Test signals: build with `CONFIG_MATH_EMULATION`, trigger a floating-point assist exception, verify `handle_fpe()` is called from traps, and check that user-visible signals or emulated instruction completion match hardware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/math-emu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfadd.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfadd.c

Purpose: implements `sgl_fadd`, single-precision IEEE-style addition for the PA-RISC software FPU.

Important APIs and types: the function takes left, right, destination, and status pointers using `sgl_floating_point` word encodings. It uses `Sgl_*` and `Ext_*` macros for field access, magnitude comparison, alignment, extension bits, normalization, rounding, and exception status.

Control flow: operands are copied locally and XORed to capture sign relationship. The routine handles NaNs and infinities first, including invalid opposite-signed infinity addition. It orders finite operands by magnitude, handles zero and denormal shortcuts, aligns the smaller operand into an extension word, performs addition or subtraction based on sign, normalizes cancellation or carry, rounds using the extension, then detects overflow and inexact.

State and persistence: writes one destination word and may update the status register. It does not allocate memory or maintain cross-call state.

Dependencies and integration: called by `fpudispatch.c` for class 3 `FADD` and by multi-op decode paths that emulate multiply-add as separate multiply and add on older formats.

Risks: signed-zero behavior for zero plus zero depends on rounding mode. The denormal path returns early in exact cases, so trap handling must stay aligned with PA-RISC requirements. The normalization labels and fallthrough make small changes risky.

Test signals: cover finite same-sign addition, opposite-sign cancellation, denormal operands, both-zero sign rules, infinities, signaling NaNs, overflow, inexact rounding ties, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfadd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfcmp.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfcmp.c

Purpose: implements `sgl_fcmp`, single-precision floating-point comparison for PA-RISC condition predicates.

Important APIs and types: inputs are two single-precision pointers, a condition selector `cond`, and a mutable status pointer. Condition helper macros such as `Exception(cond)`, `Unordered(cond)`, `Equal(cond)`, `Lessthan(cond)`, and `Greaterthan(cond)` determine the C-bit result.

Control flow: the routine copies both operands, checks for NaNs under infinity-exponent encodings, raises invalid for signaling NaNs or quiet NaNs when the condition requests an exception, and sets unordered status when appropriate. Non-NaN infinities fall through to ordinary comparisons. It then compares sign bits, treats `+0` and `-0` as equal, and uses unsigned word ordering for same-sign positives or reversed ordering for negatives.

State and persistence: result state is the FP status C-bit through `Set_status_cbit`; no destination register is written.

Dependencies and integration: called by `fpudispatch.c` compare decode for major opcodes `0x0c` and `0x0e`. `fpudispatch.c` may post-process the returned local status into compare queues or compare arrays by FPU generation.

Risks: NaN condition semantics are easy to invert, especially exception-requesting predicates. The signed comparison relies on IEEE bit ordering and special zero handling.

Test signals: compare zeros with opposite signs, positive and negative finite ordering, infinities, quiet NaN ordered/unordered predicates, signaling NaNs with invalid trap enabled and disabled, and PA2.0 compare-array update paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfcmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfdiv.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfdiv.c

Purpose: implements `sgl_fdiv`, single-precision floating-point division.

Important APIs and types: operands and destination are `sgl_floating_point` words; status controls invalid, divide-by-zero, overflow, underflow, and inexact traps. Guard and sticky booleans track rounding information.

Control flow: the function computes result sign, handles NaNs, infinities, zero divisor, and zero dividend, then computes the exponent difference. It normalizes denormal operands, performs a non-restoring divide over `SGL_P` bits, derives guard and sticky bits from the remainder, rounds if needed, installs mantissa and exponent, and handles overflow or underflow with trap wrapping or denormalization.

State and persistence: writes the destination and exception flags in the status word. It has no heap or static state.

Dependencies and integration: called by `fpudispatch.c` for `FDIV`. Depends on `sgl_float.h` for normalization, denormalization, mantissa operations, and rounding mode.

Risks: non-restoring divide is sensitive to sign-bit tests on intermediate remainders. Underflow detection distinguishes tininess before and after rounding; mistakes can set or miss underflow flags. Divide-by-zero and `0/0` must route to different exceptions.

Test signals: include finite exact and inexact divisions, subnormal numerator and denominator, division by zero, zero by zero, infinity by infinity, finite by infinity, overflow, gradual underflow, all rounding modes, and trap-enabled combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfdiv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfmpy.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfmpy.c

Purpose: implements `sgl_fmpy`, single-precision floating-point multiplication.

Important APIs and types: uses `sgl_floating_point` operands, a destination pointer, and FP status. It depends on `Sbit*`, `Slow4`, and `Sgl_*` macros for nibble-wise multiplication and IEEE field manipulation.

Control flow: the routine computes the result sign, handles NaNs, infinities, zero times infinity invalid cases, and zero operands. It calculates the biased destination exponent, normalizes denormals, left-shifts one operand for guard space, then performs a four-bit-at-a-time shift/add multiply. After left-justifying the product, it extracts guard and sticky bits, rounds according to the status rounding mode, and handles overflow, underflow, denormalization, and inexact.

State and persistence: writes one FP result and updates exception flags in `*status`. No static state is used.

Dependencies and integration: called directly by `fpudispatch.c` for `FMPY` and by multi-op emulation in `decode_06` and `decode_26`.

Risks: the product alignment and sticky accumulation depend on exact bit positions. The file has separate pre-round and underflow-round paths that must remain consistent. Invalid `inf * 0` handling must preserve NaN quieting priority.

Test signals: multiply normal, subnormal, zero, infinity, and NaN operands; verify signed zero, overflow largest-versus-infinity selection by rounding mode, underflow tininess, inexact traps, and exact powers of two.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfmpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfrem.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfrem.c

Purpose: implements `sgl_frem`, single-precision IEEE-style floating-point remainder.

Important APIs and types: takes two single operands, destination, and status. Uses `Sgl_*` macros for exponent extraction, normalization, subtraction, sign inversion, and denormal result construction.

Control flow: the routine rejects invalid first-operand infinity and zero divisor, quiets or returns NaNs, and returns the dividend when divisor is infinity. It preserves the dividend sign for the result, normalizes denormal operands, computes the exponent difference, handles quotient magnitude below one, then iteratively subtracts divisor-aligned mantissas. The final remainder is adjusted for nearest quotient selection, including exact half-divisor tie behavior, normalized, and underflow-checked.

State and persistence: writes the result and invalid or underflow flags/traps. Remainder is treated as exact, so no inexact flag is set.

Dependencies and integration: called from `fpudispatch.c` for `FREM`. Relies on PA-RISC status macros and `sgl_float.h`.

Risks: quotient rounding semantics are subtle: sign may flip if the nearest integer quotient is above the truncated quotient, and exact half cases depend on the `roundup` state. Underflow trap wrapping must preserve the computed sign.

Test signals: test dividend smaller than divisor, exactly half divisor, slightly above half, exact zero remainder, negative dividends, subnormal results, infinity and zero invalid cases, divisor infinity, and underflow trap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfrem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfsqrt.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfsqrt.c

Purpose: implements `sgl_fsqrt`, single-precision square root emulation.

Important APIs and types: source and destination are `sgl_floating_point` words; the second pointer argument is unused for decoder signature compatibility. Status controls invalid and inexact behavior.

Control flow: the function handles signaling NaNs, quiet NaNs, positive infinity, zeros, and invalid negative inputs. It normalizes denormal operands and determines whether the exponent is even. If needed it pre-shifts the significand, then performs a digit-by-digit square-root construction using `newbit`, `sum`, and subtract/shift steps. Remaining source bits indicate inexact; rounding uses current mode, with `ROUNDPLUS` and `ROUNDNEAREST` relevant for positive roots. It then computes the halved exponent and writes the result.

State and persistence: destination and status are the only mutated external state.

Dependencies and integration: called by `fpudispatch.c` for `FSQRT`. Depends on `sgl_float.h` helpers and PA-RISC exception macros from `float.h`.

Risks: comments admit the core algorithm is under-documented. Exponent parity and pre/post shifts are easy to break. Negative zero must return zero, while negative finite and negative infinity must signal invalid.

Test signals: include perfect squares, non-perfect inexact roots, subnormal inputs, smallest normal, positive infinity, quiet and signaling NaNs, negative finite values, negative infinity, signed zeros, and inexact trap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfsqrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfsub.c -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfsub.c

Purpose: implements `sgl_fsub`, single-precision subtraction for the PA-RISC software FPU.

Important APIs and types: signature mirrors `sgl_fadd`. It uses the same single-precision field and extension macros, but interprets the operand sign relation oppositely for subtract semantics.

Control flow: after copying operands and computing an XOR sign save, the routine handles NaNs and infinities. Same-signed infinities in subtraction are invalid; a right infinity returns with inverted sign. Finite operands are ordered by magnitude, with the larger operand becoming left and possibly sign-inverted. Zero and denormal shortcuts are handled exactly. The main path aligns the smaller operand, subtracts or adds magnitudes, normalizes cancellation, rounds from the extension word, then checks overflow and inexact.

State and persistence: writes destination and status flags only. No persistent memory is retained.

Dependencies and integration: called by `fpudispatch.c` for `FSUB` and by `decode_26` multi-op emulation. Shares most algorithmic structure with `sfadd.c`.

Risks: because this file is almost a sign-variant of addition, divergences from `sfadd.c` need careful review. Signed-zero selection, infinity invalid rules, and sign inversion after magnitude swapping are common bug sites.

Test signals: subtract equal finite numbers, opposite zero combinations, normal minus subnormal, subnormal minus normal, infinities with same and opposite signs, NaNs, overflow, inexact rounding, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfsub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sgl_float.h -->
# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sgl_float.h

Purpose: defines the single-precision bit-manipulation API used by all PA-RISC single FP emulation routines and the single-extended format used by fused multiply-add.

Important APIs and macros: it maps generic fields to single fields (`Sgl_sign`, `Sgl_exponent`, `Sgl_mantissa`), provides tests for zero, NaN, infinity, hidden bits, signaling NaNs, and magnitude ordering, and provides mutators for signs, exponents, mantissas, infinities, largest finite values, quiet/signaling NaNs, normalization, denormalization, overflow selection, and pointer copy. The `Sglext_*` family models a 48-bit mantissa extension across two words.

Control flow: macro expansions implement inline arithmetic primitives: shifts, cross-word shifts, alignment with sticky-bit preservation, addition/subtraction with borrow/carry, XOR swapping, normalization loops, and denormalization with tininess checks.

State and persistence: no static runtime state. The header defines the source-level ABI between arithmetic files and the bit encoding from `float.h`.

Dependencies and integration: included by every `sf*.c` file, `frnd.c`, and `fmpyfadd.c`. It depends on lower-level macros and constants such as `SGL_P`, `SGL_BIAS`, `SGL_INFINITY_EXPONENT`, `Sall`, and `Deposit_*`.

Risks: macro side effects, missing braces, and operator precedence can create subtle bugs. `Sglext_denormalize` uses DBL-related constants in one range check, which deserves scrutiny against intended single-extended width. Rounding and tininess behavior are centralized here, so changes have broad blast radius.

Test signals: compile with warning-heavy configs, compare macro operations against reference IEEE encodings, test every arithmetic routine after any header change, and add targeted tests for sticky-bit alignment and denormalization boundary exponents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/math-emu/sgl_float.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/parisc/mm/Makefile

Purpose: declares the PA-RISC architecture memory-management objects built into the kernel.

Important build rules: `obj-y := init.o fault.o ioremap.o fixmap.o` always builds core initialization, page fault handling, I/O remapping, and fixmap support. `obj-$(CONFIG_HUGETLB_PAGE) += hugetlbpage.o` conditionally includes huge TLB support.

Control flow: build-system only. Kbuild expands `obj-y` and config-dependent object lists when building `arch/parisc/mm/`.

State and persistence: no runtime state. Its persistent effect is the kernel link composition for PA-RISC MM code.

Dependencies and integration: selected from the parent architecture Makefile. The included objects provide symbols consumed by trap handling, generic MM, TLB flush code, ioremap callers, fixmap users, and hugetlb core.

Risks: omitting an always-needed object would create link failures or missing runtime handlers. Accidentally making `hugetlbpage.o` unconditional could pull hugepage code into unsupported configs; making core files conditional could break boot.

Test signals: build PA-RISC defconfigs with and without `CONFIG_HUGETLB_PAGE`, verify symbols such as `do_page_fault`, `paging_init`, `ioremap_prot`, and `set_fixmap` resolve, and run sparse or allmodconfig-style coverage for conditional hugepage paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/parisc/mm/fault.c

Purpose: handles PA-RISC page faults, access-type decoding, exception-table fixups, trap descriptions, user signal delivery, and non-access DTLB faults.

Important APIs and functions: `parisc_acctyp()` decodes faulting instructions into `VM_READ`, `VM_WRITE`, or `VM_EXEC`; `fixup_exception()` applies exception-table fixups for kernel user-access helpers; `trap_name()` names trap codes; `do_page_fault()` is the main MM fault handler; `handle_nadtlb_fault()` handles cache/probe/LPA non-access DTLB cases.

Control flow: `do_page_fault()` rejects no-MM contexts, derives access flags from the instruction, finds or expands the VMA, validates permissions, calls `handle_mm_fault()`, handles retry/completed/error cases, and maps failures to kernel fixups, user `SIGSEGV`/`SIGBUS`, memory-failure signals, or `parisc_terminate()`. `handle_nadtlb_fault()` nullifies selected cache flush/purge instructions, evaluates PROBE without faulting pages in, and returns zero for unhandled cases.

State and persistence: updates register state during fixups and non-access handlers, including IAOQ, PSW bits, base modification, target registers, and error registers. It logs fatal user faults subject to `show_unhandled_signals` and rate limits.

Dependencies and integration: called from `arch/parisc/kernel/traps.c`. Relies on Linux MM, exception tables, perf fault events, hugetlb memory failure helpers, and PA-RISC instruction/register definitions.

Risks: instruction access decoding must be accurate or permissions and signal codes will be wrong. Kernel fixups must avoid taking branch delay slots. PROBE handling intentionally does not fault pages in, so it can differ from a subsequent real access.

Test signals: user read/write/execute faults, stack growth, invalid permissions, unmapped addresses, OOM, hwpoison, kernel `get_user`/`put_user` fixups, unaligned traps, cache flush nullification, PROBE results, and LPA target zeroing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/mm/fixmap.c -->
# sources/distributed-fs/ceph-client/arch/parisc/mm/fixmap.c

Purpose: provides PA-RISC fixed-address mapping updates for kernel subsystems that need temporary or special virtual mappings.

Important APIs: `set_fixmap(enum fixed_addresses idx, phys_addr_t phys)` installs a `PAGE_KERNEL_RWX` PTE for the fixed virtual address. `clear_fixmap(enum fixed_addresses idx)` clears that PTE. Both are `notrace`, appropriate for low-level contexts.

Control flow: `set_fixmap()` converts the fixed index to a virtual address, walks the kernel page table to the PTE, writes a physical mapping with `set_pte_at()`, and flushes the one-page kernel TLB range. `clear_fixmap()` obtains the kernel PTE via `virt_to_kpte()`, warns if already empty, clears it, and flushes the same range.

State and persistence: mutates `init_mm` kernel page tables. The mapping persists until explicitly cleared or overwritten. TLB flushes synchronize CPU translation state.

Dependencies and integration: depends on `fixmap_init()` in `init.c` having allocated the fixmap page-table range. Includes cache/TLB and fixmap architecture headers. Used by architecture features needing stable high virtual slots.

Risks: always using RWX permissions is broad and may conflict with strict W/X expectations. Missing flushes would leave stale translations. Calling before `fixmap_init()` would dereference missing page tables.

Test signals: set and clear representative fixed indices, verify physical translation and permissions, detect double clear warning, check TLB invalidation on all relevant CPUs, and test under kprobe/tracing-disabled contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/mm/fixmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/mm/hugetlbpage.c -->
# sources/distributed-fs/ceph-client/arch/parisc/mm/hugetlbpage.c

Purpose: implements PA-RISC huge TLB page-table operations for Linux hugetlb.

Important APIs and functions: `huge_pte_alloc()` allocates the first base PTE for a hugepage-aligned address; `huge_pte_offset()` locates an existing one; `set_huge_pte_at()`, `huge_ptep_get_and_clear()`, `huge_ptep_set_wrprotect()`, and `huge_ptep_set_access_flags()` update the range. `purge_tlb_entries_huge()` flushes all real hugepage-sized hardware TLB entries represented by a Linux hugepage.

Control flow: allocation and lookup align addresses to `HPAGE_MASK` and walk PGD/P4D/PUD/PMD levels to huge PTEs. Setting a huge PTE writes `1 << HUGETLB_PAGE_ORDER` contiguous base PTEs, incrementing the physical address by `PAGE_SIZE` for each sub-PTE, then purges huge TLB entries. Clear and write-protect reuse the same helper with zero or protected entries.

State and persistence: mutates per-mm page tables and TLB state. The code assumes callers hold the PA TLB lock for the internal helper.

Dependencies and integration: used by generic hugetlb MM when `CONFIG_HUGETLB_PAGE` is enabled. Depends on PA-RISC TLB flush encoding, `REAL_HPAGE_SHIFT`, `HPAGE_SHIFT`, and page-table allocation helpers.

Risks: hugepage alignment is critical because callers expect the first sub-PTE. Physical address increments must not cross unintended ranges. Missing lock discipline or incomplete purge loops can leave stale huge translations.

Test signals: allocate, fault, write-protect, clear, and change access flags for hugepages; test configurations where Linux hugepage size spans multiple hardware hugepage entries; verify TLB shootdown and COW/protection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/mm/hugetlbpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/parisc/mm/init.c

Purpose: initializes PA-RISC memory management, including physical memory ranges, memblock reservations, kernel page tables, gateway and fixmap mappings, BTLB entries, space-ID allocation, TLB flushing, protection maps, and execmem setup.

Important APIs and state: exports `swapper_pg_dir`, initial PTE/PMD arrays, `pmem_ranges`, `parisc_vmalloc_start`, `paging_init()`, `mem_init()`, `free_initmem()`, `set_kernel_text_rw()`, `mark_rodata_ro()`, `alloc_sid()`, `free_sid()`, `flush_tlb_all()`, `btlb_init_per_cpu()`, and optional `execmem_arch_setup()`. Static state tracks system RAM resources, `mem_limit`, kernel read-only transition, BTLB data, and space-ID bitmaps.

Control flow: boot starts with `setup_bootmem()`, which sorts firmware memory ranges, applies gaps and `mem=`, registers resources, reserves firmware/kernel/initrd/hole memory, initializes PDT, and configures memblock. `pagetable_init()` maps all physical ranges; `gateway_init()` maps the gateway page; `fixmap_init()` allocates fixmap page tables; `paging_init()` flushes caches/TLBs. Later functions harden kernel mappings, free init memory, set vmalloc layout, and manage TLB space IDs.

State and persistence: this file establishes persistent kernel mappings and memory resources. Space IDs are allocated under `sid_lock`, freed into dirty bitmaps, and recycled only after global TLB flush.

Dependencies and integration: consumes firmware inventory, memblock, generic MM, cache/TLB code, pdc/chassis/PDT helpers, fixmap headers, and mmu context code.

Risks: early mapping size limits require bottom-up memblock allocation. Incorrect memory range truncation or hole reservation can corrupt memory. Space-ID recycling before TLB purge would create address-space aliasing. RWX-to-RO transitions must be synchronized with cache and TLB flushing.

Test signals: boot on 32-bit and 64-bit PA-RISC, sparsemem and non-sparsemem, `mem=` limits, initrd above limit, strict RWX, SMP TLB flush recycling, BTLB insertion, vmalloc start on PCXL, and execmem users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/mm/ioremap.c -->
# sources/distributed-fs/ceph-client/arch/parisc/mm/ioremap.c

Purpose: implements PA-RISC `ioremap_prot()` and exports it for mapping physical I/O ranges into kernel virtual address space.

Important API: `void __iomem *ioremap_prot(phys_addr_t phys_addr, size_t size, pgprot_t prot)` maps an I/O physical range with caller-supplied page protection. `EXPORT_SYMBOL(ioremap_prot)` makes it available to drivers and architecture code.

Control flow: with `CONFIG_EISA`, the function detects selected EISA physical address windows and extends them with `F_EXTEND(0xfc000000)`. It then rejects attempts to remap normal unreserved RAM below `high_memory` by walking pages over the requested range and returning `NULL` if any page is not reserved. Valid mappings fall through to `generic_ioremap_prot()`.

State and persistence: creates persistent vmalloc/ioremap mappings through the generic ioremap layer. It does not store private state.

Dependencies and integration: used via `asm/io.h` ioremap macros, including write-combining mappings with `_PAGE_IOREMAP`. Depends on Linux vmalloc/io/mm helpers, `high_memory`, page reserved flags, and PA-RISC EISA address extension.

Risks: `phys_addr + size - 1` can overflow if unchecked by callers. The normal-RAM rejection depends on `PageReserved` being accurate. EISA address-window boundaries must match hardware expectations or drivers may map the wrong bus address.

Test signals: map reserved device memory, reject ordinary RAM, exercise EISA windows with and without `CONFIG_EISA`, validate `ioremap_wc` paths, and test zero or overflow-prone sizes through callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/mm/ioremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/net/Makefile -->
# sources/distributed-fs/ceph-client/arch/parisc/net/Makefile

Purpose: selects PA-RISC BPF JIT objects for the kernel build.

Important build rules: `obj-$(CONFIG_BPF_JIT) += bpf_jit_core.o` includes shared PA-RISC JIT support when BPF JIT is enabled. A `CONFIG_64BIT` conditional adds `bpf_jit_comp64.o` for 64-bit kernels and `bpf_jit_comp32.o` otherwise.

Control flow: build-system only. Kbuild evaluates the config symbols and appends the architecture-specific JIT compiler object matching word size.

State and persistence: no runtime state in the Makefile. Its lasting effect is which JIT implementation is linked into the kernel image.

Dependencies and integration: integrates with the generic BPF JIT framework and PA-RISC architecture build. The selected compiler object must match the ABI, instruction encoding, register width, and calling convention for the target kernel bitness.

Risks: selecting the wrong compiler object would produce invalid code generation or link failures. Building compiler objects without `bpf_jit_core.o` would omit shared support. Missing `CONFIG_BPF_JIT` gating could include unused code in kernels that disable JIT.

Test signals: build PA-RISC with `CONFIG_BPF_JIT` on and off, for both 32-bit and 64-bit configurations; run BPF JIT selftests or verifier/JIT smoke tests; inspect linked objects to ensure only the matching compiler is included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/net/Makefile -->
