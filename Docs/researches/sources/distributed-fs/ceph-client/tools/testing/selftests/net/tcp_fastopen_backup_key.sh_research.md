# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_fastopen_backup_key.sh

## Purpose
`tcp_fastopen_backup_key.sh` is the harness for the TFO backup-key rotation test. It creates an isolated namespace, enables TCP Fast Open, runs the compiled C test in all mode combinations, and verifies no passive TFO cookie failures were recorded.

## Important APIs, Types, And Functions
Functions are `setup()`, `cleanup()`, and `do_test()`. It uses `ip netns`, namespace-local `sysctl net.ipv4.tcp_fastopen=3`, `ip tcp_metrics flush`, `nstat -az`, and the compiled `./tcp_fastopen_backup_key` binary.

## Control Flow
The script creates a temporary namespace, brings loopback up, enables client and server TFO, then calls `do_test()` sixteen times: IPv4/IPv6, procfs key path, socket-option key path, rotation path, and socket-option-plus-rotation path, with repeats. Each `do_test()` flushes TCP metrics to avoid stale cookies, executes the C binary with its option string, reads `TcpExtTCPFastOpenPassiveFail`, and fails if the counter is nonzero.

## State, Persistence, And Dependencies
State is limited to one temporary namespace and its TFO sysctl/counters. The trap deletes the namespace. The script depends on root privileges, `ip`, `nstat`, the compiled C binary in the current directory, and kernel TFO support.

## Integration Points
This wrapper provides the counter-based pass/fail signal missing from the C program alone. It connects TFO key rotation to the kernel `TcpExtTCPFastOpenPassiveFail` statistic and ensures old TCP metrics do not contaminate subsequent cases.

## Risks
Failure to delete the namespace could leave temporary state. `set -e` means unexpected command failures abort immediately through cleanup. It assumes `nstat` emits the passive-fail counter name and that local loopback TFO behavior matches the key rotation scenarios.

## Test Signals
Passing output is `all tests done` after all sixteen invocations, with each `TcpExtTCPFastOpenPassiveFail` value equal to zero. Any nonzero counter prints a failure and exits nonzero.
