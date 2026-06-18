# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ptp.h

## Purpose

`bnxt_ptp.h` defines BNXT PTP constants, timestamp/PPS data structures, helper macros, exported PTP functions, and inline timestamp conversion helpers shared by the BNXT TX/RX, ethtool, async event, and lifecycle code.

## Important APIs, types, and macros

- Register and clock constants: `BNXT_PTP_GRC_WIN`, `BNXT_PTP_GRC_WIN_BASE`, `BNXT_MAX_PHC_DRIFT`, `BNXT_CYCLES_SHIFT`, `BNXT_DEVCLK_FREQ`, low/high timer masks, default TX timestamp timeout, query timeout, and query enable flags.
- PPS event extraction macros: `EVENT_DATA2_PPS_EVENT_TYPE()`, `EVENT_DATA2_PPS_PIN_NUM()`, and `EVENT_PPS_TS()`.
- PPS pin usage constants define disabled, PPS input/output, sync input/output, and internal/external event modes.
- `struct pps_pin` and `struct bnxt_pps` store per-pin event, usage, and state for up to four TSIO pins.
- `struct bnxt_ptp_stats` stores timestamped packet, lost timestamp, and error counters.
- `struct bnxt_ptp_tx_req` stores one pending TX timestamp SKB plus PTP sequence id, header offset, and absolute timeout.
- `struct bnxt_ptp_cfg` is the central PTP state object: PTP clock info/handle, cyclecounter/timecounter, PPS info, locks, current time/high-bit cache, worker deadlines, multiplier, TX request slots, timestamp filters, register mapping, timeout, producer/consumer indices, and stats.
- `BNXT_PTP_INC_TX_AVAIL()` safely returns a TX timestamp slot under `ptp_tx_lock`.
- Exported functions cover PTP packet parse, current-time update, PPS events, timestamp filter reconfiguration, PPS reapply, hwtstamp get/set, TX timestamp SKB cleanup/reservation/storage/completion, RX timestamp extension, RTC init, PTP init, and PTP clear.
- `bnxt_timecounter_cyc2time()` reads the timecounter under seqlock retry.
- `bnxt_extend_cycles_32b_to_48b()` extends packet timestamps using cached high timer bits and low-bit wrap detection.

## Control flow role

The header lets the data path reserve TX timestamp slots and convert RX timestamps without depending on all of `bnxt_ptp.c` internals. Ettool timestamp reporting uses the presence and fields of `bp->ptp_cfg`. Async event handling calls PPS event and reapply hooks. Device init/teardown calls PTP init/clear and RTC helpers.

## State and persistence behavior

The main state defined here is runtime-only `struct bnxt_ptp_cfg`. It persists while the BNXT device instance is alive and is reset during PTP init/clear. Hardware timestamp/PPS state is applied by functions declared here but stored in firmware/hardware, not in this header.

## Dependencies and integration points

- Linux PTP and timecounter headers.
- BNXT firmware constants for timestamp query flags and async PPS event fields.
- BNXT TX path uses `BNXT_MAX_TX_TS`, `NEXT_TXTS()`, slot reservation, and completion helpers.
- BNXT RX path uses cycle-extension and conversion helpers.
- Ettool uses PTP stats and hwtstamp configuration functions.

## Risks and edge cases

- `BNXT_MAX_TX_TS` is four and `NEXT_TXTS()` assumes it is a power of two.
- `BNXT_PTP_INC_TX_AVAIL()` uses a macro with locking side effects; callers must avoid invoking it with expressions that have side effects.
- `bnxt_extend_cycles_32b_to_48b()` depends on timely `old_time` refresh and assumes at most one low-timer wrap relative to the cached high bits.
- `struct bnxt_ptp_cfg` embeds `struct ptp_clock_info`; reinitialization must preserve or rebuild pin_config carefully to avoid leaks.
- Comments mention `cyclecoutner`; typo is harmless but near timing-sensitive documentation.

## Test signals

- Compile data path users with PTP enabled and disabled through higher-level config combinations.
- TX timestamp ring wrap and slot availability tests across `BNXT_MAX_TX_TS`.
- RX timestamp wrap conversion tests for low timestamp below and above cached low bits.
- PTP clear/reinit leak checks for embedded `ptp_info.pin_config` and registered clock handles.
