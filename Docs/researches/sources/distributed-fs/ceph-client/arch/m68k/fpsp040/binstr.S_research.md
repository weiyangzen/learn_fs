# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/binstr.S

Purpose: FPSP helper converting a 64-bit binary fraction in D2:D3 into packed BCD digits in memory.

Important API: exports `binstr`. Inputs are LEN in D0, fraction in D2:D3, and destination pointer in A0. It saves/restores D0-D7 and writes BCD bytes to the output string.

Control flow and state: the loop multiplies the 64-bit fraction by 10 using separate multiply-by-8 and multiply-by-2 shifts, adds the two products with carry, extracts the digit shifted out at the high end, packs two BCD digits per byte, and repeats for LEN digits. NOPs after arithmetic preserve historical 68040 errata timing/workaround behavior. There is no persistent state; all state is register and destination-memory local.

Dependencies and integration: called by `bindec.S` for mantissa and exponent decimal strings. It includes `fpsp.h` but mainly uses registers and memory pointer conventions.

Risks and test signals: off-by-one in LEN or byte packing corrupts packed decimal results. Carry propagation across D2:D3 and BCD nibble order are critical. Test with known binary fractions producing fixed digit strings, odd/even LEN values, maximum 17-digit paths, and integration through packed decimal store instructions.
