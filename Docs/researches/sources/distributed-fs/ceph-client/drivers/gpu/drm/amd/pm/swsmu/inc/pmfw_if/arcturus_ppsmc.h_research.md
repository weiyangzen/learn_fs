<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/arcturus_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/arcturus_ppsmc.h

## Purpose
This header defines the Arcturus PPSMC mailbox ABI: PMFW response codes, message IDs, and simple typedefs for result and message words. It is the numeric command map used by Arcturus-specific SMU code when sending feature, table, DPM, BACO, VCN power, reset, BTC, debug, XGMI, bad HBM page, DF C-state, serial number, and LightSBR commands to PMFW.

## Important APIs, Types, and Functions
- Response codes mirror common PPSMC semantics: OK, failed, unknown command, rejected by prereq, and rejected busy.
- Basic messages cover SMU version, driver interface version, allowed feature masks, feature enable/disable, enabled feature masks, driver/tool DRAM addresses, table transfers, default/backup PPTable use, and system virtual DRAM address setup.
- Power and DPM messages include BACO entry/exit, ArmD3, soft/hard min/max by frequency, DPM frequency queries, workload mask, DF switch type, voltage queries, and PPT limits.
- Other IDs handle VCN0/VCN1 power, MP1 unload/reset/shutdown, soft reset, AFLL/DC BTC, dram log/debug, WAFL/XGMI, memory channel enable, bad HBM page count, DF C-state, GMI power-down, serial number reads, and LightSBR.
- Defines `PPSMC_Result` and `PPSMC_Msg` as `uint32_t`.

## Control Flow
The file is declarative. Arcturus mapping tables select these IDs for generic SMU operations, then the common message layer writes the numeric command and arguments to SMU mailbox registers. Feature and table setup in `amdgpu_smu.c` depends on these values through backend callbacks such as feature mask programming, PPTable transfer, DPM setup, VCN power gating, and reset handling.

## State and Persistence Behavior
No runtime state is stored. The constants are persistent firmware ABI values. The message count and gaps must remain synchronized with PMFW because the driver uses them as stable protocol identifiers across boots and resets.

## Dependencies and Integration Points
- Used by Arcturus PPT implementation and common SMU message mapping code.
- Connects generic SMU operations for BACO, DPM, VCN power gating, RAS serial/bad page paths, XGMI, DF C-state, and LightSBR to firmware.
- Depends on PMFW using the same result code and message numbering contract.

## Risks
- Numeric drift causes silent protocol corruption: PMFW may execute another command or reject the message.
- The LightSBR command has parameter semantics documented in comments; inverting the argument changes reset ownership between SMU/PSP and the driver.
- Some commands have ASIC-specific behavior and should not be assumed present just because a common `smu_message_type` exists.
- `PPSMC_Message_Count` is lower than later explicit serial/LightSBR values, so code must not use it as a complete max for all defines without checking intent.

## Test Signals
- Compile Arcturus backend mapping tables and confirm all referenced `PPSMC_MSG_*` names exist.
- On Arcturus hardware, verify feature mask setup, PPTable transfer, VCN power up/down, BACO transitions, XGMI controls, and LightSBR behavior.
- Check PMFW response decode for busy/prereq failure by injecting or observing rejected commands.
- Confirm serial number reads and HBM bad page reporting still use the expected command IDs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/arcturus_ppsmc.h -->
