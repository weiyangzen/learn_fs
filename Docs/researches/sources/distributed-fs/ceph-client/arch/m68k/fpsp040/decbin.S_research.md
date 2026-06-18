# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/decbin.S

Purpose: FPSP routine converting normalized packed BCD input in the FPSP frame to an exact or correctly rounded extended-precision value in FP0.

Important APIs and labels: exports `decbin`, `calc_e`, `calc_m`, `ap_st_z`, `ap_st_n`, `pwrten`, and `norm`. Uses `PTENRN/PTENRM/PTENRP`, rounding table `RTABLE`, and `fpsp.h` offsets such as `ETEMP`, `FP_SCR1`, and `USER_FPSR`.

Control flow and state: `decbin` copies packed BCD to scratch, converts exponent digits to binary with sign and a -16 adjustment, accumulates mantissa digits in FP0 by multiplying by 10 and adding each digit, applies mantissa sign, strips/appends zeros for large adjusted exponents to reduce power-of-ten error, computes `10^abs(exp)` under a directed rounding mode selected from user FPCR/sign bits, multiplies or divides FP0 by that factor, converts final INEX2 to INEX1/AIINEX in `USER_FPSR`, restores D2-D5, and returns.

Dependencies and integration: used by packed decimal input handling in the FPSP operand decode path. It operates entirely through the FPSP local frame and FPU registers.

Risks and test signals: decimal-to-binary conversion depends on exact digit extraction, exponent sign bits, and rounding-table choice. Test packed BCD inputs for zero/nonzero mantissas, positive/negative exponents, signs, large exponent reduction, all rounding modes, and inexact exception enablement.
