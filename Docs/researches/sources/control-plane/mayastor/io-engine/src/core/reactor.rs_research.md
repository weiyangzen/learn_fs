# sources/control-plane/mayastor/io-engine/src/core/reactor.rs

## Purpose
Implements the io-engine reactor runtime: one reactor per SPDK lcore, SPDK thread scheduling, Rust future dispatch, poll/interrupt-mode loops, shutdown, and freeze monitoring.

## Important APIs, Types, and Functions
- `ReactorState` includes `Init`, `Running`, `Shutdown`, `Delayed`, and `Interrupt`.
- `Reactors::init`, `launch_master`, `launch_remote`, `current`, `master`, `iter`, and SPDK thread scheduling callbacks manage global reactor setup.
- `Reactor::send_future`, `spawn_local`, `block_on`, `spawn_at`, and `spawn_at_primary` bridge futures to reactor/SPDK threads.
- `poll_reactor`, `poll_once`, `poll_times`, `add_incoming`, `destroy_exited`, `enter_interrupt_mode`, and `leave_interrupt_mode` drive execution.
- `Future for &'static Reactor` lets Tokio poll the master reactor.
- `reactor_monitor_loop` schedules heartbeat futures and emits freeze/unfreeze events.

## Control Flow and State
Initialization configures SPDK thread library, optionally enables global interrupt mode, creates reactors for all cores, and creates an init SPDK thread. SPDK thread creation is routed through `Reactors::do_op`, which schedules new threads onto reactors matching CPU masks and wakes sleeping reactors. Each reactor drains cross-core futures, runs local async tasks, polls SPDK threads, accepts incoming SPDK threads, and destroys exited ones. In interrupt mode, per-thread fd groups are nested under a reactor fd group and an eventfd wakes the reactor for Rust futures. Shutdown changes state, exits interrupt mode, waits/destroys threads, and joins remote cores.

State includes per-reactor thread queues, incoming queues, future channels, fd groups, wakeup fd, reactor state, and TID. It is process-local only.

## Dependencies and Integration Points
Depends on SPDK thread/fd group APIs, `async_task`, `crossbeam`, `Cores`, `events_api`, diagnostics, and configuration env helpers. It underpins gRPC management, bdev operations, device monitor, and environment startup/shutdown.

## Risks and Test Signals
Reactor context is safety-critical: many SPDK APIs require the correct current SPDK thread. Interrupt mode has partial-nesting rollback paths that must prevent silent poller loss. `send_future` writes to eventfd without checking short/error writes. Freeze detection schedules heartbeats and can mark a reactor frozen if futures are queued behind long work. Tests should cover cross-core `spawn_at`, interrupt-mode enter/exit with incoming threads, shutdown with remaining threads, freeze/unfreeze events, and developer delay mode.
