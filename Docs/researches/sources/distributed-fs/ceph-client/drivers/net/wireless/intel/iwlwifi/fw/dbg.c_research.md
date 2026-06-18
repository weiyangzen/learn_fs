<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dbg.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dbg.c

Purpose: implements iwlwifi firmware debug collection. It builds both legacy `IWL_FW_ERROR_DUMP_BARKER` coredumps and newer INI/TLV driven dumps, stops and restarts firmware monitor recording around collection, and emits Linux devcoredump scatterlists.

Important APIs/functions: exported collection entry points are `iwl_fw_dbg_collect_desc()`, `iwl_fw_dbg_error_collect()`, `iwl_fw_dbg_collect()`, `iwl_fw_dbg_collect_trig()`, `iwl_fw_dbg_ini_collect()`, `iwl_fw_start_dbg_conf()`, `iwl_fw_dbg_stop_sync()`, `iwl_fw_dbg_read_d3_debug_data()`, `iwl_fw_dbg_stop_restart_recording()`, `iwl_fw_disable_dbg_asserts()`, and `iwl_fw_dbg_clear_monitor_buf()`. Legacy dump construction is centered on `iwl_fw_error_dump_file()`, with helpers for RXF/TXF FIFOs, PRPH/radio registers, memory segments, paging blocks, and D3 debug data. INI collection uses `iwl_dump_ini_region_ops[]` and per-region iterators for CSR, device memory, PRPH MAC/PHY, TXF/RXF, error tables, monitor DRAM/SMEM/DBGI, paging, firmware packets, special memory, and IMR.

Control flow: triggers reserve one bit in `fwrt->dump.active_wks`, store trigger data in `fwrt->dump.wks[idx].dump_data`, and queue `iwl_fw_error_dump_wk()` or run synchronously. The worker calls optional op-mode `dump_start`, stops recording, selects legacy or INI dump generation, restarts recording, sends dump-complete if requested by firmware capability/policy, frees trigger data, and clears the active bit.

State and persistence: state lives in `struct iwl_fw_runtime`: active work bits, selected debug config, non-collect windows, firmware version/error ids, D3 buffer, TXF iterator cursor, and paging DB. The file allocates transient vmalloc and scatterlist pages; persistent output is a devcoredump, not an on-disk file. It mutates trigger occurrence counters and may force NMI/reset handshake.

Dependencies/integration: depends on transport memory/PRPH/CSR access, firmware TLVs, runtime ops, sanitize ops, debug TLV infrastructure, device-family tables, DMA sync, workqueues, and `dev_coredumpsg()`. `debugfs.c`, op-mode error paths, and INI timepoints call into it.

Risks/test signals: highest-risk areas are length accounting before flexible-array writes, endian conversions, concurrent dump work slots, device-access failures, dead-bus checks, region policy filtering, and sanitize coverage for privacy-sensitive memory. Test signals include forced user dumps, firmware assert dumps, INI timepoint dumps, monitor-only dumps, paging-enabled images, D3 transitions, multi-LMAC FIFO sizes, dump-complete command support, and devcoredump parser compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dbg.c -->
