# subset-b-006801 research

Grouped research report for BPF selftest program-test sources under `sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests`. Each section is bounded by reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_list.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_list.c

Purpose: exercises kernel verifier and runtime behavior for BPF intrusive linked lists, including `bpf_list_head`, `bpf_list_node`, required `bpf_spin_lock` ownership, nested lists, map/global/kptr storage, and peek coverage through `linked_list_peek`.

Important APIs and functions: `test_linked_list_fail_prog()` opens `linked_list_fail` with a 1 MiB verifier log, autoloads one named bad program, expects load failure, and searches the verifier log for the exact diagnostic. `test_linked_list_success()` runs selected programs from `linked_list.skel.h` with `bpf_prog_test_run_opts()` and `pkt_v4`. `clear_fields()` resets map/global backing memory through `bpf_map__update_elem()`. `init_btf()`, `list_and_rb_node_same_struct()`, and `test_btf()` synthesize BTF with libbpf `btf__add_*()` APIs to validate kernel-side metadata checks.

Control flow: `test_linked_list()` iterates the fail table, runs synthetic BTF subtests, then runs success modes with and without leaving list objects in backing maps. The success helper uses mode branches for simple push/pop, multiple push/pop, list-in-list, and all operations. `test_linked_list_peek()` delegates to `RUN_TESTS(linked_list_peek)`.

State and persistence: state is transient BPF object state plus map/global storage inside the skeleton. The `leave_in_map` dimension intentionally leaves nodes reachable until object teardown to exercise cleanup, while the non-leave path overwrites map values with `0xff`. BTF objects are loaded into the kernel and freed locally after expected success/failure.

Dependencies and integration: depends on libbpf skeletons `linked_list`, `linked_list_fail`, `linked_list_peek`, `test_btf.h`, `linux/btf.h`, and selftest network packet fixtures. It integrates with the selftest harness through `ASSERT_*` and subtest names.

Risks and test signals: high-value signals are exact verifier messages for missing locks, wrong allocation ownership, invalid direct access, bad offsets, cycles in ownership graphs, and mixed list/rb-node/refcount rules. Fragility comes from diagnostics changing, BTF error codes changing, or layout offsets in the BPF-side structs moving without updating expected strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_maps.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_maps.c

Purpose: validates that linked BPF object files resolve map definitions and weak map references consistently across compilation units.

Important APIs and functions: `test_linked_maps()` uses the generated `linked_maps` skeleton. It opens and loads the combined object, attaches it, triggers a syscall probe path with `syscall(SYS_getpgid)`, then reads BSS outputs.

Control flow: open/load, attach, trigger, assert three outputs, destroy skeleton. Failure paths jump to cleanup after attach/load problems.

State and persistence: all observable state is in skeleton BSS fields: `output_first1`, `output_second1`, and `output_weak1`. No persistent kernel state remains after `linked_maps__destroy()`.

Dependencies and integration: depends on `linked_maps.skel.h`, `test_progs.h`, and a traceable syscall trigger. It is a libbpf linker integration test, not a networking test.

Risks and test signals: expected values `2000`, `2`, and `2` signal correct strong/weak map symbol resolution. Risks are accidental changes to BPF-side constants or attach points that make `getpgid` stop triggering the programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_maps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_vars.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_vars.c

Purpose: validates libbpf linker behavior for BSS, data, rodata, and weak variable resolution across linked BPF object files.

Important APIs and functions: `test_linked_vars()` opens the `linked_vars` skeleton before load so it can seed BSS inputs, then loads, attaches, triggers `SYS_getpgid`, and checks BSS outputs.

Control flow: open, set `input_bss1`, `input_bss2`, and `input_bss_weak`, load, attach, trigger syscall, compare output accumulations, destroy.

State and persistence: state is skeleton data/BSS/rodata. The test depends on weak data and rodata winners from the first object file (`10` for data, `100` for rodata). It has no persistent resources after destroy.

Dependencies and integration: depends on `linked_vars.skel.h`, syscall-based trigger programs, and libbpf skeleton variable accessors.

Risks and test signals: output sums prove that global variable references in different sections resolved to the intended linked definitions. Fragility is mostly from changing the linked BPF fixture values or weak symbol selection rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_vars.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/livepatch_trampoline.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/livepatch_trampoline.c

Purpose: verifies BPF fentry/fexit attachment to a livepatched kernel function trampoline, specifically the livepatch sample that changes `/proc/cmdline` behavior.

Important APIs and functions: `load_livepatch()` locates `samples/livepatch/livepatch-sample.ko` using `KBUILD_OUTPUT` or a relative kernel tree. `unload_livepatch()` disables `/sys/kernel/livepatch/livepatch_sample/enabled` before unloading. `read_proc_cmdline()` opens and reads `/proc/cmdline`. `__test_livepatch_trampoline()` loads `livepatch_trampoline`, sets `my_pid`, attaches fentry/fexit either in default or reversed order, reads procfs, and checks hit counters.

Control flow: `test_livepatch_trampoline()` skips without `/sys/kernel/livepatch`, retries module loading once after unloading a stale module, runs `fentry_first` and `fexit_first`, then unloads the livepatch.

State and persistence: persistent kernel module/livepatch state is created temporarily and explicitly disabled/unloaded at the end. BPF state is skeleton BSS counters `fentry_hit` and `fexit_hit`.

Dependencies and integration: depends on kernel livepatch support, the sample livepatch module being built, `testing_helpers.h` module helpers, root privileges, procfs, and the generated skeleton.

Risks and test signals: success requires both trampoline programs to fire exactly once and the livepatch text to be visible. Risks include stale modules, missing build outputs, livepatch sysfs policy, and ordering bugs in fentry/fexit trampoline stacking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/livepatch_trampoline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/load_bytes_relative.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/load_bytes_relative.c

Purpose: tests `bpf_skb_load_bytes_relative()` behavior in a cgroup skb egress program by sending a TCP packet through a joined cgroup and checking a result map.

Important APIs and functions: `test_load_bytes_relative()` uses `test__join_cgroup()`, `start_server()`, `bpf_prog_test_load()` for `load_bytes_relative.bpf.o`, `bpf_object__find_map_by_name()`, `bpf_object__find_program_by_name()`, `bpf_prog_attach()`, `connect_to_fd()`, and `bpf_map_lookup_elem()`.

Control flow: join cgroup, start TCP server, load object as `BPF_PROG_TYPE_CGROUP_SKB`, find map/program, attach to `BPF_CGROUP_INET_EGRESS`, connect once to trigger egress, read key zero from `test_result`, and close resources in reverse order.

State and persistence: one cgroup fd, server fd, BPF object, and one map value are transient. The cgroup attachment is released when the object/fds close.

Dependencies and integration: depends on selftest cgroup setup, network helper loopback TCP, and the companion BPF object.

Risks and test signals: `map_value == 1` is the main pass signal. Risks are cgroup setup failure, attach permission failure, or no egress packet generated by the loopback connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/load_bytes_relative.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/local_kptr_stash.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/local_kptr_stash.c

Purpose: validates local kptr stashing, unstashing, and refcount acquisition rules for BPF objects, including negative verifier cases.

Important APIs and functions: each success helper loads `local_kptr_stash`, runs one or more skeleton programs with `bpf_prog_test_run_opts()` over `pkt_v4`, and checks return values. Covered programs include `stash_rb_nodes`, `stash_plain`, `stash_local_with_root`, `unstash_rb_node`, `refcount_acquire_without_unstash`, and `stash_refcounted_node`. `test_local_kptr_stash_fail()` uses `RUN_TESTS(local_kptr_stash_fail)`.

Control flow: `test_local_kptr_stash()` runs named subtests for simple stash, plain stash, local root association, unstash, refcount acquire before/after stashing, and verifier failures.

State and persistence: BPF-side local objects and refcounted nodes live only for the skeleton lifetime. Return values such as `42` and `2` encode expected object availability/refcount states.

Dependencies and integration: depends on `local_kptr_stash.skel.h`, `local_kptr_stash_fail.skel.h`, and packet test-run support.

Risks and test signals: signals are successful program test runs plus expected return values. Risks are verifier semantic changes for local kptr ownership, RB-tree roots, or refcount acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/local_kptr_stash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/log_buf.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/log_buf.c

Purpose: verifies libbpf and raw BPF syscall log-buffer handling for object load, per-program load logs, `bpf_prog_load()`, and BTF load diagnostics.

Important APIs and functions: `libbpf_print_cb()` captures libbpf print output into a fixed buffer. `obj_load_log_buf()` tests object-level and per-program log buffers on `test_log_buf`, including a good and bad program. `bpf_prog_load_log_buf()` directly loads hand-written good/bad socket-filter instruction arrays. `bpf_btf_load_log_buf()` builds raw BTF and checks BTF load log behavior. The top-level test runs these subtests.

Control flow: first round uses object and per-program buffers and expects BPF object load failure with isolated program logs. Second round removes the object log buffer so bad-program verifier logs flow through the libbpf print callback. Raw program and BTF helpers check log level zero versus verbose log levels.

State and persistence: state is in heap log buffers, static capture buffers, and temporary program/BTF fds. All fds and skeletons are closed; the old libbpf print callback is restored.

Dependencies and integration: depends on `test_log_buf.skel.h`, libbpf print callback APIs, raw `bpf_prog_load`, BTF APIs, and stable verifier log fragments.

Risks and test signals: exact substrings such as program load banners, `R0 !read_ok`, and BTF/data-section diagnostics are the pass signals. Tests are sensitive to verifier log wording and log-level policy changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/log_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/log_fixup.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/log_fixup.c

Purpose: validates verifier log fixups for BPF assembly/source metadata, ensuring loader and verifier diagnostics remain meaningful after instruction fixups.

Important APIs and functions: the file loads test BPF objects/program variants with libbpf options that capture verifier logs, toggles autoload as needed, and searches for expected strings. It uses selftest assertion macros, skeleton/object open/load APIs, and log buffers.

Control flow: subtests open the fixture object, select a program or scenario, attempt load, and compare the resulting log against expected fixed-up instruction/source references. Negative cases expect load failure; positive cases ensure fixups do not corrupt accepted loads.

State and persistence: state is limited to verifier log buffers and temporary BPF object/program fds. There is no lasting map or kernel object state after close/destroy.

Dependencies and integration: depends on companion BPF fixtures for log-fixup scenarios, libbpf verifier logging, and stable instruction/source diagnostics from the kernel verifier.

Risks and test signals: strong signals are exact fixed-up log fragments. Risk is high sensitivity to harmless verifier wording changes, compiler instruction layout changes, or BTF/source-line metadata changes in the BPF fixture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/log_fixup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lookup_and_delete.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lookup_and_delete.c

Purpose: tests lookup-and-delete semantics across supported map types, including element removal, return values, batch behavior, and unsupported map handling.

Important APIs and functions: the test creates maps, populates keys/values, calls `bpf_map_lookup_and_delete_elem()` and batch variants, and compares values and follow-up lookups. It uses selftest helpers for map fd creation and assertions.

Control flow: subtests build a map fixture, insert elements, run lookup-delete operations, then verify that successful lookups return the original value and delete the element. Unsupported or invalid combinations assert expected error codes.

State and persistence: all state is in temporary map fds. Deletion behavior is the state under test; maps are closed at the end.

Dependencies and integration: depends on kernel map implementations and libbpf/syscall wrappers. It integrates with the BPF selftest harness as a pure userspace map syscall test.

Risks and test signals: expected values, missing keys after delete, and expected `errno` values are the main signals. Risks include map-type support expansion changing which operations are rejected, and batch ordering/count semantics differing by map implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lookup_and_delete.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lookup_key.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lookup_key.c

Purpose: validates map key lookup behavior from BPF programs, especially helper semantics around locating current keys and reporting expected values.

Important APIs and functions: the harness loads the companion skeleton/object, initializes maps or inputs, runs BPF programs through attach or test-run paths, and reads BSS/map outputs for pass/fail.

Control flow: setup creates the BPF fixture, triggers the selected program path, and checks that lookup-key results match expected keys and error cases. Cleanup destroys skeleton state.

State and persistence: state is transient map content and BSS status fields. No state persists after the object closes.

Dependencies and integration: depends on the BPF fixture for lookup-key helper coverage, libbpf skeleton APIs, and `test_progs.h` assertions.

Risks and test signals: signals are exact returned keys/status values. Risks include changes to helper availability, map type behavior, or BPF-side fixture layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lookup_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lru_bug.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lru_bug.c

Purpose: regression test for LRU map preallocation/value-initialization behavior.

Important APIs and functions: `test_lru_bug()` opens and loads `lru_bug`, attaches it, then checks `skel->data->result`.

Control flow: open/load, attach, inspect the result field, destroy. The attach path triggers the BPF-side logic.

State and persistence: state is a single skeleton data result and the BPF maps inside the fixture. All state is transient.

Dependencies and integration: depends on `lru_bug.skel.h` and the BPF-side program that detects whether preallocated LRU pop incorrectly calls value initialization.

Risks and test signals: `result == 0` is expected by `ASSERT_OK`; a nonzero result means the regression was observed. Risk is low in the harness, concentrated in the companion BPF logic and attach trigger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lru_bug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lsm_bdev.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lsm_bdev.c

Purpose: integration test for BPF LSM hooks around block-device integrity/dm-verity metadata, including root hash visibility and allocation accounting.

Important APIs and functions: `run_cmd()` shells out with `popen()` and optional output capture. `has_prerequisites()` checks required tools/kernel support. `test_lsm_bdev()` creates temporary data/hash images, attaches loop devices, formats dm-verity metadata with `veritysetup`, loads and attaches `lsm_bdev`, opens a dm-verity device, stats `/dev/mapper/bpf_test_verity`, and looks up recorded device info in `verity_devices`.

Control flow: prerequisite check, temp image creation/truncation, loop setup, verity format, skeleton load/attach before activation, verity open, map lookup by device number, assertions, then structured cleanup for dm device, loops, files, fds, and skeleton.

State and persistence: manipulates real `/tmp` images, loop devices, a device-mapper target, and a BPF map. Cleanup removes dm-verity and loop state; failure paths try to close/unlink resources.

Dependencies and integration: depends on root privileges, loop devices, `losetup`, `veritysetup`, `dmsetup`/device mapper, stat-able mapper device, and `lsm_bdev.skel.h`.

Risks and test signals: map value fields `has_roothash`, `sig_valid`, `setintegrity_cnt`, and BSS `alloc_count` are key signals. Risks are environmental: missing tooling, stale mapper names, insufficient privileges, or cleanup failure leaving block resources behind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lsm_bdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lsm_cgroup.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lsm_cgroup.c

Purpose: validates cgroup-scoped BPF LSM attachment, query, stacking, detach, and enforcement behavior for socket hooks.

Important APIs and functions: `query_prog_cnt()` uses BTF to resolve LSM attach function IDs and `bpf_prog_query_opts()` to count attached programs. `test_lsm_cgroup_functional()` creates cgroups, loads `lsm_cgroup`, attaches programs through links and `bpf_prog_attach`, exercises socket create/bind/listen/connect/accept paths, checks socket priority and BSS counters, then detaches selected programs. `test_lsm_cgroup_nonvoid()` ensures non-void cgroup LSM programs are rejected.

Control flow: setup cgroups and skeleton, attach LSM programs to multiple cgroups, verify query counts, exercise sockets in target cgroups, verify hooks ran the expected number of times, join an empty cgroup to prove isolation, detach/close/destroy. The top-level runs `functional` and `nonvoid`.

State and persistence: cgroup fds, BPF links, direct cgroup attachments, sockets, and BSS counters are transient. One bind link is intentionally left for cgroup-release cleanup coverage.

Dependencies and integration: depends on BTF, cgroup helpers, network helpers, `lsm_cgroup.skel.h`, `lsm_cgroup_nonvoid.skel.h`, and kernel support for `BPF_LSM_CGROUP`.

Risks and test signals: hook counters such as socket allocation/copy counts and socket priority changes signal success. Risks include BTF attach function lookup failures, cgroup cleanup behavior, and subtle attach/detach stacking regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lsm_cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_helpers.h -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_helpers.h

Purpose: shared helper header for LWT program tests, providing namespace setup macros, ICMP packet filtering, and packet wait utilities.

Important APIs and functions: `log_err()` wraps error printing with function/line context. `RUN_TEST(name)` creates/deletes the configured `NETNS`, switches into it with `open_netns()`, runs a named helper, and closes the namespace. `netns_create()` and `netns_delete()` shell out to `ip netns`. `__expect_icmp_ipv4()` validates ICMP payload length/type. `wait_for_packet()` loops on a fd until a filter accepts a packet or timeout expires.

Control flow: LWT tests include this header after defining `NETNS`, then invoke `RUN_TEST()` from a worker thread. Packet capture helpers are called after ping or socket send operations.

State and persistence: namespace state is external and named by `NETNS`; helpers delete/recreate it per subtest. `wait_for_packet()` consumes packets from fds without persistent state.

Dependencies and integration: depends on `test_progs.h`, Linux ICMP headers, `network_helpers.h` namespace functions, and the `ip` tool.

Risks and test signals: risks are macro side effects, hard-coded namespace names, and timeout sensitivity. Test signal is binary: namespace operations succeed and expected ICMP packets are observed before timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_ip_encap.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_ip_encap.c

Purpose: end-to-end LWT BPF IP/GRE and IPv6/GRE encapsulation test over a three-namespace topology, with optional VRF routing and GSO regression coverage.

Important APIs and functions: `create_ns()`, `set_top_addr()`, `set_bottom_addr()`, `configure_vrf()`, `configure_ns1/2/3()`, and `setup_network()` build the topology. `lwt_ip_encap()` installs BPF LWT routes using `test_lwt_ip_encap.bpf.o` sections `encap_gre` or `encap_gre6`. `check_ping_ok()`, `check_ping_fails()`, `remove_routes_to_gredev()`, `add_unreachable_routes_to_gredev()`, and `test_gso_fix()` validate positive and negative paths.

Control flow: each exported test selects IPv4/IPv6 encapsulation and VRF/no-VRF plus egress/ingress subtests. The helper creates three netns, configures top and bottom veth paths plus GRE/IP6GRE devices, confirms baseline ping, removes the direct destination route, installs LWT BPF replacement routes, confirms ping recovery, optionally sends a large TCP payload to test GSO, then breaks GRE reachability and expects ping failure.

State and persistence: heavy external state includes three netns, veth pairs, VRF devices, GRE devices, routes, and sockets. Cleanup deletes all namespaces via `SYS_NOFAIL` regardless of partial failure.

Dependencies and integration: depends on `ip`, ping/ping6, network helpers, root network privileges, `test_lwt_ip_encap.bpf.o`, and GRE/IP6GRE kernel support.

Risks and test signals: pings and large TCP read/write counts are the main signals. Risks are environmental flakiness, route timing, VRF source-selection limitations, and cleanup sensitivity after partial setup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_ip_encap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_misc.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_misc.c

Purpose: runs miscellaneous LWT verifier/runtime tests packaged in the `lwt_misc` skeleton.

Important APIs and functions: `test_lwt_misc()` simply delegates to `RUN_TESTS(lwt_misc)`.

Control flow: the selftest harness enumerates skeleton-defined programs/subtests through the `RUN_TESTS` macro.

State and persistence: no user-space state beyond skeleton loading managed by the macro. Any map/program state is owned by the generated fixture.

Dependencies and integration: depends on `lwt_misc.skel.h` and the selftest harness.

Risks and test signals: the signal is that all skeleton subtests load/run as expected. Risks are located in the BPF fixture; this C wrapper has minimal behavioral complexity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_redirect.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_redirect.c

Purpose: tests LWT xmit BPF redirection to tun/tap/vlan devices, including normal ingress/egress delivery and regression cases where devices are down.

Important APIs and functions: `ping_dev()` encodes the target ifindex into destination IP. `new_packet_sock()` binds an AF_PACKET socket with `PACKET_IGNORE_OUTGOING`. `expect_icmp()` and `expect_icmp_nomac()` filter captured packets. `setup_redirect_target()` creates a tun/tap target, dummy route device, loopback source address, and two LWT BPF routes using `test_lwt_redirect.bpf.o`. `send_and_capture_test_packets()` checks egress via tun/tap fd and ingress via packet socket.

Control flow: a worker thread deletes/recreates `NETNS` for each subtest through `RUN_TEST()`. Normal MAC and no-MAC cases expect captured ICMP packets. Down-device and carrier-down VLAN cases only assert no kernel crash/panic while pings execute.

State and persistence: per-subtest netns, tun/tap fds, packet sockets, dummy/vlan devices, and routes are transient. Threading isolates namespace side effects from the main process.

Dependencies and integration: depends on `lwt_helpers.h`, `network_helpers.h`, tun/tap support, `ip`, ping, AF_PACKET, and BPF object sections for redirect variants.

Risks and test signals: packet capture on the target device is the positive signal; absence of kernel crash is the negative-regression signal. Risks include timing timeouts, busybox ping limitations, tun/tap permissions, and kernel instability in the tested paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_redirect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_reroute.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_reroute.c

Purpose: tests LWT xmit BPF rerouting by setting skb marks and policy-routing packets to a tun device, including qdisc drop regression coverage.

Important APIs and functions: `setup()` creates a tun device, dummy `link_err`, loopback source address, LWT BPF route from `test_lwt_reroute.bpf.o`, fwmark rule, and table 100 default route. `test_lwt_reroute_normal_xmit()` pings an IP whose final octet matches the tun ifindex and expects an ICMP packet on the tun fd. `overflow_fq()` sends UDP packets with `SO_TXTIME`/`SCM_TXTIME` to overflow an `fq` qdisc. `test_lwt_reroute_qdisc_dropped()` installs the fq qdisc and asserts no crash while overflowing.

Control flow: subtests run in an isolated thread and namespace using `RUN_TEST`. The normal path verifies actual packet delivery; the qdisc path is a crash-regression test.

State and persistence: state includes one netns, tun fd, dummy device, policy rule, route table, qdisc, UDP socket, and timestamp control messages. It is deleted with namespace teardown.

Dependencies and integration: depends on `lwt_helpers.h`, `network_helpers.h`, `ip`, `tc`, ping, tun support, and `SO_TXTIME`.

Risks and test signals: successful tun capture and no kernel crash are signals. Risks are qdisc/txtime support differences, timing, and route loops if the BPF fixture mark logic regresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_reroute.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_seg6local.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_seg6local.c

Purpose: end-to-end IPv6 Segment Routing local action test using End.BPF programs to manipulate SRH TLVs, flags, tags, and table lookup behavior across six namespaces.

Important APIs and functions: `setup()` creates six netns, five veth pairs, link-scope/global IPv6 addresses, SRv6 routes, `encap bpf in` route in NS2, three `seg6local action End.BPF` routes from `test_lwt_seg6local.bpf.o`, forwarding sysctls, and seg6 enablement in NS6. `cleanup()` deletes all namespaces. `test_lwt_seg6local()` starts a UDP server in NS6 and client in NS1 and sends `foobar`.

Control flow: setup topology, open NS6 for server, open NS1 for client, send UDP from `fb00::1` to `fb00::6`, read from server, compare payload, close fds/namespaces, cleanup.

State and persistence: six network namespaces, veth devices, routes, SRv6 local actions, sockets, and sysctls are temporary. Cleanup removes namespaces even after partial failure.

Dependencies and integration: depends on SRv6 kernel support, `iproute2` seg6local BPF support, network helpers, UDP helpers, and the companion BPF object.

Risks and test signals: successful receipt of exact `foobar` payload proves the SRH chain and BPF actions worked. Risks are missing SRv6 support, route setup mistakes, namespace cleanup issues, and timing/environment differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lwt_seg6local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_btf.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_btf.c

Purpose: regression test for map BTF lifetime when maps/programs are freed asynchronously and map BTF is shared by normal maps or map-in-map inner maps.

Important APIs and functions: `do_test_normal_map_btf()` loads `normal_map_btf`, attaches, triggers by setting PID and sleeping, duplicates the array map fd, creates many percpu array maps to delay deferred frees, destroys the skeleton, syncs RCU, waits, closes helper maps, and finally closes the duplicated array fd. `do_test_map_in_map_btf()` performs the same pattern for `map_in_map_btf`, deleting the inner map from the outer map before destroying.

Control flow: `test_map_btf()` runs `array_btf` and `inner_array_btf` subtests. Both force map BTF references to outlive the BPF program and surrounding skeleton objects.

State and persistence: temporary map fds and duplicated inner/array fds hold BTF references past skeleton destruction. RCU waits and sleeps model deferred cleanup timing.

Dependencies and integration: depends on `normal_map_btf.skel.h`, `map_in_map_btf.skel.h`, `kern_sync_rcu()`, and map fd duplication semantics.

Risks and test signals: absence of use-after-free/crash during delayed close is the key signal, plus `done` BSS confirmation. Timing sleeps are heuristic and may be sensitive to slow or heavily loaded systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_excl.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_excl.c

Purpose: verifies libbpf exclusive-map access enforcement, where a map can be restricted to one designated BPF program.

Important APIs and functions: `test_map_excl_allowed()` calls `bpf_map__set_exclusive_program()` for `excl_map` and autoloads only `should_have_access`, expecting load success. `test_map_excl_denied()` sets the same exclusive program but autoloads `should_not_have_access`, expecting `map_excl__load()` to fail with `-EACCES`.

Control flow: top-level runs allowed and denied subtests independently, opening/destroying a skeleton for each.

State and persistence: exclusive access metadata is attached to the libbpf map before load. No persistent state remains after skeleton destruction.

Dependencies and integration: depends on `map_excl.skel.h` and libbpf exclusive-program support.

Risks and test signals: `0` load for allowed and `-EACCES` for denied are the signals. Risks are changes in libbpf pre-load validation or kernel verifier error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_excl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_in_map.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_in_map.c

Purpose: tests concurrent access and update semantics for map-in-map structures, including array/hashtable outers, sleepable access, fd insertion/overwrite/delete, and unsupported lookup-and-delete cases.

Important APIs and functions: `thread_ctx` coordinates update and access threads. `update_map_fn()` repeatedly creates new array inner maps and updates the outer map. `access_map_fn()` triggers BPF programs with `SYS_getpgid` while updates race. `test_map_in_map_access()` selects a program/map by name, loads and attaches `access_map_in_map`, and runs the two threads with a barrier. `add_del_fd_htab()`, `overwrite_fd_htab()`, `lookup_delete_fd_htab()`, and `batched_lookup_delete_fd_htab()` exercise fd-valued hash outer-map operations.

Control flow: top-level runs access tests for array/hash and sleepable variants, then update tests for preallocated and non-preallocated hash outer maps.

State and persistence: temporary inner maps are inserted into outer maps and closed after update; kernel map references persist only while stored in the outer. Threads coordinate four iterations and store error bits in `ctx.err`.

Dependencies and integration: depends on `access_map_in_map.skel.h`, `update_map_in_htab.skel.h`, pthread barriers, syscall triggers, and map-in-map kernel support.

Risks and test signals: no thread errors and expected `-ENOTSUPP` for lookup-and-delete on htab-of-maps are signals. Risks are race sensitivity, missed synchronization, and map fd lifetime regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_in_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_init.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_init.c

Purpose: verifies that per-CPU hash and LRU per-CPU hash map values are zero-initialized correctly when slots are reused or evicted by BPF-side insertion.

Important APIs and functions: `map_populate()` fills all CPU slots with `FILL_VALUE`. `setup()` configures `hashmap1` as a chosen map type and size before skeleton load. `prog_run_insert_elem()` writes input key/value/PID into BSS, attaches the skeleton, triggers `getpgid`, and detaches. `check_values_one_cpu()` ensures only one CPU slot contains `TEST_VALUE`.

Control flow: `test_pcpu_map_init()` populates a one-entry percpu hash, deletes key 1, inserts key 1 from BPF, and checks one CPU value plus zeroed others. `test_pcpu_lru_map_init()` fills a two-entry LRU map, inserts key 3 from BPF to reuse/evict a slot, and checks initialization. Top-level skips on single-CPU systems.

State and persistence: state is temporary map contents and skeleton BSS inputs. The behavior under test is reused per-CPU value memory.

Dependencies and integration: depends on `test_map_init.skel.h`, multi-CPU availability, tracepoint/syscall trigger, and per-CPU map helpers.

Risks and test signals: one nonzero CPU and all other CPUs zero is the signal. Risks include CPU-count assumptions, current CPU scheduling, and BPF fixture attach trigger changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_kptr.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_kptr.c

Purpose: validates map-stored kptr reference counting across map types, local-storage kptrs, element deletion/update, deferred map free, and verifier failure cases.

Important APIs and functions: `test_map_kptr_success()` loads `map_kptr`, runs refcount test programs, optionally updates/deletes array, percpu array, hash, percpu hash, malloc-backed hash, LRU hash, and local-storage map elements, and adjusts expected `data->ref`. `kern_sync_rcu_tasks_trace()` runs an auxiliary BPF program to force RCU Tasks Trace grace period. `wait_for_map_release()` polls `count_ref` until `num_of_refs == 2`. `serial_test_map_kptr()` runs `RUN_TESTS(map_kptr_fail)` and success modes around RCU synchronization.

Control flow: failure tests run first. Success-map subtest exercises delete/update paths, waits for deferred release with both RCU variants, then repeats for synchronous delete observation.

State and persistence: kptr reference counts are shared between BPF maps and skeleton data/BSS. Map destruction and element deletion are intentionally used as lifecycle transitions.

Dependencies and integration: depends on `map_kptr.skel.h`, `map_kptr_fail.skel.h`, `rcu_tasks_trace_gp.skel.h`, packet test-run, and RCU sync helpers.

Risks and test signals: retval zero and expected reference counts are signals. Risks include grace-period timing, deferred free behavior, map-type-specific kptr release, and verifier rule changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_kptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_kptr_race.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_kptr_race.c

Purpose: regression suite for kptr reference leaks during map destruction races in hash maps, percpu hash maps, and socket local storage maps.

Important APIs and functions: `get_map_id()` retrieves map IDs with `bpf_map_get_info_by_fd()`. `read_refs()` runs `count_ref`. `test_htab_leak()` and `test_percpu_htab_leak()` create a map with kptr references, attach watcher fentry/fexit programs (`map_put`, `htab_map_free`) to observe map free, destroy the original skeleton, sync RCU, wait for `map_freed`, and assert refcount. `test_sk_ls_leak()` uses loopback TCP to trigger socket local storage kptr logic before watching map free.

Control flow: `serial_test_map_kptr_race()` runs hash, percpu hash, and socket local-storage leak subtests serially because they observe global/free timing.

State and persistence: two skeleton instances are used: one creates the race state, one watches map free by target map ID. Fds, sockets, and skeletons are closed after each subtest.

Dependencies and integration: depends on `map_kptr_race.skel.h`, fentry/fexit attachment, RCU sync, network helpers, and map IDs.

Risks and test signals: `map_freed == 1` and `read_refs() == 2` prove no leaked extra reference. Risks include timing/poll loops, missing fentry targets, and race behavior differing by kernel implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_kptr_race.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_lock.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_lock.c

Purpose: stresses `BPF_F_LOCK` map operations and BPF spin-lock consistency under concurrent BPF program execution and userspace map reads.

Important APIs and functions: `spin_lock_thread()` repeatedly runs a cgroup skb program 10,000 times through `bpf_prog_test_run_opts()`. `parallel_map_access()` reads map values with `bpf_map_lookup_elem_flags(..., BPF_F_LOCK)` and checks that protected fields are internally consistent. `test_map_lock()` loads `test_map_lock.bpf.o`, finds `hash_map` and `array_map`, seeds the hash map, starts four BPF runner threads and two userspace reader threads, and joins them.

Control flow: load object, get map fds, seed map, run six threads, validate joins, close object.

State and persistence: map elements are mutated by BPF programs and observed by userspace under lock. All fds are transient.

Dependencies and integration: depends on pthreads, `test_map_lock.bpf.o`, cgroup skb test-run support, and lockable map values.

Risks and test signals: consistent arrays in 10,000 reads and zero BPF retval failures are signals. Risks are nondeterministic race failures, scheduling load, and lock ABI changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_lookup_percpu_elem.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_lookup_percpu_elem.c

Purpose: runs skeleton tests for per-CPU element lookup helper behavior.

Important APIs and functions: `test_map_lookup_percpu_elem()` delegates to `RUN_TESTS(test_map_lookup_percpu_elem)`, which loads and runs subtests from the generated skeleton.

Control flow: harness macro manages skeleton load/run and assertion propagation.

State and persistence: per-CPU map state is owned by the BPF fixture and destroyed by the macro.

Dependencies and integration: depends on `test_map_lookup_percpu_elem.skel.h` and selftest macro support.

Risks and test signals: subtest pass/fail is driven by BPF-side assertions and verifier/runtime behavior. The wrapper risk is minimal; fixture/kernel helper semantics are the main risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_lookup_percpu_elem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_ops.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_ops.c

Purpose: validates BPF map operation helpers for update, delete, queue/stack push/pop/peek, and map iteration from instrumented syscall-triggered programs.

Important APIs and functions: small trigger helpers invoke specific syscalls (`getpid`, `getppid`, `getuid`, `geteuid`, `getgid`, `gettid`, `getpgid`). `setup()` opens, loads, and attaches `test_map_ops` with the current PID in rodata. Subtests such as update/delete and queue/stack operations read `skel->bss->err` after each trigger.

Control flow: each subtest creates a fresh skeleton, triggers one or more operations in sequence, checks expected success or errno such as `-EEXIST`, then destroys. The top-level dispatches named subtests.

State and persistence: state is BPF map contents plus BSS error/status fields. Fresh skeletons isolate subtests.

Dependencies and integration: depends on `test_map_ops.skel.h`, syscall trace triggers, and map helper semantics.

Risks and test signals: expected BSS `err` values and map behavior are signals. Risks include syscall attach-point mismatches, map helper errno changes, and queue/stack ordering regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_ptr.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_ptr.c

Purpose: validates BPF-side access to map metadata/pointers using a light skeleton fixture.

Important APIs and functions: `test_map_ptr()` opens `map_ptr_kern.lskel.h`, sets ringbuf `max_entries` to page size before load, loads, stores `page_size` in BSS, and runs `cg_skb` with `bpf_prog_test_run_opts()`.

Control flow: open, configure map, load, set BSS, run program on `pkt_v4`, expect successful syscall and nonzero retval, destroy.

State and persistence: state is a ring buffer map and BSS page-size value inside the skeleton. It is destroyed at cleanup.

Dependencies and integration: depends on light skeleton support, `map_ptr_kern.lskel.h`, packet fixtures, and ringbuf map creation.

Risks and test signals: nonzero program retval after successful test-run means the BPF program observed expected map properties. Risks are page-size assumptions and light-skeleton API changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_ptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mem_rdonly_untrusted.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mem_rdonly_untrusted.c

Purpose: runs verifier/runtime coverage for read-only untrusted memory handling.

Important APIs and functions: the wrapper delegates to `RUN_TESTS(mem_rdonly_untrusted)` through the generated skeleton.

Control flow: top-level macro loads the fixture and executes each declared test program.

State and persistence: no explicit userspace state; verifier and BPF-side fixture state are transient.

Dependencies and integration: depends on `mem_rdonly_untrusted.skel.h` and the BPF selftest harness.

Risks and test signals: signals are skeleton subtest results. Risks are verifier type-name or access-rule changes for `rdonly_untrusted_mem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mem_rdonly_untrusted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/metadata.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/metadata.c

Purpose: tests whether BPF program metadata references keep maps alive only when metadata is actually used.

Important APIs and functions: `prog_holds_map()` compares map IDs reported by `bpf_prog_get_info_by_fd()` against a target map ID from `bpf_map_get_info_by_fd()`. The test loads `metadata_unused` and `metadata_used` skeletons, attaches programs, triggers cgroup/network activity, and checks program map references.

Control flow: for unused metadata, the program should not hold the metadata map. For used metadata, the program should report the map in `nr_map_ids`. Cgroup and socket helpers provide trigger context, then resources are closed.

State and persistence: map/program fds and cgroup attachment are temporary. The tested state is kernel-reported program-to-map ID references.

Dependencies and integration: depends on `metadata_unused.skel.h`, `metadata_used.skel.h`, cgroup helpers, network helpers, and BPF info syscalls.

Risks and test signals: presence or absence of the metadata map ID in program info is the signal. Risks are changes in kernel info reporting or compiler optimization of metadata references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/migrate_reuseport.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/migrate_reuseport.c

Purpose: comprehensive reuseport migration test for child TCP sockets across listener shutdown/relisten flows and TCP states (`ESTABLISHED`, `SYN_RECV`, `NEW_SYN_RECV`) for IPv4 and IPv6.

Important APIs and functions: `setup_fastopen()` temporarily rewrites `/proc/sys/net/ipv4/tcp_fastopen`. `drop_ack()` attaches an XDP program to loopback to hold requests in SYN states; `pass_ack()` detaches it. `start_servers()` creates five `SO_REUSEPORT` listeners and attaches `migrate_reuseport` with `SO_ATTACH_REUSEPORT_EBPF`. `start_clients()` creates 25 clients and writes a fixed message. `update_maps()` maps listener cookies to migration targets. `migrate_dance()` uses shutdown/listen/epoll to force migrations. `count_requests()` accepts all requests and compares userspace and BPF counters.

Control flow: `serial_test_migrate_reuseport()` loads the skeleton and runs eight test cases. `run_test()` resets counters, handles fastopen setup, creates servers/clients, optionally drops final ACKs, updates maps, performs migration dance, optionally waits for SYN+ACK timer or resumes ACKs, counts accepted requests, and restores/cleans all fds/sysctls.

State and persistence: substantial transient state includes listener/client fds, reuseport maps, XDP link, TCP fastopen sysctl value, BSS counters, and TCP request queues. Cleanup closes fds, detaches XDP, and restores fastopen when used.

Dependencies and integration: depends on loopback XDP attach, TCP fast open, reuseport eBPF, epoll, network helpers, and `test_migrate_reuseport.skel.h`.

Risks and test signals: all 25 client messages must arrive at the migration target and matching BPF migration counters must equal 25. Risks include timing in SYN timer tests, sysctl permissions, loopback XDP support, and subtle TCP state-machine changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/migrate_reuseport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/missed.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/missed.c

Purpose: tests BPF perf/ring/event missed-event accounting behavior under constrained buffers or forced overflow scenarios.

Important APIs and functions: the harness uses the companion skeleton, event-buffer setup, callback counters, and selftest assertions to compare produced events and missed counts.

Control flow: setup loads/attaches the fixture, triggers enough events to exceed the consumer capacity, polls/consumes events, then checks that missed accounting matches expectations.

State and persistence: event buffers, counters, and skeleton BSS/map state are transient. No persistent resources remain after destroy.

Dependencies and integration: depends on perf/ring buffer kernel behavior, generated BPF fixture, and selftest event polling helpers.

Risks and test signals: observed missed count is the signal. Risks are timing sensitivity, CPU count differences, buffer sizing, and event-delivery changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/missed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mmap.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mmap.c

Purpose: validates mmap-able BPF map behavior, including shared userspace/kernel visibility, map sizing, page alignment, and access protections.

Important APIs and functions: the test creates/loads the companion skeleton, obtains mmap-able map fds, uses `mmap()`/`munmap()`, reads and writes mapped values, and triggers BPF programs to update map data for cross-checks.

Control flow: subtests map BPF arrays into userspace, verify initial contents, mutate via userspace and BPF paths, check synchronization, and exercise expected failure/protection cases.

State and persistence: mmap regions and map contents are transient; mappings are unmapped and skeletons/fds closed after testing.

Dependencies and integration: depends on `BPF_F_MMAPABLE` map support, page-size alignment, generated fixture, and memory mapping syscalls.

Risks and test signals: matching values seen through syscall lookup, mmap memory, and BPF-side updates are signals. Risks are architecture page-size differences and protection semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/modify_return.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/modify_return.c

Purpose: tests BPF modify-return attachment behavior and interaction between input return values, side effects, and final return codes.

Important APIs and functions: `run_test()` loads `modify_return`, sets BSS/input state, attaches programs, triggers the target function path, and checks packed side-effect/return fields using `LOWER()` and `UPPER()` helpers. `test_modify_return()` runs several input/expected combinations.

Control flow: each scenario loads a fresh skeleton, attaches modify-return/fentry/fexit style programs, invokes the target, validates side effect and returned value, and destroys.

State and persistence: state is skeleton BSS/data counters and return code fields. No persistent resources remain.

Dependencies and integration: depends on `modify_return.skel.h`, trampoline/modify-return kernel support, and stable target behavior.

Risks and test signals: expected side-effect count and signed return value are signals. Risks include attach support differences and target return packing changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/modify_return.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/module_attach.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/module_attach.c

Purpose: tests BPF attachment to functions and writable tracepoints in `bpf_testmod`, including read-only, writable, and detach behavior.

Important APIs and functions: `trigger_module_test_writable()` opens/writes/reads the module sysfs test file. `test_module_attach_prog()` selects skeleton programs by name, attaches, triggers module behavior with requested read/write sizes, and verifies BSS counters. `test_module_attach_writable()` covers writable cases. `test_module_attach_detach()` validates that destroying/detaching a link stops future hits. `test_module_attach()` iterates read and detach program-name arrays.

Control flow: per-program subtests load `test_module_attach`, attach the selected program, trigger module IO, assert outputs, then destroy. Detach tests perform a trigger before and after link destruction.

State and persistence: state is module test sysfs I/O and skeleton BSS counters. BPF links are temporary; module itself is an external prerequisite.

Dependencies and integration: depends on `bpf_testmod`, `test_module_attach.skel.h`, `testing_helpers.h`, sysfs test files, and fentry/fexit/raw tracepoint support as defined by the fixture.

Risks and test signals: correct counter increments and no increments after detach are signals. Risks include missing/unloaded test module, changed sysfs interface, and target symbol renames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/module_attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/module_fentry_shadow.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/module_fentry_shadow.c

Purpose: verifies fentry attachment to a module symbol when local/module BTF shadows or differs from vmlinux BTF.

Important APIs and functions: `get_bpf_testmod_btf_fd()` locates module BTF for `bpf_testmod`. `test_module_fentry_shadow()` loads a raw or skeleton program targeting `bpf_fentry_shadow_test`, configures expected attach BTF information, attaches, triggers the module path, and checks execution.

Control flow: obtain module BTF fd, open/load program with attach target metadata, attach fentry, trigger module function, assert result, cleanup.

State and persistence: temporary BTF fd, BPF program/link, and module-trigger state only.

Dependencies and integration: depends on `bpf_testmod`, module BTF availability, libbpf internal helpers, cgroup/test helpers, and symbol `bpf_fentry_shadow_test`.

Risks and test signals: successful load/attach and observed hit prove correct BTF target resolution. Risks include missing module BTF, symbol rename, and kernel BTF ID resolution changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/module_fentry_shadow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mptcp.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mptcp.c

Purpose: broad MPTCP/BPF integration test covering sockops storage, TCP-to-MPTCP conversion, subflow cgroup hooks, and sockmap behavior with fallback and native MPTCP sockets.

Important APIs and functions: `start_mptcp_server()` uses `IPPROTO_MPTCP`. `verify_tsk()` and `verify_msk()` read socket local storage and validate MPTCP token/first sock/congestion-control data. `test_base()` compares normal TCP and MPTCP sockops. `run_mptcpify()` verifies a BPF program converts a normal TCP connection to MPTCP. `endpoint_init()` creates veths and `ip mptcp endpoint` entries. `test_subflow()` attaches cgroup MPTCP subflow and getsockopt hooks. `test_mptcp_sockmap()` attaches sockmap injection and stream-verdict programs, then tests fallback redirect and rejection of true MPTCP sockets.

Control flow: top-level runs `base`, `mptcpify`, `subflow`, and `sockmap`. Each creates a cgroup and a fresh netns, loads the relevant skeleton, attaches cgroup/sockmap programs, runs socket traffic, validates storage or socket options, and frees netns/cgroup/skeleton resources.

State and persistence: external state includes netns `mptcp_ns`, cgroups, veth endpoints, MPTCP endpoint config, sockets, sockmap entries, and BSS status fields. All are cleaned via helper teardown and fd close.

Dependencies and integration: depends on MPTCP kernel support, `ip mptcp`, cgroup helpers, network helpers, and four skeletons: `mptcp_sock`, `mptcpify`, `mptcp_subflow`, and `mptcp_sockmap`.

Risks and test signals: valid MPTCP token/storage, no fallback flag, remote key received, subflow socket options, successful fallback sockmap redirect, and `-EOPNOTSUPP` for true MPTCP sockmap updates are signals. Risks are MPTCP feature availability, endpoint setup support, and timing while waiting for subflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mptcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/nested_trust.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/nested_trust.c

Purpose: verifies verifier trust propagation for nested pointer acquisition/access scenarios.

Important APIs and functions: `test_nested_trust()` runs `RUN_TESTS(nested_trust_failure)`, `RUN_TESTS(nested_trust_success)`, and `RUN_TESTS(nested_acquire)` through generated skeletons.

Control flow: failure, success, and acquire suites are executed in order, letting the harness validate load failures and successful program behavior.

State and persistence: no explicit userspace state; skeletons and verifier state are transient.

Dependencies and integration: depends on `nested_trust_failure.skel.h`, `nested_trust_success.skel.h`, `nested_acquire.skel.h`, and verifier trust semantics.

Risks and test signals: expected load failures/successes are signals. Risks are verifier diagnostic or trust-propagation rule changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/nested_trust.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/net_timestamping.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/net_timestamping.c

Purpose: validates socket timestamping visibility and BPF-provided timestamp fields for TCP traffic under cgroup programs.

Important APIs and functions: `timespec_to_ns64()`, `validate_key()`, and `validate_timestamp()` check timestamp ordering and tolerance. `test_socket_timestamp()` validates individual `scm_timestamping` entries. `test_recv_errmsg_cmsg()` parses error-queue control messages. `socket_recv_errmsg()` reads error queue data. `test_socket_timestamping()` configures socket timestamping. `test_tcp()` creates IPv4/IPv6 TCP traffic with optional userspace socket timestamping. `test_net_timestamping()` loads/attaches `net_timestamping` and runs subtests.

Control flow: attach cgroup programs, create TCP client/server pairs for IPv4 and IPv6, send data, receive error-queue timestamp messages, validate timestamp keys/types/order and BPF BSS fields, then cleanup sockets and cgroup.

State and persistence: state includes cgroup attachment, sockets, error queue messages, global `usr_ts`, BSS timestamp fields, and flags such as `SK_TS_SCHED`, `SK_TS_TXSW`, `SK_TS_ACK`.

Dependencies and integration: depends on `linux/net_tstamp.h`, error-queue control message format, network helpers, cgroup support, and `net_timestamping.skel.h`.

Risks and test signals: valid keys, monotonic timestamps within tolerance, and expected timestamp types are signals. Risks are timestamp timing variability, kernel timestamping support, and error queue delivery differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/net_timestamping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netcnt.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netcnt.c

Purpose: tests BPF network byte/packet accounting for a cgroup using the `netcnt` fixture.

Important APIs and functions: the harness creates/joins a cgroup, loads and attaches `netcnt`, generates network traffic with helpers, reads map/BSS counters, and compares packet/byte totals.

Control flow: setup cgroup and skeleton, attach ingress/egress accounting programs, run traffic, read counters, assert nonzero/expected deltas, detach and cleanup.

State and persistence: cgroup attachment and accounting maps are transient. Counter values are the tested state.

Dependencies and integration: depends on cgroup helpers, network helpers, `netcnt.skel.h`, and predictable local traffic.

Risks and test signals: packet/byte counters matching generated traffic are signals. Risks include traffic offload/path differences, cgroup join failure, and counter races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netcnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netfilter_link_attach.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netfilter_link_attach.c

Purpose: verifies BPF netfilter program attachment through bpf links, including hook selection and link cleanup.

Important APIs and functions: the harness loads the netfilter skeleton, attaches programs to configured netfilter hooks through link APIs, generates local packet traffic, checks BSS counters or verdict effects, and destroys links.

Control flow: open/load, attach one or more hook programs, trigger traffic, assert hit counters/verdict behavior, close links/skeleton. Negative cases exercise invalid attach combinations where present.

State and persistence: BPF netfilter links are persistent kernel objects while fds are open and are destroyed with skeleton/link cleanup. Packet counters are transient.

Dependencies and integration: depends on kernel BPF netfilter link support, network helpers, and `netfilter_link_attach.skel.h`.

Risks and test signals: hook hit counters and successful link attach/detach are signals. Risks include kernel config differences, netfilter hook ordering, and privilege requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netfilter_link_attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netns_cookie.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netns_cookie.c

Purpose: tests BPF netns cookie retrieval and consistency across sockets/network namespaces.

Important APIs and functions: the harness loads the `netns_cookie` fixture, creates or enters network namespaces, triggers socket operations, and compares BPF-observed cookies against expected userspace/kernel values.

Control flow: setup netns and skeleton, run traffic or socket operations in default and test namespaces, read BSS/map cookie fields, assert identity/difference rules, cleanup namespaces and fds.

State and persistence: netns objects, sockets, and BPF map/BSS cookie records are temporary.

Dependencies and integration: depends on network namespace support, network helpers, generated skeleton, and `bpf_get_netns_cookie()` semantics.

Risks and test signals: stable equal cookies within the same namespace and different cookies across namespaces are signals. Risks include namespace cleanup failures and helper availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netns_cookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ns_current_pid_tgid.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ns_current_pid_tgid.c

Purpose: validates namespace-aware current pid/tgid helper behavior against userspace-created PID namespaces.

Important APIs and functions: the harness loads the companion skeleton, creates child processes/namespaces, triggers BPF programs, and checks BSS/map fields containing namespace pid/tgid values.

Control flow: setup skeleton, fork/clone or run namespace helper paths, trigger the BPF program in parent/child contexts, compare current pid/tgid in namespace and global views, then cleanup child processes and skeleton.

State and persistence: process namespace state and BPF result fields are transient. Child processes must be waited/reaped.

Dependencies and integration: depends on namespace privileges, process helpers, generated skeleton, and pid namespace helper semantics.

Risks and test signals: expected pid/tgid mappings are signals. Risks include environment restrictions on PID namespaces and races around child lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ns_current_pid_tgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/obj_name.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/obj_name.c

Purpose: tests allowed and rejected BPF object names for maps/programs, including length and character constraints.

Important APIs and functions: the harness creates BPF maps/programs or opens skeleton variants with specific names, then checks success or expected errors.

Control flow: iterate valid and invalid names, attempt object creation/load, assert success for accepted names and failure for rejected ones, close fds.

State and persistence: only temporary BPF fds are created. Invalid cases should leave no persistent objects.

Dependencies and integration: depends on BPF object naming rules in the kernel and libbpf syscall wrappers.

Risks and test signals: expected accept/reject outcomes and errno values are signals. Risks are naming policy changes or libbpf pre-validation differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/obj_name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/parse_tcp_hdr_opt.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/parse_tcp_hdr_opt.c

Purpose: tests BPF parsing of TCP header options through the companion fixture, usually covering option iteration and malformed/edge option layouts.

Important APIs and functions: the harness loads `parse_tcp_hdr_opt`, prepares packet or socket traffic fixtures, runs BPF programs, and checks BSS/map results for parsed option values and errors.

Control flow: subtests trigger parsing on constructed or real TCP packets, compare expected option kinds/lengths/status, and destroy the skeleton.

State and persistence: packet buffers, sockets, and BPF result fields are transient.

Dependencies and integration: depends on TCP packet fixtures, network helpers, generated skeleton, and BPF TCP option parsing helpers.

Risks and test signals: exact parsed values and expected rejection of malformed options are signals. Risks include TCP option layout changes in fixtures and verifier/helper behavior changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/parse_tcp_hdr_opt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pe_preserve_elems.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pe_preserve_elems.c

Purpose: verifies `BPF_F_PRESERVE_ELEMS` behavior for perf-event arrays or related map types, ensuring elements survive expected close/update paths.

Important APIs and functions: `test_one_map()` accepts a map/program pair and validates preservation semantics by updating the map, running the program, and checking element state. `test_pe_preserve_elems()` loads `test_pe_preserve_elems` and applies the helper to fixture maps.

Control flow: open/load skeleton, for each map/program scenario update elements, trigger program execution, check preserved entries, and cleanup.

State and persistence: map element contents are the tested transient state. Skeleton destruction releases maps.

Dependencies and integration: depends on `test_pe_preserve_elems.skel.h`, map flags, and BPF program execution helpers.

Risks and test signals: preserved element values after program/map operations are signals. Risks include map flag support changes and fixture map-type behavior differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pe_preserve_elems.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/percpu_alloc.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/percpu_alloc.c

Purpose: validates per-CPU allocation support in BPF maps/local storage and userspace CPU-targeted map operation flags.

Important APIs and functions: `test_array()`, `test_array_sleepable()`, and `test_cgrp_local_storage()` load per-CPU allocation skeletons, set `my_pid` and `nr_cpus`, run selected programs, and check BSS aggregates (`cpu0_field_d`, `sum_field_c`). `test_failure()` runs verifier failures. `test_percpu_map_op_cpu_flag()` is a detailed userspace syscall test for `BPF_F_CPU` and `BPF_F_ALL_CPUS` on lookup/update/batch operations, including invalid combinations and `-ERANGE`. Wrapper helpers run this for percpu array/hash/LRU hash and percpu cgroup storage. `test_map_op_cpu_flag()` confirms CPU flags are rejected on non-percpu array/hash maps.

Control flow: top-level dispatches ten subtests covering BPF-side allocation, sleepable programs, cgroup storage, failure cases, percpu map CPU flags, and non-percpu rejection. The CPU-flag helper clears all CPUs, writes one CPU, checks per-CPU values, then repeats with batch APIs when supported.

State and persistence: cgroup setup, maps, per-CPU values, and BSS counters are transient. Cgroup environment is explicitly cleaned.

Dependencies and integration: depends on `percpu_alloc_array`, `percpu_alloc_cgrp_local_storage`, `percpu_alloc_fail` skeletons, libbpf possible-CPU count, cgroup helpers, and map batch syscalls.

Risks and test signals: correct BSS aggregates, verifier failures, per-CPU value isolation, and expected errors for invalid flags are signals. Risks include CPU count scaling, alignment/roundup expectations, and cgroup storage attachment cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/percpu_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_branches.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_branches.c

Purpose: tests branch stack sampling access from BPF perf-event programs with and without hardware branch sampling support.

Important APIs and functions: `check_good_sample()` and `check_bad_sample()` validate BSS/sample fields from `test_perf_branches`. `test_perf_branches_common()` attaches the BPF program to a perf event fd, triggers execution, and checks sample status. `test_perf_branches_hw()` configures a hardware perf event with branch sampling. `test_perf_branches_no_hw()` covers the no-hardware or unsupported path. `test_perf_branches()` dispatches subtests.

Control flow: create perf event, attach skeleton program, generate workload or self-trigger, inspect whether branch records are present/valid or appropriately unavailable, close perf fd and skeleton.

State and persistence: perf event fd, BPF link/program state, and BSS sample fields are transient.

Dependencies and integration: depends on perf_event_open support, branch sampling hardware/kernel support, pthread/sched helpers, libbpf internals, and `test_perf_branches.skel.h`.

Risks and test signals: valid branch entries for hardware path and clean fallback behavior for no-hardware path are signals. Risks are architecture/perf permission differences, sampling nondeterminism, and hardware feature availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_branches.c -->
