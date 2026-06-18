<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_12_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_12_pmfw.h

## Purpose
Defines PMFW metrics and static-info structures for SMU v13.0.12, including packed system, VF, FRU, and static metrics layouts used by host tools and drivers.

## Important APIs, Types, And Constants
The file exports DPM and link-count constants, `FEATURE_LIST_e`, `PCIE_LINK_SPEED_INDEX_TABLE_e`, `GFX_GUARDBAND_OFFSET_e`, `GFX_DVM_MARGIN_e`, temperature and power enums, `MetricsTable_t`, `SystemMetricsTable_t`, `VfMetricsTable_t`, `FRUProductInfo_t`, and `StaticMetricsTable_t`. `SMU_METRICS_TABLE_VERSION` is `0x15`, `SMU_SYSTEM_METRICS_TABLE_VERSION` is `0x1`, and `SMU_VF_METRICS_TABLE_VERSION` is `0x6` ORed with the VF mask bit.

## Control Flow
The driver requests metrics tables from PMFW and decodes the packed/aligned structures. Static tables describe capabilities and topology, while metrics tables report live clocks, temperatures, powers, activity, throttling, link states, XGMI/CXL/PCIe information, and partition/VF data.

## State And Persistence
Metrics are live firmware snapshots. Static metrics and FRU info are stable for the boot/device, while live fields change on each transfer. The packed layout is persistent as an ABI contract even though values are volatile.

## Dependencies And Integration
Integrated with SMU v13.0.12 server/datacenter GPU code, SR-IOV/VF metrics readers, FRU inventory paths, performance monitoring, hwmon, debugfs, and link/partition management.

## Risks And Test Signals
Risks include structure packing/alignment drift, version mismatch, interpreting VF tables as physical-function metrics, and stale enum order for temperature/power arrays. Test signals include metrics table version checks, struct size checks, plausible power/thermal/clock values, VF metrics reads, FRU field decoding, and PCIe/XGMI/CXL link telemetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_12_pmfw.h -->
