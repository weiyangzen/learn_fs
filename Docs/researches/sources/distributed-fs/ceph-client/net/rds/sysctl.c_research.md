# sources/distributed-fs/ceph-client/net/rds/sysctl.c

## Purpose
Defines the global `/proc/sys/net/rds` controls for reconnect backoff, ACK cadence, and ping behavior used by the RDS core.

## Important APIs, Types, and Functions
Exports runtime variables `rds_sysctl_reconnect_min_jiffies`, `rds_sysctl_reconnect_max_jiffies`, `rds_sysctl_max_unacked_packets`, `rds_sysctl_max_unacked_bytes`, and `rds_sysctl_ping_enable`. `rds_sysctl_init()` initializes and registers the table under init_net, and `rds_sysctl_exit()` unregisters it.

## Control Flow
The sysctl table uses `proc_doulongvec_ms_jiffies_minmax` for reconnect delays and `proc_dointvec` for ACK/ping integer controls. Init converts the minimum reconnect delay from milliseconds to jiffies before registration. Writes mutate the exported globals directly, so reconnect scheduling and send ACK pacing pick up new values without restart.

## State and Persistence
State is global kernel memory exposed through sysctl. It is not per-netns in this file and is not persisted across reboot unless user space reapplies settings.

## Dependencies and Integration
Used by `threads.c` reconnect backoff and by `send.c` to set `cp_unacked_packets` and `cp_unacked_bytes`. Depends on sysctl/proc support and RDS core initialization order.

## Risks and Test Signals
Risks include invalid tuning that can increase reconnect storms or ACK pressure, plus global rather than per-netns scope. Test signals are sysctl registration at `net/rds`, min/max enforcement for reconnect delays, live effect on reconnect worker delay growth, and ACK-required frequency changes during sustained sends.
