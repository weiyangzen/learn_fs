<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/timer.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/timer.c

Purpose: Implements the datagram RPC round-trip-time estimator used to compute adaptive retransmission timeouts for frequently issued RPC procedures.

Important APIs/types/functions: `rpc_init_rtt()` initializes `struct rpc_rtt` arrays for five timer classes. `rpc_update_rtt()` updates smoothed RTT (`srtt`) and mean deviation (`sdrtt`) using Van Jacobson-style integer arithmetic. `rpc_calc_rto()` returns the retransmission timeout for a timer class. Constants are `RPC_RTO_MAX`, `RPC_RTO_INIT`, and `RPC_RTO_MIN`.

Control flow: Initialization stores the base timeout and seeds each timer bucket with either zero adjusted smoothed RTT or `(timeo - RPC_RTO_INIT) << 3`, plus initial deviation. Updates ignore timer index zero, negative samples from jiffies wrap, and coerce zero samples to one jiffy. The sample delta adjusts `srtt`, its absolute value adjusts `sdrtt`, and deviation is clamped to a minimum. Calculation returns the fixed base timeout for timer zero, otherwise `(srtt + 7) >> 3` plus deviation, capped at 60 seconds.

State and persistence behavior: State lives in caller-owned `struct rpc_rtt`, typically per RPC client. The estimator is memory-only and can be reset by client transport timeout logic after major timeouts.

Dependencies and integration points: Used by `xprt_wait_for_reply_request_rtt()` and `xprt_update_rtt()` in `xprt.c`, with procedure timer classes supplied by RPC procedure metadata. The code is intentionally scoped to datagram-style transports; stream transports generally use fixed/default timeout handling.

Risks: Timer indexes are one-based externally and decremented internally; callers passing zero deliberately bypass estimation. Bad timer indexes beyond the fixed array would be a caller bug. Conservative handling of infrequent/non-idempotent procedures avoids stale RTTs but can underutilize good network conditions.

Test signals: Verify initialization for timeouts below/equal/above `RPC_RTO_INIT`, update behavior for zero and negative samples, min/max timeout clamps, timer-zero bypass, retransmission count interactions through `rpc_set_timeo()` callers, and reset after major timeout in `xprt_adjust_timeout()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/timer.c -->
