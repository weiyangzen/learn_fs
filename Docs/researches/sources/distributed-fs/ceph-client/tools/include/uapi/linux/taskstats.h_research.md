<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/taskstats.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/taskstats.h

Purpose: this header defines the generic-netlink taskstats ABI for exporting per-task accounting, delay, I/O, memory, and exit statistics.

Important APIs/types: `TASKSTATS_VERSION` is 17 and `TS_COMM_LEN` is 32. `struct taskstats` is append-only and contains exit code/flags, delay accounting counters/totals/min/max/timestamps, basic accounting fields, RSS/VM high watermarks, I/O counters, context switches, scaled CPU time, begin time, executable device/inode identity, thread-group stats, and IRQ/write-protect/compaction/thrashing delay data. Netlink command/type enums define GET/NEW messages, PID/TGID/STATS aggregate attributes, and CPU mask register/deregister attributes. `TASKSTATS_GENL_NAME` and version identify the family.

Control flow: userspace talks to generic netlink `TASKSTATS`, requests stats by PID/TGID or registers CPU masks for exit notifications, then parses nested aggregate attributes containing IDs and `struct taskstats`.

State and persistence: stats are kernel task accounting snapshots; exit events are emitted when listeners are registered. Counters may wrap as documented, and delay fields require kernel delay accounting.

Dependencies/integration: depends on Linux types and time types; integrated by accounting daemons, performance diagnostics, and container/task monitors.

Risks and test signals: risks include struct version drift, alignment requirements, optional delay accounting, 32-bit begin-time overflow mitigated by `ac_btime64`, and netlink nesting. Test current/exiting tasks, PID/TGID aggregation, CPU mask registration, and version/size parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/taskstats.h -->
