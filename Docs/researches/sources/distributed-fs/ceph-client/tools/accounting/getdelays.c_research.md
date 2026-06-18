# sources/distributed-fs/ceph-client/tools/accounting/getdelays.c

## Purpose
Demonstrates and exposes Linux taskstats delay accounting, IO accounting, context-switch counts, and cgroupstats through generic netlink. It can query a pid/tgid, register a CPU mask for exit notifications, run a command and report its stats, or query cgroup stats.

## Important APIs, Types, And Functions
- Generic netlink helpers `create_nl_socket()`, `recv_taskstats_msg()`, `send_cmd()`, and `get_family_id()`.
- `format_timespec()` formats version 17 taskstats max-delay timestamps.
- Print macros handle taskstats version compatibility for delay max/min and timestamp fields.
- `print_delayacct()`, `task_context_switch_counts()`, `print_cgroupstats()`, and `print_ioacct()` render decoded stats.
- `main()` parses options, registers/deregisters cpumasks, sends pid/tgid/cgroup commands, optionally waits for a forked command, and parses netlink replies.

## Control Flow
The program discovers the taskstats family, optionally registers a CPU mask, validates mutually exclusive pid/cgroup selections, waits for a forked command when `-c` is used, sends one or more taskstats/cgroupstats requests, then receives messages in a loop. It parses top-level netlink attributes, descends into pid/tgid aggregate attributes, and prints selected stats or writes raw `taskstats` records to a file. Unless `-l` is set, it exits after one stats record.

## State And Persistence
State is process-local globals for receive buffer size, debug flag, print selections, taskstats family name, and cpumask. Optional raw stats persistence occurs through `-w logfile`, which writes binary taskstats payloads. Cpumask registration persists in the kernel only until deregistration or process/socket teardown.

## Dependencies And Integration Points
Depends on `NETLINK_GENERIC`, taskstats/cgroupstats UAPI, local taskstats versions, and standard POSIX process/signal APIs. It is a reference user for kernel delay accounting.

## Risks
- Netlink parsing trusts attribute lengths enough to step through nested attributes; malformed kernel responses are not heavily guarded.
- `-c` uses `sigwait()` instead of `waitpid()` to preserve exit data; child exit status is not surfaced.
- Binary logfile format is raw `struct taskstats`, so readers must match UAPI layout/version.
- cpumask registration should be deregistered on normal exit, but abrupt termination can rely on socket cleanup.

## Test Signals
Use `getdelays -d -p <pid>`, `-d -t <tgid>`, `-i -p`, `-q`, `-C <cgroup>`, `-m <cpumask> -l`, `-c <command>`, and `-w` output. Validate taskstats version-dependent fields on kernels with versions below and above 16/17.
