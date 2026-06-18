<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dim.h -->
# sources/distributed-fs/ceph-client/include/linux/dim.h

## Purpose
Defines Dynamic Interrupt Moderation data structures and APIs for network and RDMA drivers to adapt completion interrupt coalescing based on measured traffic.

## Important APIs, Types, And Functions
Important types include `struct dim_cq_moder`, `struct dim_irq_moder`, `struct dim_sample`, `struct dim_stats`, and `struct dim`. State enums describe CQ period mode, algorithm state, tune state, stats verdict, and step result. Network APIs include `net_dim_init_irq_moder()`, `net_dim_free_irq_moder()`, `net_dim_setting()`, `net_dim_work_cancel()`, moderation profile getters/setters, and `net_dim()`. RDMA uses `rdma_dim()`. Helpers include `dim_update_sample()`, `dim_update_sample_with_comps()`, `dim_calc_stats()`, `dim_turn()`, and parking helpers.

## Control Flow
Consumers periodically capture packet, byte, event, and completion counters into `dim_sample`. `net_dim()` or `rdma_dim()` waits for enough events, computes deltas with wraparound handling, compares current stats with previous stats, and transitions the tuning state. When a new profile is needed, it schedules the embedded work item so the driver can apply new CQ moderation outside the fast path.

## State And Persistence
Each `struct dim` stores the algorithm state, previous stats, start/measuring samples, profile index, CQ mode, step direction, and parking counters. Network devices may hold RCU-protected RX/TX profile arrays in `struct dim_irq_moder`. There is no persistence beyond live driver state.

## Dependencies And Integration Points
Depends on workqueues, RCU, `ktime_get()`, kernel bit helpers, and net/RDMA driver CQ moderation controls. It integrates with ethtool coalesce support through profile and coalesce capability flags.

## Risks And Edge Cases
Counter wraparound and small time deltas can produce unreliable stats. The worker must be cancelled during teardown. Profile index bounds are fixed by network and RDMA profile counts. RCU profile replacement must not expose freed moderation tables. Applying moderation in the wrong context can race with device reset or queue teardown.

## Test Signals
Tests should simulate increasing/decreasing traffic, counter wraparound, unchanged traffic parking, event-count gating, RX and TX profile selection, RDMA completion-only sampling, RCU profile update/free, and teardown with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dim.h -->
