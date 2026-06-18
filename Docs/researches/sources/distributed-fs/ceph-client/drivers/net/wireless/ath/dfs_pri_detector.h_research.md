<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pri_detector.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pri_detector.h

Purpose: Declares the private PRI detector structures used by the DFS pattern detector implementation.

Important APIs/types/functions: Declares `global_dfs_pool_stats`, `struct pri_sequence`, `struct pri_detector`, and `pri_detector_init()`. `struct pri_detector` exposes `exit`, `add_pulse`, and `reset` method pointers plus internal queues and counters.

Control flow: No executable flow; callers allocate a detector for one `radar_detector_specs`, feed pulses through `add_pulse`, and reset or destroy through the method table.

State and persistence: Describes sequence state (`pri`, duration, count, false count, first/last/deadline timestamps) and detector state (`last_ts`, sequence list, pulse list, queue count, max count, window size). All state is volatile.

Dependencies and integration points: Includes Linux list support and relies on `dfs_pattern_detector.h` definitions for radar specs and pulse events.

Risks and test signals: Risks are mostly lifecycle and method-pointer misuse. Test signals include construction/destruction by `dfs_pattern_detector`, pulse additions yielding expected `pri_sequence` pointers, and reset clearing private queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pri_detector.h -->
