# sources/distributed-fs/ceph-client/arch/mips/math-emu/sp_rint.c

Purpose: rounds a single-precision value to an integral-valued single according to the current rounding mode.

Important APIs/functions: `ieee754sp_rint(union ieee754sp x)` handles NaNs/infinities/zeros, computes discarded residue, applies FCR31 rounding mode, sets inexact when needed, then returns `ieee754sp_flong(xm)` with the original sign restored.

Control flow: values with exponent already at least mantissa width are returned unchanged. Very small values round from zero with sticky residue. Other values shift out the fractional bits, detect round/sticky/odd, increment according to RN/RZ/RU/RD, and rebuild a single.

State and persistence: clears and sets current exception flags, especially inexact.

Dependencies and integration: used by RINT.S instruction emulation. It intentionally declares double-sized temporary locals via `COMPXDP` for wider mantissa storage.

Risks and test signals: test halfway ties-to-even, negative values under floor/ceil modes, tiny nonzero values, already-integral large values, sNaN invalid conversion, and preservation of signed zero/infinity/NaN payloads.
