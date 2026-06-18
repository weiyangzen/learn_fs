# Research: subset-b-006832

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/options.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/options.sh

## Purpose
Validates basic team driver option get/set behavior through `teamnl`, including global team options, per-port options, invalid option lookup, and implicit synchronization between `enabled`, `rx_enabled`, and `tx_enabled`. The test runs inside a private network namespace via `in_netns.sh` when invoked directly.

## Important APIs, Types, And Functions
The script uses `ip link` to create a dummy member and a team device, `teamnl getoption/setoption` to exercise netlink option paths, and net selftest helpers from `net/lib.sh` such as `require_command`, `check_err`, `check_fail`, `log_test`, and `tests_run`. Key local helpers are `get_and_check_value()`, `set_and_check_get()`, `get_port_flag()`, port attach/detach helpers, `team_test_option()`, and the implicit-change tests.

## Control Flow
Startup re-execs under a private namespace, exports four `ALL_TESTS` entries, requires `teamnl`, creates `dummy0` and `team0`, then lets `tests_run` call each test. Generic option tests attach a member only for per-port options, set values in a value1/value2/value1 sequence, and verify reads after every write. Negative tests expect lookup failure. The implicit-change tests prove setting aggregate `enabled` updates RX/TX flags and setting either split flag changes aggregate `enabled`.

## State And Persistence
All state is transient kernel netdevice state inside the namespace. `RET` and `EXIT_STATUS` are the kselftest accounting state; no persistent files are written.

## Dependencies And Integration Points
Requires the team driver, dummy netdevice support, `teamnl`, namespace support, and `tools/testing/selftests/net/lib.sh`. It integrates with kselftest via `ALL_TESTS` and `tests_run`.

## Risks
The script assumes option string formatting from `teamnl` exactly matches requested values. Port cleanup is done only inside test functions, so an early fatal failure can leave namespace-local devices until namespace teardown. Per-port option coverage depends on successful enslaving of `dummy0`.

## Test Signals
Pass signals are `log_test` results for option round trips and implicit flag propagation. Failures identify the option name and expected versus observed value or unexpected success for fake options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/options.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/propagation.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/propagation.sh

## Purpose
Exercises regressions in team lower-device feature and flag propagation: LRO propagation to a netdevsim lower, promiscuous flag propagation during enslave, and promiscuous propagation through `ndo_change_rx_flags` after the team is already up.

## Important APIs, Types, And Functions
The script uses `modprobe netdevsim`, `/sys/bus/netdevsim/new_device` and `del_device`, `ip link` team/dummy/macvlan operations, and `ethtool -K`. Local functions are `cleanup()`, `team_lro()`, `team_promisc()`, and `team_change_flags()`.

## Control Flow
With `set -e`, the script loads netdevsim, creates one simulated device, settles udev, then runs the three trigger functions. Each function builds the minimum topology needed to trigger propagation and deletes devices after the event. A trap tears down dummy/team devices, removes the simulator instance, and unloads netdevsim.

## State And Persistence
State is temporary netdevice/sysfs state. `NSIM_LRO_ID` randomizes the netdevsim id to avoid collisions. There is no persistent artifact.

## Dependencies And Integration Points
Requires root, netdevsim, team, dummy/macvlan, ethtool, udevadm, and writable netdevsim sysfs. It targets kernel team code paths linked in netdev mailing-list regressions.

## Risks
Because `set -e` is enabled, missing sysfs/debug support exits immediately. `modprobe netdevsim || :` permits a missing module until sysfs use fails. Random id collisions are unlikely but possible.

## Test Signals
The test is success-by-no-crash/no-command-failure. Relevant failures are command exit errors or kernel warnings around feature/flag propagation and lower-device lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/propagation.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/refleak.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/refleak.sh

## Purpose
Regression test for a team-port reference leak: moving an enslaved dummy interface to another network namespace and deleting it must not leave a reference that prevents deletion.

## Important APIs, Types, And Functions
The script sources `net/lib.sh`, uses `setup_ns`/`cleanup_all_ns`, and performs `ip -n` link creation, enslaving, namespace move, and deletion. There are no local functions beyond the inherited cleanup trap.

## Control Flow
It creates two namespaces, creates `team1` and `dummy1` in the first namespace, enslaves `dummy1`, moves `dummy1` to the second namespace, and deletes it there. The trap cleans all namespaces.

## State And Persistence
Only namespace-local netdevices are created. Successful deletion proves the team reference was released.

## Dependencies And Integration Points
Requires namespace support, team and dummy drivers, and kselftest net library helpers. It directly targets team netdevice refcount/lifetime logic.

## Risks
The script has no explicit assertions beyond command success; failures surface as `ip` errors or a hang/cleanup failure if references are leaked.

## Test Signals
The main signal is successful `ip -n "$ns2" link del dev dummy1`. Kernel refcount warnings or inability to delete the dummy device indicate regression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/refleak.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/team_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/team_lib.sh

## Purpose
Shared library for team driver traffic tests. It provides team setup, iperf3 traffic generation, tcpdump capture, packet counting, and “no traffic” checks used by failover and teamd active-backup tests.

## Important APIs, Types, And Functions
It sources `net/forwarding/lib.sh` with `NUM_NETIFS=0` and `REQUIRE_MZ=no`. Key helpers are `setup_team()`, `start_listening_and_sending()`, `stop_sending_and_listening()`, `save_tcpdump_outputs()`, `clear_tcpdump_outputs()`, `did_interface_receive()`, and `check_no_traffic()`. It relies on globals supplied by callers, especially `NS1`, `NS2`, `NS2_IP`, and `NODAD`.

## Control Flow
`setup_team()` detaches members, removes an existing address, brings the team down, sets the team mode via `teamnl`, enslaves members, brings the team up, and assigns the IP address. Traffic helpers start an iperf3 server in `NS2`, verify reachability, then run a long-lived sender in `NS1`. Capture helpers start/stop tcpdump per interface and grep for packets toward the configured destination port.

## State And Persistence
The only global mutable state is `sender_pid`, used to terminate the background iperf3 client. Temporary tcpdump files are managed by forwarding-library helpers.

## Dependencies And Integration Points
Requires `teamnl`, `iperf3`, `tcpdump`, network namespaces, and the forwarding test library. It is meant to be sourced, not executed standalone.

## Risks
The helpers assume a single concurrent sender and fixed TCP port `43434`. Packet counting is based on tcpdump text output and can be sensitive to timing, output format, and background process cleanup.

## Test Signals
Consumers use packet presence or absence on specific member interfaces to validate team mode behavior. `setup_team()` return codes and `slowwait` reachability checks are early failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/team_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/teamd_activebackup.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/teamd_activebackup.sh

## Purpose
End-to-end teamd active-backup runner test. It verifies that teamd can create two two-port teams in separate namespaces, carry traffic, select an active port, and move active traffic between ports.

## Important APIs, Types, And Functions
The script uses `teamd`, `teamdctl`, `teamnl` indirectly through `team_lib.sh`, `iperf3`, `tcpdump`, `ip netns`, and kselftest net helpers. Local helpers include `teamd_config_create()`, `environment_create()`, `environment_destroy()`, `set_active_port()`, `wait_to_stop_receiving()`, and `teamd_test_active_backup()`.

## Control Flow
It optionally switches to IPv4 with `-4`, otherwise using IPv6. Setup creates two namespaces, two veth pairs, JSON configs for `test_team1` and `test_team2`, starts daemonized teamd instances, brings teams up, assigns addresses, and checks ping. The test starts iperf3 traffic, verifies baseline delivery, forces `eth1` active on both teams, confirms only `eth1` receives, then forces `eth0` active and confirms only `eth0` receives.

## State And Persistence
Temporary config files and teamd PIDs are tracked in globals and removed by `environment_destroy()`. Namespace, veth, and team state is transient. `/var/run/teamd` pid/socket files may be force-removed if graceful shutdown fails.

## Dependencies And Integration Points
Requires root, namespace support, teamd/teamdctl, team driver, veth, iperf3, tcpdump, and shared `team_lib.sh`.

## Risks
Traffic assertions are timing-sensitive and depend on iperf3/tcpdump readiness. `pgrep -f` on config path must identify the right teamd process. Force-kill cleanup must not collide with unrelated same-named teamd instances.

## Test Signals
Pass is a `log_test` for active backup runner behavior. Failures are missing traffic on the active interface, traffic on inactive interface, teamd startup errors, or inability to change `runner.active_port`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/teamd_activebackup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/transmit_failover.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/transmit_failover.sh

## Purpose
Tests basic transmit failover controlled by the per-port `enabled` team option without teamd. It covers broadcast, roundrobin, and random modes over two veth links between namespaces.

## Important APIs, Types, And Functions
Uses `teamnl setoption/getoption`, `setup_team()` and traffic helpers from `team_lib.sh`, namespace helpers from `net/lib.sh`, plus `iperf3` and `tcpdump`. Main functions are `environment_create()`, `team_test_mode_failover()`, and `team_test_failover()`.

## Control Flow
Setup creates namespaces, two veth pairs, two team devices, and configures the receiving team in roundrobin. For each sender mode, it configures sender team mode/address, starts traffic, verifies both links receive when enabled, disables `eth1` through `teamnl`, verifies only `eth0` receives, re-enables `eth1`, and verifies both links receive again.

## State And Persistence
All network state is namespace-local and cleaned by `cleanup_all_ns`. The sender process is tracked by `team_lib.sh`.

## Dependencies And Integration Points
Requires team driver modes broadcast/roundrobin/random, `teamnl`, veth, namespace support, iperf3, tcpdump, and the net forwarding library.

## Risks
The test intentionally excludes activebackup and loadbalance because `enabled` alone is insufficient. Packet distribution checks assume enough traffic over a one-second capture to observe both links.

## Test Signals
Per-mode `log_test` success means disabled links stop receiving and enabled links resume. `slowwait` confirmation of the option value is a key synchronization signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/transmit_failover.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/Makefile

## Purpose
Build/install metadata for virtio_net selftests. It registers `basic_features.sh` as the test program and `virtio_net_common.sh` plus net helper libraries as installed test files/includes.

## Important APIs, Types, And Functions
Defines `TEST_PROGS`, `TEST_FILES`, `TEST_INCLUDES`, and includes `../../../lib.mk`. No functions are implemented.

## Control Flow
kselftest make infrastructure copies the script and dependencies to the output/install tree and runs `basic_features.sh`.

## State And Persistence
No runtime state. Build state is managed by kselftest output directories.

## Dependencies And Integration Points
Pairs with `config`, which requests BPF, IPv6, VRF, virtio debug, and virtio_net kernel support.

## Risks
If helper include paths change, installed tests can miss runtime libraries. This Makefile assumes the actual tests are shell-only and do not need compilation.

## Test Signals
Successful make/run should expose one test program and common helper file under the kselftest output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/basic_features.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/basic_features.sh

## Purpose
Validates a two-interface virtio_net endpoint setup, including basic IPv4/IPv6 ping and behavior when feature bit `VIRTIO_NET_F_MAC` is filtered via virtio debugfs.

## Important APIs, Types, And Functions
Uses `virtio_device_rebind()`, `virtio_feature_present()`, `virtio_filter_feature_add()`, `virtio_filter_features_clear()`, and `check_virtio_debugfs()` from `virtio_net_common.sh`; uses forwarding helpers `simple_if_init`, `vrf_prepare`, `ping_test`, `ping_do`, `check_driver`, `wait_for_dev`, and kselftest logging. Local functions include `h1_create/destroy`, `h2_create/destroy`, `initial_ping_test()`, `f_mac_test()`, `setup_prepare()`, `setup_cleanup()`, and `cleanup()`.

## Control Flow
The script identifies two virtio_net interfaces from forwarding-library `NETIFS`, validates drivers/debugfs, installs cleanup trap, prepares interfaces, and runs tests. `initial_ping_test()` resets and pings. `f_mac_test()` checks the MAC feature exists, verifies permanent address assignment with the feature present, filters the feature on both devices, rebinds, verifies permanent address assignment is no longer reported, and confirms ping still works.

## State And Persistence
It changes device MTU/address state and virtio debugfs feature filters, then clears filters and rebinds devices during cleanup. No files are persisted.

## Dependencies And Integration Points
Requires a back-to-back two-virtio-interface topology, virtio debugfs, root, forwarding library, VRF support, and ping reachability.

## Risks
Rebinding real virtio interfaces is disruptive. Debugfs feature filter support must be enabled and mounted. The second `virtio_feature_present` check appears to query `$h1` again while reporting `$h2`, so missing feature on the second device may not be independently detected.

## Test Signals
Signals include successful simple ping, expected `addr_assign_type` changes around `F_MAC` filtering, and ping after feature filtering/rebind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/basic_features.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/config

## Purpose
Kernel config fragment for virtio_net selftests. It requests features needed by forwarding/BPF helpers and the virtio feature-filter tests.

## Important APIs, Types, And Functions
Sets `CONFIG_BPF_SYSCALL`, `CONFIG_CGROUP_BPF`, `CONFIG_IPV6`, `CONFIG_IPV6_MULTIPLE_TABLES`, `CONFIG_NET_L3_MASTER_DEV`, `CONFIG_NET_VRF=m`, `CONFIG_VIRTIO_DEBUG`, and `CONFIG_VIRTIO_NET`.

## Control Flow
Consumed by kselftest/kernel config tooling; not executable.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Aligns with `basic_features.sh` requirements for IPv6/VRF and virtio debugfs feature filtering.

## Risks
It does not request debugfs itself, so runtime environments still need debugfs mounted and accessible. `CONFIG_NET_VRF=m` may require module loading.

## Test Signals
Config satisfiability is a prerequisite signal; runtime skip/failure comes from missing debugfs or non-virtio interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/virtio_net_common.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/virtio_net_common.sh

## Purpose
Common shell library for virtio_net driver tests. It defines endpoint discovery assumptions, addressing constants, and helpers for virtio device rebinding and debugfs feature filter manipulation.

## Important APIs, Types, And Functions
Exports forwarding-library variables `REQUIRE_MZ=no`, `NETIF_CREATE=no`, `NETIF_FIND_DRIVER=virtio_net`, and `NUM_NETIFS=2`. Defines IPv4/IPv6 endpoint addresses and `VIRTIO_NET_F_MAC=5`. Helper functions are `virtio_device_get()`, `virtio_device_rebind()`, `virtio_debugfs_get()`, `check_virtio_debugfs()`, `virtio_feature_present()`, `virtio_filter_features_clear()`, and `virtio_filter_feature_add()`.

## Control Flow
Consumers source this file before forwarding lib use. Device helpers resolve `/sys/class/net/$dev/device`, unbind/bind the virtio device, and read/write `/sys/kernel/debug/virtio/$device` feature files.

## State And Persistence
Feature filters persist in debugfs until cleared or device state changes. Rebind changes live device state; helper does not wait for link recreation itself.

## Dependencies And Integration Points
Requires sysfs, virtio bus driver paths, virtio debugfs, and forwarding selftest interface discovery. It is directly used by `basic_features.sh`.

## Risks
Backtick command substitution and unquoted sysfs paths assume simple device names. Rebinding can drop interface state. Missing debugfs causes a kselftest skip from `check_virtio_debugfs()`.

## Test Signals
A valid debugfs directory with `device_features`, `filter_feature_add`, `filter_feature_del`, `filter_features`, and `filter_features_clear` indicates the tests can run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/virtio_net_common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/xdp.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/xdp.py

## Purpose
Python kselftest suite for native XDP support in network drivers. It loads shared BPF objects and validates XDP PASS, DROP, TX, head/tail adjustment, queue statistics accounting, and multi-buffer program replacement behavior.

## Important APIs, Types, And Functions
Enums `TestConfig`, `XDPAction`, and `XDPStats` encode BPF map keys/actions/stat counters. `BPFProgInfo` stores object, section, and MTU. Core helpers are `_exchg_udp()`, `_test_udp()`, `_load_xdp_prog()`, `_get_stats()`, `_test_pass()`, `_test_drop()`, `_test_xdp_native_tx()`, `_test_xdp_native_tail_adjst()`, `_test_xdp_native_head_adjst()`, `get_hds_thresh()`, and `_validate_res()`. It uses `NetDrvEpEnv`, `EthtoolFamily`, `NetdevFamily`, `bkg`, `cmd`, `ip`, `defer`, and BPF map helpers from `lib.py`.

## Control Flow
`main()` creates a network-driver endpoint environment, attaches ethtool/netdev generic netlink families, then runs the test list. Each test loads `xdp_native.bpf.o` or `xdp_dummy.bpf.o` with the requested section and MTU, programs `map_xdp_setup`, exchanges UDP traffic with `socat`, reads `map_xdp_stats`, and asserts action-specific counters and data transformations. Qstats tests compare netdev qstats before/after 1000 packets and after channel count toggling. Update tests prove jumbo MTU multi-buffer XDP cannot be force-replaced with an incompatible single-buffer program.

## State And Persistence
Runtime state includes XDP programs attached to `cfg.ifname`, BPF maps, temporary MTU changes on local and remote interfaces, netdev qstats, and deferred cleanup actions. No files are persisted.

## Dependencies And Integration Points
Requires driver native XDP, BPF syscall/tooling, `ip`, `socat`, endpoint topology from `NetDrvEpEnv`, shared BPF object files in `selftests.net.lib`, and generic netlink ethtool/netdev families.

## Risks
The test is timing-sensitive around UDP listeners and hardware stat settlement. Data adjustment checks aggregate stats without per-case snapshots, so an early failure can dominate later reporting. HDS threshold handling intentionally stops head-shrink exploration when packet size exceeds header split constraints.

## Test Signals
Signals are UDP delivery or intentional loss, exact BPF stats matches, expected transformed payload bytes, qstats packet deltas, preserved stats across channel changes, and expected failure for incompatible multi-buffer to single-buffer replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/xdp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/ntsync/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/ntsync/Makefile

## Purpose
Builds the `ntsync` kselftest binary.

## Important APIs, Types, And Functions
Sets `TEST_GEN_PROGS := ntsync`, adds `$(KHDR_INCLUDES)` to `CFLAGS`, links pthread via `LDLIBS += -lpthread`, and includes `../../lib.mk`.

## Control Flow
kselftest make compiles `ntsync.c` and links with pthread support for the threaded wait tests.

## State And Persistence
No runtime state beyond generated binary output.

## Dependencies And Integration Points
Pairs with `config`, which requests `CONFIG_WINESYNC=y`, and with the Linux UAPI header `linux/ntsync.h`.

## Risks
The SPDX tag has `SPDX-LICENSE-IDENTIFIER` spelling rather than the normal `SPDX-License-Identifier`, which affects metadata scanners but not build behavior.

## Test Signals
Successful build produces the `ntsync` executable linked against pthread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/ntsync/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/ntsync/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/ntsync/config

## Purpose
Kernel config fragment enabling the Windows synchronization primitive driver tested by `ntsync.c`.

## Important APIs, Types, And Functions
Sets `CONFIG_WINESYNC=y`.

## Control Flow
Consumed by selftest config tooling; not executable.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Required for `/dev/ntsync` and the `linux/ntsync.h` ioctl UAPI exercised by the test.

## Risks
If the driver option name changes, the selftest may build but skip/fail at runtime because `/dev/ntsync` is absent.

## Test Signals
Presence of `/dev/ntsync` at runtime is the practical signal that this config requirement is satisfied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/ntsync/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/ntsync/ntsync.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/ntsync/ntsync.c

## Purpose
Comprehensive unit/integration test for the ntsync synchronization primitive driver UAPI. It validates semaphore, mutex, event, wait-any, wait-all, alertable wait, wakeup, owner-death, duplicate-object, limit, timeout, close-while-waiting, and stress behavior through `/dev/ntsync`.

## Important APIs, Types, And Functions
Uses ioctls `NTSYNC_IOC_CREATE_SEM`, `NTSYNC_IOC_SEM_READ/RELEASE`, `NTSYNC_IOC_CREATE_MUTEX`, `NTSYNC_IOC_MUTEX_READ/UNLOCK/KILL`, `NTSYNC_IOC_CREATE_EVENT`, `NTSYNC_IOC_EVENT_READ/SET/RESET/PULSE`, `NTSYNC_IOC_WAIT_ANY`, and `NTSYNC_IOC_WAIT_ALL`. Helpers include `read_sem_state()`, `release_sem()`, `read_mutex_state()`, `unlock_mutex()`, `read_event_state()`, `wait_objs()`, wait wrappers, `wait_thread()`, `get_abs_timeout()`, and `wait_for_thread()`.

## Control Flow
Each `TEST()` opens `/dev/ntsync`, creates objects, performs state transitions, and asserts return codes, errno, indexes, counts, owners, and signal states. Threaded tests start a blocking ioctl in a pthread, verify it remains blocked with timed join, release/set/unlock an object, then verify the waiter wakes with correct index and consumed state. Stress creates four threads repeatedly acquiring an ntsync mutex after a start event and checks the shared counter reaches `STRESS_LOOPS * STRESS_THREADS`.

## State And Persistence
State lives in kernel ntsync file descriptors and object descriptors. Static globals are used only for the stress test (`stress_counter`, `stress_device`, `stress_start_event`, `stress_mutex`). No persistent state is written.

## Dependencies And Integration Points
Requires `/dev/ntsync`, the ntsync UAPI header, pthreads, and kselftest harness. It tests behavior intended to match Windows-style synchronization semantics.

## Risks
Timed joins use short 100-200 ms windows and can be sensitive on very slow systems. Some tests intentionally pass duplicate descriptors, zero counts, max counts, invalid owners, and closed descriptors; incorrect cleanup can cascade if a prior ASSERT aborts a test body.

## Test Signals
Primary signals are exact errno values (`EINVAL`, `EOVERFLOW`, `ETIMEDOUT`, `EPERM`, `EOWNERDEAD`), state reads after every transition, wake indexes for alert/object waits, no premature wakeups, and stress counter equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/ntsync/ntsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/platform/x86/intel/ifs/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/platform/x86/intel/ifs/Makefile

## Purpose
Registers the Intel In Field Scan shell test with kselftest.

## Important APIs, Types, And Functions
Defines `TEST_PROGS := test_ifs.sh` and includes the platform selftest `lib.mk` path. No build products are compiled.

## Control Flow
kselftest runs `test_ifs.sh` directly.

## State And Persistence
No state beyond install/run metadata.

## Dependencies And Integration Points
Depends on `test_ifs.sh` for all runtime probing and on the platform/x86 Intel IFS driver.

## Risks
Shell-only registration means build cannot catch syntax or runtime environment issues.

## Test Signals
Successful install/run exposes `test_ifs.sh` as the single IFS test program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/platform/x86/intel/ifs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/platform/x86/intel/ifs/test_ifs.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/platform/x86/intel/ifs/test_ifs.sh

## Purpose
Hardware-dependent Intel IFS selftest. It validates driver sysfs creation, firmware image loading, corrupt-image rejection, scan execution across sibling CPUs, repeated same-CPU interval behavior, and optional Array BIST mode.

## Important APIs, Types, And Functions
Uses `/sys/devices/virtual/misc/intel_ifs_0` and `_1`, `/sys/devices/system/cpu`, `/lib/firmware/intel/ifs_0`, `current_batch`, `run_test`, `status`, `details`, `modprobe intel_ifs`, CPU online controls, and kselftest exit codes. Key functions include `append_log()`, `online_offline_cpu_list()`, `ifs_cleanup()`, `do_cmd()`, `test_exit()`, `online_all_cpus()`, `get_cpu_fms()`, `check_cpu_ifs_support_interval_time()`, `check_ifs_loaded()`, image load tests, `ifs_test_cpu()`, `ifs_test_cpus()`, `test_ifs_same_cpu_loop()`, `test_ifs_scan_available_imgs()`, and `test_ifs()`.

## Control Flow
The script prepares CPU/model state, onlines CPUs, selects a random CPU and default scan image, loads the module, checks sysfs, tests original and corrupt scan images, runs all available scan images on sibling representatives, loops same-CPU scans with model-dependent delay, and runs Array BIST if the mode directory exists. Cleanup restores images, CPU offline state, and module state, then summarizes PASS/SKIP/FAIL lines.

## State And Persistence
It can modify CPU online state, load/unload `intel_ifs`, write firmware image files during corrupt-image testing, and write a temporary `/tmp/ifs_logs.$$`. Backup/restore flags track whether a firmware image must be restored.

## Dependencies And Integration Points
Requires supported Intel Family 6 platform, IFS driver, firmware images, root, writable firmware directory for negative image tests, and sysfs CPU controls.

## Risks
This test is invasive: it onlines CPUs, modifies firmware image files, and waits platform-specific scan intervals. `eval` in `do_cmd()` requires trusted command construction. Failure during image corruption must execute cleanup to avoid leaving a bad image.

## Test Signals
Signals include sysfs directory existence, successful `current_batch` writes, rejected corrupt images, per-CPU `status=pass`, details output, Array BIST availability/skip, and final summarized pass/skip/fail counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/platform/x86/intel/ifs/test_ifs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/s390x/uvdevice/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/s390x/uvdevice/Makefile

## Purpose
Architecture-gated build metadata for the s390 Ultravisor UAPI selftest.

## Important APIs, Types, And Functions
Includes `Build.include`, checks `uname -m`, and on s390x defines `TEST_GEN_PROGS := test_uvdevice`, `LINUX_TOOL_ARCH_INCLUDE`, `CFLAGS += -Wall -Werror -static $(KHDR_INCLUDES) -I...`, then includes `../../../lib.mk`. On non-s390x it defines inert `all/clean/run_tests/install` targets.

## Control Flow
Non-s390x builds intentionally do nothing. s390x builds compile a static `test_uvdevice` binary with architecture UAPI include paths.

## State And Persistence
No runtime state beyond generated binary.

## Dependencies And Integration Points
Requires s390x architecture headers and `asm/uvdevice.h`. Pairs with `config` requesting the UV UAPI device.

## Risks
The `uname -m` gate means cross-build environments may skip unless build host reports s390x. Static `-Werror` builds can fail on warning changes.

## Test Signals
On s390x, successful build creates `test_uvdevice`; elsewhere silent no-op is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/s390x/uvdevice/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/s390x/uvdevice/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/s390x/uvdevice/config

## Purpose
Kernel config fragment for the s390 Ultravisor UAPI device selftest.

## Important APIs, Types, And Functions
Sets `CONFIG_S390_UV_UAPI=y`.

## Control Flow
Consumed by selftest/kernel config tooling.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Required for `/dev/uv` and `UVIO_IOCTL_ATT` support tested by `test_uvdevice.c`.

## Risks
Only meaningful on s390x. Device access permissions can still cause runtime skip/failure even with config enabled.

## Test Signals
Runtime opening of `/dev/uv` is the practical signal that the config and platform support are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/s390x/uvdevice/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/s390x/uvdevice/test_uvdevice.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/s390x/uvdevice/test_uvdevice.c

## Purpose
Validates Ultravisor UAPI device input validation for attestation ioctls. It focuses on bad user pointers, invalid ioctl control blocks, invalid command encodings, invalid attestation sizes, reserved fields, and invalid attestation buffer addresses.

## Important APIs, Types, And Functions
Uses `/dev/uv`, `UVIO_IOCTL_ATT`, `struct uvio_ioctl_cb`, `struct uvio_attest`, `mmap(PROT_NONE)` fault pages, and kselftest fixtures. Fixtures are `uvio_fixture` with variant `att`, and `attest_fixture`. Helpers `att_inval_sizes_test()` and `att_inval_addr_test()` mutate size/address fields and assert errno.

## Control Flow
`main()` opens `/dev/uv` and skips if unavailable. Fixture tests call the attestation ioctl with null/faulting outer pointers, null/faulting argument pointers, invalid lengths/flags/reserved fields, and malformed ioctl command numbers/types/directions. Attestation-specific tests check zero and too-large ARCB/measurement/additional-data sizes and bad addresses for all attestation buffers.

## State And Persistence
State is fixture-local descriptors, buffers, and one PROT_NONE fault page. No persistent state is modified.

## Dependencies And Integration Points
Requires s390x UV UAPI, `/dev/uv` access, `asm/uvdevice.h`, and kselftest harness.

## Risks
The test mostly validates negative paths, not successful attestation. Fixture teardown closes `uv_fd` only if nonzero, so fd 0 would not be closed, though opening `/dev/uv` should normally return a higher fd.

## Test Signals
Expected signals are `EFAULT`, `EINVAL`, and `ENOTTY` for specific invalid inputs, plus skip message when `/dev/uv` is absent or inaccessible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/s390x/uvdevice/test_uvdevice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/sdsi/sdsi.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/sdsi/sdsi.sh

## Purpose
Wrapper that prepares and runs pytest-based Intel SDSi driver tests.

## Important APIs, Types, And Functions
Uses `command -v python3`, `python3 -c "import pytest"`, `/sbin/modprobe -q -r intel_sdsi`, `/sbin/modprobe -q intel_sdsi`, and `python3 -m pytest sdsi_test.py`.

## Control Flow
It skips with exit 77 if python3, pytest, or module removal is unavailable. It then loads `intel_sdsi` and runs the pytest file, printing `[OK]` on success or `[FAIL]` with exit 1 on failure.

## State And Persistence
It unloads and reloads `intel_sdsi`, affecting live driver state. No files are written by the wrapper.

## Dependencies And Integration Points
Requires python3, pytest, modprobe, and the Intel SDSi driver/platform. It is the kselftest-facing entry point for `sdsi_test.py`.

## Risks
Exit code 77 is used as skip rather than the usual kselftest 4. Removing the driver can disrupt active SDSi devices.

## Test Signals
Wrapper-level signals are `[SKIP]`, `[OK]`, or `[FAIL]`; detailed assertions come from pytest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/sdsi/sdsi.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/sdsi/sdsi_test.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/sdsi/sdsi_test.py

## Purpose
Pytest suite for Intel SDSi auxiliary devices. It verifies driver loading, sysfs file presence, permissions, ownership, sizes, seek behavior, mailbox overflow handling, ENODEV after device removal, and optional kmemleak cleanliness.

## Important APIs, Types, And Functions
Globals discover sockets under `/sys/bus/auxiliary/devices/intel_vsec.sdsi.*`. Helpers are `read_bin_file()`, `get_dev_file_path()`, and `kmemleak_enabled()`. Test classes are `TestSDSiDriver`, `TestSDSiFilesClass`, `TestSDSiMailboxCmdsClass`, and `TestSdsiDriverLocksClass`. It uses `os.stat`, raw sysfs opens/writes, driver `unbind`, `modprobe`, and `/sys/kernel/debug/kmemleak`.

## Control Flow
Tests are parametrized across discovered socket indexes. File tests assert expected sysfs nodes, modes, root ownership, size contracts, no-seek writes for provisioning files, and seekable register reads. Mailbox tests write 1017 bytes to ensure `EOVERFLOW`. Lock/removal tests hold open provisioning fds, unbind the device, expect `ENODEV` on writes, reload underlying modules, and optionally scan kmemleak after removal.

## State And Persistence
The suite can unbind devices and unload/reload `intel_sdsi` and `intel_vsec`. It writes random bytes to provisioning nodes in negative tests and triggers kmemleak scans.

## Dependencies And Integration Points
Requires pytest, root-level sysfs access, Intel VSEC/SDSi hardware, auxiliary bus devices, driver bind/unbind sysfs, and optional kmemleak debugfs.

## Risks
`NUM_SOCKETS` is computed at import time, so module reloads during tests do not refresh parametrization. Lock/removal tests are invasive and can affect system device state. Provisioning writes must be rejected as expected to avoid changing hardware state.

## Test Signals
Signals are pytest assertions for exact modes, sizes, errno (`ESPIPE`, `EOVERFLOW`, `ENODEV`), successful driver reload, and zero-sized kmemleak report when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/sdsi/sdsi_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/usb/usbip/usbip_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/usb/usbip/usbip_test.sh

## Purpose
Manual-style USB/IP integration script that exercises export, bind, unbind, attach, detach, duplicate operations, invalid detach, and module removal/reload behavior for a specified USB bus id.

## Important APIs, Types, And Functions
Parses `-b <busid>` and `-p <usbip tools path>`. Uses `modprobe usbip_host`, `modprobe vhci_hcd`, built `src/usbip` and `src/usbipd`, `lsusb -t`, `rmmod usbip_host`, and `dmesg`.

## Control Flow
The script requires root and built tools, loads modules, starts `usbipd -D`, lists exportable devices, binds/unbinds the bus id with duplicate operation checks, verifies remote listing state, tests attach failure before export, attaches after export, waits for sysfs update, detaches ports 00/01 including repeated and invalid detach, removes `usbip_host`, tries binding without the module, reloads it, and greps dmesg for match-table diagnostics.

## State And Persistence
It changes the selected USB device's bound driver, starts a daemon, attaches devices through vhci, removes kernel modules, and reads kernel log. It does not provide a trap to restore state on early failure.

## Dependencies And Integration Points
Requires a real target USB device bus id, root, usbip userspace tools built in `tools_path`, `usbip_host`, `vhci_hcd`, `lsusb`, and localhost networking.

## Risks
The script mostly prints expected outcomes rather than asserting command status, so regressions can be missed unless output is inspected. Module removal and device binding are disruptive. Hard-coded detach ports 00/01 may not match actual attachment slot.

## Test Signals
Expected signals are visible usbip list/port output transitions, already-bound/already-imported/no-device messages, successful attach/port listing, invalid port error, and dmesg line containing “is not in match_busid table”.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/usb/usbip/usbip_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dt/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/dt/Makefile

## Purpose
Build metadata for devicetree unprobed-device selftest. It conditionally enables the test only when python3 is available.

## Important APIs, Types, And Functions
Defines `PY3 = $(shell which python3 ...)`, `TEST_PROGS := test_unprobed_devices.sh`, generated `compatible_list`, and `TEST_FILES := compatible_ignore_list`. The `compatible_list` target runs `scripts/dtc/dt-extract-compatibles -d $(top_srcdir)`.

## Control Flow
With python3 present, kselftest builds the compatible list and installs/runs the script. Without python3, `all` prints a skip warning.

## State And Persistence
Generates `$(OUTPUT)/compatible_list` from the kernel source tree.

## Dependencies And Integration Points
Depends on `dt-extract-compatibles`, python3, and the runtime script’s ignore list.

## Risks
If the generated compatible list is stale or missing, the runtime test may skip/fail nodes incorrectly. The no-python path skips at build time rather than runtime.

## Test Signals
Successful build creates `compatible_list` and installs `compatible_ignore_list` with the test script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dt/test_unprobed_devices.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/dt/test_unprobed_devices.sh

## Purpose
KTAP shell test that finds enabled devicetree nodes expected to bind to drivers and reports those without corresponding bound devices, excluding compatible strings in an ignore list.

## Important APIs, Types, And Functions
Uses `/proc/device-tree`, generated `compatible_list`, `compatible_ignore_list`, `/sys/devices/*/uevent` `OF_FULLNAME`, and `ktap_helpers.sh` functions such as `ktap_print_header`, `ktap_skip_all`, `ktap_set_plan`, `ktap_test_pass/fail/skip`, and `ktap_print_totals`.

## Control Flow
It skips if `/proc/device-tree` is absent. It builds `nodes_compatible` by walking enabled nodes with `compatible` properties while suppressing children of disabled ancestors. It builds `nodes_dev_bound` from devices with a driver and `OF_FULLNAME`. For each compatible node, it passes if bound, fails if any compatible appears in the generated compatible list and is not ignored, otherwise skips.

## State And Persistence
No state is modified. Variables hold derived node and device lists.

## Dependencies And Integration Points
Requires live devicetree, sysfs OF device names, generated compatible database, ignore list, and KTAP helpers.

## Risks
String matching uses whitespace-separated node paths and regex matching; unusual node names can affect matching. Missing compatible list entries turn unbound nodes into skips, not failures. Disabled ancestor regex can grow large.

## Test Signals
KTAP plan equals number of enabled compatible nodes. Per-node pass/fail/skip indicates binding status and whether the compatible is expected to have a driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dt/test_unprobed_devices.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/Makefile

## Purpose
Builds helper binaries and registers the efivarfs shell test.

## Important APIs, Types, And Functions
Sets `CFLAGS = -Wall`, `TEST_GEN_FILES := open-unlink create-read`, `TEST_PROGS := efivarfs.sh`, and includes `../lib.mk`.

## Control Flow
kselftest compiles `open-unlink.c` and `create-read.c`, then runs `efivarfs.sh`.

## State And Persistence
Generated helper binaries are placed in the output tree.

## Dependencies And Integration Points
Pairs with `config` requesting efivarfs and with shell tests that call the helpers from the working directory.

## Risks
No explicit `KHDR_INCLUDES`; helper compile relies on system headers for `linux/fs.h`.

## Test Signals
Successful build produces `open-unlink`, `create-read`, and the runnable shell test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/config

## Purpose
Kernel config fragment for efivarfs selftests.

## Important APIs, Types, And Functions
Sets `CONFIG_EFIVAR_FS=y`.

## Control Flow
Consumed by selftest config tooling.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Required for mounting efivarfs at `/sys/firmware/efi/efivars`.

## Risks
EFI firmware availability and efivarfs mount state remain runtime prerequisites outside this fragment.

## Test Signals
Runtime shell test checks root privileges and an efivarfs mount as practical config signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/create-read.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/create-read.c

## Purpose
Small helper verifying that a newly created efivarfs variable opened read/write returns EOF before data has been committed, and that closing succeeds.

## Important APIs, Types, And Functions
Uses `open(path, O_RDWR | O_CREAT, 0600)`, `read()`, `close()`, and standard error reporting.

## Control Flow
The program expects one path argument, opens/creates it, reads four bytes, fails if the read returns anything other than 0, closes, and exits success.

## State And Persistence
It creates a variable path supplied by the shell test. The parent script checks the file is gone afterward.

## Dependencies And Integration Points
Called by `efivarfs.sh` in `test_create_read()`. Requires root and efivarfs path semantics.

## Risks
The helper does not unlink/cleanup on failure; caller handles final checks. It tests only the immediate read behavior, not later writes.

## Test Signals
Success is read returning EOF on a new variable. Any open failure or nonzero read is a failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/create-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/efivarfs.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/efivarfs.sh

## Purpose
Main efivarfs behavior suite. It validates variable creation, empty create rejection, helper-based create/read, deletion, zero-size delete semantics, unlink of open variables, valid/invalid filename parsing, truncation protection, and multi-open close semantics.

## Important APIs, Types, And Functions
Uses `/sys/firmware/efi/efivars`, EFI attribute bytes `\x07\x00\x00\x00`, `chattr -i`, `rm`, `stat`, shell redirections, `mknod` FIFO synchronization, and helpers `create-read` and `open-unlink`. Functions include `file_cleanup()`, `check_prereqs()`, `run_test()`, individual `test_*` functions, `setup_test_multiple()`, `waitstart()`, `waitpipe()`, and `endjob()`.

## Control Flow
After root/mount checks, it runs each test in a subshell and records pass/fail. Single-variable tests create/delete a variable with a fixed GUID. Filename tests try accepted and rejected names. Multi-open tests use named pipes to hold one writer and two readers open, closing them in controlled order to validate create/delete only occurs on final close.

## State And Persistence
It writes real EFI variables under efivarfs and uses `/tmp/efivarfs_pipe*` FIFOs. Cleanup removes immutable flags and files when possible.

## Dependencies And Integration Points
Requires root, EFI firmware, efivarfs mounted, `chattr`, helper binaries, and safe firmware variable write capacity.

## Risks
EFI variable writes are invasive and can be limited by firmware storage. The cleanup trap is local to multi-test setup and uses shared `/tmp` pipe names that may collide. Incorrect cleanup can leave test variables.

## Test Signals
Signals are per-test `[PASS]`/`[FAIL]`, correct file size/existence changes, failed invalid filename creation, refused zero truncation, and final-close deletion/creation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/efivarfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/open-unlink.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/open-unlink.c

## Purpose
Helper that verifies reading from an efivarfs variable after unlink through an already-open fd does not return data.

## Important APIs, Types, And Functions
Local helpers `set_immutable()` and `get_immutable()` use `FS_IOC_GETFLAGS` and `FS_IOC_SETFLAGS` to clear `FS_IMMUTABLE_FL`. `main()` uses `open`, `write`, `unlink`, `read`, and EFI attribute bytes.

## Control Flow
It creates a variable with attributes plus one byte of data, clears immutable if set, opens it read-only, unlinks it, then reads from the still-open fd. Returning positive bytes is a failure.

## State And Persistence
Creates and removes one efivarfs variable path supplied by the shell script. It mutates immutable flags for cleanup.

## Dependencies And Integration Points
Called by `efivarfs.sh` `test_open_unlink()`. Requires Linux fs ioctl support and efivarfs behavior.

## Risks
The code writes a `uint32_t` directly into a `char` buffer, relying on alignment tolerated by target architectures. If unlink fails, the variable may remain until caller cleanup.

## Test Signals
Success is variable creation, immutable clearing as needed, successful unlink, and non-positive read after unlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/open-unlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/Makefile

## Purpose
Build and runtime recipe for exec selftests covering execveat, non-regular exec errors, load alignment, recursion depth, null argv, check-exec, and generated helper assets.

## Important APIs, Types, And Functions
Defines `TEST_PROGS`, `TEST_GEN_PROGS`, `TEST_GEN_PROGS_EXTENDED`, `TEST_GEN_FILES`, alignment-derived PIE/static-PIE binaries, `LDLIBS += -lcap`, and build rules for scripts, symlinks, denatured executable, load-address variants, static `false`, and samples from `samples/check-exec`.

## Control Flow
kselftest builds C tests and helper programs, creates runtime files such as `script`, `subdir`, `execveat.symlink`, and `execveat.denatured`, and installs `Makefile` as a runtime dependency for execveat negative tests.

## State And Persistence
Generated files in `$(OUTPUT)` include executables, symlink, copied sample scripts, and directories. `EXTRA_CLEAN` removes moved/temporary artifacts.

## Dependencies And Integration Points
Requires kernel headers, libcap, bash, samples/check-exec sources, and linker support for `-z max-page-size` and static PIE variants.

## Risks
Generated runtime assets are tightly coupled to test expectations. Missing sample files or libcap breaks check-exec tests. Static ASLR/load alignment tests depend on toolchain/linker behavior.

## Test Signals
Successful build creates all named executables and helper files; runtime tests rely on exact file modes and names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/binfmt_script.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/binfmt_script.py

## Purpose
TAP-style Python regression test for shebang (`binfmt_script`) parsing around `BINPRM_BUF_SIZE`, truncated interpreter paths, whitespace, missing newline, and oversized arguments.

## Important APIs, Types, And Functions
Global `SIZE=256`, `NAME_MAX`, and counters track TAP output. The core `test()` helper constructs interpreter paths and scripts with precise byte sizes, creates a fake Perl interpreter, executes the script with `subprocess.Popen(shell=True)`, classifies success by output containing “Executed interpreter”, and cleans generated directories/files.

## Control Flow
The script prints TAP plan 27, runs eight expected-failure cases and nineteen expected-success cases with specific hashbang buffer shapes, then prints totals and verifies test count.

## State And Persistence
Creates temporary nested directories, interpreter files, and `binfmt_script-*` scripts in the current directory, then removes them.

## Dependencies And Integration Points
Requires python3, shell execution, a filesystem supporting long nested paths, and kernel binfmt_script behavior. It is registered by the exec Makefile as a test program.

## Risks
Using `shell=True` and generated paths is safe only because inputs are internally generated. Cleanup assumes no collisions with existing generated names. Path length and `NAME_MAX` behavior vary by filesystem.

## Test Signals
TAP `ok/not ok` lines indicate whether good scripts executed and bad scripts failed. The key signal is absence of unexpected execution for truncated interpreter paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/binfmt_script.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/check-exec-tests.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/check-exec-tests.sh

## Purpose
KTAP shell suite for check-exec securebits/sample interpreter behavior. It verifies how executable-file restriction and denied interactive commands affect direct script execution, indirect interpreter execution, stdin, pipes, and `-c` arguments.

## Important APIs, Types, And Functions
Uses generated `inc`, `set-exec`, `script-exec.inc`, and `script-noexec.inc`. Helper functions are `exec_direct()`, `exec_indirect()`, `exec_stdin_reg()`, `exec_stdin_pipe()`, `exec_argument()`, `exec_interactive()`, and `ktap_test()`.

## Control Flow
It prints a KTAP plan of 28. It first tests default behavior, then runs the same execution shapes under `set-exec -f`, `set-exec -i`, and `set-exec -fi`, checking both exit status and expected output `1` for allowed cases.

## State And Persistence
No persistent state. It changes securebits only in subprocesses spawned through `set-exec`.

## Dependencies And Integration Points
Requires bash, KTAP helpers, libcap-built `set-exec`, sample `inc` interpreter, and kernel support for exec restriction securebits.

## Risks
Direct non-executable scripts return shell-specific `126`, and stderr is redirected away. The test assumes current directory in `PATH` for direct env execution.

## Test Signals
KTAP pass/fail lines identify allowed versus denied execution mode under each securebit combination, with exit status and output validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/check-exec-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/check-exec.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/check-exec.c

## Purpose
C kselftest for `execveat(AT_EXECVE_CHECK)` and exec-related securebits (`SECBIT_EXEC_RESTRICT_FILE`, `SECBIT_EXEC_DENY_INTERACTIVE`, and locked variants). It verifies access checks for executable and non-executable files across mount/file modes and privilege levels, plus securebit mutability/inheritance.

## Important APIs, Types, And Functions
Uses raw `execveat` syscall with `AT_EMPTY_PATH | AT_EXECVE_CHECK`, `prctl(PR_SET/GET_SECUREBITS)`, libcap `cap_set_secbits`, `cap_set_proc`, tmpfs mounts, `memfd_create`, pipes, sockets, device nodes, and kselftest fixtures. Helpers include `drop_privileges()`, `test_secbits_set()`, `fill_exec_fd()`, `fill_exec_path()`, `test_exec_fd()`, and `test_exec_path()`.

## Control Flow
The `access` fixture creates a tmpfs test mount with variant-controlled `MS_NOEXEC` and file execute mode, regular file, directory, device nodes, FIFO, memfd, pipefd, and socket. Tests verify `AT_EXECVE_CHECK` returns success or `EACCES` without actually executing. The `secbits` fixture runs privileged and unprivileged variants, tests setting/unsetting legacy and exec securebits, and checks locked bits cannot be changed in parent or vfork child.

## State And Persistence
Creates and unmounts `./test-mount`, temporary files, memfds, pipes, sockets, and securebit state in the process/children. It drops privileges in selected test paths.

## Dependencies And Integration Points
Requires libcap, `false` helper binary, root/capability support for mount/device-node variants, new securebits definitions, and `AT_EXECVE_CHECK` UAPI.

## Risks
Fixture setup is invasive and can fail without mount privileges. `vfork` child assertions must exit promptly. Dropping capabilities is irreversible within that process path, so ordering relies on fixture isolation.

## Test Signals
Signals are exact `execveat` success/EACCES results for regular files and memfds, EACCES for non-regular files, expected `EPERM` for unprivileged securebit changes, and locked-bit inheritance behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/check-exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/config

## Purpose
Kernel config fragment for exec selftests needing loop/block-device support.

## Important APIs, Types, And Functions
Sets `CONFIG_BLK_DEV=y` and `CONFIG_BLK_DEV_LOOP=y`.

## Control Flow
Consumed by config tooling, not executable.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Supports tests that create/check block device behavior, especially non-regular/check-exec paths using loop-device major/minor.

## Risks
Other exec tests require additional runtime features not expressed here, such as libcap, namespaces, and securebits support.

## Test Signals
Block-device test paths can create/use loop block device nodes when config and privileges allow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/execveat.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/execveat.c

## Purpose
Comprehensive `execveat(2)` selftest covering path-relative execution, absolute paths, `AT_EMPTY_PATH`, `O_PATH`, `O_CLOEXEC`, symlinks, deleted/renamed files, scripts, long paths, errno cases, and `/proc/self/comm` naming.

## Important APIs, Types, And Functions
Uses raw `execveat`, `fork`, `waitpid`, `sendfile`, `realpath`, `mkfifo`, `rename`, `unlink`, and kselftest result helpers. Key helpers are `execveat_()`, `_check_execveat_fail()`, `check_execveat_invoked_rc()`, `check_execveat()`, `concat()`, `open_or_die()`, `exe_cp()`, `check_execveat_pathmax()`, `check_execveat_comm()`, `prerequisites()`, and `run_tests()`.

## Control Flow
`main()` either acts as the executed payload when invoked with args/env or runs the test plan. Setup creates ephemeral executables/scripts, subdirectories, and FIFO. `run_tests()` opens many fd variants, checks successful execution through directory fds, absolute paths, file fds, O_PATH fds, and scripts, then checks expected failures for invalid flags, symlink no-follow, non-regular files, non-executable files, bad fds, and non-directory dirfds. It also validates near-`PATH_MAX` execution and task comm behavior.

## State And Persistence
Creates, renames, unlinks, and leaves generated output-tree files managed by the Makefile clean rules. Uses environment variables `IN_TEST`, `VERBOSE`, and `CHECK_COMM` to distinguish payload mode.

## Dependencies And Integration Points
Requires generated helpers `script`, `execveat.symlink`, `execveat.denatured`, `subdir`, and the binary itself. Integrates with kselftest TAP output.

## Risks
Expected script long-path exit can be 126 or 127 depending on shell/system. The test mutates files while fds are open to validate fd lifetime, so order matters. `TESTS_EXPECTED` must stay in sync with all result-producing checks.

## Test Signals
Signals are 54 planned kselftest results, exact errno matches (`ENOENT`, `EFAULT`, `ELOOP`, `EACCES`, `EINVAL`, `EBADF`, `ENOTDIR`), expected payload exit 99, and comm checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/execveat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/false.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/false.c

## Purpose
Minimal helper executable used by exec tests to represent a valid binary that exits unsuccessfully if actually executed.

## Important APIs, Types, And Functions
Defines only `main()` returning 1.

## Control Flow
When run, exits with status 1.

## State And Persistence
No state.

## Dependencies And Integration Points
Built statically by the exec Makefile and copied into other test files, notably `check-exec.c` and load/access probes where actual execution must be distinguishable from `AT_EXECVE_CHECK`.

## Risks
None beyond build/toolchain availability.

## Test Signals
Exit status 1 indicates real execution occurred.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/false.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/load_address.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/load_address.c

## Purpose
Validates that PIE and static PIE executables are loaded at addresses aligned to the maximum PT_LOAD segment alignment requested by linker `-z max-page-size`.

## Important APIs, Types, And Functions
Uses `dl_iterate_phdr()` with callback `ExtractStatistics()`, `struct dl_phdr_info`, `PT_LOAD`, `PT_INTERP`, `/proc/self/maps`, and kselftest result helpers. Local `struct Statistics` records load address, alignment, and interpreter presence.

## Control Flow
The program prints `/proc/self/maps`, walks only the main executable program headers, records maximum PT_LOAD alignment and whether `PT_INTERP` exists, infers whether interpreter is expected from `argv[0]` containing `.static.`, and emits four results: interpreter presence, alignment found, alignment power-of-two, and load address alignment.

## State And Persistence
No persistent state; reads its own maps and program headers.

## Dependencies And Integration Points
Built into several variants by the Makefile with different max-page-size values and static/dynamic PIE modes.

## Risks
Toolchain/linker behavior determines PT_LOAD alignment. The callback ignores shared library headers by checking `dlpi_name`, which depends on loader reporting conventions.

## Test Signals
Four kselftest results per binary show expected interpreter, nonzero alignment, power-of-two alignment, and zero load-address misalignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/load_address.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/non-regular.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/non-regular.c

## Purpose
Checks that executing non-regular files fails with the expected errno. It covers symlinks with `execv`, directories, block devices, character devices, FIFOs, and sockets with `fexecve`.

## Important APIs, Types, And Functions
Uses kselftest fixtures/variants, `symlink`, `mkdir`, `mknod`, `mkfifo`, `socket`, `execv`, and `fexecve`. Setup helpers include `rm()`, `setup_link()`, `setup_dir()`, `setup_node()`, and `setup_fifo()`.

## Control Flow
For each file variant, setup creates a path named `S_IF*.test`, the test calls `execv()` and checks errno, then teardown removes the path. Socket fixture separately creates an AF_INET stream socket and verifies `fexecve()` returns `EACCES`.

## State And Persistence
Creates temporary files/directories/nodes in the current directory and removes them. Device-node tests may skip if not root.

## Dependencies And Integration Points
Requires `/bin/true` or `/usr/bin/true` for symlink target, root for mknod variants, and kselftest harness.

## Risks
Symlink execution expects `ELOOP`, which depends on using `execv` on a symlink path in this context. Device-node setup can fail under restricted containers.

## Test Signals
Expected errno values are `ELOOP` for symlink and `EACCES` for directory, devices, FIFO, and socket.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/non-regular.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/null-argv.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/null-argv.c

## Purpose
Regression test ensuring exec calls with null or empty argv are converted by the kernel into a single empty `argv[0]` rather than exposing `argc == 0`.

## Important APIs, Types, And Functions
Uses `fork`, `waitpid`, `execve`, kselftest helpers, and macro `FORK(exec)`. `check_result()` validates child exit status.

## Control Flow
When invoked with `argv[0]` already empty, it verifies `argc == 1` and exits success. Otherwise it prints a five-test plan and forks children to re-exec itself with `str`, `NULL`, and `{ NULL }` argv combinations, with null and inherited environments. Parent expects all children to exit 0.

## State And Persistence
No persistent state. Uses process recursion through `execve`.

## Dependencies And Integration Points
Standalone exec selftest built by the exec Makefile.

## Risks
Old kernels exposing `argc == 0` fail early. The test assumes the current executable path in `argv[0]` is usable for re-exec.

## Test Signals
Five pass results indicate all null/empty argv forms became `argc == 1` with empty `argv[0]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/null-argv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/recursion-depth.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/recursion-depth.c

## Purpose
Tests that a shebang script whose interpreter is itself does not recurse indefinitely and fails with `ELOOP`.

## Important APIs, Types, And Functions
Uses `unshare(CLONE_NEWNS)`, `mount` to private root and ramfs on `/tmp`, `creat`, `write`, `execve`, and kselftest helpers.

## Control Flow
The program creates a private mount namespace, mounts ramfs at `/tmp`, writes `/tmp/1` containing `#!/tmp/1`, closes it, then calls `execve("/tmp/1", NULL, NULL)`. It expects return `-1` and `errno == ELOOP`.

## State And Persistence
Creates an isolated mount namespace and a ramfs file at `/tmp/1` inside it. No host filesystem persistence after process exit.

## Dependencies And Integration Points
Requires unprivileged or privileged mount namespace creation and ramfs mount permission. Skips if `unshare` is unavailable or denied with `EPERM`.

## Risks
Requires mount privileges in the namespace. Uses null argv/env intentionally, so it also exercises null argv behavior.

## Test Signals
Single kselftest result passes only when `execve` fails with `ELOOP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/exec/recursion-depth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fchmodat2/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/fchmodat2/Makefile

## Purpose
Builds the `fchmodat2_test` binary with sanitizer instrumentation.

## Important APIs, Types, And Functions
Adds `-Wall -O2 -g -fsanitize=address -fsanitize=undefined $(KHDR_INCLUDES)` to `CFLAGS`, adds `-static-libasan` for non-LLVM builds, sets `TEST_GEN_PROGS := fchmodat2_test`, and includes `../lib.mk`.

## Control Flow
kselftest make compiles the C test; gcc gets static ASAN runtime handling while clang relies on its default static sanitizer behavior.

## State And Persistence
Generated binary only.

## Dependencies And Integration Points
Requires compiler sanitizer support and kernel headers for `__NR_fchmodat2`.

## Risks
Static ASAN linkage can fail on toolchains without sanitizer runtime. Sanitizers can affect portability in minimal environments.

## Test Signals
Successful build produces sanitizer-instrumented `fchmodat2_test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fchmodat2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fchmodat2/fchmodat2_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/fchmodat2/fchmodat2_test.c

## Purpose
Tests `fchmodat2(2)` behavior on regular files and symlinks, especially `AT_SYMLINK_NOFOLLOW`.

## Important APIs, Types, And Functions
Uses raw syscall wrapper `sys_fchmodat2()`, `mkdtemp`, `openat`, `symlinkat`, `fstatat(AT_SYMLINK_NOFOLLOW)`, `unlinkat`, and kselftest helpers. Structures/functions include `struct testdir`, `setup_testdir()`, `cleanup_testdir()`, `expect_mode()`, `test_regfile()`, and `test_symlink()`.

## Control Flow
Each test creates a temporary directory containing `regfile` and `symlink`. The regular-file test chmods with no flags and with `AT_SYMLINK_NOFOLLOW`, checking target modes. The symlink test chmods through the symlink, checks target changed while symlink mode remains default, then tries nofollow chmod on the symlink itself and passes or skips depending on filesystem support.

## State And Persistence
Creates `/tmp/ksft-fchmodat2.XXXXXX`, a file, and a symlink, then removes them.

## Dependencies And Integration Points
Requires `__NR_fchmodat2`, filesystem support for symlink mode changes for full pass, and kselftest.

## Risks
The symlink nofollow path can legitimately fail on filesystems such as xfs or btrfs, so the test skips that case. Cleanup error path references `testdir->dfd` before assignment in one branch, but fatal setup failure exits.

## Test Signals
Two planned results: regular file pass if modes become `0100640` then `0100600`; symlink pass or skip depending on nofollow support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fchmodat2/fchmodat2_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filelock/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filelock/Makefile

## Purpose
Registers the open-file-description lock test binary.

## Important APIs, Types, And Functions
Defines `TEST_GEN_PROGS := ofdlocks` and includes `../lib.mk`.

## Control Flow
kselftest builds `ofdlocks.c`.

## State And Persistence
Generated binary only.

## Dependencies And Integration Points
Depends on kernel support for `F_OFD_SETLK` and `F_OFD_GETLK`.

## Risks
No special CFLAGS are set; warnings are not elevated.

## Test Signals
Successful build creates `ofdlocks`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filelock/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filelock/ofdlocks.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filelock/ofdlocks.c

## Purpose
Tests open-file-description lock conflict and query behavior, including `F_OFD_GETLK` with `F_UNLCK` and length-zero ranges.

## Important APIs, Types, And Functions
Uses `fcntl(F_OFD_SETLK)`, `fcntl(F_OFD_GETLK)`, `struct flock`, and helpers `lock_set()` and `lock_get()`.

## Control Flow
The program creates `/tmp/aa`, opens it twice, unlinks it, sets a read lock on the first fd, verifies another read lock does not conflict, verifies write lock query conflicts, queries lock info from the locking fd with `F_UNLCK`, compares length-one and length-zero queries, and verifies the second fd does not report its own lock.

## State And Persistence
Creates and unlinks `/tmp/aa`, keeping the file alive through open fds only.

## Dependencies And Integration Points
Requires OFD lock support in the kernel and writable `/tmp`.

## Risks
The test uses `assert()` for open failures and returns `-1` on failures rather than full kselftest result accounting. `/tmp/aa` name can collide if already present, because open uses `O_EXCL`.

## Test Signals
Printed `[SUCCESS]` lines and zero exit indicate correct OFD lock behavior; failures return nonzero after mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filelock/ofdlocks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/Makefile

## Purpose
Top-level filesystem selftest build metadata for several generic filesystem tests.

## Important APIs, Types, And Functions
Adds `$(KHDR_INCLUDES)` to `CFLAGS`, defines `TEST_GEN_PROGS := devpts_pts file_stressor anon_inode_test kernfs_test fclog`, `TEST_GEN_PROGS_EXTENDED := dnotify_test`, and includes `../lib.mk`.

## Control Flow
kselftest builds standard generated programs and extended helper/test binaries.

## State And Persistence
Generated binaries only.

## Dependencies And Integration Points
Pulls in tests for devpts, anonymous inodes, kernfs, fclog, stress, and dnotify. Some source files are outside this subset but are built here.

## Risks
Adding a program here without matching source/runtime prerequisites can break the whole directory build. Extended dnotify test is built but not necessarily run as a default test program.

## Test Signals
Successful build produces the listed filesystem test binaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/anon_inode_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/anon_inode_test.c

## Purpose
Verifies that anonymous inode file descriptors returned by the new mount API `fsopen()` reject unsupported file operations: chown, chmod, exec, and procfd reopen.

## Important APIs, Types, And Functions
Uses wrapper `sys_fsopen("tmpfs", 0)`, `fchown`, `fchmod`, `execveat(..., AT_EMPTY_PATH)`, `dup2`, `open("/proc/self/fd/500")`, and kselftest harness.

## Control Flow
Each test opens a tmpfs fs context fd. It then attempts one unsupported operation and asserts the expected errno: `EOPNOTSUPP` for chown/chmod, `EACCES` for exec, and `ENXIO` for reopening through procfd after dup2.

## State And Persistence
Creates anonymous fs context fds only; closes them after each test.

## Dependencies And Integration Points
Requires new mount API support and wrappers from `wrappers.h`.

## Risks
Tests assume procfd number 500 is available for `dup2`. Missing fsopen support fails setup rather than skipping.

## Test Signals
Four kselftest cases pass on exact unsupported-operation errno values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/anon_inode_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/binderfs/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/binderfs/Makefile

## Purpose
Build metadata for binderfs selftests.

## Important APIs, Types, And Functions
Adds `$(KHDR_INCLUDES) -pthread` to `CFLAGS`, defines `TEST_GEN_PROGS := binderfs_test`, and includes `../../lib.mk`.

## Control Flow
kselftest builds the threaded binderfs C test.

## State And Persistence
Generated binary only.

## Dependencies And Integration Points
Pairs with config enabling Android binderfs and binder IPC.

## Risks
Requires pthread support and Android binder UAPI headers.

## Test Signals
Successful build creates `binderfs_test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/binderfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/binderfs/binderfs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/binderfs/binderfs_test.c

## Purpose
Tests binderfs mount/device lifecycle in privileged and unprivileged user namespaces, plus a stress regression for binderfs device reference lifetime after unmount.

## Important APIs, Types, And Functions
Uses `mount("binder")`, `BINDER_CTL_ADD`, `BINDER_VERSION`, binderfs feature files, user namespace id maps, `socketpair`, `pthread`, and kselftest harness. Helpers include `change_mountns()`, `__do_binderfs_test()`, `wait_for_pid()`, `setid_userns_root()`, `read_nointr()`, `write_nointr()`, `write_id_mapping()`, `change_userns()`, `change_idmaps()`, and `binder_version_thread()`.

## Control Flow
The common test creates a private mount namespace, mounts binderfs, opens `binder-control`, adds `my-binder`, opens it and requests `BINDER_VERSION`, unlinks the device, verifies `binder-control` cannot be unlinked, and opens expected feature files. Privileged test runs directly as root; unprivileged test forks into a user namespace with uid/gid maps. Stress test creates 1000 binder devices in a user/mount namespace, unmounts binderfs, then concurrently calls `BINDER_VERSION` on all retained fds.

## State And Persistence
Creates temporary binderfs mountpoints under `/tmp`, binder devices, user/mount namespaces, threads, and many open fds. Cleanup unmounts and removes mount directories where possible.

## Dependencies And Integration Points
Requires `CONFIG_ANDROID_BINDERFS`, `CONFIG_ANDROID_BINDER_IPC`, user namespace support, mount permissions, and binder UAPI headers.

## Risks
Stress uses many fds and threads and can hit resource limits. Unprivileged user namespace setup depends on `/proc/*/setgroups`, uid_map, and gid_map policy. Feature-file list must track binderfs kernel features.

## Test Signals
Signals include successful binderfs mount, device add/open/version/unlink, `EPERM` on binder-control unlink, feature file presence, and no failure during post-unmount threaded `BINDER_VERSION`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/binderfs/binderfs_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/binderfs/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/binderfs/config

## Purpose
Kernel config fragment for binderfs selftests.

## Important APIs, Types, And Functions
Sets `CONFIG_ANDROID_BINDERFS=y` and `CONFIG_ANDROID_BINDER_IPC=y`.

## Control Flow
Consumed by config tooling.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Required for mounting binderfs and exercising binder device ioctls.

## Risks
Runtime namespace and permission policy can still skip/fail tests despite config.

## Test Signals
Successful binderfs mount and binder-control access indicate config support is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/binderfs/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/devpts_pts.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/devpts_pts.c

## Purpose
Validates `TIOCGPTPEER` and `/proc/<pid>/fd` symlink behavior for standard, invalid, and non-standard devpts mounts in a private mount namespace.

## Important APIs, Types, And Functions
Uses `unshare(CLONE_NEWNS)`, devpts mounts, bind mounts, `open` on ptmx, `unlockpt`, `ioctl(TIOCGPTPEER)`, `setsid`, `TIOCSCTTY`, `dup2`, `readlink`, `fork`, and `waitpid`. Helpers include `terminal_dup2()`, `terminal_set_stdfds()`, `login_pty()`, `wait_for_pid()`, `resolve_procfd_symlink()`, `do_tiocgptpeer()`, and three `verify_*` functions.

## Control Flow
The program skips unless stdin is a terminal, creates a private mount namespace, makes mounts private, tests `/dev/ptmx` bind-mounted from `/dev/pts/ptmx`, tests an invalid bind to a regular temp file expecting failure, then unmounts `/dev/pts`, mounts a new devpts instance at a temporary path, and verifies procfd symlinks point to that mountpoint.

## State And Persistence
Modifies mount namespace only: bind mounts/unmounts `/dev/ptmx` and `/dev/pts` inside the private namespace and creates temp mountpoints/files.

## Dependencies And Integration Points
Requires terminal stdin, mount namespace privileges, devpts, ptmx, and `TIOCGPTPEER` support.

## Risks
The test is skipped without a TTY, making automated coverage environment-dependent. Temporary cleanup uses `unlink` on directories in some branches, which may be imperfect but namespace exit discards mounts.

## Test Signals
Success is valid procfd symlink prefix for slave ptys, failure for invalid ptmx bind, and skip if `TIOCGPTPEER` is unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/devpts_pts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/dnotify_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/dnotify_test.c

## Purpose
Manual/extended dnotify sample that prints events for modifications or file creation in the current directory.

## Important APIs, Types, And Functions
Uses `sigaction` with `SA_SIGINFO`, `F_SETSIG`, `F_NOTIFY`, `DN_MODIFY`, `DN_CREATE`, `DN_MULTISHOT`, and signal handler storing `si_fd` in `event_fd`.

## Control Flow
It installs a realtime signal handler, opens `.`, configures dnotify to send `SIGRTMIN+1`, and loops forever pausing and printing the fd that generated an event.

## State And Persistence
Holds one directory fd and installs process signal state. No file writes.

## Dependencies And Integration Points
Built as `TEST_GEN_PROGS_EXTENDED`, useful as a manual test rather than finite automated kselftest.

## Risks
The infinite loop means it is unsuitable for default automated runs. It does not check return values for `sigaction`, `open`, or `fcntl`.

## Test Signals
Console output `Got event on fd=...` after creating/modifying files in the directory confirms dnotify delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/dnotify_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/Makefile

## Purpose
Build metadata for empty mount namespace selftests.

## Important APIs, Types, And Functions
Adds `-Wall -O2 -g $(KHDR_INCLUDES) $(TOOLS_INCLUDES)` to `CFLAGS`, links libcap, defines `TEST_GEN_PROGS := empty_mntns_test overmount_chroot_test clone3_empty_mntns_test`, includes `../../lib.mk`, and adds dependencies on `../utils.c`.

## Control Flow
kselftest builds three C binaries, linking each with filesystem utility helpers.

## State And Persistence
Generated binaries only.

## Dependencies And Integration Points
Requires statmount/listmount headers/helpers, clone3 selftest headers, and libcap utilities through `../utils.c`.

## Risks
The tests require newer kernel APIs; build can succeed while runtime skips unsupported flags.

## Test Signals
Successful build creates all three empty mount namespace test executables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/clone3_empty_mntns_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/clone3_empty_mntns_test.c

## Purpose
Tests `clone3()` with `CLONE_EMPTY_MNTNS`, ensuring it creates an empty/nullfs mount namespace, implies `CLONE_NEWNS`, composes correctly with other clone flags, rejects invalid combinations, and supports overmounting and `setns`.

## Important APIs, Types, And Functions
Uses `sys_clone3`, `CLONE_EMPTY_MNTNS`, `CLONE_NEWNS`, `CLONE_NEWUSER`, `CLONE_NEWPID`, `CLONE_PIDFD`, `CLONE_FS`, `setns`, `listmount`, `statmount_alloc`, new mount API wrappers, `chroot`, and helpers from `empty_mntns.h` and `utils.c`. Key helpers are `clone3_empty_mntns()` and `clone3_empty_mntns_supported()`.

## Control Flow
A fixture skips if clone3 empty namespaces are unsupported. Tests fork into user namespaces, clone children with empty mount namespaces, and assert exactly one root mount, root equals cwd, parent mounts unchanged, root fs type is `nullfs`, listmount returns one entry, repeated clones have distinct mount ids, and `setns` works. Other tests verify explicit `CLONE_NEWNS`, `CLONE_NEWUSER`, UTS/IPC, PID namespace pid 1, pidfd output, `CLONE_FS` rejection, EPERM without caps, tmpfs overmount/chroot, unknown flag rejection, and normal `CLONE_NEWNS` full-copy behavior.

## State And Persistence
Creates child processes, user/mount namespaces, temporary tmpfs mounts, bind mounts, pipes, pidfds, and files in child namespaces. No persistent host files are intended.

## Dependencies And Integration Points
Requires clone3, the new empty mount namespace flag, user namespace helpers, statmount/listmount, and new mount API wrappers.

## Risks
Very new UAPI constants and syscalls make this highly kernel-version dependent. Many tests encode child exit status values for failure localization but parent only sees nonzero. Overmount tests rely on `nullfs` semantics and `MOVE_MOUNT_F_EMPTY_PATH`.

## Test Signals
Signals are successful fixture support probe, one-mount listmount counts, `nullfs`/`tmpfs` statmount fs types, expected `EINVAL`/`EPERM`, valid pidfd, pid 1 in new PID namespace, and unchanged parent mount count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/clone3_empty_mntns_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/empty_mntns.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/empty_mntns.h

## Purpose
Shared header for empty mount namespace tests, defining missing UAPI constants and a helper to count mounts.

## Important APIs, Types, And Functions
Includes `statmount.h`, defines `UNSHARE_EMPTY_MNTNS` as `0x00100000` and `CLONE_EMPTY_MNTNS` as `1ULL << 37` if absent, and implements `count_mounts()` using `listmount(LSMT_ROOT, ...)` into a fixed `uint64_t list[4096]`.

## Control Flow
Header-only helper is included by test programs. `count_mounts()` returns the `listmount` syscall result.

## State And Persistence
No persistent state; uses stack buffer per call.

## Dependencies And Integration Points
Depends on statmount/listmount wrappers from the adjacent selftest infrastructure.

## Risks
The fixed 4096 mount buffer can undercount/fail on very large mount namespaces; empty namespace tests expect one mount, but parent-copy regression tests only need lower-bound checks.

## Test Signals
`count_mounts() == 1` is the central assertion signal for empty namespace creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/empty_mntns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/empty_mntns_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/empty_mntns_test.c

## Purpose
Tests empty mount namespace creation through `unshare(UNSHARE_EMPTY_MNTNS)`. It verifies basic semantics, namespace combinations, permission errors, cwd reset, statmount/listmount properties, repeated unshare, overmounting nullfs with tmpfs, and regressions for ordinary namespace behavior.

## Important APIs, Types, And Functions
Uses `unshare`, `UNSHARE_EMPTY_MNTNS`, `CLONE_NEWUSER`, `CLONE_NEWNS`, `CLONE_NEWUTS`, `CLONE_NEWIPC`, `listmount`, `statmount`, `statmount_alloc`, new mount API wrappers (`fsopen`, `fsconfig`, `fsmount`, `move_mount`), `chroot`, and helpers from `utils.c` and `empty_mntns.h`. Support probe is `unshare_empty_mntns_supported()`.

## Control Flow
The fixture skips if unsupported. Tests fork children, enter user namespaces where needed, call `unshare(UNSHARE_EMPTY_MNTNS)`, and assert one mount, root/cwd identity, permissions, root parent relationship, listmount single entry, and distinct mount IDs on repeated calls. Overmount test confirms `nullfs` root is immutable, mounts tmpfs over `/`, chroots via mount fd, then writes a file. Non-fixture tests verify invalid flags reject, normal `CLONE_NEWNS` copies mount tree, and unrelated UTS namespace behavior still works.

## State And Persistence
Creates child namespaces, tmpfs/bind mounts, temporary directories, and test files within child namespaces. No persistent host state is intended.

## Dependencies And Integration Points
Requires new `UNSHARE_EMPTY_MNTNS` support, user namespace privileges, statmount/listmount, and new mount API wrappers.

## Risks
Tests target new kernel behavior and can skip/fail on older kernels. `open("/test", O_CREAT)` expecting `ENOENT` encodes nullfs lookup behavior. Parent sees only child exit status, so debugging uses source line mapping.

## Test Signals
Signals are exact one-mount counts, root/cwd mount-id equality, `nullfs` then `tmpfs` fs types, `EINVAL` for invalid flags, full-copy count for regular `CLONE_NEWNS`, and successful file creation after tmpfs overmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/empty_mntns_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/overmount_chroot_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/overmount_chroot_test.c

## Purpose
Regression test for chrooting into the topmost layer of a repeatedly overmounted mountpoint. It verifies overmount layers remain distinct and lower-layer files are hidden after chroot.

## Important APIs, Types, And Functions
Uses user and mount namespaces, `pivot_root`, tmpfs mounts, repeated `mount("tmpfs", "/newroot")`, `get_unique_mnt_id()`, `statmount_alloc()`, `chroot`, `chdir`, and `count_mounts()`. Helper `setup_root()` creates a tmpfs root and detaches the old root.

## Control Flow
The child enters a user namespace, unshares a private mount namespace, pivots to a tmpfs root, creates `/newroot`, mounts a base tmpfs there, writes a marker, then overmounts it five times, recording each mount id and marker. It verifies the visible `/newroot` is the topmost id, chroots into it, checks `/` has the same id, confirms only the topmost marker is visible, and verifies fs type `tmpfs`.

## State And Persistence
All mounts and files are in the child namespace after pivot_root. No persistent host state is intended.

## Dependencies And Integration Points
Requires user namespace helper, mount namespace privileges, tmpfs, pivot_root syscall, statmount/listmount helpers.

## Risks
Pivot-root and mount privileges are environment-sensitive. The test assumes lower-layer marker files are hidden by overmounts, so any unexpected path traversal behavior fails.

## Test Signals
Success signals include mount count increase, topmost mount-id equality before/after chroot, topmost marker present, lower markers absent, and statmount fs type `tmpfs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/overmount_chroot_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/epoll/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/epoll/Makefile

## Purpose
Build metadata for the epoll wakeup filesystem selftest.

## Important APIs, Types, And Functions
Adds `$(KHDR_INCLUDES)` to `CFLAGS`, links pthread with `LDLIBS += -lpthread`, sets `TEST_GEN_PROGS := epoll_wakeup_test`, and includes `../../lib.mk`.

## Control Flow
kselftest builds the threaded epoll wakeup test binary from the directory’s source.

## State And Persistence
Generated binary only.

## Dependencies And Integration Points
Requires pthread and kernel headers. The generated test exercises epoll wakeup semantics but that source file is outside this work item.

## Risks
This Makefile only covers build metadata; behavioral coverage lives in `epoll_wakeup_test.c`. Link failures occur if pthread support is unavailable.

## Test Signals
Successful build produces `epoll_wakeup_test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/epoll/Makefile -->
