# sources/distributed-fs/ceph-client/block/blk-iocost.c

## Purpose
`blk-iocost.c` implements the cgroup v2 IO cost controller. It estimates I/O cost using a linear cost model, charges cgroups in device virtual time, throttles issuers that outrun their hierarchical share, dynamically adjusts the device virtual rate based on latency/rq-wait signals, and donates unused weight to maintain work conservation.

## Important APIs, Types, and Functions
The main per-device state is `struct ioc`, embedded as `rq_qos` and holding parameters, margins, vrate, timer, active cgroups, stats, autop profile state, and hweight generation. Per-device-cgroup state is `struct ioc_gq`, holding weights, inuse/active state, vtime/done_vtime, debt/delay, waitqueue, hweight caches, stats, and ancestor pointers. Per-cgroup state is `struct ioc_cgrp`, mostly the default weight.

Important functions include parameter setup (`ioc_refresh_period_us()`, `ioc_refresh_params_disk()`, `ioc_refresh_lcoefs()`), hweight propagation (`__propagate_weights()`, `current_hweight()`, `weight_updated()`), activation (`iocg_activate()`), throttling/debt (`ioc_rqos_throttle()`, `iocg_incur_debt()`, `iocg_pay_debt()`, `iocg_kick_waitq()`), donation (`hweight_after_donation()`, `transfer_surpluses()`), periodic control (`ioc_timer_fn()`, `ioc_check_iocgs()`, `ioc_adjust_base_vrate()`), cost calculation (`calc_vtime_cost_builtin()`), rq-qos hooks, and cgroup file handlers for `io.weight`, `io.cost.qos`, and `io.cost.model`.

## Control Flow
The controller is lazily initialized when root cgroup cost files are written for a queue. `blk_iocost_init()` allocates `struct ioc`, per-cpu stats, initializes timer/vtime/autop parameters, adds rq-qos hooks, and activates the blkcg policy. `io.cost.qos` enables/disables the controller, toggles request allocation-time accounting, quiesces the queue while changing settings, and disables default writeback throttling while iocost is enabled. `io.cost.model` freezes and quiesces the queue while changing linear model coefficients.

On bio issue, `ioc_rqos_throttle()` bypasses disabled/root/non-cost bios, calculates absolute cost from operation type, size, and sequential cursor, activates the leaf iocg, converts absolute cost to cgroup cost using current hweight, and either commits immediately or blocks on the iocg waitqueue until enough vtime budget exists. Bios that cannot safely block, such as root-issued or fatal-signal contexts, are issued as debt and later paid down from future budget while cgroup delay is applied. Merge hooks account extra cost for merged bios, often as debt if immediate budget is unavailable. Completion hooks advance `done_vtime` and collect latency/rq-wait signals.

The periodic timer updates active iocgs, wakes oversleeping waiters, deactivates idle groups, flushes stats up the hierarchy, detects surpluses and shortages, transfers donated inuse weight, adjusts vrate up/down based on request wait and latency misses, refreshes autop parameters, forgives old debt when the device is underutilized, and either starts the next period or returns to idle.

## State and Persistence
Runtime state spans rq-qos device objects, blkcg policy data, per-cpu counters, timers, hrtimers, waitqueues, active lists, cgroup file settings, and queue flags. There is no on-disk persistence; configuration lives in cgroupfs and runtime kernel objects. The controller maintains virtual-time accounting in microsecond-based wall time and high-resolution virtual time.

## Dependencies and Integration Points
This file integrates with blk-rq-qos, blkcg policy registration, cgroup v2 `io.*` files, blk-stat latency accounting, blk-wbt, blk-mq freeze/quiesce, request allocation timestamps, block tracepoints, and bio cgroup association. It depends on hierarchical cgroup topology through ancestor arrays and blkcg_gq parents.

## Risks
The high-risk areas are arithmetic overflow/rounding in hweight and vtime math, races between activation/deactivation and waitqueue/debt handling, timer lifecycle during policy teardown, cgroup removal while debt/delay exists, queue freeze/quiesce ordering during config writes, and fairness regressions from donation or vrate feedback. The code deliberately separates absolute cost from hweight-relative cost for debt so future hweight changes are accounted correctly.

## Test Signals
Useful tests include enabling/disabling on mq and non-mq queues, `io.weight` default and per-device parsing, `io.cost.qos` and `io.cost.model` invalid-token handling, latency/rq-wait vrate adjustment, multiple cgroup hierarchy fairness, debt path for root/fatal-signal bios, waitqueue wake timing, merge charging, idle deactivation, donation under underutilized groups, queue-depth changes, policy teardown with active timers, and tracepoint/`io.stat` counters for usage/wait/indebt/indelay.
