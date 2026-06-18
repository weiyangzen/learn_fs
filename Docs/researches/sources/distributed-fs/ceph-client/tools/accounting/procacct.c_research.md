# sources/distributed-fs/ceph-client/tools/accounting/procacct.c

## Purpose
Listens for taskstats process accounting records on task exit and prints compact process/thread resource usage, including executable device/inode metadata when available.

## Important APIs, Types, And Functions
- Reuses generic netlink helpers for socket creation, message receive, command send, and family discovery.
- `print_procacct()` formats taskstats accounting fields: pid, tgid, uid, elapsed time, group walltime, CPU time, peak VM/RSS, executable dev/inode, and command.
- `handle_aggr()` parses nested pid/tgid aggregate attributes and prints only pid aggregate stats.
- `main()` parses cpumask/debug/log options, defaults cpumask to `1`, registers the mask, and receives taskstats indefinitely.

## Control Flow
Startup selects a cpumask, optionally opens a raw output file, creates a generic netlink socket, discovers taskstats family id, and registers the cpumask for exit notifications. The receive loop decodes each netlink message, calls `handle_aggr()` for pid/tgid aggregates, writes raw taskstats data if requested, and continues forever. On `done`, it deregisters the cpumask.

## State And Persistence
State is global and process-local: socket buffer size, debug flag, family name, cpumask, and optional output file descriptor. `-w` persists raw taskstats payloads to a binary log. The cpumask registration is kernel state while the listener is active.

## Dependencies And Integration Points
Depends on generic netlink, `linux/taskstats.h`, `linux/acct.h`, `linux/kdev_t.h`, and kernel taskstats exit accounting. It complements `getdelays` by focusing on exit-time accounting rather than point queries.

## Risks
- Infinite receive loop requires external termination; normal deregistration may not run on signals.
- `send_cmd()` sets `nla_len = nla_len + 1 + NLA_HDRLEN`, unlike `getdelays`, which may be intentional for string cpumasks but should be scrutinized for non-string attributes.
- Only pid aggregate stats are printed by default; tgid aggregate handling is parsed but not printed.
- Raw log files depend on taskstats struct version and machine ABI.

## Test Signals
Run with default cpumask and create/exit processes, with `-m` for specific CPUs, `-v` debug output, `-r` buffer sizing, and `-w` raw output. Validate printed AGROUP/thread flags on kernels with taskstats version >= 12.
