# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_baco.c

`vega20_baco.c` implements BACO/BAMACO support helpers for Vega20-class hardware. It detects platform support, reports BACO state from registers, enters/exits BACO through SMU messages, cleans BIOS scratch registers after exit, handles an RAS-aware enter parameter, and exposes a VDCI flush workaround.

Public APIs are `vega20_get_bamaco_support()`, `vega20_baco_get_state()`, `vega20_baco_set_state()`, and `vega20_baco_apply_vdci_flush_workaround()`. `clean_baco_tbl` is a small `soc15_baco_cmd_entry` table that writes zeroes to `NBIF` BIOS scratch registers 6 and 7 after BACO exit.

Support detection requires `PHM_PlatformCaps_BACO`, checks a raw register bit at `0x17569`, then checks `RCC_BIF_STRAP0__STRAP_PX_CAPABLE_MASK`. State reads use `BACO_CNTL__BACO_MODE_MASK`. Setting state is idempotent. Entering BACO sets `THM_BACO_CNTL` bit 31 and sends `PPSMC_MSG_EnterBaco` with parameter 0 when RAS is absent/disabled; with RAS enabled it sends parameter 1. Exiting sends `PPSMC_MSG_ExitBaco` and programs the cleanup table. The workaround calls `vega20_set_pptable_driver_address()` and sends `PPSMC_MSG_BacoWorkAroundFlushVDCI`.

State lives in hardware/SMU registers. The code reads `adev->ras_enabled` and RAS context for sequencing and clears scratch registers to avoid stale BIOS state. Dependencies include SOC15 register access, Vega20 register definitions, Vega20 SMU messages, common BACO programming, amdgpu RAS, and Vega20 SMU manager helpers.

Risks include the magic raw support register, fragile return handling around `soc15_baco_program_registers()`, RAS-specific sequencing differences, and capability mismatch. Test signals include BACO enter/exit, runtime suspend/resume, RAS enabled/disabled boards, scratch cleanup, BAMACO capability reporting, and VDCI workaround execution.
