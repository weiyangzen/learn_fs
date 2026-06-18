# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpts.h

## Purpose
`cpts.h` defines the public data structures, register layout, constants, and inline/no-op helpers for the TI CPTS module. It is the contract between CPTS implementation code and Ethernet drivers that optionally enable `CONFIG_TI_CPTS`.

## Important APIs, Types, and Functions
`struct cpsw_cpts` maps the CPTS register block, including control, refclock select, timestamp push/load, interrupt status, FIFO pop, and event high/low registers. `struct cpts_event` represents a queued FIFO event with timeout and converted timestamp. `struct cpts` holds device state: register base, PHC metadata, cyclecounter/timecounter, reference clock, event pool, TX SKB queue, lock/mutex, IRQ-poll mode, completion, and external timestamp enable bits. The header declares `cpts_rx_timestamp()`, `cpts_tx_timestamp()`, lifecycle functions, `cpts_misc_interrupt()`, and inline helpers `cpts_can_timestamp()` and `cpts_set_irqpoll()`.

## Control Flow and State
The header documents the state model used by `cpts.c`: hardware emits typed events encoded in `EVENT_HIGH`, with event type, port, PTP message type, and sequence ID masks. The software pool is bounded by `CPTS_MAX_EVENTS`, while the hardware FIFO depth is `CPTS_FIFO_DEPTH`. `cpts_can_timestamp()` is a fast packet-classification gate that checks `ptp_classify_raw()` before drivers spend work on CPTS timestamping.

## Dependencies and Integration Points
When CPTS is enabled, consumers need Linux clock, timecounter, PTP clock kernel, SKB, list, OF, and PTP classifier types. When disabled, the header supplies no-op stubs so callers can compile without scattered `#ifdef`s; `cpts_create()` returns `NULL`, registration succeeds, timestamp hooks do nothing, and `cpts_can_timestamp()` returns false.

## Risks and Test Signals
Because `struct cpts` is exposed to companion drivers, field lifetime and locking assumptions are part of the ABI inside the kernel tree. Callers must not use no-op mode as though a PHC exists. Tests should cover both `CONFIG_TI_CPTS=y/m` and disabled builds, verify callers handle `NULL` from stub `cpts_create()`, and validate that inline classification does not alter SKB state.
