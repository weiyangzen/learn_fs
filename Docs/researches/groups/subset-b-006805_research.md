# subset-b-006805

Grouped research for Linux BPF selftests under `tools/testing/selftests/bpf/prog_tests`, focused on tc/tcx/netkit attach behavior, TC redirect helpers, TCP sockops/header-option behavior, bpffs, BTF, BPF allocator, BPRM, syscall macro, and SMC policy tests.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_bpf.c

Purpose: `tc_bpf.c` validates libbpf's classic TC BPF helper API around `bpf_tc_hook_create()`, `bpf_tc_attach()`, `bpf_tc_query()`, and `bpf_tc_detach()` on the loopback device. It checks normal attach/query/replace/detach behavior for ingress and egress hooks, API input validation, interaction with unsupported `BPF_TC_CUSTOM`, and loading a TC classifier BPF object without full root-style capabilities.

Important APIs/types/functions: `TEST_DECLARE_OPTS()` creates many `bpf_tc_opts` variants used to probe invalid and valid option combinations. `test_tc_bpf_basic()` loads program info, attaches a classifier with handle/priority/prog fd, verifies libbpf fills `prog_id`, replaces the filter, queries it back, and detaches it. `test_tc_bpf_api()` is the negative-coverage core for null hooks/options, invalid ifindexes, invalid attach points, bad parents, invalid detach/query flags, priority overflow, missing handle/priority, and allowed attach cases where the kernel/libbpf can allocate missing handle or priority. `tc_bpf_root()` sequences real hook creation and basic/API tests. `tc_bpf_non_root()` uses `cap_enable_effective()` and `cap_disable_effective()` to verify load behavior with `CAP_BPF` and `CAP_NET_ADMIN` while `CAP_SYS_ADMIN` and `CAP_PERFMON` are disabled. `test_tc_bpf()` exposes the two subtests to the selftest harness.

Control flow: the root subtest opens and loads `test_tc_bpf.skel.h`, obtains the `cls` program fd, creates an ingress hook if needed, checks that `BPF_TC_CUSTOM` hook operations return `-EOPNOTSUPP`, then runs `test_tc_bpf_basic()` over ingress, recreated ingress, and egress hooks. It ends by running the invalid-API matrix and destroying any created qdisc hook. The non-root subtest temporarily adjusts effective capabilities, loads the same skeleton, and restores capabilities. Cleanup paths reset `hook.attach_point` to both ingress and egress before destroying qdiscs to avoid leaving loopback state behind.

State and persistence: the file mutates only transient test state: loopback clsact qdisc/filter state, skeleton BPF object lifetime, `bpf_tc_opts` output fields, and process effective capabilities. There is no persistent data, but failed cleanup can leave TC hooks/filters on `lo` or altered process capabilities until the process exits. The BPF program state comes from generated skeleton maps/programs, and program ids are read from kernel state through `bpf_prog_get_info_by_fd()`.

Dependencies: depends on `test_progs.h`, `<linux/pkt_cls.h>`, `cap_helpers.h`, generated `test_tc_bpf.skel.h`, libbpf TC APIs, Linux clsact/TC support, BPF scheduler-classifier program loading, loopback ifindex 1, and enough privileges/capabilities for TC manipulation.

Integration points: this is a selftest entry point invoked by the generated BPF test runner. It tests libbpf's public TC API contract against the kernel TC subsystem and capability model, complementing newer TCX tests in `tc_links.c` and `tc_opts.c`.

Risks: the test assumes loopback ifindex is 1 and that no unrelated filter state interferes with the same handle/priority. Because it intentionally manipulates effective capabilities, early failures in capability restore paths could affect later tests in the same process. Negative tests encode exact errno expectations, so libbpf/kernel error-order changes may look like regressions even if behavior remains rejected. `system` is not used here, which keeps shell risk low compared with nearby TC tests.

Test signals: success is signaled by `ASSERT_OK`, `ASSERT_EQ`, and `ASSERT_OK_PTR` across root and non-root subtests. High-value assertions include `prog_id` propagation after attach/query, replace mode preserving handle/priority, `-EOPNOTSUPP` for custom hooks, `-EINVAL` for malformed hooks/options, successful attach with missing handle or priority, and successful skeleton load under the reduced-capability scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_change_tail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_change_tail.c

Purpose: `tc_change_tail.c` is a focused TCX selftest for a BPF program that calls `bpf_skb_change_tail()` or equivalent skb tail adjustment logic from a TC classifier. It sends small UDP payloads over a local socket pair and checks the BPF-side return code for successful and invalid tail changes.

Important APIs/types/functions: `test_tc_change_tail()` is the only exported test. It uses `LIBBPF_OPTS(bpf_tcx_opts, tcx_opts)`, generated `test_tc_change_tail.skel.h`, `bpf_program__attach_tcx()`, `create_pair()`, `xsend()`, `recv()`, and the skeleton data variable `change_tail_ret`. `LO_IFINDEX` fixes the attach target to loopback ifindex 1.

Control flow: the test opens and loads the skeleton, attaches `skel->progs.change_tail` to loopback through a TCX link, creates an IPv4 UDP socket pair, then sends four payload patterns. `"Tr"` and `"G"` are expected to pass and leave `change_tail_ret` as 0. `"E"` and `"Z"` are expected to reach paths where the helper returns `-EINVAL`. Each send is paired with a receive to ensure traffic actually traversed the hook. File descriptors are closed after the packet checks, and skeleton destruction tears down the link.

State and persistence: runtime state is limited to the TCX link stored in `skel->links.change_tail`, socket pair descriptors, the transient packet buffers, and the skeleton data field updated by BPF. There is no filesystem persistence. A failure before skeleton destruction could briefly leave a TCX program attached to loopback until process teardown.

Dependencies: depends on generated `test_tc_change_tail.skel.h`, `socket_helpers.h`, libbpf TCX attach support, loopback TCX support, Linux UDP sockets, and the kernel BPF helper semantics for skb tail modification.

Integration points: the userspace test is paired with a BPF program in the selftest build and is invoked by the BPF test harness as `test_tc_change_tail`. It integrates socket-helper traffic generation with TCX attachment to validate data-plane helper behavior.

Risks: the test is compact but assumes loopback ifindex 1 and that local UDP traffic hits the TCX hook in the expected direction. It does not explicitly initialize `c1`/`p1` to invalid values before `create_pair()`, so cleanup after a failed pair creation relies on the current control path that skips `close()`. Exact expected helper errno values may change if kernel validation order changes.

Test signals: pass criteria are successful skeleton load/attach, successful socket-pair creation, exact send/receive byte counts for 2-byte and 1-byte payloads, and `change_tail_ret` equal to either 0 or `-EINVAL` for the intended payload classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_change_tail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_helpers.h

Purpose: `tc_helpers.h` provides small inline helpers shared by TCX and netkit BPF selftests. It centralizes program-count queries, TCX link ifindex extraction, and skeleton BSS reset logic for generated `test_tc_link` skeletons.

Important APIs/types/functions: `ifindex_from_link_fd()` calls `bpf_link_get_info_by_fd()` and returns `link_info.tcx.ifindex`, using `ASSERT_OK` to report failures. `__assert_mprog_count()` wraps `bpf_prog_query()` for a target attach type and asserts both the returned count and zero errno. `assert_mprog_count()` applies that query to the default `loopback` ifindex. `assert_mprog_count_ifindex()` makes the ifindex explicit for veth/netkit tests. `tc_skel_reset_all_seen()` zeroes the skeleton BSS so packet-seen flags start fresh.

Control flow: callers use the count helpers before attachment, after attachment/replacement, and after cleanup to prove kernel multi-program state matches the expected number of attached programs. `ifindex_from_link_fd()` is used after device deletion to verify a link's TCX ifindex becomes 0. `tc_skel_reset_all_seen()` is typically called before injecting ping/ICMP traffic so subsequent BSS flags prove the current packet traversal rather than a previous packet.

State and persistence: the header does not own persistent state. It reads kernel link/query state and writes only to a skeleton's BSS memory. The `loopback` default is a macro with fallback value 1, so state is coupled to a conventional loopback ifindex unless a source file defines `loopback` first.

Dependencies: depends on `test_progs.h`, libbpf BPF link/query APIs, `struct bpf_link_info` with TCX fields, and generated `struct test_tc_link` definitions in translation units that include the header.

Integration points: included by `tc_links.c`, `tc_opts.c`, `tc_netkit.c`, and similar TCX selftests. It creates a shared assertion vocabulary for program counts and seen-flag resets across link-based and fd-based attach tests.

Risks: the header assumes `struct test_tc_link` is visible when `tc_skel_reset_all_seen()` is compiled. It also assumes that querying with `prog_ids == NULL` and `count` pointer is sufficient for every tested attach type. The fallback `loopback 1` can hide portability issues on unusual test environments where loopback ifindex differs.

Test signals: this header's behavior is indirectly tested whenever the including selftests assert program counts before and after attach/detach and when BSS flags are reset before packet injection. A broken helper would cause widespread count or stale-BSS assertion failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_links.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_links.c

Purpose: `tc_links.c` validates TCX attachment through persistent `struct bpf_link` objects. It covers basic ingress/egress attachment, ordering with before/after relative positions, revision checks, link update/detach, invalid option combinations, prepend/append semantics, device teardown behavior, and coexistence with classic TC filters/qdiscs.

Important APIs/types/functions: each `test_ns_tc_links_*` function is a selftest subentry. Core APIs are `bpf_program__attach_tcx()`, `bpf_link__fd()`, `bpf_link__update_program()`, `bpf_link__detach()`, `bpf_prog_query_opts()`, `bpf_program__set_expected_attach_type()`, and classic `bpf_tc_hook_create()/bpf_tc_attach()/bpf_tc_detach()`. The file uses `test_tc_link.skel.h` programs `tc1` through `tc6`, BSS flags such as `seen_tc1`, helpers from `tc_helpers.h`, and rtnetlink helpers for qdisc replacement. `qdisc_replace()` constructs `RTM_NEWQDISC` messages for ingress/clsact and optional block binding.

Control flow: `test_ns_tc_links_basic()` attaches one ingress and one egress link to loopback, queries program/link ids and revisions, then pings loopback to verify BPF execution. `test_tc_links_before_target()` and `test_tc_links_after_target()` load four programs for either ingress or egress and use relative fds/ids plus `BPF_F_LINK` to assert exact execution/query ordering. `test_tc_links_revision_target()` uses `expected_revision` to force an attach failure with stale revision and success with current revision. `test_tc_chain_classic()` and `test_tc_chain_mixed()` check TCX behavior beside old-style TC filters. `test_tc_links_replace_target()` validates disallowed replace flag combinations and the supported `bpf_link__update_program()` path. `test_tc_links_invalid_target()` enumerates malformed relative fd/id/link flag combinations before confirming one valid case. Prepend and append helpers check implicit head/tail insertion. Device cleanup tests attach several links to a veth, delete the netdevice, then confirm link info reports ifindex 0. `test_ns_tc_links_ingress()` stresses teardown ordering with an ingress qdisc. `test_ns_tc_links_dev_chain0()` reproduces a block/qdisc replacement scenario with a deliberate RCU wait. `test_ns_tc_links_dev_mixed()` combines TCX links and classic TC on a disposable veth before device deletion.

State and persistence: state is mostly kernel TCX multi-program arrays attached to loopback or temporary veth devices, classic TC qdiscs/filters, generated skeleton BSS flags, link ids, program ids, and query revisions. Temporary devices `tcx_opts1/tcx_opts2` and `foo/bar` are created and deleted with shell commands. The code expects skeleton destruction to close links and drop TCX state; explicit `ip link del` and qdisc destroy paths clean network state.

Dependencies: depends on libbpf's TCX link APIs, kernel TCX support, rtnetlink, `ip`, `tc`, loopback, veth, ping, generated `test_tc_link.skel.h`, `netlink_helpers.h`, `tc_helpers.h`, and privilege to manipulate network devices/qdiscs.

Integration points: this file is part of the namespaced TCX selftest suite and complements `tc_opts.c`, which exercises the fd-based `BPF_PROG_ATTACH` path. It integrates with the selftest harness via `test_ns_*` naming, generated BPF object code, and command-line networking tools.

Risks: tests are sensitive to exact revision increments, program ordering, and errno behavior. They assume no unrelated TC state exists on loopback and create fixed device names, which can collide with stale state from failed runs. Several cleanup paths execute shell commands and continue with assertions even if intermediate setup failed. The dev-chain0 test uses a 5-second heuristic wait to expose an RCU-related regression, which is intentionally timing-sensitive. Exact interaction with classic TC filters can vary across kernels lacking the tested compatibility behavior.

Test signals: key signals include query counts/revisions/prog ids/link ids, BSS seen flags after `ping`, successful and failed `bpf_program__attach_tcx()` calls for specific options, `bpf_link__update_program()` preserving link id while changing program id, link ifindex becoming 0 after device deletion, and final `assert_mprog_count(..., 0)` cleanup checks for every target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_links.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_netkit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_netkit.c

Purpose: `tc_netkit.c` tests BPF attachment to netkit devices through both `bpf_program__attach_netkit()` link APIs and fd-based `bpf_prog_attach_opts()`. It validates primary/peer attach points, L2 and L3 netkit modes, query semantics, peer-device access restrictions, packet-type propagation, neighbor behavior, scrub settings, socket mark/priority handling, and configured headroom/tailroom.

Important APIs/types/functions: `create_netkit()` builds an `RTM_NEWLINK` netlink request with `IFLA_INFO_KIND=netkit`, netkit mode/policy/scrub attributes, optional headroom/tailroom, and peer setup. `__send_icmp()` creates an ICMP datagram socket bound to `nk1`, sets `SO_MARK` and `SO_PRIORITY`, and sends an echo packet. `serial_test_tc_netkit_basic()` covers one primary and one peer link. `serial_test_tc_netkit_multi_links_target()` covers link-based relative ordering for L2/L3 and primary/peer targets. `serial_test_tc_netkit_multi_opts_target()` covers fd-based attach ordering. `serial_test_tc_netkit_device()` verifies that the visible peer interface cannot be queried/attached directly for netkit targets. `serial_test_tc_netkit_neigh_links_target()`, `serial_test_tc_netkit_pkt_type_mode()`, and `serial_test_tc_netkit_scrub_type()` cover neighbor, packet type, and scrub/room behavior.

Control flow: each serial subtest creates a netkit pair named `nk1`/`nk0`, configures namespace `foo`, addresses, link state, and optionally keeps both ends in the same namespace. Skeleton programs are opened with expected attach types set to `BPF_NETKIT_PRIMARY`, `BPF_NETKIT_PEER`, or `BPF_TCX_INGRESS`, then loaded and attached. The tests query attached program/link ids and revisions, send ICMP traffic, and assert BSS flags such as `seen_tc1`, `seen_tc2`, `seen_eth`, `seen_tc7`, `seen_host`, `seen_mcast`, `mark`, `prio`, `headroom`, and `tailroom`. Cleanup destroys the skeleton, checks program counts are zero, deletes the primary netkit device, and deletes namespace `foo`.

State and persistence: transient state includes created netkit devices, namespace `foo`, assigned IPv4 addresses, optional MAC address changes, sysctl `ping_group_range`, socket mark/priority metadata, TC/netkit BPF link state, and skeleton BSS fields. No persistent files are written. Because fixed device and namespace names are used, stale state from a previous crash could affect the next run.

Dependencies: depends on kernel netkit device support, netkit rtnetlink UAPI attributes, libbpf netkit attach/query support, `ip`, namespace privileges, ICMP datagram sockets, `write_sysctl()`, generated `test_tc_link.skel.h`, and helpers from `netlink_helpers.h` and `tc_helpers.h`.

Integration points: this file sits at the boundary between BPF selftests and the netkit virtual-device driver. It verifies that netkit-specific attach points participate in the same multi-program query/revision machinery as TCX while preserving netkit-specific packet metadata and peer restrictions.

Risks: tests are serial because they reuse global names `nk0`, `nk1`, and `foo`. The code assumes netkit support is present; unsupported kernels will fail early rather than gracefully skip unless the surrounding harness handles it. Several assertions rely on packet type and neighbor behavior for L2 versus L3 modes, which can be sensitive to route/neigh setup and ARP timing. `write_sysctl("/proc/sys/net/ipv4/ping_group_range", "0 0")` changes a namespace/system knob for ICMP socket permissions. Cleanup can fail if the netkit primary was not created but `destroy_netkit()` still runs.

Test signals: pass criteria include exact program/link query results, revision increments, visible execution flags after ICMP, expected `-EACCES` when querying peer ifindex directly, failed attachment to peer ifindex, L3 rejection of MAC address setting, L2/L3 differences for neighbor and Ethernet visibility, packet type flags being observed by a TCX ingress program on the peer, and scrub mode controlling mark/priority preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_netkit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_opts.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_opts.c

Purpose: `tc_opts.c` is the fd-based counterpart to the TCX link tests. It validates `bpf_prog_attach_opts()`, `bpf_prog_detach_opts()`, and `bpf_prog_query_opts()` for `BPF_TCX_INGRESS` and `BPF_TCX_EGRESS`, including ordering, replacement, detach-by-position, stale revisions, maximum program count, mixed link/fd attachment, and direct `BPF_PROG_QUERY` syscall behavior.

Important APIs/types/functions: the main subtests are `test_ns_tc_opts_basic`, `before`, `after`, `revision`, `chain_classic`, `replace`, `invalid`, `prepend`, `append`, `dev_cleanup`, `mixed`, `demixed`, `detach`, `detach_before`, `detach_after`, `delete_empty`, `chain_mixed`, `max`, `query`, and `query_attach`. They use generated `test_tc_link.skel.h`, helpers from `tc_helpers.h`, `bpf_prog_attach_opts`, `bpf_prog_detach_opts`, `bpf_prog_query_opts`, `bpf_tc_hook_create`, `bpf_tc_attach`, raw `syscall(__NR_bpf, BPF_PROG_QUERY, ...)`, and a local `generate_dummy_prog()` that loads a minimal `BPF_PROG_TYPE_SCHED_CLS` program.

Control flow: most target helpers run twice, once for ingress and once for egress. Basic attach adds one program per direction and verifies ping-observed BSS flags. Before/after/prepend/append attach four programs and query exact order and revision. Revision tests use `expected_revision` to trigger `-ESTALE` and then succeed. Replace tests replace programs with `BPF_F_REPLACE` and `replace_prog_fd`, including relative before placement and invalid replace combinations. Invalid tests enumerate rejected flag and relative fd/id combinations. Detach tests remove head/tail/specific relative positions using `BPF_F_BEFORE` and `BPF_F_AFTER`. Mixed/demixed tests combine fd-attached programs with `bpf_program__attach_tcx()` links and prove replacements against link-owned entries are rejected or busy. Max tests attach 63 dummy programs to a veth and assert the 64th fails with `-ERANGE`. Query tests compare libbpf query behavior with raw `union bpf_attr` query behavior for null arrays, short arrays, long arrays, and invalid flags.

State and persistence: state is transient TCX multi-program state on loopback and disposable veth devices, skeleton BSS flags, program ids, revision counters, attach flags, and query arrays. The max test creates many anonymous BPF program fds and closes them after attachment so kernel attachment references are tested independently from userspace fd lifetime. There is no file persistence. Temporary devices `tcx_opts1/tcx_opts2` can be left behind if cleanup is interrupted.

Dependencies: depends on TCX kernel support, libbpf attach/detach/query option structs, raw BPF syscall support for `BPF_PROG_QUERY`, generated `test_tc_link.skel.h`, `ip`, veth, ping, classic TC hook support, and sufficient network/BPF privileges.

Integration points: this file directly exercises the kernel `BPF_PROG_ATTACH`, `BPF_PROG_DETACH`, and `BPF_PROG_QUERY` ABI for TCX attach types. It complements `tc_links.c` by checking the non-link attachment path and mixed ownership rules between link-backed and fd-backed programs.

Risks: the file encodes many exact errno values (`-ESTALE`, `-EEXIST`, `-ERANGE`, `-ENOENT`, `-EBUSY`, `-EINVAL`) and exact revision increments, so changes in validation order can break the test while still rejecting invalid input. Fixed loopback/veth names can collide with stale resources. Some error cleanup labels in the device cleanup helper detach from `loopback` instead of the created ifindex, though the success path jumps directly to device deletion and skeleton destruction. The maximum-program test is resource-heavy compared with nearby tests because it loads 64 small programs per mode/flag scenario.

Test signals: strong signals are exact query order, revision and count checks after each operation, BSS seen flags after ping, expected stale-revision and invalid-option failures, direct syscall `ENOSPC` with truncated query arrays while returning partial ids/count, direct syscall acceptance of null id arrays, and final zero-count assertions after detach or skeleton destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_opts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_redirect.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_redirect.c

Purpose: `tc_redirect.c` builds an isolated multi-namespace network lab to validate TC BPF redirect helpers and skb timestamp behavior. It tests `bpf_redirect_peer()`, `bpf_redirect_neigh()`, a `bpf_fib_lookup()` plus redirect-neigh path, delivery-time propagation through TC programs, and L3 peer redirect through a TUN relay, using both veth and netkit device modes where applicable.

Important APIs/types/functions: namespace helpers are `netns_setup_namespaces()`, `netns_setup_links_and_routes()`, and `netns_setup_namespaces_nofail()`. `create_netkit()` creates L3 netkit pairs via rtnetlink. TC attach helpers are `qdisc_clsact_create()`, `xgress_filter_add()`, `netns_load_bpf()`, and `netns_load_dtime_bpf()`. Connectivity helpers are `test_tcp()`, `test_ping()`, `test_connectivity()`, `set_forwarding()`, `test_inet_dtime()`, `snd_tstamp()`, `rcv_tstamp()`, and `wait_netstamp_needed_key()`. Top-level behavior lives in `test_tc_redirect_peer()`, `test_tc_redirect_neigh()`, `test_tc_redirect_neigh_fib()`, `test_tc_redirect_dtime()`, `test_tc_redirect_peer_l3()`, and threaded `test_tc_redirect_run_tests()`.

Control flow: the test thread first deletes any stale namespaces, then each `RUN_TEST()` creates `ns_src`, `ns_fwd`, and `ns_dst`, builds either veth or netkit links named `src/src_fwd` and `dst/dst_fwd`, moves endpoints into namespaces, assigns IPv4/IPv6 host routes, and seeds neighbors for veth mode. Redirect tests open the relevant skeleton in `ns_fwd`, fill rodata ifindex values, load programs, attach TC ingress redirect programs and egress checker programs to forward-facing devices, toggle forwarding as needed, then run TCP and ping for IPv4 and IPv6 from source to destination. Delivery-time tests additionally attach host and forward namespace TC programs at different priorities, create sockets with timestamp options and TXTIME, and verify BPF-side counters/errors. The L3 peer test creates TUN devices in source and forward namespaces, forks a relay loop, redirects packets from `tun_fwd` to destination, adjusts routes/neighbors, then runs connectivity. Namespaces are deleted after each subtest.

State and persistence: transient state includes named network namespaces, veth/netkit pairs, TUN devices, routes, neighbor entries, forwarding sysctls inside `ns_fwd`, TC clsact qdiscs/filters, a forked relay process, socket timestamp state, skeleton BSS counters, and file descriptors. No persistent repository files are written. The test intentionally runs in a separate pthread because `open_netns()` can use mount namespace changes that should not leak to other tests.

Dependencies: depends on `ip`, ping utilities selected by `ping_command()`, veth, netkit, `/dev/net/tun`, TUNSETIFF, network namespace privileges, TC clsact support, generated skeletons `test_tc_neigh_fib`, `test_tc_neigh`, `test_tc_peer`, and `test_tc_dtime`, libbpf TC APIs, IPv4/IPv6 forwarding sysctls, socket timestamp/TXTIME APIs, and pthread/fork/wait support.

Integration points: this file is a broad integration selftest across TC BPF programs and the Linux networking stack. It links BPF redirect helper behavior to real TCP/ping data-plane traffic, FIB and neighbor lookup, netkit/veth device semantics, skb delivery-time metadata, and namespace isolation used throughout the BPF selftests.

Risks: the test is environment-sensitive: missing TUN, disabled IPv6, absent netkit support, unavailable ping tools, insufficient privileges, or stale namespaces/devices can fail setup. Fixed namespace/device names can collide with previous failed runs. Delivery-time assertions depend on timestamping being enabled promptly, so `wait_netstamp_needed_key()` retries to avoid a kernel lazy-enable race. The TUN relay child loops forever until killed; cleanup must terminate it. Exact route/neigh setup differs for veth and netkit, and forwarding toggles must remain namespace-scoped. Failure before cleanup can leave namespaces, routes, qdiscs, or relay processes behind.

Test signals: pass signals include successful namespace/link setup, TC qdisc/filter attachment on expected ifindexes, TCP and ping reachability for IPv4/IPv6 under redirect-peer, redirect-neigh, and FIB paths, zero checker drops implied by successful connectivity, nonzero delivery-time counters for expected program stages, zero BPF-side dtime error counters, valid receive timestamps within a bounded age, and clean namespace deletion after each subtest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_redirect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcp_custom_syncookie.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcp_custom_syncookie.c

Purpose: `tcp_custom_syncookie.c` validates a TC ingress BPF program that handles custom TCP syncookie logic for both IPv4 and IPv6 loopback TCP connections. It ensures the program sees both SYN and final ACK traffic and that the connection remains usable for bidirectional data transfer.

Important APIs/types/functions: `test_tcp_custom_syncookie_case` describes address family, socket type, address, and subtest name. `setup_netns()` unshares a fresh net namespace, brings loopback up, and enables ECN through `/proc/sys/net/ipv4/tcp_ecn`. `setup_tc()` creates a clsact hook on `lo` and attaches `skel->progs.tcp_custom_syncookie` to ingress. `transfer_message()` sends and receives `"Hello World"`. `create_connection()` starts a server, connects a client, accepts the child socket, and verifies traffic both directions. `test_tcp_custom_syncookie()` orchestrates setup, skeleton loading, TC attachment, per-family subtests, BSS flag reset, and cleanup.

Control flow: after namespace and TC setup, the top-level test iterates over IPv4 and IPv6 test cases. For each subtest it clears `handled_syn` and `handled_ack` in skeleton BSS, creates a TCP connection to the loopback server, transfers a small message client-to-server and server-to-client, then asserts both flags became true. At the end it deletes the loopback clsact qdisc through `tc qdisc del dev lo clsact` and destroys the skeleton.

State and persistence: state is limited to a process-local network namespace, loopback qdisc/filter state, TCP ECN sysctl in that namespace, server/client sockets, and BSS flags. No files are persisted. Namespace unshare confines link and sysctl changes to the test process/thread context.

Dependencies: depends on generated `test_tcp_custom_syncookie.skel.h`, TC clsact support, libbpf TC APIs, `ip`, `tc`, loopback IPv4/IPv6 TCP, ECN sysctl availability, and `network_helpers.h` server/connect helpers.

Integration points: combines TC ingress BPF with normal TCP socket-helper connections. The BPF side must parse SYN/ACK paths correctly while preserving TCP connection semantics visible to userspace.

Risks: the test calls `unshare(CLONE_NEWNET)` in the current thread, so it must be run in a context where later tests are not harmed by namespace change. It assumes IPv6 loopback works inside the namespace. Cleanup uses `system("tc qdisc del dev lo clsact")` without checking its return. If `setup_tc()` fails after hook creation but before attach, qdisc cleanup depends on later top-level paths.

Test signals: success is demonstrated by skeleton load, clsact hook creation and TC attach, valid TCP connections for IPv4 and IPv6, exact send/receive message length and content, and BSS flags `handled_syn` and `handled_ack` both true after each connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcp_custom_syncookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcp_estats.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcp_estats.c

Purpose: `tcp_estats.c` is a smoke test that verifies the `test_tcp_estats.bpf.o` tracepoint BPF object can be loaded as a `BPF_PROG_TYPE_TRACEPOINT` program. It does not exercise runtime traffic; its purpose is loader/verifier coverage for the compiled object.

Important APIs/types/functions: `test_tcp_estats()` calls `bpf_prog_test_load()` with file path `./test_tcp_estats.bpf.o`, requested type `BPF_PROG_TYPE_TRACEPOINT`, output `struct bpf_object *obj`, and output program fd. On success it closes the object with `bpf_object__close()`.

Control flow: the function attempts a single load. If `ASSERT_OK(err, "")` fails, it returns immediately. If load succeeds, closing the object releases the program fd and associated BPF resources.

State and persistence: no persistent state is created. Kernel BPF object/program state exists only for the lifetime of `obj` and is destroyed by `bpf_object__close()`.

Dependencies: depends on the selftest build placing `test_tcp_estats.bpf.o` in the current working directory, libbpf's test loader, tracepoint BPF program support, and a kernel verifier accepting the object.

Integration points: this is a minimal userspace harness for a separate BPF object. It integrates with the selftest runner mainly as a build/verifier regression test.

Risks: the relative object path makes the test sensitive to runner working directory. Because the assertion name is empty, diagnostics are less descriptive than nearby tests. The test does not attach to a tracepoint or check maps/output, so it will not catch runtime semantic regressions after load succeeds.

Test signals: the sole substantive signal is `bpf_prog_test_load()` returning 0 for `test_tcp_estats.bpf.o`; object close should complete without additional assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcp_estats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcp_hdr_options.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcp_hdr_options.c

Purpose: `tcp_hdr_options.c` verifies BPF sockops TCP header option parsing and writing across normal establishment, non-experimental option kind handling, syncookie, TCP Fast Open, FIN exchange, and miscellaneous callback behavior. It drives real IPv6 loopback TCP connections inside fresh network namespaces and checks skeleton BSS/maps for expected header-option data and callback stages.

Important APIs/types/functions: global expected structures include `bpf_test_option` values for passive/active establish and FIN paths plus `hdr_stg` values for active/passive stage state. `sk_fds_connect()` creates a server, active client, passive accepted socket, and optional Fast Open data path. `check_hdr_opt()`, `check_hdr_stg()`, `check_error_linum()`, and `check_hdr_and_close_fds()` validate BPF-observed state and close sockets. `prepare_out()` seeds BPF outgoing option templates. `reset_test()` clears BSS expectations and deletes line-error map entries. Scenario functions are `simple_estab()`, `no_exprm_estab()`, `syncookie_estab()`, `fastopen_estab()`, `fin()`, and `misc()`. `test_tcp_hdr_options()` loads `test_tcp_hdr_options` and `test_misc_tcp_hdr_options` skeletons, joins cgroup `/tcpbpf-hdr-opt-test`, and runs each scenario after `unshare(CLONE_NEWNET)`.

Control flow: each scenario sets expected incoming options and outgoing options, adjusts sysctls such as `tcp_syncookies` or `tcp_fastopen`, attaches the relevant cgroup sockops program, opens a TCP connection, optionally transfers data or Fast Open payload, shuts down both ends, checks inherited callback flags, checks per-socket header stage map entries, checks BSS-recorded parsed options, verifies no BPF line errors were recorded, and destroys the cgroup link. `misc()` uses a separate skeleton to count SYN, data, pure ACK, FIN, hardware timestamp, and TCP_NODELAY-related rejection behavior.

State and persistence: state includes process network namespace, loopback state, cgroup fd/link attachments, TCP sysctls in the namespace, skeleton BSS data, maps `hdr_stg_map` and `lport_linum_map`, sockets, and expected global structs. The test clears BSS/map state between scenarios. There is no file persistence. Because each subtest unshares the network namespace, sysctl changes should not persist outside that subtest context.

Dependencies: depends on generated `test_tcp_hdr_options.skel.h`, `test_misc_tcp_hdr_options.skel.h`, shared `test_tcp_hdr_options.h`, cgroup sockops attach support, IPv6 loopback TCP, TCP Fast Open and syncookie sysctls, `network_helpers.h`, and BPF helpers for parsing/writing TCP header options.

Integration points: this file links userspace TCP connection scenarios to BPF sockops programs attached to a test cgroup. It verifies the userspace-visible contract for BPF TCP header options through maps/BSS and real socket state transitions.

Risks: test behavior depends on TCP sysctl availability and namespace isolation. Fast Open without a cookie is enabled with a magic sysctl value, which can be kernel-version sensitive. Pure ACK count is allowed to be 1 or 2 because delayed ACK timing varies. The test uses globals for skeletons/map fds/expectations, so scenarios are intentionally sequential and require `reset_test()` to avoid cross-test contamination. Failure before link destruction may leave a cgroup BPF link live until skeleton teardown.

Test signals: pass signals include matching `inherit_cb_flags`, exact `bpf_test_option` structs for passive/active establish and FIN paths, expected `hdr_stg` flags for active/passive/resend/syncookie/fastopen, no entries in the line-error map, correct Fast Open data receipt, expected syncookie resend behavior, misc counts for SYN/data/ACK/FIN, zero hardware timestamp count, and true TCP_NODELAY rejection checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcp_hdr_options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcp_rtt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcp_rtt.c

Purpose: `tcp_rtt.c` validates that a BPF sockops program can read TCP RTT-related fields from `bpf_tcp_sock` and store them in socket local storage during connection establishment and after data delivery.

Important APIs/types/functions: `struct tcp_rtt_storage` mirrors values stored by the BPF program: invocation count, duplicate SACK count, delivered counts, ECN-delivered count, retransmits, measured RTT, and smoothed RTT. `send_byte()` writes one byte. `wait_for_ack()` polls `TCP_INFO.tcpi_unacked` until the byte is acknowledged. `verify_sk()` reads `socket_storage_map` with the client fd key and checks expected counters plus nonzero RTT fields. `run_test()` loads `tcp_rtt.skel.h`, attaches `_sockops` to a cgroup, opens a client connection to a server fd, verifies initial SYN-ACK state, sends a byte, waits for ACK, and verifies updated state. `test_tcp_rtt()` creates cgroup `/tcp_rtt` and a TCP server.

Control flow: the top-level test joins a cgroup, starts an IPv4 TCP server, and calls `run_test()`. The BPF program is attached as `BPF_CGROUP_SOCK_OPS`. After `connect_to_fd()`, `verify_sk()` expects one invocation and delivered count 1. After sending one byte and waiting for the ACK, `verify_sk()` expects two invocations and delivered count 2. Cleanup closes the client, destroys the skeleton, closes the server, and closes the cgroup fd.

State and persistence: state includes a temporary cgroup fd/link, a BPF socket-storage map keyed by socket fd, one server socket, one client socket, TCP_INFO polling state, and kernel TCP statistics. No files are written.

Dependencies: depends on generated `tcp_rtt.skel.h`, cgroup sockops support, BPF socket storage, IPv4 TCP sockets, `network_helpers.h`, and `TCP_INFO` reporting from the kernel.

Integration points: this userspace test validates a BPF sockops program's interaction with kernel TCP state and socket local storage. It is part of the broader TCP BPF selftest area.

Risks: RTT fields are timing-dependent, so the test only requires nonzero values rather than exact numbers. `wait_for_ack()` sleeps only 10 microseconds per retry for 100 retries, which can be tight on slow or loaded environments. It relies on socket fd keys for map lookup, which is the expected userspace side of the selftest but would fail if BPF storage keying changes.

Test signals: expected signals are successful cgroup join, server start, skeleton load, sockops attach, socket storage map lookup, `invoked` 1 then 2, delivered 1 then 2, zero dsack/CE/retransmit counts, and nonzero `mrtt_us` and `srtt`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcp_rtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcpbpf_user.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcpbpf_user.c

Purpose: `tcpbpf_user.c` is a userspace harness for the TCP BPF sockops test program. It establishes an IPv6 loopback TCP connection in a test cgroup, transfers data in both directions, performs ordered shutdown, and verifies global BPF counters for sockops events, bytes, segments, callback return tests, listen/close counts, and TCP socket options.

Important APIs/types/functions: `verify_result()` checks `struct tcpbpf_globals` from skeleton BSS against expected event and counter values. `run_test()` creates a server with `start_server()`, connects a client with `connect_to_fd()`, accepts the connection, sends 1000 bytes client-to-server and 500 bytes server-to-client, then shuts down accepted socket first to force deterministic close/accounting order. `test_tcpbpf_user()` loads `test_tcpbpf_kern.skel.h`, joins cgroup `/tcpbpf-user-test`, attaches `bpf_testcb`, and runs the traffic scenario.

Control flow: after BPF attach, the test sends payloads, receives them fully, performs FIN sequencing, closes sockets, and only calls `verify_result()` if the socket flow completed without error. Cleanup closes the cgroup fd and destroys the skeleton.

State and persistence: runtime state is the cgroup link, skeleton BSS global counters, one TCP listener, one client, one accepted socket, and data buffers. There is no persistent storage.

Dependencies: depends on generated `test_tcpbpf_kern.skel.h`, shared `test_tcpbpf.h`, cgroup sockops support, IPv6 loopback TCP, BPF helpers that read/write TCP sockopts, and `network_helpers.h`.

Integration points: this is a classic TCP BPF selftest that validates kernel sockops callbacks through userspace-observable BSS fields. It overlaps conceptually with `tcp_hdr_options.c` but focuses on general sockops events and counters.

Risks: exact byte and close-event counts depend on the BPF program and on controlled shutdown order; the code explicitly shuts down the accepted side first to reduce nondeterminism. It assumes IPv6 loopback is available. If socket creation fails early, result verification is skipped, so the preceding assertions must carry diagnostics.

Test signals: expected BSS values include a precise event bitmask, 501 bytes received, 1002 bytes acked, one data segment in/out, bad callback return value `0x80`, good callback return 0, one listen event, three close events, `tcp_save_syn` 0, `tcp_saved_syn` 1, and client/server window clamp values of 9216.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcpbpf_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpf_ma.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpf_ma.c

Purpose: `test_bpf_ma.c` validates BPF memory allocator behavior in generated BPF programs, including batch allocation/free and freeing through map destruction for regular and per-CPU allocations. It prepares BTF type ids for allocator data shapes before loading each selected BPF program.

Important APIs/types/functions: `do_bpf_ma_test()` opens `test_bpf_ma.skel.h`, obtains object BTF with `bpf_object__btf()`, finds struct ids named `bin_data_<size>` and `percpu_bin_data_<size>` for sizes listed in skeleton rodata arrays, writes those ids back into rodata arrays, selects one BPF program by name with `bpf_object__find_program_by_name()`, enables autoload only for that program, loads and attaches the skeleton, sets `skel->bss->pid` to the current process, sleeps briefly, and checks `skel->bss->err`. `test_test_bpf_ma()` runs four subtests.

Control flow: each subtest opens a fresh skeleton so rodata and autoload choices are isolated. The BTF lookup loops must complete before load because rodata carries the type ids the BPF program will use. After attach, setting the PID gates BPF-side work to the current process; `usleep(1)` gives the attached program a chance to run; then `err` is asserted as zero and the skeleton is destroyed.

State and persistence: state is in the opened BPF object, rodata type-id arrays, autoload flags, attached BPF program, and BSS `pid`/`err`. There is no filesystem state. Any kernel allocator objects are created and freed by the BPF-side test logic and should be released by map/free paths or skeleton teardown.

Dependencies: depends on generated `test_bpf_ma.skel.h`, libbpf BTF APIs, BTF names emitted by the BPF object, allocator helper support in the kernel, and whatever attach points the selected skeleton programs use.

Integration points: the userspace file supplies dynamic BTF ids and subtest selection for BPF allocator programs compiled elsewhere. It is an integration harness between libbpf skeleton loading, BTF metadata, and allocator runtime behavior.

Risks: BTF name construction must match BPF-side struct naming exactly. `usleep(1)` is a minimal wait and assumes the attached program runs promptly after `pid` is set. Only one program is autoloaded per skeleton instance, so missing or renamed program names lead to early failure. The test reports only aggregate `err` from BSS, so deeper allocator failure details must be encoded by the BPF program.

Test signals: each subtest passes when all expected BTF struct ids are found, the named program exists, load and attach succeed, and `skel->bss->err` remains zero after triggering the current-PID path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpf_ma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpf_smc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpf_smc.c

Purpose: `test_bpf_smc.c` validates BPF policy control over transparent TCP-to-SMC protocol selection. It sets up loopback service topology, optionally configures SMC UEID through generic netlink, attaches `bpf_smc` programs, populates a policy map, opens client/server links, and verifies SMC versus fallback counters.

Important APIs/types/functions: `smc_policy_ip_key` and `smc_policy_ip_value` define the policy map key/value. Non-s390x builds include generic-netlink helpers `send_cmd()`, `get_smc_nl_family_id()`, `smc_ueid()`, `setup_ueid()`, and `cleanup_ueid()` for `SMC_GEN_NETLINK` UEID configuration. `setup_netns()` creates `bpf_smc_netns` and adds loopback addresses. `set_client_addr_cb()` binds client source addresses. `run_link()` starts a TCP server, connects from a selected source address, and closes both ends. `block_link()` inserts block-mode entries in `smc_policy_ip`. `test_topo()` loads/attaches the skeleton, writes `/proc/sys/net/smc/hs_ctrl`, updates policy, runs topology links, and checks counters. `test_bpf_smc()` handles setup, subtest execution, skip, and cleanup.

Control flow: setup first ensures UEID requirements are met, then creates a test net namespace with `127.0.1.0/8` and `127.0.2.0/8` on loopback. The topology subtest attaches the BPF programs and obtains `smc_policy_ip`. It writes `linkcheck` to `hs_ctrl`, blocks `CLIENT_IP -> SERVER_IP_VIA_RISK_PATH` and `SERVER_IP -> SERVER_IP`, then runs service links: client to primary server service 1, server to itself service 2, client to primary server service 2, and client to risky server service 3. It asserts `smc_cnt` and `fallback_cnt` after stages to confirm policy and fallback decisions.

State and persistence: state includes SMC UEID table entries, a named network namespace, loopback IP aliases, `/proc/sys/net/smc/hs_ctrl`, BPF links/programs/maps, policy map contents, and skeleton BSS counters. Cleanup removes the UEID and frees the namespace. There is no repository-file persistence, but sysctl/UEID failures could leave system SMC state changed until cleanup succeeds.

Dependencies: depends on SMC kernel support, IPPROTO_SMC availability or local fallback definition, generic netlink SMC family on non-s390x, loopback networking, `network_helpers.h`, generated `bpf_smc.skel.h`, BPF fmod_ret/update-socket-protocol hooks used by the skeleton, and privileges to write SMC sysctls and create namespaces.

Integration points: the test integrates BPF programs with kernel SMC protocol selection, generic netlink management, BPF maps as policy storage, and normal TCP socket helpers. It models a service graph where some links should use SMC and some should fall back.

Risks: unsupported or misconfigured SMC causes setup failure and an explicit skip. Generic-netlink parsing is hand-written and assumes response layout sufficient to find `CTRL_ATTR_FAMILY_ID`. `send_cmd()` sets `nla_len = nla_len + 1 + NLA_HDRLEN`, which relies on string-style payload expectations. Writing `hs_ctrl` and UEID management are system-level side effects. The test uses fixed addresses and namespace name, so stale resources can collide.

Test signals: setup success or skip is the first signal. Topology success is indicated by skeleton load/attach, valid policy map fd, successful service connections, `smc_cnt` progressing from 2 to 3 to 4, and `fallback_cnt` progressing from 1 to 2 according to blocked/risky links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpf_smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpf_syscall_macro.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpf_syscall_macro.c

Purpose: `test_bpf_syscall_macro.c` validates BPF syscall kprobe argument extraction macros, including normal `PT_REGS_PARM*`, CO-RE variants, `BPF_KPROBE_SYSCALL`, architecture-specific fourth-argument handling on x86_64, and a six-argument syscall case using `splice()`.

Important APIs/types/functions: `test_bpf_syscall_macro()` opens, loads, and attaches `bpf_syscall_macro.skel.h`. It sets `skel->rodata->filter_pid` to the current process, calls `prctl()` with known arguments, checks BSS fields filled by the BPF program, then calls `splice()` with deliberately invalid fds but known pointer/value arguments and checks captured BSS fields. It uses `SPLICE_F_NONBLOCK`, `loff_t` offsets, and errno assertion on the failed syscall.

Control flow: the skeleton is opened first so rodata can be set before load. After attach, `prctl()` triggers the monitored syscall path. Assertions compare classic and CO-RE macro outputs. On x86_64, values captured from `cx` for arg4 are expected not to match because syscall arg4 uses a different register convention; the corrected arg4 fields must match. The `splice()` call is expected to fail with `EBADF` while still triggering BPF argument capture for all six arguments. Cleanup always destroys the skeleton.

State and persistence: transient state is the attached kprobe programs, rodata PID filter, BSS argument capture fields, local offset variables, and errno from `splice()`. No persistent files or kernel objects remain after skeleton destruction.

Dependencies: depends on generated `bpf_syscall_macro.skel.h`, kprobe support for syscall entry points used by the skeleton, syscall register conventions, CO-RE support, and architecture conditionals for x86_64.

Integration points: this file is a direct userspace trigger for BPF-side macro tests. It ensures BPF tracing helper macros used by many kprobe programs interpret syscall arguments correctly across regular and CO-RE accessors.

Risks: syscall wrappers and register conventions are architecture-specific; the file handles the known x86_64 arg4 caveat but other architectures depend on skeleton-side support. Kprobe attachment names can vary with kernel config. The `splice()` pointer comparisons store userspace addresses as `__u64`, which is expected for the test but assumes no pointer tagging incompatibility.

Test signals: expected signals are successful skeleton open/load/attach, matching prctl args 1/2/3/4/5 in corrected fields, x86_64 mismatch only for the intentionally wrong cx arg4 fields, matching `BPF_KPROBE_SYSCALL` fields, `splice()` returning `-1` with `-EBADF`, and exact capture of splice fd, pointer, length, and flags arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpf_syscall_macro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpffs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpffs.c

Purpose: `test_bpffs.c` validates bpffs behavior across two independent mounts, including debug iterator files, directory creation, BPF object pinning, and `renameat2()` semantics for `RENAME_EXCHANGE` and `RENAME_NOREPLACE`.

Important APIs/types/functions: `read_iter()` opens a bpffs debug file and scans for the string `iter`, proving iterator-backed debug entries produce content. `fn()` runs the actual isolated filesystem test in a child process: it unshares the mount namespace, makes mounts private, creates `/tmp/test_bpffs_testdir`, mounts tmpfs, mounts two bpffs instances, creates directories, creates an array map with `bpf_map_create()`, pins it with `bpf_obj_pin()`, exchanges directories and a pinned map path with `renameat2(RENAME_EXCHANGE)`, tests `RENAME_NOREPLACE`, then unmounts/removes paths and exits with the status. `test_test_bpffs()` forks `fn()` and checks the child exit status.

Control flow: the child isolates mount state, mounts tmpfs and bpffs under `fs1` and `fs2`, verifies `maps.debug` and `progs.debug`, creates `fs1/a/1` and `fs1/b`, pins a map at `fs1/c`, swaps `a` and `b` and verifies inode/path effects, swaps pinned map `c` with directory `b` and verifies mixed-type exchange behavior, then verifies `RENAME_NOREPLACE` fails when destination exists and the original remains. Cleanup unmounts bpffs and tmpfs and removes directories before exit. Parent waits and fails if child exits nonzero.

State and persistence: state is intentionally confined to the child mount namespace and temporary directory tree under `/tmp/test_bpffs_testdir`. It creates kernel BPF map state while pinned, two bpffs mounts, a tmpfs mount, directories, and a pinned map path. Cleanup unmounts and removes all paths; an abrupt child termination could leave temporary paths in the parent filesystem but mounts are namespace-local.

Dependencies: depends on mount namespace support, tmpfs, bpffs, `renameat2()` flags, BPF map creation/pinning, and permission to mount filesystems and create BPF maps.

Integration points: this is a filesystem-level BPF selftest that exercises bpffs VFS behavior rather than BPF program execution. It validates how bpffs participates in Linux rename semantics and debug iterators.

Risks: requires mount privileges and bpffs support. The fixed temporary directory may already exist from a prior failed run; the code tolerates initial `EEXIST` but cleanup assumptions may fail if unrelated content exists there. `read_iter()` searches for a short substring, which is a smoke signal rather than exact debug output validation. `WEXITSTATUS(status)` is used without an explicit `WIFEXITED` check.

Test signals: pass signals include successful mount namespace isolation, tmpfs and bpffs mounts, readable iterator debug files containing `iter`, successful map creation and pinning, inode movement after directory exchange, path validity after mixed map/directory exchange, expected failure of `RENAME_NOREPLACE`, and zero child exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpffs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bprm_opts.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bprm_opts.c

Purpose: `test_bprm_opts.c` verifies that a BPF `bprm_creds_for_exec` program can set `bprm->secureexec` based on task local storage and that userspace observes secure execution through environment-variable scrubbing by the dynamic loader.

Important APIs/types/functions: `bash_envp` provides `TMPDIR=shouldnotbeset`. `update_storage()` opens a pidfd for the current process, inserts `secureexec` into `secure_exec_task_map` with `BPF_NOEXIST`, and closes the pidfd. `run_set_secureexec()` forks a child, redirects output to `/dev/null`, updates task storage, then `execle()`s `/bin/bash` to return 10 if `TMPDIR` remains set and 20 if it is unset. `test_test_bprm_opts()` loads and attaches `bprm_opts.skel.h`, then runs the child path once with secureexec 0 and once with secureexec 1.

Control flow: after skeleton attach, the first child writes secureexec 0 into task local storage and should execute bash normally, preserving `TMPDIR` and exiting 10. The second writes secureexec 1 and should trigger secure execution, causing loader/shell environment scrubbing and exit 20. The parent waits for each child and translates the expected exit code to success.

State and persistence: state includes a BPF task-local-storage map entry keyed by child pidfd, a BPF LSM/bprm attachment from the skeleton, child process environment, and `/dev/null` fd redirection. No files are created except opening `/dev/null`.

Dependencies: depends on generated `bprm_opts.skel.h`, BPF support for bprm hooks and task local storage, `pidfd_open`, `/bin/bash`, dynamic loader secure-exec behavior, and `network_helpers.h` for `sys_pidfd_open`.

Integration points: this bridges BPF process-exec hooks to a concrete userspace security semantic: secureexec causes environment variables such as `TMPDIR` to be ignored/removed. It validates both kernel hook behavior and the selftest BPF program's map lookup path.

Risks: assumes `/bin/bash` exists and that `TMPDIR` is affected as expected under secure execution on the platform. `update_storage()` returns positive errno values rather than negative errors, matching child exit use but different from many kernel-style helpers. The test uses `WEXITSTATUS` without checking abnormal child termination. If a previous map entry exists for the same pidfd, `BPF_NOEXIST` would fail, though pidfds are per child.

Test signals: success requires skeleton load/attach, child with secureexec 0 exiting as normal environment-preserving execution, child with secureexec 1 exiting as secure environment-scrubbed execution, and no errors from pidfd/map update or exec setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bprm_opts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_btf_ext.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_btf_ext.c

Purpose: `test_btf_ext.c` verifies that libbpf exposes BTF.ext line and function info for a loaded BPF program exactly as the kernel reports it through `bpf_prog_get_info_by_fd()`.

Important APIs/types/functions: `subtest_line_func_info()` opens and loads `test_btf_ext.skel.h`, obtains fd for `skel->progs.global_func`, queries kernel `bpf_prog_info` line info into a local `bpf_line_info` array, gets libbpf's `bpf_program__line_info()` and count, then repeats the process for `bpf_func_info` with `bpf_program__func_info()` and count. `ASSERT_MEMEQ()` compares libbpf arrays to kernel-returned arrays. `test_btf_ext()` runs the `line_func_info` subtest.

Control flow: the subtest first retrieves line-info records by setting `info.line_info`, `info.nr_line_info`, and record size before calling `bpf_prog_get_info_by_fd()`. It then reads libbpf's parsed line-info pointer/count. It resets `info`, retrieves function-info records similarly, reads libbpf's parsed function-info pointer/count, validates pointers/counts, and compares memory for both record sets. Skeleton destruction releases the program.

State and persistence: state is read-only BTF.ext metadata associated with the loaded BPF object and local stack buffers for kernel info. No persistent files are written.

Dependencies: depends on generated `test_btf_ext.skel.h`, libbpf support for retaining BTF.ext line/function info, kernel support for returning line and function info via `BPF_OBJ_GET_INFO_BY_FD`, and `btf_helpers.h`/test assertions.

Integration points: this is a metadata consistency test between libbpf's view of the BPF object and the kernel's view after load. It protects tooling that relies on libbpf line/function metadata matching kernel program info.

Risks: local arrays are fixed at 128 entries, so a future BPF object with more records would need a larger buffer or dynamic sizing. The variable names `libbbpf_*_cnt` include a typo but are local and harmless. The test assumes record ordering and bytes are identical between libbpf metadata and kernel-returned info.

Test signals: success is signaled by skeleton load, successful kernel line-info and func-info queries, non-null libbpf line/function info pointers, matching record counts, and byte-for-byte equality of all reported records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_btf_ext.c -->
