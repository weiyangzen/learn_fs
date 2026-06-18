# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c

## Purpose
`imu_v11_0.c` implements GFX11 IMU firmware handling and IMU-programmed RLC RAM setup. It requests the correct IMU firmware, optionally stages it for PSP loading, directly uploads IRAM/DRAM when needed, starts the IMU, and writes generation-specific golden register sequences into IMU RLC RAM.

## Important APIs, Types, And Functions
The exported API is `gfx_v11_0_imu_funcs`. Key functions are `imu_v11_0_init_microcode`, `imu_v11_0_load_microcode`, `imu_v11_0_wait_for_reset_status`, `imu_v11_0_setup`, `imu_v11_0_start`, `program_imu_rlc_ram`, and `imu_v11_0_program_rlc_ram`. Static tables `imu_rlc_ram_golden_11` and `imu_rlc_ram_golden_11_0_2` hold register/data/address-mask triples via `IMU_RLC_RAM_GOLDEN_VALUE`.

## Control Flow
Init decodes the GC IP version into a firmware prefix, chooses kicker or normal firmware, requests it as required, parses `imu_firmware_header_v1_0`, and either records IMU I/D firmware entries for PSP loading or stores the firmware version for direct loading. Direct load writes IRAM then DRAM data from the firmware blob into `GFX_IMU_*_RAM_*` registers. Setup opens C2P message access and sets debug/scratch bits. Start clears `GFX_IMU_CORE_CTRL.CRESET`, asks DPM to power up GFX by IMU on APUs, then polls reset status until low five bits are set. RLC RAM programming selects tables by GC IP version, delegates 11.0.3 to `imu_v11_0_3_program_rlc_ram`, terminates the RAM list, and marks RAM valid.

## State And Persistence
State is held in `adev->gfx.imu_fw`, `adev->gfx.imu_fw_version`, `adev->firmware.ucode[]`, `adev->firmware.fw_size`, `adev->gfx.imu.mode`, and hardware IMU/RLC RAM registers. Dynamic values patch AGP and VRAM location entries from `adev->gmc`.

## Dependencies And Integration Points
Dependencies include Linux firmware loading, `amdgpu_ucode_*`, `amdgpu_is_kicker_fw`, PSP firmware loading structures, GC 11.0 register headers, DPM GFX power-up, and the companion 11.0.3 table file. It integrates with the `amdgpu_imu_funcs` call sites in the GFX bring-up path.

## Risks
Firmware prefix or kicker selection errors fail probe. PSP size accounting must match firmware sections. Polling uses `adev->usec_timeout`; too short a timeout causes false failures. Unsupported GC versions hit `BUG()`. Golden table values are hardware-sensitive and can corrupt early graphics setup if stale. Firmware version assignment is commented out for one path, so direct load relies on version being set only outside PSP cases.

## Test Signals
Signals include firmware request success for all listed GC 11.x IMU binaries, direct-load register traces, PSP load-table sizing, IMU reset completion, APU DPM interaction, RLC RAM valid bit, and boot tests across 11.0.0, 11.0.2, and 11.0.3 ASICs.
