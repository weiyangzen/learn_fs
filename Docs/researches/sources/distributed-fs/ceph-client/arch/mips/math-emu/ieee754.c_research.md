# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754.c

Purpose: defines the shared single-precision and double-precision special value tables used by the MIPS IEEE-754 emulator. These constants supply canonical zeros, ones, tens, infinities, indefinite NaNs, maxima, minima, and large powers used by the conversion and arithmetic helpers.

Important APIs/types: exports `__ieee754dp_spcvals[]` and `__ieee754sp_spcvals[]` as constant arrays of `union ieee754dp` and `union ieee754sp`. Macros `xPCNST`, `DPCNST`, and `SPCNST` build bitfield initializers with the proper exponent bias.

Control flow: there is no runtime control flow beyond static initialization. The file is included in the math emulator object set so helpers such as `ieee754sp_zero()`, `ieee754sp_inf()`, `ieee754dp_indef()`, and similar macros can index stable constants declared in the headers.

State and persistence: all data is read-only kernel text/data state. No per-task state is mutated here; exception and rounding state remains in `ieee754_csr` elsewhere.

Dependencies and integration: depends on `ieee754.h`, `ieee754sp.h`, and `ieee754dp.h` for the union layouts and exponent constants. It integrates with every arithmetic/conversion implementation that returns canonical special values.

Risks and test signals: bitfield ordering is architecture-sensitive and relies on `__BITFIELD_FIELD` definitions. Regression tests should compare raw bit patterns for all special values in legacy and NaN-2008 modes, especially indefinite NaN encodings and signed zero preservation.
