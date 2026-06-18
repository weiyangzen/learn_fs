<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_8_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_8_ppsmc.h

## Purpose

`smu_v15_0_8_ppsmc.h` defines the SMU 15.0.8 PPSMC command and response namespace. It is the numeric protocol map used by the host driver when sending messages to PMFW through the common SMU message path.

## Important APIs, Types, and Functions

The header exports response codes `PPSMC_Result_OK`, `Failed`, `UnknownCmd`, `CmdRejectedPrereq`, and `CmdRejectedBusy`; message IDs from `PPSMC_MSG_TestMessage` through `PPSMC_MSG_SetSoftMaxFclk`; reset type arguments for driver mode 1/2/3 reset; PLPD mode arguments; and typedefs `PPSMC_Result` and `PPSMC_MSG` as `uint32_t`. Messages cover version queries, feature enablement, metric table transfer, driver/tools DRAM addresses, PPT limits, DRAM logging, resets, DF C-state, MCA/RAS queries, bad-page reporting, timestamps, system/static metrics, SDMA/VCN reset, fast PPT limits, and soft min/max GFX/GL2/FCLK controls.

## Control Flow

There is no executable control flow. SMU15 platform code maps generic `SMU_MSG_*` values to these numeric `PPSMC_MSG_*` IDs, then calls `smu_cmn_send_smc_msg*()` or table-transfer helpers. Firmware replies with the result codes defined here, and common SMU code translates transport/protocol failures into kernel return values.

## State and Persistence Behavior

The header has no local state. Messages change PMFW/device state when sent: allowed feature masks, soft frequency bounds, PPT limits, reset/recovery state, RAS table erase/clear-on-read behavior, timestamps, PLPD policy, and DRAM log locations. Address-setting commands persist in firmware until reset or overwritten.

## Dependencies

It depends only on fixed-width integer types and must match the corresponding SMU15.0.8 firmware. It is meaningful when included with `smu_v15_0_8_pmfw.h`, SMU15 common message-control initialization, and platform-specific message maps.

## Integration Points

The SMU15.0.8 PPT file includes this header to build the ASIC-specific message map. Common operations such as `GetSmuVersion`, `GetDriverIfVersion`, `SetDriverDramAddr`, `GetMetricsTable`, `SetPptLimit`, `GetStaticMetricsTable`, and reset/RAS flows ultimately use these IDs.

## Risks and Edge Cases

Numeric IDs are firmware ABI values; reordering or inserting without matching firmware support sends the wrong command. Some commands require multi-argument address or size setup, so callers must preserve ordering and 32-bit splitting. Commands such as `ClearMcaOnRead`, `EraseRasTable`, reset messages, and soft limit changes have device-wide side effects. `CmdRejectedBusy` and prerequisite failures need retry or graceful fallback rather than being treated as unknown commands.

## Test Signals

Build coverage catches missing names. Runtime validation should include SMU version/driver-interface checks, metrics table retrieval, feature-mask queries, PPT get/set round trips, reset recovery paths, and RAS/MCA command handling with expected PMFW response codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_8_ppsmc.h -->
