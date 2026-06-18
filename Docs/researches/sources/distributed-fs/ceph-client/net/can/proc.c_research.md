# sources/distributed-fs/ceph-client/net/can/proc.c

## Purpose
Provides `/proc/net/can` visibility for the PF_CAN core. It exposes aggregate CAN frame statistics, a reset trigger, and receiver-list dumps for all-device and per-device CAN receive lists.

## Important APIs, Types, and Functions
Key public functions are `can_init_proc()`, `can_remove_proc()`, and timer callback `can_stat_update()`. Internal helpers include `can_init_stats()`, `calc_rate()`, `can_stats_proc_show()`, `can_reset_stats_proc_show()`, `can_rcvlist_proc_show()`, `can_rcvlist_sff_proc_show()`, `can_rcvlist_eff_proc_show()`, `can_print_rcvlist()`, and `can_print_recv_banner()`. The code reads `struct can_pkg_stats`, `struct can_rcv_lists_stats`, `struct can_dev_rcv_lists`, `struct receiver`, and per-net `net->can` proc entry pointers.

## Control Flow
`can_init_proc()` creates `/proc/net/can` and entries for `stats`, `reset_stats`, and each receiver-list view. `stats` prints total frame counters, matched frame counters, receive-list counts, and rate/ratio values when the stats timer is active. `reset_stats` sets a global `user_reset` flag; if the timer is inactive, it resets immediately. Receiver-list proc handlers enter an RCU read-side section, first print the all-device receive list, then iterate registered CAN netdevices and print their matching list buckets.

`can_stat_update()` runs once per second when enabled. It handles user reset, jiffies wrap, and counter overflow by reinitializing stats; otherwise it calculates total and current TX/RX rates, match ratios, maximums, clears delta counters, and re-arms the timer.

## State and Persistence
Statistics are per network namespace in `net->can.pkg_stats` and `net->can.rcv_lists_stats`. Proc dentries are stored in `net->can.pde_*`. `user_reset` is a file-global flag rather than per-net state, so reset requests are process-visible across namespaces until consumed. No data persists beyond runtime memory.

## Dependencies and Integration Points
Depends on procfs, seq_file, RCU, CAN receive-list internals from `af_can.h`, CAN core multi-list helpers, and netdevice iteration. It is compiled into the PF_CAN core path and assumes receiver lists are RCU-safe while printed.

## Risks
The main design risk is the global `user_reset` flag in otherwise per-net code. Proc output exposes function and user-data pointers through `%pK`, subject to kernel pointer restrictions. Rate calculations rely on periodic timer cadence and integer arithmetic, so very high counters force resets to avoid overflow. `can_init_proc()` does not unwind partially created entries if a later `proc_create_net_single()` fails.

## Test Signals
Useful signals are creation/removal of all proc entries per network namespace, accurate stats reset behavior with timer enabled and disabled, stable output under concurrent CAN filter registration/unregistration, correct all-device and per-interface receiver-list dumps, jiffies-wrap/overflow reset coverage, and no RCU or lockdep warnings while reading proc files under CAN traffic.
