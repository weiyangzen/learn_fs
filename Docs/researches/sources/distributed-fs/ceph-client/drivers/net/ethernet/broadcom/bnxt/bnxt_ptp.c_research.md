# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ptp.c

## Purpose

`bnxt_ptp.c` implements Precision Time Protocol and hardware timestamp support for BNXT devices. It registers a PHC with the Linux PTP subsystem, maps and reads device reference-clock registers, maintains a timecounter/cyclecounter, configures hardware timestamp filters, handles TX/RX timestamp conversion, supports PTP PPS/TSIO pins, queries firmware timestamps, provides optional cross-timestamping on x86 PTM-capable systems, and cleans up PTP resources on device teardown/reset.

## Important APIs and functions

- Clock operations:
  - `bnxt_ptp_settime()`, `bnxt_ptp_gettimex()`, `bnxt_ptp_adjtime()`, and `bnxt_ptp_adjfine()` implement `ptp_clock_info` time set/read/phase/frequency adjustment callbacks.
  - `bnxt_ptp_cfg_settime()`, `bnxt_ptp_adjphc()`, and `bnxt_ptp_adjfine_rtc()` program firmware/hardware RTC modes through HWRM.
  - `bnxt_ptp_timecounter_init()` and `bnxt_ptp_rtc_timecounter_init()` initialize local conversion state.
- Clock reads and conversion:
  - `__bnxt_refclk_read()`, `bnxt_refclk_read()`, and `bnxt_refclk_read_low()` read 48-bit or low 32-bit mapped reference-clock registers with system timestamp bracketing and reset serialization.
  - `bnxt_cc_read()` feeds the kernel cyclecounter.
  - `bnxt_extend_cycles_32b_to_48b()` in the header extends RX 32-bit packet timestamps using cached high bits.
  - `bnxt_ptp_update_current_time()` and `bnxt_ptp_get_current_time()` refresh `current_time` and `old_time`.
- Packet timestamp configuration:
  - `bnxt_hwtstamp_set()` validates userspace `kernel_hwtstamp_config`, maps RX filters to BNXT PTP message masks/all-packet timestamp flags, updates TX enable state, and applies hardware config.
  - `bnxt_hwtstamp_get()` returns cached hardware timestamp config.
  - `bnxt_hwrm_ptp_cfg()` and `bnxt_ptp_cfg_tstamp_filters()` program MAC timestamp capture flags.
- TX/RX timestamp data path:
  - `bnxt_ptp_parse()` classifies PTP packets and extracts sequence id/header offset for firmware timestamp queries.
  - `bnxt_ptp_get_txts_prod()` reserves one of four TX timestamp slots.
  - `bnxt_get_tx_ts_p5()` stores a TX SKB in a slot and schedules the PTP aux worker.
  - `bnxt_ptp_ts_aux_work()` polls pending TX timestamp requests, periodically refreshes timecounter state, and prevents 48-bit overflow drift.
  - `bnxt_stamp_tx_skb()` queries firmware for a TX timestamp and calls `skb_tstamp_tx()`.
  - `bnxt_tx_ts_cmp()` handles timestamp completions that carry the timestamp directly in completion rings.
  - `bnxt_get_rx_ts_p5()` converts 32-bit packet RX timestamps to extended cycles for receive code.
- PPS and pins:
  - `bnxt_ptp_pps_event()` converts async PPS event data to PTP clock events.
  - `bnxt_ptp_cfg_pin()`, `bnxt_ptp_cfg_event()`, `bnxt_ptp_perout_cfg()`, `bnxt_ptp_enable()`, `bnxt_ptp_verify()`, `bnxt_ptp_pps_init()`, and `bnxt_ptp_reapply_pps()` implement external timestamp, periodic output, and PPS pin configuration.
- Lifecycle:
  - `bnxt_map_ptp_regs()` and `bnxt_unmap_ptp_regs()` map reference-clock registers through a GRC window on P5 or direct offsets on P7.
  - `bnxt_ptp_init_rtc()`, `bnxt_ptp_init()`, `bnxt_ptp_free()`, and `bnxt_ptp_clear()` initialize/register/unregister/clear PTP resources.
  - `bnxt_ptp_free_txts_skbs()` cancels worker activity and frees queued TX timestamp SKBs.
- Optional x86 cross timestamp:
  - `bnxt_phc_get_syncdevicetime()` and `bnxt_ptp_getcrosststamp()` integrate firmware PTM query results with `get_device_system_crosststamp()` when PTM and ART are available.

## Control flow

Initialization maps PTP registers, tears down/rebuilds the PHC when PPS capability changed, initializes locks and TX timestamp slot accounting, initializes the timecounter in RTC or non-RTC mode, registers driver events with firmware, optionally queries PPS pin configuration, installs cross-timestamp support on capable x86 systems, registers the PTP clock, resets timestamp stats, and starts the aux worker for P5-plus chips.

Userspace timestamp configuration enters through `bnxt_hwtstamp_set()`. The function validates TX type and RX filter, saves the old cached state, updates `ptp->rxctl`, `rx_filter`, and `tx_tstamp_en`, then calls `bnxt_hwrm_ptp_cfg()` to program MAC timestamp capture. On firmware failure it restores the old cached config.

TX timestamping has two variants. For P5 query-based timestamps, the TX path reserves a slot with `bnxt_ptp_get_txts_prod()`, stores sequence/header metadata and SKB elsewhere, then `bnxt_get_tx_ts_p5()` publishes timeout and SKB and schedules the aux worker. The worker calls `bnxt_stamp_tx_skb()`, which queries firmware using the stored sequence/header offset, converts device cycles to ns, timestamps the SKB, updates stats, and frees the SKB. For completion-based timestamps, `bnxt_tx_ts_cmp()` receives a completion, finds the original TX buffer from the opaque field, converts the 48-bit timestamp, and timestamps the SKB if no hardware timestamp error is set.

Clock reads use seqlocks to serialize register access with firmware reset and timecounter mutation. `bnxt_ptp_gettimex()` reads the low 32-bit reference clock, extends it using cached high bits, converts it through the timecounter, and returns a timespec. Periodic aux work refreshes current time every second and forces a `timecounter_read()` every 18 minutes to avoid overflow with the 23-bit shifted cyclecounter.

PPS requests from the PTP subsystem use `bnxt_ptp_enable()`, which finds a compatible pin, configures its firmware usage/state, and configures the firmware PPS event or periodic output phase. Async firmware PPS events are converted to `PTP_CLOCK_PPSUSR` or `PTP_CLOCK_EXTTS` events.

## State and persistence behavior

- `struct bnxt_ptp_cfg` stores PHC registration, cyclecounter/timecounter, seqlock, TX timestamp spinlock, current time/high-bit cache, periodic worker deadlines, clock multiplier, TX timestamp slots, timestamp filters, RX filter/mask, TX enable bit, PTP register offsets, timeout, PPS pin state, and stats.
- Hardware/firmware state includes PTP set time, phase/frequency adjustment, MAC timestamp capture filters, PPS pin configuration, PPS event mode, periodic output phase, and mapped GRC window.
- SKB ownership for query-based TX timestamps is transferred into `ptp->txts_req[]` until the aux worker timestamps or drops it.
- `ptp->stats` persists packet/lost/error counts until PTP reinit.
- No filesystem persistence exists.

## Dependencies and integration points

- Linux PTP clock subsystem, `ptp_clock_info`, aux workers, pin configuration, PPS/extts/perout events, and cross timestamp APIs.
- Linux timestamping and SKB APIs: `kernel_hwtstamp_config`, `skb_tstamp_tx()`, `skb_shared_hwtstamps`.
- Timekeeping helpers: seqlock, cyclecounter, timecounter, system timestamp bracketing, ART cross timestamp on x86.
- BNXT HWRM commands for FUNC_PTP_CFG, FUNC_PTP_PIN_CFG/QCFG, PORT_MAC_CFG, PORT_TS_QUERY, and FUNC_PTP_TS_QUERY.
- BNXT TX/RX paths call parse/reserve/store/completion/RX conversion helpers.
- Firmware reset paths must coordinate with PTP register reads and reapply PPS/timestamp settings.

## Risks and edge cases

- Register reads during firmware reset return `-EIO`; missing serialization can read invalid BAR/GRC windows.
- 32-bit RX timestamp extension depends on `old_time` being refreshed often enough and on monotonic low-bit behavior.
- Query-based TX timestamp slots are limited to four. Exhaustion increments `ts_err`; lost queries increment `ts_lost` and free SKBs.
- Memory barriers around `abs_txts_tmo` and `tx_skb` publication are required so the aux worker sees a consistent slot.
- `bnxt_ptp_pps_event()` assumes event type is one of the handled values before calling `ptp_clock_event()` with initialized fields.
- PPS pin arrays are capped by `BNXT_MAX_TSIO_PINS`; firmware reporting more pins would need bounds review.
- `bnxt_pps_config_ok()` uses a compact boolean expression that is easy to misread; it tests whether firmware PPS capability and pin_config presence agree.
- RTC versus non-RTC modes choose different adjustment mechanisms; wrong `BNXT_PTP_USE_RTC()` behavior can double-apply or miss adjustments.
- `bnxt_unmap_ptp_regs()` clears the P5 GRC window even on P7 paths; the fixed register write should remain harmless but is platform-specific.

## Test signals

- PHC registration/read/set/adjtime/adjfine tests in RTC and non-RTC modes.
- Hardware timestamp config tests for TX on/off, RX none/all/PTP event/sync/delay request, unsupported all-RX firmware, and rollback on HWRM failure.
- TX timestamp tests for query success, query timeout before and after absolute timeout, slot exhaustion, SKB freeing, completion-based success/error, and stats.
- RX timestamp conversion tests around low-32-bit wrap and periodic `old_time` refresh.
- PPS tests for pin query, extts, perout, PPS, disable paths, invalid pin/function, firmware failures, and reapply after reset.
- Cross timestamp tests on x86 PTM+ART systems and build tests on non-x86.
- Reset/unmap tests to ensure PTP register access fails cleanly during firmware reset and resources are unregistered once.
