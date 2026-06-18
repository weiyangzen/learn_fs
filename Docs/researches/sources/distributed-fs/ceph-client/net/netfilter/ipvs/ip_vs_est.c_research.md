# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_est.c

## Purpose
`ip_vs_est.c` implements IPVS rate estimation for total, service, and destination statistics. It periodically folds per-CPU packet/byte/connection counters into aggregate counters and exponentially smoothed rates for connections per second, packets per second, and bytes per second. It uses per-netns estimator kthreads, dynamic chain distribution, and reload logic driven by estimator sysctls.

## Important APIs, types, and functions
Externally used functions are `ip_vs_est_reload_start()`, `ip_vs_est_kthread_start()`, `ip_vs_est_kthread_stop()`, `ip_vs_start_estimator()`, `ip_vs_stop_estimator()`, `ip_vs_zero_estimator()`, `ip_vs_read_estimator()`, `ip_vs_estimator_net_init()`, and `ip_vs_estimator_net_cleanup()`. Important internals include `ip_vs_chain_estimation()`, `ip_vs_tick_estimation()`, `ip_vs_estimation_kthread()`, `ip_vs_est_set_params()`, `ip_vs_est_add_kthread()`, `ip_vs_est_update_ktid()`, `ip_vs_enqueue_estimator()`, `ip_vs_est_drain_temp_list()`, `ip_vs_est_calc_limits()`, and `ip_vs_est_calc_phase()`. The key data structures are embedded in `struct netns_ipvs`, `struct ip_vs_stats`, `struct ip_vs_estimator`, `struct ip_vs_est_kt_data`, and `struct ip_vs_est_tick_data`.

## Control flow
Stats objects call `ip_vs_start_estimator()` after their per-CPU counters are allocated. The estimator starts on `est_temp_list`, creating kthread-0 context if needed. Kthread tasks are only started after the first service enables IPVS; reload work starts, stops, or restarts tasks based on config generation and `run_estimation` state. Kthread 0 can enter calculation phase, benchmark a synthetic estimator chain, choose a chain length target, stop other tasks, move existing estimators back to the temporary list, apply new limits, and then drain the temporary list into tick chains.

Each estimator kthread sleeps around `IPVS_EST_TICK`, iterates rows in a ring of `IPVS_EST_NTICKS`, and estimates only chains present in that row. `ip_vs_chain_estimation()` sums all possible CPUs using `u64_stats_fetch_begin/retry`, updates aggregate `kstats`, calculates deltas since the previous sample, and applies a smoothing factor of 1/4. Packets/connections are stored scaled by 2^10, bytes by 2^5, then decoded by `ip_vs_read_estimator()`.

Stopping an estimator removes it either from `est_temp_list` or its assigned tick chain, updates chain length/full/available bookkeeping, frees empty tick data through RCU, destroys unused nonzero kthread contexts, and may request kthread-0 stop when all estimator work is gone. Netns cleanup stops all tasks, frees the kthread array, and destroys the estimator mutex.

## State and persistence behavior
All estimator state is in-memory per netns. `est_temp_list` buffers newly added or rebalanced estimators. `est_kt_arr` stores kthread contexts, each with tick rows, chain fullness bitmaps, current row, scheduling timer, count limits, and optional benchmark stats. `est_genid` and `est_genid_done` coordinate reloads; `est_calc_phase`, `est_chain_max`, `est_add_ktid`, and `est_max_threads` determine placement. Individual estimators retain last counter snapshots and scaled smoothed rates. Zeroing stats resets the estimator baseline and rates while preserving current aggregate counters.

## Dependencies and integration points
The estimator consumes per-CPU stats allocated by `ip_vs_ctl.c` and updated by packet paths in `ip_vs_core.c`. Sysctl handlers in `ip_vs_ctl.c` change CPU affinity, nice level, run/stop state, and maximum threads, then call `ip_vs_est_reload_start()`. Service and destination add/delete paths call start/stop. Procfs and netlink stats export call `ip_vs_read_estimator()`. It depends on kthreads, RCU hlist traversal, jiffies, cpumask and housekeeping CPU selection, mutexes shared with service/control logic, and `u64_stats` synchronization with softirq writers.

## Risks and edge cases
The code has subtle locking rules: `service_mutex` protects temporary list and many kthread array mutations, while `est_mutex` protects reload/config/task state. Kthread 0 is special and kept even when empty. Calculation phase intentionally stops other tasks and moves estimators without waiting for RCU grace because tasks are stopped. Estimator addition can fail and leave entries on the temporary list for later. Time drift is corrected if a thread wakes too late. CPU hotplug/frequency changes and cpulist restrictions influence benchmarked chain limits. Readers get smoothed rates that lag real counters by design.

## Test signals
Test adding/removing services and destinations to verify estimator lifecycle, total stats estimator startup before and after first service, proc/netlink rate output after traffic, zero-stat baseline behavior, `run_estimation` toggling, cpulist and nice sysctl reloads, kthread scaling with many estimators, deletion while estimators sit on `est_temp_list`, namespace cleanup with live estimator tasks, and high packet-rate per-CPU counter reads without torn 64-bit values.
