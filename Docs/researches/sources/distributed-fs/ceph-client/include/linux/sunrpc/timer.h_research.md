# sources/distributed-fs/ceph-client/include/linux/sunrpc/timer.h

Purpose: declares the RPC round-trip-time estimator and timeout calculation helpers used by client transports.

Important APIs and types: `struct rpc_rtt` stores default timeout, five smoothed RTT values, five smoothed deviations, and per-timer timeout counts. APIs include `rpc_init_rtt()`, `rpc_update_rtt()`, and `rpc_calc_rto()`. Inline helpers `rpc_set_timeo()` and `rpc_ntimeo()` adjust/read bounded timeout counters for timer indexes.

Control flow: after successful replies, transports update RTT estimators; before retransmission/waiting, code calculates RTO. Timeout counters are capped at eight and can decay when observed timeout count decreases.

State and persistence: RTT state is per-client runtime estimator state and is not persistent.

Dependencies and integration points: used by `rpc_clnt`, `rpc_task`, and `rpc_xprt` timeout paths.

Risks and test signals: risks include wrong timer index handling, overly aggressive retransmission, timeout counter saturation, and poor behavior after network changes. Test with induced latency/loss, soft/hard mounts, multiple procedure timer classes, and reconnects.
