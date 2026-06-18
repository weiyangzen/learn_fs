# sources/distributed-fs/ceph-client/drivers/net/phy/bcm-phy-ptp.c

## Purpose
`bcm-phy-ptp.c` provides the Broadcom PHY hardware timestamping and PTP hardware clock helper used by supported Broadcom PHY drivers. In this tree it is wired through `broadcom.c` via `bcm_ptp_probe()`, `bcm_ptp_config_init()`, and `bcm_ptp_stop()`. It exposes a `mii_timestamper` for packet timestamping, registers a PHC via `ptp_clock_register()`, supports one periodic output or external timestamp pin, and programs Broadcom IEEE 1588 expansion registers through `bcm_phy_*_exp()` helpers.

## Important APIs, Types, And Functions
The central private object is `struct bcm_ptp_private`, which stores the owning `phy_device`, `mii_timestamper`, `ptp_clock`, `ptp_clock_info`, one `ptp_pin_desc`, a mutex for MDIO/PTP register sequencing, the TX timestamp queue, current TX/RX hwtstamp state, cached `NSE_CTRL`, pin activity, and delayed work for pin functions. `struct bcm_ptp_skb_cb` overlays `skb->cb` with sequence ID, PTP message type, expiry, and one-step discard state. `struct bcm_ptp_capture` is the normalized hardware timestamp record read from the timestamp FIFO.

The PHC callbacks are `bcm_ptp_gettimex()`, `bcm_ptp_settime()`, `bcm_ptp_adjtime()`, `bcm_ptp_adjfine()`, `bcm_ptp_enable()`, `bcm_ptp_verify()`, and `bcm_ptp_do_aux_work()`. The `mii_timestamper` callbacks are `bcm_ptp_rxtstamp()`, `bcm_ptp_txtstamp()`, `bcm_ptp_hwtstamp_set()`, `bcm_ptp_hwtstamp_get()`, and `bcm_ptp_ts_info()`. External users call exported `bcm_ptp_probe()`, `bcm_ptp_config_init()`, and `bcm_ptp_stop()`.

## Control Flow
Probe accepts only supported models, currently `PHY_ID_BCM54210E`, allocates state, registers a PHC, marks legacy timestamp selection with `phydev->default_timestamp`, installs `phydev->mii_ts`, and initializes queues and callbacks. Runtime PHC reads use `bcm_ptp_framesync_ts()`: disable active framesync mode, capture a pre/post system timestamp if requested, issue a CPU framesync with capture enabled, poll `INTR_STATUS` for `INTC_FSYNC`, read heartbeat registers, then restore the original `NSE_CTRL`. Setting and stepping time writes `TIME_CODE_*` and `NCO_TIME_*` through the shadow-load path and triggers `NSE_INIT`. Frequency adjustment converts scaled ppm into the Broadcom NCO base frequency and loads `NCO_FREQ_*` on a framesync.

For TX timestamping, `bcm_ptp_txtstamp()` parses the PTP header, records message type and sequence ID, handles one-step discard semantics for Sync/Pdelay Response, queues the skb, and schedules the PHC worker. `bcm_ptp_do_aux_work()` drains hardware timestamp records with `bcm_ptp_get_tstamp()` while matching them against queued skbs. RX timestamping expects the PHY to insert a 64-bit seconds/nanoseconds timestamp after the PTP header; `bcm_ptp_rxtstamp()` converts it to an skb hwtstamp and removes the inserted bytes.

Per-output and external timestamp operations share one pin. `bcm_ptp_perout_locked()` accepts only 1 PPS, writes period and pulse fields in 8 ns units, then delayed work schedules one-shot sync outputs aligned to whole seconds. `bcm_ptp_extts_locked()` configures framesync capture from SYNC1 and delayed work polls `INTR_STATUS` every quarter second, emits `PTP_CLOCK_EXTTS`, and reschedules.

## State And Persistence
All persistent state is kernel runtime state: PHY registers, `priv->nse_ctrl`, timestamping mode flags, `tx_queue`, `pin_active`, and scheduled work. There is no filesystem persistence. The hardware clock itself persists in PHY/NCO registers until reset or reconfigured. `bcm_ptp_stop()` cancels the PTP worker and active pin function, but does not unregister the PHC; ownership is devm/module lifetime through the caller.

## Dependencies And Integration Points
The file depends on phylib, Linux PTP clock APIs, net timestamping APIs, skb queues, delayed work, `ptp_classify` header parsing, and Broadcom register helpers from `bcm-phy-lib.h`. It integrates with MAC drivers through `phydev->mii_ts`, with ethtool timestamp reporting via `ts_info`, and with `broadcom.c` for lifecycle hooks. It writes Broadcom expansion registers such as `NSE_CTRL`, `TIME_SYNC`, `TX_EVENT_MODE`, `RX_EVENT_MODE`, and NCO/heartbeat registers.

## Risks And Edge Cases
Timestamp capture polling has a short fixed loop and can return `-ETIMEDOUT` if `INTC_FSYNC` does not arrive. TX matching uses only sequence ID and message type, so pathological duplicate PTP messages can be ambiguous. RX timestamp insertion assumes an 8-byte timestamp immediately after the PTP header and trims the skb in place. One pin can be configured as either perout or extts, so concurrent requests return `-EBUSY` unless the pin function matches. Perout is limited to 1 PPS and bounds pulse width to hardware limits. All hardware register sequences rely on the private mutex; callers must avoid independent unsynchronized writes to the same PTP registers.

## Test Signals
Useful test evidence includes successful `ethtool -T` PHC exposure, hwtstamp ioctl mode changes, `ptp4l` or `phc2sys` operation on BCM54210E, TX timestamp completion for two-step modes, one-step discard behavior, RX packet trimming with valid hwtstamps, and perout/extts pin events. Regression tests should exercise timeout paths, queue expiry, disabling timestamping while TX skbs are queued, and suspend/driver stop cancellation.
