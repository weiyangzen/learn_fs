<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/aldebaran_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/aldebaran_ppsmc.h

## Purpose
This header defines Aldebaran PPSMC mailbox response codes, PMFW message IDs, reset argument values, GFXOFF error codes, and typed aliases for SMU result and message words. It is an ASIC-specific firmware ABI map used by the Aldebaran SMU backend when translating generic SMU messages into the numeric protocol expected by PMFW.

## Important APIs, Types, and Functions
- Response codes: `PPSMC_Result_OK`, `Failed`, `UnknownCmd`, `CmdRejectedPrereq`, and `CmdRejectedBusy`.
- Message ID space: core version and driver interface queries, feature enable/disable, table DRAM address and transfer commands, DPM soft/hard min/max frequency commands, workload and voltage commands, PPT limit commands, MP1/reset commands, BTC, DRAM log, debug, memory channel, HBM bad page/channel, DF C-state, GMI power-down, GFXOFF, determinism, UCLK DPM mode, STB-to-DRAM, reset recovery, board power calibration, and HeavySBR.
- Reset arguments: warm reset, driver mode1/mode2, PCIe link, BIF link, and PF0 FLR.
- `GFXOFF_ERROR_e`, `PPSMC_Result`, and `PPSMC_Msg`.

## Control Flow
There is no executable control flow. Runtime control flow occurs when the Aldebaran backend maps a generic `enum smu_message_type` to one of these `PPSMC_MSG_*` values and sends it through the SMU mailbox. PMFW returns one of the response codes, which the driver message layer decodes into success, busy, prereq failure, unknown command, or generic failure. Reset operations pass one of the reset type constants as message argument data.

## State and Persistence Behavior
The file stores no runtime state. Its constants are persistent firmware ABI state: the numeric values must match Aldebaran PMFW. `#pragma pack(push, 1)` and `pop` bracket the definitions defensively even though the file only defines simple enum/typedef content.

## Dependencies and Integration Points
- Included by Aldebaran-specific SMU/PPT code and mapping tables.
- Integrates with generic `amdgpu_smu.h` message and reset paths, especially `smu_mode1_reset`, `smu_mode2_reset`, link reset, STB collection, HBM bad page reporting, and PMFW table transfers.
- Values are consumed by PMFW mailbox register programming, not by normal C function calls.

## Risks
- Message numbers are not interchangeable with Arcturus or Navi10. Copying mappings between ASICs can send a valid but wrong command.
- Some reset commands are marked retired in firmware comments; using them without version checks can fail on newer PMFW.
- Gaps and spare values are part of the ABI and should not be renumbered.
- Busy and prereq responses need retry or graceful failure at higher layers where appropriate.

## Test Signals
- Build Aldebaran SMU backend and verify all `MSG_MAP` entries resolve to these constants.
- Runtime firmware-version and driver-interface checks should pass before DPM setup.
- Exercise table transfer, power limit, GFXOFF, STB dump, HBM bad page/channel reporting, and reset commands on Aldebaran hardware or firmware simulation.
- Negative tests should confirm unknown/busy/prereq responses are decoded into the intended errno paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/aldebaran_ppsmc.h -->
