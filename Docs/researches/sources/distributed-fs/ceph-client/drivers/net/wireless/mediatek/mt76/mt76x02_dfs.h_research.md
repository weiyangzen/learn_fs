<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dfs.h

Purpose: data definitions for mt76x02 DFS detection. It describes radar specs, hardware/software detector events, sequence tracking, stats, thresholds, and public DFS entry points.

Important APIs/types/functions: `struct mt76x02_radar_specs`, `struct mt76x02_dfs_event`, `struct mt76x02_dfs_event_rb`, `struct mt76x02_dfs_sequence`, `struct mt76x02_dfs_pattern_detector`, constants such as `MT_DFS_EVENT_BUFLEN`, `MT_DFS_SEQUENCE_TH`, and public prototypes for init/regulatory/AGC adjustment.

Control flow: declarative header. Macros decode hardware event words and constants parameterize the detector implemented in `mt76x02_dfs.c`.

State and persistence: the pattern detector stores live radar sequence state and tasklet scheduling state. No data is persistent outside device lifetime.

Dependencies/integration: included by `mt76x02.h`; uses Linux list/tasklet types, nl80211 DFS regions through users, and BBP event formats.

Risks: constants define detection sensitivity and compliance behavior; ring size and sequence window changes can alter false-positive rates. Test signals include compile checks, DFS region conformance tests, event ring wrap, sequence pool growth/shrink, and debugfs stats matching detector activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dfs.h -->
