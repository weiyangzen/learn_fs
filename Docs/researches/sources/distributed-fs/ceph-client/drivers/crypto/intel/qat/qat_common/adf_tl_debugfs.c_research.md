# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_tl_debugfs.c

Purpose: implements debugfs control and formatted reporting for telemetry snapshots. It lets users start/stop telemetry, choose ring-pairs to monitor, and read aggregated device or ring-pair counters.

Important APIs: `adf_tl_dbgfs_add` and `adf_tl_dbgfs_rm`. Files include `telemetry/device_data`, `control`, and `rp_A_data` through the Gen-specific max RP slots. Helpers collect u32/u64 history values, calculate count/min/max/average, convert cycles to ns, convert bandwidth units to Mbps, and print device/slice/cmdq/RP rows.

Control flow and state: `control` write validates requested history depth, stops active telemetry if needed, and calls `adf_tl_run` or `adf_tl_halt` under `wr_lock`. RP file writes change selected RP index, restarting telemetry if active so firmware uses new indexes. Reads require active telemetry, collect recent history under `regs_hist_lock`, and print current plus min/max/avg when state > 1.

Dependencies and integration: depends on `adf_telemetry`, Gen-specific counter descriptors, service mapping, debugfs aux numbers, and misc workqueue-driven snapshots.

Risks and test signals: aggregation depends on `msg_cnt` and history index correctness; RP changes restart firmware telemetry. Test invalid control/RP inputs, zero samples, multi-sample aggregation, concurrent reads/writes, and removal while active.
