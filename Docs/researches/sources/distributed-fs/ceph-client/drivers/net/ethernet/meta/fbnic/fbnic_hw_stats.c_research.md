# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_hw_stats.c

## Purpose

`fbnic_hw_stats.c` reads, resets, and accumulates FBNIC hardware statistics. It converts raw 32-bit and split 64-bit hardware counters into monotonically increasing software counters, grouped by PHY/FEC/PCS, MAC, TMI, TTI, RPC, RXB, per-queue RDE, and PCIe/PUL categories. Ethtool and debugfs use these accumulated counters for user-visible stats.

## Important APIs, Types, And Functions

Public functions are `fbnic_stat_rd64()`, `fbnic_reset_hw_stats()`, `fbnic_init_hw_stats()`, `fbnic_get_hw_q_stats()`, `fbnic_get_hw_stats32()`, and `fbnic_get_hw_stats()`. Internal helpers are organized per stats block: reset/get for TMI, TTI, RPC, RXB fifo/enqueue/dequeue, per-queue Rx hardware stats, PCIe stats, PHY stats, and MAC stats.

`fbnic_hw_stat_rst32()`/`fbnic_hw_stat_rd32()` snapshot and accumulate 32-bit counters. `fbnic_hw_stat_rst64()`/`fbnic_hw_stat_rd64()` do the same for split 64-bit counters using `fbnic_stat_rd64()`. `fbnic_stat_rd64()` reads upper-lower-upper and returns a stable full value when upper does not change, or only the upper bits with a warning when the upper half changes too quickly.

## Control Flow

Initialization calls `spin_lock_init()` and then `fbnic_reset_hw_stats()`. Reset paths record current hardware counter baselines without clearing `value`, allowing counters to continue across device resets or power transitions after the initial zeroed allocation. `fbnic_reset_hw_stats()` resets spinlock-protected PHY/TMI/TTI/RPC/RXB/RDE/PCIe state, then resets MAC stats outside the spinlock under RTNL assumptions once a netdev exists.

`fbnic_get_hw_stats32()` locks `hw_stats.lock` and updates only 32-bit-style counters plus PHY 32-bit callbacks. `fbnic_get_hw_stats()` locks, updates 32-bit counters first, then reads wider byte/PCIe counters. Per-queue helper `fbnic_get_hw_q_stats()` updates RDE queue counters under the same lock. MAC stats are fetched via `fbd->mac` callbacks in reset and via ethtool-specific paths outside this file.

## State And Persistence

Each `struct fbnic_stat_counter` stores accumulated `value`, old hardware snapshot, and a `reported` flag used by MAC/ethtool code. State is in `fbd->hw_stats` and persists in memory for the life of the device object. Baseline snapshots are reset after hardware reset, but `value` is intentionally not cleared except by initial allocation.

## Dependencies And Integration Points

The file depends on CSR register definitions, `rd32()`, device warnings, spinlocks, RTNL assertions, and MAC operation callbacks for FEC/PCS/MAC/pause/control/RMON stats. It integrates with `fbnic_ethtool.c` stats callbacks, `fbnic_debugfs.c` PCIe stats display, and device reset/open paths that call reset/init.

## Risks And Edge Cases

Split 64-bit reads can be inconsistent under very fast counter updates; the implementation warns once and drops lower bits for that sample. Resetting baselines without clearing `value` is deliberate; code that expects reset-to-zero after PCI recovery would be wrong. `fbnic_reset_rxb_stats()` iterates `FBNIC_RXB_INTF_INDICES` for enqueue/dequeue arrays, which must remain compatible with array sizes from the header. MAC stats rely on RTNL rather than the hw_stats spinlock once registered, so callers must respect that locking contract.

## Test Signals

Useful tests include stats starting at zero after probe despite nonzero hardware counters, monotonic increases across traffic and reset, wraparound handling for 32-bit counters, split-64 warning behavior under simulated fast updates, per-queue stats bounded by `fbd->max_num_queues`, ethtool stats string/value alignment, and debugfs PCIe stats refresh. No executable tests were run for this research item.
