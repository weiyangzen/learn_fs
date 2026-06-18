# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ptp.c

## Purpose
`ixgbe_ptp.c` implements Precision Time Protocol hardware clock support for ixgbe devices. It maps hardware SYSTIME registers into Linux `cyclecounter`/`timecounter`, registers a PHC with the PTP subsystem, supports frequency and time adjustment, configures hardware timestamp filters, handles TX/RX hardware timestamps, recovers timestamp hangs, and optionally drives PPS/clock output on SDP0.

## Important APIs and functions
PHC operations are installed by `ixgbe_ptp_create_clock` and include `ixgbe_ptp_adjfine_82599`, `ixgbe_ptp_adjfine_X550`, `ixgbe_ptp_adjtime`, `ixgbe_ptp_gettimex`, `ixgbe_ptp_settime`, and `ixgbe_ptp_feature_enable`. Lifecycle entry points are `ixgbe_ptp_init`, `ixgbe_ptp_reset`, `ixgbe_ptp_suspend`, and `ixgbe_ptp_stop`.

Cyclecounter support is split by hardware generation. `ixgbe_ptp_read_82599` reads raw 64-bit fixed-point SYSTIME. `ixgbe_ptp_read_X550` converts X550-style high/low registers into a nanosecond-like cycle value. `ixgbe_ptp_start_cyclecounter` selects read functions, masks, multipliers, shifts, and TIMINCA programming based on MAC type and link speed.

Timestamping APIs include `ixgbe_ptp_hwtstamp_get`, `ixgbe_ptp_hwtstamp_set`, `ixgbe_ptp_set_timestamp_mode`, `ixgbe_ptp_tx_hwtstamp_work`, `ixgbe_ptp_rx_pktstamp`, `ixgbe_ptp_rx_rgtstamp`, `ixgbe_ptp_tx_hang`, and `ixgbe_ptp_rx_hang`. PPS support uses `ixgbe_ptp_setup_sdp_X540`, `ixgbe_ptp_setup_sdp_X550`, and `ixgbe_ptp_check_pps_event`.

## Control flow
Initialization creates or reuses a PHC, initializes `tmreg_lock`, sets up TX timestamp work, resets timestamp hardware, initializes SYSTIME to real time through the timecounter, and marks PTP running. Reset re-applies timestamp filter settings, reprograms TIMINCA/cyclecounter, clears SYSTIME registers, initializes the timecounter from `ktime_get_real`, and re-enables SDP output if configured.

Frequency adjustment computes a new TIMINCA value from `adapter->base_incval` on 82599/X540 or from the X550/E610 base period on newer MACs. Time adjustment and settime only update the software timecounter under `tmreg_lock`; the hardware SYSTIME register remains a cycle source.

Hardware timestamp configuration validates requested TX and RX modes, maps supported filters to `TSYNCTXCTL`, `TSYNCRXCTL`, `RXMTRL`, and `ETQF`, normalizes some requested RX filters to broader hardware-supported modes, clears stale TX/RX timestamp registers, and stores the accepted config in `adapter->tstamp_config`.

TX timestamping allows one outstanding skb tracked by `adapter->ptp_tx_skb` and `__IXGBE_PTP_TX_IN_PROGRESS`. Work polls `TSYNCTXCTL_VALID`, reads TX timestamp registers, converts through the timecounter, notifies the stack with `skb_tstamp_tx`, frees the skb, and clears state. RX timestamping either reads an appended packet timestamp or latched RXSTMP registers and converts it into skb hwtstamps.

## State and persistence
Key state lives in `adapter->hw_cc`, `adapter->hw_tc`, `adapter->base_incval`, `adapter->tmreg_lock`, `adapter->ptp_caps`, `adapter->ptp_clock`, `adapter->ptp_setup_sdp`, `adapter->tstamp_config`, `adapter->ptp_tx_skb`, `adapter->ptp_tx_start`, `adapter->last_overflow_check`, `adapter->last_rx_ptp_check`, and PTP-related adapter state/flag bits. Hardware state is in SYSTIME, TIMINCA, TSYNC, TSAUXC, ESDP/TSSDP, target time, and timestamp registers. PHC registration is kernel runtime state and is removed by `ixgbe_ptp_stop`.

## Dependencies and integration points
The file depends on Linux PTP, clocksource/timecounter, skb timestamp APIs, workqueues, spinlocks, netdev hwtstamp ioctl plumbing, and ixgbe interrupt/watchdog paths. It integrates with transmit code for requesting timestamps, receive code for consuming timestamps, link-change paths via `ixgbe_ptp_start_cyclecounter`, reset paths via `ixgbe_ptp_reset`, and interrupt handling for PPS events.

## Risks and edge cases
PTP behavior is hardware-generation-specific. 82599/X540 SYSTIME overflow requires periodic reads, while X550/E610 represent time differently and may need multiplier correction for non-300MHz revisions. Incorrect lock use around `timecounter` can corrupt PHC time. Timestamp filters are broader than some user requests, so user-visible config normalization is important. TX timestamp hangs can retain skb references unless watchdog cleanup runs. RX timestamp registers can latch indefinitely if hardware drops a timestamped packet.

## Test signals
Tests should validate PHC registration by MAC type, `phc2sys`/`ptp4l` operation, adjfine and settime monotonic behavior, link-speed TIMINCA recalculation on 82599/X540, hwtstamp get/set normalization for supported and unsupported filters, one-at-a-time TX timestamp locking, TX timeout cleanup counters, RX register hang recovery, appended RX timestamp handling, PPS enable/disable, suspend/resume retention of timestamp settings, and no PTP registration on unsupported devices.
