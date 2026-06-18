<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu15_driver_if_v15_0_8.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu15_driver_if_v15_0_8.h

## Purpose
Defines auxiliary SMU 15.0.8 PMFW driver-interface structures for I2C command submission, MCA bank dump offsets, error-code decoding, AVFS debug tables, interrupt identifiers, throttler bits, and clear-on-read masks. It complements the main SMU 15 table and message headers.

## Important APIs, Types, And Constants
Exports I2C types `I2cControllerPort_e`, `I2cSpeed_e`, `I2cCmdType_e`, `SwI2cCmd_t`, `SwI2cRequest_t`, and `SwI2cRequestExternal_t` with `MAX_SW_I2C_COMMANDS 24`. Error-related APIs include `MCA_BANK_OFFSET_e`, `ERR_CODE_e`, and `GC_ERROR_CODE_e`. Clock/setting enums include `PPCLK_e`, `GpioIntPolarity_e`, and `UCLK_DPM_MODE_e`. Debug payloads are split into `AvfsDebugTableMid_t`, `AvfsDebugTableAid_t`, and `AvfsDebugTableXcd_t`.

## Control Flow
The driver submits an external I2C request table, firmware executes read/write command sequences, and response bytes are returned in the same table. MCA dump messages use `MCA_BANK_OFFSET_e` to select 64-bit registers. Interrupt context IDs identify thermal throttling and VFFLR events routed from PMFW to the driver.

## State And Persistence
The header carries transient command buffers and diagnostic state, not long-lived policy. AVFS debug structures expose per-block values, and clear-on-read masks control whether uncorrected/corrected/memory-hub poll state is consumed during dumps.

## Dependencies And Integration
Depends on SMU 15.0.8 PMFW messages that transfer driver tables and dump MCA/AVFS data. It integrates with kernel error handling/RAS paths, thermal throttling notification paths, SW I2C tooling, and AVFS diagnostics.

## Risks And Test Signals
Risks include malformed I2C command counts, incorrect MCA offset selection, and mismatched error-code interpretation between driver and firmware. Test signals are successful SW I2C transactions, expected MCA dump words, decoded GC/MCA errors, VFFLR interrupt handling, thermal throttling notifications, and AVFS debug table size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu15_driver_if_v15_0_8.h -->
