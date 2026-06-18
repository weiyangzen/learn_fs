<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/debugfs.c

Purpose: registers firmware-runtime debugfs controls for manual collection, host command injection, timestamp marker scheduling, severity configuration, and firmware metadata reads.

Important APIs/functions: wrapper macros generate open/read/write file operations with per-open buffers. `iwl_dbgfs_fw_dbg_collect_write()` triggers an INI user timepoint and legacy `FW_DBG_TRIGGER_USER` collection. `iwl_dbgfs_enabled_severities_write()` sends `HOST_EVENT_CFG`. `iwl_fw_trigger_timestamp()` and `iwl_fw_timestamp_marker_wk()` schedule repeated `MARKER_CMD` emission through `iwl_fw_send_timestamp_marker_cmd()`. `iwl_dbgfs_send_hcmd_write()` parses a hex-encoded command header/body and sends it through op-mode `send_hcmd`. `iwl_dbgfs_fw_info_seq_show()` streams capability and command-version information. `iwl_fwrt_dbgfs_register()` creates the files.

Control flow: reads lazily fill a fixed kernel buffer once per open and then use `simple_read_from_buffer`; writes copy bounded user input, parse numeric or hex data, and call runtime or op-mode hooks. The timestamp worker reschedules itself while command sends succeed and a delay remains.

State and persistence: debugfs files expose and mutate `fwrt->timestamp.delay`, `fwrt->timestamp.wk`, transport debug domains, and firmware runtime command state. No durable data is stored; debugfs writes can trigger devcoredumps or firmware commands.

Dependencies/integration: depends on Linux debugfs/seq_file/hex helpers, `struct iwl_fw_runtime`, op-mode `send_hcmd`, firmware command versions, and debug collection APIs.

Risks/test signals: user input is privileged but high impact: malformed hex commands, unsupported firmware state, response SKB ownership, and repeated timestamp work need testing. Verify file creation only under debugfs builds, manual dump collection, host command length validation, capability dump formatting, and timestamp cancel/resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/debugfs.c -->
