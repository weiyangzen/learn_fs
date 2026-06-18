# sources/distributed-fs/ceph-client/net/sched/sch_cbs.c

## Purpose
`sch_cbs.c` implements the IEEE 802.1Q Credit Based Shaper qdisc for time-sensitive networking workloads. It rate-limits a traffic class using credits that accumulate at `idleslope` while packets wait and deplete at `sendslope` while packets transmit. It can operate in software or request hardware offload through the device driver's `ndo_setup_tc()`.

## Important APIs, Types, and Functions
`struct cbs_sched_data` stores offload mode, TX queue index, port rate, last transmission timestamp, current credits, configured high/low credits, slopes, watchdog, child qdisc, and selected enqueue/dequeue function pointers. The software datapath is `cbs_enqueue_soft()` and `cbs_dequeue_soft()`; offloaded mode uses `cbs_enqueue_offload()` and `cbs_dequeue_offload()`. Helpers include `timediff_to_credits()`, `delay_from_credits()`, `credits_from_len()`, `cbs_child_enqueue()`, and `cbs_child_dequeue()`.

Configuration and integration functions are `cbs_change()`, `cbs_init()`, `cbs_reset()`, `cbs_destroy()`, `cbs_dump()`, `cbs_enable_offload()`, `cbs_disable_offload()`, `cbs_set_port_rate()`, and `cbs_dev_notifier()`. Classful wrapper operations expose one child through `cbs_graft()`, `cbs_leaf()`, `cbs_find()`, `cbs_walk()`, and `cbs_dump_class()`.

## Control Flow
Initialization requires `TCA_CBS_PARMS`, creates a default `pfifo` child qdisc, registers the child in the qdisc hash, adds the CBS instance to a global notifier list, computes the TX queue index, initializes software enqueue/dequeue callbacks, sets up the watchdog, and then applies the supplied parameters.

On software enqueue, if the queue was empty and credits are positive, credits are reset to zero and `last` is set to now so an idle class stops accumulating credit. The packet is then enqueued into the child, while parent qlen/backlog are incremented. On software dequeue, CBS waits until any previously transmitted packet's estimated finish time has passed. If credits are negative, it accumulates credits according to elapsed time and `idleslope`; if credits are still negative, it schedules the watchdog for the time credits should reach zero and returns `NULL`. Once eligible, it dequeues from the child, subtracts credits according to packet length and `sendslope / port_rate`, clamps to `locredit`, and estimates the next finish timestamp using the current port rate.

In offload mode, configuration calls `ndo_setup_tc(dev, TC_SETUP_QDISC_CBS, ...)` with queue and credit parameters. The software qdisc still wraps the child queue for accounting, but dequeue no longer enforces credit timing; the hardware is expected to shape. Device up/change notifications update `port_rate` from ethtool link settings for software mode.

## State and Persistence
CBS keeps all state in memory. Persistent-looking configuration such as `idleslope`, `sendslope`, `hicredit`, `locredit`, and offload mode is only qdisc-private state visible through netlink dumps. `port_rate` is an atomic bytes-per-second value updated by notifier events. `last`, `credits`, and watchdog state are runtime scheduling state. A global `cbs_list` protected by `cbs_list_lock` tracks active instances for link speed updates.

## Dependencies and Integration Points
The qdisc depends on `pfifo_qdisc_ops` for its default child, `qdisc_watchdog` from `sch_api.c`, ethtool link settings, netdevice notifiers, `TC_SETUP_QDISC_CBS` hardware offload, and `TCA_CBS_PARMS` netlink configuration. As a one-class qdisc it integrates with tc graft/leaf/dump flows and can have its child replaced.

## Risks
Credit math uses signed 64-bit nanosecond and bytes-per-second products; extreme slopes, long time deltas, or zero port rate paths must avoid overflow and division errors. Software shaping accuracy depends on correct port speed detection; fallback speed is 10 Mbps if ethtool data is unavailable. Offload transition must restore software callbacks on disable and avoid leaving hardware shaping enabled after destroy. The notifier finds a single matching instance and then updates outside the spinlock, so list lifetime is protected by RTNL assumptions.

## Test Signals
Test mandatory-parameter validation, software shaping with positive/negative credit transitions, watchdog wakeups after negative credits, link speed change updates, offload success/failure/disable paths, grafting a replacement child qdisc, reset clearing credits and child queue, dump round-tripping slopes in kbit/s, and qlen/backlog consistency between parent and child.
