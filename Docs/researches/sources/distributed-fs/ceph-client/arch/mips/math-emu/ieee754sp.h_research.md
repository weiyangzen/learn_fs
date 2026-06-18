# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754sp.h

Purpose: internal single-precision helper header for the IEEE-754 emulator. It defines single exponent/mantissa constants, accessors, sticky shifts, denormal normalization macros, and builder/formatter declarations.

Important APIs/macros: `SP_EBIAS`, `SP_EMIN`, `SP_EMAX`, `SP_FBITS`, `SP_HIDDEN_BIT`, `SP_SIGN_BIT`, `SPSIGN`, `SPBEXP`, and `SPMANT` describe raw format. `XSPSRS64`, `XSPSRS`, and `XSPSRS1` preserve sticky information during shifts. `SPDNORMX/Y/Z` normalize denormals. `buildsp()` constructs a raw single result.

Control flow: callers expand macros to normalize inputs, perform arithmetic in extended precision, and call `ieee754sp_format()` for final rounding and exception handling.

State and persistence: no independent state. Some macros mutate caller locals and rely on `ieee754_csr` indirectly through included internals.

Dependencies and integration: includes `ieee754int.h`; used by every `sp_*` source file and by debug/conversion utilities.

Risks and test signals: macro shift expressions can be sensitive near word-width limits. Tests should stress denormal normalization, sticky bits after long shifts, exact powers of two, signed zero building, and raw bit encodings for boundary values.
