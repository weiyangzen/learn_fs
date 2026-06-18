# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/utils.py

## Purpose
This module provides process, command, defer, tool, port, and wait utilities used by Python network selftests.

## Important APIs and Types
`cmd` runs a foreground command locally, in a namespace, or through a remote host object, with optional JSON parsing, timeout, failure checking, and kselftest ready/wait file descriptors. `bkg` subclasses `cmd` for background context-managed processes. `defer` queues cleanup callbacks while the KSFT runner arms the defer queue. Tool wrappers `tool`, `bpftool`, `ip`, `ethtool`, and `bpftrace` run common networking commands. Utility functions include `fd_read_timeout`, `rand_port`, `rand_ports`, `wait_port_listen`, and `wait_file`. Exceptions `CmdInitFailure` and `CmdExitFailure` expose failed command objects.

## Control Flow and State
`cmd.__init__` may rewrite commands for namespaces, create readiness pipes, launch `subprocess.Popen`, optionally wait for `KSFT_READY_FD`, and process foreground commands immediately. `bkg.__exit__` terminates or waits according to initialization flags. Deferred callbacks are stored in global `GLOBAL_DEFER_QUEUE`, guarded by `GLOBAL_DEFER_ARMED`. `bpftrace(json=True)` converts line-oriented JSON map events into a dictionary.

## Dependencies and Integration
It depends on Python `subprocess`, `select`, `socket`, command-line tools, `/proc/net`, and the `ksft.h` readiness protocol. It is used throughout the Python selftest package and underpins `ksft.py` cleanup semantics.

## Risks and Test Signals
String commands containing spaces are naïvely split unless `shell` is specified, so complex quoting requires care. `cmd.process` always calls `communicate`, so long-running commands should use `bkg`. Timeouts and command failures raise exceptions by default. Successful signals are zero return codes, parsed JSON results, readiness bytes from child programs, and observed `/proc/net` listener rows.
