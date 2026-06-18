# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_ptp.h

## Purpose
This header exposes qede PTP and hardware timestamping entry points to the rest of the qede driver and provides the inline Rx CQE timestamp gate used by the fastpath.

## Important APIs, Types, and Functions
The header includes Linux PTP, net timestamp, and timecounter interfaces plus `qede.h`. It declares `qede_ptp_rx_ts()`, `qede_ptp_tx_ts()`, `qede_hwtstamp_get()`, `qede_hwtstamp_set()`, `qede_ptp_disable()`, `qede_ptp_enable()`, and `qede_ptp_get_ts_info()`.

The inline `qede_ptp_record_rx_ts()` checks the Rx CQE parsing flags. If `TIMESTAMPRECORDED` is set and `TIMESYNCPKT` is also set, it calls `qede_ptp_rx_ts(edev, skb)`. If hardware recorded a timestamp for a non-PTP packet, it emits an informational diagnostic instead of attaching a timestamp.

## Control Flow
Receive processing in `qede_fp.c` calls `qede_ptp_record_rx_ts()` after skb protocol/hash/checksum metadata is prepared and before passing the skb to the stack. The inline function makes the fastpath cheap when no timestamp bit is present and delegates all timestamp conversion and skb hwtstamp mutation to `qede_ptp.c`.

## State and Persistence Behavior
The header owns no storage. Its inline helper reads CQE flags and may cause `qede_ptp_rx_ts()` to mutate skb timestamp metadata. PTP lifecycle and filter state live in the `struct qede_ptp` implementation hidden in `qede_ptp.c`.

## Dependencies and Integration Points
It depends on firmware CQE bit definitions such as `PARSING_AND_ERR_FLAGS_TIMESTAMPRECORDED_SHIFT` and `PARSING_AND_ERR_FLAGS_TIMESYNCPKT_SHIFT`, qede logging macros, and skb/netdev types from `qede.h`. It integrates fastpath Rx processing with the PTP implementation without exposing the private `struct qede_ptp` layout.

## Risks
The inline assumes CQE parsing flags are valid for the regular fast-path CQE form passed by the caller. A mismatch in firmware flag definitions would either miss timestamps or call into PTP for non-timesync traffic. Logging for unexpected non-PTP timestamps happens in the Rx path, so repeated firmware anomalies could add log noise under traffic.

## Test Signals
Compile coverage should verify all qede objects that include the header see the needed PTP and CQE types. Runtime signals are Rx PTP packets acquiring hardware timestamps, ordinary packets not being timestamped, and the informational path triggering only when hardware sets timestamp-recorded without the timesync packet bit.
