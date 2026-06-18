# sources/distributed-fs/ceph-client/tools/testing/selftests/vsock/vmtest.sh

## Purpose

`vmtest.sh` is a KTAP-producing integration harness for vsock behavior in virtual machines and network namespaces. It boots virtme-ng/QEMU guests with a fixed vhost-vsock CID, runs `vsock_test` in host and guest roles, validates loopback and cross-namespace visibility rules, checks same-CID VM admission rules, verifies namespace deletion does not break established sockets, and fails tests on new vsock-related kernel warnings or oopses.

## Important APIs, Types, and Functions

The script sources `../kselftest/ktap_helpers.sh` for `KSFT_*` status codes. Important constants are `VSOCK_TEST`, `TEST_GUEST_PORT`, `TEST_HOST_PORT`, `SSH_HOST_PORT`, `VSOCK_CID`, wait intervals, `QEMU_TEST_PORT_FWD`, `QEMU_SSH_PORT_FWD`, and `KERNEL_CMDLINE`. `TEST_NAMES`, `TEST_DESCS`, `USE_SHARED_VM`, and `NS_MODES` drive discovery and scheduling. Core helpers include `check_result()`, `add_namespaces()`, `init_namespaces()`, `del_namespaces()`, `vm_ssh()`, `check_deps()`, `check_vng()`, `check_socat()`, `handle_build()`, `setup_home()`, `create_pidfile()`, `terminate_pidfiles()`, `vm_start()`, `vm_wait_for_ssh()`, `wait_for_listener()`, `vm_vsock_test()`, `host_vsock_test()`, `vm_dmesg_check()`, `run_shared_vm_tests()`, and `run_ns_tests()`.

## Control Flow

Argument parsing handles `-b` for building the current kernel, `-q` for QEMU binary selection, `-v` for verbose logs, and optional test names. Setup validates dependencies, supported virtme-ng versions, socat vsock/unix support, optionally builds the kernel, creates an SSH key and test home, and prints a KTAP plan. Shared VM tests boot one guest in the initial namespace and run host-client, guest-client, and loopback scenarios. Namespace tests create parent namespaces with `child_ns_mode` set to global or local, create child namespaces, run each selected test, and tear namespaces down between tests. Individual tests start VMs in specific namespaces, bridge TCP or UNIX sockets with socat where needed, run `vsock_test` or socat probes, compare expected success/failure, and inspect dmesg warning/oops counters before and after.

## State and Persistence Behavior

The script creates temporary logs under `/tmp`, a temporary home directory with an SSH key and copied `vsock_test`, temporary QEMU pidfiles, transient network namespaces, pid-tracked background socat/vng processes, and guest state. `trap cleanup EXIT` kills pidfile-tracked processes, deletes namespaces, and removes the temporary home. It does not persist test results except the printed log path and any external build artifacts created by `-b`.

## Dependencies and Integration Points

Dependencies include `vng`, QEMU, busybox, `ssh`, `ss`, `socat` with vsock and unix support, `nsenter`, `pkill`, `ip netns`, the built `vsock_test` binary, host permissions to manage network namespaces, and a kernel with vsock namespace sysctls. It integrates with QEMU user networking, vhost-vsock PCI, virtme-init SSH conventions, `/proc/sys/net/vsock/ns_mode`, `/proc/sys/net/vsock/child_ns_mode`, guest dmesg, and kselftest KTAP output.

## Risks and Edge Cases

The harness is environment-sensitive: missing root privileges, unavailable namespace support, port conflicts on 2222/50000/50001, unsupported virtme-ng behavior, or socat without vsock support cause skips or failures. Some tests depend on fixed CID `1234` and fixed host ports. Several failure tests infer isolation by checking that `TEST` was not delivered, so timeouts and listener readiness matter. Dmesg warning matching is limited to warnings containing `vsock`.

## Test Signals

Pass signals are KTAP `ok` lines for selected tests, successful shared VM startup, successful `vsock_test` client/server exchanges where expected, failed socat delivery for disallowed namespace combinations, successful same-CID boot only for allowed local/global combinations, preserved socket data after namespace deletion, and no increase in host or guest oops/vsock warning counters.
