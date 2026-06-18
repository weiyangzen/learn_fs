# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_0_d.h

## Purpose

`smu_7_1_0_d.h` is a generated AMD SMU 7.1.0 register-definition header. It exports preprocessor constants that bind symbolic register names to the numeric MMIO, indirect-index, SRAM-table, thermal, power-management, ROM, fuse, and GPIO addresses for this ASIC generation. The file contains no executable code; its value is as a compile-time hardware contract used by register access helpers elsewhere in the AMDGPU power-management and SMU paths.

The header is guarded by `SMU_7_1_0_D_H` and is paired conceptually with `smu_7_1_0_sh_mask.h` for bitfield masks/shifts and with `smu_7_1_0_enum.h` for command and field-value encodings. It follows the local ASIC-register convention where `mm*` names identify directly addressed MMIO registers and `ix*` names identify indirect registers or indexed table locations reached through an SMU/GCK/ROM index/data window.

## Important APIs, Types, And Constants

This file does not define C functions, structs, or enums. Its API surface is the set of `#define` register constants.

Important exported groups include:

- Indirect SMU/GCK/ROM windows: `mmGCK_SMC_IND_INDEX`, `mmGCK_SMC_IND_DATA`, `mmSMC_IND_INDEX`, `mmSMC_IND_DATA`, numbered aliases such as `mmSMC_IND_INDEX_0` through `mmSMC_IND_INDEX_7`, and ROM aliases such as `mmROM_SMC_IND_INDEX`.
- SMU mailbox registers: `mmSMC_MESSAGE_0` through `mmSMC_MESSAGE_11`, `mmSMC_RESP_0` through `mmSMC_RESP_11`, and `mmSMC_MSG_ARG_0` through `mmSMC_MSG_ARG_11`. These form the host-to-SMC command channel used by driver code that writes an argument, writes a message ID, then polls a response register.
- SMC system-control and scratch/register addresses: `ixSMC_SYSCON_RESET_CNTL`, `ixSMC_SYSCON_CLOCK_CNTL_*`, `ixSMC_SYSCON_MISC_CNTL`, `ixSMC_SYSCON_MSG_ARG_0`, `ixSMC_PC_C`, and `ixSMC_SCRATCH9`.
- Clock-generation and PLL registers: `ixCG_DCLK_CNTL`, `ixCG_VCLK_CNTL`, `ixCG_ECLK_CNTL`, `ixCG_ACLK_CNTL`, `ixCG_SPLL_FUNC_CNTL*`, `ixSPLL_CNTL_MODE`, `ixCG_SPLL_SPREAD_SPECTRUM*`, `ixMPLL_BYPASSCLK_SEL`, `ixCG_CLKPIN_CNTL*`, `ixTHM_CLK_CNTL`, and `ixMISC_CLK_CTRL`.
- Fuse and firmware/status registers: `ixRCU_UC_EVENTS`, `ixRCU_MISC_CTRL`, `ixCC_*_FUSES`, `ixSMU_MAIN_PLL_OP_FREQ`, `ixSMU_STATUS`, `ixSMU_FIRMWARE`, `ixSMU_INPUT_DATA`, and `ixSMU_EFUSE_0`.
- Large contiguous SRAM/table maps: `ixDPM_TABLE_1` through `ixDPM_TABLE_506`, `ixMCARB_DRAM_TIMING_TABLE_1` through `ixMCARB_DRAM_TIMING_TABLE_144`, `ixMC_REGISTERS_TABLE_1` through `ixMC_REGISTERS_TABLE_113`, `ixFAN_TABLE_1` through `ixFAN_TABLE_9`, `ixSOFT_REGISTERS_TABLE_1` through `ixSOFT_REGISTERS_TABLE_30`, `ixPM_FUSES_1` through `ixPM_FUSES_19`, and `ixSMU_PM_STATUS_0` through `ixSMU_PM_STATUS_127`.
- Thermal and fan registers: `ixCG_THERMAL_INT_ENA`, `ixCG_THERMAL_INT_CTRL`, `ixCG_THERMAL_INT_STATUS`, `ixCG_THERMAL_CTRL`, `ixCG_THERMAL_STATUS`, `ixCG_FDO_CTRL*`, `ixCG_TACH_CTRL`, `ixCG_TACH_STATUS`, `ixTHM_TMON*_RDIL*_DATA`, `ixTHM_TMON*_RDIR*_DATA`, and TMON interrupt/debug registers.
- Power-management control registers: `ixGENERAL_PWRMGT`, `ixCNB_PWRMGT_CNTL`, `ixSCLK_PWRMGT_CNTL`, `ixTARGET_AND_CURRENT_PROFILE_INDEX`, `ixCG_FREQ_TRAN_VOTING_*`, `ixCG_ACPI_CNTL`, `ixSCLK_DEEP_SLEEP_CNTL*`, `ixLCLK_DEEP_SLEEP_CNTL*`, `ixCG_ULV_PARAMETER`, and `ixSCLK_MIN_DIV`.
- ROM-control/data registers: `ixROM_CNTL`, `ixPAGE_MIRROR_CNTL`, `ixROM_STATUS`, `ixROM_INDEX`, `ixROM_DATA`, `ixROM_START`, `ixROM_SW_CNTL`, `ixROM_SW_STATUS`, `ixROM_SW_COMMAND`, and `ixROM_SW_DATA_1` through `ixROM_SW_DATA_64`.

## Control Flow

There is no runtime control flow inside this header. Downstream control flow is implicit in the mailbox and indirect-register patterns:

1. Code selects an indirect SMC address by writing an `ix*` address to one of the `mmSMC_IND_INDEX_*` registers.
2. Code transfers data through the matching `mmSMC_IND_DATA_*` register.
3. For SMC commands, code optionally writes an argument to `mmSMC_MSG_ARG_0`, clears or checks `mmSMC_RESP_0`, writes a command ID to `mmSMC_MESSAGE_0`, and polls `mmSMC_RESP_0` until firmware returns a nonzero result.

Nearby consumers show the expected pattern. `pm/powerplay/smumgr/smu7_smumgr.c` uses SMU7 index/data and mailbox names in helpers such as `smu7_copy_bytes_to_smc()`, `smu7_send_msg_to_smc()`, and `smu7_send_msg_to_smc_with_parameter()`. The legacy `kv_smc.c` path uses equivalent SMU 7.0.0 constants in the same pattern, confirming the intended integration shape for this register family.

## State And Persistence Behavior

The header itself owns no mutable state and performs no persistence. The constants address persistent or semi-persistent hardware and firmware state:

- SMC SRAM and table regions hold firmware-owned DPM, memory-controller, fan, fuse, soft-register, and status data.
- `ixDPM_TABLE_*`, `ixMCARB_DRAM_TIMING_TABLE_*`, `ixMC_REGISTERS_TABLE_*`, and related table constants are offsets into firmware-visible storage, not host memory allocations.
- Mailbox registers are transient command/response state shared between the host driver and the SMC firmware.
- Fuse and ROM constants expose hardware configuration or firmware image data that may be read as stable device configuration, but writes to control registers can affect hardware behavior immediately.

Because these constants are direct hardware contracts, they should be treated as immutable for a given ASIC revision unless regenerated from authoritative register documentation.

## Dependencies And Integration Points

The file depends only on the C preprocessor and include-guard mechanics. Its real dependencies are external hardware contracts:

- The SMU 7.1.0 ASIC register map supplies the numeric addresses.
- Register-access macros and helpers such as `RREG32`, `WREG32`, `cgs_read_register()`, `cgs_write_register()`, `cgs_read_ind_register()`, and higher-level `PHM_*` field helpers consume these constants.
- `smu_7_1_0_sh_mask.h` supplies masks/shifts for fields at the addresses defined here.
- `smu_7_1_0_enum.h` supplies command IDs and enumerated field values that may be written through the mailbox or into related fields.
- Adjacent generated headers for `smu_7_0_0`, `smu_7_1_1`, `smu_7_1_2`, and `smu_7_1_3` provide compatible but revision-specific maps. Selecting the wrong revision can produce valid C that accesses the wrong hardware locations.

No exact `#include "smu/smu_7_1_0_d.h"` consumer was found in the scanned AMDGPU subtree, while the adjacent versioned headers are actively included by power-management code. This suggests this header is part of the generated ASIC-register inventory and may be selected indirectly, conditionally, or kept for completeness of supported revisions.

## Risks

- Address drift is the primary risk. A single incorrect constant can make the driver read or write the wrong MMIO or indirect register, causing power-management failures, firmware hangs, thermal/fan misbehavior, or GPU instability.
- The repeated table ranges are mechanically regular but easy to corrupt in manual edits. For example, `ixDPM_TABLE_*`, `ixSMU_PM_STATUS_*`, and ROM data ranges must remain contiguous 4-byte strides unless the hardware spec says otherwise.
- Mailbox aliasing is subtle. Multiple symbolic names share the same numeric index/data addresses for different blocks or instances. A change that appears to remove duplication can break code readability or generated-header parity.
- This header defines only addresses, not access ordering, locking, polling timeouts, or bitfield masks. Callers must still use the correct register access domain and the corresponding `*_sh_mask.h` field definitions.
- Because no direct consumer was found in this tree, compile coverage may not catch accidental changes unless a configuration or generated include path selects the 7.1.0 revision.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration signals:

- Build configurations that include SMU 7.1.0 headers should compile without duplicate-name or missing-mask errors.
- Static checks can verify contiguous ranges keep a 4-byte stride for the generated tables and that mailbox index/data pairs remain matched.
- Runtime SMU smoke tests on matching hardware should confirm SMC SRAM reads/writes, firmware message send/poll behavior, DPM table access, thermal status reads, and fan/ROM access continue to work.
- Kernel logs from SMU mailbox paths are important: unsupported or failed message responses after a register-map change are strong regression signals.
- Cross-checking against the adjacent `smu_7_1_0_sh_mask.h` should confirm every field mask is associated with an address constant expected by consumers.
