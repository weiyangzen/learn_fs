# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_spy.c

## Purpose
Implements the legacy Wireless Extensions spy API for libipw devices. It lets users configure a small list of MAC addresses to monitor signal quality, read the last quality samples, set threshold triggers, and emit threshold-crossing events.

## Important APIs, Types, and Functions
Exported handlers are `ipw_wx_set_spy`, `ipw_wx_get_spy`, `ipw_wx_set_thrspy`, `ipw_wx_get_thrspy`, and `libipw_spy_update`. Internal helpers are `get_spydata` and `iw_send_thrspy_event`. State lives in `struct iw_spy_data` embedded in `struct libipw_device`.

## Control Flow
`get_spydata()` returns the device spy state only when `ieee->spy_enabled` is true. `ipw_wx_set_spy()` disables spy collection by setting `spy_number` to zero, uses write memory barriers around the address/stat updates, copies up to the user-specified addresses from the wext buffer, clears stats, and re-enables the list length. `ipw_wx_get_spy()` returns configured addresses and their quality records, then clears updated flags. Threshold set/get simply copy low/high quality thresholds. `libipw_spy_update()` is called from RX processing with a source address and quality sample; it updates matching entries and sends `SIOCGIWTHRSPY` when level crosses below low or above high with hysteresis.

## State and Persistence Behavior
State is in-memory only: configured spy addresses, quality samples, thresholds, and per-address under-threshold booleans. No locks are taken in the update path; the code relies on RTNL serialization of wext handlers, temporary `spy_number` disablement, and memory barriers so interrupt/tasklet RX sees consistent enough data.

## Dependencies and Integration Points
Depends on Wireless Extensions, `iw_handler`, `wext`, netdevice, Ethernet helpers, and `libipw.h`. `libipw_rx()` calls `libipw_spy_update()` when spy records are configured and RX stats include signal/noise/quality masks.

## Risks
The lockless design is intentionally approximate and depends on small fixed arrays; extending it without synchronization would be risky. `wrqu->data.length` is assumed to be validated by the wext layer against `IW_MAX_SPY`. Threshold logic uses only `level`, so drivers must populate quality consistently. If `spy_enabled` is not set by the driver, all handlers return `-EOPNOTSUPP`.

## Test Signals
Enable spy support in ipw drivers, set/get zero and multiple spy addresses, RX updates for matching/nonmatching MACs, updated-flag clearing, threshold set/get, low-to-high and high-to-low event hysteresis, concurrent RX during address updates, and disabled-spy error paths are useful signals.
