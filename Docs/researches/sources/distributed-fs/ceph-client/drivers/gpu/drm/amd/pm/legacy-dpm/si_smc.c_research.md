# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_smc.c

## Purpose
`si_smc.c` implements low-level Southern Islands SMC access helpers for the legacy DPM path. It controls SMC reset/clock state, loads SMC firmware from `adev->pm.fw`, copies arbitrary byte ranges into SMC SRAM, sends firmware messages, and reads/writes SMC SRAM dwords through indirect MMIO registers.

## Important APIs And Control Flow
`si_set_smc_sram_address()` validates 4-byte alignment and address limit, programs `mmSMC_IND_INDEX_0`, and disables auto-increment. `amdgpu_si_copy_bytes_to_smc()` serializes access with `adev->reg.smc.lock`, writes big-endian SMC words, and handles trailing bytes by read-modify-write. `amdgpu_si_load_smc_ucode()` parses `smc_firmware_header_v1_0`, records firmware version, enables auto-increment, and streams aligned firmware words. `amdgpu_si_send_msg_to_smc()` verifies the SMC is running, writes `mmSMC_MESSAGE_0`, polls `mmSMC_RESP_0`, and uses longer timeouts for slow power-state messages.

## State, Persistence, And Dependencies
Persistent effects are entirely hardware and device state: SMC SRAM contents, reset and clock bits, firmware version in `adev->pm.fw_version`, and message/response registers. The code depends on `amdgpu.h`, `sid.h`, `ppsmc.h`, `amdgpu_ucode.h`, `sislands_smc.h`, and generated SMU/GFX register definitions. All SRAM access is protected by the SMC spinlock; reset and clock helpers perform direct register writes without additional policy checks.

## Risks And Test Signals
Risks include wrong SMC SRAM limits, endian conversion mistakes, trailing-byte corruption, timeouts hidden by unconditional `PPSMC_Result_OK` in `amdgpu_si_wait_for_smc_inactive()`, and firmware header size/address mismatch. Test signals are clean firmware load logs, no timeout warnings from `amdgpu_si_send_msg_to_smc()`, successful DPM enable, and stable suspend/resume and power-state switching on SI hardware.
