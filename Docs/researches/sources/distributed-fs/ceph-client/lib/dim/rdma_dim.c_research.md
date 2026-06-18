# sources/distributed-fs/ceph-client/lib/dim/rdma_dim.c

## Purpose
Implements the RDMA-specific Dynamic Interrupt Moderation tuning algorithm.

## APIs, Types, and Functions
The exported API is `rdma_dim(struct dim *dim, u64 completions)`. Internal helpers are `rdma_dim_step()`, `rdma_dim_stats_compare()`, and `rdma_dim_decision()`.

## Control Flow
`rdma_dim()` increments the measuring sample's event and completion counters, then follows the common DIM states. In measuring state it waits for `DIM_NEVENTS`, calculates stats, and calls `rdma_dim_decision()`. RDMA comparison prioritizes completions per millisecond and then completion-per-event ratio. The decision function turns direction on worse stats, steps on better stats, resets to profile zero for low completion-per-event ratios in same stats, and schedules work when the profile index changes.

## State and Persistence
All state is caller-owned in `struct dim`, especially sample counters, previous stats, profile index, tune state, and work item. There is no global mutable state.

## Dependencies and Integration Points
Depends on common DIM helpers from `dim.c`, `linux/dim.h`, and workqueues. It integrates with RDMA completion paths and driver work callbacks that apply new CQ moderation profiles.

## Risks and Test Signals
Risks include completion counter overflow assumptions, profile-index edge handling, oscillation under noisy RDMA workloads, and scheduling work after queue teardown. Test signals include synthetic completion-rate tests, profile edge tests, RDMA driver CQ moderation integration, and work cancellation/teardown races.
