# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk_prereqs.sh

## Purpose

This shell helper validates and runs the `xskxceiver` AF_XDP selftest under expected prerequisites. It checks root privileges, `ip` utility availability, veth support, manages test status output, performs interface cleanup, and invokes the compiled `xskxceiver` binary with veth interface arguments.

## Important APIs, Types, and Functions

It defines kselftest status constants, `XSKOBJ=xskxceiver`, and functions `validate_root_exec`, `validate_veth_support`, `test_status`, `test_exit`, `cleanup_iface`, `clear_configs`, `cleanup_exit`, `validate_ip_utility`, and `exec_xskxceiver`. Important external commands are `ip link add/del/set` and `./xskxceiver`.

## Control Flow

Callers source or execute the script around AF_XDP test setup. Validation fails or skips via `test_exit`; veth support is probed by trying to create and delete a veth; cleanup restores MTU and removes XDP/xdpgeneric attachments. `exec_xskxceiver` appends busy-poll arguments when requested, executes the binary against `VETH0` and `VETH1`, and records status/name arrays unless list mode is active.

## State and Persistence Behavior

The script mutates network interface state and shell arrays such as `statusList` and `nameList`. It relies on environment variables including `VETH0`, `VETH1`, `ARGS`, `busy_poll`, `list`, and `TEST_NAME`.

## Dependencies and Integration Points

It integrates with AF_XDP shell test orchestration and the `xskxceiver` binary. Dependencies are root privileges, iproute2, veth kernel support, and interfaces created by the surrounding test script.

## Risks and Test Signals

Risks include global shell-variable coupling, incomplete cleanup after interruption, treating root requirement as failure instead of skip in one path, and stale XDP state on shared devices. Signals are prerequisite pass/skip output, successful veth probe, `xskxceiver` exit status, and restored interface MTU/XDP mode.
