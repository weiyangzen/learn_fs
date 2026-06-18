# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_cmp.c

Purpose: implements single-precision comparisons for the emulator, returning whether the requested comparison predicate is true.

Important APIs/functions: `ieee754sp_cmp(union ieee754sp x, union ieee754sp y, int cmp, int sig)` accepts a bitmask of `IEEE754_CLT`, `CEQ`, `CGT`, and `CUN`, plus a signaling flag for unordered comparisons.

Control flow: values are classified and denormals optionally flushed, then current exceptions are cleared. If either operand is NaN, invalid operation is raised for signaling comparisons or sNaN operands, and unordered result is selected from `cmp`. Otherwise raw signed values are transformed into an order-preserving integer domain and compared.

State and persistence: mutates only the current exception flags in `ieee754_csr`.

Dependencies and integration: used by COP1 compare instruction emulation. Depends on `SP_SIGN_BIT` and internal classification macros.

Risks and test signals: validate signed zero equality, negative ordering transform, all unordered predicates, sNaN invalid exceptions, qNaN with nonsignaling compare, and denormal flush behavior.
