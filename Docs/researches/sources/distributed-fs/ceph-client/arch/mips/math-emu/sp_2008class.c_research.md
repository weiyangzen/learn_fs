# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_2008class.c

Purpose: implements the MIPS/IEEE-754-2008 single-precision `CLASS.S` operation, returning a 10-bit mask describing the class and sign of a floating-point operand.

Important APIs/functions: `ieee754sp_2008class(union ieee754sp x)` expands `COMPXSP` and `EXPLODEXSP` to classify the raw value, then maps `SNAN`, `QNAN`, signed infinities, normals, denormals, and zeros to the architecture-defined bit positions.

Control flow: single switch on `xc`. Signed non-NaN classes shift a base mask by either 0 for negative classes or 4 for positive classes. Unknown classes log with `pr_err()` and return 0.

State and persistence: no exception flags are cleared or set here, and no persistent state is changed. It is a pure classification helper apart from an unexpected-class log.

Dependencies and integration: included by the FPU emulator for `CLASS.S` instruction handling; depends on `ieee754sp.h` classification macros and `ieee754_csr.nan2008` behavior via `EXPLODEXSP`.

Risks and test signals: verify exact bit mask mapping, especially signed zero and signed denormal values. Include sNaN/qNaN bit patterns in both NaN modes to confirm classification matches the active FCR31 mode.
