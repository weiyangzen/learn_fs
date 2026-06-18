# subset-b-006799 research

This grouped report covers Linux BPF selftest harness files from `sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests`. Each section preserves the source path and is intended for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_tcp_skb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_tcp_skb.c

## Purpose
Tests cgroup skb ingress/egress programs on TCP connection setup, data transfer, and teardown. It exercises four combinations of client/server placement and close initiator placement relative to a test cgroup, validating observed TCP packet sequences and final socket states.

## Important APIs, types, and functions
Uses `cgroup_tcp_skb.skel.h`, `cgroup_tcp_skb.h`, `cgroup_helpers.h`, and `network_helpers.h`. `install_filters()` attaches egress and ingress programs with `bpf_program__attach_cgroup()` and resets skeleton BSS counters. `talk_to_cgroup()` and `talk_to_outside()` create IPv6 stream sockets, move the current task between root and test cgroup, connect with `connect_fd_to_fd()`, accept, write, and read. `close_connection()` performs half-close/full-close sequencing and waits for packet counters to settle. `test_cgroup_tcp_skb()` orchestrates all scenarios and checks BSS `g_unexpected` and `g_sock_state`.

## Control flow and state
The test creates `/test_cgroup_tcp_skb`, loads the skeleton, attaches a different ingress/egress program pair per scenario, performs connection traffic, validates BPF-observed TCP state, then destroys links before the next scenario. Persistent state is only runtime test state: socket FDs, cgroup FD, BPF links, and skeleton BSS fields (`g_sock_port`, `g_packet_count`, `g_sock_state`, `g_unexpected`). Cleanup closes all FDs, destroys links, cleans cgroup environment, and destroys the skeleton.

## Dependencies and integration points
Depends on cgroup v2 test helpers, IPv6 loopback sockets, generated BPF programs that implement server/client ingress/egress state machines, and test harness assertions. Integrates with the BPF selftest runner through `test_cgroup_tcp_skb()`.

## Risks and test signals
Timing is sensitive around ACK/FIN observation; `close_connection()` uses bounded sleeps and counter stabilization. Failures signal cgroup attachment problems, missed skb hooks, TCP state regression, or unexpected packet classification. The strongest signals are `g_unexpected == 0`, expected `CLOSED`/`TIME_WAIT`, and successful socket IO in each scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_tcp_skb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_v1v2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_v1v2.c

## Purpose
Verifies that a cgroup connect4 BPF policy can block TCP connects both in a pure cgroup v2 environment and when cgroup v1 `net_cls` classid is also active.

## Important APIs, types, and functions
Uses `connect4_dropper.skel.h`, `cgroup_helpers.h`, and `network_helpers.h`. `run_test()` loads the skeleton, sets target server port in BSS, attaches `connect_v4_dropper` to the supplied cgroup, optionally joins classid, and expects `connect_to_fd_opts()` to fail with `EPERM`. `test_cgroup_v1v2()` first verifies baseline connectivity without BPF, then runs cgroup-v2-only and cgroup-v1v2 subcases.

## Control flow and state
State consists of server/client sockets, a cgroup FD, optional classid hierarchy, and BPF BSS `port`. The same server is reused for both policy subcases after baseline connectivity is checked. Cleanup destroys skeletons and classid environment.

## Dependencies and integration points
Requires cgroup helper support, cgroup v1 classid setup, IPv4 TCP sockets, and a generated cgroup connect program. It integrates as a selftest entry point `test_cgroup_v1v2()`.

## Risks and test signals
Main risks are environmental: classid mount/setup failure and port byte-order confusion. Passing signal is an `EPERM` connect failure only after BPF is attached, with baseline connect succeeding beforehand.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_v1v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_xattr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_xattr.c

## Purpose
Tests BPF cgroup xattr reading helpers and cgroupfs xattr access from tracing programs. It validates both skeleton-driven `RUN_TESTS(cgroup_read_xattr)` coverage and an explicit parent/child cgroupfs xattr scenario.

## Important APIs, types, and functions
Uses `set_cgroup_xattr()`, `test__join_cgroup()`, `read_cgroupfs_xattr.skel.h`, and `cgroup_read_xattr.skel.h`. `test_read_cgroup_xattr()` creates `foo/` and `foo/bar/`, sets `user.bpf_test` xattrs to two values, loads and attaches the skeleton, sets `target_pid`, opens a temp file to trigger hooks, and checks BSS booleans `found_value_a` and `found_value_b`.

## Control flow and state
The test persists xattrs on temporary test cgroups and creates `/tmp/selftests_cgroup_xattr` as a trigger file. All state is cleaned by closing cgroup FDs, destroying the skeleton, and unlinking the temp file.

## Dependencies and integration points
Requires cgroupfs xattr support, generated BPF skeletons, and filesystem operations. It integrates with the selftest runner via `test_cgroup_xattr()`.

## Risks and test signals
Risks include filesystems without cgroup xattr support and trigger hook changes. Positive signals are successful xattr setup, skeleton attach, and both BSS discovery flags set after the file open trigger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgrp_kfunc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgrp_kfunc.c

## Purpose
Validates cgroup kfunc acquire/release, map retention, ancestor lookup, ID lookup, and namespace behavior. It also runs negative verifier cases from `cgrp_kfunc_failure`.

## Important APIs, types, and functions
Uses `cgrp_kfunc_success.skel.h`, `cgrp_kfunc_failure.skel.h`, cgroup helpers, `unshare(CLONE_NEWCGROUP)`, `fork()`, and `bpf_prog_test_run_opts()`. `open_load_cgrp_kfunc_skel()` sets target PID before load. `run_success_test()` attaches a named program and triggers mkdir/remove of a test cgroup. `test_cgrp_from_id_ns()` forks, joins a cgroup, unshares cgroup namespace, runs a BPF program directly, and communicates result over a pipe.

## Control flow and state
The top-level test sets up a cgroup environment, loops over success program names, then runs a namespace subtest and generated failure tests. State is held in skeleton BSS (`pid`, `err`, `invocations`), cgroup directories, child process state, and pipe FDs. Cleanup removes cgroups and destroys skeletons.

## Dependencies and integration points
Requires cgroup namespace support, cgroup helper environment, generated success/failure BPF objects, and the selftest harness. `env.has_testmod` is not used here; coverage is focused on core cgroup kfuncs.

## Risks and test signals
Fork/namespace setup can fail under restricted privileges. Passing signals are one invocation after cgroup mkdir/rmdir, zero BSS error, successful direct program run inside cgroup namespace, and expected failures from `RUN_TESTS(cgrp_kfunc_failure)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgrp_kfunc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgrp_local_storage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgrp_local_storage.c

## Purpose
Exercises cgroup local storage behavior across cgroup v2 and v1 net_cls hierarchies, including tracepoint BTF access, cgroup-attached socket programs, recursion safety, verifier rejection, sleepable iterators, and RCU-lock requirements.

## Important APIs, types, and functions
Uses skeletons `cgrp_ls_tp_btf`, `cgrp_ls_recursion`, `cgrp_ls_attach_cgroup`, `cgrp_ls_negative`, and `cgrp_ls_sleepable`. `CGROUP_MODE_SET()` writes global mode into each skeleton BSS. `test_tp_btf()` mutates a cgroup local storage map and validates tracepoint counters. `test_attach_cgroup()` attaches cgroup and tracing programs, opens a TCP connection, and checks socket cookie map values. Sleepable tests use `bpf_program__set_autoload()`, `bpf_program__attach_iter()`, `bpf_iter_create()`, and RCU-specific load expectations.

## Control flow and state
`test_cgrp_local_storage()` runs `cgrp2_local_storage()` then `cgrp1_local_storage()`. The v2 path joins `/cgrp_local_storage`; the v1 path sets up classid and obtains hierarchy ID. Runtime state includes global `is_cgroup1`/`target_hid`, skeleton BSS counters/IDs, cgroup storage maps, socket cookie map entries, sockets, iterator links, and cgroup/classid FDs.

## Dependencies and integration points
Depends on cgroup v1/v2 helpers, network helpers, syscall tracepoints, BPF iterators, cgroup local storage map semantics, and generated verifier-negative programs. It is integrated as a single selftest that fans out through subtests.

## Risks and test signals
Risks include cgroup v1 availability, RCU semantic differences, and iterator support. Signals include successful map update/lookup/delete, exactly three enter/exit counts in the tracepoint case, expected cookie value derived from client port, no recursion deadlock, rejected negative skeleton, and correct cgroup ID from sleepable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgrp_local_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/check_mtu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/check_mtu.c

## Purpose
Tests `bpf_check_mtu()` helper behavior for XDP and TC programs, including direct test-run execution, ifindex lookup, XDP link attach metadata, and `BPF_MTU_CHK_SEGS`.

## Important APIs, types, and functions
Uses `test_check_mtu.skel.h`, `pkt_v4`, `bpf_prog_test_run_opts()`, `bpf_program__attach_xdp()`, `bpf_link_get_info_by_fd()`, and `bpf_tc`-style return expectations. `read_mtu_device_lo()` reads `/sys/class/net/lo/mtu`. XDP and TC helpers set rodata constants (`GLOBAL_USER_MTU`, `GLOBAL_USER_IFINDEX`) before load, then inspect BSS results `global_bpf_mtu_xdp` and `global_bpf_mtu_tc`.

## Control flow and state
`test_ns_check_mtu()` checks XDP attach, reads loopback MTU, then runs XDP and TC subtests with and without explicit ifindex. `test_chk_segs_flag()` temporarily lowers loopback MTU to 10 and restores it. State includes skeleton rodata/BSS, link info, loopback MTU, and transient link MTU modification.

## Dependencies and integration points
Requires loopback device, XDP attach support, TC helper support in prog test-run, and network helper packet fixtures. This is likely run in a network namespace selftest context because it can change `lo` MTU.

## Risks and test signals
Changing loopback MTU is risky if cleanup is interrupted. Attach can fail on kernels without XDP link support. Passing signals are expected retval (`XDP_PASS` or `BPF_OK`), BSS MTU equals user-space MTU, XDP link info reports `BPF_LINK_TYPE_XDP` and ifindex 1, and segs-flag run succeeds after MTU restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/check_mtu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/clone_attach_btf_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/clone_attach_btf_id.c

## Purpose
Verifies that cloning a tracing program preserves or reports the expected attach BTF ID metadata.

## Important APIs, types, and functions
Uses `clone_attach_btf_id.skel.h`, `bpf_prog_get_info_by_fd()`, and `bpf_program__fd()`. `get_prog_attach_btf_id()` reads `struct bpf_prog_info.attach_btf_id`. `test_clone_attach_btf_id()` loads the skeleton and compares attach BTF IDs for relevant programs.

## Control flow and state
The test has minimal runtime state: skeleton object and program FDs. It opens/loads the generated object, queries metadata through kernel BPF info API, asserts equality or expected values, then destroys the skeleton.

## Dependencies and integration points
Depends on generated tracing BPF object and kernel support for `attach_btf_id` in program info. Integrated as a small selftest entry.

## Risks and test signals
Risk is kernel metadata behavior drift. The signal is `bpf_prog_get_info_by_fd()` succeeding and reported attach BTF IDs matching expectations for cloned attach targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/clone_attach_btf_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cls_redirect.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cls_redirect.c

## Purpose
Tests a TC classifier redirect/decapsulation program in three implementations: inlined, subprogram-based, and dynptr-based. It synthesizes GUE-encapsulated IPv4/IPv6 TCP/UDP packets around real socket tuples and checks accept-vs-forward behavior.

## Important APIs, types, and functions
Uses `test_cls_redirect.skel.h`, `test_cls_redirect_dynptr.skel.h`, `test_cls_redirect_subprogs.skel.h`, `progs/test_cls_redirect.h`, and network helpers. `set_up_conn()` creates UDP/TCP server/client pairs and records swapped src/dst addresses. `encap_init()` and `build_input()` construct Ethernet/IP/UDP/GUE/inner IP/TCP-or-UDP packet bytes. `test_cls_redirect_common()` runs a table of `struct test_cfg` cases through `bpf_prog_test_run_opts()` and checks `TC_ACT_REDIRECT` plus output length decapsulation.

## Control flow and state
The test creates known IPv4 and IPv6 sockets for both UDP and TCP, loads each skeleton variant with rodata `ENCAPSULATION_IP` and `ENCAPSULATION_PORT`, and runs seven semantic cases for both families. State is socket FD arrays, generated packet buffers, BPF test-run options, and output size. No persistent state remains after FDs and skeletons are closed.

## Dependencies and integration points
Depends on loopback sockets, packet fixture headers in `test_cls_redirect.h`, generated classifier variants, and TC action constants. Integrated through `test_cls_redirect()` subtests.

## Risks and test signals
Packet construction is byte-order and header-layout sensitive. Connection-known cases depend on socket tuple matching. Passing signals are successful test-run, `retval == TC_ACT_REDIRECT`, and output shrink only for ACCEPT/decap cases while FORWARD cases preserve encapsulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cls_redirect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/compute_live_registers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/compute_live_registers.c

## Purpose
Runs generated verifier coverage for live-register computation.

## Important APIs, types, and functions
Uses `compute_live_registers.skel.h` and `RUN_TESTS(compute_live_registers)` from the selftest harness. The file has no local helpers beyond `test_compute_live_registers()`.

## Control flow and state
Control flow delegates entirely to the generated skeleton test runner. State is whatever the skeleton and harness maintain during open/load/run; this file introduces no persistent state.

## Dependencies and integration points
Depends on the generated BPF object and harness macros. Integrated as a single selftest entry.

## Risks and test signals
Risks are contained in the generated program and verifier expectations. Passing signal is `RUN_TESTS` success for all skeleton-defined subtests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/compute_live_registers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/connect_force_port.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/connect_force_port.c

## Purpose
Tests cgroup connect/getpeername/getsockname programs that rewrite or report forced local and peer ports for IPv4/IPv6 TCP and UDP sockets.

## Important APIs, types, and functions
Uses `bpf_object__open_file()` to load either `connect_force_port4.bpf.o` or `connect_force_port6.bpf.o`, finds `.bss` initial value, attaches programs with `bpf_prog_attach()` to connect/getpeername/getsockname cgroup attach types, and checks sockets with `getsockname()`/`getpeername()`. `verify_ports()` compares host-order expected ports.

## Control flow and state
`test_connect_force_port()` joins `/connect_force_port`, starts four servers (IPv4/IPv6, stream/datagram), and runs `run_test()` for each. `run_test()` seeds BSS with the real server port before load, attaches three cgroup programs, connects, verifies expected local port 22222/22223 and peer port 60000, then closes the BPF object.

## Dependencies and integration points
Requires cgroup connect hooks, cgroup sock address hooks for name queries, IPv4/IPv6 sockets, and external `.bpf.o` files instead of skeletons. Integrated as a cgroup network selftest.

## Risks and test signals
Risk comes from port availability, BSS initial-value manipulation before load, and attach cleanup relying on object close. Passing signals are successful connection and exact observed local/peer port rewrites for all families/types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/connect_force_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/connect_ping.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/connect_ping.c

## Purpose
Tests cgroup connect programs for IPv4 and IPv6 ping sockets, including optional bind behavior that changes the local address.

## Important APIs, types, and functions
Uses `connect_ping.skel.h`, `unshare(CLONE_NEWNET | CLONE_NEWNS)`, sysfs/bpffs mounts, loopback address setup, `write_sysctl()` for ping group range, and cgroup attach helpers. `subtest()` creates datagram ICMP/ICMPv6 sockets, connects to loopback, validates invocation counters and local bound address through `getsockname()`.

## Control flow and state
The top-level function creates isolated network and mount namespaces, remounts `/sys`, mounts bpffs, configures loopback IPv4/IPv6 addresses, joins `/connect_ping`, loads and attaches IPv4/IPv6 connect programs, then runs four subtests: v4, v4-bind, v6, v6-bind. State is namespace-local network config, cgroup FD, skeleton links, and BSS fields `do_bind`, `invocations_v4`, `invocations_v6`, `has_error`.

## Dependencies and integration points
Requires privilege to unshare/mount/configure networking, ping socket permissions, cgroup hooks, and generated skeleton. Integrated into selftests as `test_connect_ping()`.

## Risks and test signals
Environmental setup is the primary risk. Passing signals are exactly one family-specific invocation, no BPF error, and expected local address: loopback when not binding, `1.1.1.1` or `2001:db8::1` when binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/connect_ping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_autosize.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_autosize.c

## Purpose
Tests CO-RE autosizing across a custom 32-bit-pointer target BTF and BPF-side 64-bit target, including same-size, downsize, probed reads, and expected signed-load failure.

## Important APIs, types, and functions
Uses libbpf BTF construction (`btf__new_empty()`, `btf__set_pointer_size()`, `btf__add_int()`, `btf__add_struct()`, `btf__raw_data()`), custom `bpf_object_open_opts.btf_custom_path`, skeleton `test_core_autosize`, and BSS map lookup. A real-layout `test_struct___real` mirrors the custom target BTF.

## Control flow and state
The test writes a temporary BTF file, opens the skeleton with that BTF, disables `handle_signed`, loads and attaches three programs, reads `.bss` into local `out`, and checks all expected values. It then reloads with signed handling enabled and expects load failure. State is temporary `/tmp/core_autosize.btf.*`, BTF object, skeleton links, and BSS output.

## Dependencies and integration points
Depends on libbpf BTF APIs, generated CO-RE skeleton, mmap/lookup of BSS data, and tracepoint attachment. Integrated as a CO-RE selftest.

## Risks and test signals
Risks include BTF encoding mistakes, pointer-size assumptions, and temp-file cleanup. Passing signals are exact values for same-sized/down-sized/probed reads and an expected load error for signed autosize handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_autosize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_extern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_extern.c

## Purpose
Validates CO-RE external kconfig variable handling, including default kernel config lookup, custom kconfig strings, booleans/tristates/chars/strings/integer parsing, bounds, and expected load failures.

## Important APIs, types, and functions
Uses `test_core_extern.skel.h`, `bpf_object_open_opts.kconfig`, `uname()` plus `KERNEL_VERSION()`, skeleton data section comparison, and table-driven `struct test_case`. Each case carries config text, expected failure flag, and expected `test_core_extern__data`.

## Control flow and state
For each test case, the skeleton is opened with optional custom kconfig, loaded, attached, triggered by `usleep(1)`, and then its data section is compared word-by-word with expected data after filling dynamic kernel version and missing value. State is per-case skeleton data; no external persistence.

## Dependencies and integration points
Depends on libbpf kconfig extern resolution, generated tracepoint program, and kernel version parsing from `uname`. Integrated as `test_core_extern()`.

## Risks and test signals
Parsing edge cases are intentional risk areas. Test signals are load failure for bad configs and exact data-section equality for successful configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_extern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_kern.c

## Purpose
Tests lightweight skeleton CO-RE relocations against kernel BTF for prototype/type existence behavior.

## Important APIs, types, and functions
Uses `core_kern.lskel.h`. `test_core_kern_lskel()` calls `core_kern_lskel__open_and_load()`, attaches `core_relo_proto`, triggers tracepoints with `usleep(1)`, and checks `proto_out[]`.

## Control flow and state
State is limited to the lightweight skeleton and BSS `proto_out`. Link FD is returned by generated attach helper and cleaned by skeleton destruction.

## Dependencies and integration points
Depends on vmlinux BTF and lightweight skeleton support. Integrated as `test_core_kern_lskel()`.

## Risks and test signals
Risk is kernel BTF or lskel attach support drift. Passing signals are true/false/true values in `proto_out` for expected type-existence queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_kern_overflow.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_kern_overflow.c

## Purpose
Ensures a lightweight skeleton with overflowing or invalid kernel CO-RE relocation fails to open/load.

## Important APIs, types, and functions
Uses `core_kern_overflow.lskel.h` and `ASSERT_NULL()` around `core_kern_overflow_lskel__open_and_load()`.

## Control flow and state
There is no long-lived state. If an unexpected skeleton is returned, it is destroyed after the assertion.

## Dependencies and integration points
Depends on generated lskel and verifier/libbpf relocation rejection. Integrated through `test_core_kern_overflow_lskel()`.

## Risks and test signals
The main signal is negative: open/load must return NULL. A successful load would indicate lost overflow validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_kern_overflow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_read_macros.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_read_macros.c

## Purpose
Tests BPF CORE/probe read macros for kernel and user memory, including a flavored/shuffled user struct.

## Important APIs, types, and functions
Uses `test_core_read_macros.skel.h`, local `callback_head` and `callback_head___shuffled`, skeleton BSS pointers/embedded structs, and tracepoint attach. The test seeds kernel-side BSS structs and user-space local structures, then checks output fields.

## Control flow and state
The skeleton is opened/loaded, BSS `my_pid` and input pointers/fields are initialized, the skeleton attaches, a tracepoint is triggered by sleep, and BSS outputs are compared to constants. User pointers reference stack locals during the attached interval only.

## Dependencies and integration points
Depends on generated BPF programs, user memory read support, kernel memory read helpers, and CO-RE field flavor matching. Integrated as `test_core_read_macros()`.

## Risks and test signals
Stack lifetime and pointer validity are important. Passing signals are exact output constants for kernel probe/core and user probe/core read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_read_macros.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_reloc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_reloc.c

## Purpose
Provides comprehensive CO-RE relocation testing. It covers kernel/module BTF, struct flavors, nesting, arrays, primitives, modifiers, pointer-as-array, integer signedness, field existence, bitfields, size/offset relocations, type existence/match/size, type IDs, enum values including 64-bit enum values, and btfgen-generated minimal BTFs.

## Important APIs, types, and functions
Central type is `struct core_reloc_test_case`, with object file, target BTF file, input/output byte blobs, expected failure flags, attach program/raw tracepoint names, optional setup, optional trigger, and testmod requirement. Many macros generate table rows. `setup_type_id_case_*()` parses local and target BTFs to fill expected type IDs. `run_btfgen()` invokes `./bpftool gen min_core_btf`. `run_core_reloc_tests()` opens BPF objects with optional `btf_custom_path`, loads, mmaps `.bss`, copies input, attaches raw tracepoint/tp_btf, triggers, and compares output bytes.

## Control flow and state
`test_core_reloc()` runs the table directly; `test_core_reloc_btfgen()` reruns supported cases through generated minimal BTF files. Each subtest may skip if it requires unavailable testmod, lacks target BTF for btfgen, or marks btfgen failure. Runtime state includes temporary `/tmp/core_reloc.btf.*`, mmaped `.bss` struct `data`, BPF object/link/map handles, and expected blobs from static table data. Cleanup unmaps, removes temp BTF, destroys links, and closes objects per case.

## Dependencies and integration points
Depends on many generated `.bpf.o` and `btf__core_reloc_*.bpf.o` files, vmlinux/module BTF, optional `bpf_testmod`, `bpftool`, libbpf BTF APIs, raw tracepoint attachment, and shared CO-RE type definitions. It is a high-value integration point between libbpf relocation logic and kernel verifier/runtime execution.

## Risks and test signals
Risks include brittle expected byte blobs, missing BTF files, absent `bpftool`, module availability, and table entries whose failure semantics differ between direct and btfgen modes. Passing signals are successful load/attach for positive cases, expected load failures for negative cases, no BPF-set skip flag, and exact `memcmp()` of BSS output against expected output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_reloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_reloc_raw.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_reloc_raw.c

## Purpose
Tests raw BPF syscall handling for a CO-RE relocation that references a non-existent local BTF type ID, which cannot be expressed through normal libbpf loading.

## Important APIs, types, and functions
Uses handcrafted raw BTF (`struct test_btf`), `bpf_btf_load()`, `sys_bpf_prog_load()`, raw `union bpf_attr`, `bpf_func_info`, and `bpf_core_relo`. `test_bad_local_id()` sets relocation `type_id = 100500` and asserts verifier log contains the bad type ID message.

## Control flow and state
The test loads raw BTF, then attempts direct program load with one relocation. Program load is expected to fail. State is limited to BTF FD, optional program FD, and static log buffer.

## Dependencies and integration points
Depends on BPF syscall ABI, verifier log behavior, and test BTF encoding helpers. Integrated via `test_core_reloc_raw()` subtest `bad_local_id`.

## Risks and test signals
Verifier log wording is part of the assertion and can drift. Passing signal is rejected program load plus log substring `relo #0: bad type id 100500`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_reloc_raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_retro.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_retro.c

## Purpose
Validates backwards-compatible CO-RE behavior in `test_core_retro` by attaching a kprobe-like program, filtering by current TGID, and checking result map state after a trigger.

## Important APIs, types, and functions
Uses `test_core_retro.skel.h`, `bpf_map__update_elem()` on `exp_tgid_map`, skeleton attach, and result map/BSS checks.

## Control flow and state
The test opens/loads the skeleton, writes current PID into a map keyed by zero, attaches probes, triggers execution, reads expected result, and closes the skeleton. State is map-backed expected TGID and runtime skeleton output.

## Dependencies and integration points
Depends on generated BPF object and kernel probe/CO-RE support. Integrated as `test_core_retro()`.

## Risks and test signals
Risk is that process filtering or probe trigger does not fire. Passing signals are successful map update/attach and expected result value after trigger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_retro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cpu_mask.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cpu_mask.c

## Purpose
Unit-tests CPU mask string parsing/formatting helpers from libbpf internals against a table of valid and invalid CPU-list strings.

## Important APIs, types, and functions
Uses `parse_cpu_mask_str()` from `bpf/libbpf_internal.h`. `validate_mask()` compares parsed boolean mask arrays to expected strings. Test cases include ranges, commas, whitespace/duplicates, and invalid syntax.

## Control flow and state
The test iterates static cases, calls parser, and validates either failure or per-CPU booleans. State is local allocated/filled mask arrays; no persistence.

## Dependencies and integration points
Depends on libbpf internal parser and BTF include ordering only. Integrated as `test_cpu_mask()`.

## Risks and test signals
Risks are parser behavior changes and case naming mismatch. Passing signals are successful parse for valid cases, rejected invalid inputs, and exact expected mask bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cpu_mask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cpumask.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cpumask.c

## Purpose
Validates BPF cpumask kfunc success cases and verifier failure cases.

## Important APIs, types, and functions
Uses `cpumask_success.skel.h`, `cpumask_failure.skel.h`, a table of success program names, `bpf_object__find_program_by_name()`, `bpf_program__set_autoload()`, skeleton load/attach, and BSS error checks.

## Control flow and state
For each success program, the skeleton is opened, only the named program is autoloaded, loaded/attached or test-run as defined by the skeleton, and error state is checked. Then `RUN_TESTS(cpumask_failure)` executes negative coverage. State is skeleton BSS and per-program autoload setting.

## Dependencies and integration points
Depends on kernel cpumask kfunc support, generated success/failure BPF objects, and selftest harness. Integrated through `test_cpumask()`.

## Risks and test signals
Risks include missing kfunc support and verifier semantic changes. Signals are zero BSS errors for success cases and expected verifier failure for negative programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cpumask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/crypto_sanity.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/crypto_sanity.c

## Purpose
Tests BPF crypto helper setup plus TC egress encryption/decryption sanity against Linux AF_ALG AES-ECB output.

## Important APIs, types, and functions
Uses `crypto_sanity.skel.h`, `crypto_basic.skel.h`, AF_ALG sockets (`socket(AF_ALG)`, `bind`, `setsockopt(ALG_SET_KEY)`, `accept`, `sendmsg` with `ALG_SET_OP`), `bpf_tc_hook_create()`, `bpf_tc_attach()`, `bpf_prog_test_run_opts()`, and network namespace helpers. `do_crypt_afalg()` computes reference ciphertext/plaintext.

## Control flow and state
`test_crypto_basic()` delegates to generated basic tests. `test_crypto_sanity()` creates a netns, configures IPv6 loopback, initializes AF_ALG, seeds BPF BSS key/algo/authsize, runs setup program, attaches encrypt TC program, sends UDP plaintext, compares BPF destination buffer against AF_ALG encryption, detaches, attaches decrypt program, sends ciphertext, and compares decrypted output. State includes netns, AF_ALG FDs, TC hook/filter state, skeleton BSS/data, and UDP sockets.

## Dependencies and integration points
Requires `ip` tooling, netns privilege, AF_ALG skcipher `ecb(aes)`, TC BPF support, loopback device, and generated skeletons. Integrated as two selftest entry points.

## Risks and test signals
Risks include unavailable crypto algorithm, namespace setup failure, TC hook cleanup, and fixed block-size assumptions. Passing signals are zero BSS status after setup/encrypt/decrypt and byte equality with AF_ALG reference output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/crypto_sanity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ctx_rewrite.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ctx_rewrite.c

## Purpose
Validates verifier context access rewriting by loading tiny raw BPF programs that read/write specific context fields, disassembling translated instructions, and matching them against BTF-aware patterns.

## Important APIs, types, and functions
Defines `struct test_case` with program type, expected attach type, field offset/size, and read/write patterns. Uses raw `BPF_LDX_MEM`, `BPF_STX_MEM`, `BPF_ST_MEM`, `bpf_prog_load()`, `get_xlated_program()`, `disasm_insn()`, `btf__load_vmlinux_btf()`, and POSIX regex. `match_pattern()` substitutes `$ctx/$src/$dst`, resolves `type::field` and grouped offsets through BTF, ignores whitespace/semicolons, and prints side-by-side mismatches.

## Control flow and state
`test_ctx_rewrite()` compiles regexes, loads vmlinux BTF, and runs every static case. `run_one_testcase()` builds up to three minimal programs per case (read, STX write, ST write), then `match_program()` loads, retrieves translated code, disassembles into memory, and matches the pattern. State is local regex objects, vmlinux BTF, generated instruction arrays, program FDs, translated instruction buffers, and disassembly text.

## Dependencies and integration points
Depends on vmlinux BTF, verifier rewrite logic, disassembly helpers, architecture-specific instruction output, and program types such as SCHED_CLS, CGROUP_SOCK, SOCK_OPS, CGROUP_SYSCTL, and CGROUP_SOCKOPT. Integrated as a detailed verifier regression test.

## Risks and test signals
Risks are architecture-specific disassembly differences, BTF field layout drift, and pattern brittleness. Passing signal is every generated program loading and its translated instructions matching BTF-resolved expected patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ctx_rewrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/custom_sec_handlers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/custom_sec_handlers.c

## Purpose
Tests libbpf custom SEC handler registration, setup/preload/attach callbacks, fallback handlers, and overriding built-in-like prefixes.

## Important APIs, types, and functions
Uses `libbpf_register_prog_handler()`, `libbpf_unregister_prog_handler()`, `libbpf_prog_handler_opts`, generated `test_custom_sec_handlers.skel.h`, callback cookies, `bpf_program__attach_raw_tracepoint()`, and `bpf_program__attach_tracepoint()`. Constructor registers `abc`, `abc/`, and `custom+`; destructor unregisters them. Runtime registers `kprobe+` and fallback NULL handler.

## Control flow and state
Callbacks alter autoload (`abc1` disabled), set `BPF_F_SLEEPABLE` for fallback, and attach selected custom programs. The test opens skeleton, validates inferred program types/autoload, loads, auto-attaches, verifies an unsupported manual attach error, triggers with sleep, and checks BSS called flags. Global state is handler IDs and callback cookies.

## Dependencies and integration points
Depends on libbpf section handler API and generated skeleton section names. It is tightly integrated with libbpf loader behavior, including fallback matching order.

## Risks and test signals
Handler registration is global process state; cleanup correctness matters. Passing signals include positive handler IDs, expected program types/autoload, successful load/attach, `EOPNOTSUPP` for unsupported attach, called flags true only for auto-attached sections, and unregister success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/custom_sec_handlers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/d_path.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/d_path.c

## Purpose
Tests `bpf_d_path` helper behavior for stat/close hooks, verifier rejection of wrong memory/type usage, and verifier-generated memory access after helper writes.

## Important APIs, types, and functions
Uses `test_d_path.skel.h`, `test_d_path_check_rdonly_mem.skel.h`, `test_d_path_check_types.skel.h`, `readlink("/proc/<pid>/fd/<fd>")`, `close_range` syscall wrapper, and file/socket/pipe triggers. `trigger_fstat_events()` opens pipe, socket, proc, dev, deleted temp file, and `/tmp` O_PATH, records expected paths, stats/closes them. `attach_and_load()` loads/attaches and sets BSS `my_pid`.

## Control flow and state
`test_d_path()` runs basic path comparison, two negative load tests, and memory-access test. Basic subtest compares BPF-captured `paths_stat` and `paths_close` plus return lengths to user-space `src.paths`. Memory-access subtest creates a deleted shm file and expects BPF to match fallocate path. State includes global expected path array, temporary files, open FDs, and skeleton BSS arrays/flags.

## Dependencies and integration points
Requires BPF trampolines/hooks for `security_inode_getattr` and `filp_close`, procfs/dev/tmp availability, close_range syscall number fallback, and helper verifier support. Integrated through subtests.

## Risks and test signals
Path strings can vary by filesystem or deleted-file formatting. Passing signals are hooks called, every expected path equal for stat and close, helper return lengths include NUL, negative skeletons rejected, and memory-access path match set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/d_path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/decap_sanity.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/decap_sanity.c

## Purpose
Runs a namespace-level decapsulation sanity test for the generated `decap_sanity` BPF program, using IPv6 loopback and a fixed UDP test port.

## Important APIs, types, and functions
Uses `decap_sanity.skel.h`, network helpers, `ip netns` setup, socket APIs, and BPF program attach/test-run paths inside the generated skeleton.

## Control flow and state
The test creates a named netns, configures IPv6 loopback address `face::1`, loads/attaches the skeleton, sends or tests UDP traffic to port 7777 as defined by the BPF object, validates BSS status, and deletes the namespace. Runtime state is namespace config, sockets, and skeleton state.

## Dependencies and integration points
Depends on `ip` tooling, namespace privileges, IPv6 loopback support, and generated decapsulation BPF program. Integrated as `test_decap_sanity()`.

## Risks and test signals
Environmental namespace setup is the main risk. Signals are successful skeleton load/attach, UDP trigger completion, and BPF status/counters showing expected decapsulation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/decap_sanity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/deny_namespace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/deny_namespace.c

## Purpose
Tests LSM/cgroup-like policy for denying namespace creation under selected credential/capability conditions.

## Important APIs, types, and functions
Uses `test_deny_namespace.skel.h`, `cap_helpers.h`, `fork()`, `waitpid()`, `unshare()`/user namespace creation helpers, and test subfunctions for privileged BPF-denied and unprivileged no-BPF cases. `wait_for_pid()` normalizes child exit handling.

## Control flow and state
The file loads/attaches the deny-namespace skeleton for one subtest, forks children to attempt namespace creation, and checks child status. Another subtest drops/adjusts capabilities to validate unprivileged behavior without BPF. State is child PIDs, capability state, and skeleton BSS if used.

## Dependencies and integration points
Requires user namespace support, capabilities manipulation, generated LSM skeleton, and kernel namespace policy hooks. Integrated as `test_deny_namespace()`.

## Risks and test signals
Host sysctls may disable unprivileged user namespaces. Passing signals are expected child exit statuses: BPF-denied creation fails where policy applies, and no-BPF unprivileged behavior matches kernel configuration assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/deny_namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/dmabuf_iter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/dmabuf_iter.c

## Purpose
Tests BPF dma-buf iterator programs, including default iterator output, no infinite reads, large output from many buffers, and open-coded iterator use.

## Important APIs, types, and functions
Uses `dmabuf_iter.skel.h`, `/dev/udmabuf`, `/dev/dma_heap/system`, `memfd_create()`, `UDMABUF_CREATE`, `DMA_HEAP_IOCTL_ALLOC`, `DMA_BUF_SET_NAME_B`, `bpf_iter_create()`, `getline()`, map updates/lookups, and `bpf_prog_test_run_opts()`. `create_udmabuf()` and `create_sys_heap_dmabuf()` create named buffers. `DmabufInfo` parses iterator output fields.

## Control flow and state
The test opens/loads skeleton, seeds a hash map with expected buffer names, creates two test dma-bufs, attaches iterator programs, runs subtests, optionally creates 100 additional system-heap buffers, then destroys all FDs and skeleton. State includes global dma-buf FDs/sizes/names, BPF map keyed by names, iterator FDs/files, and parsed output.

## Dependencies and integration points
Requires dma-buf kernel support, `/dev/udmabuf`, `/dev/dma_heap/system`, ioctl support, BPF iterator support, and generated skeleton. Integrated as `test_dmabuf_iter()`.

## Risks and test signals
Device availability is the biggest risk. Passing signals are iterator reads eventually returning zero, expected named udmabuf and system heap buffers found with correct size/exporter, large output exceeding 4096 bytes with many buffers, and open-coded iteration marking map entries found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/dmabuf_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/dummy_st_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/dummy_st_ops.c

## Purpose
Tests dummy struct_ops program loading/test-run behavior, argument marshaling, fentry attachment to struct_ops programs, sleepable invocation, null rejection, and negative verifier cases.

## Important APIs, types, and functions
Uses `dummy_st_ops_success.skel.h`, `dummy_st_ops_fail.skel.h`, `trace_dummy_st_ops.skel.h`, `bpf_map__attach_struct_ops()`, `bpf_prog_test_run_opts()`, `bpf_program__set_attach_target()`, and `struct bpf_dummy_ops_state`. Subtests cover return value, pointer argument mutation, multiple arguments, sleepable program, and null pointer rejection.

## Control flow and state
Each subtest loads its own skeleton, optionally attaches tracing skeleton to a target BPF program, runs the target through `bpf_prog_test_run_opts()` with explicit context args, checks return values/BSS, and destroys skeletons. `test_dummy_st_ops()` also runs failure skeleton tests. State is local ctx arrays, dummy state structs, trace BSS, and skeleton BSS.

## Dependencies and integration points
Depends on kernel dummy struct_ops test hook, generated success/fail/trace objects, tracing attach support, and prog test-run for struct_ops-like programs.

## Risks and test signals
Kernel support may be absent or attach intentionally unsupported. Passing signals include `-EOPNOTSUPP` for actual struct_ops attach, expected return values, pointer mutation to `0x5a`, fentry observed original value, captured multiple args, sleepable run success, `-EINVAL` for null, and negative skeleton failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/dummy_st_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/dynptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/dynptr.c

## Purpose
Tests many successful BPF dynptr operations and generated failure cases across syscall-sleepable, skb, skb tracepoint, and XDP execution contexts.

## Important APIs, types, and functions
Uses `dynptr_success.skel.h`, `dynptr_fail.skel.h`, `network_helpers.h`, `bpf_prog_test_run_opts()`, `bpf_program__attach()`, `bpf_prog_test_load()` for auxiliary skb tracepoint triggering, and a table mapping program names to setup type. Success cases include dynptr read/write/data/copy/memset, skb metadata/data, ringbuf, adjust, null/readonly checks, clone, string compares, probe reads, and user-copy helpers.

## Control flow and state
For each success case, only the named program is autoloaded, BSS `pid`, `user_ptr`, `expected_str`, and data `test_len` are initialized, then the selected setup path triggers execution. XDP uses a large buffer, with size adjusted for 64K page systems. After trigger, BSS `err` must be zero. Negative cases are delegated to `RUN_TESTS(dynptr_fail)`.

## Dependencies and integration points
Depends on dynptr helper/kfunc support, generated success/fail BPF objects, packet fixtures, test-run support for XDP and skb programs, and auxiliary `test_pkt_access.bpf.o`.

## Risks and test signals
Risks include page-size-specific XDP bounds and context-specific helper availability. Passing signal is zero BSS error for all success programs and expected verifier rejection in failure skeleton tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/dynptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/empty_skb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/empty_skb.c

## Purpose
Tests generated BPF behavior against an empty skb or minimal packet context.

## Important APIs, types, and functions
Uses `empty_skb.skel.h`, `network_helpers.h`, and network interface helpers. The top-level `test_empty_skb()` loads and runs skeleton-defined programs against empty or synthetic skb data.

## Control flow and state
The file delegates most logic to the generated skeleton. Runtime state is skeleton object, possible test-run packet/context buffers, and BSS/result fields from the BPF program.

## Dependencies and integration points
Depends on generated BPF object, skb test-run support, and network helper fixtures. Integrated as a simple selftest entry.

## Risks and test signals
Risk is primarily kernel handling of zero-length skb data. Passing signal is skeleton test success without verifier/runtime faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/empty_skb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/enable_stats.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/enable_stats.c

## Purpose
Runs generated tests for enabling BPF runtime statistics.

## Important APIs, types, and functions
Uses `test_enable_stats.skel.h` and selftest skeleton helpers inside `test_enable_stats()`.

## Control flow and state
The function opens/loads/runs generated programs and checks stats as encoded in the skeleton. This file keeps no custom persistent state.

## Dependencies and integration points
Depends on kernel support for BPF stats and the generated skeleton. Integrated as `test_enable_stats()`.

## Risks and test signals
Risks include stats support disabled or permission issues. Passing signal is generated skeleton success and expected stats observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/enable_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/endian.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/endian.c

## Purpose
Tests BPF endian conversion helpers/macros for 16-, 32-, and 64-bit values.

## Important APIs, types, and functions
Uses `test_endian.skel.h`, constants `IN16/IN32/IN64` and expected byte-swapped `OUT16/OUT32/OUT64`, and skeleton BSS/data fields populated by generated programs.

## Control flow and state
The test loads/attaches or test-runs the skeleton, triggers conversion, and checks outputs against constants. State is only skeleton runtime state.

## Dependencies and integration points
Depends on generated BPF program and selftest harness. Integrated as `test_endian()`.

## Risks and test signals
Risk is endian assumptions across host architectures; expected constants encode byte swaps. Passing signal is exact equality for all conversion widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/endian.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/exceptions.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/exceptions.c

## Purpose
Tests BPF exception support, including successful exception/throw/catch-style execution, verifier/load failures, extension attach behavior, and assertion helper behavior.

## Important APIs, types, and functions
Uses `exceptions.skel.h`, `exceptions_ext.skel.h`, `exceptions_fail.skel.h`, `exceptions_assert.skel.h`, large verifier log buffer, `bpf_prog_test_run_opts()`, and macros such as `RUN_SUCCESS` and `RUN_EXT` to encode expected return values, load/attach errors, and BSS side effects.

## Control flow and state
`test_exceptions()` runs failure, success, extension, and assertion subtests. Success paths run individual skeleton programs through test-run and compare retval/BSS state. Failure paths expect load rejection and inspect log/error conditions. Extension paths load base and extension skeletons with specified attach expectations. State is skeleton BSS/data, links, test-run contexts, and verifier log text.

## Dependencies and integration points
Depends on kernel BPF exception feature support, generated success/fail/extension/assert BPF objects, verifier log behavior, and prog test-run. Integrated as a feature-level selftest.

## Risks and test signals
Exception semantics are evolving and verifier logs can drift. Passing signals are expected load failures for invalid cases, exact return values for success programs, correct extension attach outcomes, and assertion behavior matching generated expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/exceptions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/exe_ctx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/exe_ctx.c

## Purpose
Tests execution context behavior for generated `test_ctx` BPF programs.

## Important APIs, types, and functions
Uses `test_ctx.skel.h`, syscall helpers, and the selftest harness. `test_exe_ctx()` loads/attaches the skeleton and triggers relevant syscalls to validate context values.

## Control flow and state
Runtime state is skeleton BSS/output and the current task/syscall context. The file does not persist external artifacts.

## Dependencies and integration points
Depends on generated skeleton and syscall tracepoint/kprobe support. Integrated as `test_exe_ctx()`.

## Risks and test signals
Risks are hook availability and context layout drift. Passing signals are skeleton assertions or BSS checks succeeding after syscall trigger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/exe_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/exhandler.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/exhandler.c

## Purpose
Tests generated exception-handler kernel BPF behavior through `exhandler_kern` skeleton.

## Important APIs, types, and functions
Uses `exhandler_kern.skel.h` and selftest load/attach/run helpers. `test_exhandler()` delegates to the skeleton and checks expected output.

## Control flow and state
The file has simple open/load/attach/trigger/cleanup flow, with state in skeleton BSS and links.

## Dependencies and integration points
Depends on generated BPF object and kernel support for the tested exception-handler mechanism. Integrated as `test_exhandler()`.

## Risks and test signals
Risk is feature availability or verifier behavior drift. Passing signal is successful skeleton execution with expected BSS/result values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/exhandler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fd_array.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fd_array.c

## Purpose
Tests `BPF_PROG_LOAD` `fd_array` semantics for extra map/BTF references: normal use, duplicates, already referenced maps, BTF lifetime, invalid FDs, and too many FDs.

## Important APIs, types, and functions
Uses raw map creation (`bpf_map_create()`), raw BTF load (`bpf_btf_load()`), `bpf_prog_load()` with `bpf_prog_load_opts.fd_array`, `bpf_prog_get_info_by_fd()` map IDs, `bpf_map_get_fd_by_id()`, `bpf_btf_get_fd_by_id()`, and `kern_sync_rcu()`. Helper `__load_test_prog()` builds a tiny XDP program using one map.

## Control flow and state
Subtests create maps/BTFs, load a program with specified fd arrays, inspect bound map IDs, close original FDs, and verify kernel object lifetimes. BTF lifetime test waits for program cleanup after closing program FD. Invalid cases expect `-EBADF`, `-EINVAL`, or `-E2BIG`. State is FDs, kernel object IDs, and short-lived loaded programs.

## Dependencies and integration points
Depends on BPF syscall support for `fd_array`, map/BTF refcounting, RCU synchronization helper, and verifier acceptance of the tiny XDP program. Integrated as `test_fd_array_cnt()`.

## Risks and test signals
Lifetime checks can be timing-sensitive. Passing signals include expected map ID counts, objects staying alive while program holds refs, BTF disappearing after program cleanup, and exact errors for trash/oversized arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fd_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fd_htab_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fd_htab_lookup.c

## Purpose
Stress-tests concurrent lookup and update of an outer hash map containing inner map IDs, validating safe fd lookup while maps are being replaced and freed.

## Important APIs, types, and functions
Uses `fd_htab_lookup.skel.h`, pthreads, `bpf_map_create()`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, and `bpf_map_get_fd_by_id()`. `htab_lookup_fn()` repeatedly reads IDs from the outer map, obtains inner FDs, and checks inner value equals key. `htab_update_fn()` repeatedly creates/replaces inner arrays. `setup_htab()` seeds the map.

## Control flow and state
The test loads the skeleton, obtains `outer_map` FD, initializes eight entries, starts eight writer and sixteen reader threads, joins all, and requires every thread return NULL. Runtime state is shared `htab_op_ctx` with fd, loop count from `FD_HTAB_LOOP_NR`, entry count, and stop flag.

## Dependencies and integration points
Depends on map-in-map semantics, map ID lookup, pthreads, generated skeleton map definition, and kernel refcount correctness under concurrency.

## Risks and test signals
Concurrent `stop` flag is not atomic but used only as a coarse test stop. Passing signal is no lookup/update error, no stale invalid inner map errors except tolerated `-ENOENT`, and all threads joining with NULL return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fd_htab_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fentry_fexit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fentry_fexit.c

## Purpose
Tests that fentry and fexit lightweight skeletons can be loaded/attached together and observe expected counters.

## Important APIs, types, and functions
Uses `fentry_test.lskel.h` and `fexit_test.lskel.h`. `test_fentry_fexit()` opens/loads/attaches both skeletons and validates combined behavior.

## Control flow and state
State is the two lskel objects, links, and BSS counters. The test triggers target functions indirectly through sleep or skeleton attach behavior and then cleans both skeletons.

## Dependencies and integration points
Depends on BTF-enabled fentry/fexit attach support and generated lightweight skeletons. Integrated as a combined tracing selftest.

## Risks and test signals
Risk is attach target availability. Passing signal is successful load/attach and expected fentry/fexit BSS counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fentry_fexit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fentry_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fentry_test.c

## Purpose
Tests fentry attach behavior for normal and many-argument target functions.

## Important APIs, types, and functions
Uses `fentry_test.lskel.h`, `fentry_many_args.skel.h`, shared `fentry_test_common()`, generated attach helpers, and BSS counters/results.

## Control flow and state
`fentry_test()` runs the lightweight skeleton path; `fentry_many_args()` runs the many-arguments skeleton path. Both load/attach, trigger target functions, and check BSS values. State is skeleton BSS and links.

## Dependencies and integration points
Depends on fentry trampoline support and generated target/trace programs. Integrated via `test_fentry_test()` subtests.

## Risks and test signals
Risk is function prototype or trampoline ABI drift. Passing signal is expected counts and argument values in BSS after triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fentry_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_bpf2bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_bpf2bpf.c

## Purpose
Comprehensively tests tracing and extension programs attached to BPF-to-BPF functions: fexit, freplace, fmod_ret rejection, multiple replacement attachments, cgroup BPF fentry, program-map compatibility, and invalid replacement cases.

## Important APIs, types, and functions
Uses many external `.bpf.o` files plus skeletons `bind4_prog`, `freplace_progmap`, and `xdp_dummy`. `test_fexit_bpf2bpf_common()` loads target object, gets target program ID/BTF, sets attach targets for all programs in the tracing/replacement object, loads, attaches traces, validates `bpf_link_info` target object/BTF IDs, optionally runs target with `bpf_prog_test_run_opts()`, and checks internal data map. Helpers cover second attach, load-failure log assertions, manual fentry load with `attach_prog_fd`/`attach_btf_id`, and cpumap owner compatibility.

## Control flow and state
`serial_test_fexit_bpf2bpf()` runs many subtests serially because they can affect other tests. Runtime state includes target/tracing BPF objects, arrays of programs/links, target program IDs/BTF IDs, internal data maps, cgroup FD for cgroup BPF fentry, and cpumap update state. Cleanup destroys links and closes all objects per subtest.

## Dependencies and integration points
Depends on BPF trampoline, fexit/fentry/freplace, BTF function metadata, cgroup BPF attach, XDP/cpumap maps, verifier diagnostics, and numerous generated target objects. It is a central integration test for tracing/ext programs.

## Risks and test signals
Risks include global serial side effects, verifier log wording, BTF ID lookup failures, and target object mismatch. Passing signals are correct link attach metadata, internal result map entries set to one, expected load failures for invalid replacements, successful cgroup-BPF fentry info fields, and successful cpumap update through freplace target resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_bpf2bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_sleep.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_sleep.c

## Purpose
Tests sleepable fexit behavior across a cloned child stack/thread context.

## Important APIs, types, and functions
Uses `fexit_sleep.lskel.h`, `clone()`-style helper `do_sleep()`, `mmap()` stack allocation, `sched.h`, and time/syscall headers. The child triggers sleep/syscall behavior while fexit programs observe it.

## Control flow and state
The test loads/attaches the lightweight skeleton, allocates a stack, starts a child with `do_sleep()`, waits for completion, and checks skeleton BSS counters/results. State is stack mapping, child task, and skeleton BSS.

## Dependencies and integration points
Depends on sleepable fexit trampoline support, clone/fork permissions, and generated lskel. Integrated as `test_fexit_sleep()`.

## Risks and test signals
Risks include scheduling/timing and stack cleanup. Passing signal is successful child completion and expected fexit observations in BSS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_stress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_stress.c

## Purpose
Provides stress coverage for fexit attach/detach or execution behavior using helpers from `bpf_util.h`.

## Important APIs, types, and functions
Includes `test_progs.h` and `bpf_util.h`; the file is minimal and delegates details to harness or generated code paths compiled with this test.

## Control flow and state
Control flow is expected to run repeated fexit operations or generated stress logic. This source introduces no persistent custom data structures beyond any local counters in omitted/generated portions.

## Dependencies and integration points
Depends on fexit support and selftest utility helpers. Integrated as an fexit stress selftest.

## Risks and test signals
Risks are timing and resource exhaustion under repeated attach/detach. Passing signal is completing the stress sequence without verifier, attach, or runtime errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_stress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_test.c

## Purpose
Tests fexit attach behavior for normal and many-argument target functions.

## Important APIs, types, and functions
Uses `fexit_test.lskel.h`, `fexit_many_args.skel.h`, shared `fexit_test_common()`, generated attach helpers, and BSS result/counter checks.

## Control flow and state
`fexit_test()` runs the lightweight skeleton path; `fexit_many_args()` runs the many-argument path. Both load/attach, trigger target execution, validate BSS state, and destroy skeletons.

## Dependencies and integration points
Depends on fexit trampoline support and generated target tracing programs. Integrated via `test_fexit_test()` subtests.

## Risks and test signals
Risk is trampoline ABI or target prototype drift. Passing signals are expected counts and argument capture values in BSS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fib_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fib_lookup.c

## Purpose
Tests `bpf_fib_lookup()` over IPv4/IPv6 routes, neighbor states, direct/table lookups, source address updates, policy marks, and multipath/gateway MAC resolution in an isolated namespace.

## Important APIs, types, and functions
Uses `fib_lookup.skel.h`, network helpers, `ip` commands in `setup_netns()`, table-driven `struct fib_lookup_test`, `set_lookup_params()` to populate `struct bpf_fib_lookup`, address assertion helpers, and `bpf_prog_test_run_opts()` with `struct __sk_buff` context. Constants define test addresses, marks, route table, and expected MACs.

## Control flow and state
The test creates netns `fib_lookup_ns`, configures veth/routes/neighbors/rules, sets skb ifindex to `veth1`, then iterates test cases. For each case it sets BSS `fib_params` and `lookup_flags`, runs the BPF program, checks return code, optional rewritten src/dst IPs, destination MAC, and direct-lookup `tbid` clearing. Cleanup closes netns and deletes it.

## Dependencies and integration points
Requires `ip` tooling, namespace privileges, veth/route/neigh/rule support, BPF FIB helper, generated skeleton, and packet fixture. Integrated as a network helper selftest.

## Risks and test signals
Networking setup is complex and environment-sensitive. Passing signals are exact helper return codes, expected address rewrites, expected destination MAC bytes, and zeroed `tbid` after direct lookup cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fib_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/file_reader.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/file_reader.c

## Purpose
Tests BPF file-reading behavior on executable file contents, including successful reads and expected page-fault handling, plus generated negative verifier/load cases.

## Important APIs, types, and functions
Uses `file_reader.skel.h`, `file_reader_fail.skel.h`, `dladdr()` to get executable base, `/proc/self/exe`, `madvise(MADV_PAGEOUT)`, skeleton autoload selection by program name, and BSS buffers. `initialize_file_contents()` reads 256 KiB from the executable and pages out a 512 KiB range around the executable mapping.

## Control flow and state
`run_test()` initializes file contents, opens the skeleton, autoloads only the requested program, copies expected bytes into BSS `user_buf`, sets current PID, loads/attaches, opens `/proc/self/exe` to trigger, and asserts BSS `err == 0` and `run_success == 1`. Top-level runs two positive subtests and `RUN_TESTS(file_reader_fail)`. State includes global `file_contents`, user pointer string, paged-out executable mapping range, and skeleton BSS.

## Dependencies and integration points
Depends on executable mapping introspection through libdl, procfs, page-out support, generated file reader programs, and BPF file read helper/kfunc support. Integrated as `test_file_reader()`.

## Risks and test signals
Risks include executables smaller than 256 KiB, `MADV_PAGEOUT` behavior, and address alignment assumptions. Passing signals are full executable read, successful page-out calls, trigger open, zero BSS error, success flag set, and generated negative tests failing as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/file_reader.c -->
