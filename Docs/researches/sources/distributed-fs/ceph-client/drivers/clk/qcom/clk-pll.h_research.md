# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-pll.h

## Purpose
Defines the legacy Qualcomm PLL descriptor contract for `clk-pll.c` and SoC clock controller tables.

## Important APIs, Types, And Functions
`struct pll_freq_tbl` maps requested frequency to L/M/N/internal config bits. `struct clk_pll` stores L/M/N/config/mode/status registers, status bit, optional post-divider field, frequency table, and embedded `clk_regmap`. `struct pll_config` stores boot-time VCO, pre/post divider, M/N enable, and output masks. The header declares PLL ops and SR configuration helpers.

## Control Flow
SoC code fills `clk_pll` and optional `pll_config`, configures the hardware during probe, and registers the clock with one of the exported ops. Runtime behavior is implemented by `clk-pll.c`.

## State And Persistence
The header describes static software descriptors plus frequency/config tables. Hardware persistence is represented by the register addresses; no mutable software cache is exposed.

## Dependencies And Integration Points
Includes CCF and `clk-regmap.h`. It integrates with older Qualcomm CC drivers and common qcom PLL FSM setup helpers.

## Risks And Edge Cases
The frequency table is ceil-style and must be ordered. Register widths are fixed in the implementation, so descriptors must match hardware generation. Vote ops require parent-child topology to be correct.

## Test Signals
Build coverage, frequency-table ordering checks, and runtime PLL enable/rate tests validate the header.
