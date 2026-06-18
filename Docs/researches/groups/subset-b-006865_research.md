# subset-b-006865 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib.sh

## Purpose
This Bash library is the shared harness for Linux networking selftests. It provides kselftest status constants, namespace setup and cleanup, wait helpers, test result aggregation, tc/qdisc counter utilities, netdevsim helpers, and automatically deferred cleanup wrappers for temporary network configuration.

## Important APIs and Functions
The exported surface is function-oriented. `setup_ns`, `cleanup_ns`, `cleanup_all_ns`, and `in_all_ns` manage randomly suffixed network namespaces through the global `NS_LIST`. `busywait`, `slowwait`, `busywait_for_counter`, and `slowwait_for_counter` poll commands until predicates succeed. `ksft_status_merge`, `ksft_exit_status_merge`, `log_test`, `check_err`, `check_fail`, `check_err_fail`, `xfail`, `xfail_on_slow`, `omit_on_slow`, and `xfail_on_veth` implement kselftest-style pass/fail/skip/xfail result handling. `create_netdevsim`, `create_netdevsim_port`, and `cleanup_netdevsim` manipulate the netdevsim bus. `tc_rule_stats_get`, `tc_rule_handle_stats_get`, `tc_set_flower_counter`, and `tc_get_flower_counter` read or create tc statistics. The `adf_*` functions wrap `ip`, `bridge`, and route changes with deferred reversal.

## Control Flow and State
Tests source this file, call setup functions, then either run individual checks or invoke `tests_run`, which executes `TESTS` or `ALL_TESTS` inside `in_defer_scope`. State is persisted only in shell globals: `NS_LIST`, `EXIT_STATUS`, `RET`, `retmsg`, and `FAIL_TO_XFAIL`. Namespace cleanup kills remaining namespace processes before deleting namespaces and busy-waits for disappearance. Deferred cleanup comes from `lib/sh/defer.sh`, so changes made with `adf_*` are unwound in reverse scope order.

## Dependencies and Integration
The library assumes Bash, `iproute2`, `jq`, `tc`, `bridge`, `sysctl`, `modprobe`, `udevadm`, `netdevsim`, and kselftest exit conventions. It is integrated by many shell tests under `tools/testing/selftests/net`, including the lwt and macvlan scripts in this subset.

## Risks and Test Signals
The helpers require root and kernel namespace support. `eval` is used for namespace variable assignment and deferred command execution, so callers must pass trusted arguments. `mktemp -u` creates names before use and can theoretically race, though randomized names reduce collisions. Successful tests usually emit formatted `TEST:` lines and use `EXIT_STATUS`; failure signals include nonzero `RET`, failed namespace deletion warnings, tc counter mismatches, or skipped tests when required tools are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/Makefile

## Purpose
This Makefile builds and packages the reusable networking selftest helper programs, BPF objects, Python scripts, shell helpers, and YNL/spec files needed by tests outside this directory.

## Important Targets and Variables
`CFLAGS` enables warnings, debug info, optimization, kernel UAPI include paths, and kselftest include paths. `TEST_FILES` installs the kernel YNL tree, netlink specs, and `ksft_setup_loopback.sh`. `TEST_GEN_FILES` builds object files for all `*.bpf.c` files plus the `csum`, `gro`, and `xdp_helper` executables. `TEST_INCLUDES` collects Python and shell helper files. The file includes the common `../../lib.mk` and networking BPF rules from `../bpf.mk`.

## Control Flow and State
The Makefile is declarative; build state is the generated binaries/objects and installed selftest file set. Wildcards automatically add new BPF C files and helper includes without target edits.

## Dependencies and Integration
It depends on the kernel selftests Makefile framework, a C compiler, libbpf/BPF build support from `bpf.mk`, and kernel headers. It feeds the helper artifacts consumed by shell and Python networking tests, including XDP, GRO, checksum, and YNL-based tests.

## Risks and Test Signals
The broad wildcard for `*.bpf.c` can expose build breaks when new BPF programs are added. Header paths must match the kernel source tree layout. A successful signal is creation of all `TEST_GEN_FILES`; failures will usually appear as compiler, linker, or BPF skeleton/toolchain errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/csum.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/csum.c

## Purpose
`csum.c` is a standalone checksum-offload exerciser for IPv4/IPv6 TCP and UDP receive and transmit paths. It can craft good, bad, zero-disabled, zero-sum, raw IP, UDP-socket, or PF_PACKET/VNET_HDR packets to verify NIC and kernel checksum behavior.

## Important APIs and Functions
Configuration is stored in `cfg_*` globals populated by `parse_args`. Packet construction flows through `build_packet_ipv4`, `build_packet_ipv6`, `build_packet_udp`, `build_packet_tcp`, `build_packet_udp_encap`, and `build_packet`, using `checksum_nofold`, `checksum_fold`, and `checksum` for pseudo-header and transport checksums. Transmit paths use `open_inet`, `open_packet`, `send_inet`, and `send_packet`. Receive paths use `recv_prepare_udp`, `recv_prepare_packet`, `recv_prepare_packet_filter`, `recv_packet`, `recv_udp`, and protocol-specific validators such as `recv_verify_packet_ipv4`, `recv_verify_packet_ipv6`, `recv_verify_packet_udp`, and `recv_verify_packet_tcp`.

## Control Flow and State
`main` parses options, opens receive sockets before transmitting, optionally transmits `cfg_num_pkt` packets, then polls for packets until `cfg_timeout_ms` expires. The sender either writes payload via UDP socket, raw socket, or PF_PACKET with `PACKET_VNET_HDR` to request `CHECKSUM_PARTIAL`. The receiver consumes both UDP socket delivery and PF_PACKET auxdata, counting matching packets and validating checksums. Runtime state lives entirely in process globals and sockets; no persistent files are written.

## Dependencies and Integration
The program depends on Linux raw sockets, PF_PACKET, `PACKET_AUXDATA`, optional `PACKET_VNET_HDR`, BPF socket filters, UAPI headers, and kselftest helpers. It is built by `lib/Makefile` and intended for hardware/NIC checksum testing, not a default single-host kselftest.

## Risks and Test Signals
It requires privileges and accurate source/destination addresses and MACs for PF_PACKET mode. Randomization can change payload length per packet and may interact with GRO, so GSO packets with `TP_STATUS_CSUMNOTREADY` are skipped for checksum validation. Important pass signals are stderr `OK`, observed PF_PACKET count at least `cfg_num_pkt`, UDP delivery for good UDP checksums, no UDP delivery for bad checksums, and `TP_STATUS_CSUM_VALID` never being reported for intentionally bad checksums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/csum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/gro.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/gro.c

## Purpose
`gro.c` is a raw-packet GRO conformance helper. It sends or receives crafted Ethernet/IP/TCP packets and validates whether GRO coalesces or flushes packets for data, ACK, TCP flag, TCP option, checksum, IPv4/IPv6 header, extension-header, fragmentation, size-limit, and capacity cases.

## Important APIs and Functions
`parse_args` selects IPv4, IPv6, IP-in-IP, IPv6-in-IPv6, sender/receiver mode, test name, interface, addresses, MACs, flow count, and verbosity. Packet generation is centered on `create_packet`, `fill_datalinklayer`, `fill_networklayer`, `fill_transportlayer`, `tcp_checksum`, and `write_packet`. Specialized senders include `send_data_pkts`, `send_flags`, `send_changed_checksum`, `send_changed_seq`, `send_changed_ts`, `send_diff_opt`, `send_ip_options`, `send_fragment4`, `send_fragment6`, `send_flush_id_case`, `send_ipv6_exthdr`, `send_large`, `send_ack`, and `send_capacity`. Receiver validation uses `setup_sock_filter`, `bind_packetsocket`, `check_recv_pkts`, and `check_capacity_pkts`.

## Control Flow and State
After argument parsing, `main` computes `tcp_offset`, `total_hdr_len`, and Ethernet protocol based on encapsulation mode. Sender mode uses a PF_PACKET raw socket, optional `SO_TXTIME`, and a large branch on `testname` to emit the exact packet sequence followed by a FIN marker. Receiver mode creates a filtered PF_PACKET socket, calls `ksft_ready`, then validates received packet geometry against expected coalesced payload sizes for the same `testname`. State is process-local globals; there is no disk persistence.

## Dependencies and Integration
The helper depends on Linux PF_PACKET raw sockets, classic BPF socket filters, `SO_TXTIME`, Ethernet/IP/TCP headers, and `ksft_ready` from `ksft.h` for parent/child synchronization. It is built by `lib/Makefile` and used by GRO-focused selftests that coordinate separate sender and receiver instances.

## Risks and Test Signals
Timing is intentionally acknowledged as flaky because GRO windows are time-sensitive. Tests require root, correct MAC/interface parameters, and traffic isolation. Header offsets vary with IPv4 options and IPv6 extension headers; mistakes in offset calculation can cause false failures. Pass signals are `Test succeeded` or `Gro::<test> test passed`; capacity tests additionally print `STATS: received=... wire=... coalesced=...` and fail if expected coalescing, packet ordering, or payload geometry differs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/gro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/ksft.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/ksft.h

## Purpose
This small C header provides readiness and wait synchronization helpers for compiled networking selftest helpers run under the Python `bkg`/kselftest environment.

## Important APIs and Functions
`ksft_ready()` writes `ready\n` to the file descriptor named by `KSFT_READY_FD`, or stdout when the variable is absent. `ksft_wait()` reads one byte from `KSFT_WAIT_FD`, or stdin when the variable is absent. Both close non-stdio descriptors after use and report invalid fd values or I/O errors to stderr.

## Control Flow and State
There is no persistent state. The helpers bridge environment variables into file-descriptor handshakes: child programs call `ksft_ready()` after binding/listening and `ksft_wait()` before exit when the parent owns shutdown timing.

## Dependencies and Integration
It depends only on libc `getenv`, `atoi`, `write`, `read`, `close`, and stdio. It integrates with `lib/py/utils.py` command helpers, especially background commands using `ksft_ready` and `ksft_wait`, and is used by `gro.c` and `xdp_helper.c`.

## Risks and Test Signals
Fd `0` is treated as invalid for environment-provided descriptors, while missing variables deliberately fall back to stdio. A blocked `ksft_wait()` can hang if the parent never writes the byte. The readiness signal is the exact `ready\n` payload expected by the Python helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/ksft.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/ksft_setup_loopback.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/ksft_setup_loopback.sh

## Purpose
This setup wrapper runs a kselftest over a real network interface in hardware loopback mode while isolating the actual test inside two macvlan-backed namespaces.

## Important APIs and Functions
The script is primarily linear. `cleanup` removes server/client macvlan interfaces and namespaces, disables NIC loopback with `ethtool -K`, restores `gro_flush_timeout` and `napi_defer_hard_irqs`, and exits with the original status. It exports `LOCAL_V6`, `REMOTE_V6`, `NETIF=server`, `REMOTE_TYPE=netns`, and `REMOTE_ARGS=<client namespace>` for the invoked test.

## Control Flow and State
The script validates `NETIF`, snapshots sysfs GRO/NAPI settings, creates random server and client namespaces, enables hardware loopback, adjusts NAPI/GRO timers, creates server/client macvlans with fixed MAC and IPv6 addresses, and finally runs the requested command with `ip netns exec` inside the server namespace. Persistent state is limited to temporary namespaces, macvlan devices, NIC loopback feature state, and sysfs knob values restored by the EXIT trap.

## Dependencies and Integration
It depends on root, `ip`, `ethtool`, sysfs paths under `/sys/class/net/$NETIF`, macvlan support, and a NIC that supports loopback. It replaces older loopback setup scripts and is installed by the networking helper Makefile.

## Risks and Test Signals
It changes real hardware state, so cleanup correctness matters. Missing sysfs attributes or unsupported loopback will fail early. Because the test sees only the macvlan name `server`, callers must rely on exported environment variables rather than the original `NETIF`. Successful setup prints namespace names and then delegates pass/fail status to the wrapped test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/ksft_setup_loopback.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/__init__.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/__init__.py

## Purpose
This package initializer presents a single import surface for Python networking selftests.

## Important APIs and Types
It re-exports constants, KTAP helpers, assertions, namespace classes, netdevsim classes, command wrappers, BPF map helpers, and YNL family wrappers through `__all__`. Key exports include `ksft_run`, `ksft_exit`, `NetNS`, `NetNSEnter`, `cmd`, `bkg`, `defer`, `bpftool`, `ip`, `NetdevSimDev`, `YnlFamily`, `RtnlFamily`, `EthtoolFamily`, `NetdevFamily`, and `Netlink`.

## Control Flow and State
Importing this module imports the submodules and exposes their names. It has no independent runtime control flow or state beyond Python import caching.

## Dependencies and Integration
It depends on sibling modules in `lib/py`. Tests can write `from lib.py import ...` without knowing the internal module layout.

## Risks and Test Signals
Import failures in any re-exported module can prevent all users from starting. The `__all__` list is the integration contract; omissions there affect wildcard imports and public package clarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/bpf.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/bpf.py

## Purpose
This module provides small Python wrappers for common `bpftool` operations used by BPF/XDP selftests.

## Important APIs and Functions
`_format_hex_bytes(value)` encodes a signed 32-bit integer as little-endian hex bytes for bpftool CLI syntax. `bpf_map_set(map_name, key, value)` updates a named BPF map entry. `bpf_map_dump(map_id)` returns a dictionary of formatted array-map key/value entries from JSON output. `bpf_prog_map_ids(prog_id)` reads a BPF program's map IDs, resolves their names, and returns a name-to-ID mapping.

## Control Flow and State
All functions are synchronous wrappers around `bpftool` invocations. The only state modified is kernel BPF map state via `bpf_map_set`; dump and ID lookup are read-only from the module perspective.

## Dependencies and Integration
It depends on `bpftool` from `utils.py`, JSON output support in bpftool, and map/program names matching loaded BPF objects. XDP tests can use it to configure `map_xdp_setup` and read stats maps.

## Risks and Test Signals
`_format_hex_bytes` uses `signed=True`, so values outside signed 32-bit range can raise errors. The formatted fields returned by bpftool differ by map type and kernel/bpftool version. Successful signals are valid JSON parse results and expected map IDs or updated entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/bpf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/consts.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/consts.py

## Purpose
This module centralizes path constants and the current test program name for Python network selftests.

## Important APIs and Values
`KSFT_DIR` resolves to the selftests tree rooted above `lib/py`. `KSRC` resolves to the kernel source root. `KSFT_MAIN_NAME` is the current script basename without suffix, used in KTAP result names.

## Control Flow and State
The module performs path resolution at import time using `Path(__file__)` and `sys.argv[0]`. There is no mutable state.

## Dependencies and Integration
It is consumed by `ksft.py` for KTAP naming and by `ynl.py` to choose in-tree versus installed YNL/spec paths.

## Risks and Test Signals
The relative path calculation assumes the kernel selftest directory layout. Running scripts from unusual wrappers can alter `sys.argv[0]` and therefore KTAP case names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/consts.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/ksft.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/ksft.py

## Purpose
This module implements a Python kselftest/KTAP runner and assertion library for networking tests.

## Important APIs and Types
Exception types `KsftFailEx`, `KsftSkipEx`, `KsftXfailEx`, and `KsftTerminate` encode test outcomes. Assertion helpers include `ksft_eq`, `ksft_ne`, `ksft_true`, `ksft_not_none`, `ksft_in`, `ksft_not_in`, `ksft_is`, `ksft_ge`, `ksft_gt`, `ksft_lt`, and context manager `ksft_raises`. `ksft_busy_wait` polls a condition. `ktap_result` emits one KTAP result line. `ksft_disruptive` skips tests when `DISRUPTIVE` disables disruptive cases. `ksft_variants` and `KsftNamedVariant` generate parameterized cases. `ksft_setup`, `ksft_run`, `ksft_flush_defer`, and `ksft_exit` manage execution.

## Control Flow and State
`ksft_run` parses `-h`, `-l`, `-t`, and `-T`, generates case tuples from explicit cases or globals/prefix discovery, emits `TAP version 13` and the plan, then runs each case with deferred cleanup armed. Failures set global `KSFT_RESULT`; aggregate status is held in `KSFT_RESULT_ALL`. `SIGTERM` is trapped to allow cleanup on runner timeouts. Deferred cleanup uses `utils.GLOBAL_DEFER_QUEUE`, flushed after every case.

## Dependencies and Integration
It depends on standard Python modules plus sibling `utils`. Tests such as `link_netns.py` call `ksft_run([...])` and `ksft_exit()`. The command-line filters mirror common kselftest needs for listing and selecting cases.

## Risks and Test Signals
`KSFT_RESULT` prevents multiple `ksft_run()` invocations in one process. Assertions mark failure but do not raise, so tests continue unless they raise explicitly. Deferred cleanup exceptions convert a test to failure. Pass/fail signals are KTAP lines and the final totals line; process exit is controlled by `ksft_exit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/ksft.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/netns.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/netns.py

## Purpose
This module provides Python context managers for creating network namespaces and temporarily entering an existing namespace.

## Important APIs and Types
`NetNS(name=None)` creates a named or random namespace through `ip netns add`, deletes it in `__del__`/context exit, and stringifies to the namespace name. `NetNSEnter(ns_name)` opens `/run/netns/<name>`, saves `/proc/thread-self/ns/net`, calls `setns` via libc on entry, and restores the saved namespace on exit.

## Control Flow and State
`NetNS` persists kernel namespace state until explicit context exit or object destruction. `NetNSEnter` changes the calling thread's network namespace for the duration of the `with` block and stores the saved namespace file object in `self.saved`.

## Dependencies and Integration
It depends on `ip` from `utils.py`, `ctypes` loading `libc.so.6`, `/run/netns`, and Linux `setns`. Python tests use it to build isolated topologies and to instantiate netlink sockets inside a namespace.

## Risks and Test Signals
Destructor-based cleanup is not deterministic if references survive, so context-manager use is preferred. `setns` affects only the current thread and can be dangerous in multi-threaded tests. Missing privileges or namespace paths cause immediate exceptions from `ip` or libc calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/netns.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/nsim.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/nsim.py

## Purpose
This module wraps Linux `netdevsim` devices and ports for Python networking selftests.

## Important APIs and Types
`NetdevSimDev` represents a bus device. It can `ctrl_write` under `/sys/bus/netdevsim`, `dfs_write` under debugfs, create a random-address device with port and queue counts, reload it into a namespace, collect ifnames, wait for port netdevices, remove the device, and remove individual ports. `NetdevSim` represents one port, verifies udev-provided names against port index when applicable, reads detailed JSON link state, records `ifindex`, and writes per-port debugfs attributes.

## Control Flow and State
Construction loads `netdevsim` if needed, writes `new_device`, waits for the expected netdevices, optionally moves the devlink device to a namespace, settles udev, and creates `NetdevSim` port objects. Kernel state persists until `remove()` or context exit writes `del_device`. Object state records bus address, debugfs directories, namespace, port list, and removal status.

## Dependencies and Integration
It depends on `/sys/bus/netdevsim`, `/sys/kernel/debug/netdevsim`, `modprobe`, `devlink`, `udevadm`, `ip -d -j`, and helpers from `utils.py`. It integrates with tests needing synthetic NICs and debugfs-controllable behavior.

## Risks and Test Signals
Random address selection handles `ENOSPC` collisions but still assumes sysfs/debugfs availability and mounted debugfs. `wait_for_netdevs` busy-waits for up to five seconds without sleep, which may be CPU-heavy. A successful signal is a populated `nsims` list with JSON link metadata and valid ifindexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/nsim.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/utils.py -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/utils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/ynl.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/ynl.py

## Purpose
This module bridges network selftests to the kernel YNL Python library and pre-binds common netlink family specs.

## Important APIs and Types
It imports and re-exports `YnlFamily`, `NlError`, `NlPolicy`, and `Netlink`. Wrapper classes `EthtoolFamily`, `RtnlFamily`, `RtnlAddrFamily`, `NetdevFamily`, `NetshaperFamily`, `NlctrlFamily`, `DevlinkFamily`, and `PSPFamily` call `YnlFamily` with the matching YAML spec and disabled schema validation for speed.

## Control Flow and State
At import time it decides between installed selftests and in-tree source layout by checking for `kselftest-list.txt`. It appends the chosen tools path to `sys.path`, imports the YNL library, sets `SPEC_PATH`, or emits a KTAP skip and exits with code 4 if import fails. Wrapper instantiation opens family access based on YAML specs.

## Dependencies and Integration
It depends on `consts.py`, `ksft.py`, kernel `tools/net/ynl` Python modules, and YAML specs under either installed `net/lib/specs` or in-tree `Documentation/netlink/specs`. `link_netns.py` uses `RtnlFamily` for notification checking.

## Risks and Test Signals
Import-time exit means missing YNL support skips the whole test process. The path heuristic assumes either installed selftests or kernel source layout. Successful operation is indicated by wrapper construction and valid YNL request/notification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/ynl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/sh/defer.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/sh/defer.sh

## Purpose
This Bash helper implements scoped deferred cleanup for shell networking selftests, similar to stack-based `defer` semantics.

## Important APIs and Functions
Public functions are `defer_scope_push`, `defer_scope_pop`, `defer`, `defer_prio`, `defer_scopes_cleanup`, and `in_defer_scope`. Internal functions build associative-array keys, schedule quoted commands, run deferred commands, and wipe scope counters. Priority defers run before default defers, and both tracks run in LIFO order.

## Control Flow and State
State is held in associative arrays `__DEFER__JOBS` and `__DEFER__NJOBS`, keyed by scope id and track, plus `__DEFER__SCOPE_ID`. `in_defer_scope` pushes a scope, runs a command, pops and executes cleanup, then returns the command status. `DEFER_PAUSE_ON_FAIL=yes` optionally pauses after failed cleanup commands.

## Dependencies and Integration
It requires Bash associative arrays and `${@@Q}` quoting support. `lib.sh` sources it and uses it in `tests_run` and `adf_*` cleanup wrappers.

## Risks and Test Signals
Deferred commands are executed with `eval`, so callers must pass trusted command components. `defer_scopes_cleanup` loops down through scope `0`, so misuse of the global scope can trigger broad cleanup. Failed cleanup commands do not automatically fail the original scope unless callers inspect side effects; the optional pause aids debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/sh/defer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_dummy.bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_dummy.bpf.c

## Purpose
This is a minimal XDP BPF object used when tests need an attachable XDP program without changing packet behavior.

## Important APIs and Functions
It defines `xdp_dummy_prog` in section `xdp` and `xdp_dummy_prog_frags` in section `xdp.frags`. Both return `XDP_PASS`. `_license` declares GPL licensing.

## Control Flow and State
There is no map state and no branching; every packet is passed unchanged in both linear and frags-capable XDP modes.

## Dependencies and Integration
It depends on BPF helper headers and is built by `lib/Makefile`/`bpf.mk`. Tests can attach it to exercise XDP attach paths or feature negotiation without packet drops or redirects.

## Risks and Test Signals
The only realistic failures are BPF compile/load/attach failures or unsupported `xdp.frags`. Runtime pass signal is unchanged traffic through an attached XDP hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_dummy.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_helper.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_helper.c

## Purpose
`xdp_helper.c` is a userspace AF_XDP socket binder used by queue/XSK tests to verify kernel XDP socket state and optional zerocopy support.

## Important APIs and Functions
`main` accepts `ifindex queue_id [-z]`. It creates an `AF_XDP` socket, supports probe mode with `- -`, allocates UMEM with `mmap`, registers UMEM and fill/completion/RX rings through `setsockopt`, then binds `sockaddr_xdp` to the requested interface queue. `print_usage` documents syntax. It uses `ksft_ready` and `ksft_wait` for parent-controlled lifetime.

## Control Flow and State
After setup, `bind` is retried up to three times on `EBUSY`. In normal mode, successful bind reports readiness and blocks until the parent writes the wait byte. Runtime state is the AF_XDP socket, UMEM mapping, and ring configuration; no files are persisted.

## Dependencies and Integration
It depends on Linux AF_XDP, `linux/if_xdp.h`, `ksft.h`, and root/capabilities. Python background helpers can start it with readiness waits. Queue tests inspect kernel-visible XSK association while this process keeps the socket open.

## Risks and Test Signals
If the kernel lacks AF_XDP, socket creation returns `EAFNOSUPPORT` and the program exits `-1` to signal unsupported rather than generic failure. Most setup `setsockopt` calls are not checked, so failures may surface only at bind. Success signals are `AF_XDP support detected` in probe mode or a `ready\n` handshake after bind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_metadata.bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_metadata.bpf.c

## Purpose
This XDP BPF program tests receive metadata support by reading the hardware/kernel RSS hash and hash type for selected packets.

## Important APIs and Maps
`map_xdp_setup` is an array map keyed by `XDP_PORT` and `XDP_PROTO` to filter destination port and L4 protocol. `map_rss` stores `RSS_KEY_HASH`, `RSS_KEY_TYPE`, packet count, and error count. `xdp_rss_hash` parses Ethernet, IPv4/IPv6, and TCP/UDP headers; `get_dest_port` safely extracts TCP/UDP destination ports. The program calls kfunc `bpf_xdp_metadata_rx_hash`.

## Control Flow and State
On each packet, the program validates header bounds, applies optional protocol and port filters from `map_xdp_setup`, calls `bpf_xdp_metadata_rx_hash`, increments error count on failure, or updates hash/type and increments packet count on success. It always returns `XDP_PASS`.

## Dependencies and Integration
It depends on XDP metadata kfunc availability, BPF map support, libbpf section loading, and userspace configuration through bpftool or `lib/py/bpf.py`. It is built as a BPF object by the helper Makefile.

## Risks and Test Signals
Unsupported metadata kfuncs or drivers without RX hash support increment error count or fail load depending on kernel support. The parser does not walk IPv6 extension headers. Test signals are `map_rss` packet count/error count and observed hash/type values while traffic continues to pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_metadata.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_native.bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_native.bpf.c

## Purpose
This BPF object provides configurable native XDP behavior for selftests: pass, drop, transmit back, adjust tail, and adjust head for selected UDP traffic over IPv4 or IPv6.

## Important APIs and Maps
`map_xdp_setup` configures mode, UDP port, adjustment offset, and fill tag. `map_xdp_stats` counts RX, pass, drop, TX, and abort events. `xdp_prog` and `xdp_prog_frags` call `xdp_prog_common`. Major helpers include `filter_udphdr`, `record_stats`, `xdp_mode_pass`, `xdp_mode_drop_handler`, `xdp_mode_tx_handler`, `update_pkt`, `xdp_adjst_tail`, `xdp_adjst_tail_shrnk_data`, `xdp_adjst_tail_grow_data`, `xdp_head_adjst`, `xdp_adjst_head_shrnk_data`, and `xdp_adjst_head_grow_data`.

## Control Flow and State
For each packet, `xdp_prog_common` reads mode and port from `map_xdp_setup`. Pass/drop modes only count matching UDP packets. TX mode swaps MAC and IP addresses and returns `XDP_TX`. Tail/head adjustment modes update IP/UDP lengths, adjust checksums, add or remove bytes, and either pass or abort on validation/helper failure. State is held in BPF maps and packet mutations; no userspace files are written.

## Dependencies and Integration
It depends on XDP helpers and kfuncs such as weak `bpf_xdp_pull_data`, `bpf_xdp_get_buff_len`, `bpf_xdp_load_bytes`, `bpf_xdp_store_bytes`, `bpf_xdp_adjust_tail`, `bpf_xdp_adjust_head`, `bpf_csum_diff`, and atomic map increments. Userspace tests configure maps and inspect stats via bpftool.

## Risks and Test Signals
Packet mutation is bounds-sensitive and supports only UDP directly under IPv4/IPv6. IPv4 header checksum updates are incomplete for some adjustment paths compared with UDP checksum handling, so tests must know expected behavior. Invalid adjustment sizes cause `XDP_ABORTED` and increment abort stats. Pass signals are expected map counters, reflected packets for TX mode, and payload/tag/length changes observed by test traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_native.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/link_netns.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/link_netns.py

## Purpose
This Python selftest validates `link-netnsid` behavior for link creation, peer-link creation, and rtnetlink notification suppression across network namespaces.

## Important APIs and Functions
`test_event` subscribes to rtnetlink link notifications in one namespace and verifies no unexpected notification is queued after creating/deleting links that reference another namespace. `validate_link_netns` reads `ip -d -j link show` and compares `link_netnsid`. `test_link_net` covers single-device link types including ipvlan, macsec, macvlan, macvtap, vlan, GRE/VTI/IPIP/IP6 tunnel types, sit, and xfrm. `test_peer_net` covers peer devices `vxcan`, `netkit`, and `veth`. `main` runs the three cases through `ksft_run`.

## Control Flow and State
Each test builds temporary namespaces with `NetNS`, assigns namespace IDs with `ip netns set`, creates links with combinations of `netns`, `link-netns`, and peer `netns`, validates the resulting JSON field, then deletes created links. State is transient kernel namespace/link state scoped to context managers.

## Dependencies and Integration
It depends on `lib.py` helpers, YNL rtnetlink support, `iproute2`, and kernel support for the listed link types. It uses `RtnlFamily.ntf_subscribe` and `check_ntf` to inspect async netlink messages.

## Risks and Test Signals
Some link types may be unavailable as modules or kernel config. Tunnel types marked as fallback expect dev-net behavior rather than link-netns behavior. Pass signals are KTAP `ok` lines; failures come from missing/incorrect `link_netnsid` values or unexpected rtnetlink notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/link_netns.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lwt_dst_cache_ref_loop.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lwt_dst_cache_ref_loop.sh

## Purpose
This shell test exercises lightweight tunnel encapsulation cases that historically could create dst-cache reference loops in lwtunnel input/output/xmit paths. It is explicitly a trigger script: kmemleak or kernel stability observation is needed to detect the bug.

## Important APIs and Functions
`check_compatibility` creates a temporary namespace, veth pair, loads `ila` if needed, attempts route encap setup for ILA, IOAM6, RPL, and SEG6, and records skip flags. `setup` creates three namespaces (`alpha`, `beta`, `gamma`) connected by two veth pairs with IPv6 forwarding through beta. `run_ila`, `run_ioam6`, `run_rpl`, and `run_seg6` install relevant encap routes and run ping6 traffic. `cleanup` removes namespaces and unloads `ila` if it was loaded by the script.

## Control Flow and State
The script requires root and `ip`, runs compatibility checks, installs an EXIT cleanup trap, builds the topology, confirms baseline ping reachability, then runs each encap case. It mutates namespace, route, sysctl, and module state; cleanup reverses namespace and optional module state but not global kmemleak state.

## Dependencies and Integration
It sources `lib.sh` for namespace helpers and kselftest exit codes. It depends on IPv6, veth, route encap support for ILA/IOAM6/RPL/SEG6, `modprobe`, and optional `kmemleak` monitoring outside the script.

## Risks and Test Signals
The script warns it may crash kernels lacking the loop-prevention fix. Its exit status is blindly pass after traffic attempts; absence of user-visible failure is not proof. Meaningful signals are kernel stability and external kmemleak results, while unsupported encap types print `SKIP:` lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/lwt_dst_cache_ref_loop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/macvlan_mcast_shared_mac.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/macvlan_mcast_shared_mac.sh

## Purpose
This shell selftest verifies multicast delivery to a macvlan bridge port when the source MAC equals the macvlan's own MAC, modeling shared virtual MAC cases such as VRRP.

## Important APIs and Functions
`setup` creates source and bridge namespaces, a veth pair, assigns `SHARED_MAC` to the source veth and macvlan, configures IPv4 addresses, creates `macvlan0` in bridge mode, and enables all-multicast. `test_macvlan_mcast_shared_mac` starts tcpdump on `macvlan0`, waits for listening, sends multicast pings from the source namespace, and counts captured ICMP packets. `cleanup` removes capture files and namespaces.

## Control Flow and State
The script sources `lib.sh`, sets a cleanup trap, builds the topology, runs one test, logs it through `log_test`, and exits with accumulated `EXIT_STATUS`. State consists of temporary namespaces, veth/macvlan links, IP addresses, and temporary capture files.

## Dependencies and Integration
It depends on root, `ip`, `ping`, `tcpdump`, macvlan bridge mode, multicast delivery, and `lib.sh` result helpers.

## Risks and Test Signals
Tcpdump startup is timing-sensitive and guarded by `slowwait` on its output. Multicast filtering or lack of all-multicast support can cause false failures. The pass signal is at least one ICMP packet in the capture and a kselftest OK result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/macvlan_mcast_shared_mac.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/Makefile

## Purpose
This Makefile builds and installs the MPTCP selftest suite programs and scripts.

## Important Targets and Variables
`CFLAGS` includes kernel UAPI and tools headers. `TEST_PROGS` lists shell tests such as `diag.sh`, `mptcp_connect.sh`, checksum/mmap/sendfile/splice wrappers, join, sockopt, path-manager, simultaneous-flow, and userspace PM tests. `TEST_GEN_FILES` builds `mptcp_connect`, `mptcp_diag`, `mptcp_inq`, `mptcp_sockopt`, and `pm_nl_ctl`. `TEST_FILES` installs `mptcp_lib.sh` and `settings`. `TEST_INCLUDES` includes shared net shell helpers. `EXTRA_CLEAN` removes packet captures.

## Control Flow and State
The Makefile delegates build and install behavior to `../../lib.mk`. Generated state is the compiled helper binaries and installed scripts/files.

## Dependencies and Integration
It depends on the kselftest framework, GCC/clang, kernel headers, and the wider MPTCP shell library. The wrapper scripts in this subset rely on `mptcp_connect.sh` and the generated `mptcp_connect` binary.

## Risks and Test Signals
Header mismatch can break compilation of newer MPTCP structs/options. Successful build produces all `TEST_GEN_FILES`; runtime suite signals are produced by the individual shell tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/config

## Purpose
This file declares kernel configuration requirements for the MPTCP selftest suite.

## Important Entries
It requires core MPTCP (`CONFIG_MPTCP`, `CONFIG_MPTCP_IPV6`), diagnostic modules (`CONFIG_INET_DIAG`, `CONFIG_INET_MPTCP_DIAG`), IPv6 and advanced routing, multiple routing tables, veth, netfilter/nftables/xtables support, BPF match, netem/ingress qdisc, pedit/csum actions, syncookies, and kallsyms.

## Control Flow and State
There is no executable control flow. The selftest framework uses these symbols to document or validate required kernel features.

## Dependencies and Integration
It supports scripts such as `mptcp_connect.sh`, `diag.sh`, and related MPTCP tests that need namespaces, routing, netfilter, tc, and MPTCP diagnostics.

## Risks and Test Signals
Missing symbols usually cause runtime skips or failures rather than direct config-file execution errors. The config is broad because the MPTCP suite tests transport, path manager, diagnostics, filtering, and failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/diag.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/diag.sh

## Purpose
This shell selftest validates MPTCP diagnostic visibility and counters through `ss`, `/proc/net/protocols`, MPTCP nstat counters, and the compiled `mptcp_diag` helper.

## Important APIs and Functions
It uses `mptcp_lib_check_mptcp`, `mptcp_lib_check_tools`, `mptcp_lib_ns_init`, `mptcp_lib_result_*`, and `mptcp_connect`. Local helpers include `flush_pids`, `cleanup`, `get_msk_inuse`, `__chk_nr`, `chk_msk_nr`, `chk_listener_nr`, `wait_msk_nr`, `chk_msk_fallback_nr`, `chk_msk_remote_key_nr`, `chk_msk_listen`, `chk_msk_inuse`, `chk_msk_cestab`, `chk_dump_one`, `chk_dump_subflow`, `chk_msk_info`, `chk_last_time_info`, `wait_connected`, and `chk_sndbuf`.

## Control Flow and State
The script creates one namespace, starts MPTCP listener/client pairs on loopback, validates listener filters and post-handshake socket counts, checks send-buffer parity and last activity timestamps, verifies remote keys and fallback state, compares `mptcp_diag` output with `ss`, kills processes, and repeats with TCP fallback and many-client/listener scenarios. State is namespace-scoped sockets/processes and counters, cleaned by trap.

## Dependencies and Integration
It depends on `mptcp_lib.sh`, `ip`, `ss`, `mptcp_connect`, `mptcp_diag`, MPTCP diag kernel support, and loopback namespace networking. It integrates with the MPTCP Makefile as a `TEST_PROGS` entry.

## Risks and Test Signals
Timing and process cleanup are important; `flush_pids` uses SIGUSR1 then waits before SIGKILL cleanup. Feature gaps may be skipped if the suite is not requiring all features. Pass/fail signals are accumulated TAP results from `mptcp_lib_result_print_all_tap`; failures include mismatched socket counts, missing tokens, missing fallback, stale in-use counters, or mismatched diag output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/diag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect.c

## Purpose
`mptcp_connect.c` is the core userspace data-transfer helper for MPTCP selftests. It can act as client or server, use MPTCP or TCP sockets, and exercise multiple I/O paths, socket options, control messages, truncation/reset behavior, repeated disconnect/reconnect, and MPTCP fast open.

## Important APIs and Functions
Option parsing is handled by `parse_opts`, `parse_proto`, `parse_mode`, `parse_peek`, `parse_cmsg_types`, and `parse_setsock_options`. Socket setup uses `sock_listen_mptcp`, `sock_connect_mptcp`, `set_rcvbuf`, `set_sndbuf`, `set_mark`, `set_transparent`, `set_mptfo`, and `sock_test_tcpulp`. Data paths include `copyfd_io_poll`, `copyfd_io_mmap`, `copyfd_io_sendfile`, `copyfd_io_splice`, `do_rnd_write`, `do_rnd_read`, `do_recvmsg_cmsg`, `process_cmsg`, `do_mmap`, `do_sendfile`, and `do_splice`. Connection loops are `main_loop_s` for listeners and `main_loop` for clients; `xdisconnect` tests reconnect on an existing socket.

## Control Flow and State
`main` seeds RNG, installs a SIGUSR1 handler to set `quit`, parses options, then either listens and accepts one or more connections or connects to a peer. In poll mode, it interleaves reads and writes with nonblocking `poll`, optional random write/read chunking, truncation limits, and shutdown when input EOF is reached. In mmap/sendfile/splice modes, regular input files are transferred through the selected zero/copy path before reading the reply. Global `cfg_*` variables drive behavior; `wstate` tracks pre-read or MPTFO data still needing transmission.

## Dependencies and Integration
It depends on Linux MPTCP protocol number 262, TCP ULP behavior, socket options such as `SO_MARK`, `SO_RCVBUF`, `SO_SNDBUF`, `TCP_FASTOPEN`, `TCP_INQ`, `SO_TIMESTAMPNS_NEW`, `IP_TRANSPARENT`, and `IPV6_TRANSPARENT`, plus system calls `poll`, `mmap`, `sendfile`, `splice`, `shutdown`, and reconnect-by-`AF_UNSPEC`. It is orchestrated by `mptcp_connect.sh`, `diag.sh`, and wrapper scripts.

## Risks and Test Signals
Many code paths are intentionally sensitive to kernel semantics. Cmsg validation expects timestamp and TCP_INQ ancillary data when requested. Negative truncation tolerates reset/EPIPE to test fastclose. MPTFO preloads data into `wstate` and requires careful spool handling. Pass signals are zero exit status, matching stdout file contents in shell harnesses, and optional runtime output within `cfg_time`; failures print detailed syscall or validation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect.sh

## Purpose
This shell test builds a four-namespace routed topology and uses `mptcp_connect` to validate MPTCP transfers over loopback, multi-hop IPv4/IPv6 paths, TCP fallback combinations, checksum mode, peek mode, MPTFO, transparent proxying, and full disconnect/reconnect.

## Important APIs and Functions
Setup code creates namespaces `ns1` to `ns4`, veth links, IPv4/IPv6 addresses, forwarding, optional checksum sysctls, random or requested ethtool feature changes, and netem loss/delay/reorder. Helpers include `cleanup`, `set_ethtool_flags`, `set_random_ethtool_flags`, `check_mptcp_disabled`, `do_ping`, `do_transfer`, `make_file`, `run_tests_lo`, `run_tests`, `run_test_transparent`, `run_tests_peekmode`, `run_tests_mptfo`, `run_tests_disconnect`, `display_time`, `log_if_error`, and `stop_if_error`.

## Control Flow and State
The script parses options for delay/loss/reorder, capture, file size, buffer sizes, transfer mode, TCP coverage, IPv4-only mode, and MPTCP checksums. It validates MPTCP can be disabled by sysctl, pings all namespace addresses, installs tc qdiscs, then runs transfer matrices. `do_transfer` starts a listener and connector, applies timeouts, optionally starts tcpdump, captures nstat counters before/after, compares transferred files both directions, and validates MPTCP counters such as MPCapable SYN/ACK, fallback, checksum errors, syncookie counters, and OoO notes.

## Dependencies and Integration
It depends on `mptcp_lib.sh`, `mptcp_connect`, `ip`, `tc`, `ethtool`, `nft` for transparent proxy cases, `tcpdump` when capture is enabled, `dd`, `/dev/urandom`, kernel MPTCP counters, and namespace/routing support. Wrapper scripts in this subset call it with `-C`, `-m mmap`, `-m sendfile`, or `-m splice`.

## Risks and Test Signals
The test intentionally randomizes file size, netem, and offload toggles unless fixed by options, which improves coverage but can affect reproducibility. Packet capture creates `.pcap` files when enabled. Transparent proxy and MPTFO cases are skipped if kernel support is absent. Pass signals are per-transfer TAP results, bidirectional file equality, expected MPTCP counter deltas, no checksum errors, and final zero `final_ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_checksum.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_checksum.sh

## Purpose
This wrapper runs the standard MPTCP connect transfer suite with MPTCP data checksums enabled.

## Important APIs and Functions
It sets `MPTCP_LIB_KSFT_TEST` to the wrapper basename and execs `mptcp_connect.sh -C "$@"`.

## Control Flow and State
All substantive setup, transfer, and validation happens in `mptcp_connect.sh`; this file only selects checksum mode and forwards user arguments.

## Dependencies and Integration
It depends on the sibling `mptcp_connect.sh` script and `mptcp_lib.sh` conventions for naming KTAP tests.

## Risks and Test Signals
Risks are inherited from `mptcp_connect.sh`, with added dependence on `net.mptcp.checksum_enabled` support. Pass/fail is the delegated script's exit status and TAP output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_checksum.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_mmap.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_mmap.sh

## Purpose
This wrapper runs the MPTCP connect transfer suite using the `mmap` send path in `mptcp_connect`.

## Important APIs and Functions
It sets `MPTCP_LIB_KSFT_TEST` to its basename and invokes `mptcp_connect.sh -m mmap "$@"`.

## Control Flow and State
The wrapper has no internal test logic. It selects mmap mode, where `mptcp_connect.c` memory maps a regular input file and writes it to the socket, while `mptcp_connect.sh` handles topology and validation.

## Dependencies and Integration
It depends on `mptcp_connect.sh`, a regular generated input file, and kernel/userspace support for `mmap`.

## Risks and Test Signals
Failures usually indicate delegated transfer mismatch or mmap/write path errors in the helper. TAP naming is adjusted by `MPTCP_LIB_KSFT_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_mmap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_sendfile.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_sendfile.sh

## Purpose
This wrapper runs the MPTCP connect transfer suite using the `sendfile` data path.

## Important APIs and Functions
It sets `MPTCP_LIB_KSFT_TEST` and invokes `mptcp_connect.sh -m sendfile "$@"`.

## Control Flow and State
All test state is owned by the delegated script. The selected mode causes `mptcp_connect.c` to transfer regular-file input with `sendfile`.

## Dependencies and Integration
It depends on `mptcp_connect.sh`, `mptcp_connect`, and kernel support for `sendfile` from regular files to TCP/MPTCP sockets.

## Risks and Test Signals
Risks are inherited from the main transfer matrix plus sendfile-specific syscall behavior. Success is delegated TAP pass and matching received files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_sendfile.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_splice.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_splice.sh

## Purpose
This wrapper runs the MPTCP connect transfer suite using the `splice` data path.

## Important APIs and Functions
It sets `MPTCP_LIB_KSFT_TEST` and invokes `mptcp_connect.sh -m splice "$@"`.

## Control Flow and State
The wrapper delegates all setup and validation. The selected mode causes `mptcp_connect.c` to move bytes through a pipe with `splice`.

## Dependencies and Integration
It depends on `mptcp_connect.sh`, `mptcp_connect`, regular input files, pipes, and kernel splice support for the involved descriptors.

## Risks and Test Signals
Splice mode can expose kernel/socket path differences from read/write or sendfile. Success is delegated zero exit status, TAP pass, and file equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect_splice.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_diag.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_diag.c

## Purpose
`mptcp_diag.c` is a diagnostic helper that queries Linux sock_diag netlink for MPTCP socket information by token or TCP subflow tuple and prints selected MPTCP info/subflow attributes.

## Important APIs and Functions
`parse_opts` accepts `-t <token>` and `-s "<saddr>:<sport> <daddr>:<dport>"`. `get_mptcpinfo` builds an `inet_diag_req_v2` for an MPTCP token, requesting `INET_DIAG_INFO` and passing `INET_DIAG_REQ_PROTOCOL=IPPROTO_MPTCP`. `get_subflow_info` parses an IPv4 TCP tuple and requests TCP diag/ULP info. Netlink helpers include `send_query`, `recv_nlmsg`, `parse_rtattr_flags`, `parse_nlmsg`, `print_info_msg`, and `print_subflow_info`.

## Control Flow and State
The program opens a `NETLINK_SOCK_DIAG` socket, sends one query for each requested mode, receives netlink responses, parses rtattrs, and prints human-readable fields. For older kernels with shorter `mptcp_info`, `parse_nlmsg` copies payload into a zero-filled full struct. State is process-local query parameters and receive buffers.

## Dependencies and Integration
It depends on Linux inet_diag/sock_diag UAPI, MPTCP diag kernel support, and IPv4 tuple parsing for subflow mode. `diag.sh` compares its token and subflow output against `ss`.

## Risks and Test Signals
Subflow mode only parses IPv4-style `addr:port` pairs with `sscanf`, so IPv6 subflows are outside this helper's current path. Netlink errors are printed but not deeply classified. Useful signals are printed `token:`, flags, checksum, sequence/counter fields, and subflow `token:` data matching `ss`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_diag.c -->
