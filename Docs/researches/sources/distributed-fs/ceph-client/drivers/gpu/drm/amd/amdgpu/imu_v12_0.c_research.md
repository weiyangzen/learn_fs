# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_0.c

## Purpose
`imu_v12_0.c` implements GFX12.0 IMU firmware loading, IMU startup, and RLC RAM programming. It keeps the v11 firmware flow but adds GFX12 transfer-RAM addressing, GRBM index remapping, and MMHUB-derived GFXHUB aperture settings.

## Important APIs, Types, And Functions
The exported object is `gfx_v12_0_imu_funcs`. Key functions are `imu_v12_0_init_microcode`, `imu_v12_0_load_microcode`, `imu_v12_0_wait_for_reset_status`, `imu_v12_0_setup`, `imu_v12_0_start`, `program_imu_rlc_ram_old`, `imu_v12_0_grbm_gfx_index_remap`, `imu_v12_init_gfxhub_settings`, `program_imu_rlc_ram`, and `imu_v12_0_program_rlc_ram`. `TRANSFER_RAM_MASK` is `0x001c0000`.

## Control Flow
Init requests normal or kicker GFX12.0 IMU firmware, stores the firmware version, and for PSP loading records IMU I/D entries plus aligned firmware sizes. Direct load writes firmware IRAM and DRAM arrays to IMU RAM registers. Setup opens C2P message access and, in debug mode, sets C2PMSG and scratch bits. Start releases IMU reset and optionally invokes APU DPM power-up, then polls reset status. RLC programming selects IP 12.0.0/12.0.1, currently falls back to `program_imu_rlc_ram_old` because `r` remains `-EINVAL`, writes a terminator, and marks RAM valid. The newer `program_imu_rlc_ram` path supports triplet arrays, MMHUB value substitution, and GRBM index remapping.

## State And Persistence
State includes firmware pointers/version, PSP firmware table accounting, IMU C2P/scratch/core registers, and IMU RLC RAM. Aperture values may be sourced live from MMHUB registers rather than static table data.

## Dependencies And Integration Points
Dependencies include firmware APIs, amdgpu ucode helpers, `amdgpu_is_kicker_fw`, PSP firmware loading, DPM APU hooks, GC 12.0 register headers, MMHUB 4.1 register headers, and `amdgpu_imu_funcs` users in GFX bring-up.

## Risks
The new triplet programming path is effectively disabled by `r = -EINVAL`, so intended data-driven programming may be incomplete or future-facing. `BUG()` handles unsupported versions. MMHUB/GFX register mapping must remain exact. GRBM remapping is bit-sensitive and can mis-target per-instance writes. Firmware load failure blocks initialization.

## Test Signals
Signals include firmware availability for `gc_12_0_0_imu.bin`, `gc_12_0_1_imu.bin`, and kicker firmware; direct and PSP load paths; reset polling; RLC RAM valid bit; MMHUB aperture consistency; and boot/display/compute workloads on 12.0.0 and 12.0.1 devices.
