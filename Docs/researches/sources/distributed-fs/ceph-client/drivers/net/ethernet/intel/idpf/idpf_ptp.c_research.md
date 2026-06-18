# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_ptp.c

## Purpose
`idpf_ptp.c` implements Precision Time Protocol and hardware timestamping support for IDPF. It negotiates PTP feature access, registers a Linux PHC, reads and adjusts the device clock through direct MMIO or mailbox commands, maintains cached PHC time for 32-bit timestamp extension, manages TX timestamp latch allocation and release, enables RX timestamping on queues, and provides PTP clock callbacks.

## Important APIs, types, and functions
- Feature access: `idpf_ptp_get_features_access()` and internal `idpf_ptp_get_access()`.
- Clock reads: `idpf_ptp_read_src_clk_reg_direct()`, `idpf_ptp_read_src_clk_reg_mailbox()`, and `idpf_ptp_read_src_clk_reg()`.
- Cross timestamping: direct/mailbox helpers and `idpf_ptp_get_crosststamp()` when platform support exists.
- PHC operations: `idpf_ptp_gettimex64()`, `idpf_ptp_settime64()`, `idpf_ptp_adjtime()`, `idpf_ptp_adjfine()`, `idpf_ptp_do_aux_work()`, and capability setup in `idpf_ptp_set_caps()`.
- Cached timestamp extension: `idpf_ptp_update_cached_phctime()`, `idpf_ptp_tstamp_extend_32b_to_64b()`, and `idpf_ptp_extend_ts()`.
- Timestamp mode and latches: `idpf_ptp_request_ts()`, `idpf_ptp_set_timestamp_mode()`, `idpf_ptp_set_rx_tstamp()`, `idpf_tstamp_task()`, and release helpers.
- Lifecycle: `idpf_ptp_init()`, `idpf_ptp_create_clock()`, `idpf_ptp_release()`, and `idpf_ptp_get_txq_tstamp_capability()`.

## Control flow
PTP init first checks the virtchnl PTP capability, allocates `adapter->ptp`, initializes register offsets through device ops if available, obtains PTP capabilities via mailbox, derives access mode for each feature, initializes the direct clock read spinlock, registers the PHC, schedules periodic PHC-cache work if the clock can be read, programs the base increment value when adjustment is supported, and initializes clock time from realtime when settime is supported. Failure unwinds the PHC worker, clock registration, and allocated state.

Clock read dispatch depends on negotiated access. Direct access serializes with `read_dev_clk_lock`, writes shadow-time enable and execute command bits, captures optional system pre/post timestamps, and reads low/high clock registers. Mailbox access wraps `idpf_ptp_get_dev_clk_time()` or `idpf_ptp_get_cross_time()`. PHC get/set/adjust callbacks translate Linux PTP requests to these lower-level operations and update cached PHC time after set/adjust.

The periodic PTP auxiliary worker refreshes `adapter->ptp->cached_phc_time` and `cached_phc_jiffies` every 500 ms and writes the same cached time into each live RX queue. RX/TX timestamp extension uses the cached 64-bit PHC value plus the low 32 bits from hardware; if the cache is older than two seconds, `idpf_ptp_extend_ts()` increments discarded stats and returns zero.

TX timestamp requests allocate an entry from `tx_q->cached_tstamp_caps->latches_free` under spinlock, hold an skb reference, mark `SKBTX_IN_PROGRESS`, move the latch to `latches_in_use`, and return the negotiated index for the descriptor. Release paths cancel pending timestamp work, free unused latches, consume skb references for in-use latches, increment flushed stats, and free vport timestamp capability state.

Timestamp mode changes validate TX type, enable/disable PTP flags on all RX queues depending on `rx_filter`, normalize filters to NONE or ALL, and store the resulting `kernel_hwtstamp_config` on the vport.

## State and persistence behavior
Adapter PTP state lives in `struct idpf_ptp`: PHC registration, capability bits, access modes, direct register pointers, base increment/max adjustment, cached PHC time, secondary mailbox metadata, and read lock. Vport timestamp state includes `tstamp_config`, `tx_tstamp_caps`, latch lists, per-latch skb references, and `tstamp_stats`. RX queues cache PHC time for timestamp extension and carry a PTP queue flag. State is recreated on driver load/reset and released during PTP teardown.

## Dependencies and integration points
The file depends on Linux PTP clock infrastructure, timekeeping cross timestamp APIs, PCI PTM/ART checks, IDPF virtchnl PTP mailbox commands, queue structures, timestamp stats, and `idpf_ptp.h` types. It integrates with ethtool timestamp reporting in `idpf_ethtool.c`, hwtstamp NDOs in `idpf_lib.c`, TX descriptor setup in datapath files, and queue/vport release paths.

## Risks and edge cases
- Timestamp extension depends on the cached PHC time being refreshed within two seconds; worker stalls or mailbox failures cause discarded timestamps.
- Direct clock reads require correct shadow-time command masks and register pointers; partial register initialization would return invalid time.
- Large `adjtime` values use non-atomic get/adjust/set, which can race real time progression and other adjusters.
- `idpf_ptp_adjfine()` logs mailbox errors but returns 0; callers may not see failure.
- Latch list handling must preserve skb references and list membership across completion, reset, and release.
- Platform cross timestamping is conditional on ARM arch timer or x86 ART/PTM/TSC-known-frequency support; unsupported platforms must degrade cleanly.

## Test signals
Validate PHC registration, `phc2sys`/`testptp` get/set/adjfine/adjtime, direct and mailbox clock-read devices, cross timestamp availability on supported platforms, RX and TX hardware timestamp traffic, stale cache discard behavior, latch exhaustion and release, reset/unload with outstanding timestamp skbs, ethtool `--show-time-stamping`, and mailbox failure injection for PTP commands.
