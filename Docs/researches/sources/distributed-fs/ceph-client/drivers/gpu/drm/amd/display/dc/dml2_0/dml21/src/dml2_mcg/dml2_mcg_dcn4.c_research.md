# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn4.c

## Purpose
Builds the DCN4 min-clock table used by core mode support and DPMM latency/bandwidth mapping. It derives DRAM bandwidth rows and associated minimum FCLK/DCFCLK requirements from SoC clock tables, derate factors, and fabric/return bus widths.

## Important APIs, types, and functions
- `mcg_dcn4_build_min_clock_table()` is the exported wrapper around `build_min_clock_table()`.
- `uclk_to_dram_bw_kbps()` converts UCLK and DRAM geometry into pre-derate DRAM bandwidth.
- `round_up_to_quantized_values()` maps computed clocks to the next provided clock-table value.
- `build_min_clk_table_fine_grained()` handles fine-grained or unequal DCFCLK/FCLK/UCLK table shapes by computing balanced bandwidth rows, shifting FCLK requirements upward, clamping to minimums and maximums, deriving DCFCLK from FCLK and bus ratios, pruning invalid rows, and pruning duplicate rows.
- `build_min_clk_table_coarse_grained()` copies aligned UCLK/FCLK/DCFCLK table rows directly.
- `build_min_clock_table()` validates inputs, fills fixed clocks, max clocks, spread-spectrum adjusted max clocks, chooses fine/coarse construction, and returns success.

## Control flow and integration
The MCG factory selects this builder for DCN40, DCN4 stage2, and DCN4 stage2 auto-DRR/SVP projects. The generated `dml2_mcg_min_clock_table` feeds core mode support and DPMM's latency minimum selection.

## State and persistence behavior
All persistent output is written to caller-provided `min_table`: fixed clocks, max clocks, max spread-spectrum clocks, and `dram_bw_table`. No static mutable state is used.

## Dependencies
Includes `dml2_mcg_dcn4.h` and SoC parameter types. It depends on SoC bounding-box clock tables, DRAM config, QoS derate percentages, fabric data-return width, return bus width, downspread percent, and max FCLK constraints.

## Risks and edge cases
The function rejects missing SoC/min-table pointers, DCFCLK/FCLK tables with fewer than two values, and UCLK tables larger than `DML_MCG_MAX_CLK_TABLE_SIZE`. It assumes max clock tables for DISPCLK/DPPCLK have at least one entry. Fine-grained duplicate pruning shifts entries using `entries[j + 1]`, so table bounds and row counts must remain valid. `round_up_to_quantized_values()` returns 0 if no value is larger than the input, which can later be pruned or misinterpreted if not expected.

## Test signals
Tests should cover coarse aligned tables, fine-grained two-entry DCFCLK/FCLK tables, unequal table counts, max-FCLK clamping, duplicate pruning, invalid over-max pruning, downspread max-SS calculations, and invalid input/table-size failures.
