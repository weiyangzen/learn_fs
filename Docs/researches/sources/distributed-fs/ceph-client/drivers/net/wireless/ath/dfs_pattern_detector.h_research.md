<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pattern_detector.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pattern_detector.h

Purpose: Declares the public ath DFS pattern detector interface and the common radar pulse/spec/stat structures shared with PRI detector code and ath drivers.

Important APIs/types/functions: Defines `PRI_TOLERANCE`, `struct ath_dfs_pool_stats`, `struct pulse_event`, `struct radar_detector_specs`, `struct dfs_pattern_detector`, and `dfs_pattern_detector_init()`.

Control flow: No implementation flow, but the `dfs_pattern_detector` method table defines object-style operations: `exit`, `set_dfs_domain`, `add_pulse`, and `get_stats`.

State and persistence: Describes detector runtime state: DFS region, radar type count, last pulse timestamp, `ath_common` pointer for logging, radar spec pointer, and channel detector list.

Dependencies and integration points: Includes kernel list/types and nl80211 region definitions; used by ath DFS-capable drivers and `dfs_pri_detector`.

Risks and test signals: ABI/layout risks are low inside the kernel tree but method-pointer misuse or unset domain handling can affect radar behavior. Test signals include compile coverage, detector initialization by DFS-capable drivers, and stats reporting after pulse injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pattern_detector.h -->
