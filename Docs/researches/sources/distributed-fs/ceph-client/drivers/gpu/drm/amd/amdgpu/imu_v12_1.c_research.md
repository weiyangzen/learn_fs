# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_1.c

## Purpose
`imu_v12_1.c` implements the newer GFX12.1 IMU firmware path, with emphasis on per-XCC firmware loading and compute partition switching rather than local start/setup/RLC RAM programming.

## Important APIs, Types, And Functions
The exported object is `gfx_v12_1_imu_funcs`. Important functions are `imu_v12_1_init_microcode`, `imu_v12_1_xcc_load_microcode`, `imu_v12_1_load_microcode`, `imu_v12_1_switch_compute_partition`, and `imu_v12_1_init_mcm_addr_lut`. It declares firmware `amdgpu/gc_12_1_0_imu.bin`.

## Control Flow
Init decodes the GC IP version into a short prefix, requests the required IMU firmware, stores the firmware version, and for PSP loading records IMU I/D firmware entries and aligned sizes. `load_microcode` rejects missing firmware, computes `NUM_XCC(adev->gfx.xcc_mask)`, and uploads the same firmware IRAM/DRAM image to each XCC instance via `GET_INST(GC, xcc_id)`. Compute partition switching calls `psp_spatial_partition` when PSP functions are present, using total XCC count divided by XCCs per XCP, then records `adev->gfx.num_xcc_per_xcp`.

## State And Persistence
State includes `adev->gfx.imu_fw`, `adev->gfx.imu_fw_version`, PSP firmware entries, per-XCC IMU RAM contents, and `adev->gfx.num_xcc_per_xcp`. `init_mcm_addr_lut` is a placeholder and persists nothing.

## Dependencies And Integration Points
Dependencies include Linux firmware loading, amdgpu ucode helpers, GC 12.1 register headers, MMHUB 4.2 headers, XCC macros, PSP spatial partitioning, and the `amdgpu_imu_funcs` interface. The file includes DPM headers but does not currently start or power up IMU directly.

## Risks
`ucode_prefix[15]` is smaller than older IMU files and depends on decoded names fitting. Per-XCC loops assume XCC IDs are dense from zero to `NUM_XCC(mask)-1`; sparse masks would need scrutiny. Partition switching divides by `num_xccs_per_xcp` without a local zero guard. TODO comments indicate incomplete ASP/interface and MCM LUT handling.

## Test Signals
Firmware request success, per-XCC IMU RAM upload traces, multi-XCC hardware boot, PSP spatial partition return codes, invalid partition parameter tests, and compute partition mode transitions are key signals.
