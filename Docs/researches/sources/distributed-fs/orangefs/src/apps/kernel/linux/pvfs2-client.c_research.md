<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/kernel/linux/pvfs2-client.c -->
# sources/distributed-fs/orangefs/src/apps/kernel/linux/pvfs2-client.c

## Purpose
Implements the supervising `pvfs2-client` daemon wrapper for Linux kernel-client deployments. It validates root execution, optionally backgrounds itself, watches a child `pvfs2-client-core`, forwards signals, and translates wrapper options into the core process command line.

## Important APIs, Types, And Functions
`options_t` carries cache, logging, descriptor, performance, readahead, event, key, and BMI settings. `main` parses options, installs signal handlers, daemonizes, and enters `monitor_pvfs2_client`. `client_sig_handler` kills the process group and waits for the core child on normal termination signals. `verify_pvfs2_client_path` checks executable paths. `monitor_pvfs2_client` forks, builds `arg_list`, execs `pvfs2-client-core`, and interprets exit statuses. `parse_args` maps short and long command-line switches to `options_t`.

## Control Flow
The parent loops forever spawning the core, redirecting stdio to `/dev/null`, waiting for exit, and logging restart decisions. Device-initialization failures sleep and retry up to `MAX_DEV_INIT_FAILURES`; `PVFS_ENODEV` exits; `PVFS_EAGAIN` restarts immediately; signal deaths are rate-limited by `CLIENT_RESTART_INTERVAL_SECS` and `CLIENT_MAX_RESTARTS`.

## State And Persistence
State is in memory: `core_pid`, `s_client_core_path`, parsed option pointers, restart counters, and the process group. Persistent effects are the log target, syslog records, and the running child process. No config file is written.

## Dependencies And Integration Points
Depends on POSIX process/signal APIs, `gossip` logging, OrangeFS error codes, and cache defaults from `acache.h`/`ncache.h`. It is the service-level launcher for the kernel request-device client core.

## Risks And Test Signals
Risks include fixed `arg_list[128]` capacity, duplicated `--perf-time-interval-secs` forwarding, signal fanout with `kill(0, signum)`, assert-based fork/wait handling, leaked logfile open descriptor from writability probing, and options accepted by `parse_args` only when build flags expose them. Test signals are root/non-root startup, foreground/background behavior, invalid core path rejection, restart throttling, logtype variants, signal shutdown, and forwarding of every option to the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/kernel/linux/pvfs2-client.c -->
