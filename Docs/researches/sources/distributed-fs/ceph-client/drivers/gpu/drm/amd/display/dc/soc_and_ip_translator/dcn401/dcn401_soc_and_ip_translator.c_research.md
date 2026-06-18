<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn401/dcn401_soc_and_ip_translator.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn401/dcn401_soc_and_ip_translator.c

## Purpose

`dcn401_soc_and_ip_translator.c` supplies DCN4.01 DML2 SoC bounding-box and IP-capability data. It starts from static bounding-box tables, then overlays runtime SMU clock tables, VBIOS latency values, and software policy overrides.

## Important APIs, Types, And Functions

- `dcn401_get_soc_bb(soc_bb, dc, config)`: exported full bounding-box construction.
- `dcn401_update_soc_bb_with_values_from_clk_mgr`, `dcn401_update_soc_bb_with_values_from_vbios`, and `dcn401_update_soc_bb_with_values_from_software_policy`: reusable update layers.
- `dcn401_convert_dc_clock_table_to_soc_bb_clock_table(...)`: maps `clk_bw_params` to `dml2_soc_state_table`, optionally clipped by DC-mode clock limits.
- `dcn401_construct_soc_and_ip_translator(...)`: installs function table callbacks.
- Static `dcn401_get_ip_caps(ip_caps)` returns `dml2_dcn401_max_ip_caps`.

## Control Flow

`dcn401_get_soc_bb` copies default DCN401 SoC and QoS tables, then applies updates in priority order: clock manager values, VBIOS values, and software policy overrides. Clock-table conversion independently handles DCFCLK, FCLK, UCLK, DISPCLK, DPPCLK, DTBCLK, and SOCCLK, filling unused entries with zero and truncating values when `config->use_clock_dc_limits` is active.

## State And Persistence Behavior

The file writes only caller-provided `struct dml2_soc_bb` and `struct dml2_ip_capabilities` outputs. It reads runtime state from `dc->clk_mgr`, `dc->caps`, `dc->res_pool`, `dc->ctx->dc_bios`, and `dc->bb_overrides`. No state is retained between calls.

## Dependencies And Integration Points

It depends on DCN4 bounding-box headers, DML2 SoC/IP structures, `clk_mgr`, BIOS `bb_info`, and the generic `soc_and_ip_translator` function-table interface. DCN42 reuses the VBIOS and software-policy update helpers.

## Risks And Edge Cases

- Clock entries are assumed sorted ascending for DC-limit clipping logic.
- Null `bw_params` is handled, but `dc->clk_mgr` and its function table are assumed valid.
- DC-mode clipping can reduce `num_clk_values`; consumers must tolerate shortened tables.
- Unit conversions mix MHz to kHz and 100 ns/ns to microseconds; mistakes directly affect DML validation.
- Software overrides intentionally supersede VBIOS values, so bad overrides can destabilize watermark and p-state decisions.

## Test Signals

Tests should compare generated SoC tables against known SMU/VBIOS inputs, including DC-limit clipping boundaries and zero/empty clock tables. Runtime signals include DML validation changes, watermark/p-state regressions, and display mode acceptance differences when BIOS or debug overrides change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/soc_and_ip_translator/dcn401/dcn401_soc_and_ip_translator.c -->
