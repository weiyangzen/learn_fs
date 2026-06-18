# sources/distributed-fs/ceph-client/tools/testing/selftests/connector/proc_filter.c

## Purpose

`proc_filter.c` is an interactive process connector selftest/listener. It registers with the kernel connector netlink proc event source, optionally requests a filtered event stream, prints received process events, and unregisters on SIGINT. The complete 310-line file was read.

## Important APIs, Types, and Functions

Important globals are `interrupted`, `nl_sock`, `ret_errno`, `tcount`, `evn`, and `filter`. Key functions are `send_message()`, `register_proc_netlink()`, `sigint()`, `handle_packet()`, `handle_events()`, and `main()`.

## Control Flow

`main()` parses optional `-f`, installs a SIGINT handler, builds either legacy `enum proc_cn_mcast_op` input or `struct proc_input` filtering for `PROC_EVENT_NONZERO_EXIT`, registers a `NETLINK_CONNECTOR` socket and epoll fd, loops handling events until interrupted, sends ignore/unregister, closes fds, prints total count, and exits.

## State and Persistence Behavior

It opens a netlink socket bound to `CN_IDX_PROC`, registers kernel listener state, creates an epoll fd, increments `tcount` for events, and unregisters listener state before exit when interrupted normally.

## Dependencies and Integration Points

It depends on Linux connector headers, `NETLINK_CONNECTOR`, `CN_IDX_PROC`, `CN_VAL_PROC`, proc connector events, epoll, signals, and kselftest print helpers.

## Risks and Edge Cases

The program is listener-like and runs until SIGINT, so automated harnesses need to manage lifetime. Error cleanup paths close different fd subsets but can reference `epoll_fd` after partial initialization. Filtered mode depends on `struct proc_input` kernel support. `handle_packet()` assigns to its local `event` pointer and does not copy back through the parameter, which is fine because callers only rely on printing/counting.

## Test Signals

Signals include successful netlink registration, receipt and printing of fork/exec/exit/uid/gid/session/ptrace/comm/coredump events, filtered nonzero-exit events with `-f`, clean unregister, and nonzero `tcount` when events occur.
