# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn10/dcn10_fpu.c

## Purpose

`dcn10_fpu.c` centralizes DCN1.0 code that touches floating-point state. AMD display mode calculations use floating-point values in kernel code, so this file follows the DC FPU isolation pattern: public functions must be called while FPU access is already enabled by the caller, and they assert that condition with `dc_assert_fp_enabled()`.

Functionally, this file provides DCN1.0 DML IP and SoC bounding-box defaults and a construction-time adjustment function for Raven/DCN1 variants.

## Important APIs, Types, And Data

Exported data:

- `dcn1_0_ip`: DML `_vcs_dpi_ip_params_st` defaults for DCN1.0, including buffer sizes, chunk sizes, line-buffer limits, DPP/writeback counts, scaler throughput, scaler ratios/taps, timing delays, underscan, minimum vblank, and DCFCLK cstate latency.
- `dcn1_0_soc`: DML `_vcs_dpi_soc_bounding_box_st` defaults for DCN1.0, including SR/urgent/writeback latencies, DRAM bandwidth policy, request size, DRAM timing, channel/bank configuration, page size, clock-change latency, and return bus width.

Exported function:

- `dcn10_resource_construct_fp(struct dc *dc)`: applies construction-time floating-point DCN1 resource adjustments to `dc->dcn_soc`, `dc->dcn_ip`, `dc->dml`, and debug flags.

## Control Flow

`dcn10_resource_construct_fp` performs a small sequence of ASIC-specific adjustments:

1. It asserts FPU access is enabled.
2. For `DCN_VERSION_1_01`, it reduces the DPP count to three in both DML IP and DCN IP data, and changes DRAM clock-change latency to 23 microseconds.
3. For `ASICREV_IS_RV1_F0`, it lowers urgent latency, disables DMCU through `dc->debug.disable_dmcu`, and adjusts maximum fabric/DRAM bandwidth.
4. It derives `dc->dcn_soc->number_of_channels` from `asic_id.vram_width / ddr4_dram_width`, asserts the result is less than three, and works around old SBIOS data that reports zero channels by forcing two.
5. For single-channel memory, it rewrites fabric/DRAM bandwidth values to single-channel limits, with a separate RV1 F0 maximum.

There are no loops beyond the simple conditional flow and no calls into the generated DML equations.

## State And Persistence Behavior

The function mutates in-memory driver state during resource construction:

- `dc->dml.ip.max_num_dpp`
- `dc->dcn_soc->dram_clock_change_latency`
- `dc->dcn_ip->max_num_dpp`
- `dc->dcn_soc->urgent_latency`
- `dc->debug.disable_dmcu`
- `dc->dcn_soc->fabric_and_dram_bandwidth_*`
- `dc->dcn_soc->number_of_channels`

The file has no disk persistence and allocates no memory. The global `dcn1_0_ip` and `dcn1_0_soc` structures are mutable globals by type, though this file itself only writes through the `dc` instance passed into the function.

## Dependencies And Integration Points

Direct dependencies:

- `dcn10/dcn10_resource.h` for DCN1 resource definitions, ASIC revision helpers, and constants such as `ddr4_dram_width`.
- `resource.h` and `struct dc` state.
- `amdgpu_dm/dc_fpu.h` for `dc_assert_fp_enabled`.

Integration points:

- Called from DCN1 resource construction code after the caller has entered the DC FPU critical section.
- The DML and legacy bandwidth paths later consume the adjusted `dc->dml`, `dc->dcn_soc`, and `dc->dcn_ip` values during mode validation and watermark calculation.
- Debug behavior is affected through `dc->debug.disable_dmcu`.

## Risks And Edge Cases

- The function assumes the caller enabled FPU access. Calling it outside the FPU-protected region triggers a warning/assert path and risks illegal kernel FPU use.
- `number_of_channels` depends on firmware-reported `vram_width`; bad firmware is partly handled for zero channels but not for other unexpected values except an assert for values >= 3.
- The DCN_VERSION_1_01 branch changes both DML and legacy DCN IP DPP counts; missing one would desynchronize DML validation from resource programming.
- The RV1 F0 and single-channel bandwidth tables are hard-coded. Incorrect ASIC revision detection directly changes mode validation capacity.
- The file-level FPU isolation comment says FPU users should be static/noinline, but the visible public function itself uses floating-point assignments. The actual protection relies on caller-side FPU enable plus `dc_assert_fp_enabled()`.

## Test Signals

Useful validation signals include:

- Construction tests for DCN 1.0, DCN 1.01, RV1 F0, single-channel, dual-channel, and zero-channel firmware cases.
- Assertions/warnings when invoking without DC FPU protection in debug kernels.
- Mode validation comparisons before and after construction to confirm DPP count, latency, and bandwidth values reach DML and legacy calculators.
- Display bring-up on Raven variants that rely on DMCU disable or adjusted urgent latency.
