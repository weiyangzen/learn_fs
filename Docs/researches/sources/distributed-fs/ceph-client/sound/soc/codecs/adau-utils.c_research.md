# sources/distributed-fs/ceph-client/sound/soc/codecs/adau-utils.c

## Purpose
Shared helper module for ADAU-family codec drivers. It currently exports a single PLL configuration calculator used by drivers such as ADAU1372 and ADAU1373.

## Important APIs, Types, and Functions
`adau_calc_pll_cfg(freq_in, freq_out, regs[5])` computes five PLL register bytes. It handles disabled output by zeroing all fields, integer ratios by setting `r` only, and fractional ratios by reducing the input clock with a divider, calculating fractional `n/m` with `gcd()`, and setting the fractional-mode bit.

## Control Flow
The function validates output frequency and ratio constraints after computing `r`, `n`, `m`, and `div`. It returns `-EINVAL` for unsupported divisors, feedback ratios outside 2..8, or 16-bit fraction fields. On success it writes bytes `[m_hi, m_lo, n_hi, n_lo, control]`.

## State and Persistence
No persistent state. The caller owns the output buffer and writes the resulting bytes to hardware.

## Dependencies and Integration Points
Depends on Linux `gcd`, `DIV_ROUND_UP`, and module export infrastructure. `EXPORT_SYMBOL_GPL(adau_calc_pll_cfg)` makes it available to other GPL codec modules.

## Risks
The function assumes `freq_in` is nonzero when `freq_out` is nonzero; callers must validate or provide a real input clock. Integer division choices directly affect PLL lock behavior, so boundary frequencies need hardware validation.

## Test Signals
Unit-style tests for integer ratio, fractional ratio, disabled output, invalid high/low ratio, excessive divider, and zero input protection in callers.
