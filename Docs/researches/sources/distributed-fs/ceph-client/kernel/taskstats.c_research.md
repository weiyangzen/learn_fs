# sources/distributed-fs/ceph-client/kernel/taskstats.c

## Purpose
`taskstats.c` exports per-task and per-thread-group accounting to userspace over generic netlink, and can send exit-time taskstats to listeners registered per CPU. It also provides cgroupstats query support through the same family.

## Important APIs, types, and functions
- Global state: per-CPU `taskstats_seqnum`, `family_registered`, `taskstats_cache`, generic netlink `family`, and per-CPU `listener_array`.
- Listener types: `struct listener` and `struct listener_list`.
- Netlink helpers: `prepare_reply()`, `send_reply()`, `send_cpu_listeners()`, `mk_reply()`.
- Stats collection: `fill_stats()`, `fill_stats_for_pid()`, `fill_stats_for_tgid()`, `fill_tgid_exit()`, `taskstats_tgid_alloc()`.
- User commands: `cmd_attr_pid()`, `cmd_attr_tgid()`, `cmd_attr_register_cpumask()`, `cmd_attr_deregister_cpumask()`, `taskstats_user_cmd()`, `cgroupstats_user_cmd()`.
- Lifecycle: `taskstats_exit()`, `taskstats_init_early()`, and late init `taskstats_init()`.

## Control flow
Early init creates the slab cache and initializes per-CPU listener lists. Late init registers the generic netlink family. User `TASKSTATS_CMD_GET` requests dispatch to listener registration/deregistration or PID/TGID stats replies. PID stats pin a task by vpid and fill one record; TGID stats lock signal state, combine dead accumulated stats with live thread stats, and return an aggregate. On task exit, if the family is registered and listeners exist for the current CPU, the code allocates a reply, fills PID stats and optionally TGID stats when the group is dead, then unicasts clones to registered listeners, cleaning dead listeners on `-ECONNREFUSED`.

## State and persistence behavior
Persistent kernel state includes the per-CPU listener lists and optional per-signal `taskstats` aggregate allocated from `taskstats_cache`. Exit accounting accumulates into `signal->stats` for thread groups. Netlink messages are transient.

## Dependencies and integration points
It integrates with generic netlink, pid/user namespaces, delay accounting, BSD/xacct accounting, executable file lookup, cgroupstats, CPU masks, per-CPU data, task cputime, task exit paths, and slab allocation.

## Risks
The interface crosses namespaces and permissions. Listener registration is restricted to init user and pid namespaces, and generic netlink ops use admin permissions for taskstats get. Per-CPU listener cleanup must handle clone allocation failure and dead netlink ports. TGID aggregation races are managed with RCU and signal locks, but live tasks can change while stats are sampled.

## Test signals
Use userspace taskstats tools or selftests to query PID/TGID stats, register/deregister CPU masks, observe exit notifications, and request cgroupstats by fd. CPU hotplug/listener behavior, net namespace behavior, and accounting fields under delayacct/xacct configs are important coverage.
