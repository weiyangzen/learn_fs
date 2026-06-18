# sources/distributed-fs/ceph-client/net/ipv4/metrics.c

## Purpose
`metrics.c` parses and allocates IPv4 FIB destination metrics from netlink route attributes, converting user-provided `RTAX_*` values into a refcounted `struct dst_metrics`.

## Important APIs, Types, And Functions
The internal parser is `ip_metrics_convert()`. The exported allocator is `ip_fib_metrics_init()`, which returns default metrics when no metrics attribute is supplied or a newly allocated metrics block on success.

## Control Flow
`ip_fib_metrics_init()` allocates zeroed metrics storage, then `ip_metrics_convert()` iterates nested netlink attributes. Numeric metrics must be `u32`; congestion-control algorithm metrics are string-resolved through TCP congestion-control registration. Selected values are clamped for MSS, MTU, and hoplimit. Feature masks are rejected if unknown bits are set. ECN-capable congestion algorithms set `DST_FEATURE_ECN_CA`.

## State And Persistence
Allocated metrics are in-memory route state with refcount initialized to one. The parser has no global state, but it consults TCP congestion-control registry state when resolving `RTAX_CC_ALGO`.

## Dependencies And Integration Points
The file integrates rtnetlink extended acknowledgements, `array_index_nospec()` bounds hardening, TCP congestion-control lookup, `dst_default_metrics`, and route creation paths that call `ip_fib_metrics_init()`.

## Risks
The main risks are ABI validation regressions, accepting unknown feature bits, forgetting to clamp legacy IPv4 limits, mishandling unknown congestion-control names, and leaks on parser failure.

## Test Signals
Exercise absent metrics, valid numeric metrics, invalid attribute lengths, out-of-range metric type, unknown feature bits, MSS/MTU/hoplimit clamping, known and unknown congestion-control names, ECN-CA feature propagation, and allocation failure cleanup.
