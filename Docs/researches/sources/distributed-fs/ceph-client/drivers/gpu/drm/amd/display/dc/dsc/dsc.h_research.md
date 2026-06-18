# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dsc.h

## Purpose

`dsc.h` is the Display Core internal DSC interface header. It defines external configuration input, OPTC output configuration, hardware readback structs, encoder capability structures, and the generation-specific DSC function table.

## Important APIs, Types, And Functions

Important types include `struct dsc_config`, `struct dsc_optc_config`, `struct dcn_dsc_state`, `struct dcn_dsc_reg_state`, `union dsc_enc_slice_caps`, `struct dsc_enc_caps`, and `struct dsc_funcs`. The function table covers capability query, state readback, validation, hardware config, PPS packing, enable/disable/disconnect, disconnect wait, single-encoder cap query, and FGCg control.

## Control Flow

The header has no implementation flow. It defines the polymorphic contract consumed by shared policy code and HWSS wrappers: policy computes `dc_dsc_cfg`, generation backends validate/program hardware, and timing generator/OPTC code consumes `dsc_optc_config`.

## State, Dependencies, Risks, And Test Signals

`dsc_config` is transient input. `dcn_dsc_state` and `dcn_dsc_reg_state` are readback snapshots. Persistent effects occur only when a backend function table writes hardware registers. The file intentionally includes only `dc_dsc.h`, `dc_hw_types.h`, and `dc_types.h` to avoid EDID utility breakage. Risks include include expansion, function-table contract drift, and fixed-point unit confusion such as bytes-per-pixel u3.28. Build all DSC generations and exercise HWSS DSC wrappers.
