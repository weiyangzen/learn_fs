# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_imu.h

## Purpose
`amdgpu_imu.h` defines the interface for the AMDGPU IMU block used by some graphics IPs for microcode loading, RLC RAM programming, reset status, compute partition switching, and MCM address lookup setup.

## Important APIs, types, and functions
It defines `enum imu_work_mode` with `DEBUG_MODE` and `MISSION_MODE`, `struct amdgpu_imu_funcs`, `struct imu_rlc_ram_golden`, the `IMU_RLC_RAM_GOLDEN_VALUE()` initializer macro, and `struct amdgpu_imu`.

## Control flow
There is no executable control flow. ASIC-specific code installs `amdgpu_imu_funcs`, then graphics initialization calls through those hooks to initialize/load microcode, set up/start IMU, program RLC RAM, wait for reset status, switch compute partitions, and initialize MCM address lookup tables.

## State and persistence behavior
`struct amdgpu_imu` stores a function-table pointer and runtime mode. Golden RLC RAM entries are static data used to program hardware registers. No persistent state is defined.

## Dependencies and integration points
The header depends on AMDGPU device and register-index conventions such as `*_HWIP` and `*_BASE_IDX`. It integrates with GFX initialization, RLC setup, partition switching, and reset flow for IP generations that use IMU.

## Risks and edge cases
Function pointers must be implemented for the target IP before use. Golden register macros depend on token-pasting register names matching SOC header definitions. Incorrect work mode or RLC RAM data can prevent graphics bring-up or partition switching.

## Test signals
Microcode init/load, IMU start, RLC RAM programming verification, compute partition switch tests, MCM address LUT init, and reset-status timeout tests validate this header contract.
