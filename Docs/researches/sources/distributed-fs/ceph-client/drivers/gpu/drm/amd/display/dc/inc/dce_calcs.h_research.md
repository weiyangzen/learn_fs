# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/dce_calcs.h

## Purpose

`dce_calcs.h` defines the legacy DCE bandwidth and watermark calculation interface. It models DCE IP constants, VBIOS/board memory characteristics, per-mode scratch variables, and output watermarks/clocks using `bw_fixed`.

## Important APIs, Types, And Functions

Key types include `enum bw_calcs_version`, `enum bw_defines`, `struct bw_calcs_dceip`, `struct bw_calcs_vbios`, and `struct bw_calcs_data`. Public functions are `bw_calcs_init(...)` to initialize static DCE/VBIOS inputs and `bw_calcs(...)` to validate a pipe set and fill `struct dce_bw_output`.

## Control Flow

Initialization populates static IP and board parameters from ASIC ID and firmware-derived values. Runtime calculation consumes a DC context, DCE IP data, VBIOS data, current pipe array, and pipe count. It computes scaler, tiling, compression, cursor, urgent latency, stutter, DRAM/NB p-state, request bandwidth, DISPCLK/SCLK/YCLK requirements, and watermarks, returning whether the configuration is supported.

## State And Persistence Behavior

The header defines large temporary calculation state but does not persist data itself. Callers keep initialized DCE/VBIOS inputs and store final values in `dce_bw_output` within `dc_state.bw_ctx`. There is no disk persistence and no direct register programming.

## Dependencies And Integration Points

It depends on `bw_fixed.h` and forward-declared DC/pipe/output types. `core_types.h` embeds DCE output in `union bw_output`. Resource validation and HWSS bandwidth programming consume the resulting clocks, watermarks, and state-change enable flags.

## Risks And Edge Cases

The formulas use many fixed-point divisions and array indexes up to `maximum_number_of_surfaces`. Incorrect pipe counts or unsupported surface combinations can overflow arrays or produce invalid watermarks. Legacy enum constants include negative `notok/na` values mixed with positive symbolic values. Fixed-point precision and rounding determine borderline validation outcomes.

## Test Signals

Golden tests should cover legacy ASIC versions, multi-display sync, underlay formats, FBC/LPT, writeback, rotations, tiling modes, scatter-gather, cursor sizes, compression rates, and p-state/stutter enablement. Integration signals include `dce_bw_output` watermarks, required clocks, validation failure status, and underflow behavior.
