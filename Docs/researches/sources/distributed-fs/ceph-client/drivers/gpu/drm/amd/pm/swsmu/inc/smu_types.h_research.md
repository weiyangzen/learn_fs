<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_types.h

## Purpose

`smu_types.h` is the common SMU enumeration contract shared across AMDGPU SWSMU generations. It defines the generic `SMU_MSG_*`, `SMU_*CLK`, and `SMU_FEATURE_*_BIT` namespaces that platform-specific code maps onto ASIC/PMFW-specific command IDs and feature bits.

## Important APIs, Types, and Functions

The main macros are `SMU_MESSAGE_TYPES` and `SMU_FEATURE_MASKS`, each expanded through `__SMU_DUMMY_MAP` to create `enum smu_message_type` and `enum smu_feature_mask`. `enum smu_clk_type` lists clock domains such as GFXCLK, VCLK/DCLK pairs, SOCCLK, UCLK, DCEFCLK, DISPCLK, FCLK, PCIe, ISP, OD-specific entries, fan curve controls, and GL2CLK. Message flags `SMU_MSG_VF_FLAG`, `SMU_MSG_RAS_PRI`, `SMU_MSG_NO_PRECHECK` and firmware capability flag `SMU_FW_CAP_RAS_PRI` annotate special message behavior.

## Control Flow

The file has no runtime flow, but it drives mapping control flow. Platform files declare arrays such as `cmn2asic_msg_mapping`, `cmn2asic_mapping` clock maps, table maps, feature maps, and workload maps indexed by these enums. Helpers like `smu_cmn_to_asic_specific_index()`, `smu_cmn_send_smc_msg*()`, and feature-mask routines use the generic enum as the frontend contract and reject or translate unsupported entries.

## State and Persistence Behavior

No state is stored here. The enums name state controlled elsewhere: firmware-enabled feature masks, frequency domains, power profile choices, RAS-priority command handling, and message precheck policy. The numeric order of enum members persists as an in-kernel ABI between common code and every platform mapping table.

## Dependencies

This header is consumed by `amdgpu_smu.h`, SMU generation headers, and all platform PPT implementations. It relies on every mapping table being sized to `SMU_MSG_MAX_COUNT`, `SMU_CLK_COUNT`, or `SMU_FEATURE_COUNT` and initialized consistently.

## Integration Points

Arcturus, Cyan Skillfish, Navi, Sienna, SMU13, SMU14, and SMU15 files all map subsets of these messages/features to PMFW IDs. User-facing sysfs and hwmon operations often begin with a generic `SMU_*` clock or message and then flow through these maps.

## Risks and Edge Cases

Adding or reordering enum entries can silently break array-indexed mappings if all tables are not updated. Some generic messages are valid only for specific generations, virtual functions, or RAS-priority firmware. Feature names are broad and sometimes generation-specific despite sharing a common enum; unsupported entries must remain unmapped rather than assumed available.

## Test Signals

Compile-time array-size coverage, platform boot probes, message-map lookup tests, feature enable/disable smoke tests, and sysfs clock/OD operations across multiple ASIC generations are the best validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_types.h -->
