# sources/distributed-fs/ceph-client/include/linux/irq_poll.h

## Purpose
`irq_poll.h` declares the lightweight IRQ polling abstraction for drivers that need NAPI-like deferred polling outside the networking stack.

## Important APIs, types, and functions
It defines `irq_poll_fn`, `struct irq_poll` with list, state, weight, and callback, state bits `IRQ_POLL_F_SCHED` and `IRQ_POLL_F_DISABLE`, and APIs `irq_poll_sched`, `irq_poll_init`, `irq_poll_complete`, `irq_poll_enable`, and `irq_poll_disable`.

## Control flow
Drivers initialize a poll object with weight and callback, schedule it from interrupt context, process work in the poll callback, and call complete/enable/disable as work drains or devices stop.

## State and persistence
State is runtime-only in the poll object and core poll lists. There is no persistence.

## Dependencies and integration points
It integrates with block/storage and other drivers needing interrupt mitigation, list management, and softirq-like polling infrastructure.

## Risks and test signals
Risks include scheduling after disable, failing to complete, weight starvation, and lifetime races during device removal. Tests should cover concurrent schedule/disable, callback budget exhaustion, completion rearm, and teardown with pending work.
