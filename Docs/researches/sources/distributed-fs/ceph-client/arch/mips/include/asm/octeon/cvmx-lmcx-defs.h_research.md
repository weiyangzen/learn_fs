# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-lmcx-defs.h

## Purpose
`cvmx-lmcx-defs.h` is a generated OCTEON SDK register-definition header for the LMC memory-controller blocks. It gives C code the physical CSR address formulas and 64-bit union overlays needed to initialize, tune, monitor, and diagnose DDR/DDR2/DDR3 memory-controller state on multiple OCTEON chip families. The file does not implement a driver by itself; it is the ABI surface consumed by platform, boot, EDAC, memory-training, and low-level MIPS/OCTEON code that reads or writes LMC CSRs through the broader CVMX CSR access layer.

## Important APIs, Types, And Functions
The address macros are the main API. They map controller `block_id` values, and occasionally rank or DIMM offsets, into IO-segment CSR addresses via `CVMX_ADD_IO_SEG(...)`. The exported register families cover BIST (`CVMX_LMCX_BIST_CTL`, `CVMX_LMCX_BIST_RESULT`), memory setup (`MEM_CFG0`, `MEM_CFG1`, `CONFIG`, `CONTROL`, `CTL`, `CTL1`, `DDR2_CTL`, `RESET_CTL`), PLL/DLL/clocking (`PLL_CTL`, `PLL_STATUS`, `PLL_BWCTL`, `DDR_PLL_CTL`, `DLL_CTL*`, `DCLK_*`), ECC and fault capture (`ECC_SYND`, `FADR`, `SCRAMBLED_FADR`, `INT`, `INT_EN`, `NXM`), training and leveling (`READ_LEVEL_*`, `RLEVEL_*`, `WLEVEL_*`, `CHAR_*`, `TRO_*`), DIMM and mode-register programming (`DIMMX_PARAMS`, `DIMM_CTL`, `MODEREG_PARAMS*`), performance counters (`IFB_CNT*`, `OPS_CNT*`, `DCLK_CNT*`), and on-die termination or compensation (`COMP_CTL*`, `RODT_*`, `WODT_*`).

Most registers are defined as `union cvmx_lmcx_*` with a raw `uint64_t u64` member plus a named bitfield struct `s`. Many unions also expose chip-specific overlays such as `cn30xx`, `cn38xx`, `cn50xx`, `cn52xx`, `cn58xx`, `cn61xx`, `cn63xx`, `cn63xxp1`, `cn66xx`, `cn68xx`, and `cn56xxp1`. These overlays preserve register names while reflecting different reserved ranges, field widths, or fields that exist only on particular silicon revisions.

Four static inline address helpers, `CVMX_LMCX_DUAL_MEMCFG()`, `CVMX_LMCX_ECC_SYND()`, `CVMX_LMCX_FADR()`, and `CVMX_LMCX_NXM()`, dispatch on `cvmx_get_octeon_family()`. They adjust the controller stride for CN68XX versus older families, using `0x1000000` for CN68XX and usually `0x60000000` otherwise. This family switch is the only real executable logic in the header.

## Control Flow
There is no runtime control flow beyond the four inline address helpers. Normal users compute a CSR address with a `CVMX_LMCX_*` macro or helper, read the 64-bit value through the CVMX CSR access functions, interpret or modify fields through the matching `union cvmx_lmcx_*`, and write it back if needed. Initialization code would typically program PLL/DLL and delay values, set memory geometry and timing registers, assert or clear reset/init bits, configure mode-register and ODT behavior, then poll status or interrupt fields such as `init_status`, `pll_status`, `sec_err`, `ded_err`, and training `status` fields.

The union bitfield layout uses `#ifdef __BIG_ENDIAN_BITFIELD` in every meaningful struct. This produces reversed declaration order for little-endian builds while keeping field names stable for callers. The generated layout assumes a compiler and ABI where these 64-bit bitfields match hardware CSR bit numbering under the selected endianness mode.

## State And Persistence
The file itself stores no software state. Its definitions describe persistent hardware state in memory-controller CSRs: memory geometry, rank masks, ECC enable and syndrome state, no-existent-memory write reporting, DDR timing, PLL/DLL configuration, read/write leveling results, ODT masks, counter values, and interrupt enable/pending bits. Writes through these definitions can affect live DRAM availability, refresh, ECC reporting, training margins, and reset behavior until the next hardware reset or reprogramming. Some registers are status or counter-like, while others are configuration latches that must be programmed in a silicon-prescribed sequence by external code.

## Dependencies And Integration Points
The header depends on OCTEON SDK infrastructure for `uint64_t`, `CVMX_ADD_IO_SEG`, `cvmx_get_octeon_family()`, `OCTEON_*` family constants, and `OCTEON_FAMILY_MASK`. It integrates with the MIPS/OCTEON CSR read/write helpers and any kernel subsystems that configure DRAM, handle ECC interrupts, expose memory-controller performance counters, or decode memory errors. Because the source is under `arch/mips/include/asm/octeon`, its consumers are architecture-specific and normally compiled only for Cavium/Marvell OCTEON platforms.

The LMC header also pairs with other generated CSR headers in the same directory. For example, interrupt controller code must route LMC interrupt causes exposed by `CVMX_LMCX_INT` and `CVMX_LMCX_INT_EN`; boot and board code must combine this file's memory geometry/timing with fuse, reset, and clock information from MIO and other OCTEON blocks.

## Risks
The highest risk is ABI drift: a wrong address stride, masked index width, chip-family case, bitfield width, or endian declaration order can write the wrong CSR bit or even the wrong controller instance. That is especially dangerous for `CONFIG`, `CONTROL`, `RESET_CTL`, PLL/DLL, and timing registers because incorrect writes can corrupt memory operation rather than fail cleanly.

The `block_id` macros mask different numbers of bits, usually `& 1` for older two-controller formulas and `& 3` for newer four-controller formulas. Passing an out-of-range block silently wraps; caller-side validation is required when the number of LMC instances differs by chip. The static inline helpers also fall back to the older `0x60000000` stride for unknown families, so adding silicon without updating this file can produce plausible but wrong addresses.

Bitfields over memory-mapped registers are compiler-layout-sensitive. The raw `u64` member is safer for masks in highly portable code, while field access is convenient but must be validated on both endian configurations. Several registers contain chip-revision-specific reserved fields; writing a generic overlay to a revision that reserves those bits may set undefined hardware state.

## Test Signals
Useful validation starts with compile coverage for both big-endian and little-endian MIPS/OCTEON configurations, ensuring all unions and helpers compile without bitfield-size overflow. Address tests can assert known CSR addresses for representative families, especially the CN68XX stride cases in `CVMX_LMCX_DUAL_MEMCFG`, `ECC_SYND`, `FADR`, and `NXM`, plus masked offset behavior for rank/DIMM macros.

Hardware or simulator tests should read stable status registers such as BIST result, counters, and PLL status; verify ECC interrupt mask/cause wiring; and exercise read/write leveling status fields during memory bring-up. Regression tests for generated headers should diff register names, address constants, family overlays, and reserved-bit widths against the vendor CSR database or a known-good SDK version.
