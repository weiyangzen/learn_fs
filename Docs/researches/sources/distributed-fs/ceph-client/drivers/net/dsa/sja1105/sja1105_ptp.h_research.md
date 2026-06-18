# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_ptp.h

## Purpose

This header defines the SJA1105 PTP interface used by the driver when `CONFIG_NET_DSA_SJA1105_PTP` is enabled, and provides no-op stubs when it is disabled. It is the shared contract between main DSA operations, TAS scheduling, tagger timestamp handling, and the PTP implementation.

## Important APIs, Types, and Data

- `SJA1105_TICK_NS` defines the hardware clock tick as 8 ns.
- `ns_to_sja1105_ticks()` and `sja1105_ticks_to_ns()` convert between nanoseconds and hardware ticks.
- `future_base_time()` computes the first schedule base time at or after `now`.
- `ns_to_sja1105_delta()` and `sja1105_delta_to_ns()` convert TAS correction deltas in 200 ns units.
- `struct sja1105_ptp_cmd` mirrors PTP control bits for clock pin start/stop, schedule start/stop, reset, corrected clock timestamps, and add/set mode.
- `struct sja1105_ptp_data` stores PTP runtime state when enabled, or only a mutex when disabled.
- The header declares PHC registration, timestamp callbacks, hwtstamp callbacks, internal PHC get/set/adjust helpers, command commit, per-generation command packers, and SJA1110 meta timestamp handling.

## Control Flow

With PTP enabled, callers use the declared functions implemented in `sja1105_ptp.c`. With PTP disabled, the header substitutes inline stubs or `NULL` callback macros. This lets `sja1105_main.c` keep the same structure fields and DSA ops wiring while compiling out actual PHC/timestamp behavior.

The inline conversion helpers are used by PTP and TAS code to keep time arithmetic consistent. `future_base_time()` avoids starting periodic output or schedules in the past by advancing by an integer number of cycles.

## State and Persistence Behavior

When enabled, `struct sja1105_ptp_data` owns timers, queues, PHC registration state, command shadow, lock, EXTS enable state, and last sync timestamp. When disabled, only the lock remains because reload code still uses `priv->ptp_data.lock` for common lock ordering. Stubbed get/set/adjust functions return success, so reload code can compile and run without PTP hardware-clock preservation work.

## Dependencies and Integration Points

The header depends on Linux timer support and is guarded by `IS_ENABLED(CONFIG_NET_DSA_SJA1105_PTP)`. It integrates with `sja1105_main.c`, `sja1105_ptp.c`, `sja1105_tas.c`, and tagger metadata paths. Public callback declarations match DSA timestamp and hwtstamp operation signatures.

## Risks and Edge Cases

- When PTP is disabled, several DSA callbacks are `NULL`; call sites must tolerate disabled timestamp support.
- Stubbed internal PHC functions return zero without touching output values, so code that uses outputs must only do so in contexts where PTP is enabled or the value is otherwise irrelevant.
- Time conversion helpers use integer division and truncate sub-tick/sub-delta values.
- `future_base_time()` assumes positive cycle time; callers must validate cycle values.

## Test Signals

Build testing should cover both `CONFIG_NET_DSA_SJA1105_PTP=y/m` and disabled configurations. Enabled builds should expose PHC/timestamp callbacks and compile TAS users of conversion helpers. Disabled builds should still compile main reload logic, DSA ops should omit timestamp callbacks through `NULL` macros, and probe/setup should proceed without PTP clock registration.
