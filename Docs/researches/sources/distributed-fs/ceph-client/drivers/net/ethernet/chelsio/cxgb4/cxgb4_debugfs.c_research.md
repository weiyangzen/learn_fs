# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_debugfs.c

## Purpose

`cxgb4_debugfs.c` creates and implements the debugfs surface for Chelsio `cxgb4` adapters. It exposes hardware and firmware diagnostics for CIM logic analyzers, TP logic analyzer data, PM stats, transmit rates, congestion tables, clocks, firmware logs, mailbox logs, MPS tracing and TCAM, RSS configuration, DCB state, SGE queue state, adapter memory windows, TID allocation, memory layout, crypto/TLS counters, and TP protocol stats.

Most entries are read-only diagnostics, but selected entries allow privileged debug mutations such as writing raw firmware mailbox commands, configuring MPS trace filters, changing the RSS key, clearing PM stats, setting the TP LA mask, updating the blocked freelist bitmap, and toggling boolean debug knobs.

## Important APIs, Types, And Functions

- `seq_open_tab()` and `struct seq_tab` implement a reusable `seq_file` table abstraction used by many fixed-row hardware dumps.
- `seq_tab_trim()` shrinks a table after a hardware read returns fewer rows than allocated.
- CIM readers: `cim_la_open()`, `cim_pif_la_open()`, `cim_ma_la_open()`, `cim_qcfg_show()`, `cim_ibq_open()`, and `cim_obq_open()` read CIM logic analyzers and queues.
- TP/ULP/PM diagnostics: `tp_la_open()`, `tp_la_write()`, `ulprx_la_open()`, `pm_stats_show()`, `pm_stats_clear()`, `tx_rate_show()`, `cctrl_tbl_show()`, `clk_show()`.
- Firmware logs: `devlog_open()` snapshots firmware device log memory under `win0_lock`; `devlog_show()` formats entries. `mboxlog_show()` displays the driver's mailbox command log.
- Mailbox raw access: `mbox_show()` reads mailbox registers; `mbox_write()` accepts eight 64-bit words and hands mailbox ownership to firmware.
- MPS tracing: `mps_trc_show()` displays a trace filter; `mps_trc_write()` parses the trace-filter command language and calls `t4_set_trace_filter()`.
- Memory and flash readers: `mem_open()`, `mem_read()`, `flash_read()`, and `add_debugfs_mem()` expose adapter memory regions and serial flash.
- MPS TCAM: `mps_tcam_show()` decodes TCAM entries, VLAN/VNI fields, replication maps, PF/VF/port validity, and T6-specific fields.
- RSS diagnostics: `rss_open()`, `rss_config_show()`, `rss_key_show()`, `rss_key_write()`, `rss_pf_config_open()`, and `rss_vf_config_open()`.
- DCB diagnostics: `dcb_info_show()` iterates ports and prints DCB state, version, message bits, PG/PFC/app cache fields when `CONFIG_CHELSIO_T4_DCB` is enabled.
- SGE diagnostics: `sge_qinfo_show()`, `sge_queue_entries()`, and `sge_qinfo_open()` report Ethernet, mirror, mqprio, offload, control, and firmware event queues.
- `t4_setup_debugfs()` is the top-level registration function. It creates common files, T5+ files, memory-region files, flash, and boolean knobs.
- `add_debugfs_files()` is exported to add arrays of `struct t4_debugfs_entry`.

## Control Flow

At adapter setup time, the main driver calls `t4_setup_debugfs(adap)`. The function creates a static list of adapter debugfs files under `adap->debugfs_root`, conditionally adds DCB and IPv6 CLIP files, adds T5+ CIM OBQ files for non-T4 chips, scans memory enable registers to add EDC/MC/HMA memory files with file sizes, creates a flash file sized to `adap->params.sf_size`, and creates `use_backdoor` and `trace_rss` boolean nodes.

For most read-only entries, open allocates either a `seq_tab` buffer or a single `seq_file` context, reads the relevant hardware/firmware state into memory, and the `show` callback formats it row by row. Examples include CIM LA snapshots, PIF/MA LA data, ULPRX LA data, RSS indirection table, PF/VF RSS configuration, device log snapshots, and SGE queue views.

Some entries read live registers on each show call rather than snapshotting into a table. Examples include clock/timer information, congestion control tables, resource summaries, memory layout, TID usage, crypto stats, TP stats, and sensors.

Debug write paths follow narrow parser/control flows:

- `tp_la_write()` copies up to 31 bytes, parses an unsigned mask value, bounds it to 16 bits, shifts into the upper half of `TP_DBG_LA_CONFIG_A`, and updates `adap->params.tp.la_mask`.
- `pm_stats_clear()` writes zero to PM RX/TX stat config registers and returns the input count.
- `mbox_write()` requires exactly eight hexadecimal 64-bit words plus newline, verifies mailbox owner is the physical layer, writes mailbox data flits, then sets valid/firmware-owner bits.
- `mps_trc_write()` copies at most 1 KiB, supports `disable` or a trace specification with `rxN`, `txN`, `loopbackN`, `qid=`, `snaplen=`, `minlen=`, `not`, and up to two pattern/mask/anchor expressions, validates alignment and field bounds, updates RSS trace control registers, and calls `t4_set_trace_filter()`.
- `rss_key_write()` accepts a 40-byte hex RSS key, parses it into ten 32-bit words in reverse display order, and calls `t4_write_rss_key()`.
- `blocked_fl_write()` parses a userspace bitmap into a temporary bitmap and copies it into `adap->sge.blocked_fl`.

## State And Persistence

Most file state is transient and allocated per open. `seq_open_tab()` embeds a private table buffer in the seq file; device log open snapshots the firmware log into a private buffer; memory and flash files rely on file size and `private_data` to encode adapter plus memory index.

Persistent or semi-persistent runtime state touched by this file includes:

- Hardware registers and firmware state read through `t4_*` helpers.
- `adap->params.tp.la_mask`, modified by `tp_la_write()`.
- PM RX/TX stat configuration registers, cleared by `pm_stats_clear()`.
- Firmware mailbox registers, modified by `mbox_write()`.
- MPS trace filter hardware and `adap->trace_rss`, used by trace show/write.
- RSS secret key in hardware, modified by `rss_key_write()`.
- `adap->sge.blocked_fl`, modified by `blocked_fl_write()`.
- `adap->use_bd` and `adap->trace_rss` boolean debugfs knobs.

No disk persistence is implemented. State either reflects hardware/firmware at read time, per-open snapshots, or driver runtime fields.

## Dependencies And Integration Points

- Includes Linux debugfs, seq_file, string helper, sort, and ctype APIs.
- Depends heavily on Chelsio common-code helpers: `t4_cim_read*`, `t4_tp_read_la`, `t4_ulprx_read_la`, `t4_pmtx_get_stats`, `t4_pmrx_get_stats`, `t4_get_chan_txrate`, `t4_read_cong_tbl`, `t4_memory_rw`, `t4_read_flash`, `t4_get_trace_filter`, `t4_set_trace_filter`, `t4_read_rss*`, `t4_write_rss_key`, `t4_query_params`, `t4_get_*_stats`, and many register macros.
- Integrates with `clip_tbl`, `l2t`, `cudbg`, crypto/TLS/IPsec, DCB, mqprio, and ULD queue state when those features are compiled/enabled.
- Uses `win0_lock` for adapter memory-window reads in device log and memory dump paths and `stats_lock` for TP stats.
- Uses `uld_mutex`, per-port `vi_mirror_mutex`, and mqprio mutexes to enumerate queue state without racing higher-level queue lists.
- Exposes entries under the adapter's debugfs root created by the core driver.

## Risks And Edge Cases

- Debugfs is privileged but powerful. `mbox_write()` can send arbitrary firmware mailbox commands, and trace/RSS/debug knobs can materially alter hardware behavior.
- Several diagnostic paths assume hardware/firmware access is healthy; surprise device removal or firmware failure can surface as register/mailbox errors.
- `mboxlog_show()` intentionally does not lock the mailbox log, so output may contain partially updated entries.
- `devlog_show()` prints firmware-provided format strings with kernel `seq_printf()`. The code assumes firmware format strings are compatible with kernel formatting and parameters.
- `mps_trc_write()` has complex parsing and alignment constraints; invalid anchors, masks longer/shorter than data, too many splits, out-of-range ports, or oversized input return errors.
- Memory and flash reads allocate buffers proportional to requested count or use fixed chunks; very large user reads depend on VFS/read chunking and allocation success.
- `add_debugfs_files()` encodes small integer data by pointer arithmetic on `struct adapter *`; this is a common local idiom but depends on only low offset values being used.
- Many show functions contain chip-version-specific paths. New chip support must update both register choices and output decoding.

## Test Signals

Useful validation signals include:

- Build coverage across T4/T5/T6 feature combinations, including DCB, IPv6, TLS device, inline IPsec, and mqprio.
- Mount debugfs on hardware or emulation and verify every file in `t4_debugfs_files` opens without kernel warnings.
- Read-only smoke tests for CIM LA, devlog, mboxlog, mps_tcam, RSS config, SGE qinfo, meminfo, tids, crypto, and TP stats.
- Parser tests through debugfs writes: invalid and valid `traceN` commands, valid 40-byte RSS keys, invalid RSS key characters/lengths, valid/invalid blocked freelist bitmaps, and TP LA mask bounds.
- Firmware-error tests where mailbox reads fail, confirming show/open paths return errors without leaking seq private buffers.
- Lockdep/KASAN/KCSAN runs while queues, DCB, mqprio, ULDs, and mirror VIs are being created/destroyed and `sge_qinfo` is read.
