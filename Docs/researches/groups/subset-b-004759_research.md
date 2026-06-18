# subset-b-004759 research

Grouped research for the ath6kl core/debug/HIF/HTC boundary. Each section is wrapped for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/core.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/core.h

## Purpose
`core.h` is the central ath6kl driver contract. It collects firmware naming/version constants, firmware capability flags, hardware parameter tables, driver state enums, per-VIF state, station/aggregation/key/cookie structures, the main `struct ath6kl`, and prototypes exported across core, cfg80211, WMI, HTC, HIF, aggregation, recovery, and diagnostic code. It is not an implementation file; its main behavioral importance is defining which state is shared and which locks/queues protect it.

## Important APIs, types, and functions
Key constants include firmware API names (`fw-2.bin` through `fw-5.bin`), AR6003/AR6004 firmware paths and board-data paths, receive buffer sizes, cookie limits, WMI timeout values, scan/listen defaults, and configuration flags such as `ATH6KL_CONF_ENABLE_11N`, `ATH6KL_CONF_ENABLE_TX_BURST`, and `ATH6KL_CONF_UART_DEBUG`. `enum ath6kl_fw_capability` defines the negotiated firmware feature bitmap, including P2P, scheduled scan, WOW multicast filtering, heartbeat polling, 64-bit rates, endpoint mapping, and checksum limitations.

The major state types are `struct ath6kl_vif`, `struct ath6kl`, `struct ath6kl_sta`, `struct ath6kl_cookie`, `struct target_stats`, `struct ath6kl_bmi`, `struct ath6kl_mbox_info`, RX aggregation structures (`aggr_info`, `aggr_info_conn`, `rxtid`), and key material structures. `ath6kl_vif_from_wdev()`, `ath6kl_priv()`, and `ath6kl_get_hi_item_addr()` are small helper APIs. The prototypes at the bottom define the cross-file integration surface for init/cleanup, WMI events, cfg80211 VIF stop, HTC RX/TX callbacks, diagnostics, firmware recovery, cookies, RX refills, and aggregation.

## Control flow and integration
`struct ath6kl` is the root object. Bus-specific code fills `hif_ops`, HTC attachment fills `htc_ops`, core initialization creates `htc_target` and `wmi`, and cfg80211/VIF paths hang interfaces from `vif_list`. WMI events update `ath6kl_vif` connection/scan/stats fields, while HTC invokes `ath6kl_rx()`, `ath6kl_tx_complete()`, `ath6kl_core_rx_complete()`, and `ath6kl_core_tx_complete()` for transport completion. Firmware boot and target diagnostic paths use `ath6kl_bmi`, firmware blobs in `ar->fw*`, mailbox information in `ar->mbox_info`, and target-type address helpers.

## State and persistence behavior
All state is in-memory kernel driver state. Persistence across operations is through `struct ath6kl` lifetime, per-VIF profiles, firmware capability bits, cached firmware image pointers, per-station AP-mode queues, aggregation reorder queues, target stats snapshots, and debug-only fields under `CONFIG_ATH6KL_DEBUG`. Locking contracts are partially documented: `ar->lock` protects AMSDU queues, cookies, and TX counters; `list_lock` protects VIF list membership; per-VIF `if_lock` protects stats/flags; `psq_lock` protects station power-save queues; `mcastpsq_lock` is noted as mostly redundant.

## Dependencies and integration points
The header depends on Linux netdevice, cfg80211, firmware loading, timers, semaphores, workqueues, SKBs, WMI, BMI, HTC, and target register definitions. It is included by most ath6kl implementation files and is therefore sensitive to include cycles; it also includes `htc.h`, while `hif.h` includes `core.h`, creating a tightly coupled local header graph.

## Risks and test signals
The main risks are stale lock documentation, shared mutable fields updated from workqueue/interrupt/cfg80211 contexts, firmware capability mismatches, and size/limit constants that must match target firmware contracts. Useful test signals include successful firmware boot across AR6003/AR6004 variants, VIF add/remove under concurrency, AP-mode station power-save queue behavior, aggregation reorder tests, suspend/WOW/resume transitions, heartbeat recovery, and exercising diagnostic read/write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/debug.c

## Purpose
`debug.c` implements ath6kl logging helpers, target-stat reads, firmware log collection, debugfs files, diagnostic register access, credit/endpoint statistic reporting, roam-table commands, and debugfs knobs for roaming, keepalive, disconnect timeout, QoS streams, scan interval, listen interval, and power-save parameters. Most of the file is compiled only with `CONFIG_ATH6KL_DEBUG`, but `ath6kl_printk()`, `ath6kl_info()`, `ath6kl_err()`, `ath6kl_warn()`, and `ath6kl_read_tgt_stats()` are always present and exported.

## Important APIs, types, and functions
`ath6kl_dbg()` and `ath6kl_dbg_dump()` gate debug output on `debug_mask` and always feed tracepoints. `ath6kl_read_tgt_stats()` serializes a WMI stats request with `ar->sem`, sets `STATS_UPDATE_PEND`, sends `ath6kl_wmi_get_stats_cmd()`, and waits on `ar->event_wq`. `ath6kl_debug_fwlog_event()` records fixed-size firmware log slots in `ar->debug.fwlog_queue`, limiting the queue to 20 entries. `ath6kl_debug_roam_tbl_event()` validates and stores firmware roam-table events and wakes waiters.

The debugfs file operations expose `tgt_stats`, SDIO-only `credit_dist_stats`, `endpoint_stats`, `fwlog`, `fwlog_block`, `fwlog_mask`, `reg_addr`, `reg_dump`, `lrssi_roam_threshold`, `reg_write`, `war_stats`, `roam_table`, `force_roam`, `roam_mode`, `keepalive`, `disconnect_timeout`, `create_qos`, `delete_qos`, `bgscan_interval`, `listen_interval`, and `power_params`. Initialization is split between `ath6kl_debug_init()` for early firmware logs and `ath6kl_debug_init_fs()` after cfg80211/wiphy debugfs exists.

## Control flow and integration
Read paths either format cached driver fields or actively query firmware. Stats and roam table reads issue WMI commands and wait for event handlers to clear pending bits. Firmware log reads pull pending firmware logs with `ath6kl_read_fwlogs()` then drain the SKB queue; `fwlog_block` waits on a completion if the queue is empty. Register dump uses `ath6kl_diag_read32()` over valid register ranges, with `reg_addr` selecting either a single register or all predefined ranges. Write paths parse user input, update local debug fields, and send WMI commands such as `set_roam_lrssi`, `force_roam`, `set_roam_mode`, `set_keepalive`, `disctimeout`, QoS create/delete, scan params, listen interval, and PM params.

## State and persistence behavior
Debug state persists in `ar->debug`: firmware log queue/completion/open flag, `fwlog_mask`, diagnostic read/write addresses, workaround counters, roam-table buffer and length, keepalive, and disconnect timeout. The firmware log queue is bounded and drops oldest entries. Roam table storage is dynamically resized. Many debugfs writes update driver fields only after or before sending WMI; those fields are in-memory and reset on driver teardown.

## Dependencies and integration points
The file depends on debugfs, SKBs, vmalloc, tracepoints, target register macros, WMI command/event paths, HTC endpoint and credit distribution structures, diagnostic HIF helpers, and cfg80211 wiphy debugfs. It observes `ar->hif_type` to expose SDIO credit distribution only for mailbox/SDIO-style operation.

## Risks and test signals
Risks include debugfs read buffers sized by estimates, blocking waits under `ar->sem`, firmware log single-open semantics without a lock around `fwlog_open`, user-triggered diagnostic register writes, and many debugfs controls that can alter firmware runtime behavior. Test signals include reading every debugfs file before and after association, blocked fwlog wakeup behavior, roam table timeout/error handling, invalid register address rejection, endpoint stat reset, WMI command error propagation, and cleanup waking blocked fwlog readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/debug.h

## Purpose
`debug.h` defines the ath6kl debug and logging interface. It declares debug mask bits, exported logging functions, target stats read API, workaround identifiers, debug-only hooks, and no-op stubs when `CONFIG_ATH6KL_DEBUG` is disabled.

## Important APIs, types, and functions
`enum ATH6K_DEBUG_MASK` assigns bit flags for credit, WLAN TX/RX, BMI, HTC, HIF, IRQ, WMI, generic trace, scatter, cfg80211, raw bytes, aggregation, SDIO, boot, suspend, USB, and recovery logs, plus `ATH6KL_DBG_ANY`. The always-available logging functions are `ath6kl_printk()`, `ath6kl_info()`, `ath6kl_err()`, and `ath6kl_warn()`. Debug builds add `ath6kl_dbg()`, `ath6kl_dbg_dump()`, register dump hooks, credit dump hooks, firmware log event ingestion, workaround accounting, roam-table event ingestion, debug state setters, init, debugfs init, and cleanup.

## Control flow and integration
Callers can use the same debug APIs regardless of build configuration. In debug builds, calls route to `debug.c` and tracepoints; in non-debug builds, most debug hooks compile away, while info/error/warn logging remains available. This allows HTC/HIF/core code to keep instrumentation calls without surrounding each call with `#ifdef`.

## State and persistence behavior
This header declares `extern unsigned int debug_mask`, which controls runtime debug verbosity in debug builds. It does not own storage itself. The no-op stubs avoid persistent debug state when `CONFIG_ATH6KL_DEBUG` is off.

## Dependencies and integration points
`debug.h` includes `hif.h` and `trace.h`, so users get access to HIF-visible register structures and tracepoint declarations. This contributes to ath6kl's tight local header coupling but keeps instrumentation declarations centralized.

## Risks and test signals
Risks are mostly interface-level: adding a debug hook must keep stub and real signatures identical, and debug mask bit reuse can break user expectations. Build tests should cover both `CONFIG_ATH6KL_DEBUG=y` and disabled configurations. Runtime tests should verify `debug_mask`-gated logs and tracepoints still work in debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/hif-ops.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/hif-ops.h

## Purpose
`hif-ops.h` is the inline dispatch layer for host interface operations. It wraps `ar->hif_ops` function pointers with consistent names and optional HIF debug logging, hiding whether the actual bus is SDIO, USB, or another implementation.

## Important APIs, types, and functions
The wrappers cover synchronous read/write (`hif_read_write_sync()`), asynchronous writes (`hif_write_async()`), IRQ enable/disable, scatter request get/add/enable/submit/cleanup, suspend/resume, diagnostic read/write, BMI read/write, power on/off, stop, pipe send, default pipe lookup, service-to-pipe mapping, and free pipe queue depth. These wrappers are the call surface consumed by HIF common code, HTC mailbox code, HTC pipe code, BMI, diagnostics, and core power management.

## Control flow and integration
All wrappers immediately dispatch through `ar->hif_ops`. Mailbox code uses read/write and scatter calls for SDIO mailbox traffic; pipe HTC uses pipe wrappers for USB-style message flow; diagnostics use `diag_read32`/`diag_write32`; firmware boot uses BMI calls; suspend and resume pass through cfg80211 WOW parameters. Because the wrappers do not null-check `ar->hif_ops` or individual callbacks, core initialization must attach a complete HIF ops table before these APIs are called.

## State and persistence behavior
This header owns no state. It is a stateless dispatch layer over the persistent `struct ath6kl` bus binding. The effects of calls persist in lower bus driver queues, device power state, interrupts, scatter pools, and firmware/target state.

## Dependencies and integration points
It includes `hif.h` for structures and `debug.h` for logging. This creates a simple but performance-sensitive inline layer used throughout ath6kl. Pipe-specific wrappers assume HIF implementations provide pipe primitives; mailbox paths rely on read/write/scatter primitives.

## Risks and test signals
Risks include missing bus callbacks, calling wrappers before HIF attach or after cleanup, and mismatched assumptions about synchronous versus asynchronous completion context. Test signals include boot over each supported HIF type, suspend/resume/WOW cycles, BMI firmware download, diagnostic reads, scatter transfer enable/fallback, and pipe send completions under backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/hif-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/hif.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/hif.c

## Purpose
`hif.c` implements common HIF support for mailbox-style ath6kl transports: asynchronous read/write completion dispatch, virtual scatter buffer copying, firmware crash dump handling, mailbox polling, RX interrupt masking, scatter request submission, interrupt processing, interrupt enable/disable, and initial mailbox block-size setup.

## Important APIs, types, and functions
`ath6kl_hif_rw_comp_handler()` receives bus async completion status, stores it in the `htc_packet`, and invokes the packet completion callback. `ath6kl_hif_submit_scat_req()` prepares read or write scatter requests, assigns mailbox addresses, copies virtual scatter bounce buffers when needed, dispatches through `ath6kl_hif_scat_req_rw()`, and updates synchronous read status. `ath6kl_hif_poll_mboxmsg_rx()` repeatedly reads the interrupt register table until mailbox data and a valid lookahead are present or timeout. `ath6kl_hif_intr_bh_handler()` loops through `proc_pending_irqs()` until no more work or communication timeout. `ath6kl_hif_unmask_intrs()`, `ath6kl_hif_mask_intrs()`, and `ath6kl_hif_setup()` manage chip-level and host-level interrupt state.

## Control flow and integration
The bottom-half interrupt handler reads target interrupt status registers, extracts mailbox lookahead, calls `ath6kl_htc_rxmsg_pending_handler()` to drain HTC messages, and then handles CPU, error, and counter interrupts. Counter debug interrupts trigger `ath6kl_hif_proc_dbg_intr()`, which clears the debug counter, dumps firmware crash registers through diagnostic reads, reads firmware logs, and notifies firmware recovery with `ATH6KL_FW_ASSERT`. RX flow control toggles mailbox data interrupts when HTC runs out of receive buffers.

## State and persistence behavior
Persistent state lives in `struct ath6kl_device`: shadow interrupt process/enable registers, lock, HTC context, and backpointer to `ar`. `ath6kl_hif_setup()` stores mailbox block size, verifies it is a power of two, and derives `target->block_mask` for mailbox padding. Interrupt enable shadows are updated under `dev->lock` and written to target registers. Scatter requests are owned by lower HIF pools and returned by callers.

## Dependencies and integration points
The file depends on target register addresses/macros, HIF ops wrappers, HTC RX pending handler, diagnostic helpers, firmware log reader, and recovery notification. It assumes its HIF implementation allows synchronous I/O in bottom-half processing context.

## Risks and test signals
Risks include timeout handling during target unresponsiveness, stale interrupt shadow state, mailbox lookahead zero/mismatch cases, race-sensitive RX interrupt masking, crash dump diagnostic read failure, and scatter bounce copy length correctness. Test signals include forced firmware assert, mailbox RX under buffer starvation, interrupt mask/unmask around start/stop, scatter read/write with virtual and real scatter, invalid block-size rejection, and stress RX that forces `chk_irq_status_cnt` rechecks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/hif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/hif.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/hif.h

## Purpose
`hif.h` defines the host interface contract and shared structures for ath6kl bus implementations. It includes mailbox address layout, request flag bits, scatter-gather limits, interrupt register layouts, `struct ath6kl_device`, and `struct ath6kl_hif_ops`.

## Important APIs, types, and functions
Important constants include mailbox block sizes, DMA buffer size, mailbox base/width/end addresses, extended mailbox and GMBOX ranges, SDIO async IRQ mode, scatter request limits, communication timeout, and combined HIF request flag macros such as `HIF_WR_ASYNC_BLOCK_INC`, `HIF_RD_SYNC_BLOCK_FIX`, and `HIF_WR_SYNC_BYTE_INC`. `struct bus_request` tracks a bus transaction or scatter request. `struct hif_scatter_req` describes multi-entry transfers with completion, status, optional virtual DMA bounce buffer, and inline `scat_list`. `struct ath6kl_irq_proc_registers` and `struct ath6kl_irq_enable_reg` mirror target interrupt register tables. `struct ath6kl_hif_ops` is the bus implementation vtable.

## Control flow and integration
HTC mailbox code uses HIF request flags to submit mailbox reads/writes, HIF common code reads/writes interrupt registers, BMI uses HIF read/write paths during firmware boot, and HTC pipe code uses pipe-specific operations. Interrupt bottom halves receive `struct ath6kl_device`, whose `htc_cnxt` points back to HTC and whose `ar` points to the root driver object.

## State and persistence behavior
The header defines persistent per-device HIF state but does not allocate it. Bus implementations persist queues of `bus_request`, scatter pools, interrupt enable shadows, and private `ar->hif_priv`. Request flags encode direction, sync/async mode, byte/block basis, and fixed/incremental address behavior, and those flags must remain consistent with HIF implementation semantics.

## Dependencies and integration points
`hif.h` includes `common.h`, `core.h`, and Linux scatterlist definitions. The include of `core.h` makes this header tightly coupled to the driver root state. It exports setup/mask/unmask/poll/RX-control/interrupt/scatter functions implemented in `hif.c`.

## Risks and test signals
Risks include duplicate scatter limit constants, bus implementations misinterpreting request flags, inline flexible array sizing for scatter items, packed interrupt register layout mismatch with firmware, and cyclic header dependencies. Test signals include compiling every HIF implementation, SDIO CMD53 fixed/incremental transfer tests, scatter limits, mailbox address range use, interrupt register table reads, and suspend/resume with active bus queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/hif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc-ops.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc-ops.h

## Purpose
`htc-ops.h` is the inline dispatch layer for HTC operations. It lets core/WMI code call HTC lifecycle, service connection, TX/RX buffer, activity, credit, and completion functions without knowing whether the attached HTC backend is mailbox or pipe.

## Important APIs, types, and functions
Wrappers include `ath6kl_htc_create()`, `ath6kl_htc_wait_target()`, `ath6kl_htc_start()`, `ath6kl_htc_conn_service()`, `ath6kl_htc_tx()`, `ath6kl_htc_stop()`, `ath6kl_htc_cleanup()`, `ath6kl_htc_flush_txep()`, `ath6kl_htc_flush_rx_buf()`, `ath6kl_htc_activity_changed()`, `ath6kl_htc_get_rxbuf_num()`, `ath6kl_htc_add_rxbuf_multiple()`, `ath6kl_htc_credit_setup()`, `ath6kl_htc_tx_complete()`, and `ath6kl_htc_rx_complete()`.

## Control flow and integration
Core initialization selects a backend by calling either mailbox or pipe attach, which writes `ar->htc_ops`. Later, generic code uses these wrappers to create a target, wait for firmware readiness, connect WMI/control/data services, start HTC, submit packets, add RX buffers, flush on teardown, and route bus-level pipe completions. The `target->dev->ar` path is used for most dispatches after target creation.

## State and persistence behavior
This header owns no state. It dispatches over `ar->htc_ops` and `struct htc_target` state allocated by the selected backend. Effects persist in endpoint queues, credit accounting, HIF queues, target flags, and service mappings.

## Dependencies and integration points
It includes `htc.h` and `debug.h`. It is a narrow polymorphic boundary between generic ath6kl core/WMI code and the transport implementations in `htc_mbox.c` and `htc_pipe.c`.

## Risks and test signals
The wrappers assume all ops are non-null and target backpointers are valid. Pipe-only completion wrappers call `ar->htc_ops->tx_complete/rx_complete`, which mailbox ops do not fill, so they must only be used by pipe HIF paths. Test signals include both HTC backend attach paths, service connection smoke tests, teardown flushes, and ensuring pipe completion paths are never invoked for mailbox backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc.h

## Purpose
`htc.h` defines the Host Target Communications protocol structures and local driver state used by both mailbox and pipe HTC implementations. It describes frame headers, control messages, service IDs, endpoints, packet containers, callbacks, credit distribution, endpoint stats, backend ops, and `struct htc_target`.

## Important APIs, types, and functions
Protocol definitions include HTC frame flags, RX trailer flags, message IDs (`READY`, `CONN_SVC`, `CONN_SVC_RESP`, setup complete), HTC versions, service IDs for WMI control/data ACs, endpoint IDs, credit report records, lookahead records, bundling limits, and operational flags. `struct htc_frame_hdr` is the packed wire header. Control structures include ready, connect, connect response, setup complete, record header, credit report, and lookahead reports.

Local structures include `struct htc_packet`, endpoint callbacks (`struct htc_ep_callbacks`), service connect request/response, `struct htc_endpoint_credit_dist`, `struct ath6kl_htc_credit_info`, endpoint stats, `struct htc_endpoint`, `struct htc_control_buffer`, pipe credit allocation entries, `struct ath6kl_htc_ops`, and the root `struct htc_target`. Inline helpers initialize TX/RX packet metadata, reset RX packet buffers, and count list depth.

## Control flow and integration
Core/WMI code creates `htc_packet` objects and submits them to the selected backend. Backends parse and generate `htc_frame_hdr`, connect WMI services to endpoints, use callbacks for RX, TX complete, RX refill, queue-full decisions, and multi-TX completion, and update endpoint stats. HIF interrupt or pipe completion paths eventually route packets back through endpoint callbacks.

## State and persistence behavior
`struct htc_target` persists endpoint arrays, credit distribution lists, control buffer pools, locks, target credit size/count, target version, RX/TX bundling limits, scatter sizing, pipe control response buffer, and pipe credit allocation. Endpoint state persists service id, queues, callbacks, queue depths, sequence numbers, connection flags, per-endpoint stats, pipe IDs, and credit-flow mode.

## Dependencies and integration points
`htc.h` depends on ath6kl `common.h` and Linux list/SKB conventions. It is included by `core.h`, HTC backends, HIF wrappers, and debug reporting. It is the main contract between ath6kl upper layers and HTC transports.

## Risks and test signals
Risks include packed wire-structure ABI drift, endpoint ID bounds, payload length validation, trailer parsing, credit accounting, queue-depth helper cost on long lists, and backend differences hidden behind a common ops table. Test signals include service connect responses, WMI data over all AC endpoints, credit report processing, bundled RX/TX, endpoint stat accuracy, setup-complete negotiation for HTC 2.0 versus 2.1, and stop/cleanup with queued packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc_mbox.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc_mbox.c

## Purpose
`htc_mbox.c` implements the mailbox/SDIO HTC backend. It handles target readiness, service connection, endpoint setup, TX credit distribution, asynchronous mailbox TX, optional scatter TX/RX bundling, mailbox RX lookahead processing, trailer parsing, control buffers, RX buffer flow control, start/stop/reset, and attachment of `ath6kl_htc_mbox_ops`.

## Important APIs, types, and functions
Credit functions include `ath6kl_credit_init()`, `ath6kl_credit_seek()`, `ath6kl_credit_update()`, `ath6kl_credit_redistribute()`, `ath6kl_credit_distribute()`, and `ath6kl_htc_mbox_credit_setup()`. TX functions include `ath6kl_htc_tx_prep_pkt()`, `ath6kl_htc_tx_issue()`, `htc_check_credits()`, `ath6kl_htc_tx_pkts_get()`, `ath6kl_htc_tx_bundle()`, `ath6kl_htc_tx_from_queue()`, `ath6kl_htc_tx_try()`, and `ath6kl_htc_mbox_tx()`. RX functions include `ath6kl_htc_rx_alloc()`, `ath6kl_htc_rx_fetch()`, `ath6kl_htc_rx_process_hdr()`, `ath6kl_htc_rx_process_packets()`, and the exported `ath6kl_htc_rxmsg_pending_handler()`. Lifecycle functions include `ath6kl_htc_mbox_create()`, `ath6kl_htc_mbox_wait_target()`, `ath6kl_htc_mbox_start()`, `ath6kl_htc_mbox_stop()`, `ath6kl_htc_mbox_cleanup()`, and `ath6kl_htc_mbox_attach()`.

## Control flow and integration
Create allocates `htc_target` and `ath6kl_device`, initializes locks/lists, calls `ath6kl_hif_setup()`, and allocates control buffers. `wait_target` polls endpoint 0 for `HTC_MSG_READY`, records target credits/credit size/version/bundle limits, enables scatter bundling if supported, and connects a pseudo control service. Service connection sends `HTC_MSG_CONN_SVC` synchronously over endpoint 0, waits for a response, assigns endpoint state, callbacks, max sizes, credit accounting, and thresholds. Start queues control RX buffers, initializes credit distribution, sends setup complete, and unmasks interrupts.

TX queues packets by endpoint, enforces max depth through `tx_full`, obtains credits, prepares HTC headers, optionally bundles with scatter requests, writes to mailbox asynchronously, and completes packets through upper callbacks. RX begins from a HIF mailbox lookahead, allocates buffers from endpoint queues or `rx_allocthresh`, fetches single or bundled packets, validates headers, parses trailers for credits/lookaheads, indicates packets to endpoint callbacks, and masks RX interrupts when buffers are unavailable.

## State and persistence behavior
State persists in endpoint TX/RX queues, free control TX/RX buffer lists, credit distribution list, target credit totals, bundle masks, scatter limits, `rx_st_flags`, `ep_waiting`, `chk_irq_status_cnt`, and endpoint stats. Stop sets `HTC_OP_STATE_STOPPING`, masks interrupts synchronously, flushes TX/RX queues, and resets control buffers. RX starvation persists as `HTC_RECV_WAIT_BUFFERS` until new buffers are added for the waiting endpoint.

## Dependencies and integration points
This backend depends on common HIF read/write, scatter, interrupt mask/unmask, RX control, debug/trace, target mailbox fields in `ar->mbox_info`, and upper endpoint callbacks provided by WMI/core. It is primarily used with SDIO mailbox transports.

## Risks and test signals
Risks include credit leaks on TX failure, scatter rollback correctness, trailer length validation, lookahead/header mismatch handling, RX starvation deadlock, endpoint 0 control buffer ownership, block/credit alignment disabling bundling, and queue flush races around stop. Test signals include HTC 2.0/2.1 ready negotiation, service connect failures, high-throughput bundled TX/RX, low-credit recovery, RX buffer exhaustion/unblock, firmware crash while polling, endpoint flush by tag, and repeated start/stop cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc_pipe.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc_pipe.c

## Purpose
`htc_pipe.c` implements the pipe-oriented HTC backend, used by message-based HIFs such as USB. Unlike mailbox HTC, it sends SKBs through HIF pipes, matches TX completions through per-endpoint lookup queues, receives complete SKBs from HIF, stores endpoint 0 control responses in a small buffer, and uses simpler per-service credit allocation.

## Important APIs, types, and functions
TX path functions include `htc_try_send()`, `get_htc_packet_credit_based()`, `get_htc_packet()`, `htc_issue_packets()`, `ath6kl_htc_pipe_tx()`, `ath6kl_htc_pipe_tx_complete()`, and `htc_send_packets_multiple()`. Control packet helpers allocate SKB-backed HTC control packets. Credit setup functions include `htc_setup_target_buffer_assignments()`, `htc_get_credit_alloc()`, and `htc_process_credit_report()`. RX functions include `ath6kl_htc_pipe_rx_complete()`, `htc_process_trailer()`, packet-container pool helpers, and `do_recv_completion()`. Lifecycle and service functions include `ath6kl_htc_pipe_create()`, `ath6kl_htc_pipe_wait_target()`, `ath6kl_htc_pipe_start()`, `ath6kl_htc_pipe_stop()`, `ath6kl_htc_pipe_conn_service()`, and `ath6kl_htc_pipe_attach()`.

## Control flow and integration
Create allocates `htc_target`, initializes endpoint states, creates a small pool of `htc_packet` containers for RX adaptation, allocates `ath6kl_device`, and asks HIF for default control pipes. Target wait polls `pipe.ctrl_response_valid`, validates `HTC_MSG_READY`, stores target credit count/size, assigns service credit budgets, and connects pseudo endpoint 0. Service connection sends a connect message over endpoint 0, waits for a control response captured by RX completion, validates response, configures endpoint callbacks/credits, maps WMI service to uplink/downlink HIF pipes, and optionally disables credit flow control.

TX queues are bounded by endpoint `max_txq_depth`; overflow packets are passed to `tx_full`. The drain path either consumes HTC credits or uses HIF pipe free queue count, pushes an HTC header into the SKB, records the packet in `ep->pipe.tx_lookup_queue`, and calls `ath6kl_hif_pipe_send()`. HIF TX completion parses the SKB header for endpoint id, finds the corresponding `htc_packet`, restores the SKB by removing the HTC header, completes to upper callbacks, and retriggers queue draining when credit flow is disabled. RX completion validates header and length, processes credit trailers, captures endpoint 0 control messages before setup complete, wraps data SKBs in temporary HTC packet containers, calls endpoint RX callbacks, and returns the container to the pool.

## State and persistence behavior
Persistent pipe state includes endpoint TX queues, RX queues, per-endpoint pipe IDs, TX lookup queues, credit-flow enablement, target credit size/count, static service credit allocation array, endpoint 0 control response buffer/valid flag, `HTC_OP_STATE_SETUP_COMPLETE`, and the packet-container pool. There is no mailbox interrupt state. Stop flushes RX/TX queues, resets endpoints, and clears setup-complete.

## Dependencies and integration points
The backend depends on pipe HIF operations (`pipe_send`, `pipe_get_default`, `pipe_map_service`, and free queue count), SKB headroom manipulation, upper endpoint callbacks, and HIF completion paths calling `ath6kl_htc_pipe_tx_complete()`/`ath6kl_htc_pipe_rx_complete()`. It shares protocol structures with mailbox HTC through `htc.h`.

## Risks and test signals
Risks include SKB headroom assumptions for pushing HTC headers, TX lookup failures if completions race with flush, endpoint id trust in completed SKBs, control response polling timeouts, RX packet container pool exhaustion, trailer validation, credit allocation imbalance, and minimal/no-op activity and credit setup hooks. Test signals include USB/pipe firmware boot, endpoint 0 ready/connect/setup sequence, TX completion lookup under flush, non-credit-flow endpoints under HIF queue pressure, malformed RX headers/trailers, RX before `ar->htc_target` initialization, and repeated stop/start cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc_pipe.c -->
