# Research: subset-b-004398

Work item: `subset-b-004398`

This grouped report covers Chelsio `cxgb4` DCB, debugfs, ethtool, and FCoE support files. Each file section is bounded for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_dcb.c

## Purpose

`cxgb4_dcb.c` implements Data Center Bridging and DCBX support for the Chelsio `cxgb4` Ethernet driver when `CONFIG_CHELSIO_T4_DCB` is enabled. It is the driver-side bridge between firmware DCB messages, the per-port `struct port_dcb_info` cache, and Linux DCB netlink operations exposed through `struct dcbnl_rtnl_ops`.

The file supports both firmware-managed DCBX and host-managed DCBX. Firmware events drive a small state machine, populate priority-group, priority-flow-control, and application-priority state, and then the DCBNL callbacks translate Linux CEE/IEEE requests into Chelsio firmware mailbox reads/writes.

## Important APIs, Types, And Functions

- `dcb_ver_array[]` maps firmware DCB version ids to log strings. It is exported via the header for diagnostics such as debugfs DCB information.
- `cxgb4_dcb_state_init()` clears a port's `struct port_dcb_info`, preserves a previously selected DCB version, and moves the state to `CXGB4_DCB_STATE_START`.
- `cxgb4_dcb_version_init()` defaults the per-port DCBX version request to `FW_PORT_DCB_VER_AUTO`.
- `cxgb4_dcb_reset()` removes registered DCB application mappings and reinitializes DCB state, typically after link-down or firmware de-sync.
- `cxgb4_dcb_state_fsm()` is the central state machine. Inputs are firmware disabled, firmware enabled, firmware incomplete, and firmware all-synced events. It transitions among start, host, firmware-incomplete, and firmware-all-synced states and fires `linkwatch_fire_event()` when externally visible DCB state changes.
- `cxgb4_dcb_handle_fw_update()` consumes `struct fw_port_cmd` DCB payloads from firmware. Control messages drive the FSM; data messages update PGID, PGRATE/TSA, PRIORATE, PFC, and application-priority caches.
- `cxgb4_dcb_ops` is the exported DCBNL operation table. It wires IEEE callbacks (`ieee_getets`, `ieee_getpfc`, `ieee_getapp`, `ieee_setapp`, peer ETS/PFC) and CEE callbacks (`getpgtccfg*`, `setpgtccfg*`, `getpfccfg`, `setpfccfg`, app table, peer app table, peer PG/PFC).
- The internal helpers `INIT_PORT_DCB_*_CMD()` are used throughout to form `FW_PORT_CMD` mailbox commands for local, peer, sync, and write DCB actions.
- `bitswap_1()` from the header is used to convert firmware PFC bit ordering to the IEEE/CEE representation expected by the kernel.

## Control Flow

Initialization starts in the main driver by calling `cxgb4_dcb_version_init()` and `cxgb4_dcb_state_init()` for each netdev/port. At this point the port has no active negotiated DCB information.

Firmware DCB control updates enter through `cxgb4_dcb_handle_fw_update()`. For `FW_PORT_DCB_TYPE_CONTROL`, the code decodes the `ALL_SYNCD` bit into either `CXGB4_DCB_INPUT_FW_ALLSYNCED` or `CXGB4_DCB_INPUT_FW_INCOMPLETE`. If the current requested version is not unknown, it also reads the running firmware DCB version from `dcb_version_to_app_state`, accepts CEE 1.01 or IEEE, logs the negotiated version, and marks unknown on mismatch. The state machine then updates the per-port state.

Non-control firmware DCB updates are rejected if the port is still in `START` or host-managed state. Otherwise the switch on firmware DCB type updates the per-port cache:

- `FW_PORT_DCB_TYPE_PGID` stores the firmware priority-group map and marks `CXGB4_DCB_FW_PGID`.
- `FW_PORT_DCB_TYPE_PGRATE` stores supported traffic classes, per-PG bandwidth, TSA values, and may fake IEEE sync once PGID is already known.
- `FW_PORT_DCB_TYPE_PRIORATE` stores strict priority rates.
- `FW_PORT_DCB_TYPE_PFC` stores PFC enablement and max PFC TCs and may fake IEEE sync.
- `FW_PORT_DCB_TYPE_APP_ID` translates firmware selector/priority representation to `struct dcb_app`, registers it with either `dcb_ieee_setapp()` or `dcb_setapp()`, stores the firmware table entry in `dcb->app_priority[]`, and marks the app message bit.

DCBNL get paths either return cached state or issue firmware mailbox reads for fresh local/peer values. Priority-group callbacks read PGID and PGRATE, convert the firmware's reversed TC order where needed, and expose bandwidth/priority-type fields. PFC callbacks read or update the cached `pfcen` bitmap and use firmware write commands for changes. App callbacks search the firmware APP table, use empty protocol id as end-of-table, and translate CEE and IEEE selector/priority encodings.

DCBNL set paths mostly write firmware DCB subcommands. PGID/PGRATE updates read the current firmware table, update one nibble or bandwidth entry, then write back. PFC writes update the `FW_PORT_DCB_TYPE_PFC` payload and update the software cache only after firmware success. App writes locate an existing or empty table slot, emit `FW_PORT_DCB_TYPE_APP_ID`, optionally set `FW_PORT_CMD_APPLY_F` for host-managed state, and then register the app in the kernel DCB app table.

## State And Persistence

The durable in-memory state lives in `struct port_dcb_info` embedded in each `struct port_info`. It caches:

- FSM state and DCBNL capability mask.
- `enabled` flag visible through `getstate()`.
- received firmware message bitmap.
- negotiated DCBX version.
- PGID, PFC enable bitmap, supported TC counts, bandwidth rates, priority rates, TSA values.
- up to eight firmware application-priority entries.

Firmware is the persistent source of truth for actual DCB configuration. The driver cache is reset on `cxgb4_dcb_reset()` and repopulated from firmware updates or explicit mailbox reads. Link transitions matter: `__cxgb4_setapp()` rejects app writes when carrier is down because DCB info is discarded on link-up. Host-managed writes set `FW_PORT_CMD_APPLY_F` to push changes immediately.

The Linux DCB app tables are also updated as side effects through `dcb_setapp()`, `dcb_ieee_setapp()`, `dcb_ieee_delapp()`, and `dcb_setapp()` with priority zero for cleanup. This means software-visible state spans both the Chelsio per-port cache and the kernel DCB app registry.

## Dependencies And Integration Points

- Requires `CONFIG_CHELSIO_T4_DCB`; otherwise the header provides no-op initialization.
- Depends on `cxgb4.h` for `struct adapter`, `struct port_info`, `netdev2pinfo()`, port/channel mapping, and firmware mailbox helpers.
- Uses Chelsio firmware APIs and constants from `t4fw_api.h`, especially `FW_PORT_CMD`, `FW_PORT_DCB_TYPE_*`, and DCB version/capability fields.
- Uses `t4_wr_mbox()` to synchronously read/write firmware DCB state.
- Integrates with Linux DCBNL through `struct dcbnl_rtnl_ops`.
- Uses `linkwatch_fire_event()` to notify the networking core when DCB sync state affects link-visible behavior.
- Uses kernel DCB app helpers (`dcb_setapp`, `dcb_ieee_setapp`, `dcb_ieee_getapp_mask`, `dcb_ieee_delapp`) to keep the OS registry aligned.
- Debug output is consumed by `cxgb4_debugfs.c` when `dcb_info` is enabled.

## Risks And Edge Cases

- Firmware DCB events received in `START` or `HOST` state are logged and ignored. If event ordering changes, the driver may fail to populate DCB state.
- Version mismatch handling logs a warning and sets version unknown; later code indexes `dcb_ver_array` by firmware-provided ids, so invalid firmware version values would be risky if they escape expected enum ranges.
- Several setter callbacks return `void` due to DCBNL API shape and can only log firmware failures; callers may not get precise failure propagation for PG/PFC changes.
- App table handling is capped at `CXGB4_MAX_DCBX_APP_SUPPORTED` eight entries and returns `-EBUSY` when full.
- IEEE app priority conversion uses `ffs(prio) - 1`; empty priority masks can produce `-1` if not guarded by successful firmware/kernel app lookup.
- DCB write paths depend on carrier state and firmware state; attempts during link transitions can return `-ENOLINK` or silently expose stale cached values until firmware refreshes.
- The code assumes firmware bit ordering for PFC differs from spec and corrects with `bitswap_1()` in some paths; inconsistent use would produce reversed priority reporting.

## Test Signals

Useful validation signals include:

- Build coverage with `CONFIG_CHELSIO_T4_DCB=y` and without it to confirm the header stubs and operation table references are correct.
- DCBNL queries via `dcbtool` or `lldptool` for CEE and IEEE modes, checking PG, PFC, app, peer app, and DCBX capability reporting.
- Firmware event injection or hardware link tests that cover `START -> FW_INCOMPLETE -> FW_ALLSYNCED`, de-sync back to incomplete, and host-managed mode.
- App table set/get/delete tests for ethertype and port selectors, including full-table behavior.
- Link down/up tests to confirm `cxgb4_dcb_reset()` clears app registrations and that firmware repopulates state.
- Debugfs `dcb_info` inspection for negotiated version, state, PG/PFC/app values, and message bit progression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_dcb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_dcb.h

## Purpose

`cxgb4_dcb.h` declares the Chelsio `cxgb4` DCB support contract. It defines DCB capability masks, firmware command-initialization macros, DCB state enums, firmware-message tracking bits, the per-port DCB cache structure, and the public DCB entry points used by the rest of the driver.

When `CONFIG_CHELSIO_T4_DCB` is disabled, the header collapses DCB initialization to a no-op and exposes `CXGB4_DCB_ENABLED false`, allowing common driver code to compile without DCB support.

## Important APIs, Types, And Constants

- `CXGB4_DCBX_FW_SUPPORT` combines CEE, IEEE, and `DCB_CAP_DCBX_LLD_MANAGED` for firmware-managed DCBX.
- `CXGB4_DCBX_HOST_SUPPORT` combines CEE, IEEE, and `DCB_CAP_DCBX_HOST` for host-managed DCBX.
- `CXGB4_MAX_PRIORITY` and `CXGB4_MAX_TCS` are aliases for `CXGB4_MAX_DCBX_APP_SUPPORTED`, currently eight.
- `INIT_PORT_DCB_CMD()` constructs a `struct fw_port_cmd` with operation, request/execution flag, port id, DCB action, and length. It is the common mailbox command initializer for the implementation.
- `INIT_PORT_DCB_READ_PEER_CMD()`, `INIT_PORT_DCB_READ_LOCAL_CMD()`, `INIT_PORT_DCB_READ_SYNC_CMD()`, and `INIT_PORT_DCB_WRITE_CMD()` specialize the generic initializer for firmware DCB read/write actions.
- `IEEE_FAUX_SYNC()` advances IEEE DCB state to all-synced when the firmware provides enough IEEE sub-state without a normal all-synced control transition.
- `enum cxgb4_dcb_state` describes per-port DCB state: start, host, firmware incomplete, firmware all-synced.
- `enum cxgb4_dcb_state_input` defines inputs accepted by the FSM.
- `enum cxgb4_dcb_fw_msgs` tracks which DCB data message types have been received: PGID, PGRATE, PRIORATE, PFC, APP_ID.
- `struct port_dcb_info` is the per-port cache used by DCBNL, debugfs, and firmware event handling.
- Public functions include `cxgb4_dcb_state_init()`, `cxgb4_dcb_version_init()`, `cxgb4_dcb_reset()`, `cxgb4_dcb_state_fsm()`, and `cxgb4_dcb_handle_fw_update()`.
- `cxgb4_dcb_ops` is the exported Linux DCBNL ops table.
- `bitswap_1()` reverses bits in a byte, used to convert firmware PFC priority bit ordering to the OS-visible representation.
- `dcb_ver_array[]` is declared for shared version-name reporting.

## Control Flow

The header is included from `cxgb4_dcb.c` and indirectly from common driver code through `cxgb4.h` integration. With DCB enabled, initialization code can call the declared state/version init routines, firmware event handling can call `cxgb4_dcb_handle_fw_update()`, and netdev setup can attach `cxgb4_dcb_ops` to expose DCBNL operations.

The command macros centralize mailbox command construction. Each call zeroes the command, fills `op_to_portid` with `FW_CMD_OP_V(FW_PORT_CMD)`, `FW_CMD_REQUEST_F`, either `FW_CMD_READ_F` or `FW_CMD_EXEC_F`, and the firmware port id, then fills `action_to_len16` with the DCB action and length. This avoids repeated open-coded firmware command setup in the implementation.

When DCB support is compiled out, only `cxgb4_dcb_state_init()` remains as an inline empty function. Code guarded by `CXGB4_DCB_ENABLED` or `CONFIG_CHELSIO_T4_DCB` should avoid referencing DCB-only declarations in that configuration.

## State And Persistence

`struct port_dcb_info` is the authoritative in-driver cache format. It persists for the life of a `struct port_info` and is reset/repopulated by the implementation. It stores both state-machine metadata and firmware-derived DCB content:

- `state`, `msgs`, `supported`, and `enabled`.
- `pgid`, `dcb_version`, `pfcen`, max PG/PFC TC counts.
- `pgrate[8]`, `priorate[8]`, and `tsa[8]`.
- `app_priority[8]`, each containing user priority map, selector field, and protocol id.

No on-disk persistence is defined here. Actual DCB configuration persists in firmware/hardware; this structure is the kernel runtime mirror.

## Dependencies And Integration Points

- Includes `<linux/netdevice.h>`, `<linux/dcbnl.h>`, and `<net/dcbnl.h>` for netdev and DCBNL types.
- Uses firmware command macros and constants from the broader `cxgb4` include graph, so this header expects to be included in contexts where `FW_PORT_CMD`, `FW_CMD_*`, `FW_LEN16`, and related fields are available.
- The fallback no-op path is controlled by `CONFIG_CHELSIO_T4_DCB`.
- `struct port_dcb_info` is embedded in `struct port_info`, linking this header to the main adapter/port object model.

## Risks And Edge Cases

- `CXGB4_MAX_PRIORITY` and `CXGB4_MAX_TCS` being aliases for the app-table size assumes all relevant DCB arrays are eight entries; changing app support without revisiting TC/priority semantics could introduce bounds bugs.
- `IEEE_FAUX_SYNC()` is a macro with side effects; callers must pass valid netdev and DCB pointers and understand it can trigger the FSM.
- `bitswap_1()` accepts `unsigned char` and returns `__u8`; callers must not use it for wider masks without truncation awareness.
- The disabled-DCB branch exposes only one no-op function. Any unguarded use of other DCB symbols will fail builds without `CONFIG_CHELSIO_T4_DCB`.

## Test Signals

- Compile-test with `CONFIG_CHELSIO_T4_DCB=y` and `n`.
- Static checks that every DCB mailbox command path uses the initializer macros and sets the expected sub-type before `t4_wr_mbox()`.
- Runtime DCB tests confirming `struct port_dcb_info` fields reported by debugfs match DCBNL outputs.
- Bit-order tests for `bitswap_1()` using representative PFC masks such as `0x80`, `0x01`, and mixed masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_dcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_debugfs.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_debugfs.h

## Purpose

`cxgb4_debugfs.h` declares the small shared interface for the `cxgb4` debugfs implementation. It provides the debugfs entry descriptor, the reusable `seq_tab` table abstraction, a hex conversion helper, and the public functions used by adapter setup and other driver modules to register debugfs files or open adapter memory views.

## Important APIs And Types

- `struct t4_debugfs_entry` describes one debugfs file: name, file operations, mode, and a small `data` byte that is added to the adapter pointer as `i_private`. The data byte is used to distinguish mailbox number, trace index, CIM queue id, or memory index.
- `struct seq_tab` stores a reusable table backing buffer for `seq_file` output. It contains a row formatter callback, row count, row width, header flag, and flexible-array row data.
- `hex2val()` converts a hexadecimal character to its numeric value using `isdigit()` and `tolower()`. Callers are expected to validate with `isxdigit()` first.
- `seq_open_tab()` allocates and initializes a `seq_tab` private buffer for table-style debugfs files.
- `t4_setup_debugfs()` creates the adapter's debugfs files.
- `add_debugfs_files()` registers an array of `struct t4_debugfs_entry` under an adapter debugfs root.
- `mem_open()` prepares memory-like debugfs file reads and flushes firmware cache state in the implementation.

## Control Flow

Driver setup calls `t4_setup_debugfs(adap)`. That implementation builds arrays of `struct t4_debugfs_entry` and calls `add_debugfs_files()`. Each entry's `data` byte becomes an offset from the adapter pointer in `debugfs_create_file()`, allowing one `file_operations` implementation to serve multiple mailbox, trace, or queue files.

Table-style debugfs implementations call `seq_open_tab()` from their open routines, fill `seq_tab->data` with hardware state, then rely on shared seq operations in the `.c` file to iterate rows and call the provided `show()` callback.

## State And Persistence

This header defines no global state. `struct seq_tab` instances are per-open seq private allocations and are freed by `seq_release_private()`. `struct t4_debugfs_entry` arrays are usually static in the implementation and describe registration metadata only.

## Dependencies And Integration Points

- Includes `<linux/export.h>` and relies on Linux VFS/debugfs/seq_file types supplied through surrounding includes.
- `struct adapter` is referenced but not defined here; consumers include this header in contexts where the main `cxgb4` adapter type is visible.
- `hex2val()` depends on ctype helpers being available to the translation unit.
- The functions declared here are implemented in `cxgb4_debugfs.c` and used by the main driver setup path and any module that contributes debugfs files.

## Risks And Edge Cases

- `hex2val()` does not reject non-hex characters. It must only be called after validation, as `rss_key_write()` does.
- The `data` field is only `unsigned char`, so it is suitable for small selectors but not large offsets.
- Pointer arithmetic on `(void *)adap + data` is a GNU C extension used by this driver; new users should preserve the local convention and keep offsets small and intentional.
- `seq_tab` row width and row count must match the amount of data filled by the open routine. A mismatch can produce misformatted output or out-of-bounds interpretation.

## Test Signals

- Compile-test all translation units including this header with debugfs enabled.
- Exercise at least one `seq_open_tab()` user per table shape to confirm header flag, row count, and width behavior.
- Validate `hex2val()` callers reject invalid characters before conversion.
- Confirm newly added `t4_debugfs_entry` users pass correct file modes and selector values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_ethtool.c

## Purpose

`cxgb4_ethtool.c` implements the ethtool operations for Chelsio `cxgb4` net devices. It exposes driver/firmware information, string sets, port and adapter statistics, register and EEPROM access, link mode and FEC configuration, pause and coalescing settings, ring sizing, RSS indirection and hash fields, n-tuple filter management, firmware/PHY/boot flashing, timestamp information, debug dumps, module EEPROM access, private flags, and offline loopback self-test support.

It is the main bridge between generic Linux ethtool requests and the driver's adapter, port, SGE, firmware, filter, cudbg, and hardware access helpers.

## Important APIs, Types, And Functions

- String and count tables: `stats_strings`, `adapter_stats_strings`, `loopback_stats_strings`, `cxgb4_priv_flags_strings`, `cxgb4_selftest_strings`, and `get_sset_count()`.
- Basic info: `get_drvinfo()`, `get_regs_len()`, `get_regs()`, `get_eeprom_len()`, `get_msglevel()`, `set_msglevel()`.
- Statistics: `collect_sge_port_stats()`, `collect_adapter_stats()`, and `get_stats()`.
- Link and media mapping: `from_fw_port_mod_type()`, `speed_to_fw_caps()`, `fw_caps_to_lmm()`, `lmm_to_fw_caps()`, `get_link_ksettings()`, and `set_link_ksettings()`.
- FEC translation: `fwcap_to_eth_fec()`, `cc_to_eth_fec()`, `eth_to_cc_fec()`, `get_fecparam()`, `set_fecparam()`.
- Pause/ring/coalesce: `get_pauseparam()`, `set_pauseparam()`, `get_sge_param()`, `set_sge_param()`, `set_rx_intr_params()`, `set_adaptive_rx_setting()`, `set_dbqtimer_tick()`, `set_dbqtimer()`, `set_dbqtimer_tickval()`, `set_coalesce()`, `get_coalesce()`.
- EEPROM: `eeprom_rd_phys()`, `eeprom_wr_phys()`, `get_eeprom()`, `set_eeprom()` with `EEPROM_MAGIC`.
- Flashing: `cxgb4_validate_fw_image()`, `cxgb4_validate_phy_image()`, `cxgb4_validate_boot_image()`, `cxgb4_validate_bootcfg_image()`, `cxgb4_ethtool_get_flash_region()`, `cxgb4_ethtool_flash_region()`, `set_flash()`.
- RSS: `get_rss_table_size()`, `get_rss_table()`, `set_rss_table()`, `cxgb4_get_rxfh_fields()`.
- Filters: `cxgb4_init_ethtool_filters()`, `cxgb4_cleanup_ethtool_filters()`, `cxgb4_get_filter_entry()`, `cxgb4_fill_filter_rule()`, `cxgb4_ntuple_get_filter()`, `cxgb4_ntuple_set_filter()`, `cxgb4_ntuple_del_filter()`, `get_rxnfc()`, `set_rxnfc()`.
- Debug dumps: `set_dump()`, `get_dump_flag()`, `get_dump_data()`.
- Module EEPROM: `cxgb4_get_module_info()` and `cxgb4_get_module_eeprom()`.
- Private flags and self-test: `cxgb4_get_priv_flags()`, `cxgb4_set_priv_flags()`, `cxgb4_lb_test()`, `cxgb4_self_test()`.
- `cxgb_ethtool_ops` is the operation table installed by `cxgb4_set_ethtool_ops()`.

## Control Flow

During netdev setup, `cxgb4_set_ethtool_ops(netdev)` installs `cxgb_ethtool_ops`. Ettool callbacks then enter this file with a `struct net_device *`, recover `struct port_info` and `struct adapter`, and delegate to common-code helpers or update driver state.

Information and statistics paths are mostly read-only. `get_drvinfo()` copies driver, bus, firmware, TP, and expansion-ROM versions. `get_stats()` first asks hardware for port stats with baseline offsets, then appends aggregated SGE queue counters, adapter doorbell/write-combine counters, the port id, and loopback stats. `get_regs()` returns a full hardware register dump using the adapter-version tag.

Link configuration paths translate between ethtool link masks and firmware capability bits. `get_link_ksettings()` refreshes port info if the netdev is down, fills supported/advertising/lp masks, speed, duplex, autoneg, MDIO fields, and port type. `set_link_ksettings()` validates full duplex, maps either a forced speed or an advertised mode mask into firmware capabilities, saves the old link config, calls `t4_link_l1cfg()`, and restores old config on firmware failure.

Coalescing combines RX interrupt settings and TX SGE doorbell queue timers. RX holdoff changes are applied to each response queue. TX doorbell timer tick is global to the adapter, so `set_dbqtimer_tickval()` records timer values for all ports, changes the global tick, rereads dependent timer values, and then reapplies closest timer values to all ports.

EEPROM access translates physical offsets to per-PF VPD offsets. Reads allocate an EEPROM-sized buffer and read aligned words. Writes require `EEPROM_MAGIC`, enforce PF partition bounds for non-PF0, perform read-modify-write for unaligned endpoints, disable EEPROM write protection, write words, and re-enable protection on success.

Flashing loads firmware data by name through `request_firmware()`. If the request targets all regions, it repeatedly identifies each image by signature and size, flashes the specific region, advances by the image size, and stops on errors. Explicit region flashing dispatches directly to firmware, PHY, boot, or bootcfg loaders. Firmware flashing requires the cxgb4 driver to be the PCIe firmware master when a master is already valid.

RSS and filter control are stateful. RSS table changes require a supported hash function/key combination and `CXGB4_FULL_INIT_DONE`, update `pi->rss[]`, and push to hardware. Ettool n-tuple filters use an allocated per-port bitmap and location-to-TID array. Insert validates initialization, range, and duplicate location, converts ethtool flow rule into a Chelsio filter specification through `cxgb4_flow_rule_replace()`, records the adjusted TID, and marks the bitmap. Delete validates location, fetches the filter, converts absolute TID to the appropriate namespace, destroys the flow rule, and clears bookkeeping.

Debug dump control stores the requested cudbg flag and computed length in `adapter->eth_dump`; data collection later calls `cxgb4_cudbg_collect()`. Module EEPROM reads use firmware I2C helpers and choose SFF-8079, SFF-8472, SFF-8436, or SFF-8636 metadata based on port/module type and transceiver bytes.

## State And Persistence

Persistent runtime state modified by ethtool includes:

- `adapter->msg_enable` for driver message level.
- Per-port `struct link_config` fields: speed caps, advertised caps, autoneg, requested pause, requested FEC.
- SGE queue sizes before full initialization; ring size changes are rejected after `CXGB4_FULL_INIT_DONE`.
- RX response queue interrupt parameters and adaptive RX flags.
- Adapter global SGE DBQ timer tick and per-Ethernet-TXQ timer indices.
- EEPROM/VPD contents and flash/firmware/PHY/boot images in nonvolatile adapter storage.
- `pi->rss[]` and hardware RSS indirection table.
- `adapter->ethtool_filters`, including per-port bitmaps, location arrays, and in-use counts.
- `adapter->eth_dump` cudbg flag/length/version.
- `adapter->eth_flags` and `pi->eth_flags` private flags.

Some values are hardware-derived snapshots rather than software state, such as register dumps, stats, module EEPROM contents, and firmware versions.

## Dependencies And Integration Points

- Includes Linux firmware and MDIO headers plus `cxgb4.h`, `t4_regs.h`, `t4fw_api.h`, `cxgb4_cudbg.h`, `cxgb4_filter.h`, and `cxgb4_tc_flower.h`.
- Uses Linux ethtool core types and helpers, including link ksettings, RSS parameters, FEC parameters, EEPROM, flash, RX flow rules, timestamp info, and dump APIs.
- Integrates with Chelsio common-code functions for hardware register reads, firmware mailbox operations, link L1 configuration, EEPROM/VPD access, firmware upgrades, I2C reads, RSS writes, SGE timers, cudbg collection, and self-test packet loopback.
- Filter support bridges ethtool n-tuple flow rules into the driver's tc-flower/filter path using `cxgb4_flow_rule_replace()` and `cxgb4_flow_rule_destroy()`.
- Optional TLS-device counters are included in stats when `CONFIG_CHELSIO_TLS_DEVICE` is enabled.

## Risks And Edge Cases

- Flashing and EEPROM writes are high-impact operations. Incorrect firmware region detection, bad image sizes, or power loss can leave adapter firmware/storage inconsistent.
- `cxgb4_validate_fw_image()` reads at a fixed signature offset; callers must ensure firmware data is large enough before validation to avoid short-buffer assumptions.
- `set_eeprom()` disables write protection and only re-enables it on the no-error write path; failures after disabling protection are a sensitive area to audit.
- `set_link_ksettings()` and `set_fecparam()` mutate `link_config` before firmware calls and restore on failure. Any future side effects before restore must preserve rollback semantics.
- Ring size changes are only allowed before full initialization; user expectations may differ if they attempt runtime resizing.
- RSS table changes require the interface to have completed full initialization at least once and reject unsupported key/hash-function changes.
- `get_rxnfc()` assumes `adap->ethtool_filters` is valid for rule-count paths; initialization failure or unsupported filters must be handled by setup.
- Filter bookkeeping must stay synchronized with the underlying filter tables; failures after hardware insertion but before bitmap update, or vice versa, would leak or hide rules.
- Coalescing DBQ tick is adapter-global; changing it for one netdev changes timing scale for all ports.

## Test Signals

Recommended signals include:

- `ethtool -i`, `-S`, `-d`, `-g`, `-c`, `-k`, `--show-fec`, `--show-pause`, and module EEPROM reads on supported hardware.
- Link mode set tests for autoneg on/off, unsupported speeds, full-duplex validation, FEC changes, and firmware rejection rollback.
- Ring parameter tests before and after full initialization to verify `-EBUSY` behavior.
- Coalesce tests covering RX usecs/count, adaptive RX, DBQ timer tick/value changes, and multi-port preservation.
- EEPROM read/write tests with magic validation, unaligned writes, PF partition bounds, and write-protect behavior.
- Flash tests with valid individual images, all-region concatenated images, bad signatures, non-master PF, and firmware-loader failures.
- RSS indirection get/set tests, including unsupported key/hash changes.
- Ettool n-tuple insert/get/delete tests for IPv4/IPv6 TCP/UDP, duplicate locations, out-of-range locations, and cleanup on adapter teardown.
- Cudbg dump set/get/data collection tests for buffer sizing and no-dump `-ENOENT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_fcoe.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_fcoe.c

## Purpose

`cxgb4_fcoe.c` implements the Chelsio `cxgb4` FCoE offload control helpers when `CONFIG_CHELSIO_T4_FCOE` is enabled. It validates supported FCoE SOF/EOF frame markers and toggles netdev feature bits for FCoE CRC offload and FCoE MTU handling.

The implementation is small but sits on sensitive boundaries: it changes advertised netdev capabilities and validates Fibre Channel over Ethernet framing before offload.

## Important APIs And Functions

- `cxgb_fcoe_sof_eof_supported(struct adapter *adap, struct sk_buff *skb)` reads the FCoE header at `skb_network_header(skb)`, accepts only `FC_SOF_I3` or `FC_SOF_N3`, copies the EOF byte from the final four bytes of the skb, and accepts only `FC_EOF_N` or `FC_EOF_T`.
- `cxgb_fcoe_enable(struct net_device *netdev)` enables FCoE offload features for a port. It rejects T4 chips and adapters that have not completed full initialization, sets `NETIF_F_FCOE_CRC` in `features` and `vlan_features`, enables `netdev->fcoe_mtu`, calls `netdev_features_change()`, and marks `pi->fcoe.flags` with `CXGB_FCOE_ENABLED`.
- `cxgb_fcoe_disable(struct net_device *netdev)` requires the enabled flag, clears the flag, removes FCoE CRC from `features` and `vlan_features`, disables `fcoe_mtu`, and calls `netdev_features_change()`.

## Control Flow

The enable path starts from a netdev, recovers `struct port_info` and `struct adapter`, rejects unsupported chips with `is_t4(adap->params.chip)`, rejects incomplete adapter initialization, logs enablement, updates netdev feature masks, notifies the networking core, and records the runtime enabled bit.

The disable path recovers the same objects, rejects disable when the feature was not enabled, logs disablement, clears the runtime flag, removes feature bits, disables FCoE MTU support, and notifies the networking core.

The SOF/EOF validation path is used on an skb containing an FCoE frame. It reads the SOF byte directly from the FCoE header, then copies one byte from `skb->len - 4` to inspect EOF. Unsupported markers produce device error logs and return `false`; accepted markers return `true`.

## State And Persistence

The only driver-owned persistent state is `pi->fcoe.flags`, specifically `CXGB_FCOE_ENABLED`. The netdev state also persists while enabled:

- `netdev->features` includes `NETIF_F_FCOE_CRC`.
- `netdev->vlan_features` includes `NETIF_F_FCOE_CRC`.
- `netdev->fcoe_mtu` is set.

There is no on-disk persistence. State is runtime-only and tied to the netdev/adapter lifetime.

## Dependencies And Integration Points

- Compiled only under `CONFIG_CHELSIO_T4_FCOE`.
- Includes `<scsi/fc/fc_fs.h>` for Fibre Channel SOF/EOF constants and `<scsi/libfcoe.h>` for FCoE definitions.
- Includes `cxgb4.h` for adapter, port, feature flags, chip helpers, and netdev private data.
- Integrates with Linux netdev feature negotiation via `netdev_features_change()`.
- Depends on `CXGB4_FULL_INIT_DONE` being set before enabling offload.

## Risks And Edge Cases

- `cxgb_fcoe_sof_eof_supported()` assumes the skb is long enough and laid out such that `skb_network_header()` points to an FCoE header and `skb->len - 4` contains EOF. Callers must ensure frame validity before invoking it.
- Enable rejects T4 chips but permits later chips only after full init; error reporting is simply `-EINVAL`, so callers need context to distinguish unsupported chip from initialization state.
- Directly mutating `netdev->features` and `vlan_features` must remain synchronized with the driver's feature-fixup paths elsewhere in the driver.
- Disable returns `-EINVAL` if not currently enabled, which makes repeated disable non-idempotent.

## Test Signals

- Build coverage with `CONFIG_CHELSIO_T4_FCOE=y` and disabled.
- Enable tests on T4 and non-T4 chips, before and after full initialization.
- Feature verification after enable/disable through `ethtool -k` or direct netdev inspection for FCoE CRC and VLAN feature changes.
- skb validation tests for accepted SOF/EOF pairs, unsupported SOF, unsupported EOF, and too-short/malformed skb handling by callers.
- Repeated enable/disable sequencing tests to confirm flag and netdev feature state stay consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_fcoe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_fcoe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_fcoe.h

## Purpose

`cxgb4_fcoe.h` declares the optional FCoE offload state and helpers for the Chelsio `cxgb4` driver. Its contents are only present when `CONFIG_CHELSIO_T4_FCOE` is enabled.

## Important APIs, Types, And Constants

- `CXGB_FCOE_TXPKT_CSUM_START` and `CXGB_FCOE_TXPKT_CSUM_END` define checksum offset constants used by FCoE transmit packet handling elsewhere in the driver.
- `CXGB_FCOE_ENABLED` is the bit stored in `struct cxgb_fcoe::flags` to indicate runtime enablement.
- `struct cxgb_fcoe` currently contains an 8-bit `flags` field.
- `cxgb_fcoe_enable()` and `cxgb_fcoe_disable()` toggle FCoE offload features on a netdev.
- `cxgb_fcoe_sof_eof_supported()` validates FCoE SOF/EOF markers for an skb.

## Control Flow

When FCoE support is enabled in the kernel configuration, `struct port_info` can embed or reference `struct cxgb_fcoe` and other driver paths can call the declared helpers. When support is disabled, the header contributes no state or function prototypes, so all call sites must be configuration-guarded.

## State And Persistence

The only state defined here is `struct cxgb_fcoe::flags`. It is runtime-only and currently uses `CXGB_FCOE_ENABLED` to track whether netdev FCoE offload features have been enabled.

The checksum constants are compile-time protocol/layout constants, not runtime state.

## Dependencies And Integration Points

- Controlled by `CONFIG_CHELSIO_T4_FCOE`.
- Uses `struct net_device`, `struct adapter`, and `struct sk_buff` types from the broader driver/kernel include context.
- Implemented by `cxgb4_fcoe.c`.
- Integrates with netdev feature flags and FCoE skb processing paths elsewhere in `cxgb4`.

## Risks And Edge Cases

- Because the disabled configuration does not provide stubs, unguarded callers will fail to compile when FCoE is off.
- `flags` is a `u8`; future additions should remain within byte-width flags or change the type deliberately.
- The checksum offset constants must stay aligned with the hardware transmit descriptor/FCoE header layout expected by other source files.

## Test Signals

- Compile-test with `CONFIG_CHELSIO_T4_FCOE=y` and `n`.
- Static search for unguarded FCoE helper calls in non-FCoE builds.
- Runtime enable/disable tests should observe `CXGB_FCOE_ENABLED` and netdev feature bits changing together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_fcoe.h -->
