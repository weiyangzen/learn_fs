# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ppsmc.h

## Purpose
`ppsmc.h` is the shared PowerPlay-to-SMC message and flag vocabulary for Radeon DPM code. It defines firmware result codes, state/system/extra flags, fan-control modes, display watermark values, thermal-protection modes, and SMC message IDs used across multiple ASIC families.

## Important APIs, Types, And Functions
The file exports constants and two typedefs: `PPSMC_Result` as an 8-bit firmware response and `PPSMC_Msg` as a 16-bit message type. Important constants include `PPSMC_Result_OK`/`PPSMC_Result_Failed`, state flags such as `PPSMC_SWSTATE_FLAG_DC`, `UVD`, `VCE`, and `PCIE_X1`, system flags such as `GPIO_DC`, `STEPVDDC`, and `GDDR5`, state behavior flags such as `POWERBOOST` and deep-sleep controls, `enum FAN_CONTROL`, legacy 8-bit messages for RV7xx/NI-era firmware, CI/KV/KB 16-bit DPM messages, and TN 32-bit-valued message macros.

## Control Flow
There is no local execution. Runtime control flow occurs in SMC client code that writes one of these message IDs to an SMC mailbox, waits for a response, and branches on `PPSMC_Result_OK`. Common flows include halt/resume, switching to driver or initial states, forcing high/medium/no levels, enabling or disabling CAC/DTE/ULV/Thermal DPM, powering UVD/VCE/SAMU/ACP blocks, setting enabled masks, forcing PCIe or MCLK/SCLK levels, and querying clocks.

## State, Persistence, And Dependencies
The constants represent protocol state in firmware mailboxes and SMC-managed state machines. They do not store kernel state themselves. The header uses packed pragmas for consistency with adjacent firmware ABI headers, although it contains only scalar constants and an enum. It depends on fixed-width integer types and is consumed by ASIC-specific DPM and SMC mailbox implementations.

## Integration Points
`rv770_dpm.c`, NI/SI/CI/KV DPM code, and SMC transport files use these definitions to build state tables and send mailbox commands. `nislands_smc.h` relies on the flag meanings for state-table fields, and `pptable.h` supplies BIOS-derived classifications that are translated into these SMC flags and messages.

## Risks
Message IDs are firmware ABI. Reusing an ID for the wrong ASIC family can cause silent no-ops, failed responses, or incorrect power-state transitions. Some macros intentionally overlap by family and width, and `PPSMC_MSG_PCIeDPM_Disable` is defined twice with the same value, so consumers must not assume a unique list. The typedef `PPSMC_Msg` is 16-bit even though TN macros are declared with 32-bit casts, so code passing TN-only IDs through `PPSMC_Msg` should be checked for truncation assumptions. Feature flags must match the SMC firmware version loaded for the device.

## Test Signals
Test signals include successful SMC halt/resume handshakes, mailbox timeout/error handling, DPM enable/disable, forced-level changes, AC/DC transitions, thermal interrupt enablement, UVD/VCE/SAMU/ACP power toggles, clock query responses, and negative tests that unsupported messages return failure without corrupting state.
