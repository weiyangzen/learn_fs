# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_ptp.c

## Purpose
`igb_ptp.c` implements Precision Time Protocol support for the Intel `igb` PCI Ethernet driver. It exposes a PHC through `ptp_clock_register()`, configures hardware timestamp filters, converts NIC timer values into kernel `ktime_t` hardware timestamps, manages SDP pins for external timestamp and periodic output features, and recovers from known timestamp latch hangs.

## Important APIs, Types, And Functions
The main public entry points are `igb_ptp_init()`, `igb_ptp_reset()`, `igb_ptp_stop()`, `igb_ptp_suspend()`, `igb_ptp_rx_hang()`, `igb_ptp_tx_hang()`, `igb_ptp_rx_pktstamp()`, `igb_ptp_rx_rgtstamp()`, `igb_ptp_hwtstamp_get()`, and `igb_ptp_hwtstamp_set()`. PTP clock operations are installed in `adapter->ptp_caps` and differ by MAC generation: 82576 uses a `cyclecounter`/`timecounter`, 82580/i350/i354 use a 40-bit timer with overflow work, and i210/i211 use seconds/nanoseconds SYSTIM registers directly. Pin support is handled by `igb_pin_direction()`, `igb_pin_extts()`, `igb_pin_perout()`, and feature callbacks for 82580 and i210.

## Control Flow
Probe calls `igb_ptp_init()`, which selects capabilities and function pointers by `hw->mac.type`, registers the PHC, initializes locks/work, and calls `igb_ptp_reset()`. Reset reapplies timestamp mode, initializes timer increment registers or writes the current wall clock into SYSTIM, enables timestamp interrupts, and schedules overflow maintenance where required. Timestamp ioctl changes enter through `igb_ptp_hwtstamp_set()`, which validates requested TX/RX modes and programs TSYNC, ETQF, FTQF, and related registers. TX timestamp completion is handled by `igb_ptp_tx_work()` or watchdog cleanup; RX timestamps are read either from inline packet headers or global RXSTMP registers.

## State And Persistence
Persistent driver state lives in `struct igb_adapter`: `ptp_clock`, `ptp_caps`, `ptp_flags`, `tmreg_lock`, `cc`, `tc`, `tstamp_config`, `ptp_tx_skb`, `ptp_tx_start`, `perout[]`, `sdp_config[]`, timeout counters, and PPS state. Hardware state is volatile and must be rebuilt after reset. The saved `tstamp_config` is the software shadow returned to users and replayed by `igb_ptp_reset()`.

## Dependencies And Integration Points
The file depends on Linux PTP, hwtstamp, net timestamping, workqueue, timecounter, and PCI MMIO APIs. It integrates with `igb` TX/RX paths through skb timestamp callbacks and with netdev timestamping ioctls through `igb_ptp_hwtstamp_get/set()`. SDP pin routing integrates with the PTP pin framework via `ptp_find_pin()` and `ptp_pin_desc`.

## Risks
The code is sensitive to register ordering, timer width overflow, and hardware generation differences. 82576 and 82580 require periodic timecounter updates to prevent stale conversion after SYSTIM wrap. Only one TX timestamp skb is tracked, so races around `ptp_tx_skb` and `__IGB_PTP_TX_IN_PROGRESS` must remain carefully ordered. RX/TX timestamp valid bits can wedge hardware until cleared by watchdog paths. Incorrect filter programming can silently broaden filters to all packets on newer hardware.

## Test Signals
Useful validation includes PHC registration logs, `phc2sys`/`ptp4l` operation, `ethtool -T`, timestamp ioctl filter tests, TX timestamp timeout counters, RX hang clear counters, suspend/resume and reset tests, and SDP EXTS/PEROUT/PPS tests on hardware supporting those pins.
