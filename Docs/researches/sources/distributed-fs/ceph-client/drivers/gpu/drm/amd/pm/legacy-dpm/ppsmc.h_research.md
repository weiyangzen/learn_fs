# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/ppsmc.h

## Purpose

`ppsmc.h` defines legacy PowerPlay SMC firmware constants shared by several AMD DPM generations. It contains software-state flags, thermal/system flags, fan-control modes, SMC result codes, and many SMC message IDs used to command firmware features such as DPM, CAC, BAPM, ULV, UVD/VCE/SAMU/ACP power, clock masks, PCIe/NB DPM, thermal DPM, and ucode loading.

## Important APIs, Types, and Macros

The file is macro-heavy. It defines `PPSMC_Result_OK`, `PPSMC_Result_Failed`, `typedef uint8_t PPSMC_Result`, and `typedef uint16_t PPSMC_Msg`. `enum FAN_CONTROL` declares `FAN_CONTROL_FUZZY` and `FAN_CONTROL_TABLE`. Message IDs include early 8-bit commands like `PPSMC_MSG_Halt`, `PPSMC_MSG_SwitchToSwState`, `PPSMC_MSG_EnableCac`, `PPSMC_MSG_EnableULV`, `PPSMC_MSG_SetEnabledLevels`, and CI/KV/KB 16-bit commands like `PPSMC_MSG_DPM_Enable`, `PPSMC_MSG_SCLKDPM_SetEnabledMask`, `PPSMC_MSG_SCLKDPM_GetEnabledMask`, `PPSMC_MSG_UVDDPM_Enable`, `PPSMC_MSG_VCEDPM_Enable`, `PPSMC_MSG_NBDPM_Enable`, `PPSMC_MSG_EnableBAPM`, and block power on/off commands. Later message IDs cover driver/SMU DRAM addresses and ucode loading.

## Control Flow

There is no direct control flow. Callers pass these constants to ASIC-specific mailbox helpers. In this subset, `kv_smc.c` writes the IDs to SMC message registers and `kv_dpm.c` selects messages according to DPM enable, BAPM enable, SCLK masks, forced levels, UVD/VCE/SAMU/ACP gating, ULV, CAC, and NB DPM state.

## State and Persistence Behavior

The header has no runtime state. The constants map to firmware commands that mutate SMU state, power state, DPM masks, firmware loading state, and block power status. Effects persist in SMU firmware and hardware until later messages or reset.

## Dependencies and Integration Points

The file uses `#pragma pack(push, 1)`/`pop`, fixed-width integer types, and no other includes. It is included by legacy SMC/DPM headers such as `kv_dpm.h` and `sislands_smc.h`. It is part of the firmware ABI between the kernel driver and legacy SMU firmware.

## Risks and Edge Cases

Message IDs are hardware/firmware contracts; changing values breaks runtime control. Some macros are duplicated, such as `PPSMC_MSG_PCIeDPM_Disable`, and message widths vary between `uint8_t`, `uint16_t`, and `uint32_t` casts while `PPSMC_Msg` is `uint16_t`. Callers must use the right generation-specific command. Unsupported messages may return firmware failure codes or no response, depending on ASIC firmware.

## Test Signals

Build coverage catches missing names. Runtime validation includes successful SMC responses for DPM enable/disable, CAC/BAPM toggles, SCLK enabled masks, UVD/VCE/SAMU/ACP power messages, and suspend/resume. Firmware tracing or mailbox debug logs are useful when a specific message returns `0xfe`, `0xff`, or times out.
