# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn42.c

## Purpose
Builds a DCN42-specific min-clock table. Unlike the DCN4 builder, this version uses FCLK table rows as the primary row count and computes DRAM bandwidth from UCLK plus WCK ratio, matching the newer memory-clock representation.

## Important APIs, types, and functions
- `mcg_dcn42_build_min_clock_table()` is the exported wrapper.
- `uclk_to_dram_bw_kbps()` computes bandwidth as `uclk * channel_count * channel_width_bytes * wck_ratio * 2`.
- `build_min_clk_table_coarse_grained()` iterates over FCLK rows, uses matching UCLK/WCK rows where available, and repeats the last UCLK bandwidth/min-UCLK for extra FCLK rows.
- `build_min_clock_table()` validates pointers and UCLK table size, fills fixed clocks, max clocks, spread-spectrum max clocks, DCFCLK/FCLK max, and invokes coarse table construction.

## Control flow and integration
The MCG factory routes `dml2_project_dcn42` to this builder. Its output is consumed by core support and DPMM the same way as the DCN4 min-clock table, but the `dram_bw_table.entries[].min_uclk_khz` field is explicitly populated for alternate DRAM bandwidth conversion.

## State and persistence behavior
All state is written into caller-provided `dml2_mcg_min_clock_table`. No static mutable state is used.

## Dependencies
Includes the DCN42 MCG header and SoC parameter types. It depends on SoC clock tables for UCLK, WCK ratio, DCFCLK, FCLK, DISPCLK, DPPCLK, DSC/DTB/PHY clocks, and fixed ref clocks.

## Risks and edge cases
The implementation assumes FCLK, DCFCLK, DISPCLK, and DPPCLK tables have entries; only optional DSC/DTB/PHY max clocks guard zero entries. If FCLK has more entries than UCLK, the last UCLK entry is reused, so table ordering and WCK ratio alignment are critical. It validates UCLK count against `DML_MCG_MAX_CLK_TABLE_SIZE` but not FCLK count explicitly.

## Test signals
Tests should include equal UCLK/FCLK row counts, extra FCLK rows, WCK ratio changes, optional zero-entry DSC/DTB/PHY clocks, downspread max-SS calculations, and invalid null/oversized UCLK inputs.
