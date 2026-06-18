# `sources/distributed-fs/ceph-client/drivers/md/dm-delay.c`

## Purpose

`dm-delay.c` implements the `delay` target, a testing and simulation target that remaps reads, writes, and flushes to configured devices while delaying each class independently. It can use the same backing mapping for all operations, separate read/write mappings, or separate read/write/flush mappings.

## Important APIs, Types, and Functions

`struct delay_class` stores a `dm_dev`, starting sector, millisecond delay, and active operation count for one IO class. `struct delay_c` owns the delayed-bio list, timer or low-latency worker, workqueue, locks, `may_delay` suspend gate, and the three classes. `delay_ctr()` parses 3, 6, or 9 arguments and chooses either a kthread for delays under 50 ms or a timer plus workqueue for longer delays. `delay_map()` selects read/write/flush class, remaps the bio, and delegates to `delay_bio()`. `flush_delayed_bios()` drains expired or all delayed bios, decrements class counters, rearms timers, and submits bios through `dm_submit_bio_remap()`.

## Control Flow

Mapped bios are immediately rewritten to the selected backing device and sector. If the selected class delay is zero, `delay_bio()` returns `DM_MAPIO_REMAPPED`. Otherwise, per-bio `dm_delay_info` is filled, the bio is appended to `delayed_bios`, and either the fast kthread is woken or the timer is reduced to the new expiry. The timer queues `flush_expired_bios()` on `kdelayd`; the fast worker loops, drains expired bios, and sleeps for a fraction of the minimum requested delay.

Suspend sets `may_delay=false`, deletes the timer for timer mode, and flushes all delayed bios. Resume re-enables delay for future IO. Destruction shuts down timer/workqueue or kthread and releases every referenced `dm_dev`.

## State and Persistence Behavior

The target has no persistent metadata. Runtime state is the delayed bio queue and per-class operation counters. The `process_bios_lock` serializes list extraction and flushing, while `delayed_bios_lock` protects list mutation and suspend gating.

## Dependencies and Integration Points

The target integrates through `.ctr`, `.dtr`, `.map`, `.presuspend`, `.resume`, `.status`, `.iterate_devices`, and optional zoned `.report_zones`. It uses device-mapper per-bio data, timers, workqueues, kthreads, bio lists, and `dm_report_zones()` for the read class. It advertises integrity pass-through and host-managed zoned support.

## Risks and Edge Cases

Suspend races are controlled by `may_delay` under the list spinlock, but latency behavior depends on jiffies granularity for timer mode and sleep interval selection for fast mode. The constructor may acquire the same device multiple times when read/write/flush share arguments, so destructor must release all three class references. Status info reports in-flight delayed counts and can be used to detect leaks.

## Test Signals

Tests should cover 3/6/9 argument tables, zero delay pass-through, short-delay kthread mode, long-delay timer mode, flush-specific routing, suspend flushing, status counters, and zoned report forwarding from the read device. Timing tests should allow scheduler tolerance while verifying ordering and eventual completion.
