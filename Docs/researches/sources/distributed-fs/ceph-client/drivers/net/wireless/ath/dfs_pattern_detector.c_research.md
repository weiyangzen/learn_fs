<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pattern_detector.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pattern_detector.c

Purpose: Implements the ath DFS radar pattern detector facade, selecting regulatory-domain radar specs and coordinating per-channel PRI detectors.

Important APIs/types/functions: Exports `dfs_pattern_detector_init()`. Internal types include `struct radar_types` and `struct channel_detector`. Key functions are `get_dfs_domain_radar_types()`, `channel_detector_create()`, `channel_detector_get()`, `dpd_set_domain()`, `dpd_add_pulse()`, `dpd_reset()`, and `dpd_exit()`.

Control flow: Initialization creates a `dfs_pattern_detector`, installs the default method table, and sets the requested DFS domain if certification-onus support is enabled. Domain selection points at ETSI, FCC, or JP pattern tables and clears old channel detectors. Each pulse finds or creates a channel detector for its frequency, resets all detectors on timestamp wrap, and runs every radar-type `pri_detector`. A successful sequence copies the matched spec to the caller, logs the detection, resets that detector, and returns true.

State and persistence: Keeps `region`, radar spec pointer/count, `last_pulse_ts`, `common`, and a list of channel detectors with detector arrays. State is in-memory and freed by `exit()`.

Dependencies and integration points: Depends on cfg80211 DFS region enums, `dfs_pri_detector`, `ath_dbg`, and caller-provided pulse events from hardware-specific ath drivers.

Risks and test signals: Risks include fail-safe radar detection for unset domains, allocation failure under GFP_ATOMIC, timestamp wrap reset effects, and false positives/negatives from static regulatory patterns. Test signals are DFS CAC/radar simulations per domain, pulse sequences at tolerance boundaries, multi-channel off-channel reports, and pool statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pattern_detector.c -->
