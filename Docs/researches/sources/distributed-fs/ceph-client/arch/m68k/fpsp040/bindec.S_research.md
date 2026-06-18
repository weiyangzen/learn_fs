# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/bindec.S

Purpose: FPSP routine converting an extended-precision binary floating-point input to packed BCD format for packed move-out operations.

Important APIs and labels: exports `bindec` and `sc_mul`; uses `fpsp.h` stack offsets, power-of-ten tables `PTENRN/PTENRM/PTENRP`, helper `binstr`, and integer conversion helper `sintdo`. Constants include `LOG2`, `LOG2UP1`, single-precision `FONE/FTWO/FTEN/F4933`, and rounding table `RBDTBL`.

Control flow and state: `bindec` saves D2-D7/A2 and FP0-FP2, normalizes denormal/unnormal inputs, computes an approximate decimal exponent `ILOG`, calculates display length from the k-factor, builds `10^ISCALE` in a directed rounding mode, scales the absolute input, forces round-to-zero for controlled inexact handling, uses `sintdo` to round to integer digits, adjusts if digit count is off, calls `binstr` for mantissa and exponent BCD digits, writes sign bits, clears transient FPSR inexact state, and restores registers.

Dependencies and integration: called by FPSP packed decimal store paths, shares local stack frame state through A6, and reports exceptions through `USER_FPSR`.

Risks and test signals: decimal conversion is highly rounding-sensitive, especially denormals, k-factor bounds, and exact/inexact propagation. Test packed decimal output for normal, denormal, zero, large/small exponent, all rounding modes, and positive/negative k-factors.
