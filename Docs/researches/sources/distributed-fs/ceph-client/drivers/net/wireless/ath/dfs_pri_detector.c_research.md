<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pri_detector.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pri_detector.c

Purpose: Implements pulse repetition interval detection for a single radar specification, including reusable singleton pools for pulse and sequence objects.

Important APIs/types/functions: Exports `pri_detector_init()`. Internal helpers include `pde_get_multiple()`, pool registration/get/put functions, `pulse_queue_enqueue()`, `pulse_queue_dequeue()`, `pulse_queue_check_window()`, `pseq_handler_create_sequences()`, `pseq_handler_add_to_existing_seqs()`, `pseq_handler_check_detection()`, `pri_detector_add_pulse()`, `pri_detector_reset()`, and `pri_detector_exit()`. Exposes `global_dfs_pool_stats`.

Control flow: New pulses are filtered by width, minimum timestamp spacing, and chirp requirement. Existing sequences are advanced or aged out, new candidate sequences are built by comparing the current timestamp to queued historical pulses, and detection fires when a sequence reaches the spec threshold with enough matching pulses relative to false pulses. Non-detecting pulses are queued within a sliding time window.

State and persistence: Each detector keeps last timestamp, pulse queue, candidate sequence list, count, max count, and window size. Singleton pools retain freed `pulse_elem` and `pri_sequence` objects while any detector exists, protected by `pool_lock`; pools are freed when the last detector deregisters.

Dependencies and integration points: Used by `dfs_pattern_detector.c`; consumes `struct radar_detector_specs` and `struct pulse_event`; logs and stats are shared at ath DFS level.

Risks and test signals: Risks include GFP_ATOMIC allocation failures, false sequence growth under noisy pulses, timestamp arithmetic assumptions, pool reference imbalance, and boundary tolerance errors. Test signals are synthetic radar bursts, random noise rejection, chirp-required patterns, detector reset/exit leak checks, and pool stats consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pri_detector.c -->
