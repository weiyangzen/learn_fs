# Research: subset-b-006859

Grouped research for the exact source files assigned to `subset-b-006859`. Each section is source-tree-aligned and wrapped for deterministic reconciliation into the mapped per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_nexthops.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_nexthops.sh

## Purpose
`fib_nexthops.sh` is a Linux kselftest shell suite for the standalone nexthop object API and its interaction with IPv4 and IPv6 FIB routes. It creates three network namespaces (`me`, `peer`, `remote`) connected by multiple veth pairs, then exercises ordinary nexthops, nexthop groups, resilient nexthop groups, FDB nexthop groups, compatibility mode notifications, route attachment, live traffic, and stress loops. The opening topology models two parallel links from `me` to `peer` and a remote host network behind `peer`, allowing route resolution, multipath selection, and ping-based runtime validation.

## Important APIs, Functions, and Types
The script sources `lib.sh` for namespace helpers such as `setup_ns` and uses `ip`, `bridge`, `sysctl`, `ping`, `ip6tables`, `jq`, `mausezahn`, and shell built-ins. Core harness functions are `log_test()`, `run_cmd()`, `setup()`, `cleanup()`, `check_output()`, `check_nexthop()`, `check_nexthop_bucket()`, `check_route()`, and `check_route6()`. `get_linklocal()` extracts IPv6 link-local addresses from `ip -6 -br addr`. Feature checks include `check_nexthop_fdb_support()` and `check_nexthop_res_support()`.

Functional test entry points are split by family and feature: `basic()`, `basic_res()`, `ipv4_fcnal()`, `ipv6_fcnal()`, `ipv4_grp_fcnal()`, `ipv6_grp_fcnal()`, `ipv4_res_grp_fcnal()`, `ipv6_res_grp_fcnal()`, `ipv4_withv6_fcnal()`, `ipv4_fcnal_runtime()`, `ipv6_fcnal_runtime()`, FDB group tests, large group tests, multipath selection tests, compatibility-mode tests, and torture tests.

## Control Flow
Command-line flags select `TESTS` (`-t`, `-4`, `-6`) and behavior (`-p`, `-P`, `-v`, `-w`). Main validates root, `ip`, iproute2 nexthop support, and kernel nexthop support. For each selected test it calls `setup`, invokes the test function by name, and calls `cleanup`. Most tests create nexthops or routes, compare `ip` output against exact strings, then delete or flush state before proceeding.

The IPv4 and IPv6 paths are intentionally parallel but not identical. IPv6 includes route restrictions around IPv4 gateways, rpfilter default-route coverage, per-CPU dst reference regression checks, and IPv6 route output formatting. IPv4 includes IPv6 nexthop support, MPLS encap nexthops, default route selection, and IPv4-specific route deletion semantics. Resilient group tests validate bucket creation, bucket migration after member deletion or replacement, idle/unbalanced timer rendering, 16-bit weights, and large bucket dumps.

## State and Persistence
All networking state is transient and lives inside test namespaces. The script changes per-namespace sysctls for forwarding, multipath neighbor selection, link-down route ignoring, DAD behavior, and nexthop compatibility mode. Runtime scratch state includes monitor tempfiles in `/var/run`, a large temporary iproute batch file, counters (`nsuccess`, `nfail`, `nskip`, `ret`), and background process IDs during torture tests. Cleanup deletes namespaces and therefore should remove interfaces, routes, nexthops, neighbors, VXLAN devices, and iptables state created inside the namespace.

## Dependencies and Integration Points
The file integrates with the kselftest networking framework and `tools/testing/selftests/net/lib.sh`. It depends on a privileged kernel environment with network namespaces, veth, dummy/bridge/VXLAN/MPLS support for selected tests, modern iproute2 nexthop syntax, and optional `jq` and `mausezahn`. It returns kselftest skip code `4` when prerequisites are missing. The test is launched by the selftests make/kselftest harness but can also be run directly with `-t` to isolate a function.

## Risks
Exact string matching against `ip` output is sensitive to iproute2 formatting changes. Torture tests sleep for 300 seconds and spawn background loops, so interrupted runs can leave processes if cleanup is bypassed. Some skip paths return without logging through `log_test`, and optional dependencies make coverage environment-dependent. The script toggles `net.ipv4.nexthop_compat_mode` and expects to restore it; failure mid-test could affect subsequent tests in the namespace. FDB tests require specific bridge and VXLAN semantics and may fail on kernels lacking recent nexthop FDB features.

## Test Signals
Success is reported through `[ OK ]` lines and final pass/fail/skip totals. A substantive run covers nexthop creation/deletion/replacement, route references to `nhid`, group member updates after device down or nexthop deletion, resilient bucket dumps and migration, ping reachability through single and multipath routes, blackhole behavior, route notification line counts under compatibility mode, FDB nexthop attachment to bridge entries, neighbor-aware multipath selection, and long-running crash-free torture loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_nexthops.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_rule_tests.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_rule_tests.sh

## Purpose
`fib_rule_tests.sh` validates the IPv4 and IPv6 FIB rule API. It confirms that rule selectors redirect lookups into the expected routing table, that invalid selectors are rejected, that socket traffic observes DS Field / DSCP rules during connect and send, and that VRF master-device matching behaves as expected.

## Important APIs, Functions, and Types
The script sources `lib.sh` and uses `ip`, `nettest`, and namespace helpers. Global constants define routing tables (`RTABLE`, `RTABLE_PEER`, `RTABLE_VRF`), dummy device addresses, gateways, and source addresses. `setup()` creates `testns` with `dummy0`; `setup_peer()` adds a second namespace with veth links and loopback service addresses; `setup_vrf()` creates `vrf0`. `fib_check_iproute_support()` gates optional selectors by checking both `ip rule help` and `ip route get help`.

The helper pairs `fib_rule6_test_match_n_redirect()` / `fib_rule4_test_match_n_redirect()` add a rule, run `ip route get` with a matching selector and a nonmatching selector, and then delete the rule by preference. Reject helpers verify that DS Field values containing ECN bits are not accepted as rule keys. Connect tests use `nettest` for UDP and TCP in isolated namespaces.

## Control Flow
Main parses `-t`, verifies root and `ip`, checks that `nettest` is generated, runs `cleanup`, then `setup`, and dispatches selected tests. The default `TESTS` cover plain IPv6, plain IPv4, IPv6 connect, IPv4 connect, IPv6 VRF, and IPv4 VRF. Each rule test first installs a default route in a non-main table, then adds selectors such as `oif`, `iif`, `tos`/`dsfield`, `fwmark`, `uidrange`, `sport`, `dport`, `ipproto`, `dscp`, and IPv6 `flowlabel`. VRF variants call the same selector matrix after enslaving `dummy0` to `vrf0`.

Connect tests set up a peer namespace with explicit routes in `RTABLE_PEER`, install a DS Field or DSCP rule, then verify `nettest` succeeds for matching ECN variants and fails for nonmatching values. The DS Field loops intentionally combine the configured DS value with all ECN bit combinations to prove ECN is ignored in DSCP-style matching.

## State and Persistence
State is limited to network namespaces, dummy/veth devices, routes, rules, and VRF links created during the run. Rules are deleted by preference or exact expression after each check. Peer namespaces are created only for connect tests and removed by `cleanup_peer()`. No persistent files are written.

## Dependencies and Integration Points
The file is a kselftest networking script integrated through `lib.sh` and the generated `nettest` binary. It requires root, network namespaces, dummy, veth, VRF support for VRF cases, and a sufficiently new iproute2 for optional rule selectors. The script skips optional selector blocks by printing `SKIP` but continues the surrounding test matrix.

## Risks
Because rule deletion derives preference from `ip rule show`, unexpected duplicate rules or formatting changes could delete the wrong rule in a dirty namespace; the script mitigates this by creating an isolated namespace. Some optional feature checks are coarse string matches, so new iproute2 help wording could incorrectly skip or run a block. `nettest` availability is mandatory for the script as written.

## Test Signals
Important signals include successful `ip route get ... | grep "table $RTABLE"` for matches, absence of the table marker for nonmatches, return code `2` for rejected DS Field rule additions, successful `nettest` UDP/TCP connections for matching DS Field and DSCP values, failed connections for mismatches, and VRF `oif` / `iif` selectors redirecting when the physical device is enslaved to `vrf0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_rule_tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_tests.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_tests.sh

## Purpose
`fib_tests.sh` is a broad Linux FIB behavior regression suite. It validates route lifetime and lookup behavior under device unregister, admin-down, carrier-down, suppress rules, nexthop validation, route add/replace semantics, netlink notifications, IPv6 garbage collection, route metrics, address-derived prefix route metrics, preferred source cleanup, IPv4 routes with IPv6 gateways, route mangling interactions, broadcast neighbor lookups, multipath receive-list behavior, multipath load balancing, and IPv6 RA-to-static route promotion.

## Important APIs, Functions, and Types
The script sources `lib.sh` and uses `ip`, `ping`, `ping6`, `tc`, `iptables`, `ip6tables`, `socat`, `mausezahn`, `jq`, `bc`, `perf`, and optional `ra6` / `rd6`. Harness functions include `log_test()`, `setup()`, `cleanup()`, `run_cmd()`, `check_expected()`, `check_route()`, and `check_route6()`. Route setup helpers (`route_setup()`, `forwarding_setup()`, `add_route()`, `add_route6()`) build reusable two- and three-namespace topologies. Feature probes include `ip_addr_metric_check()`, `socat_check()`, `iptables_check()`, `ip6tables_check()`, `ip_neigh_get_check()`, and `mpath_dep_check()`.

## Control Flow
Main installs `trap cleanup EXIT`, parses `-t`, `-p`, `-P`, and `-v`, checks root, `ip`, and `fibmatch` support, then dispatches symbolic test names from `TESTS`. Many tests call `setup()` or `route_setup()` internally and cleanup at the end. The first group exercises route removal or link-down marking when devices disappear or go down. Route add/replace tests use controlled veth topologies to assert exact `ip route` output after duplicate adds, appends, prepends, multipath conversion, invalid replacement attempts, metrics, and reject routes.

Later groups test source address deletion in default and VRF tables, IPv6 route garbage collection for expiring routes and redirect exceptions, RA-learned routes promoted by static addresses, route notification size with encapsulated multipath nexthops, DS Field matching without ECN sensitivity, socket traffic through sport/dport FIB rules despite mangle table marks, and multipath behavior using tracepoints or tc flower counters.

## State and Persistence
The script heavily mutates namespace-scoped state: sysctls, dummy and veth devices, VRFs, routes, neighbors, tc qdiscs/filters, iptables/ip6tables rules, and temporary service processes. It writes `errors.txt` in the current working directory during route monitor tests and uses temporary files for `socat` and `perf` output. Most state is removed through cleanup helpers, though comments note that system services such as `systemd-networkd` can interfere with RA timing.

## Dependencies and Integration Points
This file is integrated with kselftest and `lib.sh`. It depends on a privileged kernel with namespaces, dummy, veth, VRF, bridge-related tc helpers from the library, FIB tracepoints, and recent iproute2 `fibmatch`. Optional subtests require `socat`, `iptables`, `ip6tables`, `ip neigh get`, `mausezahn`, `jq`, `bc`, `perf`, and `ipv6toolkit` tools (`ra6`, `rd6`). It exercises kernel datapath behavior directly rather than mocking route tables.

## Risks
The suite is sensitive to exact `ip` output, kernel timing, and optional user-space tools. Some subtests sleep for route expiration or RA processing and can be flaky on slow or managed systems. `fib4_nexthop()` is only a placeholder, so IPv4 nexthop validation in `fib_nexthop_test()` is currently incomplete compared with IPv6. Monitor tests write `errors.txt` in the working directory; one IPv6 notify path leaves the removal commented. Long multipath tests require perf tracepoints and offload/GRO settings that may be unavailable.

## Test Signals
Signals include expected return codes from `ip route get fibmatch`, absence or presence of `dead linkdown`, exact route dump strings after add/replace, successful or failed pings through selected routes, netlink monitor output not containing `Message too long`, zero `expires` routes after GC, correct prefix-route metric ordering, correct removal of routes or preferred sources when addresses disappear, DSCP route matching independent of ECN bits, successful UDP traffic under matching FIB rules, and multipath counters showing both legs used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fin_ack_lat.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fin_ack_lat.c

## Purpose
`fin_ack_lat.c` is a small TCP loopback latency probe used to detect latency spikes caused by a FIN/ACK handling race. It starts a server on an ephemeral local TCP port, forks a client, and continuously performs short connect/send/read/close cycles. The client prints a line only when a round trip exceeds 100 ms; the shell wrapper treats any printed line as a failure.

## Important APIs, Functions, and Types
The program uses POSIX sockets and timing APIs: `socket`, `setsockopt`, `bind`, `listen`, `getsockname`, `fork`, `connect`, `send`, `read`, `accept`, `close`, `gettimeofday`, `signal`, and `kill`. `timediff()` converts `struct timeval` pairs to microseconds. `client()` owns the active loop and latency calculation. `server()` accepts a connection, reads one integer, and closes immediately, creating the FIN/ACK interaction under test. `sig_handler()` attempts to terminate the child when the parent receives `SIGTERM`.

## Control Flow
`main()` installs a `SIGTERM` handler, creates an IPv4 TCP socket, enables `SO_REUSEADDR | SO_REUSEPORT`, binds to `INADDR_ANY` with port zero, listens, discovers the chosen port, prints it to stderr, and forks. The child calls `client(port)`, repeatedly connecting to `127.0.0.1`, sending an integer, reading until the server close, timing the whole operation, and closing with `SO_LINGER` set to zero and `TCP_NODELAY` enabled. The parent calls `server()`, which loops accepting and closing connections after a read.

## State and Persistence
State is process-local: a global `child_pid`, socket descriptors, timing counters (`sum_lat`, `nr_lat`), and the ephemeral server port. No files are written by the C program. The parent and child run indefinitely until externally killed by the wrapper or signal handling.

## Dependencies and Integration Points
The file is compiled as a generated selftest binary and invoked by `fin_ack_lat.sh`. It assumes IPv4 loopback is available and that TCP sockets support linger and `TCP_NODELAY`. It integrates with the test by emitting spike lines to stdout and server port information to stderr.

## Risks
The signal handler calls `kill(SIGTERM, child_pid)`, which reverses the usual `kill(pid, signal)` argument order. In practice the shell wrapper kills processes by name, but this handler is suspicious and could fail to reap the child as intended. The client reads from a connection the server closes without sending data; the test relies on timing of close/error behavior rather than payload echo. There is no rate limiting in the loop, so the test can be CPU-intensive during the 30-second wrapper run.

## Test Signals
The key signal is absence of stdout lines over the wrapper runtime. Each printed line includes local port, latency in microseconds, average latency, and sample count, and represents a latency spike above 100 ms. Process exit is normally controlled by the shell wrapper rather than the program returning from `main()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fin_ack_lat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fin_ack_lat.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fin_ack_lat.sh

## Purpose
`fin_ack_lat.sh` is the kselftest wrapper for `fin_ack_lat`. It runs the generated latency probe for a fixed period and fails if the probe reports any FIN/ACK latency spike.

## Important APIs, Functions, and Types
The script is intentionally small. `cleanup()` kills processes named `fin_ack_lat` and removes the temporary log. `do_test()` starts `./fin_ack_lat`, pipes stdout through `tee` into a temporary file, sleeps for the requested runtime, counts log lines with `wc -l`, and returns failure if the count is greater than zero. It uses `mktemp`, `trap`, `pidof`, `kill`, `tee`, `wc`, and `awk`.

## Control Flow
The script enables `set -e`, creates `/tmp/fin_ack_latency.XXXX.log`, installs `trap cleanup EXIT`, and calls `do_test "30"`. The probe runs in the background while the wrapper sleeps for 30 seconds. After the sleep, the wrapper counts spike lines and prints `FAIL: N spikes detected` when any are present. If no spikes are observed, it prints `test done`.

## State and Persistence
The only persistent state during execution is the temporary log file under `/tmp`. Cleanup removes that file and attempts to kill all processes returned by `pidof fin_ack_lat`. The background PID is stored in `PID` but not used by cleanup.

## Dependencies and Integration Points
The wrapper assumes the `fin_ack_lat` binary exists in the current directory, typically built by the kselftest harness. It depends on normal POSIX shell utilities and process visibility through `pidof`. It integrates with kselftest via its exit status: zero when no spikes are logged, nonzero when `do_test` returns failure.

## Risks
`kill $(pidof fin_ack_lat)` can fail when no process exists; because cleanup runs under `set -e`, that can affect script exit behavior if the process has already exited. It also kills every matching process name, not only the PID started by this script. The wrapper only watches stdout; stderr server-port output is not counted as a failure. The 30-second runtime is a compromise and may miss rare races on quiet systems or produce environment-sensitive failures on overloaded hosts.

## Test Signals
The signal is binary: zero spike lines means pass and `test done`; one or more stdout lines from the C probe means failure with a count. A spike line contains the client local port, the single-iteration latency, the running average, and the number of samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/fin_ack_lat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/Makefile

## Purpose
The forwarding `Makefile` enumerates the shell programs, support files, generated binaries, and include dependencies that make up the networking forwarding selftests. It is declarative glue for the kselftest build/install harness rather than executable test logic.

## Important APIs, Functions, and Types
Key make variables are `TEST_PROGS`, `TEST_FILES`, `TEST_GEN_PROGS`, and `TEST_INCLUDES`. `TEST_PROGS` lists runnable forwarding scenarios, including bridge, VXLAN, GRE/IPIP, router, tc, scheduler, mirroring, and nexthop tests. `TEST_FILES` lists shared shell libraries and sample configuration files copied with the tests. `TEST_GEN_PROGS := ipmr` declares a generated helper binary. `TEST_INCLUDES` pulls shell libraries from `../lib/sh/*.sh` and `../lib.sh`. The file includes `../../lib.mk`, which supplies standard kselftest build, install, and run rules.

## Control Flow
Make processing is simple: variable lists are expanded and then interpreted by `lib.mk`. There are no custom rules in this file. The trailing comments mark the end of each variable block and help avoid accidentally appending later content to long backslash-continued lists.

## State and Persistence
The Makefile itself does not create runtime state. Through `lib.mk`, it influences build outputs for `TEST_GEN_PROGS` and install/copy behavior for scripts and libraries. Its main persistent effect is determining which test files are visible to kselftest automation.

## Dependencies and Integration Points
This file is an integration point between individual forwarding shell tests and the top-level kselftest infrastructure. The bridge files in this subset are listed in `TEST_PROGS`, while common harness files such as `lib.sh`, `devlink_lib.sh`, `tc_common.sh`, and tunnel libraries are listed in `TEST_FILES`. External dependencies are not declared here; each shell test performs its own feature checks.

## Risks
The long continuation lists are easy to break by missing a backslash or placing content after the `# end` comments. Adding a test script without listing it in `TEST_PROGS` prevents normal kselftest discovery. Removing a library from `TEST_FILES` can cause installed test trees to fail even when in-tree runs work. The Makefile does not encode per-test prerequisites, so scheduling systems must rely on scripts to skip unsupported environments.

## Test Signals
The Makefile has no direct pass/fail signals. Its correctness is reflected by kselftest being able to build generated helpers, install all required support files, and discover/run the listed forwarding scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_activity_notify.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_activity_notify.sh

## Purpose
`bridge_activity_notify.sh` tests bridge FDB `activity_notify`, `inactive`, and `norefresh` semantics. It builds a simple two-host bridge topology and verifies transitions between inactive and active FDB states, as well as whether replacing an FDB entry refreshes its `updated` timestamp.

## Important APIs, Functions, and Types
The script sources forwarding `lib.sh` and uses `adf_*` helpers, `bridge`, `ip`, `jq`, `mausezahn` via `$MZ`, `busywait`, `slowwait`, and `bridge_ageing_time_get`. `setup_prepare()` maps four physical/netns test interfaces into `h1`, `swp1`, `swp2`, and `h2`, prepares VRFs, initializes hosts, and creates `br1`. `fdb_active_wait()` and `fdb_inactive_wait()` poll `bridge -d fdb get` for the `inactive` marker.

## Control Flow
After checking that `bridge fdb help` contains `activity_notify`, the script installs cleanup, prepares the topology, waits for setup, and runs `ALL_TESTS`: `new_inactive_test`, `existing_active_test`, and `norefresh_test`. The first test adds a static inactive entry with activity notifications, injects traffic from `h1`, and waits for it to become active. The second converts an existing dynamic entry into a static activity-notify entry with `norefresh`, then waits for bridge aging to mark it inactive. The third compares JSON `updated` time after replacement with and without `norefresh`.

## State and Persistence
State is limited to `br1`, its two bridge ports, host interface addresses, and FDB entries. The bridge is created with low aging time and multicast snooping disabled. The tests add and delete a fixed MAC address. Deferred state cleanup is handled by the forwarding library trap and explicit FDB deletion in each test.

## Dependencies and Integration Points
It integrates with the forwarding harness and requires support for the bridge FDB `activity_notify` keyword, JSON FDB output through `bridge -j`, and packet injection through `$MZ`. It also depends on ADF helper wrappers that abstract device operations for offload-capable environments.

## Risks
Timing-based state transitions can be sensitive to bridge aging configuration and system load. The script expects exact textual markers (`inactive`, `activity_notify`) in `bridge` output. If injected traffic is lost for reasons unrelated to FDB activity, the inactive-to-active transition will fail. The test uses one fixed MAC, so cleanup failure can contaminate subsequent tests in the same topology.

## Test Signals
Pass conditions are an inactive static entry becoming active after traffic, an active activity-notify entry becoming inactive after aging, and `updated` resetting only when replacement is performed without `norefresh`. Failures are reported through the forwarding harness `check_err`, `check_fail`, and `log_test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_activity_notify.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_fdb_learning_limit.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_fdb_learning_limit.sh

## Purpose
`bridge_fdb_learning_limit.sh` validates bridge FDB learned-entry accounting and the `fdb_max_learned` limit. It distinguishes dynamic learned entries from static, user, extern-learn, and local entries, and checks which entry types count toward or override learned FDB accounting.

## Important APIs, Functions, and Types
The script sources forwarding `lib.sh`, uses `ip`, `bridge`, `jq`, and `ping_do`, and defines `FDB_TYPES` rows with three fields: entry type, whether it is counted, and whether it overrides an existing learned entry. `fdb_get_n_learned()` reads `fdb_n_learned` from `ip -d -j link show dev br0 type bridge`. `fdb_get_n_mac()` counts matching non-VLAN FDB records. `fdb_add()` abstracts creation of learned, local, static, user (`static use`), and `extern_learn` entries.

## Control Flow
`check_fdb_n_learned_support()` first gates the feature by checking iproute2 help for `fdb_max_learned` and reading `fdb_n_learned` from a temporary bridge. The topology uses six netifs: two host-facing ports, one bridge-only port for local MAC testing, and bridge `br0`. `check_accounting()` resets the FDB, fills learned entries by changing `h1`'s MAC and pinging `h2`, checks the learned count, then runs `check_accounting_one_type()` for every FDB type. `check_limit()` sets `fdb_max_learned`, fills beyond the limit, verifies the cap, and then attempts to insert each FDB type at the limit.

## State and Persistence
The script creates `br0`, enslaves `swp1` and `swp2`, toggles `swp2` learning off, and temporarily enslaves `swp3` when testing local MACs. It repeatedly changes `h1`'s MAC address and resets the bridge FDB. `fdb_reset()` flushes the bridge FDB but reinstalls `h1`'s default MAC as a static `use` entry so dynamic learning starts from a controlled baseline.

## Dependencies and Integration Points
It integrates with the forwarding harness, VRF setup, and common ping helpers. It requires bridge support for `fdb_n_learned` and `fdb_max_learned`, iproute2 JSON details, and a kernel that exposes learned FDB accounting in bridge link info.

## Risks
The learned-entry fill depends on ping traffic creating FDB entries reliably and on `swp2` not learning reply MACs. If bridge output schema changes, `jq` selectors can fail. `bridge fdb flush dev br0` semantics must preserve or remove the expected records before the script reinstalls the default MAC. The limit test assumes `NUM_PKTS` exceeds `FDB_LIMIT` and that learned entries are dropped once the cap is reached.

## Test Signals
Signals include exact `fdb_n_learned` values after reset, fill, add, delete, and override operations; insertion success or rejection at the learned limit depending on entry type; and per-type `log_test` entries documenting accounting and limit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_fdb_learning_limit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_fdb_local_vlan_0.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_fdb_local_vlan_0.sh

## Purpose
`bridge_fdb_local_vlan_0.sh` tests the bridge `fdb_local_vlan_0` option, which controls whether local FDB entries are shared through VLAN 0. It validates both FDB table representation and end-to-end forwarding for bridge and port MAC addresses across 802.1d and 802.1q bridge modes, including runtime toggling and MAC address changes.

## Important APIs, Functions, and Types
The script sources forwarding `lib.sh` and uses ADF helpers, `bridge`, `ip`, `tc`, `jq`, and `$MZ`. `setup_prepare()` creates three hosts / switch-side links, enables forwarding, and installs routes between two IPv4/IPv6 subnets through a bridge gateway. `adf_bridge_create()` creates `br` with requested bridge attributes and restores its MAC after VLAN configuration. `check_mac_presence()` inspects JSON FDB output for a device MAC and VLAN. `do_end_to_end_test()` injects UDP traffic and checks tc flower counters on the expected receiving device.

## Control Flow
Default tests cover no-sharing and sharing cases for both non-VLAN-filtering and VLAN-filtering bridges, plus `test_addr_set`. The bridge is configured with VLANs 1, 2, and 3 on the bridge and on `swp1` / `swp2`. `do_test_no_sharing()` creates a bridge without sharing, verifies MAC entries per VLAN, changes port and bridge MACs, then toggles `fdb_local_vlan_0=1` and expects shared behavior. `do_test_sharing()` starts with sharing enabled, checks FDB sharing and forwarding, verifies flooding for nonexistent FDBs, checks that misleading nonlocal VLAN 0 entries do not affect VLAN-aware lookup, changes MACs, then toggles sharing off. `test_addr_set()` specifically covers bridge MAC assignment through `NET_ADDR_SET`.

## State and Persistence
The test creates bridge `br`, VLAN membership, VRF host state, tc ingress counters on `h2` and `h3`, and deferred cleanup actions through the harness. It temporarily changes MAC addresses on `swp1` and `br`, adds and deletes FDB records, and relies on per-test defer scopes for cleanup.

## Dependencies and Integration Points
It depends on the ADF forwarding library, bridge VLAN filtering, the `fdb_local_vlan_0` bridge attribute, JSON FDB output, tc flower counters, and mausezahn packet injection. It is integrated into the forwarding Makefile as a runnable test.

## Risks
The semantics under test differ between 802.1d and 802.1q modes; a mistake in expected flooding counts can mask a data-plane regression. End-to-end checks use exact packet counter deltas of 10, so background traffic on the same test devices would be problematic. The support probe uses `adf_ip_link_add XXbr ...` and must be cleaned by the library's defer scope. The test is sensitive to bridge FDB JSON schema and to MAC restoration after address changes.

## Test Signals
Pass signals include expected presence or absence of local MAC FDB entries on VLAN 0 and VLANs 1-3, exact tc counter increments for packets addressed to shared local MACs, flooding to `h2` for nonexistent or ignored entries, no flooding when VLAN 0 lookup is valid, and behavior changes after toggling `fdb_local_vlan_0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_fdb_local_vlan_0.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_igmp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_igmp.sh

## Purpose
`bridge_igmp.sh` validates bridge IGMP snooping and multicast database behavior for IGMPv2 and IGMPv3. It covers report/leave handling, IGMPv3 include and exclude filter-mode transitions, source-specific multicast forwarding, automatically added S,G entries for star-exclude ports, timeout behavior, and per-VLAN snooping interactions with STP state.

## Important APIs, Functions, and Types
The script sources forwarding `lib.sh`, uses `ip`, `bridge`, `jq`, `$MZ`, tc-enabled multicast helpers from the library (`mcast_packet_test`, `brmcast_check_sg_entries`, `brmcast_check_sg_state`, `brmcast_check_sg_fwding`), and JSON bridge MDB output. It defines raw IGMPv3 payload hex strings for IS_INCLUDE, IS_EXCLUDE, ALLOW, TO_EXCLUDE, and BLOCK records. `v3include_prepare()` and `v3exclude_prepare()` are shared setup routines that send crafted IGMPv3 reports and verify resulting MDB filter modes and source lists.

## Control Flow
The topology is a two-host bridge `br0` with multicast snooping and querier enabled. `v2reportleave_test()` uses `ip address ... autojoin` to create and remove an IGMPv2 membership and checks multicast forwarding before and after leave. IGMPv3 tests set bridge IGMP version 3, inject crafted packets with mausezahn, sleep for processing/timer windows, verify MDB JSON, and test S,G forwarding. Include-mode tests cover include-to-allow, include-to-is_include, include-to-is_exclude, include-to-to_exclude, and include-to-block transitions. Exclude-mode tests cover exclude-to-allow, exclude-to-is_include, exclude-to-is_exclude, exclude-to-to_exclude, exclude-to-block, timeout, and auto-added S,G entries. The final tests enable VLAN multicast snooping and verify IGMP query transmission starts when port or VLAN STP state enters forwarding.

## State and Persistence
State is in `br0`, `swp1`, `swp2`, host addresses, bridge MDB entries, multicast timers, STP state, VLAN multicast snooping attributes, and multicast statistics. `v3cleanup()` removes MDB entries and restores IGMP version 2. Some tests temporarily change multicast query intervals, response intervals, membership intervals, last-member intervals, VLAN filtering, and stats settings before restoring defaults.

## Dependencies and Integration Points
The file integrates with forwarding `lib.sh` and requires bridge multicast snooping, bridge MDB JSON with detailed source lists, mausezahn packet injection, jq, tc support from the harness, and per-VLAN multicast/stats support for the STP tests. It is listed as a forwarding `TEST_PROGS` script.

## Risks
The test uses handcrafted IGMP payload checksums and raw protocol bytes, so any packet-definition error invalidates the scenario. Timer-based tests are sensitive to system load and bridge timer units. Output checks assume specific JSON fields such as `source_list`, `filter_mode`, `flags`, and multicast xstats. Some functions refer to arrays named `X` and `Y` populated by prepare functions or local scopes; shell scoping mistakes could cause subtle test fragility.

## Test Signals
Signals include MDB entries appearing after reports and disappearing after leaves, expected filter modes (`include` or `exclude`), expected source lists and forwarding states, absence of stale sources after transitions, traffic forwarding only for allowed sources, `added_by_star_ex` flags on auto-created S,G entries, transition from exclude to include after timeout, and increasing IGMP query counters after STP forwarding state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_igmp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_locked_port.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_locked_port.sh

## Purpose
`bridge_locked_port.sh` tests bridge locked-port behavior and MAC Authentication Bypass (MAB). It verifies that locked ports block traffic until authorized by an FDB entry, that VLAN and IPv6 cases behave like IPv4, and that MAB-created locked FDB entries have correct lifecycle, roaming, configuration, flush, and redirect behavior.

## Important APIs, Functions, and Types
The script sources forwarding `lib.sh` and uses `ip`, `bridge`, `tc`, `$MZ`, `ping_do`, `ping6_do`, `vlan_create`, `vlan_destroy`, `mac_get`, `check_locked_port_support`, and `check_port_mab_support`. The topology has two hosts and two switch ports under VLAN-filtering bridge `br0`; `swp1` starts with learning disabled. Host helpers create IPv4/IPv6 addresses and VLAN subinterfaces for VLAN 100 tests.

## Control Flow
After setup, `tests_run` dispatches eight tests. `locked_port_ipv4()`, `locked_port_ipv6()`, and `locked_port_vlan()` confirm baseline connectivity, enable `locked on`, verify traffic fails without a static FDB entry, add a static entry for the host MAC, and verify traffic succeeds. `locked_port_mab()` enables learning, locked mode, and MAB, verifies a locked FDB entry is created by denied traffic, then replaces it with a static entry to authorize traffic. `locked_port_mab_roam()` checks that a locked entry can roam to an unlocked port but cannot roam back to a locked one. `locked_port_mab_config()` enforces that MAB requires both `locked on` and learning enabled. `locked_port_mab_flush()` ensures disabling MAB flushes only locked entries on that port. `locked_port_mab_redirect()` verifies tc mirred redirection can pass traffic from a locked port without creating locked entries until the redirect filter is removed.

## State and Persistence
The script creates `br0`, enslaves two switch ports, configures VLAN 100 as needed, toggles bridge link attributes (`learning`, `locked`, `mab`), adds and removes static and locked FDB entries, and installs a temporary tc `clsact` filter for redirection. Cleanup tears down bridge, VLANs, host addresses, and VRFs.

## Dependencies and Integration Points
It depends on forwarding `lib.sh`, bridge locked-port support, bridge MAB support for MAB tests, VLAN filtering, tc flower/mirred for redirect, and mausezahn for synthetic source MAC injection. Unsupported locked or MAB features are skipped per test through library support checks.

## Risks
The bridge port state is mutable across tests, so failure to restore `learning`, `locked`, or `mab` could affect later cases. Tests use command substitution with backticks for `mac_get`, which is functional but fragile if a helper emits extra text. MAB learning and roam checks depend on timely FDB updates after synthetic traffic. The redirect test must remove tc filters and qdiscs or it can perturb following bridge tests.

## Test Signals
Signals include pings succeeding before locking, failing while locked without FDB authorization, succeeding after static FDB authorization, locked FDB entries appearing with the `locked` marker under MAB, replacement removing the `locked` marker, allowed roam to unlocked ports, denied roam to locked ports, rejected invalid MAB configurations, selective flush of locked entries when MAB is disabled, and no locked entry for redirected traffic until redirection is removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_locked_port.sh -->
