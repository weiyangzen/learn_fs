# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_ptp.c

## Purpose

`i40e_ptp.c` implements IEEE 1588/PTP hardware timestamp support for i40e devices. It registers the adapter PHC with Linux PTP, reads/writes and adjusts the hardware clock, configures hardware timestamp filters for netdev timestamping, handles Tx/Rx timestamp extraction and watchdog cleanup, configures external timestamp/PPS/perout pins on supported 25G devices, and preserves PTP time across device resets.

## Important APIs, Types, and Functions

- Clock operations registered in `ptp_clock_info`: `i40e_ptp_adjfine()`, `i40e_ptp_adjtime()`, `i40e_ptp_gettimex()`, and `i40e_ptp_settime()`.
- Netdev hwtstamp entry points: `i40e_ptp_hwtstamp_get()` and `i40e_ptp_hwtstamp_set()`.
- Timestamp data path helpers: `i40e_ptp_tx_hwtstamp()`, `i40e_ptp_rx_hwtstamp()`, `i40e_ptp_tx_hang()`, `i40e_ptp_rx_hang()`, and `i40e_ptp_get_rx_events()`.
- Clock lifecycle: `i40e_ptp_init()`, `i40e_ptp_stop()`, `i40e_ptp_set_increment()`, `i40e_ptp_save_hw_time()`, and `i40e_ptp_restore_hw_time()`.
- Pin support: `enum i40e_ptp_pin`, `enum i40e_ptp_gpio_pin_state`, `struct i40e_ptp_pins_settings`, `i40e_ptp_alloc_pins()`, `i40e_ptp_free_pins()`, `i40e_ptp_set_pins()`, and `i40e_ptp_feature_enable()`.
- Constants define the base increment and link-speed multipliers: 40G/25G/no link use 1.6 ns, 10G/5G use 3.2 ns, 1G uses 32 ns, and 100M disables PHC progression.

## Control Flow

Initialization starts in `i40e_ptp_init()`. The driver reads `PRTTSYN_CTL0.PF_ID` and only enables PTP on the PF assigned to the port timesync block. It initializes locks, creates or reuses a PHC through `i40e_ptp_create_clock()`, enables timesync bits in `PRTTSYN_CTL0/CTL1`, programs the link-speed-dependent increment, reapplies saved hwtstamp configuration, restores hardware time using the saved time plus monotonic reset delta, and configures the 1PPS signal.

HWTSTAMP setup flows through `i40e_ptp_hwtstamp_set()` into `i40e_ptp_set_timestamp_mode()`. That function configures external trigger behavior, enables event interrupts, initializes EXTS work, validates Tx type, broadens supported Rx filters where hardware cannot match exactly, clears latched timestamp registers, toggles Tx timestamp interrupts, and updates `PRTTSYN_CTL1` message type and UDP recognition bits. `i40e_ptp_hwtstamp_get()` returns the shadow `pf->tstamp_config`.

PHC reads latch low then high time registers and optionally capture system pre/post timestamps. Writes program low then high because hardware updates on high write. Small time adjustments use `I40E_PRTTSYN_ADJ`; large adjustments read, add a `timespec64` delta, write full time, and reprogram 1PPS. Frequency adjustment recalculates the increment from `I40E_PTP_40GB_INCVAL * pf->ptp_adj_mult` and `adjust_by_scaled_ppm()`.

Tx timestamp flow uses `__I40E_PTP_TX_IN_PROGRESS` as a bit lock and `pf->ptp_tx_skb` as the pending packet. On interrupt, `i40e_ptp_tx_hwtstamp()` reads `TXTIME_L/H`, converts ns to `skb_shared_hwtstamps`, clears the bit before notifying the stack, and frees the skb. `i40e_ptp_tx_hang()` frees a stale skb after roughly one second. Rx timestamp flow reads status, verifies the descriptor-provided latch index is set, clears the tracked latch flag, reads `RXTIME_L/H`, and stores the converted timestamp on the skb. `i40e_ptp_rx_hang()` clears latches that have remained set for over one second.

Pin flow is limited to a specific 25G SFP28 subsystem and normally PF0. PTP core pin requests are translated into internal pin states, checked against an allowed pin/LED state table, written to GPIO control registers, and followed by timing-event reset.

## State and Persistence Behavior

The file maintains `pf->ptp_clock`, `pf->ptp_caps`, `pf->tstamp_config`, `pf->ptp_tx`, `pf->ptp_rx`, pending Tx skb state, latch event flags/timestamps, timestamp timeout counters, pin settings, and reset-time snapshots. Hardware state includes PRTTSYN time, increment, adjust, Tx/Rx latch registers, external event registers, interrupt enables, GPIO/LED routing, and PF ownership in `PRTTSYN_CTL0`. Across resets, `i40e_ptp_save_hw_time()` snapshots PHC time and monotonic start; `i40e_ptp_restore_hw_time()` adds elapsed monotonic time before restoring registers.

## Dependencies and Integration Points

The implementation depends on Linux PTP, net timestamping, sk_buff timestamp APIs, workqueues, locks, jiffies, `ptp_classify.h`, `posix-clock.h`, i40e PF/VSI structures, i40e device IDs, register macros, and AdminQ link info. It integrates with the netdev hwtstamp ioctl/netlink path, Tx/Rx interrupt and clean paths, periodic service/watchdog tasks, reset/suspend/resume handling, and platform-specific GPIO pins. It also uses `I40E_HW_CAP_PTP_L4` to decide whether Layer 4 PTP filters can be enabled.

## Risks

- Hardware timestamp latches are scarce and can block future timestamps if not cleared. The watchdogs mitigate this but dropped frames or missed interrupts can still lose timestamps.
- Tx timestamp state relies on correct bit-lock ordering around `pf->ptp_tx_skb`; premature notification before clearing the bit could cause timestamp request races, which the code explicitly avoids.
- PTP register access must be serialized with `tmreg_lock` for time operations and `ptp_rx_lock` for Rx latch state. Missing those locks in future changes would risk inconsistent time or latch accounting.
- `i40e_ptp_set_timestamp_mode()` broadens Rx filters. User space must inspect the returned config to see the effective mode.
- 100 Mbps link sets increment multiplier to zero and warns once, effectively stopping the PHC.
- Pin configuration depends on a hard-coded allowed state table and PF0 ownership. Unsupported combinations return errors or no-op on non-PF0 paths.
- `i40e_ptp_set_timestamp_mode()` contains `regval &= 0`, intentionally clearing AUX bits before setting event level; future edits should treat it as full reinitialization, not a masked update.

## Test Signals

Validation should cover PHC registration and removal, `phc2sys`/`testptp` get/set/adjfine/adjtime operations, hwtstamp get/set with supported and unsupported filters, Tx and Rx timestamp delivery under traffic, watchdog counters for stale Tx/Rx timestamp latches, link-speed changes updating PHC rate, reset preserving PHC time within expected drift, PF ownership rejection on non-owning PFs, and pin/perout/extts/PPS behavior on the supported 25G PTP-pin device. Kernel logs should show PHC enabled/removed and no repeated timestamp hang warnings during normal PTP traffic.
