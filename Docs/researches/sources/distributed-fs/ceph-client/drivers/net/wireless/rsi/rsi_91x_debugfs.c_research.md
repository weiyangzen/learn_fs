# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_debugfs.c

Purpose: debugfs instrumentation for RSI devices.

Important APIs/functions: `rsi_init_dbgfs()` creates a per-wiphy debugfs directory and files; `rsi_remove_dbgfs()` removes it. Read handlers expose SDIO interrupt/buffer stats, LMAC firmware version, FSM/queue TX stats, and current debug-zone mask. `rsi_debug_zone_write()` updates global `rsi_zone_enabled` from a hex value.

Control flow: file operations use `single_open()` and `seq_read`. `dev_debugfs_files[]` describes file names, permissions, and fops. Initialization allocates `struct rsi_debugfs`, stores it on the adapter, creates the directory from `wiphy_name()`, and creates the requested number of entries.

State and persistence: debugfs state persists while the adapter exists. It reads live counters from `struct rsi_common` and SDIO device state, and mutates the global debug-zone mask.

Dependencies/integration: Linux debugfs/seq_file, RSI SDIO private structure, common TX stats/FSM, firmware version fields, and driver debug macro.

Risks: `sdio_stats` assumes an SDIO-shaped `adapter->rsi_dev`, so exposing it for non-SDIO adapters would be unsafe unless `num_debugfs_entries` excludes it. `debug_zone` is world-writable (`0666`) and controls global logging. `rsi_remove_dbgfs()` frees entries but not the allocated `dev_dbgfs` object in this file.

Test signals: mount debugfs, read all files on SDIO and non-SDIO builds, write debug masks, verify FSM names match `NUM_FSM_STATES`, and check cleanup on device removal.
