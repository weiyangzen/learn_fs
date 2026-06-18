<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_6.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_6.h

## Purpose
This header defines the SMU13.0.6 PMFW-side ABI fragments used for software I2C, error-code classification, AVFS debug tables, thermal interrupt notifications, throttler masks, clock IDs, UCLK DPM mode selection, and ClearMcaOnRead control. It is narrower than the full discrete GPU PPTable headers and leaves active table IDs to the consuming PPT implementation.

## Important APIs, Types, and Functions
The version is `SMU13_0_6_DRIVER_IF_VERSION`. Important types include I2C enums and `SwI2cRequestExternal_t`, `ERR_CODE_e`, `GC_ERROR_CODE_e`, `PPCLK_e`, `UCLK_DPM_MODE_e`, `AvfsDebugTableAid_t`, and `AvfsDebugTableXcd_t`. Error enums map MMHUB, VCN, JPEG, SDMA, SOC, GC, and shared MP5 error categories. I2C speed enums explicitly mark older 50 KHz, high-speed 1 MHz, and 2.3 MHz modes as unsupported. Interrupt and throttler constants include `IH_INTERRUPT_ID_TO_DRIVER`, `IH_INTERRUPT_CONTEXT_ID_THERMAL_THROTTLING`, `THROTTLER_PROCHOT_BIT`, PPT, socket/VR/HBM thermal bits, and `ClearMcaOnRead_UE_FLAG_MASK` / `ClearMcaOnRead_CE_POLL_MASK`.

## Control Flow
The header has no internal control flow. `smu13/smu_v13_0_6_ppt.c` includes it, defines local table mappings, initializes `SMU_TABLE_I2C_COMMANDS`, sends ClearMcaOnRead messages using the masks, handles thermal-throttling interrupt context IDs, and uses the software I2C request structures for firmware-mediated bus access. Error-code enums provide typed values for firmware RAS/error events rather than in-header behavior.

## State and Persistence Behavior
I2C request structures are transient command buffers. ClearMcaOnRead masks affect firmware behavior for clearing uncorrectable flags and correctable-error polling on read, so the resulting behavior persists in firmware policy until changed or reset. AVFS debug tables are snapshots per AID or XCD. Error code enums describe latched hardware/firmware events consumed by RAS or interrupt paths.

## Dependencies and Integration Points
Integration points are `smu_v13_0_6_ppt.c`, `smu_v13_0_6_ppsmc.h`, generic SMU message/table infrastructure, RAS/MCA clearing, thermal interrupt handling, software I2C support, and debug/AVFS table readers. The active table IDs are not taken from this header because its `TABLE_*` section is commented out in the source.

## Risks
The commented table definitions are a trap for maintainers; consumers must use the active local mapping in `smu_v13_0_6_ppt.c`. Unsupported I2C enum entries preserve numeric positions and should not be used as valid speeds. ClearMcaOnRead behavior is version-sensitive in the consumer and can affect RAS visibility if enabled or disabled on unsupported firmware. Error code values have intentional gaps and shared SOC codes, so compacting or renumbering them would break firmware event decoding.

## Test Signals
Build `smu_v13_0_6_ppt.c`, validate software I2C transfers, confirm thermal interrupt handling reaches the driver on over-temperature events, exercise ClearMcaOnRead only on firmware versions that advertise support, verify RAS logs preserve expected error-code names and MCA clearing behavior, and inspect AVFS debug snapshots for correct AID/XCD dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_6.h -->
