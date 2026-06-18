# subset-b-006869 research

Grouped research report for subset-b-006869. Each section is source-tree aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/openvswitch/openvswitch.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/openvswitch/openvswitch.sh

## Purpose
`openvswitch.sh` is the kernel selftest driver for the in-kernel Open vSwitch datapath. It builds isolated sandboxes with network namespaces, veth pairs, OVS datapaths, vports, and flows, then validates basic forwarding, conntrack, NAT, upcalls, tunnel metadata, tunnel vport lifetime, drop reasons, and psample delivery.

## Important APIs, functions, and data
- `tests` is the test manifest consumed by the bottom-of-file dispatcher. Each pair maps a short test name to a KTAP-style description.
- `ovs_wait` retries commands for `WAIT_TIMEOUT`, extended on `KSFT_MACHINE_SLOW=yes`, and is used to absorb asynchronous netlink/upcall races.
- `sbx_add`, `ovs_setenv`, `ovs_sbx`, `on_exit`, and `ovs_exit_sig` implement sandbox directories and LIFO cleanup stored in each sandbox `cleanup` file.
- `ovs_add_dp`, `ovs_add_if`, `ovs_del_if`, `ovs_add_flow`, and `ovs_del_flows` delegate datapath operations to the colocated `ovs-dpctl.py` helper.
- `ovs_add_netns_and_veths` creates namespaces and veth pairs, moves peer ends into namespaces, optionally assigns addresses, attaches the host-side veth to a datapath, and can start upcall listeners.
- `ovs_drop_record_and_run` and `ovs_drop_reason_count` use `perf record/script` over `skb:kfree_skb` to check OVS drop reason accounting.
- Test bodies `test_psample`, `test_drop_reason`, `test_arp_ping`, `test_ct_connect_v4`, `test_connect_v4`, `test_nat_connect_v4`, `test_nat_related_v4`, `test_netlink_checks`, `test_upcall_interfaces`, `test_tunnel_metadata`, and `test_tunnel_refcount` each define one topology and expected behavior.

## Control flow
The script parses `-p`, `-v`, and `-t`, validates requested test names, then iterates over the `tests` manifest. `run_test` checks pyroute2 availability through `ovs-dpctl.py -h`, checks that the `openvswitch` module is loaded, invokes `test_${name}` in a subshell, prints `[ OK ]`, `[FAIL]`, or `[SKIP]`, and updates the aggregate exit code. Test functions create a sandbox, create datapaths/vports, install flows, run traffic tools such as `ping`, `arping`, `nc`, or `iperf`-style probes, and rely on `trap ovs_exit_sig EXIT TERM INT ERR` for cleanup.

## State and persistence
Runtime state lives in per-test sandbox directories under the current working directory: `debug.log`, `stdout`, `stderr`, per-vport upcall outputs, tcpdump outputs, `perf.data`, and `cleanup`. Kernel state includes network namespaces, veth links, OVS datapaths, vports, flows, and netlink listeners. The script deliberately removes sandbox directories on pass and non-paused failures, but preserves logs when `-p` is used.

## Dependencies and integration points
It requires root-capable networking, the `openvswitch` kernel module, `python3`, pyroute2 through `ovs-dpctl.py`, `iproute2`, and test-specific tools (`arping`, `nc`, `perf`, `pahole`, `tcpdump`). It integrates tightly with `ovs-dpctl.py` for generic-netlink OVS control and with Linux kselftest skip semantics (`ksft_skip=4`).

## Risks and edge cases
The tests are timing sensitive around upcall listener startup and tunnel device deletion, so `ovs_wait` is critical. Cleanup is shell-fragment based and must remain quoted enough to avoid deleting unrelated namespaces or links. Several checks inspect `dmesg`, `perf`, and `pahole` output, making them kernel-version and permission sensitive. Flow/action parser limitations in `ovs-dpctl.py` can make a shell test fail before reaching kernel behavior.

## Test signals
Success is reported by per-test `[ OK ]` lines and exit code 0 unless every test skipped, in which case kselftest skip code 4 is retained. Important assertions include successful ARP/ping/nc traffic, rejected unsafe flow actions producing kernel warnings, psample output matching cookies and truncated data, upcall output containing expected decoded keys, NAT flow counters, and tunnel vports disappearing after datapath deletion.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/openvswitch/openvswitch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/openvswitch/ovs-dpctl.py -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/openvswitch/ovs-dpctl.py

## Purpose
`ovs-dpctl.py` is a Python generic-netlink control utility for the kernel Open vSwitch datapath. It is used by `openvswitch.sh` to create/delete datapaths, add/delete vports, add/dump/delete flows, receive upcalls, and print psample events without depending on the full userspace Open vSwitch tool stack.

## Important APIs, types, and functions
- Generic-netlink family constants cover `ovs_datapath`, `ovs_vport`, `ovs_flow`, `ovs_packet`, and `psample` usage.
- Parsing helpers (`intparse`, `parse_flags`, `parse_ct_state`, `convert_mac`, `convert_ipv4`, `convert_ipv6`, `parse_attrs`) translate dpctl-like strings into netlink attributes.
- `ovs_dp_msg` extends `genlmsg` with `dpifindex`, matching OVS generic-netlink message headers.
- `ovsactions` defines `OVS_ACTION_ATTR_*` layouts and parsers/formatters for output, recirc, ct/nat, clone, set/set_masked, trunc, drop, userspace, sample, and psample actions.
- `ovskey` defines `OVS_KEY_ATTR_*` flow key layouts and parsers/formatters for ports, Ethernet, IPv4/IPv6, ARP, TCP/UDP/SCTP, ICMP, CT state/zone/mark, recirc, dp hash, skb mark, and tunnel metadata.
- `OvsPacket` listens for `OVS_PACKET_CMD_MISS`, `ACTION`, and `EXECUTE` upcalls and dispatches to an `OvsFlow` handler.
- `OvsDatapath` wraps datapath `GET/NEW/DEL`; `OvsVport` wraps vport `GET/NEW/SET/DEL`; `OvsFlow` wraps flow `NEW/DEL/GET` and upcall formatting.
- `PsampleEvent` binds the `psample` multicast group and prints sample rate, group, cookie, and packet data.
- `main` exposes subcommands: `show`, `add-dp`, `del-dp`, `add-if`, `del-if`, `dump-flows`, `add-flow`, `del-flows`, and `psample-events`.

## Control flow
Startup imports pyroute2 and exits with a clear message if missing or too old. `main` registers custom `ovskey` and `ovsactions` atoms with pyroute2, parses command-line arguments, constructs socket helpers, and dispatches by subcommand. Add/show/delete operations perform an OVS datapath lookup before vport or flow operations. `add-flow` parses the user flow and action strings into nested NLAs, then sends `OVS_FLOW_CMD_NEW`. Upcall modes keep the process in a blocking netlink receive loop and print decoded MISS/ACTION events.

## State and persistence
The script itself persists no files. Its durable effects are kernel datapaths, vports, flows, tunnel links created through pyroute2 `IPRoute`, and live netlink sockets. For `add-if -u` and `add-dp -u`, the process stays alive to keep upcall sockets registered; killing that process changes kernel upcall delivery state.

## Dependencies and integration points
It depends on `pyroute2 >= 0.6`, Python `ipaddress`, generic netlink, the Open vSwitch kernel module, and netlink UAPI compatibility. `openvswitch.sh` shells out to it for all datapath operations, and several tests grep its upcall/psample textual output. Tunnel vport creation integrates with kernel lightweight tunnel devices through `pyroute2.iproute.IPRoute` when `--lwt` is enabled.

## Risks and edge cases
The parser supports only the flow/action subset implemented in this file; unsupported OVS syntax raises `ValueError`. Some parsing code assumes delimiters exist and can index past an empty string for malformed input. Long clone recursion requires a high recursion limit. Several default arguments instantiate sockets at definition time (`OvsPacket()`, `NDB()`, `OvsVport()`), which is acceptable for the selftest but can surprise reuse. Kernel and pyroute2 NLA map drift is a primary compatibility risk.

## Test signals
Functional signals come from `openvswitch.sh`: datapaths show expected ports, flow dumps expose counters and actions, unsafe flow additions fail, upcall handlers print decoded `MISS upcall` and `userspace action command`, and `psample-events` prints expected rate/group/cookie/data lines.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/openvswitch/ovs-dpctl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/Makefile -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/Makefile

## Purpose
The OVPN `Makefile` builds and packages the OpenVPN data-channel accelerator selftests. It compiles `ovpn-cli`, declares shell tests, and includes supporting fixtures for the kselftest install/run harness.

## Important variables and build APIs
- `CFLAGS` enables strict warnings, debug symbols, no optimization, and kernel header includes from `KHDR_INCLUDES`.
- `pkg-config` probes `mbedcrypto-3`, `mbedtls-3`, `libnl-3.0`, and `libnl-genl-3.0`, with fallback include and library flags for common distro layouts.
- `TEST_FILES` ships `common.sh`, `data64.key`, the `json` fixture directory, peer tables, and the YNL Python CLI used for notifications.
- `TEST_PROGS` lists the executable shell tests and mode variants.
- `TEST_GEN_FILES := ovpn-cli` tells kselftest infrastructure to build the local C helper.

## Control flow
The Makefile is declarative. After setting compiler/linker inputs and test manifests, it includes `../../lib.mk`, which provides kselftest build, install, and run targets.

## State and persistence
Build output is `ovpn-cli`. Installed or staged tests include the declared fixtures and shell scripts. No runtime state is created by the Makefile itself.

## Dependencies and integration points
The helper requires libnl generic netlink and mbedTLS/mbedcrypto. The tests integrate with `tools/testing/selftests/lib.mk`, kernel headers containing `linux/ovpn.h`, the YNL CLI under `tools/net/ynl/pyynl/cli.py`, and fixture files consumed by `common.sh`.

## Risks and edge cases
Fallback library names may fail on systems using only versioned pkg-config names or nonstandard libnl paths. The test list assumes all referenced scripts and fixture directories are installed together; missing `json`, peer files, or `data64.key` causes runtime failures.

## Test signals
A successful build produces `ovpn-cli`; successful kselftest packaging includes every `TEST_PROGS` script and `TEST_FILES` dependency.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/common.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/common.sh

## Purpose
`common.sh` is the shared OVPN selftest library. It provides KTAP-aware command wrappers, namespace and interface setup, peer/key registration, notification capture and comparison, and cleanup for all OVPN test variants.

## Important APIs and functions
- Environment knobs include `OVPN_UDP_PEERS_FILE`, `OVPN_TCP_PEERS_FILE`, `OVPN_CLI`, `OVPN_YNL`, `OVPN_ALG`, `OVPN_PROTO`, `OVPN_FLOAT`, `OVPN_SYMMETRIC_ID`, `OVPN_VERBOSE`, and derived `OVPN_ID_OFFSET`.
- `OVPN_JQ_FILTER` normalizes YNL JSON notifications by flattening arrays, dropping IPv6 remote notifications, deleting `ifindex`, sorting by peer id, and selecting each message.
- `ovpn_cmd_run`, `ovpn_cmd_ok`, `ovpn_cmd_mayfail`, and `ovpn_cmd_fail` standardize command execution and failure reporting.
- `ovpn_run_stage` and `ovpn_stage_err` connect test stages to `ktap_test_pass`/`ktap_test_fail` under `set -eE`.
- `ovpn_create_ns`, `ovpn_setup_ns`, and `ovpn_cleanup_peer_ns` manage per-peer network namespaces, veth topology, `tunN` OVPN interfaces, overlay IPs, MTU, and optional LAN-behind-peer routing.
- `ovpn_build_capture_filter` emits tcpdump filters that match OpenVPN DATA_V2 headers for UDP and TCP.
- `ovpn_setup_listener`, `ovpn_compare_ntfs`, and `ovpn_stop_listener` capture YNL peer multicast notifications and diff them against JSON fixtures.
- `ovpn_add_peer` registers UDP or TCP peers and installs keys, switching between asymmetric and symmetric peer IDs.
- `ovpn_cleanup` kills background `ovpn-cli` processes, listener PIDs, veth links, and OVPN namespaces.

## Control flow
Tests source this file, then call its functions from staged test bodies. At source time it computes `OVPN_NUM_PEERS` from the selected peer table unless already set. Setup generally creates namespaces, starts listeners, creates OVPN interfaces, registers peers and keys, then test-specific traffic/lifecycle stages run. Cleanup is driven by each test script's EXIT trap.

## State and persistence
Runtime state includes network namespaces `ovpn_peer*`, veth links, OVPN netdevices `tun*`, background `ovpn-cli` daemons that keep sockets alive, YNL listener PIDs, temporary JSON files, nftables state in some tests, and `OVPN_TMP_JSONS`/`OVPN_LISTENER_PIDS` associative arrays. The file intentionally removes this state during cleanup.

## Dependencies and integration points
It depends on Bash associative arrays, `iproute2`, `jq`, `diff`, `tcpdump`, `timeout`, `killall`, the built `ovpn-cli`, kselftest KTAP helpers, peer fixture files, `data64.key`, and the YNL CLI. It integrates with `ovpn-cli.c` commands such as `new_iface`, `new_multi_peer`, `new_peer`, `new_key`, `set_peer`, `del_peer`, and `listen/connect`.

## Risks and edge cases
Asynchronous YNL listener startup can stall, so `test.sh` serializes listener creation. JSON comparison intentionally ignores IPv6 remote notifications and `ifindex`; changes in notification schema or ordering require fixture updates. Cleanup uses `killall` by basename, which can affect other same-named helpers in the namespace context. TCP mode uses background listeners and fixed sleeps, making it timing sensitive.

## Test signals
A healthy common setup yields reachable tunnel IPs, tcpdump matches for DATA_V2 headers, successful key operations, and JSON diffs against `json/peer*.json` with no output differences.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/config -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/config

## Purpose
The OVPN `config` file declares the kernel configuration prerequisites for running the OpenVPN data-channel accelerator selftests.

## Important settings
It requires core crypto and networking support (`CONFIG_CRYPTO`, AES, GCM, CHACHA20POLY1305, `CONFIG_INET`, `CONFIG_NET`), tunnel and netfilter support (`CONFIG_NET_UDP_TUNNEL`, `CONFIG_NETFILTER`, `CONFIG_NF_TABLES`, `CONFIG_NF_TABLES_INET`), stream parsing for TCP mode, destination cache support, and the OVPN module (`CONFIG_OVPN=m`).

## Control flow
There is no executable control flow. Kselftest tooling can use this file as a requirements manifest when evaluating whether a kernel is suitable for the test directory.

## State and persistence
No runtime state is created. The file represents build-time/kernel-capability state only.

## Dependencies and integration points
The listed symbols correspond to features used by `ovpn-cli.c`, `common.sh`, and the shell tests: crypto algorithms for data-channel keys, nftables for mark filtering, UDP tunnel plumbing, TCP stream parsing, and the `ovpn` module itself.

## Risks and edge cases
If `CONFIG_OVPN` or required crypto is absent, tests skip or fail during `modprobe`/key setup. If nftables support is missing, `test-mark.sh` cannot validate socket marks. If stream parser support is missing, TCP variants are unreliable.

## Test signals
The practical signal is that `modprobe -q ovpn` succeeds and all selected OVPN shell tests can create OVPN interfaces, peers, and keys.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer0-float.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer0-float.json

## Purpose
`peer0-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer0 in the asymmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 9 event(s), event type(s) peer-del-ntf, peer-float-ntf, peer id sequence `[1, 2, 3, 1, 2, 3, 4, 5, 6]`, and delete reason set `expired, userspace`. It also expects float notifications to remote IPv4 addresses 10.10.1.3, 10.10.2.3, 10.10.3.3.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer0-float.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer0-symm-float.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer0-symm-float.json

## Purpose
`peer0-symm-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer0 in the symmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 9 event(s), event type(s) peer-del-ntf, peer-float-ntf, peer id sequence `[1, 2, 3, 1, 2, 3, 4, 5, 6]`, and delete reason set `expired, userspace`. It also expects float notifications to remote IPv4 addresses 10.10.1.3, 10.10.2.3, 10.10.3.3.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer0-symm-float.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer0-symm.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer0-symm.json

## Purpose
`peer0-symm.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer0 in the symmetric peer-id, non-floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 6 event(s), event type(s) peer-del-ntf, peer id sequence `[1, 2, 3, 4, 5, 6]`, and delete reason set `expired, userspace`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer0-symm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer0.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer0.json

## Purpose
`peer0.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer0 in the asymmetric peer-id, non-floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 6 event(s), event type(s) peer-del-ntf, peer id sequence `[1, 2, 3, 4, 5, 6]`, and delete reason set `expired, userspace`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer0.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer1-float.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer1-float.json

## Purpose
`peer1-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer1 in the asymmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[10]`, and delete reason set `userspace`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer1-float.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer1-symm-float.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer1-symm-float.json

## Purpose
`peer1-symm-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer1 in the symmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[1]`, and delete reason set `userspace`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer1-symm-float.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer1-symm.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer1-symm.json

## Purpose
`peer1-symm.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer1 in the symmetric peer-id, non-floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[1]`, and delete reason set `userspace`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer1-symm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer1.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer1.json

## Purpose
`peer1.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer1 in the asymmetric peer-id, non-floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[10]`, and delete reason set `userspace`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer1.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer2-float.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer2-float.json

## Purpose
`peer2-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer2 in the asymmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[11]`, and delete reason set `userspace`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer2-float.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer2-symm-float.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer2-symm-float.json

## Purpose
`peer2-symm-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer2 in the symmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[2]`, and delete reason set `userspace`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer2-symm-float.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer2-symm.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer2-symm.json

## Purpose
`peer2-symm.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer2 in the symmetric peer-id, non-floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[2]`, and delete reason set `userspace`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer2-symm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer2.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer2.json

## Purpose
`peer2.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer2 in the asymmetric peer-id, non-floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[11]`, and delete reason set `userspace`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer2.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer3-float.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer3-float.json

## Purpose
`peer3-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer3 in the asymmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[12]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer3-float.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer3-symm-float.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer3-symm-float.json

## Purpose
`peer3-symm-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer3 in the symmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[3]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer3-symm-float.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer3-symm.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer3-symm.json

## Purpose
`peer3-symm.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer3 in the symmetric peer-id, non-floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[3]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer3-symm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer3.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer3.json

## Purpose
`peer3.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer3 in the asymmetric peer-id, non-floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[12]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer3.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer4-float.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer4-float.json

## Purpose
`peer4-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer4 in the asymmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[13]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer4-float.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer4-symm-float.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer4-symm-float.json

## Purpose
`peer4-symm-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer4 in the symmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[4]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer4-symm-float.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer4-symm.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer4-symm.json

## Purpose
`peer4-symm.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer4 in the symmetric peer-id, non-floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[4]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer4-symm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer4.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer4.json

## Purpose
`peer4.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer4 in the asymmetric peer-id, non-floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[13]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer4.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer5-float.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer5-float.json

## Purpose
`peer5-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer5 in the asymmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[14]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer5-float.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer5-symm-float.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer5-symm-float.json

## Purpose
`peer5-symm-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer5 in the symmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[5]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer5-symm-float.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer5-symm.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer5-symm.json

## Purpose
`peer5-symm.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer5 in the symmetric peer-id, non-floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[5]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer5-symm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer5.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer5.json

## Purpose
`peer5.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer5 in the asymmetric peer-id, non-floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[14]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer5.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer6-float.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer6-float.json

## Purpose
`peer6-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer6 in the asymmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[15]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer6-float.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer6-symm-float.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer6-symm-float.json

## Purpose
`peer6-symm-float.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer6 in the symmetric peer-id, floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[6]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer6-symm-float.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer6-symm.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer6-symm.json

## Purpose
`peer6-symm.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer6 in the symmetric peer-id, non-floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[6]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer6-symm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer6.json -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer6.json

## Purpose
`peer6.json` is an expected YNL notification fixture for the OVPN selftests. It records the normalized peer multicast events expected for peer6 in the asymmetric peer-id, non-floating transport scenario.

## Important schema and data
The file is newline-delimited JSON. Each row has `name` and `msg.peer`; `msg.ifindex` is present in the fixture but deleted before comparison by `OVPN_JQ_FILTER`. This fixture contains 1 event(s), event type(s) peer-del-ntf, peer id sequence `[15]`, and delete reason set `expired`. It contains no float notification entries.

## Control flow
`common.sh` selects this file in `ovpn_compare_ntfs` by building the suffix from `OVPN_SYMMETRIC_ID` and `OVPN_FLOAT`, then compares it with captured YNL output using `jq -s "$OVPN_JQ_FILTER"` and `diff`. The fixture is passive data; the test script controls when listener output is stopped and compared.

## State and persistence
The fixture is persistent expected output. Runtime notifications are captured in temporary files and removed after comparison; this file is not modified by tests.

## Dependencies and integration points
It depends on the YNL `ovpn --subscribe peers --output-json` message schema, the peer IDs created by `udp_peers.txt`/`tcp_peers.txt`, the ID offset rules in `common.sh`, and the lifecycle stages in `test.sh` that delete peer 1 and 2 while allowing later peers to expire.

## Risks and edge cases
Any kernel notification schema change, additional event, changed delete reason, changed peer ID mapping, or ordering difference will produce a fixture diff. Because `ifindex` is stripped, interface-number churn is tolerated, but peer IDs and event names are not.

## Test signals
A passing notification stage prints `Checking notifications for peer ... OK` for this peer/mode combination. A failure emits the unified diff between normalized expected fixture rows and captured YNL rows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/json/peer6.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/ovpn-cli.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/ovpn-cli.c

## Purpose
`ovpn-cli.c` is the C control utility used by the OVPN selftests to create/delete OVPN interfaces, create sockets, register peers, configure keys, query state, swap keys, and listen for OVPN multicast notifications. It speaks directly to rtnetlink and the `ovpn` generic-netlink family.

## Important APIs, types, and functions
- `struct ovpn_ctx` is the central command context: command, cipher/key material, addresses, peer IDs, interface name/index, socket FDs, keepalive values, key slot/id, socket mark, symmetric/asymmetric ID mode, and peer file path.
- `struct nl_ctx` owns a libnl socket/message/callback set plus the resolved OVPN family id.
- Netlink helpers `nl_ctx_alloc_flags`, `ovpn_nl_msg_send`, `ovpn_nl_cb_error`, `ovpn_nl_cb_ack`, and `ovpn_nl_cb_finish` build and send generic-netlink requests with extended ACK reporting.
- Key helpers `ovpn_parse_key`, `ovpn_parse_cipher`, `ovpn_parse_key_direction`, and `ovpn_parse_key_slot` decode base64 key files into encrypt/decrypt keys and nonce tails.
- Socket helpers `ovpn_socket`, `ovpn_udp_socket`, `ovpn_listen`, `ovpn_accept`, and `ovpn_connect` create UDP/TCP sockets, set reuse options and optional `SO_MARK`, bind/listen/connect, and keep sockets alive for kernel peer ownership.
- Peer/key operations include `ovpn_new_peer`, `ovpn_set_peer`, `ovpn_del_peer`, `ovpn_get_peer`, `ovpn_new_key`, `ovpn_del_key`, `ovpn_get_key`, and `ovpn_swap_keys`.
- Rtnetlink helpers `ovpn_addattr`, `ovpn_nest_start`, `ovpn_rt_send`, `ovpn_new_iface`, and `ovpn_del_iface` create/delete OVPN netdevices with optional P2P/MP mode.
- Multicast helpers `ovpn_get_mcast_id`, `ovpn_listen_mcast`, and `ovpn_handle_msg` subscribe to peer notifications.
- CLI parsing is split across `ovpn_parse_cmd`, `ovpn_parse_cmd_args`, and `ovpn_run_cmd`.

## Control flow
`main` parses the command, initializes defaults (`AF_UNSPEC`, no cipher), parses command-specific arguments, then dispatches through `ovpn_run_cmd`. Interface creation uses rtnetlink. Peer and key commands use generic netlink with nested OVPN attributes. `listen` accepts TCP clients listed in a peers file and registers each accepted socket; `connect` opens a TCP socket, registers a peer, optionally installs a key, sends test data, then backgrounds itself. UDP multi-peer mode creates one socket and registers all peers from a table. Long-lived socket commands call `ovpn_waitbg`, daemonizing and pausing until signaled so the kernel can keep using their socket FDs.

## State and persistence
Persistent effects are kernel netdevices, peer entries, key slots, keepalive settings, socket ownership, and multicast subscription state while the process runs. Key material is read from a base64 file and stored only in process memory before being sent to the kernel. TCP/UDP socket commands intentionally persist as daemonized processes until killed by test cleanup.

## Dependencies and integration points
It depends on `linux/ovpn.h`, libnl generic netlink, rtnetlink, mbedTLS base64/error helpers, kselftest headers, and standard socket APIs. Shell tests call it through `ip netns exec` for every OVPN management operation. The YNL notification fixtures rely on the same kernel OVPN multicast events this tool can listen to through `listen_mcast`.

## Risks and edge cases
Argument validation is uneven: many `strtoul` calls rely on `errno` without always resetting it, and `del_key` requires a slot in practice despite usage suggesting it is optional. Backgrounding via `daemon(1,1); pause()` requires cleanup to kill helpers, otherwise sockets and peer state can linger. Peer-file parsing is fixed-width with `fscanf` and `MAX_PEERS` only enforced in TCP listen mode. The code carries compatibility shims for older libnl; changes in `linux/ovpn.h` attributes or libnl behavior can break message construction.

## Test signals
The shell tests treat zero exit codes as success and grep/observe side effects through traffic, `get_peer`, `get_key`, YNL notification diffs, and socket behavior. CLI stderr/stdout includes useful signals such as created/deleted interfaces, accepted/connected TCP sockets, peer/key dumps, multicast notification names, and detailed kernel extended ACK messages on failure.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/ovpn-cli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-chachapoly.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-chachapoly.sh

## Purpose
This thin OVPN selftest wrapper runs the ChaCha20-Poly1305 algorithm variant. It exists so kselftest can expose the mode as a separate `TEST_PROGS` entry while sharing the common implementation.

## Important APIs and data
The only behavior is setting `OVPN_ALG="chachapoly"` before sourcing `test.sh`. The script then executes `source test.sh` or `source test-close-socket.sh`, so all functions, traps, and KTAP reporting come from the sourced file.

## Control flow
Bash evaluates the variable assignment, sources the target test script in the same shell, and the sourced script immediately runs its staged test plan. There are no local functions or local cleanup handlers in this wrapper.

## State and persistence
State is inherited from the sourced test. The assignment changes environment-visible shell variables that affect peer setup, key algorithm choice, MTU, transport mode, or fixture selection.

## Dependencies and integration points
It depends on the target sourced script, `common.sh`, `ovpn-cli`, fixture files, and the same root/networking requirements as the base test. It reuses the full main OVPN lifecycle and traffic plan while changing the cipher sent to `ovpn-cli new_key`.

## Risks and edge cases
Because the script uses `source`, any syntax error or early exit in the target script terminates this wrapper. The variable must be set before sourcing; moving it afterward would silently run the default scenario.

## Test signals
The test signals are exactly those of the sourced base script: KTAP plan/pass/fail lines, command wrapper failures, traffic checks, key/peer lifecycle checks, and notification fixture diffs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-chachapoly.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-close-socket-tcp.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-close-socket-tcp.sh

## Purpose
This thin OVPN selftest wrapper runs the TCP close-socket variant. It exists so kselftest can expose the mode as a separate `TEST_PROGS` entry while sharing the common implementation.

## Important APIs and data
The only behavior is setting `OVPN_PROTO="TCP"` before sourcing `test-close-socket.sh`. The script then executes `source test.sh` or `source test-close-socket.sh`, so all functions, traps, and KTAP reporting come from the sourced file.

## Control flow
Bash evaluates the variable assignment, sources the target test script in the same shell, and the sourced script immediately runs its staged test plan. There are no local functions or local cleanup handlers in this wrapper.

## State and persistence
State is inherited from the sourced test. The assignment changes environment-visible shell variables that affect peer setup, key algorithm choice, MTU, transport mode, or fixture selection.

## Dependencies and integration points
It depends on the target sourced script, `common.sh`, `ovpn-cli`, fixture files, and the same root/networking requirements as the base test. It reuses the close-socket topology in TCP mode so listener/connect socket lifetime paths are exercised.

## Risks and edge cases
Because the script uses `source`, any syntax error or early exit in the target script terminates this wrapper. The variable must be set before sourcing; moving it afterward would silently run the default scenario.

## Test signals
The test signals are exactly those of the sourced base script: KTAP plan/pass/fail lines, command wrapper failures, traffic checks, key/peer lifecycle checks, and notification fixture diffs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-close-socket-tcp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-close-socket.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-close-socket.sh

## Purpose
`test-close-socket.sh` validates that OVPN peer state and data forwarding survive normal setup and then behave correctly when userspace socket-owning helper processes are closed during cleanup. It is shared by UDP mode and `test-close-socket-tcp.sh`.

## Important APIs and functions
- Sources `common.sh`, enabling namespace setup, peer registration, command wrappers, and cleanup.
- `ovpn_prepare_network` creates peer namespaces, creates OVPN interfaces, registers every peer, and sets keepalive intervals/timeouts on both server and peers.
- `ovpn_run_ping_traffic` sends high-count ping traffic from peer0 to every peer tunnel IP.
- `ovpn_run_iperf` starts an iperf3 server in peer0 and runs a zerocopy client from peer1.
- `ovpn_test_exit` cleans namespaces and removes the `ovpn` module, printing partial KTAP totals if the test exits early.

## Control flow
With `set -eE`, the script installs EXIT and ERR traps, prints a KTAP header with plan 3, performs cleanup, loads the `ovpn` module, and runs three stages: topology setup, ping traffic, and iperf throughput. On completion it marks `ovpn_test_finished=1` and calls `ktap_finished`.

## State and persistence
Runtime state is the common OVPN namespace topology plus background `ovpn-cli` helpers that own sockets. All state is intended to be removed in the EXIT trap by `ovpn_cleanup` and `modprobe -r ovpn`.

## Dependencies and integration points
It depends on `common.sh`, `ovpn-cli`, `ip`, `ping`, `iperf3`, the selected peer table, `data64.key`, and the `ovpn` kernel module. TCP mode is selected externally by `test-close-socket-tcp.sh` via `OVPN_PROTO=TCP`.

## Risks and edge cases
If iperf3 is absent or slow, the third stage fails. Background socket helpers must be killed reliably or the module removal can fail. The test uses high packet counts, so slow machines may expose timing sensitivity even though this script has no explicit slow-machine tuning.

## Test signals
Expected KTAP stages are `setup network topology`, `run ping traffic`, and `run iperf throughput`. Any command wrapper failure prints the command and return code before the ERR trap records the active stage as failed.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-close-socket.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-float.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-float.sh

## Purpose
This thin OVPN selftest wrapper runs the floating transport variant. It exists so kselftest can expose the mode as a separate `TEST_PROGS` entry while sharing the common implementation.

## Important APIs and data
The only behavior is setting `OVPN_FLOAT="1"` before sourcing `test.sh`. The script then executes `source test.sh` or `source test-close-socket.sh`, so all functions, traps, and KTAP reporting come from the sourced file.

## Control flow
Bash evaluates the variable assignment, sources the target test script in the same shell, and the sourced script immediately runs its staged test plan. There are no local functions or local cleanup handlers in this wrapper.

## State and persistence
State is inherited from the sourced test. The assignment changes environment-visible shell variables that affect peer setup, key algorithm choice, MTU, transport mode, or fixture selection.

## Dependencies and integration points
It depends on the target sourced script, `common.sh`, `ovpn-cli`, fixture files, and the same root/networking requirements as the base test. It enables the additional floating peer checks and selects `*-float.json` notification fixtures.

## Risks and edge cases
Because the script uses `source`, any syntax error or early exit in the target script terminates this wrapper. The variable must be set before sourcing; moving it afterward would silently run the default scenario.

## Test signals
The test signals are exactly those of the sourced base script: KTAP plan/pass/fail lines, command wrapper failures, traffic checks, key/peer lifecycle checks, and notification fixture diffs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-float.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-large-mtu.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-large-mtu.sh

## Purpose
This thin OVPN selftest wrapper runs the large-MTU variant. It exists so kselftest can expose the mode as a separate `TEST_PROGS` entry while sharing the common implementation.

## Important APIs and data
The only behavior is setting `MTU="1500"` before sourcing `test.sh`. The script then executes `source test.sh` or `source test-close-socket.sh`, so all functions, traps, and KTAP reporting come from the sourced file.

## Control flow
Bash evaluates the variable assignment, sources the target test script in the same shell, and the sourced script immediately runs its staged test plan. There are no local functions or local cleanup handlers in this wrapper.

## State and persistence
State is inherited from the sourced test. The assignment changes environment-visible shell variables that affect peer setup, key algorithm choice, MTU, transport mode, or fixture selection.

## Dependencies and integration points
It depends on the target sourced script, `common.sh`, `ovpn-cli`, fixture files, and the same root/networking requirements as the base test. It forces tunnel interface MTU during namespace setup while retaining the main data, key, lifecycle, and notification checks.

## Risks and edge cases
Because the script uses `source`, any syntax error or early exit in the target script terminates this wrapper. The variable must be set before sourcing; moving it afterward would silently run the default scenario.

## Test signals
The test signals are exactly those of the sourced base script: KTAP plan/pass/fail lines, command wrapper failures, traffic checks, key/peer lifecycle checks, and notification fixture diffs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-large-mtu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-mark.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-mark.sh

## Purpose
`test-mark.sh` validates OVPN socket firewall mark propagation. It creates a multi-peer UDP topology with a server-side socket mark, installs an nftables output rule that drops packets with that mark, verifies traffic is dropped and counted, removes the rule, and verifies recovery.

## Important APIs and functions
- `MARK=1056` is passed to `ovpn-cli new_multi_peer` and matched by nftables `meta mark`.
- `ovpn_mark_prepare_network` creates namespaces/interfaces, creates the marked server multi-peer socket, installs server/client keys, registers peers, and sets keepalive values.
- `ovpn_mark_run_baseline_traffic` proves tunnel traffic works before filtering.
- `ovpn_mark_add_drop_rule` flushes nftables, creates an inet filter output chain, and installs a counter drop rule for `MARK`.
- `ovpn_mark_verify_drop_traffic` expects ping failures, parses transmitted packet counts, and verifies the nft counter equals the expected drop total.
- `ovpn_mark_remove_drop_rule` and `ovpn_mark_verify_traffic_recovery` clear filtering and ensure traffic resumes.

## Control flow
The script uses `set -eE`, sources `common.sh`, installs EXIT/ERR traps, declares a six-stage KTAP plan, cleans old state, loads `ovpn`, and runs the mark-specific stages in order.

## State and persistence
It creates OVPN namespaces/devices/peers plus an nftables ruleset inside `ovpn_peer0`. Cleanup removes OVPN state and unloads the module; `ovpn_mark_remove_drop_rule` flushes nftables before the recovery stage.

## Dependencies and integration points
It depends on `common.sh`, `ovpn-cli`, `nft`, `ping`, `ip`, the UDP peer table, `data64.key`, and `CONFIG_NF_TABLES*` support from the OVPN config. It specifically exercises the `mark` argument handled by `ovpn-cli` in `CMD_NEW_MULTI_PEER` and `SO_MARK` in `ovpn_socket`.

## Risks and edge cases
Counter parsing depends on nft output text. The expected drop counter is derived from ping's transmitted count, so unusual ping output can fail parsing. The script configures only peers 0 through 3 despite `OVPN_NUM_PEERS` potentially being larger, intentionally narrowing the mark scenario.

## Test signals
Pass signals are six KTAP stages: setup, baseline traffic, nft rule install, marked traffic drop/count, rule removal, and recovery traffic. A mismatch between expected and actual nft packet counters is the central failure signal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-mark.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-symmetric-id-float.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-symmetric-id-float.sh

## Purpose
This thin OVPN selftest wrapper runs the symmetric peer-id plus floating transport variant. It exists so kselftest can expose the mode as a separate `TEST_PROGS` entry while sharing the common implementation.

## Important APIs and data
The only behavior is setting `OVPN_SYMMETRIC_ID="1"` and `OVPN_FLOAT="1"` before sourcing `test.sh`. The script then executes `source test.sh` or `source test-close-socket.sh`, so all functions, traps, and KTAP reporting come from the sourced file.

## Control flow
Bash evaluates the variable assignment, sources the target test script in the same shell, and the sourced script immediately runs its staged test plan. There are no local functions or local cleanup handlers in this wrapper.

## State and persistence
State is inherited from the sourced test. The assignment changes environment-visible shell variables that affect peer setup, key algorithm choice, MTU, transport mode, or fixture selection.

## Dependencies and integration points
It depends on the target sourced script, `common.sh`, `ovpn-cli`, fixture files, and the same root/networking requirements as the base test. It selects symmetric peer IDs, runs float checks, and compares against `*-symm-float.json` fixtures.

## Risks and edge cases
Because the script uses `source`, any syntax error or early exit in the target script terminates this wrapper. The variable must be set before sourcing; moving it afterward would silently run the default scenario.

## Test signals
The test signals are exactly those of the sourced base script: KTAP plan/pass/fail lines, command wrapper failures, traffic checks, key/peer lifecycle checks, and notification fixture diffs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-symmetric-id-float.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-symmetric-id-tcp.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-symmetric-id-tcp.sh

## Purpose
This thin OVPN selftest wrapper runs the TCP symmetric peer-id variant. It exists so kselftest can expose the mode as a separate `TEST_PROGS` entry while sharing the common implementation.

## Important APIs and data
The only behavior is setting `OVPN_PROTO="TCP"` and `OVPN_SYMMETRIC_ID=1` before sourcing `test.sh`. The script then executes `source test.sh` or `source test-close-socket.sh`, so all functions, traps, and KTAP reporting come from the sourced file.

## Control flow
Bash evaluates the variable assignment, sources the target test script in the same shell, and the sourced script immediately runs its staged test plan. There are no local functions or local cleanup handlers in this wrapper.

## State and persistence
State is inherited from the sourced test. The assignment changes environment-visible shell variables that affect peer setup, key algorithm choice, MTU, transport mode, or fixture selection.

## Dependencies and integration points
It depends on the target sourced script, `common.sh`, `ovpn-cli`, fixture files, and the same root/networking requirements as the base test. It exercises the main test plan over TCP with symmetric peer IDs and symmetric notification fixtures.

## Risks and edge cases
Because the script uses `source`, any syntax error or early exit in the target script terminates this wrapper. The variable must be set before sourcing; moving it afterward would silently run the default scenario.

## Test signals
The test signals are exactly those of the sourced base script: KTAP plan/pass/fail lines, command wrapper failures, traffic checks, key/peer lifecycle checks, and notification fixture diffs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-symmetric-id-tcp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-symmetric-id.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-symmetric-id.sh

## Purpose
This thin OVPN selftest wrapper runs the symmetric peer-id UDP variant. It exists so kselftest can expose the mode as a separate `TEST_PROGS` entry while sharing the common implementation.

## Important APIs and data
The only behavior is setting `OVPN_SYMMETRIC_ID="1"` before sourcing `test.sh`. The script then executes `source test.sh` or `source test-close-socket.sh`, so all functions, traps, and KTAP reporting come from the sourced file.

## Control flow
Bash evaluates the variable assignment, sources the target test script in the same shell, and the sourced script immediately runs its staged test plan. There are no local functions or local cleanup handlers in this wrapper.

## State and persistence
State is inherited from the sourced test. The assignment changes environment-visible shell variables that affect peer setup, key algorithm choice, MTU, transport mode, or fixture selection.

## Dependencies and integration points
It depends on the target sourced script, `common.sh`, `ovpn-cli`, fixture files, and the same root/networking requirements as the base test. It keeps the default UDP transport while changing peer ID mapping and expected notifications.

## Risks and edge cases
Because the script uses `source`, any syntax error or early exit in the target script terminates this wrapper. The variable must be set before sourcing; moving it afterward would silently run the default scenario.

## Test signals
The test signals are exactly those of the sourced base script: KTAP plan/pass/fail lines, command wrapper failures, traffic checks, key/peer lifecycle checks, and notification fixture diffs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-symmetric-id.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-tcp.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-tcp.sh

## Purpose
This thin OVPN selftest wrapper runs the TCP transport variant. It exists so kselftest can expose the mode as a separate `TEST_PROGS` entry while sharing the common implementation.

## Important APIs and data
The only behavior is setting `OVPN_PROTO="TCP"` before sourcing `test.sh`. The script then executes `source test.sh` or `source test-close-socket.sh`, so all functions, traps, and KTAP reporting come from the sourced file.

## Control flow
Bash evaluates the variable assignment, sources the target test script in the same shell, and the sourced script immediately runs its staged test plan. There are no local functions or local cleanup handlers in this wrapper.

## State and persistence
State is inherited from the sourced test. The assignment changes environment-visible shell variables that affect peer setup, key algorithm choice, MTU, transport mode, or fixture selection.

## Dependencies and integration points
It depends on the target sourced script, `common.sh`, `ovpn-cli`, fixture files, and the same root/networking requirements as the base test. It reuses the main lifecycle with TCP listener/connect setup and TCP DATA_V2 tcpdump filters.

## Risks and edge cases
Because the script uses `source`, any syntax error or early exit in the target script terminates this wrapper. The variable must be set before sourcing; moving it afterward would silently run the default scenario.

## Test signals
The test signals are exactly those of the sourced base script: KTAP plan/pass/fail lines, command wrapper failures, traffic checks, key/peer lifecycle checks, and notification fixture diffs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-tcp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test.sh

## Purpose
`test.sh` is the main OVPN data-channel accelerator integration test. It validates namespace topology setup, tunnel traffic, LAN-behind-peer routing, optional floating transport addresses, throughput, key rollover, peer/key queries, deletion during traffic, stale-key deletion, timeout behavior, and YNL notification output.

## Important APIs and functions
- `ovpn_prepare_network` creates all namespaces, starts notification listeners, configures OVPN interfaces and veth underlay links, registers peers, and sets keepalive values.
- `ovpn_run_basic_traffic` starts tcpdump filters for OpenVPN DATA_V2 headers and sends baseline plus large-payload pings to each peer.
- `ovpn_run_lan_traffic` validates the extra LAN address behind peer1.
- `ovpn_run_float_mode` changes peer underlay addresses and verifies tunnel reachability after peer float.
- `ovpn_run_iperf` checks throughput with iperf3.
- `ovpn_run_key_rollover` adds secondary keys and swaps them on peers.
- `ovpn_run_queries` and `ovpn_query_peer_missing` validate successful and failing peer queries.
- `ovpn_run_peer_cleanup`, `ovpn_run_traffic_delete_peer`, `ovpn_run_key_cleanup`, and `ovpn_run_timeouts` exercise lifecycle cleanup and timeout notifications.
- `ovpn_run_notifications` compares captured YNL output against `json/peer*.json` fixtures selected by mode.

## Control flow
The script sources `common.sh`, installs EXIT and ERR traps, chooses a KTAP plan of 12 or 13 depending on `OVPN_FLOAT`, cleans old state, loads `ovpn`, then runs each stage with `ovpn_run_stage`. Wrapper scripts change behavior by setting `OVPN_PROTO`, `OVPN_ALG`, `OVPN_FLOAT`, `OVPN_SYMMETRIC_ID`, or `MTU` before sourcing this file.

## State and persistence
Runtime state includes namespaces `ovpn_peer0..N`, veth underlay links, OVPN interfaces `tun0..N`, routes, addresses, background socket-owning `ovpn-cli` processes, tcpdump and iperf children, temporary YNL JSON captures, peer/key state in the kernel, and optional changed underlay addresses for float mode. The EXIT trap removes this state.

## Dependencies and integration points
It depends on `common.sh`, `ovpn-cli`, `ip`, `ping`, `tcpdump`, `timeout`, `iperf3`, `jq`, `diff`, peer tables, JSON fixtures, YNL CLI, `data64.key`, and the `ovpn` module. It is the target sourced by most thin OVPN wrapper scripts.

## Risks and edge cases
The test is timing sensitive around YNL listener startup, tcpdump readiness, TCP listener setup, timeout sleeps, and background traffic during deletion. It normalizes notifications but still requires exact peer IDs, event names, delete reasons, and float remote addresses. TCP mode treats one peer deletion as non-fatal because protocol behavior can differ.

## Test signals
Passing output is a full KTAP run with all planned stages passing. Strong signals include tcpdump seeing both expected DATA_V2 peer IDs, pings succeeding before and after key rollover/float, missing peer query failing as expected, stale key deletion succeeding, timeout-generated delete notifications, and all JSON fixture diffs passing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/Makefile -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/Makefile

## Purpose
The packetdrill `Makefile` registers packetdrill scripts and their helper files with the kselftest framework.

## Important variables
- `TEST_INCLUDES` lists shared helpers required by packetdrill tests: `defaults.sh`, `ksft_runner.sh`, `set_sysctls.py`, and KTAP helpers.
- `TEST_PROGS := $(wildcard *.pkt)` makes every packetdrill script in the directory a test program.
- `include ../../lib.mk` delegates build/install/run mechanics to kselftest infrastructure.

## Control flow
There is no procedural logic beyond make expansion. At build or install time, `lib.mk` consumes `TEST_PROGS` and `TEST_INCLUDES`.

## State and persistence
The Makefile creates no runtime state. It controls which files are staged into the selftest output.

## Dependencies and integration points
It assumes packetdrill `.pkt` files in the same directory and helper scripts installed beside them. The actual runner is `ksft_runner.sh`, which invokes the external `packetdrill` binary.

## Risks and edge cases
Using `wildcard *.pkt` means new packetdrill scripts are automatically included, but accidentally staged or experimental `.pkt` files also become tests. Missing helper inclusion breaks installed-tree runs.

## Test signals
The Makefile's success signal is that kselftest lists and installs every `.pkt` script with the helper files required to execute them.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/config -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/config

## Purpose
The packetdrill `config` file lists kernel configuration requirements for TCP/IP packetdrill selftests.

## Important settings
It requires 1000 Hz timer granularity, IPv6, network namespaces, FIFO/FQ qdiscs, proc sysctl support, SYN cookies, CUBIC congestion control, TCP MD5 signatures, and TUN support.

## Control flow
The file is declarative and has no executable flow. It informs kselftest/environment checks about required kernel capabilities.

## State and persistence
No runtime state is created. The values describe kernel build configuration.

## Dependencies and integration points
The settings match assumptions in `defaults.sh` and `ksft_runner.sh`, including namespace isolation, TUN device setup, sysctl tuning, TCP Fast Open/cookies, IPv6 runs, and timing-sensitive packetdrill expectations.

## Risks and edge cases
Packetdrill tests can fail or skip unpredictably if a kernel lacks one of these capabilities, especially `CONFIG_HZ_1000`, network namespaces, qdisc support, or TCP feature support.

## Test signals
The downstream signal is packetdrill scripts passing for their selected IP versions under `ksft_runner.sh`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/defaults.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/defaults.sh

## Purpose
`defaults.sh` programs a deterministic TCP environment for packetdrill tests. It resets cached TCP metrics and applies production-like sysctl defaults that packetdrill scripts assume.

## Important APIs and settings
The script uses `ip tcp_metrics flush`, many `sysctl -q net.ipv4.*` writes, and `tc qdisc add dev tun0 root pfifo`. It sets receive/send buffer ranges, timestamps, SYN retry counts, F-RTO, SACK/DSACK, FACK off, reordering threshold, CUBIC, slow-start-after-idle off, RACK/TLP, TSO divisor, ECN off, pacing ratios, `tcp_notsent_lowat`, TCP Fast Open and a fixed Fast Open key, and SYN cookies.

## Control flow
Commands run sequentially and mostly suppress output. There are no functions or traps. The final qdisc override changes `tun0` from a potentially pacing FQ default to pfifo to avoid packetdrill timing failures.

## State and persistence
It mutates sysctls and qdisc state in the current network namespace. Under `ksft_runner.sh`, packetdrill is run inside `unshare -n`, so these changes are intended to be namespace-local.

## Dependencies and integration points
It depends on `ip`, `sysctl`, `tc`, a `tun0` device prepared by packetdrill, and kernel support for the named sysctls. Packetdrill `.pkt` tests rely on these values for stable TCP behavior.

## Risks and edge cases
If not run in an isolated network namespace, the sysctl changes can affect the host. Missing sysctls or qdisc support can fail commands. The pfifo override assumes `tun0` exists when this script is run.

## Test signals
Packetdrill timing and TCP behavior should become reproducible; failures often manifest later as packetdrill timing mismatches rather than direct output from this script.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/defaults.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/ksft_runner.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/ksft_runner.sh

## Purpose
`ksft_runner.sh` is the KTAP wrapper for packetdrill `.pkt` scripts. It runs each script under packetdrill for the requested IP version(s), translating results into kselftest pass/fail/xfail/skip output.

## Important APIs and data
- Sources `../../kselftest/ktap_helpers.sh`.
- `ip_args` maps `ipv4`, `ipv4-mapped-ipv6`, and `ipv6` to packetdrill command-line options, local/gateway/remote addresses, Fast Open cookies, and socket error cmsg constants.
- `KSFT_MACHINE_SLOW` adds `--tolerance_usecs=14000` and downgrades failures to expected failures via `ktap_test_xfail`.
- The script discovers requested IP versions by grepping `^--ip_version=` in the `.pkt` file; absent means run all three supported variants.

## Control flow
It requires exactly one script argument, skips all tests if `packetdrill` is not in `PATH`, computes packetdrill options, prints a KTAP header and plan, then loops over each selected IP version. Each run executes `unshare -n packetdrill ... $script` and records pass or fail/xfail.

## State and persistence
Packetdrill runs in a fresh network namespace for each IP version, limiting sysctl, interface, and qdisc state to that run. The runner itself persists no files.

## Dependencies and integration points
It depends on Bash associative arrays, `packetdrill`, `unshare`, KTAP helpers, and packetdrill scripts that may include `defaults.sh` or `set_sysctls.py`. The `-D` definitions provide constants consumed by `.pkt` scripts.

## Risks and edge cases
The grep-based IP-version parser accepts only zero or one explicit `--ip_version=ipv4`/`ipv6`; multiple declarations are treated as unsupported. Slow-machine mode can hide real regressions as xfails. Packetdrill must be installed outside the kernel tree.

## Test signals
A missing packetdrill binary produces a KTAP skip-all. Otherwise each IP version emits one KTAP pass/fail/xfail line, and the script exits through `ktap_finished`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/ksft_runner.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/set_sysctls.py -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/set_sysctls.py

## Purpose
`set_sysctls.py` is a packetdrill helper that changes proc/sysctl files and writes a restoration shell script for the packetdrill process.

## Important APIs and functions
- Reads `PACKETDRILL_PID` from the environment to name `/tmp/sysctl_restore_${PACKETDRILL_PID}.sh`.
- Iterates over command-line arguments of the form `<proc-file>=<val>`.
- Uses `subprocess.check_output(['cat', path])` to capture current values and writes `echo "old" > path` commands to the restore script.
- Uses `os.system('echo "new" > path')` to apply the requested value and then marks the restore script executable.

## Control flow
At import/execution time it opens the restore file, writes a bash shebang, processes all arguments in order, applies new values immediately, and chmods the restore script.

## State and persistence
It mutates proc files in the current namespace and persists a temporary restore script under `/tmp`. Packetdrill scripts can run that restore script at the end using their parent PID convention.

## Dependencies and integration points
It depends on Python 3, `PACKETDRILL_PID`, readable/writable proc files, `/tmp`, `cat`, shell redirection, and packetdrill scripts that know to call the restore file. It complements `defaults.sh` for per-test sysctl changes.

## Risks and edge cases
Arguments are split on every `=`, so values containing `=` are unsupported. `os.system` with interpolated paths/values assumes trusted packetdrill input. Missing `PACKETDRILL_PID` raises a KeyError before any friendly error. Restore scripts are left in `/tmp` if tests do not execute them or clean up.

## Test signals
The main signal is subsequent packetdrill behavior under modified sysctls. A restore script at `/tmp/sysctl_restore_${PACKETDRILL_PID}.sh` is evidence that previous values were captured.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/set_sysctls.py -->
