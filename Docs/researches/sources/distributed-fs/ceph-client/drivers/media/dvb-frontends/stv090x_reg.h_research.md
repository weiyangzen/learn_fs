# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x_reg.h

## Purpose
`stv090x_reg.h` is the symbolic register map and bitfield catalog for STV0900/STV0903 demodulators. It contains no executable code; its purpose is to let `stv090x.c` express hardware access by names instead of numeric addresses and to feed the private `STV090x_GETFIELD`/`STV090x_SETFIELD` macros with consistent offsets and widths.

## Important Register Families
The file begins with global chip identification, DAC/output, interrupt, I2C repeater, GPIO, clock, PLL, standby, ADC, tuner-test, and FSK/DiSEqC support registers. It then defines per-path DiSEqC TX/RX registers under `Px_DISTX*` and `Px_DISRX*`.

The main per-demodulator block is parameterized by `STV090x_Px_*(__x)` macros, with P1 and P2 aliases generated from path number. Addressing generally uses a 0x200 separation between paths for demod/FEC/TS blocks and smaller offsets for shared low-level blocks. Important families include AGC/IQ/power, demod mode/status, carrier frequency and search bounds, timing recovery and symbol-rate registers, equalizer/FFE, noise estimators, DVB-S2 MODCOD and PLS root registers, Viterbi configuration/status, packet delineator and MIS filtering, LDPC/BCH counters, TS FIFO/output registers, and error/PER/BER counters.

The final global families define LDPC iteration and LLR gain tuning, `GENCFG` for single/dual LDPC demod mode, `RCCFGH`, `TSGENERAL`/`TSGENERAL1X`, reset controls, and test DiSEqC receive selection.

## Control Flow And Integration
The implementation includes this header before the public/private headers. Init tables in `stv090x.c` use register constants directly. Field macros from `stv090x_priv.h` combine names such as `STV090x_OFFST_Px_LOCK_DEFINITIF_FIELD` and `STV090x_WIDTH_Px_LOCK_DEFINITIF_FIELD` to read lock, status, MODCOD, rolloff, transport stream, and DiSEqC bits. Demod-specific macros such as `STV090x_Px_DSTATUS(__x)` allow a single implementation path to select P1 or P2 at compile time through `STV090x_READ_DEMOD(state, DSTATUS)`.

## State And Persistence Behavior
The header has no runtime state. It documents the hardware state that the driver persists in registers: PLL and clocks, standby, ADC power/range, demod search modes, symbol/carrier offsets, MODCOD masks, PLS/MIS filtering, packet/error counters, TS FIFO mode/speed, and DiSEqC FIFO state. Because these names map directly to hardware registers, any value written by the implementation remains in the chip until overwritten, reset, or powered down.

## Dependencies
The register map depends on the STV090x hardware data sheet conventions and on the private bitfield macros using a strict `STV090x_OFFST_*`/`STV090x_WIDTH_*` naming scheme. It is tightly coupled to `stv090x.c`; nearly every helper there references one or more constants from this header.

## Risks And Edge Cases
Register-map correctness is critical. A wrong address or bit offset can misprogram hardware without compiler errors if the symbol name still exists. Some comments mark fields as `check`, indicating areas that may have been uncertain when authored. Several macros use arithmetic on path or index arguments; callers must pass valid path numbers and index ranges. P1/P2 address formulas are not uniform across all families, so adding new register names by copying a nearby macro can be risky.

## Test Signals
The strongest signals are hardware bring-up and tuning success across both STV0900 paths and the STV0903 single path. Specific checks should cover chip ID reads, I2C repeater enable/disable, PLL/mclk programming, per-path demod lock bits, Viterbi and packet delineator lock bits, C/N and RF metric reads, MODCOD mask programming, MIS/PLS filtering, TS FIFO configuration and line lock, DiSEqC TX/RX FIFO operation, sleep/wakeup clock bits, and error-counter reset/readback behavior. Static review should also verify every `STV090x_*_FIELD` used by `stv090x.c` has matching offset and width definitions.
