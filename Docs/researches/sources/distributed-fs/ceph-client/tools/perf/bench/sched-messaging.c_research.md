# Research: sources/distributed-fs/ceph-client/tools/perf/bench/sched-messaging.c

Purpose: implements a hackbench-derived scheduler/IPC benchmark using groups of senders and receivers communicating through pipes or Unix socketpairs, in process or thread mode.

Important APIs/types/functions: `bench_sched_messaging()` is the entry. `fdpair()` creates pipe/socketpair channels. `ready()` blocks workers until main releases them. `sender()` writes fixed-size messages to receiver fds. `receiver()` polls/reads until expected packets arrive. `group()` allocates sender/receiver contexts and starts workers. `reap_worker()` joins threads or waits processes. `sig_handler()` kills child processes on abnormal termination.

Control flow: options choose pipes, thread mode, group count, and loops. Main allocates a worker table, creates ready/wake fds, installs signal handlers for process mode, builds each group of 20 senders and 20 receivers, waits for every worker readiness byte, starts timing, writes one wake byte, reaps all workers, stops timing, prints default/simple output, and frees contexts.

State and persistence: global linked lists retain allocated sender/receiver contexts until cleanup; worker table holds pthread ids or pids. No files persist. IPC fds are inherited by forked workers or shared by threads.

Dependencies and integration: depends on pthreads, fork/wait, sockets/pipes, poll, Linux list helpers, parse-options, and bench output globals.

Risks: high group counts create many fds and processes/threads. Signal cleanup only handles process mode. Context/fd ownership is complex across fork/thread paths; fd leaks can skew long repeated use. The fixed group size of 20 is embedded in the benchmark.

Test signals: process and thread modes, pipe vs socketpair, varied group/loop counts, simple/default output, SIGINT cleanup, and fd/resource-limit stress.
