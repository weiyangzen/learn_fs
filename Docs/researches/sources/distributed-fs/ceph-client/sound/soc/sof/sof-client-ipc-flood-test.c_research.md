# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-ipc-flood-test.c

Purpose: Auxiliary SOF client that exposes debugfs-triggered IPC flood tests for measuring IPC latency and stress behavior.

Important APIs/state: `struct sof_ipc_flood_priv` stores debugfs root, backward-compatible symlinks, and a result buffer. Debugfs files `ipc_flood_count` and `ipc_flood_duration_ms` share `sof_ipc_flood_fops`; aux num selects count or duration mode. `sof_debug_ipc_flood_test()` sends repeated `SOF_IPC_GLB_TEST_MSG | SOF_IPC_TEST_IPC_FLOOD` commands and records min/max/average response times.

Control flow: Open rejects crashed firmware and takes a debugfs active reference. Write parses user count/duration, clamps to 10000 IPCs or 1000 ms, resumes runtime PM, boots DSP, runs the test through no-reply IPC sends, autosuspends, and returns count on success. Read returns the last formatted result. Probe creates per-device debugfs files and symlinks for auxdev id 0, then enables runtime PM; remove disables PM and removes debugfs.

Dependencies and integration: Uses SOF client APIs, auxiliary bus, debugfs, runtime PM, IPC test command support in firmware, and generic auxiliary PM behavior.

Risks: Flooding is bounded but still stresses firmware and can perturb active audio. Result buffer is shared per client without explicit serialization. `ktime_get_ns() + duration * NSEC_PER_MSEC` is simple and bounded by clamp. Open-time crashed check does not prevent crash during write.

Test signals: Count and duration writes, zero values, clamp limits, firmware crashed open, runtime PM resume errors, DSP boot errors, IPC failure mid-test, readback formatting, symlink creation/removal for id 0.
