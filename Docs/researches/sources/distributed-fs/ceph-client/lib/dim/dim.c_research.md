# sources/distributed-fs/ceph-client/lib/dim/dim.c

## Purpose
Provides common state-machine helpers and statistics calculation for Dynamic Interrupt Moderation.

## APIs, Types, and Functions
Exports `dim_on_top()`, `dim_turn()`, `dim_park_on_top()`, `dim_park_tired()`, and `dim_calc_stats()`. These operate on `struct dim`, `struct dim_sample`, and `struct dim_stats` from `<linux/dim.h>`.

## Control Flow
`dim_on_top()` interprets tuning direction and step counters to decide whether a local optimum has been reached. `dim_turn()` flips between left and right tuning directions and resets the new direction's step counter. Parking helpers reset counters and set parking states. `dim_calc_stats()` computes elapsed microseconds and counter deltas with wrap handling, then derives packets, bytes, events, completions per millisecond, and completion-per-event ratio.

## State and Persistence
The functions mutate caller-owned `struct dim` state only. No global state is maintained. Statistics are derived from caller-provided samples.

## Dependencies and Integration Points
Depends on `linux/dim.h`, time delta helpers, bit-gap counter wrap helpers, and module export infrastructure. It is shared by `net_dim.c`, `rdma_dim.c`, and drivers using DIM.

## Risks and Test Signals
Risks include divide-by-zero without the zero-delta guard, counter wrap mistakes, misclassifying local optimum state, and tuning oscillation from wrong step counters. Test signals include synthetic sample deltas, wraparound tests, state-machine unit tests for each tune state, and driver-level interrupt moderation behavior.
