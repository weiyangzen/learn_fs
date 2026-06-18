# sources/distributed-fs/ceph-client/drivers/soundwire/stream.c

## Purpose

`stream.c` is the generic SoundWire stream state machine and bus reconfiguration engine. It allocates stream/master/slave/port runtimes, validates and configures streams, computes and programs transport/port parameters, prepares/deprepares ports, enables/disables channels, performs single-link and multi-link bank switches, and exposes ASoC helper APIs for startup/shutdown.

## Important APIs, types, and functions

- Exported frame shape tables and lookup helpers: `sdw_rows`, `sdw_cols`, `sdw_find_row_index()`, `sdw_find_col_index()`.
- Public stream lifecycle APIs: `sdw_alloc_stream()`, `sdw_release_stream()`, `sdw_prepare_stream()`, `sdw_enable_stream()`, `sdw_disable_stream()`, `sdw_deprepare_stream()`, `sdw_startup_stream()`, `sdw_shutdown_stream()`.
- Runtime membership APIs: `sdw_stream_add_master()`, `sdw_stream_remove_master()`, `sdw_stream_add_slave()`, `sdw_stream_remove_slave()`.
- `sdw_get_slave_dpn_prop()` finds source/sink port capability records.
- Internal programming helpers configure slave DPn registers, master port ops, channel enable, port prepare/deprepare, bus config callbacks, SDCA clock scaling, and bank switches.
- Lock helpers acquire all involved bus locks in bus-id order and release in reverse order.

## Control flow

ASoC startup allocates a stream and installs it on all DAIs. Slave and master drivers add their runtime portions with stream configuration and port configuration; adding the first slave moves the stream to `CONFIGURED`. `sdw_prepare_stream()` locks all buses, validates state, optionally updates bus bandwidth and recomputes bus parameters, programs transport and port parameters, performs a bank switch, prepares ports on the new bank, and moves to `PREPARED`.

`sdw_enable_stream()` reprograms parameters for already prepared/disabled streams, enables slave and master channel bits in the alternate bank, bank-switches, and marks `ENABLED`. `sdw_disable_stream()` disables channel bits, marks `DISABLED`, reprograms active stream params, bank-switches, then disables the previous current bank too. `sdw_deprepare_stream()` marks `DEPREPARED`, deprepares ports, subtracts bandwidth including multi-lane accounting, recomputes/programs bus params, and bank-switches.

Bank switching writes broadcast frame control to `next_bank`. In multi-link mode, transfers are deferred with SSP sync and completed after controller `post_bank_switch()` triggers hardware sync; otherwise the bank toggles immediately. Error paths free deferred message buffers and unlock message locks.

## State and persistence behavior

Software state is spread across `sdw_stream_runtime` (`state`, params, master list, type, runtime count), `sdw_master_runtime`, `sdw_slave_runtime`, `sdw_port_runtime`, `bus->params`, bus bandwidth/lane usage, stream refcounts, and BPT refcounts. Hardware state is programmed into slave DPn/DP0 registers, master port registers via controller callbacks, bus frame control banks, and channel enable bits. The state machine allows only specific transitions and treats BPT streams as mutually exclusive with audio streams on a bus.

## Dependencies and integration points

This file depends on SoundWire register definitions, generic bus transfer APIs, controller `sdw_master_ops`/`sdw_master_port_ops`, slave driver `port_prep` and `bus_config` callbacks, SDCA clock scaling helpers, and ASoC DAI stream plumbing. Intel and Qualcomm drivers both rely on these exported APIs for PCM and BPT streams.

## Risks and edge cases

- State transitions are strict; callers that remove members or call prepare/enable out of order get `-EINVAL`.
- `_sdw_prepare_stream()` restores only one `bus->params` snapshot on error, even though it can iterate multiple buses; multi-bus error recovery should be reviewed.
- Multi-link locking combines bus locks and `msg_lock`; ordering and error unlock paths are critical.
- Port preparation polls while holding `bus_lock` because interrupts cannot be used in that context; bad timeouts can block stream setup.
- BPT streams are constrained to DP0 and mutually exclusive with audio streams by bus refcounts.
- Bandwidth accounting for multi-lane ports subtracts lane-specific bandwidth during deprepare; incorrect lane assignment can underflow counters.
- Several TODOs note missing port capability validation and asynchronous mode support.

## Test signals

Exercise all public stream transitions, invalid transition rejection, single-link and multi-link bank switch, multi-master lock ordering, BPT exclusivity, DP0 and DPn port prepare/deprepare, simple and full port types, read-only word length, SDCA clock scaling, lane-control bandwidth accounting, slave driver port callbacks, and failure injection for transfer, controller port ops, compute params, and bus_config callbacks. Lockdep and KASAN are high-value for this file.
