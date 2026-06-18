# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ptp.c

## Purpose

`ice_ptp.c` is the main Intel ICE driver implementation for Linux PTP 1588 support. It registers and manages the PHC, wires `ndo_hwtstamp_get`/`ndo_hwtstamp_set` and `ptp_clock_info` callbacks, handles Tx and Rx packet timestamp conversion, configures PTP GPIO pins for external timestamp and periodic output features, and coordinates PHY timestamp calibration across E810, E830, E82X/generic, and E825C/ETH56G hardware.

The file also owns the PTP lifecycle through initialization, periodic PHC-cache maintenance, interrupt processing, link-change recalibration, reset preparation, reset rebuild, and driver release. It is closely tied to `ice_ptp_hw.c`/`ice_ptp_hw.h` for register-level operations and to `ice_txrx.c`/`ice_txrx_lib.c` for packet timestamp request and receive timestamp delivery.

## Important APIs, Types, And Functions

- Static pin tables (`ice_pin_desc_e82x`, `ice_pin_desc_e825c`, `ice_pin_desc_e810`, `ice_pin_desc_dpll`) define per-family GPIO direction, pin naming, and input/output delay compensation.
- `ice_ptp_read_src_clk_reg()` reads the PHC source clock with optional `ptp_system_timestamp` pre/post samples and special 64-bit E830 handling.
- `ice_ptp_extend_32b_ts()` and `ice_ptp_extend_40b_ts()` convert narrow hardware timestamp captures into 64-bit nanoseconds using a recent cached PHC time.
- Tx timestamp APIs include `ice_ptp_request_ts()`, `ice_ptp_process_ts()`, `ice_ptp_ts_irq()`, `ice_ptp_req_tx_single_tstamp()`, and `ice_ptp_complete_tx_single_tstamp()`.
- Tx tracker helpers allocate, flush, stale-mark, and release `struct ice_ptp_tx` state, including E82X quad partitioning versus per-port timestamp blocks.
- PHC callbacks include `ice_ptp_adjfine()`, `ice_ptp_gettimex64()`, `ice_ptp_settime64()`, `ice_ptp_adjtime()`, `ice_ptp_adjtime_nonatomic()`, and optional cross timestamp callbacks through `ice_ptp_getcrosststamp()`.
- Ancillary clock features are implemented by `ice_ptp_extts_event()`, `ice_ptp_cfg_extts()`, `ice_ptp_cfg_perout()`, `ice_ptp_write_perout()`, `ice_verify_pin()`, and `ice_ptp_gpio_enable()`.
- Timestamp mode APIs `ice_ptp_hwtstamp_get()`, `ice_ptp_hwtstamp_set()`, `ice_ptp_set_timestamp_mode()`, and `ice_ptp_restore_timestamp_mode()` translate user hwtstamp requests into driver and register state.
- Lifecycle APIs include `ice_ptp_init()`, `ice_ptp_release()`, `ice_ptp_prepare_for_reset()`, `ice_ptp_rebuild()`, `ice_ptp_link_change()`, `ice_ptp_queue_work()`, and `ice_ptp_clock_index()`.

## Control Flow

Initialization enters through `ice_ptp_init()`. It sets `ICE_PTP_INITIALIZING`, validates the hardware lane number, initializes hardware PTP metadata, chooses a Tx timestamp interrupt mode, initializes the source-timer owner if this PF owns the PHC, adds the PF port to the adapter port list, initializes the port Tx tracker, starts or resets PHY timestamping, configures Tx timestamp interrupts, marks the state ready, and starts the PTP kthread worker. The owner path calls `ice_ptp_init_owner()`, which initializes the PHC and TSPLL/CGU, locks PTP hardware, writes the base increment value and initial wall-clock time, configures PHY timestamp interrupts, and registers the `ptp_clock`.

Timestamping configuration flows from `ice_ptp_hwtstamp_set()` to `ice_ptp_set_timestamp_mode()`. Tx mode is limited to off/on, while many PTP/NTP Rx filters collapse to `HWTSTAMP_FILTER_ALL`. The final state is stored in `pf->ptp.tstamp_config`, then applied immediately by `ice_ptp_restore_timestamp_mode()`, which configures Tx interrupts, toggles per-ring Rx timestamp flags, and triggers a software Tx timestamp interrupt to drain pending captures after reset.

Tx timestamp request flow starts in the transmit path through `ice_ptp_request_ts()`. The function holds the tracker spinlock, rejects uninitialized or calibrating trackers, finds a free timestamp slot, stores a referenced SKB and start jiffies, sets `SKBTX_IN_PROGRESS`, and returns the hardware PHY timestamp index. Completion is interrupt-driven. For E810 low-latency timestamp firmware support, the IRQ top half may call `ice_ptp_req_tx_single_tstamp()` and a later firmware completion calls `ice_ptp_complete_tx_single_tstamp()`. Other E810/E82X/E825C paths use threaded processing via `ice_ptp_process_ts()` and `ice_ptp_process_tx_tstamp()`, while E830 can process in the top half with register reads.

`ice_ptp_process_tx_tstamp()` loops all in-use slots, checks the ready bitmap when available, reads PHY timestamp memory, filters stale or invalid values, clears tracker state under lock, extends the 40-bit timestamp to 64-bit nanoseconds, reports it with `skb_tstamp_tx()`, and frees the SKB. It drops timestamps when the link is down, when a request is older than two seconds, when the value is not marked valid, when a no-ready-bitmap device returns the same value as its cached copy, or when the request was stale-marked by a clock update.

Receive timestamp flow is lighter. `ice_set_rx_tstamp()` updates all main VSI Rx ring `ptp_rx` flags. Receive-side code calls `ice_ptp_get_rx_hwts()`, which checks the descriptor valid bit, reads the ring cached PHC time, extends the descriptor's high timestamp field with `ice_ptp_extend_32b_ts()`, and returns a nanosecond timestamp.

The periodic worker `ice_ptp_periodic_work()` runs only in `ICE_PTP_READY`, refreshes the PF and Rx-ring cached PHC time via `ice_ptp_update_cached_phctime()`, checks for stuck ready timestamps with `ice_ptp_maybe_trigger_tx_interrupt()`, and reschedules itself every 500 ms or after 10 ms on cache update contention. This periodic cache is essential to safely extend 32-bit/40-bit hardware timestamp captures.

Time adjustment callbacks disable periodic outputs before changing the PHC, then restore them. `ice_ptp_settime64()` also clears E82X PHY offset readiness, writes the new PHC time under the PTP hardware lock, refreshes cached PHC time, and restarts all E82X PHY timestamping for recalibration. `ice_ptp_adjtime()` uses an atomic signed-32-bit hardware adjustment when possible and falls back to a get/add/set sequence for larger deltas. Frequency changes in `ice_ptp_adjfine()` compute a scaled increment from the base increment and write it through the hardware helper.

GPIO and pin control are exposed through `ptp_clock_info`. `ice_ptp_set_caps()` installs common callbacks, then selects family-specific pin/crosstimestamp capabilities. E810 may read an NVM SDP connection section and build dynamic pin descriptors, falling back to static E810 or DPLL pins. External timestamp enable writes AUX input, GPIO, and OICR event interrupt state; event delivery reads GLTSYN event registers, subtracts input delay compensation, clears the channel bit, and calls `ptp_clock_event()`. Periodic output enable validates the requested pin and period, calculates a start time at least 500 ms in the future when needed, compensates output propagation delay, writes target/period registers, and optionally toggles E825C CGU 1PPS output.

Reset flow starts with `ice_ptp_prepare_for_reset()`: it moves to `ICE_PTP_RESETTING`, disables Tx/Rx timestamping, cancels periodic work, releases Tx tracker state for non-PFR resets, disables periodic outputs, disables the source clock, and saves real time for later reconstruction. `ice_ptp_rebuild()` ensures preparation has happened, then source-timer owners call `ice_ptp_rebuild_owner()` to reinitialize PHC/TSPLL, restore approximate time from cached PHC plus elapsed wall time, flush all timestamp trackers, re-enable PHY interrupts, recalibrate PHYs, and restore perout/extts features. Successful rebuild returns to `ICE_PTP_READY`; failures set `ICE_PTP_ERROR`.

## State And Persistence

The primary persistent runtime state is `pf->ptp`. It tracks the state machine, Tx interrupt mode, the per-port tracker, delayed work, cached PHC time and jiffies, the kthread worker, external timestamp IRQ bits, pin descriptors, cached perout/extts requests, PTP clock info and clock handle, current hwtstamp configuration, reset-time snapshot, and Tx timestamp counters.

Each port stores `struct ice_ptp_port` state: list membership in `adapter->ports.ports`, Tx tracker, delayed calibration work, PHY start mutex, link state, FIFO busy retry count, and port number. Tx slots in `struct ice_ptp_tx` hold SKB references, start jiffies, cached timestamp values for no-ready-bitmap hardware, in-use and stale bitmaps, block/offset/length mapping, init/calibrating flags, and the last low-latency timestamp index.

The driver does not persist PTP settings to files. Hardware state is persisted only in device registers and firmware-managed blocks: source clock time, increment values, PHY timestamp block state, GPIO mode, AUX input/output configuration, TSPLL/CGU configuration, interrupt masks, and timestamp memory. User-requested perout/extts settings are cached in memory so reset rebuild can replay them. `reset_time` and `cached_phc_time` are used to approximate PHC restoration after reset but are volatile.

## Dependencies And Integration Points

`ice_ptp.c` includes `ice.h`, `ice_lib.h`, and `ice_trace.h`, and depends heavily on register definitions and helper APIs from the ICE driver. Important dependencies include `ice_ptp_hw.*` PHC/PHY helpers, TSPLL/CGU helpers, E82X and ETH56G PHY calibration helpers, low-level `rd32`/`wr32`/`rd64` register access, device capability fields in `struct ice_hw`, reset state helpers, adapter port-list ownership, and the Linux PTP clock framework.

Packet integration occurs with the Tx and Rx datapaths. `ice_txrx.c` requests Tx timestamp slots through `ice_ptp_request_ts()`, while receive paths in `ice_txrx_lib.c` call `ice_ptp_get_rx_hwts()` for normal and XDP receive timestamp extraction. Netdevice integration occurs through `ice_main.c` operations that point to `ice_ptp_hwtstamp_get()` and `ice_ptp_hwtstamp_set()`.

Interrupt integration uses PF OICR bits for Tx timestamp and external timestamp events. Some paths wake threaded miscellaneous interrupt handling by setting `ICE_MISC_THREAD_TX_TSTAMP`; E830 can process directly in the IRQ top half. Cross timestamp support integrates with `get_device_system_crosststamp()`, X86 ART, PTM/HH hardware registers, and optional `CONFIG_ICE_HWTS`.

## Risks

- Correct timestamp extension depends on `cached_phc_time` being refreshed before the 32-bit timestamp window wraps. The worker warns after two seconds and discards old Tx timestamps, but prolonged scheduling delays can still drop or suppress timestamp reporting.
- Tx tracker correctness relies on precise locking and slot ownership. The implementation intentionally releases the tracker lock while sleeping PHY reads occur, so teardown, link-down flushing, and stale marking must keep the bitmap/SKB state consistent.
- Low-latency E810 timestamp flow uses firmware proxy registers and `last_ll_ts_idx_read`; missed firmware completion or stale cached timestamp equality can leave requests pending until timeout.
- Clock set/adjust operations must stale-mark outstanding Tx timestamps and recalibrate E82X PHYs. Missing this path after new hardware-specific clock changes would risk reporting timestamps extended against the wrong epoch.
- Perout and extts replay after reset is memory-only. A rebuild failure can leave cached requests inconsistent with hardware state until userspace reconfigures them.
- Pin descriptor setup is hardware-family and NVM dependent. Invalid or unexpected SDP NVM data can disable OS pin access or produce wrong GPIO direction mapping.
- E82X source-timer ownership spans multiple PF ports. Bugs in `adapter->ctrl_pf`, `adapter->ports.ports`, or reset propagation can cause one PF to miss all-port Tx timestamp processing.
- Hardware family switch statements contain multiple special cases. Adding a new `mac_type` without updating timestamp processing, pin capabilities, cross timestamp support, Tx interrupt mode, and PHY calibration paths would likely degrade PTP behavior silently or with `-ENODEV`/`-EOPNOTSUPP`.

## Test Signals

Good validation signals include kselftest or PTP userspace coverage for `SIOCSHWTSTAMP`/netlink hwtstamp get/set, `ptp4l` and `phc2sys` stability, Tx timestamp completion counts versus skipped/timeouts/flushed/discarded counters, Rx timestamp validity under ring cache refresh pressure, and perout/extts loopback tests with edge selection and delay compensation.

Reset tests should cover PFR and non-PFR reset, link down/up, E82X recalibration, E825C DPLL/SyncE paths, perout/extts replay, and clock owner versus secondary PF behavior. Hardware-specific tests should cover E810 low-latency firmware timestamping, E810 no-ready-bitmap cached-value suppression, E82X quad timestamp ownership, E830 top-half timestamp processing, and ETH56G/E825C PHY start/stop behavior. Static and fault-injection tests should exercise allocation failures in Tx tracker/workqueue setup, semaphore acquisition failures, PHY register read failures, and busy `ICE_CFG_BUSY` cached-PHC updates.
