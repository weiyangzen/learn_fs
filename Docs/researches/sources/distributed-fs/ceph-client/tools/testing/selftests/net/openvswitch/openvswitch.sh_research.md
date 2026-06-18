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
