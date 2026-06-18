# sources/distributed-fs/ceph-client/drivers/ras/cec.c

Purpose: implements the RAS Correctable Errors Collector. It counts correctable DRAM errors per page frame, applies decay to approximate recency, and soft-offlines pages whose correctable error count reaches a configurable threshold.

Important APIs and functions: internal state is `struct ce_array ce_arr`, backed by one page of sorted `u64` entries. Main functions are `cec_add_elem()`, `cec_notifier()`, `do_spring_cleaning()`, `find_elem()`, `del_lru_elem_unlocked()`, `create_debugfs_nodes()`, and `cec_init()`. Boot option parsing is via `parse_cec_param()`.

Control flow: late init allocates the page array, creates debugfs controls under `ras/cec`, schedules delayed decay work, and registers an MCE notifier. The notifier only handles correctable memory errors with usable addresses. `cec_add_elem()` inserts or refreshes a PFN, sets max decay generation, increments count, soft-offlines through `memory_failure_queue()` when threshold is reached, otherwise triggers cleaning when enough updates have accumulated. Periodic work decays all entries and reschedules itself.

State and persistence: all collector data is volatile in `ce_arr`. `ce_mutex` protects the array, counters, threshold, and decay interactions. Debugfs knobs hold `decay_interval`, `action_threshold`, and optional debug insertion PFN. There is no persistence across reboot.

Dependencies and integration: uses x86 MCE helpers, RAS debugfs root, workqueues, memory failure infrastructure, and kernel debugfs attributes. `parse_ras_param()` in `ras.c` delegates `ras=cec_disable` handling here when enabled.

Risks: the page-sized array is intentionally simple but does O(n) memmove/delete. `del_lru_elem_unlocked()` returns `PFN(ca->array[min_idx])` after deletion, which is only diagnostic but worth review because the entry was shifted. Threshold setter stores the raw debugfs value before clamping the global action threshold. Intel defaults threshold to 2, which changes behavior by vendor.

Test signals: boot with `ras=cec_disable`, debugfs threshold and decay bounds, manual PFN insertion when `CONFIG_RAS_CEC_DEBUG`, duplicate PFN count increments, full-array eviction, threshold soft-offline, invalid PFN warning, and delayed decay rescheduling.
