## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_ptp.c

### Purpose
`sparx5_ptp.c` implements hardware timestamping and PHC support for Sparx5. It registers PTP clocks, programs TOD increments for the switch core clock, handles hwtstamp configuration, classifies PTP packets for one-step/two-step rewrite, manages pending TX timestamp SKBs, and reconstructs RX/TX timestamps.

### Important APIs, Types, And Functions
Exports include `sparx5_ptp_hwtstamp_set/get()`, `sparx5_ptp_txtstamp_request()`, `sparx5_ptp_txtstamp_release()`, `sparx5_get_hwtimestamp()`, `sparx5_ptp_irq_handler()`, `sparx5_ptp_gettime64()`, `sparx5_ptp_init()`, `sparx5_ptp_deinit()`, and `sparx5_ptp_rxtstamp()`. PHC operations are `sparx5_ptp_adjfine()`, `sparx5_ptp_settime64()`, `sparx5_ptp_gettime64()`, and `sparx5_ptp_adjtime()`.

### Control Flow
Initialization requests the PTP IRQ when supported, registers three PHCs, initializes locks and per-port TX queues, programs nominal TOD increments for each domain, and enables master counters. TX hwtstamp configuration sets a per-port rewrite command and normalizes RX filters to `HWTSTAMP_FILTER_ALL`. TX timestamp request classifies the skb, stores IFH rewrite metadata, queues two-step PTP SKBs with a rolling timestamp ID, and marks `SKBTX_IN_PROGRESS`. The IRQ drains hardware timestamp FIFO entries, matches IDs to queued SKBs, reconstructs time using current TOD seconds plus hardware nanoseconds, reports timestamps, and frees SKBs.

### State, Persistence, And Dependencies
State lives in `sparx5->phc[]`, locks, `sparx5->ptp_skbs`, per-port `tx_skbs` and `ts_id`, per-port `ptp_cmd`, and PTP/TOD hardware registers. Dependencies include Linux PTP clock APIs, `ptp_classify_raw()`, `ptp_parse_header()`, skb timestamp APIs, generated PTP/REW registers, core clock constants, and netdev bridge masks.

### Integration Points
Netdev hwtstamp ops call set/get, packet TX calls txtstamp request and writes IFH fields, packet RX calls `sparx5_ptp_rxtstamp()`, and QoS/PSFP base-time calculation reads PHC time.

### Risks
PTP is rejected for bridged ports to avoid duplicate forwarded transparent-clock frames. Two-step skb ownership is subtle and bounded by `SPARX5_MAX_PTP_ID`; leaks or double frees can occur if busy/error paths diverge. `sparx5_ptp_txtstamp_release()` decrements `port->ts_id`, which can underflow around zero. Clock adjustment math is core-clock-specific and split to avoid overflow.

### Test Signals
Test hwtstamp filter normalization, bridge-port rejection, one-step and two-step Sync/Delay packet classification, timestamp ID wrap, pending queue timeout cleanup, IRQ matching and overflow warning, PHC get/set/adjfine/adjtime for each core clock, RX timestamp seconds rollover, and deinit queue purging.
