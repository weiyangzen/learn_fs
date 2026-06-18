# subset-b-006804 research

Grouped research for Linux BPF selftest harness files under `sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests`. Each section is delimited for deterministic split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_listen.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_listen.c

Purpose: serial regression suite for listening sockets stored in SOCKMAP and SOCKHASH, covering map update/lookup/delete, redirect helpers, BPF link attachment, and reuseport selection. Important APIs are `test_sockmap_listen__open_and_load`, `bpf_map_update_elem`, `bpf_map_lookup_elem`, `bpf_map_delete_elem`, `bpf_prog_attach`, `bpf_link_create`, `bpf_program__attach_sockmap`, and socket helpers from `sockmap_helpers.h`.

Control flow builds matrices across map type, IPv4/IPv6, TCP/UDP, and named subtests. `test_ops` covers invalid/open/bound/listening insertions, deletion after close, lookup cookie behavior, child cloning, orphan children, and races against listen/accept. `test_redir` attaches SK_SKB parser/verdict or SK_MSG verdict programs and checks connected/listening redirection. `test_reuseport` verifies selecting listening sockets, rejecting connected targets, and mixed reuseport groups. Persistent state lives in kernel maps, BPF links, verdict counters, sockets, and skeleton BSS flag `test_sockmap`; cleanup deletes map entries and closes descriptors. Risks are race sensitivity, kernel error-code differences between map types, nonblocking socket timing, and link detach leaks. Test signals are `FAIL`, `ASSERT_*`, pass/drop counter checks, socket cookie comparisons, expected `EINVAL/ENOENT/EOPNOTSUPP/ECONNREFUSED`, and matrix subtest names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_listen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_redir.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_redir.c

Purpose: exhaustive sockmap/sockhash redirection matrix across SK_MSG/SK_SKB, ingress/egress directions, socket families, and socket types. Key types are `enum prog_type`, `struct maps`, `struct redir_spec`, and `struct socket_spec`; key APIs include `test_sockmap_redir__open_and_load`, `create_socket_pairs`, `bpf_prog_attach`, map updates, `send`, and `recv_timeout`.

Control flow starts at `serial_test_sockmap_redir`, runs `test_map` for SOCKMAP and SOCKHASH, then iterates four redirect modes and intra/cross-protocol socket pairs. `get_redir_params` selects the BPF program, attach type, and redirect flags. `test_send_redir_recv` populates input/output maps, sends data, validates supported combinations by receiving redirected payload, and validates unsupported combinations by pass/drop counters and empty queues. State is kernel socket queues, map entries, verdict counters, and skeleton BSS redirect flags. Dependencies are `sockmap_helpers.h`, libbpf skeletons, AF_INET/AF_INET6/AF_UNIX/AF_VSOCK support, and test timeout helpers. Risks include unsupported combinations intentionally dropping packets, AF_VSOCK verdict timing races handled by `UNSUPPORTED_RACY_VERD`, OOB handling, and cleanup after partial setup. Test signals are subtest names containing map/hash, redirect mode, socket kind, supported arrow, OOB suffix, pass/drop counts, payload byte checks, and expected `EACCES` on blocked sends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_redir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_strp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_strp.c

Purpose: validates SOCKMAP stream parser behavior for TCP, including preexisting receive data, packet framing, partial reads, multiple framed packets in one skb, verdict redirection, and FIONREAD visibility. Key helpers are `sockmap_strp_init`, `sockmap_strp_consume_pre_data`, `create_pair`, `create_socket_pairs`, `bpf_prog_attach`, `bpf_map_update_elem`, `recv_timeout`, and `ioctl(FIONREAD)`.

Control flow loads `test_sockmap_strp` skeleton, attaches parser and verdict programs to `sock_map`, then each subtest creates loopback pairs and sends framed `head+body` packets. Dispatch mode changes skeleton data `verdict_max_size` to route by packet size. Multiple-packet mode allocates a large buffer of repeated frames. Partial-read mode proves no data is delivered until complete header/body arrives. Verdict mode simulates proxy forwarding from one socket pair to another. State includes socket map membership, skeleton data fields, stream parser queues, preloaded receive queue data, and heap buffers. Dependencies are TCP sockets, `test_skmsg_load_helpers.skel.h`, sockmap helper wrappers, and kernel strparser behavior. Risks include timing around delayed data-ready work, packet truncation, and incomplete cleanup of descriptors on assertions. Test signals are exact byte counts, memcmp payload checks, `FIONREAD` availability, expected EAGAIN retry for pre-data, and named subtests for IPv4/IPv6 pass/verdict/partial/multiple/dispatch cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_strp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt.c

Purpose: table-driven verifier and runtime test for `BPF_PROG_TYPE_CGROUP_SOCKOPT` on cgroup get/setsockopt hooks, including syscall and io_uring paths. Important data is `struct sockopt_test`, which embeds raw `struct bpf_insn` programs, attach metadata, socket option inputs/expected outputs, expected errors, and io_uring support flags.

Control flow joins `/sockopt`, then for each test loads raw BPF with `bpf_prog_load`, attaches either by `bpf_prog_attach` or `bpf_link_create`, creates an AF_INET TCP socket, optionally calls setsockopt, then optionally calls getsockopt. `uring_sockopt` uses mini liburing SQE/CQE command helpers for socket operations when supported. State is mostly per-test stack state plus kernel cgroup attachments, socket option values, verifier log buffer, and dynamically allocated optval memory. Dependencies include cgroup helpers, `io_uring/mini_liburing.h`, raw BPF instruction macros, socket constants, and page-size normalization. Risks include mutating `set_optlen/get_optlen` fields in the global test table for page-size conversion, expectations tied to verifier error policy, and mixed errno/result handling between syscalls and io_uring. Test signals include DENY_LOAD/DENY_ATTACH cases, expected `EPERM/EFAULT/EOPNOTSUPP`, optlen shrink/expand checks, optval byte rewrites, attach-type mismatch failures, and three execution lanes: attach, link, and selected io_uring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt_inherit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt_inherit.c

Purpose: checks cgroup sockopt inheritance semantics for custom options across listening and accepted sockets. It uses `sockopt_inherit` skeleton programs `_getsockopt` and `_setsockopt` attached to one cgroup, plus network helper callbacks to seed custom option values.

Control flow joins `/sockopt_inherit`, loads skeleton, sets BSS page size, attaches get/set sockopt programs through libbpf links, starts a loopback server with `post_socket_cb`, then runs `server_thread` to listen, verify listener options, accept a client, and verify inherited versus listener-only options. A condition variable synchronizes the client connection after the server has entered listen. State includes BPF-managed custom option storage, listener and accepted sockets, pthread synchronization primitives, and link lifetime. Dependencies are `cgroup_helpers.h`, `network_helpers.h`, pthreads, and custom SOL level `0xdeadbeef`. Risks are server thread early return without closing accepted descriptors, synchronization correctness, and false failures if callback socket creation does not seed all three options. Test signals are `verify_sockopt` expected bytes: listener has all custom options, accepted socket inherits two but not `CUSTOM_LISTENER`, client side sees zero, and pthread return value aggregates server failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt_inherit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt_multi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt_multi.c

Purpose: validates ordering and composition of multiple cgroup sockopt programs attached at parent and child cgroups. It tests both getsockopt rewriting and setsockopt rewriting for `IP_TOS`.

Control flow joins `/parent` and `/parent/child`, loads `sockopt_multi`, sets page size in BSS, creates one TCP socket, then runs get and set scenarios. In getsockopt, baseline kernel value `0x80` is checked, child program rewrites to `0x90`, parent program then rewrites to `0xA0`, unexpected initial value `0x40` is denied, and detaching child leaves parent denial/rewrite behavior. In setsockopt, child adds `0x10` and parent adds another `0x10`. State includes parent/child cgroup links, one socket option value, skeleton BSS page size, and link lifetimes. Dependencies are cgroup v2 helper setup, libbpf skeleton APIs, and IP socket options. Risks are cgroup hierarchy setup assumptions, program ordering expectations, and cleanup after mid-test failures. Test signals are precise byte values `0x80`, `0x90`, `0xA0`, `0x80 + 2*0x10`, expected `getsockopt` failure for unexpected input, and `ASSERT_OK` on link attach and final runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt_multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt_qos_to_cc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt_qos_to_cc.c

Purpose: targeted cgroup sockopt test that maps IPv6 traffic class/QoS changes to TCP congestion-control changes. It loads `sockopt_qos_to_cc` and verifies a `setsockopt(IPV6_TCLASS)` triggers the BPF program to set `TCP_CONGESTION` to `reno`.

Control flow joins `/sockopt_qos_to_cc`, opens and loads the skeleton, records page size in BSS, creates an IPv6 TCP socket, sets initial congestion control to `cubic`, attaches the cgroup program, then calls `run_setsockopt_test`. That helper writes traffic class `0x2D` and reads `TCP_CONGESTION` back. State is only the cgroup link, socket congestion-control setting, and page-size BSS value. Dependencies include cgroup helpers from `test_progs.h`, TCP congestion algorithms available in the kernel, IPv6 sockets, and `netinet/tcp.h`. Risks include environment dependency on `cubic` and `reno` availability, permissions for changing congestion control, and failing before link attachment if IPv6 is unavailable. Test signals are successful IPv6 socket creation, successful initial `TCP_CONGESTION=cubic`, successful program attachment, and final string equality `reno`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt_qos_to_cc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt_sk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt_sk.c

Purpose: exercises cgroup sockopt programs that inspect or modify socket context, including oversized optvals, custom options, send buffer rewriting, congestion-control string extension, TCP zerocopy receive, netlink NULL optval, and raw TCP sockets.

Control flow joins `/sockopt_sk`, loads `sockopt_sk`, sets BSS page size, attaches `_setsockopt` and `_getsockopt`, then runs `getsetsockopt`. That helper creates different socket types and runs a fixed sequence: IP_TOS bypass with two-page buffer, IP_TTL denial, custom SOL handling, IP_FREEBIND page-boundary behavior, SO_SNDBUF rewrite, TCP_CONGESTION string rewrite from `nv` to `cubic`, TCP_ZEROCOPY_RECEIVE cases, NETLINK membership NULL-buffer get, and raw TCP saved-SYN interception. State includes BPF cgroup links, page-sized heap buffer, socket option kernel state, and skeleton BSS. Dependencies include netlink headers, TCP options, page-size behavior, and cgroup helpers. Risks include algorithm availability, kernel option semantics, page-size assumptions, and complex cleanup across socket type switches. Test signals are expected `EPERM` for IP_TTL, exact optlen and byte values, SO_SNDBUF equals `0x55AA*2`, congestion string `cubic`, `EINVAL` for unaligned zerocopy address, netlink optlen `8`, and expected error for raw TCP `TCP_SAVED_SYN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockopt_sk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/spin_lock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/spin_lock.c

Purpose: validates successful BPF spin-lock use under concurrent execution and negative verifier diagnostics for invalid lock identities and forbidden calls while holding locks. It uses `test_spin_lock` and `test_spin_lock_fail` skeletons.

Control flow first runs `test_spin_lock_success`, which loads the success program and starts four pthreads repeatedly invoking `bpf_prog_test_run_opts` on `bpf_spin_lock_test`. Then `test_spin_lock` iterates `spin_lock_fail_tests`, autoloads one failure program at a time, expects skeleton load failure, and matches verifier logs with fixed substrings or regex. State includes a 1 MiB verifier log buffer, thread IDs, test-run packet input `pkt_v4`, and per-program autoload flags. Dependencies are regex library, libbpf log capture through open opts, network helper packet data, pthreads, and kernel verifier messages. Risks include verifier log text drift, regex fragility, JIT/kfunc support causing skip, and concurrent test-run nondeterminism. Test signals are successful threaded program runs with nonzero retval, expected load failure for each negative program, explicit skip when JIT lacks kfunc calls, and matching messages such as `bpf_spin_unlock of different lock` or global function call restrictions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/spin_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stack_var_off.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stack_var_off.c

Purpose: small test for BPF stack reads/writes through offsets not known statically. It loads `test_stack_var_off`, initializes BSS input values, attaches the probe, triggers it with a short sleep, and checks the computed result.

Control flow is linear: open/load skeleton, set `test_pid` to the current process to filter events, initialize `input[0]=2` and `input[1]=42`, attach, wait, then assert `probe_res == 42`. State is skeleton BSS only; no persistent maps are manipulated by the harness. Dependencies are generated skeleton code, `test_progs.h`, and the BPF side probe firing during `usleep`. Risks are event timing sensitivity and accidental triggering by unrelated processes if PID filtering breaks. Test signals are skeleton load/attach success and final BSS result equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stack_var_off.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_build_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_build_id.c

Purpose: validates stack trace collection with build IDs from tracepoint context and consistency between stack-id maps and stack maps. It uses `test_stacktrace_build_id` skeleton and helper functions `compare_map_keys`, `compare_stack_ips`, and `read_build_id`.

Control flow loads and attaches the skeleton, triggers stack collection with `dd` and `./urandom_read`, disables collection through `control_map[0]=1`, verifies matching keys in `stackid_hmap` and `stackmap`, reads the build ID of `urandom_read`, scans `stackmap` entries for a valid matching build ID, retries once on known race, then compares build-ID stack contents with address stack map. State lives in BPF maps `control_map`, `stackid_hmap`, `stackmap`, and `stack_amap`; harness state is retry counter and local build-ID buffer. Dependencies include external helper binary `urandom_read`, shell commands, build-id availability, and perf stack depth constants. Risks are documented race where build ID translation can return raw IP status, external command failures, and map iteration ordering. Test signals are map key symmetry, found build ID match, optional retry warning, and `compare_stack_ips` success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_build_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_build_id_nmi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_build_id_nmi.c

Purpose: NMI/perf-event variant of build-ID stack trace validation. It reuses `test_stacktrace_build_id` but changes program type to `BPF_PROG_TYPE_PERF_EVENT` and attaches to a hardware CPU cycles perf event.

Control flow opens the skeleton, overrides `oncpu` program type, loads it, opens a CPU 0 perf event with `read_perf_max_sample_freq`, attaches the program, runs `dd` and pinned `taskset 0x1 ./urandom_read 100000`, disables collection, compares stack map keys, reads the `urandom_read` build ID, scans build-ID stack entries, and retries once on translation race. State is perf-event fd/link, same BPF maps as the non-NMI variant, and local retry/build-ID state. Dependencies include hardware perf event support, CPU 0 availability, `taskset`, `urandom_read`, and kernel build-ID translation in NMI context. Risks include skip paths for unsupported PMU, races in build-ID status, and intentional omission of `compare_stack_ips` because NMI translation can fall back to IP. Test signals are skip on `ENOENT/EOPNOTSUPP`, map key symmetry, found build ID, and absence of final IP comparison by design.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_build_id_nmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_ips.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_ips.c

Purpose: x86_64-only validation that stack trace IPs collected from kprobe, kprobe_multi, raw tracepoint, fentry, and fexit contexts resolve to expected kernel symbols. Important helper `check_stacktrace_ips` loads kallsyms, looks up stack map IPs, and compares symbol base addresses.

Control flow each subtest loads `stacktrace_ips`, skips if `CONFIG_UNWINDER_ORC` is absent, attaches one probe flavor to bpf_testmod hooks, triggers `trigger_module_test_read`, loads kallsyms, and compares stack entries. Raw tracepoint additionally queries the JITed BPF program address with `bpf_prog_get_info_by_fd` and expects it plus `bpf_trace_run2`. State includes stack map contents, skeleton BSS `stack_key`, kernel symbol tables, and probe links. Dependencies are x86_64, ORC unwinder, bpf_testmod symbols, kallsyms access, and generated skeleton kconfig. Risks include architecture-specific stacks, symbol drift, missing test module, and retprobe versus entry stack ordering differences. Test signals are subtests for `kprobe_multi`, `kretprobe_multi`, `raw_tp`, `kprobe`, `kretprobe`, `fentry`, and `fexit`, with exact symbol-sequence comparisons or skip on unsupported architecture/config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_ips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_map.c

Purpose: tests basic stack map collection and map consistency using `stacktrace_map` skeleton. It verifies that stack ID hash map keys match stack map keys, address stack maps match, and lookup-and-delete removes a collected stack.

Control flow opens/loads skeleton, gets map fds, attaches, sleeps to allow events, disables collection via `control_map`, compares keys both directions, compares stack IP arrays, then uses BSS `stack_id` to `bpf_map_lookup_and_delete_elem` and confirms a subsequent lookup returns `-ENOENT`. State is held in BPF maps `control_map`, `stackid_hmap`, `stackmap`, `stack_amap`, and BSS `stack_id`. Dependencies are stack trace helpers from `test_progs.h` and periodic event generation by the attached BPF program. Risks include timing, empty stack maps, and errno handling around lookup/delete. Test signals are successful map comparisons, address stack comparison, lookup-delete success, and deleted-key absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_map_raw_tp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_map_raw_tp.c

Purpose: raw tracepoint version of stack map key consistency testing. It loads `stacktrace_map.bpf.o` as `BPF_PROG_TYPE_RAW_TRACEPOINT`, attaches program `oncpu` to `sched_switch`, and validates map relationships after a short run.

Control flow uses `bpf_prog_test_load`, finds the program by name, attaches raw tracepoint link, locates maps with `bpf_find_map`, sleeps, writes `control_map[0]=1`, then compares keys between `stackid_hmap` and `stackmap` in both directions. State includes the raw tracepoint link, generic `bpf_object`, three map fds, and control flag. Dependencies are `sched_switch` raw tracepoint availability and helper comparison functions. Risks are failure to find maps by name, no events during sleep, and cleanup if attach or map discovery fails. Test signals are raw tracepoint attach success and bidirectional map key comparison success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_map_raw_tp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_map_skip.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_map_skip.c

Purpose: validates stack trace collection with skipped frames, expecting a reduced depth of two IPs and no internal failure flag. It uses `stacktrace_map_skip` skeleton.

Control flow loads skeleton, obtains stack maps, sets BSS `pid` to current process, attaches, sleeps for events, sets BSS `control=1` to stop collection, compares stack ID keys with stack map keys both directions, compares only `TEST_STACK_DEPTH` IPs against `stack_amap`, then checks BSS `failed == 0`. State is skeleton BSS and three map fds. Dependencies are stack comparison helpers, process-specific filtering, and generated BPF code implementing skip logic. Risks are event timing and false positives if stack depth or skip semantics change. Test signals are map fd assertions, attach success, two-way key comparison, IP comparison for depth two, and zero failure flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stacktrace_map_skip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/static_linked.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/static_linked.c

Purpose: verifies statically linked BPF subprogram/object behavior using `test_static_linked` skeleton and read-only data initialization before load.

Control flow opens skeleton, writes `rodata->rovar1=1` and `rodata->rovar2=4`, loads, attaches, triggers with `usleep`, then checks computed mutable data values. State is skeleton rodata inputs and data outputs `var1` and `var2`. Dependencies are skeleton generation for the statically linked BPF object and the attached program firing during sleep. Risks are minimal, mainly timing and mismatches in linked helper calculations. Test signals are expected equations `var1 = 1 * 2 + 2 + 3` and `var2 = 4 * 3 + 5 + 6`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/static_linked.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stream.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stream.c

Purpose: tests BPF program stream output APIs and verifier success/failure skeleton suites. It includes `RUN_TESTS(stream_fail)`, `RUN_TESTS(stream)`, direct `bpf_prog_stream_read` syscall checks, and arena fault-address reporting.

Control flow `test_stream_syscall` loads `stream`, runs `stream_syscall`, checks invalid program fd, invalid stream id, NULL buffer, reads stdout in two chunks, and confirms stdout/stderr drain. `test_stream_arena_fault_address` is architecture-gated to x86_64/aarch64, runs read and write fault programs, reads stderr stream, and checks reported fault address string from BSS. State includes stream buffers inside kernel, skeleton BSS fault address, and local read buffers. Dependencies are `bpf_prog_stream_read`, `bpf_test_run_opts`, stream skeletons, and supported arena fault reporting architecture. Risks are syscall ABI changes, buffer sizing, and architecture skip coverage. Test signals are expected `-EINVAL`, `-ENOENT`, `-EFAULT`, exact byte counts `2`, `1`, `0`, and stderr containing hex fault address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/string_kfuncs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/string_kfuncs.c

Purpose: validates BPF string kfunc success, verifier/runtime failure, and too-long string handling for strcmp-like and search/length functions. It uses `string_kfuncs_success`, `string_kfuncs_failure1`, and `string_kfuncs_failure2` skeletons.

Control flow first runs generated success and failure suites through `RUN_TESTS`. `run_too_long_tests` loads the second failure skeleton, fills BSS `long_str` with `a`, then for each test case constructs `test_<name>_too_long`, finds that program, runs it with `bpf_prog_test_run_opts`, and expects return `-E2BIG`. State is skeleton BSS long string and per-program test-run opts. Dependencies are generated BPF programs for each string kfunc case and test harness program lookup by name. Risks are name drift between `test_cases` and BPF program sections, error-code changes, and long-string size assumptions. Test signals are all RUN_TESTS results plus each too-long subtest returning exactly `-E2BIG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/string_kfuncs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/struct_ops_autocreate.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/struct_ops_autocreate.c

Purpose: tests libbpf struct_ops map autocreate behavior, optional maps, autoload side effects, and shadow variable program replacement. It uses `struct_ops_autocreate` and `struct_ops_autocreate2` skeletons.

Control flow has four subtests. `cant_load_full_object` expects load failure when a mismatched struct_ops map remains autocreated and verifies captured libbpf log plus `-ENOTSUP`. `can_load_partial_object` disables `testmod_2`, loads, confirms `test_1` remains autoloaded while `test_2` is disabled, attaches struct_ops, and checks BSS result `42`. `optional_maps` validates optional autocreate defaults, flips autocreate flags, loads, and attaches optional map. `autoload_and_shadow_vars` rewrites `testmod_1->test_1` from `bar` to `foo` before load and checks autoload/result. State includes skeleton map autocreate flags, program autoload flags, struct_ops links, captured log memory, and BSS result. Dependencies are bpf_testmod struct_ops support, libbpf shadow vars, and `bpf_map__attach_struct_ops`. Risks include libbpf log text drift and kernel BTF mismatch expectations. Test signals are expected load failure/success, log substring, autoload flag assertions, and `test_1_result == 42`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/struct_ops_autocreate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/struct_ops_private_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/struct_ops_private_stack.c

Purpose: architecture-gated struct_ops tests for BPF private stack use, invalid private stack programs, and recursive private stack behavior. It uses three skeletons: success, failure, and recursion.

Control flow on x86_64/aarch64/powerpc64 runs `private_stack`, `private_stack_fail`, and `private_stack_recur`; otherwise it skips. Success loads and attaches struct_ops map `testmod_1`, triggers bpf_testmod read, and checks BSS `val_i=3` and `val_j=8`. Failure opens and expects skeleton load failure. Recursion loads/attaches another struct_ops program, triggers read, and expects `val_j=3`. State is struct_ops links and skeleton BSS outputs. Dependencies are architecture support for private stack, bpf_testmod read trigger, and generated skeletons. Risks are architecture coverage gaps and failing cleanup of struct_ops links on attach/trigger failure. Test signals are architecture skip, expected load error for fail skeleton, trigger success, and exact BSS value assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/struct_ops_private_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/subprogs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/subprogs.c

Purpose: validates BPF subprogram execution results and robustness of skeleton load while `bpf_jit_harden` toggles. It uses `test_subprogs` and `test_subprogs_unused` skeletons.

Control flow `subprogs_alone` loads and attaches the main skeleton, waits, checks BSS results `12`, `17`, `19`, and `36`, then loads an unused-program skeleton to ensure unused subprograms do not break loading. `subprogs_and_jit_harden` opens `/proc/sys/net/core/bpf_jit_harden`, starts a thread repeatedly writing `2` and `0`, then repeatedly opens/loads the skeleton. State includes sysctl fd, toggler stop flag, pthread, and skeleton BSS results. Dependencies are writable JIT harden sysctl, generated skeletons, pthreads, and trace/probe activity during sleep. Risks include permission/environment failures for sysctl, race sensitivity, and restoring sysctl value only by toggling loop stop rather than saving original. Test signals are BSS result equality and ten successful loads under JIT hardening churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/subprogs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/subprogs_extable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/subprogs_extable.c

Purpose: verifies exception table handling for BPF subprograms through the `test_subprogs_extable` skeleton.

Control flow opens/loads and attaches the skeleton, triggers bpf_testmod read with size `456`, asserts BSS `triggered` is nonzero, detaches, and destroys. State is limited to skeleton link state and BSS `triggered`. Dependencies are bpf_testmod read trigger and generated BPF code using subprogram exception table behavior. Risks are missing test module or trigger path not firing. Test signals are skeleton open/load/attach success, trigger success, and `triggered != 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/subprogs_extable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/subskeleton.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/subskeleton.c

Purpose: tests libbpf subskeleton access for a library-like part of a BPF object, both through generated full skeleton and through generic `bpf_object` APIs. It uses `test_subskeleton` and `test_subskeleton_lib.subskel`.

Control flow `subskeleton_lib_setup` opens a subskeleton over an existing object and initializes rodata/data/BSS values. `subskeleton_lib_subresult` reopens the subskeleton after load, checks computed library output, program/map names, weak and extern variables, and kconfig access. `subtest_skel_subskeleton` drives the full skeleton path; `subtest_obj_subskeleton` uses `test_subskeleton__elf_bytes`, `bpf_object__open_mem`, initial map values, manual program attach, and BSS map access. State is shared BPF object maps, subskeleton views, rodata/data/BSS fields, and link lifetime. Dependencies are libbpf subskeleton generated headers, ELF embedded bytes, and tracepoint/probe firing via `usleep`. Risks include object API and skeleton API diverging, initial-value pointer misuse, and map/program name changes. Test signals are library result `1+2+3+4+5+6`, final output multiplied by `rovar1=10`, correct map/program names, `CONFIG_BPF_SYSCALL` true, and both subtests passing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/subskeleton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/summarization.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/summarization.c

Purpose: validates verifier summarization rules for freplace programs, especially whether extension programs may change packet data or sleep relative to replaced subprogram summaries. It uses `summarization` and `summarization_freplace` skeletons.

Control flow `test_summarization_freplace` builds a matrix over main programs and replacement functions. `test_aux` opens the main object with verifier log capture, autoloads one main program, loads it, opens freplace object, autoloads one replacement, sets autoattach and attach target to the selected subprogram/main program, loads freplace, and checks whether load should succeed. State includes verifier log buffer, selected autoload flags, attach target metadata, and skeleton lifetimes. Dependencies are libbpf attach-target APIs, verifier summaries, packet-data side-effect analysis, and sleepable helper policies. Risks include expected log substrings drifting, the special `might_sleep` skip path changing if support is added, and matrix size hidden by `ARRAY_SIZE` over two-dimensional arrays. Test signals are subtest names `<target>_with_<replacement>`, load success when side effects are compatible, load failure with `Extension program changes packet data` or `Extension program may sleep`, and optional skip for unsupported sleepable helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/summarization.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/syscall.c

Purpose: tests `BPF_PROG_TYPE_SYSCALL` style helpers embedded in `syscall` skeleton, including dynamically loading a program/map from BPF and updating an outer map.

Control flow `load_prog` subtest fills `struct args` with verifier log buffer, max entries, and zero fds, runs skeleton program `load_prog` with context through `bpf_prog_test_run_opts`, then checks returned fds, verifier log prefix, and map lookup key `12` value `34`. It closes all fds captured in context. `update_outer_map` simply runs the skeleton program and expects retval `1`. State includes context struct passed to BPF test run, dynamically created map/prog/BTF fds, verifier log buffer, and map contents. Dependencies are generated syscall BPF object, BPF test-run context support, and kernel ability to create BPF objects from a syscall program. Risks are fd cleanup leaks on partial failures and verifier log expectation fragility. Test signals are `retval == 1`, positive fd fields, verifier log processed marker, map value `34`, and successful outer-map update run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tailcalls.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tailcalls.c

Purpose: broad tail-call regression harness for prog-array patching, tail-call limit accounting, bpf2bpf call interactions, fentry/fexit tracing, pinned prog-array update races, freplace constraints, hierarchy loops, failure cases, and sleepable programs.

Control flow is a long subtest dispatcher. Early tests load raw `.bpf.o` files, populate `jmp_table`, delete/update entries, and validate retval changes. `test_tailcall_count` and hierarchy helpers verify tail-call counter values, optionally attaching fentry/fexit probes to subprograms. Bpf2bpf tests check subprogram stack use, indirect key selection, unaligned stack data, and nested tailcall loops. `test_tailcall_poke` pins `/sys/fs/bpf/jmp_table`, updates it from a thread while loading another skeleton sharing the map. Freplace tests assert update/attach failures for extended programs. Sleepable tests reject mixed normal/sleepable tailcall maps and allow sleepable-to-sleepable uprobe flow. State includes many BPF objects, prog-array maps, internal BSS maps, pinned map path, trace links, pthread stop flag, and test-run packets. Dependencies are numerous generated objects/skeletons, bpffs, libbpf attach APIs, uprobe support, and network helper `pkt_v4`. Risks include pinned-map cleanup, concurrent update races, exact counter expectations (`33`, `34`, `68`, `70`, `31`), architecture/JIT differences, and many early-exit cleanup paths. Test signals are named subtests, retval assertions, BSS counter lookups, expected freplace/update errors, load failure from `tailcall_fail`, and sleepable executed flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tailcalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_fd_query_rawtp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_fd_query_rawtp.c

Purpose: validates `bpf_task_fd_query` metadata for a raw tracepoint attachment. It loads `test_get_stack_rawtp.bpf.o`, opens raw tracepoint `sys_enter`, and queries the resulting fd.

Control flow loads the raw tracepoint program, calls `bpf_raw_tracepoint_open`, then queries current process and fd with normal buffer, zero-length buffer, NULL buffer, and too-small buffer. State is the raw tracepoint fd, program object, output buffer, and returned metadata fields. Dependencies are raw tracepoint support and `bpf_task_fd_query`. Risks include missing close for raw tracepoint fd in this harness and exact truncation semantics. Test signals are `fd_type == BPF_FD_TYPE_RAW_TRACEPOINT`, name `sys_enter`, zero/NULL buffer returning required length, and small buffer returning `ENOSPC` with truncated `"sy"`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_fd_query_rawtp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_fd_query_tp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_fd_query_tp.c

Purpose: validates `bpf_task_fd_query` for perf-event tracepoint attachments. It tests `sched/sched_switch` and `syscalls/sys_enter_read`.

Control flow loads `test_tracepoint.bpf.o`, resolves tracepoint id from tracing/debugfs, opens perf event, enables it, attaches BPF with `PERF_EVENT_IOC_SET_BPF`, then queries current process and perf fd. State includes tracepoint id buffer, perf event fd, BPF object, and query output fields. Dependencies are tracing filesystem path, perf event tracepoint support, syscall constants, and `bpf_task_fd_query`. Risks include apparent check using `err` rather than `pmu_fd` after `perf_event_open`, path differences across kernels, and cleanup if open/read fails. Test signals are returned `BPF_FD_TYPE_TRACEPOINT` and tracepoint names `sched_switch` and `sys_enter_read`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_fd_query_tp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_kfunc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_kfunc.c

Purpose: tests task-related BPF kfunc acquire/release, current/from-pid/from-vpid behavior, map exchange, trusted walked task references, CO-RE flavor relocation, and negative verifier cases. It uses success and failure skeletons.

Control flow `run_success_test` opens/loads success skeleton with current pid, finds a named program, attaches it, forks a child, waits, and checks BSS `err` before and after. `run_vpid_success_test` uses `clone(CLONE_NEWPID)` to run `run_vpid_test` as PID 1 in a new namespace, then runs selected program via `bpf_prog_test_run_opts` and encodes errors in exit status. The dispatcher iterates success test name arrays and then runs `RUN_TESTS(task_kfunc_failure)`. State includes skeleton BSS pid/err, attached links, child processes, clone stack, and namespace process status. Dependencies are task kfunc kernel support, PID namespaces, fork/clone permissions, and generated program names. Risks include namespace restrictions, child cleanup, status encoding ambiguity, and program-name drift. Test signals are each success subtest returning BSS err zero, vpid exit status zero, and all failure skeleton tests passing expected verifier failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_kfunc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_local_data.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_local_data.h

Purpose: header-only user-space helper ABI for task local data backed by a BPF task local storage map and user pointers. It offers static and dynamic TLD key creation, lazy per-thread data allocation, optional pthread destructor cleanup, and map updates keyed by pidfd.

Important types are `tld_key_t`, `struct tld_metadata`, `struct tld_meta_u`, `struct tld_data_u`, and `struct tld_map_value`. Control flow centers on `__tld_create_key`, which initializes page-aligned metadata, atomically reserves metadata slots, assigns offsets, and enforces page-size/dynamic-size bounds. `tld_get_data` lazily calls `__tld_init_data_p`, which opens a pidfd for current tid, allocates aligned per-thread data, constructs page-aligned map value pointers plus start offset, updates the BPF map, and stores thread-local data pointer. `tld_free` frees per-thread memory. State is weak atomic global metadata, optional pthread key, and `__thread` data pointer; kernel-visible state is map value containing user pointer and metadata pointer. Dependencies are C11 atomics, pidfd syscall, aligned allocation, libbpf `bpf_map_update_elem`, and matching BPF-side layout. Risks include option inconsistency across translation units, memory leaks without cleanup, offset overflow/error encoding in signed 16-bit key, and one-page ABI constraints. Test signals are indirect through task-local-data consumers: valid keys produce aligned per-thread storage, duplicate/oversized keys return negative errors, and BPF can fetch cached keys by name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_local_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_local_storage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_local_storage.c

Purpose: comprehensive task local storage and user-pointer test harness. It covers syscall enter/exit pairing, exit credential safety, recursion prevention, sleepable-program deadlock avoidance, task-local user pointer translation, page-boundary validation, update failure modes, map creation failures, and generated negative tests.

Control flow dispatches subtests. `sys_enter_exit` filters current tid and expects two gettid enter/exit events. `exit_creds` triggers process exit and loops on RCU/run counter to ensure NULL credential handling. `recursion` uses pidfd map keys and checks map values plus `recursion_misses`. `nodeadlock` pins all threads to one CPU, starts 32 socket-create loops, then checks no busy errors. UPTR tests update task-local maps with parent pidfd keys and user data pointers, fork child to prove parent address translation, change pointers, ensure lookup hides kernel pointer, validate page-boundary rejection, update flag errors, and BTF/map shape failures. State includes many skeleton BSS counters, task-storage maps, pidfds, eventfd, static aligned user data, mmap pages, threads, CPU affinity, and forked children. Dependencies are task local storage helpers, BTF, pidfd syscalls, preemptible kernel for nodeadlock, UPTR support, and generated failure skeletons. Risks include high concurrency timing, CPU affinity restoration, RCU wait loops, namespace/process side effects, and page-size assumptions. Test signals are exact counters, no recursion/deadlock errors, expected errno `EOPNOTSUPP/ENOENT/EEXIST/E2BIG/EINVAL`, user-data result formulas, hidden uptr lookup values, and `RUN_TESTS(uptr_failure)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_local_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_pt_regs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_pt_regs.c

Purpose: verifies task pt_regs retrieval for a uprobe context. It attaches `test_task_pt_regs` program to a local noinline trigger function in `/proc/self/exe`.

Control flow gets uprobe offset for `trigger_func`, opens/loads skeleton, attaches `handle_uprobe`, invokes `trigger_func`, checks BSS `uprobe_res == 1`, then compares BSS `current_regs` and `ctx_regs` byte-for-byte. State is uprobe link and BSS register snapshots. Dependencies are uprobe offset helper, self-executable attachment, generated skeleton, and architecture-compatible pt_regs layout. Risks include compiler/linker changing function visibility despite `noinline`, uprobe attach restrictions, and register struct layout sensitivity. Test signals are attach success, trigger result one, and memcmp equality of current and context registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_pt_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_under_cgroup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_under_cgroup.c

Purpose: checks task-under-cgroup detection from LSM and TP_BTF programs. It uses `test_task_under_cgroup` skeleton and cgroup `/foo`.

Control flow joins cgroup `/foo`, opens skeleton, seeds rodata `local_pid`, BSS `remote_pid`, and rodata cgroup id, loads, attaches LSM first, attaches TP_BTF second so LSM observes that attach path, forks a child to trigger task activity, detaches, and verifies `remote_pid` changed from local pid. State is cgroup fd/id, BSS remote pid, rodata local pid/cgid, LSM and trace links, and child process. Dependencies are cgroup helper setup, LSM BPF support, TP_BTF attach support, and fork/wait. Risks include a suspicious assertion pattern around `test__join_cgroup` that treats negative fd as OK, environment cgroup setup, and attach order sensitivity. Test signals are successful skeleton load/attachments, child fork/wait, and final `remote_pid != local_pid`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_under_cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_work_stress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_work_stress.c

Purpose: stress-tests BPF task work scheduling and optional deletion under concurrent `bpf_prog_test_run_opts` calls. It uses `task_work_stress` skeleton programs `schedule_task_work` and `delete_task_work`.

Control flow `task_work_run` opens skeleton, enables autoload for scheduler/deleter, loads, starts sixteen scheduler threads running the scheduler program until an atomic exit flag is set, optionally starts a deleter thread, sleeps for `BPF_TASK_WORK_TEST_TIME` seconds defaulting to one, stops threads, joins them, then validates BSS counters. `runner` loops test-run calls until error or exit. State includes thread arrays, atomic exit flags, started flags, skeleton BSS counters, selected program fds, and environment-controlled duration. Dependencies are pthreads, atomics, BPF test-run support, and task work kfunc/helper behavior in generated BPF. Risks include scheduling nondeterminism, duration too short or too long, high contention, and partial thread creation cleanup. Test signals are `callback_scheduled > 0`, `schedule_error > 0`, delete mode `delete_success > 0` and `callback_success < callback_scheduled`, non-delete mode exact equality of callback success and scheduled count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_work_stress.c -->
