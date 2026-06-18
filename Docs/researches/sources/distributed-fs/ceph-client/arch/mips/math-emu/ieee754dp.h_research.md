# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754dp.h

Purpose: internal double-precision helper header for the IEEE-754 emulator. It defines double exponent/mantissa constants, raw field accessors, sticky shifts, denormal normalization macros, and final builder helpers.

Important APIs/macros: `DP_EBIAS`, `DP_EMIN`, `DP_EMAX`, `DP_FBITS`, `DP_HIDDEN_BIT`, `DPSIGN`, `DPBEXP`, and `DPMANT` describe the format. `XDPSRS`, `XDPSRS1`, and `XDPSRSX1` implement sticky right shifts used by arithmetic. `DPDNORMX/Y/Z` normalize denormal mantissas. `builddp()` constructs raw double values, and declarations expose `ieee754dp_nanxcpt()` and `ieee754dp_format()`.

Control flow: this file is macro-heavy and inlines logic into callers. Arithmetic files unpack values, normalize denormals, operate on extended mantissas, then call `ieee754dp_format()`.

State and persistence: no standalone state. Macros may read or update caller locals and rely on `ieee754_csr` through included internal helpers.

Dependencies and integration: includes `ieee754int.h`, which provides class and exception helpers. All double-precision math files depend on these definitions.

Risks and test signals: sticky shift macros must avoid undefined behavior for large shifts and preserve nonzero low bits. Validate boundary mantissas, denormal normalization loops, 64-bit shifts, and construction of min/max/infinity/NaN constants.
