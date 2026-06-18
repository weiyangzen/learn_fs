# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mp1_v13_0.c

## Purpose

`amdgpu_ras_mp1_v13_0.c` adapts rascore MP1 operations to AMDGPU SMU firmware messages for MP1 v13.0-era ASICs. It queries valid MCA bank counts, dumps bank registers, sends firmware EEPROM commands, and reports firmware RAS EEPROM feature enablement.

## Important APIs, Types, And Functions

The exported table is `amdgpu_ras_mp1_sys_func_v13_0`. Static functions are `mp1_v13_0_get_valid_bank_count`, `mp1_v13_0_dump_valid_bank`, `mp1_v13_0_eeprom_send_msg`, and `mp1_v13_0_get_ras_enabled_mask`. `pmfw_eeprom_msgs` maps rascore EEPROM command enums to `SMU_MSG_*` opcodes.

## Control Flow, State, And Persistence

All hardware operations try to take `adev->reset_domain->sem` with `down_read_trylock`; failure returns `-RAS_CORE_GPU_IN_MODE1_RESET`. Bank count chooses CE or non-CE query messages. Bank dump computes doubleword offsets for each 64-bit ACA register and issues two SMU reads. EEPROM sends forward firmware EEPROM commands through `amdgpu_smu_ras_send_msg`. Feature query sets `RAS_CORE_FW_FEATURE_BIT__RAS_EEPROM` if `SMU_FEATURE_HROM_EN_BIT` is enabled.

## Dependencies And Integration Points

It depends on `amdgpu_smu.h`, reset-domain locking, SMU RAS message helpers, and rascore MP1 callbacks. It is installed by `amdgpu_ras_mgr_init_mp1_config` for MP1 IP versions 13.0.6, 13.0.12, and 13.0.14.

## Risks And Test Signals

Risks include message enum drift, invalid EEPROM command indexes, reset lock starvation, partial 64-bit register reads, and feature-mask false negatives during reset. Test signals include bank count/dump tests under normal and reset conditions, firmware EEPROM command coverage, HROM feature detection, and ACA update paths that consume dumped MCA registers.
