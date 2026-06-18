# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpts.c

## Purpose
`cpts.c` implements the TI Common Platform Time Sync helper used by CPSW/EMAC-style Ethernet drivers to expose a PTP hardware clock and attach hardware timestamps to PTP packets. It manages the CPTS event FIFO, converts the 32-bit hardware counter through Linux `cyclecounter`/`timecounter`, registers a PHC through `ptp_clock_register()`, and provides exported RX/TX timestamp hooks for network drivers.

## Important APIs, Types, and Functions
The exported surface is `cpts_create()`, `cpts_release()`, `cpts_register()`, `cpts_unregister()`, `cpts_rx_timestamp()`, `cpts_tx_timestamp()`, and `cpts_misc_interrupt()`. Internally, `cpts_fifo_read()` drains hardware events, `cpts_update_cur_time()` pushes a timestamp event to sync the timecounter, `cpts_match_tx_ts()` matches deferred TX timestamp events against queued SKBs, and `cpts_find_ts()` finds RX events by PTP message type/sequence ID. The PTP callbacks are `cpts_ptp_adjfine()`, `cpts_ptp_adjtime()`, `cpts_ptp_gettimeex()`, `cpts_ptp_settime()`, `cpts_ptp_enable()`, and `cpts_overflow_check()`.

## Control Flow and State
`cpts_create()` allocates state, parses DT clock conversion hints and optional refclock mux data, prepares the CPTS clock, initializes locks/completions, calculates multiplier/shift, and leaves the device disabled. `cpts_register()` initializes the event pool and TX queue, enables the reference clock and CPTS interrupt bit, initializes the timecounter, registers the PHC, and schedules overflow work. Hardware FIFO entries are converted into `struct cpts_event` objects from a fixed pool; RX/TX events move to `cpts->events`, push events update `cur_timestamp`, and hardware events become `PTP_CLOCK_EXTTS` notifications. TX timestamping defers SKBs into `cpts->txq` and the PTP worker later matches them by encoded PTP message type and sequence ID.

## Dependencies and Integration Points
This file depends on Linux PTP, timecounter, clock, workqueue, SKB timestamping, DT clock provider, and packet classification helpers. The owning Ethernet driver must call RX/TX timestamp hooks around packet handling and call `cpts_misc_interrupt()` if using interrupt-driven CPTS FIFO draining. `cpts_set_irqpoll()` from the header selects completion-based interrupt mode versus direct polling.

## Risks and Test Signals
The event pool is fixed at `CPTS_MAX_EVENTS`; high timestamp rates can exhaust it and depend on timeout purging. TX timestamp matching is by PTP mtype/sequence ID plus event type, so duplicate sequence IDs in flight can misassociate timestamps. `cpts_ptp_adjfine()` applies `mult_new` only after a push event, making timestamp-push failure visible as clock adjustment lag. Test signals include PHC registration/index, `phc2sys`/`ptp4l` stability, RX/TX hardware timestamp delivery, external timestamp events, FIFO overflow/purge warnings, suspend/remove unregister cleanup, and timeout logs from `cpts_update_cur_time()`.
