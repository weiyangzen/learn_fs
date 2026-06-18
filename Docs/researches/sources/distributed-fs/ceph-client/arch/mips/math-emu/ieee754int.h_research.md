# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754int.h

Purpose: private common header for IEEE-754 emulator internals. It provides class-pair indexing, fused multiply-add flag bits, exception flag helpers, and unpack/flush macros for single and double values.

Important APIs/macros: `CLPAIR()` indexes switch cases over two value classes. `MADDF_NEGATE_PRODUCT` and `MADDF_NEGATE_ADDITION` parameterize fused operations. `ieee754_clearcx()`, `ieee754_setcx()`, and `ieee754_setandtestcx()` mutate current and sticky exception flags. `COMP*`, `EXPLODE*`, and `FLUSH*` macros declare locals, classify raw inputs, normalize exponent/mantissa fields, and optionally flush denormals to zero when `nod` is set.

Control flow: arithmetic functions use a consistent pattern: `COMP`, `EXPLODE`, `ieee754_clearcx`, `FLUSH`, class-pair special handling, arithmetic on normalized mantissas, and precision-specific formatting.

State and persistence: exception mutations are per-current-task via `ieee754_csr`; no global state is allocated.

Dependencies and integration: included by both precision-specific internal headers. It bridges raw union fields from `ieee754.h` with arithmetic implementations.

Risks and test signals: macro side effects are dense and caller-local variable names are fixed. Test classifying sNaN/qNaN under `nan2008`, denormal flushing under `nod`, exception sticky accumulation, and every class-pair switch table for missing combinations.
