# sources/distributed-fs/ceph-client/net/ipv4/tcp_hybla.c

## Purpose
`tcp_hybla.c` implements TCP Hybla, module name `hybla`, which compensates high-RTT paths by scaling slow-start and congestion-avoidance growth using a rho factor derived from measured RTT relative to a configurable reference RTT.

## Important APIs, Types, And Functions
`struct hybla` stores enable state, fractional cwnd credits, integer and fixed-point rho/rho-squared values, and minimum observed RTT. The key functions are `hybla_recalc_param()`, `hybla_init()`, `hybla_state()`, `hybla_fraction()`, and `hybla_cong_avoid()`. The module parameter `rtt0` is the reference RTT in milliseconds.

## Control Flow
Initialization sets cwnd/clamp, calculates rho from initial srtt, records minimum RTT, and sets cwnd to rho. On each congestion-avoidance call, the algorithm recalculates rho if a new minimum RTT appears. If the flow is not cwnd-limited, it returns. If Hybla is disabled because the CA state is not open, it delegates to Reno. In slow start it computes an exponential increment based on rho integer/fractional parts; outside slow start it computes `rho^2 / cwnd` in fixed-point units. Fractional increments are accumulated in `snd_cwnd_cents`, converted to packets when they reach 128, then cwnd is clamped to ssthresh and `snd_cwnd_clamp`.

## State, Persistence, Dependencies, And Integration
All growth state is per-socket; `rtt0` persists as a module parameter. The module integrates through TCP congestion ops and delegates ssthresh/undo to Reno. It depends on TCP srtt, cwnd helpers, and fixed-point tables for fractional powers.

## Risks And Test Signals
Risks include division by an invalid `rtt0`, excessive growth for high rho, fixed-point overflow in `1 << min(rho, 16)`, stale minimum RTT, and reduced behavior outside `TCP_CA_Open`. Tests should validate module parameter behavior, initialization with different RTTs, slow-start increments, congestion-avoidance fractional accumulation, state transitions to Reno fallback, cwnd clamp enforcement, and min-RTT recalculation.
