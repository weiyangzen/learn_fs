# Group Research: subset-b-000748

This grouped report covers the MIPS FPU emulator single/double IEEE-754 helpers and MIPS memory-management cache, page, ioremap, DMA, fault, and exception-vector support under `sources/distributed-fs/ceph-client/arch/mips`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dsemul.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dsemul.c

Purpose: implements branch delay-slot emulation by placing a tiny `struct emuframe` in a per-process user page at `STACK_TOP`. The frame contains the instruction to execute and a `BREAK_MATH` instruction that returns control to the kernel. This avoids full instruction emulation while keeping execution in user privilege.

Important APIs and functions: `mips_dsemul()` allocates/fills a frame and redirects `regs->cp0_epc`; `do_dsemulret()` handles the break return; `dsemul_thread_cleanup()` frees a thread-owned frame; `dsemul_thread_rollback()` rewinds EPC during signal/exception paths; `dsemul_mm_cleanup()` releases the mm bitmap. The `emuframe` allocation state lives in `mm->context.bd_emupage_allocmap` protected by `bd_emupage_lock`, with waiters on `bd_emupage_queue`.

Control flow: `mips_dsemul()` fast-paths NOP and microMIPS `ADDIUPC`, otherwise allocates or reuses a frame, writes it with `access_process_vm(FOLL_FORCE|FOLL_WRITE)`, records branch/continue PCs in `current->thread`, and sets EPC to the frame. On break, `do_dsemulret()` frees the frame and jumps to `bd_emu_cont_pc`.

Dependencies and integration: called by the MIPS FPU/branch emulator and trap paths; uses `asm/branch.h`, `asm/inst.h`, `asm/fpu_emulator.h`, user access helpers, task/mm context state, and MIPS ISA mode helpers.

Risks and test signals: correctness depends on not trusting user-created break frames, atomic frame ownership, signal rollback, microMIPS halfword encoding, and frame exhaustion wait behavior. Test with branch delay-slot FPU instructions, invalid delay-slot instructions, signals during emulation, fork/exit cleanup, and concurrent threads exhausting the emupage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dsemul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754.c

Purpose: defines the shared single-precision and double-precision special value tables used by the MIPS IEEE-754 emulator. These constants supply canonical zeros, ones, tens, infinities, indefinite NaNs, maxima, minima, and large powers used by the conversion and arithmetic helpers.

Important APIs/types: exports `__ieee754dp_spcvals[]` and `__ieee754sp_spcvals[]` as constant arrays of `union ieee754dp` and `union ieee754sp`. Macros `xPCNST`, `DPCNST`, and `SPCNST` build bitfield initializers with the proper exponent bias.

Control flow: there is no runtime control flow beyond static initialization. The file is included in the math emulator object set so helpers such as `ieee754sp_zero()`, `ieee754sp_inf()`, `ieee754dp_indef()`, and similar macros can index stable constants declared in the headers.

State and persistence: all data is read-only kernel text/data state. No per-task state is mutated here; exception and rounding state remains in `ieee754_csr` elsewhere.

Dependencies and integration: depends on `ieee754.h`, `ieee754sp.h`, and `ieee754dp.h` for the union layouts and exponent constants. It integrates with every arithmetic/conversion implementation that returns canonical special values.

Risks and test signals: bitfield ordering is architecture-sensitive and relies on `__BITFIELD_FIELD` definitions. Regression tests should compare raw bit patterns for all special values in legacy and NaN-2008 modes, especially indefinite NaN encodings and signed zero preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754.h -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754.h

Purpose: public common header for the MIPS software FPU IEEE-754 emulator. It defines the raw single/double union layouts, operation prototypes, class and exception constants, compare masks, and access to the emulated FPU control/status register.

Important APIs/types: `union ieee754sp` and `union ieee754dp` expose sign, biased exponent, mantissa, and raw `bits`. The header declares arithmetic, conversion, compare, sqrt, fused multiply-add, min/max, class, abs, and neg APIs for both precisions. `struct _ieee754_csr` maps FCR31 fields such as rounding mode, exception cause/sticky/mask bits, `nan2008`, `abs2008`, and `nod`.

Control flow: inline helpers get/set rounding mode, current exceptions, and sticky exceptions. The macro `ieee754_csr` resolves to `current->thread.fpu.fcr31`, so all operations implicitly act on the current task's FPU state.

State and persistence: persistent state is per-task FPU control state. Helpers mutate exception cause/sticky bits and rounding mode but do not allocate memory or keep global state.

Dependencies and integration: includes Linux types, scheduler state, byte order, and MIPS bitfield helpers. It is consumed by `cp1emu.c` and all `sp_*`/`dp_*` emulator files.

Risks and test signals: because it maps a bitfield over FCR31, ABI bit ordering and endianness must be correct. Tests should validate exception masks, sticky flag accumulation, condition code fields, NaN-2008 toggles, and raw bit output for all public operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754d.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754d.c

Purpose: debug dumping helpers for single and double IEEE-754 emulator values. It prints raw bits and a decoded textual representation to the kernel log, useful when diagnosing software FPU emulation.

Important APIs/functions: `ieee754dp_dump(char *m, union ieee754dp x)` and `ieee754sp_dump(char *m, union ieee754sp x)` both return the input value after printing. They classify using `ieee754dp_class()` or `ieee754sp_class()` and inspect sign, exponent, and mantissa bits through precision-specific macros.

Control flow: each function prints a prefix and raw bits, switches on the value class, and renders NaN mantissas, signed infinity, signed zero, denormal mantissa/exponent, or normal mantissa/exponent. Unknown classes print an error-like string.

State and persistence: no persistent state is stored. The only side effect is `printk()` output, which can affect log volume and timing when enabled.

Dependencies and integration: depends on `linux/printk.h`, `linux/types.h`, and both precision headers. It is a diagnostic endpoint for emulator maintainers and can be called inline in math paths during debugging.

Risks and test signals: avoid using in hot paths without rate control. Tests are mainly developer diagnostics: feed representative bit patterns and confirm class decoding, exponent bias display, signed zero, and NaN mantissa rendering remain sane.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754dp.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754dp.c

Purpose: double-precision common implementation for classification, signaling-NaN quieting, and final result formatting with rounding, underflow, overflow, and exception flag handling.

Important APIs/functions: `ieee754dp_class()` returns the internal class; `ieee754dp_nanxcpt()` raises invalid operation and converts an sNaN to qNaN according to legacy or NaN-2008 mode; `ieee754dp_format(int sn, int xe, u64 xm)` turns an unbiased exponent plus guard/round/sticky mantissa into a final `union ieee754dp`.

Control flow: `ieee754dp_format()` handles tiny results first, respecting `ieee754_csr.nod`, then sets inexact/underflow if GRS bits exist, rounds by `ieee754_csr.rm`, adjusts exponent on carry, detects overflow, and finally builds normal or denormal output.

State and persistence: updates `ieee754_csr.cx` and sticky `sx` through `ieee754_setcx()`. It has no global mutable state.

Dependencies and integration: used by all double-precision arithmetic/conversion helpers; depends on `ieee754dp.h` and internal macros from `ieee754int.h`.

Risks and test signals: rounding and tininess behavior are fragile. Exercise all rounding modes, underflow with `nod`, exponent overflow, qNaN/sNaN conversion under both NaN modes, exact denormals, and exceptions masked/unmasked through FCR31.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754dp.h -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754dp.h

Purpose: internal double-precision helper header for the IEEE-754 emulator. It defines double exponent/mantissa constants, raw field accessors, sticky shifts, denormal normalization macros, and final builder helpers.

Important APIs/macros: `DP_EBIAS`, `DP_EMIN`, `DP_EMAX`, `DP_FBITS`, `DP_HIDDEN_BIT`, `DPSIGN`, `DPBEXP`, and `DPMANT` describe the format. `XDPSRS`, `XDPSRS1`, and `XDPSRSX1` implement sticky right shifts used by arithmetic. `DPDNORMX/Y/Z` normalize denormal mantissas. `builddp()` constructs raw double values, and declarations expose `ieee754dp_nanxcpt()` and `ieee754dp_format()`.

Control flow: this file is macro-heavy and inlines logic into callers. Arithmetic files unpack values, normalize denormals, operate on extended mantissas, then call `ieee754dp_format()`.

State and persistence: no standalone state. Macros may read or update caller locals and rely on `ieee754_csr` through included internal helpers.

Dependencies and integration: includes `ieee754int.h`, which provides class and exception helpers. All double-precision math files depend on these definitions.

Risks and test signals: sticky shift macros must avoid undefined behavior for large shifts and preserve nonzero low bits. Validate boundary mantissas, denormal normalization loops, 64-bit shifts, and construction of min/max/infinity/NaN constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754int.h -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754int.h

Purpose: private common header for IEEE-754 emulator internals. It provides class-pair indexing, fused multiply-add flag bits, exception flag helpers, and unpack/flush macros for single and double values.

Important APIs/macros: `CLPAIR()` indexes switch cases over two value classes. `MADDF_NEGATE_PRODUCT` and `MADDF_NEGATE_ADDITION` parameterize fused operations. `ieee754_clearcx()`, `ieee754_setcx()`, and `ieee754_setandtestcx()` mutate current and sticky exception flags. `COMP*`, `EXPLODE*`, and `FLUSH*` macros declare locals, classify raw inputs, normalize exponent/mantissa fields, and optionally flush denormals to zero when `nod` is set.

Control flow: arithmetic functions use a consistent pattern: `COMP`, `EXPLODE`, `ieee754_clearcx`, `FLUSH`, class-pair special handling, arithmetic on normalized mantissas, and precision-specific formatting.

State and persistence: exception mutations are per-current-task via `ieee754_csr`; no global state is allocated.

Dependencies and integration: included by both precision-specific internal headers. It bridges raw union fields from `ieee754.h` with arithmetic implementations.

Risks and test signals: macro side effects are dense and caller-local variable names are fixed. Test classifying sNaN/qNaN under `nan2008`, denormal flushing under `nod`, exception sticky accumulation, and every class-pair switch table for missing combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754sp.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754sp.c

Purpose: single-precision common implementation for classification, signaling-NaN exception conversion, and final result formatting with IEEE-754 rounding and exception behavior.

Important APIs/functions: `ieee754sp_class()` returns a class from raw fields; `ieee754sp_nanxcpt()` raises invalid operation and quiets signaling NaNs according to `nan2008`; `ieee754sp_format(int sn, int xe, unsigned int xm)` creates a final single from sign, unbiased exponent, and a mantissa with guard/round/sticky bits.

Control flow: `ieee754sp_format()` handles subnormal/tiny results, optional no-denormal flush, inexact rounding, exponent carry, overflow to infinity or max finite based on rounding mode, and normal/denormal construction via `buildsp()`.

State and persistence: updates the current task's FCR31 exception cause/sticky bits through `ieee754_setcx()`. No other state is stored.

Dependencies and integration: used by all `sp_*` arithmetic and conversion files, and by double-to-single conversion. It depends on `ieee754sp.h`.

Risks and test signals: highest-risk areas are underflow after rounding, GRS handling, NaN-2008 sNaN conversion, and overflow result selection under RU/RD/RZ/RN. Tests should use raw bit vectors around exponent and mantissa boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754sp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754sp.h -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754sp.h

Purpose: internal single-precision helper header for the IEEE-754 emulator. It defines single exponent/mantissa constants, accessors, sticky shifts, denormal normalization macros, and builder/formatter declarations.

Important APIs/macros: `SP_EBIAS`, `SP_EMIN`, `SP_EMAX`, `SP_FBITS`, `SP_HIDDEN_BIT`, `SP_SIGN_BIT`, `SPSIGN`, `SPBEXP`, and `SPMANT` describe raw format. `XSPSRS64`, `XSPSRS`, and `XSPSRS1` preserve sticky information during shifts. `SPDNORMX/Y/Z` normalize denormals. `buildsp()` constructs a raw single result.

Control flow: callers expand macros to normalize inputs, perform arithmetic in extended precision, and call `ieee754sp_format()` for final rounding and exception handling.

State and persistence: no independent state. Some macros mutate caller locals and rely on `ieee754_csr` indirectly through included internals.

Dependencies and integration: includes `ieee754int.h`; used by every `sp_*` source file and by debug/conversion utilities.

Risks and test signals: macro shift expressions can be sensitive near word-width limits. Tests should stress denormal normalization, sticky bits after long shifts, exact powers of two, signed zero building, and raw bit encodings for boundary values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754sp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/me-debugfs.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/me-debugfs.c

Purpose: exposes MIPS FPU emulator statistics through debugfs. It creates aggregate counter files and per-instruction counter files under `mips_debugfs_dir`, enabling runtime observability of software FPU emulation.

Important APIs/functions: defines per-CPU `fpuemustats`; `fpuemu_stat_get()` sums a selected `local_t` counter across online CPUs; `adjust_instruction_counter_name()` converts struct field underscores to dotted instruction names; `fpuemustats_clear_show()` zeroes many counters on the current CPU; `debugfs_fpuemu()` creates the debugfs tree.

Control flow: at `arch_initcall`, the file creates `fpuemustats`, a `fpuemustats_clear` file, aggregate stats, and an `instructions` subdirectory. `DEFINE_SIMPLE_ATTRIBUTE` and `DEFINE_SHOW_ATTRIBUTE` connect debugfs reads to counter aggregation/clear behavior.

State and persistence: state is per-CPU in-memory counters only. There is no persistence across reboot. The clear path writes only this CPU's counters, while reads aggregate online CPUs.

Dependencies and integration: depends on `asm/fpu_emulator.h` counter layout, `asm/debug.h` root directory, debugfs, cpumask iteration, and local counters.

Risks and test signals: clear-on-read is surprising and only clears the local CPU. Tests should mount debugfs, validate file names, check aggregate reads after emulated instructions, and verify no NULL debugfs root assumptions under disabled debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/me-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_2008class.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_2008class.c

Purpose: implements the MIPS/IEEE-754-2008 single-precision `CLASS.S` operation, returning a 10-bit mask describing the class and sign of a floating-point operand.

Important APIs/functions: `ieee754sp_2008class(union ieee754sp x)` expands `COMPXSP` and `EXPLODEXSP` to classify the raw value, then maps `SNAN`, `QNAN`, signed infinities, normals, denormals, and zeros to the architecture-defined bit positions.

Control flow: single switch on `xc`. Signed non-NaN classes shift a base mask by either 0 for negative classes or 4 for positive classes. Unknown classes log with `pr_err()` and return 0.

State and persistence: no exception flags are cleared or set here, and no persistent state is changed. It is a pure classification helper apart from an unexpected-class log.

Dependencies and integration: included by the FPU emulator for `CLASS.S` instruction handling; depends on `ieee754sp.h` classification macros and `ieee754_csr.nan2008` behavior via `EXPLODEXSP`.

Risks and test signals: verify exact bit mask mapping, especially signed zero and signed denormal values. Include sNaN/qNaN bit patterns in both NaN modes to confirm classification matches the active FCR31 mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_2008class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_add.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_add.c

Purpose: implements single-precision IEEE-754 addition for the MIPS FPU emulator.

Important APIs/functions: `ieee754sp_add(union ieee754sp x, union ieee754sp y)` is the exported helper. It uses `EXPLODEXSP`, `EXPLODEYSP`, `FLUSHXSP/YSP`, `ieee754sp_nanxcpt()`, special value constructors, sticky shifts, and `ieee754sp_format()`.

Control flow: after classification and exception reset, a `CLPAIR` switch handles sNaN/qNaN precedence, infinities, signed zero rules, and denormal normalization. For finite nonzero values it adds guard/round/sticky bits, aligns exponents by sticky right shifting, adds equal-sign mantissas or subtracts opposite-sign mantissas, normalizes cancellation, and delegates rounding/overflow/underflow to the formatter.

State and persistence: updates only `ieee754_csr` exception fields. The rounding mode determines signed zero for exact cancellation.

Dependencies and integration: called from `cp1emu.c` for ADD.S and by legacy `abs/neg` helpers when `abs2008` is disabled.

Risks and test signals: test all NaN precedence cases, `+inf + -inf`, signed zero under round-down, denormal inputs with and without `nod`, cancellation normalization, exponent alignment with sticky bits, and each rounding mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_add.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_cmp.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_cmp.c

Purpose: implements single-precision comparisons for the emulator, returning whether the requested comparison predicate is true.

Important APIs/functions: `ieee754sp_cmp(union ieee754sp x, union ieee754sp y, int cmp, int sig)` accepts a bitmask of `IEEE754_CLT`, `CEQ`, `CGT`, and `CUN`, plus a signaling flag for unordered comparisons.

Control flow: values are classified and denormals optionally flushed, then current exceptions are cleared. If either operand is NaN, invalid operation is raised for signaling comparisons or sNaN operands, and unordered result is selected from `cmp`. Otherwise raw signed values are transformed into an order-preserving integer domain and compared.

State and persistence: mutates only the current exception flags in `ieee754_csr`.

Dependencies and integration: used by COP1 compare instruction emulation. Depends on `SP_SIGN_BIT` and internal classification macros.

Risks and test signals: validate signed zero equality, negative ordering transform, all unordered predicates, sNaN invalid exceptions, qNaN with nonsignaling compare, and denormal flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_cmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_div.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_div.c

Purpose: implements single-precision division in software for MIPS FPU emulation.

Important APIs/functions: `ieee754sp_div(union ieee754sp x, union ieee754sp y)` handles all IEEE classes, raises zero-divide or invalid exceptions, performs a bitwise quotient loop, and uses `ieee754sp_format()` for final rounding.

Control flow: after unpacking and clearing exceptions, the class-pair switch handles NaNs, infinities, zero/zero invalid, finite/zero divide-by-zero, zero/finite signed zero, and denormal normalization. The finite path shifts operands into GRS space, computes quotient bits by repeated subtract/shift, sets sticky if remainder remains, normalizes the quotient, and formats with sign `xs ^ ys`.

State and persistence: only exception flags in FCR31 are changed.

Dependencies and integration: called by DIV.S emulation; depends on sticky shift and class macros from `ieee754sp.h`.

Risks and test signals: test exact and inexact quotients, divide by zero, zero divided by finite, infinity combinations, denormal operands, rounding carry, and sticky remainder behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fdp.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fdp.c

Purpose: converts double-precision emulator values to single precision.

Important APIs/functions: `ieee754sp_fdp(union ieee754dp x)` is the exported conversion helper. `ieee754sp_nan_fdp()` builds a single NaN payload from double sign and mantissa. The implementation uses double unpacking and single formatting.

Control flow: after clearing exceptions and flushing double denormals as configured, it handles sNaN by quieting first, converts qNaN payloads with legacy fallback to indefinite if the truncated payload is not still NaN, preserves infinity and signed zero, treats double denormals as underflow/inexact to zero or min denormal depending on rounding, and formats normal values after a sticky right shift from DP mantissa width to SP plus GRS bits.

State and persistence: updates current exception flags for invalid, underflow, and inexact cases.

Dependencies and integration: used by CVT.S.D emulation and relies on both precision headers.

Risks and test signals: test NaN payload truncation, legacy versus NaN-2008 mode, min double normal/denormal conversion, overflows to single infinity/max, and all rounding modes around halfway values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fint.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fint.c

Purpose: converts signed 32-bit integers to single-precision emulator values.

Important APIs/functions: `ieee754sp_fint(int x)` handles zero, +/-1, +/-10 through special constants, then converts magnitude/sign into an extended mantissa and calls `ieee754sp_format()`.

Control flow: clears current exceptions, detects sign, handles the most-negative integer without unsafe negation, sets an initial exponent of `SP_FBITS + 3`, shifts right with sticky bits if the integer is too wide for extended precision, otherwise normalizes left until the hidden bit reaches the expected position.

State and persistence: only the current exception flags can change via the formatter, mainly inexact for unrepresentable integers.

Dependencies and integration: called by CVT.S.W emulation and uses single helper macros/constants.

Risks and test signals: test `INT_MIN`, exact powers of two, values requiring rounding, +/-1 and +/-10 fast constants, and all rounding modes for integers just above 24-bit precision.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_flong.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_flong.c

Purpose: converts signed 64-bit integers to single-precision emulator values.

Important APIs/functions: `ieee754sp_flong(s64 x)` mirrors the 32-bit conversion with a 64-bit temporary mantissa, special-casing zero, +/-1, +/-10, and the most-negative 64-bit value.

Control flow: after sign/magnitude extraction, it sets an extended single exponent and either sticky-shifts right until the value fits or left-normalizes small magnitudes before calling `ieee754sp_format()`.

State and persistence: formatter updates inexact/overflow only through the current task's FCR31 exception fields. No other state exists.

Dependencies and integration: used by CVT.S.L and by `ieee754sp_rint()` to rebuild rounded integral results.

Risks and test signals: test `S64_MIN`, large values that round to powers of two, exact 24-bit mantissas, low values, and all rounding modes. Watch that the 64-bit temporary interacts correctly with single-precision shift macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_flong.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fmax.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fmax.c

Purpose: implements MIPS single-precision `MAX.S` and `MAXA.S` semantics, including NaN preference rules and signed-zero tie handling.

Important APIs/functions: `ieee754sp_fmax()` returns the numeric maximum; `ieee754sp_fmaxa()` returns the operand with maximum absolute magnitude. Both use classification, denormal flush, invalid exception for sNaN, and direct field comparisons.

Control flow: each function first handles sNaN and qNaN precedence, preferring numeric operands over quiet NaNs. Infinity/zero cases are handled explicitly. The finite path compares signs, exponents, and mantissas; `fmaxa` ignores sign for magnitude then uses sign as a tie breaker.

State and persistence: mutates only exception flags for sNaN invalid operations.

Dependencies and integration: used by MIPS R6 or IEEE-754-2008 max instruction emulation through the COP1 emulator.

Risks and test signals: test qNaN versus numeric, sNaN invalid, +0 versus -0, equal-magnitude opposite signs for `MAXA`, infinities, denormals under `nod`, and exact mantissa tie cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fmax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fmin.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fmin.c

Purpose: implements MIPS single-precision `MIN.S` and `MINA.S` semantics.

Important APIs/functions: `ieee754sp_fmin()` returns the numeric minimum; `ieee754sp_fmina()` returns the operand with minimum absolute magnitude. They share the same classification and NaN handling approach as the max helpers.

Control flow: sNaNs raise invalid and are quieted, qNaNs are returned only if both operands are qNaN, and numeric operands are preferred when exactly one input is qNaN. Explicit infinity/zero logic handles signed zero. Finite comparisons examine sign, exponent, and mantissa, with absolute-value comparison in `fmina`.

State and persistence: only current exception flags change on signaling NaNs.

Dependencies and integration: called by COP1 emulator for min/mina instructions. Depends on single-precision classification and denormal macros.

Risks and test signals: test -0 versus +0, negative finite ordering, qNaN numeric preference, both-qNaN behavior, sNaN exceptions, equal magnitude ties, and denormal cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_fmin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_maddf.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_maddf.c

Purpose: implements single-precision fused multiply-add/subtract variants for MIPS, computing `z +/- (x*y)` with one final rounding.

Important APIs/functions: internal `_sp_maddf(z, x, y, flags)` handles the operation. Wrappers `ieee754sp_maddf`, `msubf`, `madd`, `msub`, `nmadd`, and `nmsub` select sign transformations using `enum maddf_flags`.

Control flow: the function unpacks three operands, flushes denormals, clears exceptions, computes product sign and optional negations, applies NaN precedence z/x/y with sNaN first, handles invalid `inf*0`, infinity addition conflicts, zero product plus z rules, then multiplies to a 64-bit product, aligns z and product exponents, adds or subtracts, normalizes, and formats once.

State and persistence: updates FCR31 exception flags for invalid/inexact/overflow/underflow through helper calls.

Dependencies and integration: used by fused COP1 instruction emulation and relies on precise single formatter behavior.

Risks and test signals: fused rounding must not double-round. Test `inf*0`, opposite-sign infinities, signed-zero results, cancellation to zero under round-down, denormal z/product, all wrapper sign combinations, and halfway rounding cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_maddf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_mul.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_mul.c

Purpose: implements single-precision multiplication for the MIPS FPU emulator.

Important APIs/functions: `ieee754sp_mul(union ieee754sp x, union ieee754sp y)` handles all special classes, performs a 24x24-bit mantissa multiply using 16-bit partial products, and formats the rounded result.

Control flow: after class handling, finite operands are denormal-normalized, sign is XORed, exponent is summed, mantissas are shifted to the top of words, partial products are accumulated into high/low 32-bit words, sticky information is preserved from the low product, and the result is shifted into single GRS format.

State and persistence: exception flags are updated through invalid special cases and final formatting.

Dependencies and integration: used by MUL.S and fused helpers for non-fused multiply-like behavior. Depends on single internal header macros.

Risks and test signals: test `0*inf` invalid, qNaN/sNaN precedence, product normalization carry, low-word sticky propagation, overflow/underflow, signed zero, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_mul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_rint.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_rint.c

Purpose: rounds a single-precision value to an integral-valued single according to the current rounding mode.

Important APIs/functions: `ieee754sp_rint(union ieee754sp x)` handles NaNs/infinities/zeros, computes discarded residue, applies FCR31 rounding mode, sets inexact when needed, then returns `ieee754sp_flong(xm)` with the original sign restored.

Control flow: values with exponent already at least mantissa width are returned unchanged. Very small values round from zero with sticky residue. Other values shift out the fractional bits, detect round/sticky/odd, increment according to RN/RZ/RU/RD, and rebuild a single.

State and persistence: clears and sets current exception flags, especially inexact.

Dependencies and integration: used by RINT.S instruction emulation. It intentionally declares double-sized temporary locals via `COMPXDP` for wider mantissa storage.

Risks and test signals: test halfway ties-to-even, negative values under floor/ceil modes, tiny nonzero values, already-integral large values, sNaN invalid conversion, and preservation of signed zero/infinity/NaN payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_rint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_simple.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_simple.c

Purpose: implements single-precision absolute value and negation, respecting the MIPS `abs2008` mode bit.

Important APIs/functions: `ieee754sp_neg()` flips sign directly in IEEE-754-2008 mode, or emulates legacy semantics by subtracting from +0 with temporary round-down mode. `ieee754sp_abs()` clears sign directly in 2008 mode, or uses add/sub from +0 with temporary round-down mode in legacy mode.

Control flow: both functions branch on `ieee754_csr.abs2008`. Legacy paths save/restore `ieee754_csr.rm` and call add/sub helpers to preserve historical NaN and signed-zero behavior.

State and persistence: may temporarily modify rounding mode and may set exception flags indirectly through add/sub. Direct 2008 mode only mutates the returned union.

Dependencies and integration: used by ABS.S and NEG.S instruction emulation.

Risks and test signals: verify legacy versus 2008 mode differences for NaNs and signed zeros, preservation of rounding mode after calls, and exception behavior for signaling NaNs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_sqrt.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_sqrt.c

Purpose: implements single-precision square root in software.

Important APIs/functions: `ieee754sp_sqrt(union ieee754sp x)` handles special classes, normalizes the operand, computes the square root bit by bit, and rounds according to FCR31.

Control flow: sNaN raises invalid and quiets, qNaN/zero/+inf return unchanged, negative finite or -inf raises invalid and returns indefinite. Finite positive values are normalized by exponent parity, then a restoring square-root loop builds `q`. Remainder sets inexact, and RU/RN rounding adjusts `q` before rebuilding the raw exponent/mantissa.

State and persistence: mutates only current exception flags, notably invalid and inexact.

Dependencies and integration: called by SQRT.S emulation; uses `ieee754sp.h` constants but implements final packing directly rather than through `ieee754sp_format()`.

Risks and test signals: test negative inputs, +/-0, +inf, sNaN/qNaN, denormals, perfect squares, inexact roots under all rounding modes, and exponent parity transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_sqrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_sub.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_sub.c

Purpose: implements single-precision subtraction for the MIPS IEEE-754 emulator.

Important APIs/functions: `ieee754sp_sub(union ieee754sp x, union ieee754sp y)` mirrors `sp_add.c` but flips the sign of `y` after special-class handling and uses subtraction-specific infinity/zero rules.

Control flow: classification handles NaNs, `inf - inf`, finite minus infinity, infinity minus finite, zeros, and denormals. For finite operands it toggles `ys`, aligns exponents using sticky shifts, adds if signs match or subtracts magnitudes if signs differ, handles exact zero with round-down sign, normalizes, and formats.

State and persistence: updates current exception flags and uses rounding mode for exact-zero sign.

Dependencies and integration: used by SUB.S and by legacy abs/neg paths.

Risks and test signals: test `inf - inf` invalid, signed zero combinations, cancellation, exponent alignment sticky bits, denormal normalization, qNaN/sNaN precedence, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_sub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_tint.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_tint.c

Purpose: converts a single-precision value to a signed 32-bit integer according to current rounding mode.

Important APIs/functions: `ieee754sp_tint(union ieee754sp x)` returns integer values, `ieee754si_indef()` for NaNs, and `ieee754si_overflow(xs)` for infinities/out-of-range values.

Control flow: clears exceptions, classifies/flushes, rejects NaN/inf with invalid, handles zero, permits the exact `-2^31` corner, shifts mantissas left for large exponents, otherwise extracts residue/round/sticky/odd bits and applies RN/RZ/RU/RD rounding. Post-round overflow sets invalid.

State and persistence: mutates FCR31 exception flags for invalid and inexact.

Dependencies and integration: used by CVT.W.S, ROUND/TRUNC/CEIL/FLOOR paths with rounding mode set by higher-level emulator code.

Risks and test signals: test `-2^31`, just-overflowing positives/negatives, NaN/inf invalid, fractional ties-to-even, directed rounding, tiny values, and inexact flag behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_tint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_tlong.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_tlong.c

Purpose: converts a single-precision value to a signed 64-bit integer according to FCR31 rounding mode.

Important APIs/functions: `ieee754sp_tlong(union ieee754sp x)` returns `s64`, using `ieee754di_indef()` for NaNs and `ieee754di_overflow(xs)` for invalid infinities/out-of-range inputs.

Control flow: after classification and exception reset, NaN/inf cases set invalid, zero returns 0, the exact `-2^63` corner is accepted, large exponents shift the mantissa left, and smaller exponents compute residue/round/sticky/odd for rounding. If rounding creates a 64-bit overflow, invalid is raised.

State and persistence: updates only current exception flags.

Dependencies and integration: used by CVT.L.S and rounding-mode variants in the COP1 emulator.

Risks and test signals: test near `S64_MIN/S64_MAX`, tie values, negative directed rounding, inexact flag, NaN/inf invalid, and the use of double-width temporary macros with single inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_tlong.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/mm/Makefile

Purpose: Kbuild manifest for Linux/MIPS memory-management objects. It selects common MM, cache, TLB, page, ioremap, debug, and CPU-family-specific sources based on configuration.

Important build outputs: always builds `cache.o`, `context.o`, `extable.o`, `fault.o`, `init.o`, `mmap.o`, `page.o`, `page-funcs.o`, `pgtable.o`, `tlbex.o`, `tlbex-fault.o`, and `tlb-funcs.o`. It selects `uasm-micromips.o` or `uasm-mips.o`, includes `maccess.o` when EVA is disabled, and chooses 32-bit or 64-bit ioremap/pgtable variants.

Control flow: build-time conditionals wire CPU families: R3K, R4K, SB1, and Octeon cache/TLB/error-vector objects, plus optional secondary cache and debugfs modules.

State and persistence: no runtime state; it controls which code participates in the kernel image.

Dependencies and integration: central to all files in this subset. Mis-selection affects cache flush function pointer initialization, exception vectors, DMA coherency, and page table behavior.

Risks and test signals: verify configs combine exactly one appropriate cache/TLB family, 32/64-bit ioremap variants, highmem/hugetlb/DMA objects, and no missing object for selected CPU. Build matrix coverage is the primary test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/c-octeon.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/c-octeon.c

Purpose: Cavium Octeon-specific cache initialization, cache flush operations, and cache error notification handling.

Important APIs/functions: `octeon_cache_init()` probes caches, initializes global cache flush function pointers, builds page routines, and installs the Octeon cache error vector. `register_co_cache_error_notifier()` and `unregister_co_cache_error_notifier()` expose a raw notifier chain. Exception handlers `cache_parity_error_octeon_recoverable()` and `_non_recoverable()` report or panic.

Control flow: data-cache flushing is mostly no-op because Octeon flushes dcache on TLB changes. I-cache operations use local `synci` and SMP IPIs/calls for other cores. `probe_octeon()` derives cache metadata from CPU type/config registers and logs it.

State and persistence: global `cache_err_dcache[NR_CPUS]` stores dcache error state captured by the low-level vector; cache function pointers become global runtime MM behavior.

Dependencies and integration: depends on Octeon CPU helpers, SMP, `set_handler()`, `asm/octeon/octeon.h`, and common `cache.c` globals.

Risks and test signals: test on Octeon generations, SMP I-cache invalidation, notifier behavior, recoverable versus nested error paths, and unsupported CPU panic. Validate cache metadata logged during boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/c-octeon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/c-r3k.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/c-r3k.c

Purpose: R2000/R3000 cache probing and cache operation implementation.

Important APIs/functions: `r3k_cache_init()` probes cache sizes/line sizes, assigns global cache flush and DMA function pointers, logs cache geometry, and builds clear/copy page routines. `r3k_cache_size()` and `r3k_cache_lsize()` use isolated cache space. Flush helpers cover I-cache, D-cache, page flush, and DMA writeback/invalidate.

Control flow: probing manipulates CP0 status isolate-cache bits and KSEG0 memory to infer sizes. Range flushes fall back to whole-cache flush if the range is too large or not KSEG0. Page flush checks ASID and PTE validity before flushing physical KSEG0 aliases.

State and persistence: static cache geometry variables and global function pointers persist for the booted kernel. No dynamic allocation.

Dependencies and integration: initialized from `cpu_cache_init()` for R3K CPUs; relies on CP0 status, KSEG0 addressing, MMU context, PTE helpers, and page routine generation.

Risks and test signals: cache probing writes through KSEG0 and is hardware-sensitive. Test boot on R3K/Tx39xx variants, DMA sync paths, executable page flushes, ASID-zero short-circuiting, and `BUG()` path for unsupported kernel vmap flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/c-r3k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/c-r4k.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/c-r4k.c

Purpose: primary R4K-style cache subsystem for many MIPS CPUs. It probes cache geometry, selects optimized blast functions, implements cache/TLB coherency hooks, DMA cache operations, CPU errata workarounds, coherency attributes, and power-management restoration.

Important APIs/functions: `r4k_cache_init()` is the main entry. It calls `probe_pcache()`, `probe_vcache()`, `setup_scache()`, selects line-size-specific flush functions, sets global cache flush pointers, builds page routines, flushes caches, configures CCA, and installs cache error handlers. Public globals include exported `r4k_blast_dcache` and `r4k_blast_icache`.

Control flow: flush paths use `r4k_on_each_cpu()` to decide whether cache ops must run on foreign cores. Page/range flushes check ASID/MMID validity, executable mappings, dcache aliasing, icache fill behavior, and whether a temporary coherent mapping is required. DMA paths choose scache or dcache operations by cache inclusivity, size, and IPI constraints.

State and persistence: cache sizes and function pointers are static/global boot state. `_page_cachable_default`, `shm_align_mask`, and CPU option flags are configured once and restored after CPU PM exit.

Dependencies and integration: central implementation behind `cache.c` globals for R4K, SB1, and many MIPS32/MIPS64 CPUs; depends on CP0 config registers, SMP masks, board secondary cache ops, uasm page generation, and exception vectors.

Risks and test signals: high risk due to CPU-specific errata and aliases. Test boot on each CPU family, executable mmap/JIT coherency, DMA map/unmap, SMP flush scope, Loongson/BMIPS overrides, `cca=` early param, CPU suspend/resume, and cache error vector installation. The file contains duplicated CPU cases and workaround branches that deserve build-matrix coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/c-r4k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/cache.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/cache.c

Purpose: common MIPS cache abstraction layer. It declares global cache operation function pointers, implements generic user cacheflush syscall glue, folio/page D-cache maintenance, protection map setup, and selects CPU-family cache initialization.

Important APIs/functions: global pointers such as `flush_cache_all`, `flush_cache_page`, `flush_icache_range`, `flush_data_cache_page`, DMA cache hooks, and vmap flush hooks are assigned by CPU-specific files. `SYSCALL_DEFINE3(cacheflush)` flushes user I-cache ranges. `__flush_dcache_folio_pages()`, `__flush_anon_page()`, and `__update_cache()` handle aliasing and executable mappings. `cpu_cache_init()` dispatches to R3K/R4K/Octeon initializers.

Control flow: folio flushes defer by marking dcache dirty if unmapped, otherwise map pages locally and call selected cache ops. `__update_cache()` clears dirty folios when PTEs enter the TLB and flushes aliases or executable pages.

State and persistence: global function pointers and `_page_cachable_default` are boot-persistent. Folio dcache-dirty flags are runtime page state.

Dependencies and integration: bridges Linux MM core, syscall layer, MIPS CPU feature detection, and CPU-specific cache implementations.

Risks and test signals: uninitialized function pointers or alias mistakes can corrupt user/kernel memory. Test cacheflush syscall access checks, mmap executable writes, anonymous page aliasing, folio dirty clearing, CPU family boot selection, and protection map permission bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/cerr-sb1.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/cerr-sb1.c

Purpose: SiByte SB1 cache error decoder and fatal handler. It reads CP0 cache error state, bus watcher state, and cache tag/data contents to print diagnostics before stalling or panicking.

Important APIs/functions: `sb1_cache_error()` is the exception-level C handler. Helpers `breakout_errctl()`, `breakout_cerri()`, `breakout_cerrd()`, `extract_ic()`, `extract_dc()`, `dc_ecc()`, and parity helpers decode I-cache/D-cache tags, data parity, ECC, LRU, and physical/virtual addresses.

Control flow: the handler optionally freezes bus trace, reads CP0 error registers through inline assembly, decodes I-cache and D-cache conditions, validates indicated indexes against EPC/DPA, extracts cache contents when useful, checks bus watcher counters, then either loops forever under `CONFIG_SB1_CERR_STALL` or panics.

State and persistence: no persistent recovery state. It performs destructive reads of bus watcher registers and emits kernel logs.

Dependencies and integration: paired with `cex-sb1.S` low-level vector and selected by R4K cache error setup for SB1 CPUs. Uses SiByte SCD registers and MIPS CP0 cache tag/data registers.

Risks and test signals: must avoid making corruption worse in cache-error context. Test mostly by fault injection/emulation, build configs with/without bus watcher tracing, and validate printed decoding for known tag/ECC patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/cerr-sb1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/cex-gen.S -->
# sources/distributed-fs/ceph-client/arch/mips/mm/cex-gen.S

Purpose: generic MIPS cache error exception vector used when no CPU-specific vector is installed.

Important symbols: `except_vec2_generic` is copied to the cache error vector. It disables KSEG0 caching by clearing cache mode bits in CP0 Config and setting uncached mode, waits a few cycles, then jumps to `cache_parity_error`.

Control flow: runs in a highly constrained exception context with `noreorder`, `noat`, and minimal instructions. It does not save full register state; it uses `k0/k1` scratch registers and transfers to the secondary C/assembly error path.

State and persistence: mutates CP0 Config cache coherency mode. No memory state is allocated.

Dependencies and integration: installed by `r4k_cache_error_setup()` for non-SB1 CPUs. Depends on `cache_parity_error` existing elsewhere in the MIPS exception code.

Risks and test signals: vector size and instruction safety are critical because caches may be unreliable. Test by build/link checks, vector copy size validation, and cache error injection where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/cex-gen.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/cex-oct.S -->
# sources/distributed-fs/ceph-client/arch/mips/mm/cex-oct.S

Purpose: Octeon-specific cache error exception vector. It captures dcache error state before memory access and dispatches recoverable or nonrecoverable errors.

Important symbols: `except_vec2_octeon` is the compact vector; `handle_cache_err` saves full exception state and calls `cache_parity_error_octeon_recoverable()`.

Control flow: reads hardware core id, indexes `cache_err_dcache`, reads and clears CP0 Dcache CacheErr before normal memory activity, checks EXL for nested exception, jumps directly to nonrecoverable panic path if nested, otherwise saves registers and returns through `ret_from_exception` after the C handler.

State and persistence: writes captured dcache error to global `cache_err_dcache[core]` for later reporting.

Dependencies and integration: installed by `octeon_cache_error_setup()` in `c-octeon.c`; depends on Octeon CP0 selectors, stackframe macros, and C handlers.

Risks and test signals: ordering before memory access is essential due to errata. Test vector size, nested exception path, recoverable return, per-core storage, and correct clearing of CacheErr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/cex-oct.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/cex-sb1.S -->
# sources/distributed-fs/ceph-client/arch/mips/mm/cex-sb1.S

Purpose: SB1-specific cache error vector with limited recovery for certain I-cache errors and fatal dispatch for unrecoverable cases.

Important symbols: `except_vec2_sb1` is copied to the vector; `handle_vec2_sb1` switches KSEG0 uncached, obtains a usable stack if possible, and jumps to `sb1_cache_error()`.

Control flow: the vector saves `k0/k1` to low memory, checks `C0_ERRCTL` recoverable and cache-type bits, treats D-cache and unclear cases as unrecoverable, invalidates all ways for recoverable internal I-cache errors at the indicated index, restores scratch regs and `eret`s. Fatal path disables caching and jumps to the C decoder.

State and persistence: temporarily uses low memory locations `0x170/0x178`, mutates cache tags via `cache Index_Invalidate_I`, and changes CP0 Config on fatal path.

Dependencies and integration: installed by `r4k_cache_error_setup()` for SB1/SB1A and paired with `cerr-sb1.c`.

Risks and test signals: low-memory scratch use can race across CPUs; vector instruction budget is strict. Test recoverable icache injection, fatal dcache path, SMP reentry assumptions, and config options forcing fatal behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/cex-sb1.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/context.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/context.c

Purpose: manages MIPS ASID/MMID allocation and context switching for address spaces.

Important APIs/functions: `get_new_mmu_context()` and `check_mmu_context()` handle classic per-CPU ASIDs. `check_switch_mmu_context()` handles both ASID and MMID CPUs, writes EntryHi or MemoryMapID, invalidates TLBs on generation rollover, and sets up the TLB miss handler PGD. `mmid_init()` initializes the MMID allocator.

Control flow: ASID mode increments per-CPU ASID and flushes on wrap. MMID mode uses a global version, bitmap allocator, reserved per-CPU MMIDs, rollover flush mask, and a fast path using relaxed cmpxchg before taking `cpu_mmid_lock`.

State and persistence: global `mmid_version`, `num_mmids`, `mmid_map`, per-CPU `reserved_mmids`, and `tlb_flush_pending` persist for runtime context management. Per-mm CPU contexts are updated.

Dependencies and integration: called on context switch by MIPS MMU code and TLB refill setup. Depends on CPU ASID masks, ginvt support, SMP sibling masks, and `TLBMISS_HANDLER_SETUP_PGD`.

Risks and test signals: memory ordering and rollover are subtle. A duplicated `if (cpu_has_vtag_icache)` appears in the flush-pending path and is harmless but noisy. Test ASID wrap, MMID exhaustion, SMP sibling shared FTLB invalidation, CPU hotplug assumptions, and DEBUG_VM warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/dma-noncoherent.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/dma-noncoherent.c

Purpose: architecture DMA synchronization for non-coherent MIPS systems.

Important APIs/functions: `arch_dma_prep_coherent()`, `arch_dma_set_uncached()`, `arch_sync_dma_for_device()`, `arch_sync_dma_for_cpu()`, and `arch_setup_dma_ops()` integrate with Linux DMA mapping. Internal helpers choose writeback, invalidate, or writeback-invalidate by DMA direction.

Control flow: `dma_sync_phys()` walks potentially highmem physical ranges page by page, maps each page with `kmap_atomic()`, and performs cache maintenance for device or CPU ownership. CPU-side post-DMA flush is conditional on `cpu_needs_post_dma_flush()` for CPUs that may speculatively fill stale lines or have MAARs.

State and persistence: only sets `dev->dma_coherent` during setup. No persistent per-mapping state.

Dependencies and integration: depends on cache hooks from `cache.c`/CPU-specific cache files, DMA mapping core, highmem, CPU type detection, and MIPS uncached address bases.

Risks and test signals: wrong direction handling causes data corruption. Test highmem scatterlist segments, each DMA direction, zero/invalid directions hitting BUG, post-DMA invalidate on affected CPUs, and coherent allocation preparation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/dma-noncoherent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/extable.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/extable.c

Purpose: MIPS exception table fixup helper for recoverable kernel faults.

Important APIs/functions: `fixup_exception(struct pt_regs *regs)` searches exception tables using `exception_epc(regs)`. If a fixup is found, it rewrites `regs->cp0_epc` to `fixup->nextinsn` and returns true.

Control flow: simple lookup and branch. No locks or allocations are taken, making it suitable for page fault/oops recovery contexts.

State and persistence: mutates only the register frame EPC passed by the caller.

Dependencies and integration: used by `fault.c` in the kernel no-context page fault path. Depends on Linux extable infrastructure and MIPS branch-aware `exception_epc()`.

Risks and test signals: correctness depends on the EPC used for branch-delay exceptions. Test recoverable copy_to/from_user faults, branch-delay fault fixups, and no-fixup kernel oops behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/extable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/fault.c

Purpose: MIPS page fault handler. It classifies user/kernel faults, handles vmalloc/module faults, enforces access permissions, invokes Linux MM fault resolution, and reports signals or kernel oopses.

Important APIs/functions: `do_page_fault()` wraps exception context tracking around `__do_page_fault()`. `__do_page_fault()` implements the fault logic and is marked `NOKPROBE_SYMBOL`. Global `show_unhandled_signals` controls user signal logging.

Control flow: notifies kprobes, handles vmalloc fault synchronization, rejects faults without user context, sets FAULT_FLAG_USER/WRITE, locks and finds VMA, checks write/read/execute permissions including RIXI support, calls `handle_mm_fault()`, handles retry/completed/error bits, sends SIGSEGV/SIGBUS for user faults, or uses `fixup_exception()`/`die()` for kernel faults. 32-bit vmalloc faults copy kernel PGD/PMD entries into the current page table.

State and persistence: updates current thread fault metadata (`cp0_badvaddr`, `error_code`, `trap_nr`) and may modify per-mm page tables in vmalloc fault.

Dependencies and integration: central trap entry for MIPS memory faults; integrates with Linux mm, perf, kprobes, context tracking, exception tables, and signal delivery.

Risks and test signals: test user read/write/exec faults, RI/XI violations, kernel uaccess fixups, OOM/SIGBUS paths, vmalloc/module faults on 32-bit, branch-delay EPC handling, and ratelimited signal logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/highmem.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/highmem.c

Purpose: minimal MIPS highmem support globals and kmap TLB flush hook.

Important APIs/functions: defines `highstart_pfn` and `highend_pfn`. `kmap_flush_tlb(unsigned long addr)` calls `flush_tlb_one(addr)` and is exported.

Control flow: no complex flow; this file supplies architecture glue used by generic highmem/kmap code.

State and persistence: highmem PFN bounds are global boot/runtime state set by memory initialization elsewhere.

Dependencies and integration: depends on fixmap and TLB flush helpers. Built only under `CONFIG_HIGHMEM`.

Risks and test signals: highmem is incompatible with dcache aliasing in `init.c`, so test highmem boot only on supported CPUs. Validate kmap/kunmap TLB invalidation under local and SMP workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/highmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/hugetlbpage.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/hugetlbpage.c

Purpose: architecture helpers for locating and allocating hugepage PTE storage on MIPS.

Important APIs/functions: `huge_pte_alloc()` walks PGD/P4D/PUD levels and allocates a PMD entry cast as `pte_t *`. `huge_pte_offset()` walks existing levels and returns the PMD-backed huge PTE pointer if present.

Control flow: both functions are straightforward page-table walks. Allocation uses generic `p4d_alloc`, `pud_alloc`, and `pmd_alloc`.

State and persistence: mutates page tables only when allocating. No global state.

Dependencies and integration: used by Linux hugetlb core for MIPS hugepage mappings. Depends on folded/non-folded page-table abstractions and TLB flush semantics elsewhere.

Risks and test signals: casting PMD to PTE is architecture contract-sensitive. Test hugepage mmap, fault, unmap, fork, and page table teardown across folded page table configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/hugetlbpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/init.c

Purpose: MIPS memory initialization and architecture MM glue. It sets up zero pages, coherent kmap mappings, user page copy helpers, fixmap page tables, MAAR speculative regions, zone limits, highmem constraints, init memory freeing, percpu areas, root page tables, and execmem module ranges.

Important APIs/functions: `arch_setup_zero_pages()`, `kmap_coherent()`, `kmap_noncoherent()`, `kunmap_coherent()`, `copy_user_highpage()`, `copy_to_user_page()`, `copy_from_user_page()`, `fixrange_init()`, `maar_init()`, `arch_zone_limits_init()`, `arch_mm_preinit()`, `free_initmem()`, and `setup_per_cpu_areas()`.

Control flow: boot code allocates zero pages with optional page coloring, creates temporary wired TLB mappings for coherent aliases, handles dcache alias-safe user copies, allocates fixmap PTE pages under highmem, records/configures MAAR ranges for RAM, trims unsupported highmem, frees init sections, and initializes percpu offsets.

State and persistence: exports `empty_zero_page`, `zero_page_mask`, page table roots/invalid tables, `pgd_current`, per-CPU offsets, and recorded MAAR config for secondary CPUs.

Dependencies and integration: tightly integrated with memblock, TLB wired entries, cache aliases, highmem, kcore, execmem, pgalloc, and CPU feature bits.

Risks and test signals: high risk around aliases and wired TLB slots. Test boot memory maps, highmem enable/disable, user page copy on aliasing CPUs, MAAR logging, secondary CPU MAAR replay, initmem poisoning/freeing, and module exec ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/ioremap.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/ioremap.c

Purpose: 32-bit MIPS `ioremap_prot()`/`iounmap()` implementation for mapping physical I/O resources into kernel virtual address space.

Important APIs/functions: `ioremap_prot(phys_addr_t phys_addr, unsigned long size, pgprot_t prot)` supports platform overrides, big-phys fixups, low-512MB KSEG1 uncached shortcut, RAM remap rejection, vmalloc area allocation, and `ioremap_page_range()`. `iounmap()` delegates to platform unmap or vunmaps non-KSEG1 mappings.

Control flow: validates size/wraparound, uses KSEG1 for low uncached ranges, rejects early calls before slab, walks system RAM to avoid remapping allocatable RAM, aligns physical/virtual range, allocates `VM_IOREMAP`, maps pages with global/present/read/write cache flags, and returns offset-adjusted pointer.

State and persistence: creates/removes vmalloc mappings. No file-global state.

Dependencies and integration: depends on platform hooks, `fixup_bigphys_addr`, vmalloc, resource/RAM walking, cache attributes, and TLB/cache flush infrastructure.

Risks and test signals: test wraparound, zero size, RAM rejection, KSEG1 fast path, platform override paths, unaligned resources, and iounmap of platform/KSEG1/vmalloc mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/ioremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/ioremap64.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/ioremap64.c

Purpose: simplified 64-bit MIPS `ioremap_prot()`/`iounmap()` implementation using direct uncached or I/O base address translation unless a platform hook handles the mapping.

Important APIs/functions: `ioremap_prot(phys_addr_t offset, unsigned long size, pgprot_t prot)` chooses `IO_BASE` for uncached mappings and `UNCAC_BASE` otherwise, after trying `plat_ioremap()`. `iounmap()` only calls `plat_iounmap()`. Both are exported.

Control flow: no range validation or vmalloc page table mapping is performed here; the returned pointer is base plus physical offset when platform code does not override.

State and persistence: no global state and no generic mapping allocation.

Dependencies and integration: selected under `CONFIG_64BIT`; depends on MIPS direct map layout, platform ioremap hooks, and cache attribute bits.

Risks and test signals: correctness depends on 64-bit address-space layout and platform hook coverage. Test uncached versus cached attributes, high physical offsets, platform override/unmap behavior, and drivers expecting `iounmap()` to be a no-op for direct mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/ioremap64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/maccess.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/maccess.c

Purpose: architecture policy hook for kernel nofault reads.

Important APIs/functions: `copy_from_kernel_nofault_allowed(const void *unsafe_src, size_t size)` returns true only when the source address has the top address bit set, treating that as kernel space.

Control flow: simple address check, no memory access.

State and persistence: no state.

Dependencies and integration: built when EVA is disabled. Used by generic nofault memory access helpers to reject user-like source addresses.

Risks and test signals: address-space split assumptions must match MIPS kernel layout. Test kernel text/data/vmalloc addresses accepted and user addresses rejected on 32-bit and 64-bit non-EVA configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/maccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/mmap.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/mmap.c

Purpose: MIPS-specific mmap address selection and virtual-address validation, including cache-color alignment for shared mappings on aliasing caches.

Important APIs/functions: `arch_get_unmapped_area()`, `arch_get_unmapped_area_topdown()`, internal `arch_get_unmapped_area_common()`, exported `shm_align_mask`, and `__virt_addr_valid()`.

Control flow: common mmap search rejects oversized mappings, validates `MAP_FIXED` against `TASK_SIZE` and cache-color constraints, aligns requested addresses for file/shared mappings, probes VMA gaps, then uses `vm_unmapped_area()` bottom-up or top-down with fallback. `__virt_addr_valid()` checks kernel virtual range and PFN validity.

State and persistence: `shm_align_mask` is global and updated by cache initialization based on aliasing constraints.

Dependencies and integration: used by Linux mmap core and cache alias handling. Depends on `current->mm`, VMA gap helpers, randomization/topdown policy from generic mm, and MIPS address translation.

Risks and test signals: test shared mappings with pgoff color alignment, MAP_FIXED rejection, topdown fallback, huge lengths, ASLR interactions, and `virt_addr_valid` around PAGE_OFFSET/MAP_BASE boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/page-funcs.S -->
# sources/distributed-fs/ceph-client/arch/mips/mm/page-funcs.S

Purpose: reserves executable code slots for runtime-generated `clear_page` and `copy_page` implementations.

Important symbols: exports `__clear_page_start`, `__clear_page_end`, `__copy_page_start`, and `__copy_page_end`. Defines either `clear_page`/`copy_page` directly or CPU fallback names `clear_page_cpu`/`copy_page_cpu` under `CONFIG_SIBYTE_DMA_PAGEOPS`.

Control flow: initial functions are dummy infinite jumps followed by fixed `.space` areas. `page.c` overwrites these slots at boot using the uasm generator, then callers execute the generated code.

State and persistence: the reserved text area is patched once at boot and then acts as kernel text. Function symbols are exported.

Dependencies and integration: paired with `build_clear_page()` and `build_copy_page()` in `page.c`; size comments define maximum generated sequence budgets.

Risks and test signals: generated code must fit the reserved spaces. Test boot-time `BUG_ON(buf > end)` never triggers, symbols export correctly, and generated clear/copy work under all selected CPU/cache configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/page-funcs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/page.c -->
# sources/distributed-fs/ceph-client/arch/mips/mm/page.c

Purpose: generates optimized MIPS `clear_page` and `copy_page` routines at boot using the micro-assembler, with optional SiByte DMA page operations.

Important APIs/functions: `build_clear_page()` and `build_copy_page()` synthesize instruction streams into the slots from `page-funcs.S`. Helper `set_prefetch_parameters()` selects word sizes, cache line sizes, prefetch modes, and loop sizes by CPU type. Optional `clear_page()` and `copy_page()` use SB1 DMA descriptors when `CONFIG_SIBYTE_DMA_PAGEOPS` is enabled.

Control flow: the generator runs once per routine via atomics, initializes labels/relocs, validates prefetch assumptions, emits prefetch/cache/store/load loops with CPU errata workarounds, resolves relocations, checks code size, and logs debug words. The DMA variants fall back to CPU routines unless both addresses are KSEG0, then program per-CPU descriptors and busy-wait for interrupt completion.

State and persistence: generated code persists in kernel text slots. Static prefetch and loop parameters are boot-time state. SB1 DMA uses cacheline-aligned per-channel descriptors.

Dependencies and integration: called by CPU cache init (`r3k`, `r4k`, `octeon`) and used by core page allocator/copy paths. Depends on uasm, CPU feature bits, cache ops, and optional SiByte registers.

Risks and test signals: generated code size, R6 prefetch offsets, DADDIU workaround, cache-line assumptions, and DMA busy-wait are sensitive. Test clear/copy correctness, boot on CPU variants, KSEG0 and non-KSEG0 paths, and debug code dump when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/page.c -->
