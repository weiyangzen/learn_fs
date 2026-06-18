<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_6_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_6_pmfw.h

## Purpose
Defines SMU v13.0.6 PMFW metrics structures and static metrics for a datacenter/server GPU generation.

## Important APIs, Types, And Constants
Exports DPM/link-count constants, `FEATURE_LIST_e`, `PCIE_LINK_SPEED_INDEX_TABLE_e`, `GFX_GUARDBAND_e`, packed `MetricsTableV0_t`, `MetricsTableV1_t`, `MetricsTableV2_t`, `VfMetricsTable_t`, and `StaticMetricsTable_t`. `SMU_METRICS_TABLE_VERSION` is `0x11` and `SMU_VF_METRICS_TABLE_VERSION` is `0x5`.

## Control Flow
Driver code transfers metrics tables from PMFW and chooses the expected layout/version. The metrics versions capture live clocks, temperatures, power, utilization, link state, throttling, and partition/VF information, while static metrics describe immutable hardware/topology information.

## State And Persistence
Metrics values are live snapshots; static metrics are boot/device-stable. Packed and aligned structure layout is the persistent ABI and must match firmware exactly.

## Dependencies And Integration
Integrates with SMU v13.0.6 monitoring, hwmon, debugfs, RAS/performance tooling, SR-IOV VF reporting, PCIe/XGMI/CXL link telemetry, and management utilities.

## Risks And Test Signals
Risks include selecting the wrong metrics version, struct packing drift, and interpreting VF tables as PF tables. Test signals include version checks, expected struct sizes, plausible telemetry values under load/idle, VF metrics reads, and link telemetry consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_6_pmfw.h -->
