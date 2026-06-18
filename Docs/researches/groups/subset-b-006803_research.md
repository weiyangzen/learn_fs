# subset-b-006803

Grouped research for Linux BPF selftests focused on socket lookup, cgroup socket-address hooks, socket storage, skb helpers, sockmap/sockhash behavior, kTLS interactions, and supporting socket helpers under `tools/testing/selftests/bpf/prog_tests`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_lookup.c

Purpose: `sk_lookup.c` is a userspace BPF selftest for the `BPF_SK_LOOKUP` netns attach point. It validates attaching, detaching, querying, socket redirection, lookup drops, reuseport interaction, `bpf_sk_assign()` corner cases, context access, and multi-program ordering for TCP and UDP over IPv4, IPv6, and IPv4-mapped IPv6. All behavioral tests run inside a dedicated network namespace configured with loopback IPv6 addresses.

Important APIs/types/functions: `struct test` describes lookup scenarios with a lookup program, optional reuseport program, sockmap, socket type, external client endpoint, internal listener endpoint, and expected accepting server. `struct inet_addr` and `enum server` encode endpoints and selected reuseport members. `make_server()` creates listener sockets through `start_server_str()` and optionally attaches a reuseport BPF program. `attach_lookup_prog()` attaches a `struct bpf_program` to the current netns with `bpf_program__attach_netns()`. `update_lookup_map()` stores socket FDs in BPF maps for BPF-side redirection. `tcp_echo_test()` and `udp_echo_test()` prove the redirected path by sending one byte and echoing it back; the UDP path uses `IP_RECVORIGDSTADDR`/`IPV6_RECVORIGDSTADDR` so replies come from the original destination.

Control flow: `test_sk_lookup()` calls `switch_netns()`, opens and loads `test_sk_lookup.skel.h`, then dispatches `run_tests()`. `run_tests()` executes query tests, redirect tests, lookup-drop tests, reuseport-drop tests, `bpf_sk_assign()` helper tests, and multi-program tests. Redirect cases attach a lookup program, create one or two backend sockets, update `redir_map`, optionally add a connected UDP reuseport member, connect a client to the external address, and assert that the echo comes from the intended server. Drop cases attach `lookup_drop`, `check_ifindex`, or reuseport-drop programs and expect `ECONNREFUSED`. `run_sk_assign()` uses `bpf_prog_test_run_opts()` with a synthetic `bpf_sk_lookup` context and checks that the selected cookie matches the expected socket. Multi-program cases attach two netns links and verify both programs ran while combined pass/drop/redirect verdicts produce expected connection behavior.

State and persistence: runtime state consists of temporary netns membership, listener/client socket FDs, BPF links, and map entries keyed by server index. `switch_netns()` uses `unshare(CLONE_NEWNET)` and `system("ip ...")` to add `fd00::1` and `fd00::2` to loopback. The skeleton owns BPF maps such as `redir_map` and `run_map`, BPF programs for redirection/drop/reuseport decisions, and BSS state used by the BPF side. There is no durable file output.

Dependencies: depends on libbpf skeleton generation for `test_sk_lookup.bpf.c`, kernel support for `BPF_SK_LOOKUP`, netns BPF links, `bpf_prog_query()`, `bpf_prog_test_run_opts()`, sockmap updates with socket FDs, socket cookies, reuseport eBPF attachment, IPv6 loopback configuration, and network helper APIs from the selftest harness. It also depends on the `ip` command and permission to create a network namespace.

Integration points: this file exercises the kernel socket lookup hook from the userspace selftest runner. It integrates BPF netns links, reuseport programs attached with `SO_ATTACH_REUSEPORT_EBPF`, BPF maps containing socket references, network helper socket factories, cgroup/test helper assertions, and BPF verifier/test-run infrastructure for synthetic `bpf_sk_lookup` contexts.

Risks: the test is sensitive to network namespace setup and loopback IPv6 configuration; failures in `system("ip ...")` abort later cases. UDP behavior depends on ancillary original-destination control messages and IPv4-mapped IPv6 normalization. Several tests assume specific errno values (`ECONNREFUSED`, `EEXIST`, connected-socket rejection) that can change if kernel lookup semantics change. The source snapshot contains duplicated lines, including duplicate local declaration text in `tcp_recv_send()` and a duplicate `.sock_map` initializer in one table entry; these are source-quality risks to watch during compilation or reconciliation. Map updates use `BPF_NOEXIST`, so stale entries would break subsequent subtests if cleanup paths fail before skeleton destruction.

Test signals: successful subtests include `query lookup prog`, the TCP/UDP IPv4/IPv6 redirect matrix, drop-on-lookup, drop-on-reuseport, `sk_assign` error/replace/null/context cases, connected socket rejection for TCP/UDP, and all nine multi-program combinations. Strong signals are successful one-byte echo through the selected backend, expected `ECONNREFUSED` for drop paths, matching selected socket cookies in test-run mode, and `run_map` showing both attached lookup programs executed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_storage_omem_uncharge.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_storage_omem_uncharge.c

Purpose: this selftest verifies that socket-local BPF storage memory accounting is uncharged when a socket is closed after storage updates. It specifically checks that updating a `BPF_MAP_TYPE_SK_STORAGE` entry and then closing the socket triggers the BPF-side close path to observe the expected cookie and zero outstanding `omem`.

Important APIs/types/functions: `test_sk_storage_omem_uncharge()` is the only test entry. It uses `sk_storage_omem_uncharge__open_and_load()`, `bpf_map__fd()`, `socket(AF_INET6, SOCK_STREAM, 0)`, `getsockopt(SO_COOKIE)`, `bpf_map_update_elem()`, and `sk_storage_omem_uncharge__attach()`. The skeleton BSS fields `cookie`, `cookie_found`, and `omem` are the test contract with the BPF program.

Control flow: the test opens and loads the skeleton, obtains the storage map FD, creates an unbound IPv6 stream socket, stores the socket cookie in skeleton BSS, inserts storage value `0`, updates it to `0xdeadbeef`, attaches the BPF program, closes the socket, and checks `cookie_found == 2` plus `omem == 0`.

State and persistence: state is limited to one socket FD, one sk_storage map entry keyed by that FD, and BSS counters in the skeleton. No namespace or durable file state is created. Cleanup destroys the skeleton and closes the socket if the close-trigger path was not reached.

Dependencies: requires kernel sk_storage support, socket cookies, libbpf skeleton support, BPF program attachment for the skeleton's close/tracing hook, and normal selftest assertion macros.

Integration points: this is a targeted regression test for interaction between socket lifetime, sk_storage map replacement, socket memory accounting, and BPF program observation during socket close. It is intentionally independent of address binding and network namespaces.

Risks: the test assumes the BPF program will observe exactly two cookie matches across the inserted and replaced storage state. If the BPF side changes accounting points, `cookie_found` may be brittle. A failure before attach leaves the accounting behavior untested, although cleanup still closes the socket.

Test signals: pass criteria are successful map updates, successful skeleton attach, close of the socket, `cookie_found` equal to `2`, and `omem` equal to `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_storage_omem_uncharge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_storage_tracing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_storage_tracing.c

Purpose: `sk_storage_tracing.c` tests BPF socket storage from tracing programs while TCP sockets transition through listen, shutdown, and close-related states. It also verifies that a program attempting to trace itself with sk_storage is rejected or unavailable as expected.

Important APIs/types/functions: `struct sk_stg` mirrors BPF map values containing `pid`, `last_notclose_state`, and `comm`. `check_sk_stg()` looks up per-socket storage and validates state, PID, and task command. `do_test()` creates a TCP IPv6 loopback connection, seeds `del_sk_stg_map`, performs half-closes, and validates storage cleanup and state capture. `serial_test_sk_storage_tracing()` is the serial entry point.

Control flow: the serial test records `my_pid`, attempts to open/load `test_sk_storage_trace_itself` and expects a null result, opens/loads `test_sk_storage_tracing`, attaches tracing programs, and runs `do_test()`. `do_test()` starts an IPv6 server, connects to it, inserts the active socket into a delete map, accepts the passive side, performs active and passive `shutdown(SHUT_WR)` operations with EOF reads, confirms the delete map no longer contains the active socket, and validates captured states for listener (`BPF_TCP_LISTEN`), active (`BPF_TCP_FIN_WAIT2`), and passive (`BPF_TCP_LAST_ACK`) sockets.

State and persistence: state lives in skeleton maps `sk_stg_map` and `del_sk_stg_map`, BSS `task_comm`, process PID, and transient TCP socket FDs. No persistent output is produced. The test is serial because tracing hooks and global socket-storage observations can interfere with parallel tests.

Dependencies: depends on IPv6 loopback TCP support, selftest `start_server()`/`connect_to_fd()` helpers, BPF sk_storage maps, tracing program attach support, TCP state constants, and libbpf skeletons for both accepted and rejected BPF objects.

Integration points: integrates tracing hooks with socket storage, kernel TCP state tracking, process identity reporting through BPF, and map deletion semantics keyed by socket FDs.

Risks: TCP close state timing is sensitive; different kernel state transitions could alter expected `FIN_WAIT2` or `LAST_ACK` observations. The `read()` assertions use `ASSERT_OK(err)` after EOF reads, so the intended zero-byte EOF path matters. It also depends on `TEST_COMM`/task command alignment with the BPF-side captured comm.

Test signals: the rejected `test_sk_storage_trace_itself` load, successful tracing skeleton attach, deletion of `del_sk_stg_map` entry, and exact `sk_stg_map` state/PID/comm matches for listen, active, and passive sockets are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_storage_tracing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_ctx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_ctx.c

Purpose: `skb_ctx.c` validates `bpf_prog_test_run_opts()` handling of `struct __sk_buff` context input/output for a `BPF_PROG_TYPE_SCHED_CLS` program. It checks that invalid context sizes and prohibited nonzero fields are rejected, then verifies that writable context fields are modified as expected.

Important APIs/types/functions: `test_skb_ctx()` constructs a `struct __sk_buff`, fills `LIBBPF_OPTS(bpf_test_run_opts)`, loads `test_skb_ctx.bpf.o` with `bpf_prog_test_load()`, runs `bpf_prog_test_run_opts()`, and validates returned context fields. It uses `pkt_v4` from `network_helpers.h` as packet data.

Control flow: the test first verifies that `ctx_in` with zero `ctx_size_in` and `ctx_out` with zero `ctx_size_out` both fail. It then sets nonzero `len`, `tc_index`, `hash`, and `sk` fields one by one and expects rejection. With a valid context, it runs the BPF program and checks `retval`, output context size, incremented `cb[]`, `priority`, `tstamp`, and `mark`, while stable fields such as `ifindex` and `ingress_ifindex` remain as expected.

State and persistence: state is entirely local to the loaded BPF object, the `__sk_buff` context buffer, and test-run options. There is no socket, namespace, or durable state.

Dependencies: requires `test_skb_ctx.bpf.o`, libbpf program test-run support for SCHED_CLS, `struct __sk_buff` context validation in the kernel, and IPv4 packet fixture data.

Integration points: this file bridges userspace BPF test-run APIs with the kernel's skb context validation and writable-field behavior for classifier programs.

Risks: the test encodes the exact set of context fields rejected by the kernel. If kernel policy changes for fields such as `tc_index`, `hash`, or `sk`, this test will need adjustment. It also assumes fixed output modifications performed by the paired BPF object.

Test signals: expected failures for zero context sizes and prohibited fields, followed by a successful run with `retval == 0`, full context output size, and expected incremented context fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_helpers.c

Purpose: `skb_helpers.c` is a compact smoke test for skb helper behavior in a SCHED_CLS test-run context. It loads `test_skb_helpers.bpf.o` and runs it against a small IPv4 packet and a `struct __sk_buff` containing GSO and wire-length metadata.

Important APIs/types/functions: `test_skb_helpers()` creates `struct __sk_buff` with `wire_len`, `gso_segs`, and `gso_size`, prepares `bpf_test_run_opts`, calls `bpf_prog_test_load()` for `BPF_PROG_TYPE_SCHED_CLS`, executes `bpf_prog_test_run_opts()`, and closes the object.

Control flow: there is a single load/run/close path. Any helper-specific assertions are implemented inside the paired BPF object; the userspace side checks only that load and test-run succeed.

State and persistence: state is limited to the local skb context and BPF object FD. No maps, sockets, namespaces, or files are persisted.

Dependencies: depends on `test_skb_helpers.bpf.o`, libbpf test-run APIs, packet fixture `pkt_v4`, and kernel support for the skb helper set used by the BPF program.

Integration points: integrates the selftest runner with SCHED_CLS program loading and test-run execution for helpers that consume skb metadata such as GSO and wire length.

Risks: because the userspace side has no explicit result checks, regressions must be surfaced by the BPF program's return value or load/run failure. If helper behavior changes but the BPF program still returns success, this wrapper will not detect it.

Test signals: successful BPF object load and successful `bpf_prog_test_run_opts()` are the observable signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_load_bytes.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_load_bytes.c

Purpose: `skb_load_bytes.c` verifies `bpf_skb_load_bytes()` behavior for invalid and valid offsets in a SCHED_CLS-style test-run. It checks that an all-ones offset fails with `-EFAULT` while a normal offset succeeds.

Important APIs/types/functions: `test_skb_load_bytes()` opens and loads `skb_load_bytes.skel.h`, obtains the `skb_process` program FD, sets BSS field `load_offset`, runs `bpf_prog_test_run_opts()`, and reads BSS `test_result`. It uses `pkt_v4` and an empty `struct __sk_buff`.

Control flow: after skeleton load, the test sets `load_offset` to `(uint32_t)-1`, runs the program, and expects `test_result == -EFAULT`. It then sets offset `10`, reruns, and expects `test_result == 0`. Cleanup destroys the skeleton.

State and persistence: state is in skeleton BSS fields and the local test-run context. There is no persistent external state.

Dependencies: depends on the `skb_load_bytes` BPF skeleton, SCHED_CLS test-run support, `bpf_skb_load_bytes()` helper behavior, and the IPv4 packet fixture.

Integration points: links userspace test-run setup to BPF-side helper return codes for packet byte access.

Risks: expected errno is exact; helper or verifier behavior changes for out-of-range offsets would require updating the test. The valid offset assumes the packet fixture is long enough for the BPF program's load size.

Test signals: two successful test-run calls with BSS `test_result` equal to `-EFAULT` and `0`, respectively.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_load_bytes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skc_to_unix_sock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skc_to_unix_sock.c

Purpose: this test validates the `bpf_skc_to_unix_sock()` conversion path for Unix sockets by triggering a Unix listen operation and checking that the BPF program captured the abstract socket path.

Important APIs/types/functions: `test_skc_to_unix_sock()` opens `test_skc_to_unix_sock.skel.h`, sets rodata `my_pid`, loads and attaches the skeleton, creates an `AF_UNIX` stream socket, binds it to an abstract path, calls `listen()`, and compares skeleton BSS `path` with `sock_path`.

Control flow: open skeleton, set PID filter, load, attach, create Unix socket, initialize `sockaddr_un` with `sun_path[0] = '\0'` for abstract namespace, bind, listen, assert the captured path string matches `"@skc_to_unix_sock"`, then close/destroy.

State and persistence: state is one Unix socket FD, skeleton rodata/BSS, and transient abstract Unix namespace entry. No filesystem socket path is created because the address is abstract.

Dependencies: requires the paired BPF skeleton, Unix domain sockets, BPF attach point used by the BPF program for `unix_listen`, and kernel support for converting `sock_common` to `unix_sock`.

Integration points: exercises BTF/kfunc or helper-based socket type conversion from a kernel socket context into Unix-specific fields, using a real userspace bind/listen trigger.

Risks: abstract Unix path formatting is subtle: the userspace string stores `"@..."` but the sockaddr uses a leading NUL. If BPF-side path normalization changes, the string comparison will fail. The socket FD is initialized to `0`, so cleanup closes it only after successful positive FD creation.

Test signals: successful load/attach, successful abstract Unix bind/listen, and exact BSS path match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skc_to_unix_sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skeleton.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skeleton.c

Purpose: `skeleton.c` is a broad libbpf skeleton contract test. It verifies generated skeleton accessors for `.bss`, `.data`, `.rodata`, dynamic data/rodata maps, kconfig externs, read-mostly data, mmap flags, non-mmapable maps, packed structs, and embedded ELF bytes.

Important APIs/types/functions: `test_skeleton()` uses `test_skeleton__open/load/attach/destroy()`, map name inspection through `bpf_map__name()`, `bpf_map__fd()`, `bpf_map__map_flags()`, `mmap()`, and `test_skeleton__elf_bytes()`. The local packed `struct s` matches BPF-side global data layout.

Control flow: the test opens the skeleton and asserts kconfig is not mmaped before load. It validates initial `.data`, `.bss`, `.rodata`, `.rodata.dyn`, and `.data.dyn` values, writes preload values into data/BSS/rodata, loads and confirms values remain, writes runtime inputs, sets a read-mostly variable, attaches the program, triggers a tracepoint with `usleep(1)`, and verifies output globals, kconfig extern values, dynamic arrays, huge array tail, non-mmapable map behavior, and embedded ELF byte access.

State and persistence: state is skeleton-owned mmaped data sections, BPF maps, BPF links after attach, and one failed `mmap()` check against a non-mmapable map FD. No durable output is produced.

Dependencies: depends on libbpf skeleton generation, global data map mmap support, kconfig extern population, tracepoint attach/trigger behavior, and the paired `test_skeleton.bpf.o` layout.

Integration points: this is a libbpf API integration test rather than a networking test. It validates that userspace C structs generated by bpftool stay ABI-compatible with BPF global variables and map flags.

Risks: checks are tightly coupled to the BPF object's initialized values and section names. Tracepoint triggering via `usleep(1)` assumes the attached program observes a sched/syscall-related event quickly. Kconfig extern availability and map mmap behavior are kernel/config dependent.

Test signals: correct initial/preload/post-attach values, kconfig values copied into BSS, dynamic array outputs, failed mmap on `data_non_mmapable`, map flags equal zero for that map, and non-null embedded ELF bytes with nonnegative size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skeleton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/snprintf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/snprintf.c

Purpose: `snprintf.c` tests `bpf_snprintf()` formatting and verifier validation. Positive coverage checks numeric, IP, symbol, pointer, string, overflow, padding, no-argument, and no-buffer formats; negative coverage checks invalid format strings are rejected at load time.

Important APIs/types/functions: `test_snprintf_positive()` loads and attaches `test_snprintf.skel.h`, sets BSS `pid`, triggers the program, and compares BSS output buffers and return values. `load_single_snprintf()` injects a candidate format into `test_snprintf_single` rodata and attempts load. `test_snprintf_negative()` asserts valid and invalid load results. `test_snprintf()` creates two subtests.

Control flow: the positive subtest opens/loads, filters by PID, attaches, triggers with `usleep(1)`, and checks all expected strings/return lengths. Symbol and hashed pointer output use prefix/minimum comparisons where exact content is kernel/compiler dependent. The negative subtest repeatedly opens a single-format skeleton, copies up to ten bytes of the requested format into rodata, loads it, and asserts whether the verifier accepts or rejects it.

State and persistence: state is in skeleton rodata/BSS buffers and return values. There are no sockets, maps beyond skeleton globals, or persistent files.

Dependencies: requires `bpf_snprintf()` helper support, symbol formatting, BPF verifier format-string validation, tracepoint attachment used by the BPF object, and libbpf skeletons `test_snprintf` and `test_snprintf_single`.

Integration points: integrates helper runtime formatting behavior with verifier-time format validation and userspace skeleton BSS observation.

Risks: expected return values include C string terminators via `sizeof()`, so edits to expected constants must preserve the helper's return convention. Symbol output depends on compiler inlining and kernel symbol formatting; the test deliberately checks only a stable prefix/minimum. Pointer hashing changes across boots, so only a prefix and expected length are checked.

Test signals: positive subtest exact matches for stable formats, prefix/minimum matches for symbol/pointer formats, and negative subtest load acceptance/rejection for valid, unterminated, too-many-specifier, invalid-specifier, non-ASCII, and non-printable format strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/snprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/snprintf_btf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/snprintf_btf.c

Purpose: `snprintf_btf.c` demonstrates and validates `bpf_snprintf_btf()` formatting for multiple data types from a network receive hook. It ensures the BPF program ran, returned a positive formatting result, and executed all BPF-side subtests.

Important APIs/types/functions: `serial_test_snprintf_btf()` opens, loads, and attaches `netif_receive_skb.skel.h`, triggers receive processing with `system("ping -c 1 127.0.0.1 > /dev/null")`, then checks BSS fields `skip`, `ret`, `ran_subtests`, and `num_subtests`.

Control flow: open skeleton, load, attach, run a loopback ping, handle BPF-side `skip` if `__builtin_btf_type_id` is unavailable, assert positive `bpf_snprintf_btf` return, assert at least one subtest ran, and assert all declared subtests ran.

State and persistence: state is skeleton BSS counters and transient ICMP loopback traffic. No durable files are produced, but the test shells out to `ping`.

Dependencies: requires BTF support, `bpf_snprintf_btf()`, BPF program attachment to the receive path, loopback networking, the `ping` command, and serial execution to avoid shared network/BTF side effects.

Integration points: links BPF BTF pretty-print formatting with a real `netif_receive_skb` trigger and userspace selftest skip/pass accounting.

Risks: depends on external `ping` availability and permission. Systems lacking compiler/kernel support for `__builtin_btf_type_id` intentionally skip. If loopback receive path is filtered or ping unavailable, the BPF program may not run.

Test signals: no skip unless expected, positive `ret`, nonzero `ran_subtests`, and `ran_subtests == num_subtests`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/snprintf_btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_addr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_addr.c

Purpose: `sock_addr.c` is the central cgroup socket-address hook selftest matrix. It verifies BPF programs for bind, connect, sendmsg, recvmsg, getsockname, and getpeername hooks across IPv4, IPv6, Unix sockets, user syscalls, and synthetic kernel socket operations implemented by BPF test-run helpers.

Important APIs/types/functions: `struct sock_addr_test` defines each matrix row: test type, subtest name, skeleton load/destroy functions, cgroup attach type, socket operations table, socket family/type, requested and expected endpoint data, expected source rewrite, and expected result. `BPF_SKEL_FUNCS` and `BPF_SKEL_FUNCS_RAW` generate load/attach/destroy wrappers for many skeletons. `struct sock_ops` abstracts user operations and BPF-test-run-backed kernel operations. `run_bpf_prog()`, `kernel_init_sock()`, `kernel_connect()`, `kernel_bind()`, `kernel_sendmsg()`, `kernel_getsockname()`, and `kernel_getpeername()` invoke programs in `sock_addr_kern.skel.h` through `bpf_prog_test_run_opts()`. `cmp_addr()` and `cmp_sock_addr()` validate rewritten addresses.

Control flow: `test_sock_addr()` joins `/sock_addr` cgroup, creates a named netns with loopback and veth IPv4/IPv6 addresses, loads the kernel-operation helper skeleton, then iterates the large `tests[]` table. For each subtest, it loads and attaches the target cgroup program, dispatches to `test_bind()`, `test_connect()`, `test_xmsg()`, `test_getsockname()`, or `test_getpeername()`, verifies expected errno or success, and destroys the skeleton. Test helpers create requested addresses, run the operation through the selected `sock_ops`, and compare local, peer, or source addresses with expected rewritten values.

State and persistence: runtime state includes the `/sock_addr` cgroup FD, named netns `sock_addr`, veth devices named `test_sock_addr1/2`, loopback/veth addresses, the global `sock_addr_kern` skeleton, many transient sockets, and cgroup-attached BPF links. Cleanup unloads the helper skeleton, closes the netns token, deletes the netns, and closes the cgroup FD. No durable output is produced.

Dependencies: depends on many generated skeletons (`bind4_prog`, `bind6_prog`, `connect*_prog`, `sendmsg*_prog`, `recvmsg*_prog`, `getsockname*_prog`, `getpeername*_prog`, and Unix variants), cgroup v2 selftest helpers, network namespace and veth creation via `ip`, IPv4/IPv6/Unix socket support, and kernel support for cgroup socket-address attach types including Unix getname hooks.

Integration points: integrates cgroup BPF attach APIs, userspace sockets, synthetic in-kernel socket operations driven by BPF test-run, network helper utilities, and the selftest cgroup/network namespace harness. It also serves as the high-level table defining expected address rewrite and denial semantics for multiple BPF hook families.

Risks: the file is table-heavy and easy to regress by mismatching attach type, socket family, or expected address. The source snapshot includes duplicated text in `kernel_getpeername()` and an extra `{` visible in the table region; these are source-quality risks that should be checked at compile time. Netns/veth setup requires privileges and `ip`; cleanup must run to avoid leaked netns. Unix sockaddr length comparisons are byte-level, so address-length mismatches can fail even when visible names match. Kernel-operation paths rely on the helper skeleton's single implicit socket state rather than real FDs.

Test signals: each matrix row reports a named subtest. Key signals are load rejection for wrong expected attach type, attach rejection for raw wrong attach type, `EPERM` for deny programs, `ENOTSUPP` for unsupported cases, success for rewrite cases, and exact address/source comparisons after bind/connect/sendmsg/recvmsg/getsockname/getpeername.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_create.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_create.c

Purpose: `sock_create.c` tests `BPF_CGROUP_INET_SOCK_CREATE` programs that mutate or deny socket creation. It validates priority, mark, bound device, protocol filtering, and compatibility behavior when `expected_attach_type` is omitted.

Important APIs/types/functions: `struct sock_create_test` stores a description, raw BPF instruction array, attach/expected attach type, socket domain/type/protocol, expected socket option, and expected error category. `load_prog()` loads `BPF_PROG_TYPE_CGROUP_SOCK` instructions with verifier log options. `run_test()` attaches the program to a cgroup, creates a socket, reads expected socket options, and detaches.

Control flow: `test_sock_create()` joins `/sock_create`, iterates the table as subtests, and asserts `run_test()` succeeds. Each run loads the inline instructions, attaches to the cgroup, calls `socket()`, treats denied creates as success only for `DENY_CREATE`, checks `SO_PRIORITY`, `SO_MARK`, or `SO_BINDTOIFINDEX` when requested, then detaches and closes FDs.

State and persistence: state is a temporary cgroup FD, BPF program FD, one socket FD per subtest, verifier log buffer, and any socket options set by the BPF program. No persistent state is created.

Dependencies: depends on cgroup helpers, raw BPF instruction macros, `bpf_prog_load()`, `bpf_prog_attach()`, `BPF_PROG_TYPE_CGROUP_SOCK`, socket options `SO_PRIORITY`, `SO_MARK`, and `SO_BINDTOIFINDEX`, and root privileges for cgroup/socket mark behavior.

Integration points: exercises the cgroup socket-create hook directly with hand-written BPF instructions instead of skeletons, making it a low-level verifier and hook semantics test.

Risks: inline instruction arrays are brittle and need correct offsets into `struct bpf_sock`. The ICMPv6 denial table row uses `domain = AF_INET` with `protocol = IPPROTO_ICMPV6`, which may be intentional compatibility coverage or a table risk. Expected mark `666` assumes root UID path; non-root execution would use UID as mark.

Test signals: successful mutation of priority/mark/bound interface for IPv4 and IPv6 UDP sockets, denied ICMP/ICMPv6 creation where expected, and successful load/attach without `expected_attach_type` in compatibility mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_destroy.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_destroy.c

Purpose: `sock_destroy.c` tests BPF socket destruction from iterator programs for TCP and UDP client/server sockets. It verifies that iterator-triggered destruction produces expected application-visible errors and that invalid destruction programs fail via `RUN_TESTS(sock_destroy_prog_fail)`.

Important APIs/types/functions: `start_iter_sockets()` attaches a BPF iterator program, creates an iterator FD, and drains it to execute socket-destroy logic. `test_tcp_client()`, `test_tcp_server()`, `test_udp_client()`, and `test_udp_server()` create sockets and invoke specific iterator programs from `sock_destroy_prog.skel.h`. `test_sock_destroy()` manages cgroup/netns setup and subtest dispatch.

Control flow: the top-level test loads the skeleton, joins `/sock_destroy`, attaches a cgroup `sock_connect` program, creates and enters netns `sock_destroy_netns`, then runs TCP client, TCP server, UDP client, and UDP server subtests. TCP client/server tests establish connections, send once, run the destroy iterator, then assert the next send fails with `ECONNABORTED` for destroyed client or `ECONNRESET` for destroyed server. UDP server starts a reuseport group, destroys all server sockets by port, then asserts reads fail with `ECONNABORTED`.

State and persistence: state includes the named netns, cgroup link, BPF iterator links/FDs, listener/client/accepted sockets, skeleton BSS `serv_port`, and reuseport FD arrays. Cleanup closes netns and deletes it with `ip netns del`.

Dependencies: depends on BPF iterators over sockets, `bpf_sock_destroy()` behavior in the BPF object, cgroup connect hook support, IPv6 loopback networking, reuseport UDP helpers, and network namespace tooling.

Integration points: integrates cgroup hooks that mark or filter sockets with iterator programs that walk and destroy sockets, then validates visible userspace socket error semantics.

Risks: errno expectations depend on TCP/UDP state and kernel destroy semantics. Iterator drain relies on reading until EOF; partial iterator failures could leave sockets alive. Netns cleanup uses `SYS_NOFAIL`, so leaked state is unlikely but still possible if process dies abruptly.

Test signals: failed send/read after iterator destruction with expected errno, successful destruction of all reuseport UDP server sockets, and expected failures from `sock_destroy_prog_fail` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_destroy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_fields.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_fields.c

Purpose: `sock_fields.c` validates BPF access to `struct bpf_sock`, `struct bpf_tcp_sock`, cgroup IDs, and socket-local storage counters from cgroup skb programs. It drives a real IPv6 TCP connection and checks that ingress/egress programs captured correct socket and TCP state.

Important APIs/types/functions: `check_result()` reads skeleton BSS snapshots of listener/server/client `bpf_sock` and `bpf_tcp_sock`, validates line-number error map entries, and compares cgroup IDs. `check_sk_pkt_out_cnt()` verifies socket storage counters for accepted and client sockets. `init_sk_storage()` seeds two sk_storage maps. `test()` creates the TCP flow and sends data. `serial_test_sock_fields()` sets up netns/cgroups and attaches BPF programs.

Control flow: serial setup unshares a network namespace, brings loopback up, joins parent and child cgroups, records cgroup IDs, opens/loads the skeleton, attaches egress/ingress/read-dst-port programs to the child cgroup, records map FDs, and runs `test()`. The flow listens on `::1:0xcafe`, connects, accepts, seeds storage for the accepted socket, sends two `MSG_EOR` messages from server to client, performs shutdown handshakes, then validates packet counters and captured fields.

State and persistence: state includes the process network namespace after `unshare(CLONE_NEWNET)`, cgroup FDs/IDs, skeleton maps `linum_map`, `sk_pkt_out_cnt`, `sk_pkt_out_cnt10`, BSS snapshots of socket fields, and three TCP socket FDs. No durable files are written.

Dependencies: depends on cgroup skb attach support, sk_storage with spin locks, BPF access to socket/tcp fields, IPv6 loopback TCP, cgroup helper APIs, and specific TCP state/metric behavior after two data packets and shutdown.

Integration points: ties cgroup ingress/egress programs to socket field snapshots, TCP accounting, socket storage counters, and cgroup identity propagation.

Risks: TCP metrics such as `snd_cwnd`, `bytes_acked`, `bytes_received`, and packet counters are kernel-behavior sensitive. The test expects a fixed listen port and therefore creates a dedicated netns. Packet coalescing is mitigated with `MSG_EOR` but remains a networking timing risk. The test is serial because it changes namespace and cgroup state.

Test signals: zero line-number failure for dst-port access, correct listener/server/client socket addresses and ports, sensible TCP counters, expected cgroup IDs, and storage counters at least `0xeB9F + 2/20` for passive and `0xeB9F + 4/40` for active sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_fields.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_iter_batch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_iter_batch.c

Purpose: `sock_iter_batch.c` stress-tests batched BPF socket iterator resume behavior. It verifies that iterating socket hash buckets remains correct when sockets are removed, added, or force iterator batch reallocation while iteration is in progress for UDP, TCP listening sockets, and TCP established sockets.

Important APIs/types/functions: `struct iter_out` is the BPF iterator output record with bucket index and socket cookie. `struct sock_count` tracks unique cookies and occurrence counts. `read_n()` drains a requested number of iterator records. `get_nth_socket()`, `was_seen()`, and `check_n_were_seen_once()` correlate iterator cookies with userspace socket FDs. Mutation helpers include `remove_seen`, `remove_unseen`, `remove_all`, `add_some`, `force_realloc`, and established-socket variants. `do_resume_test()` runs table-driven mutation scenarios. `do_test()` verifies simple two-bucket batched reads.

Control flow: `test_sock_iter_batch()` creates netns `sock_iter_batch_netns`, enters it, runs TCP and UDP simple batch tests with one-by-one and bulk reads, then runs `do_resume_tests()`. Simple tests create two reuseport groups, load the iterator skeleton with target ports/family/state, attach the TCP or UDP iterator, partially read one bucket, close that bucket, then verify the second bucket is read fully. Resume tests create reuseport groups and optionally established TCP connections, attach an iterator, read part of the stream, mutate sockets according to the test case, then confirm remaining original sockets are seen exactly once or no extra sockets are returned.

State and persistence: state includes named parent and child netns, optional sysctl `net.ipv4.tcp_child_ehash_entries`, reuseport listener arrays, accepted/connected socket arrays, BPF iterator links/FDs, skeleton rodata filter fields, and in-memory cookie counts. Cleanup deletes netns, resets the sysctl to `0`, frees FD arrays, and destroys links/skeletons.

Dependencies: depends on BPF socket iterators, reuseport server helpers, socket cookies, TCP/UDP IPv4/IPv6 loopback, `poll()`/accept helpers, network namespace tools, and permission to set `net.ipv4.tcp_child_ehash_entries` for established-socket collision scenarios.

Integration points: exercises the kernel BPF iterator batch/resume implementation under concurrent socket table mutations, including direct BPF-side socket destruction through `iter_tcp_destroy`.

Risks: timing and hash bucket placement are central. The test intentionally forces buckets and collisions, but port hashing can still produce rare collisions handled by conditional assertions. The source snapshot shows duplicated parameter text in `remove_seen()` and duplicated `.sock_type` assignment in the test table; these are source-quality risks. Mutation helpers can leak `close_idx` allocation on early return in `remove_all_established`. Sysctl manipulation must be restored or later networking tests may be affected.

Test signals: no duplicate cookie sightings, expected counts of sockets seen exactly once after each mutation, iterator EOF when all sockets are removed, successful realloc stress cases, and successful TCP/UDP simple batch reads in both one-by-one and bulk modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_iter_batch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_ops_get_sk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_ops_get_sk.c

Purpose: `sock_ops_get_sk.c` verifies that a sock_ops BPF program can obtain and use a socket reference through the get-sk helper path during a TCP connection.

Important APIs/types/functions: `run_sock_ops_test()` attaches a sock_ops program to a cgroup with `bpf_prog_attach(BPF_CGROUP_SOCK_OPS)`, starts an IPv6 TCP server, connects a client, and closes both sockets. `test_ns_sock_ops_get_sk()` loads `sock_ops_get_sk.skel.h`, joins `/sock_ops_get_sk`, runs the helper test, and destroys the skeleton.

Control flow: load skeleton, join cgroup, obtain program FD for `sockops_get_sk`, attach to cgroup, create server and client connection, then close sockets and cgroup FD. Assertions ensure program attach and socket operations succeed.

State and persistence: state is limited to a cgroup FD, BPF program attachment, server/client socket FDs, and skeleton lifetime. No durable state is written.

Dependencies: requires cgroup sock_ops attach support, IPv6 loopback TCP, the paired skeleton, and selftest network/cgroup helpers.

Integration points: connects sock_ops cgroup hooks with real TCP connection establishment so the BPF-side helper can be exercised in kernel context.

Risks: userspace does not inspect BPF-side counters, so detailed helper correctness must be asserted by the BPF object or verifier. If the program loads and attaches but silently does not observe the expected callback, this wrapper may not detect it unless BPF-side state causes failure.

Test signals: successful skeleton load, cgroup join, sock_ops attach, server start, and client connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_ops_get_sk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_post_bind.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_post_bind.c

Purpose: `sock_post_bind.c` tests cgroup post-bind programs for IPv4 and IPv6 sockets. It validates attach type compatibility, allow/deny verdicts after bind, denial for specific IP/port combinations, and retry behavior on alternate ports.

Important APIs/types/functions: `struct sock_post_bind_test` holds raw BPF instructions, attach/expected attach type, socket domain/type, bind IP/port/retry port, and expected result. `load_prog()` loads inline `BPF_PROG_TYPE_CGROUP_SOCK` programs. `bind_sock()` performs the bind and optional retry. `run_test()` loads, attaches, runs bind, and detaches.

Control flow: `test_sock_post_bind()` joins `/post_bind`, creates a netns object, iterates the table as subtests, and asserts `run_test()` succeeds. Each run loads the program with expected attach type, attaches to the requested post-bind hook, handles expected attach rejection, binds a socket to the configured address/port, treats `EPERM` as BPF denial, retries on configured alternate port, and compares the resulting category with the expected result.

State and persistence: state is the cgroup FD, netns object, raw BPF program FD, one socket per subtest, and verifier log buffer. Cleanup frees the netns and closes the cgroup.

Dependencies: depends on cgroup post-bind attach types, raw BPF instruction macros, IPv4/IPv6 socket binding, `inet_pton()`, cgroup helpers, and `netns_new()`.

Integration points: exercises the post-bind cgroup hook after socket address assignment and before userspace observes bind success.

Risks: exact source-port checks use constants in network byte order and are easy to misread (`0x1002`, `0x2001`). The test treats non-`EPERM` bind failures as infrastructure errors, so occupied ports or namespace setup issues can obscure BPF behavior. Attach rejection paths still call detach best-effort on the program FD.

Test signals: expected attach rejection for mismatched attach types, expected `BIND_REJECT`, `SUCCESS`, `RETRY_SUCCESS`, or `RETRY_REJECT` for each bind scenario, and verifier log output on load failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_post_bind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/socket_cookie.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/socket_cookie.c

Purpose: `socket_cookie.c` tests socket-cookie collection and update across cgroup and tracing programs. It validates that a TCP client socket cookie maps to a value derived from the client's local port.

Important APIs/types/functions: `struct socket_cookie` mirrors map values with `cookie_key` and `cookie_value`. `test_socket_cookie()` opens `socket_cookie_prog.skel.h`, joins `/socket_cookie`, attaches cgroup and tracing programs, creates a TCP IPv6 loopback connection, looks up `socket_cookies` by client FD, obtains the client's local port with `getsockname()`, and computes the expected value.

Control flow: load skeleton, join cgroup, attach `set_cookie` and `update_cookie_sockops` to the cgroup, attach tracing updater, start server, connect client, look up map value, read local port, assert `cookie_value == (ntohs(port) << 8) | 0xFF`, then close sockets/cgroup and destroy skeleton.

State and persistence: state includes cgroup links, tracing link, server/client sockets, skeleton map `socket_cookies`, and one looked-up cookie value. No durable output is created.

Dependencies: depends on socket cookie helpers, cgroup attach support, sock_ops/tracing programs in the skeleton, IPv6 loopback TCP, and map lookup by socket FD.

Integration points: combines cgroup socket hooks, sock_ops/tracing updates, map entries keyed by socket reference, and userspace validation from socket metadata.

Risks: the expected value encodes BPF-side policy; if the BPF object changes, userspace must change with it. Map lookup by socket FD requires the BPF map type/key semantics to match the kernel's socket-storage or socket-cookie behavior.

Test signals: successful attachment of all three programs, successful TCP connection, successful map lookup, and exact computed cookie value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/socket_cookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/socket_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/socket_helpers.h

Purpose: `socket_helpers.h` provides reusable socket utilities for BPF socket selftests. It centralizes assertion-reporting wrappers, loopback address initialization, timed accept/recv/connect helpers, socket pair creation across address families, automatic FD cleanup, and socket-kind stringification.

Important APIs/types/functions: failure macros `_FAIL`, `FAIL`, `FAIL_ERRNO`, and `FAIL_LIBBPF` report via `error_at_line()` and `CHECK_FAIL()`. `xaccept_nonblock`, `xbind`, `xclose`, `xconnect`, `xgetsockname`, `xgetsockopt`, `xlisten`, `xsetsockopt`, `xsend`, `xrecv_nonblock`, and `xsocket` wrap syscalls with assertions. `init_addr_loopback*()` build AF_INET, AF_INET6, AF_UNIX, and AF_VSOCK loopback addresses. `socket_loopback_reuseport()` creates a bound/listening or datagram socket and optionally attaches a reuseport BPF program. `create_pair()` and `create_socket_pairs()` build connected endpoint pairs. `socket_kind_to_str()` returns compact family/type labels.

Control flow: helpers generally initialize a sockaddr, create sockets, bind/connect/listen as needed, and return either FDs or negative errors while marking selftest failures. `create_pair()` creates a server and client, handles nonblocking/in-progress connects through `poll_connect()`, then for datagram sockets connects the server back to the client, while stream/seqpacket sockets accept a peer. Cleanup uses `take_fd()` and `__close_fd` to transfer ownership safely.

State and persistence: the header itself persists no state. Callers receive live socket FDs and must close them or use cleanup attributes. Helper timeouts use `IO_TIMEOUT_SEC = 30`; error string buffers use `MAX_STRERR_LEN = 256`.

Dependencies: depends on POSIX sockets, `select()`, Unix sockets, Linux vsock definitions, libbpf error formatting, and the BPF selftest assertion framework. It includes compatibility definitions for `VMADDR_CID_LOCAL`, `auto`, and cleanup-style helpers.

Integration points: used by sockmap and kTLS tests to reduce repeated socket setup and error handling. It bridges standard socket APIs with selftest reporting conventions.

Risks: wrappers mark failures but still return syscall values; callers must check them. `poll_connect()` uses `select()` and `SO_ERROR`, which is adequate for selftests but not a general event loop. AF_UNIX loopback initialization only sets `sa_family_t` length, so callers needing named paths must override it. VSOCK support depends on local kernel/transport support.

Test signals: indirect signals come from users such as sockmap tests. A helper works when connected pairs can send/receive data, timeouts catch stalled I/O, and wrapper failures include useful syscall context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/socket_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_basic.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_basic.c

Purpose: `sockmap_basic.c` is a broad sockmap/sockhash regression suite. It covers map creation/update/free, socket lifetime cleanup, SK_MSG and SK_SKB attach/query APIs, BPF link update semantics, map-to-map socket copying, FIONREAD/MSG_PEEK/shutdown behavior, Unix/vsock edge cases, zero-copy receive recovery, copied sequence recovery, and mixed native/BPF redirect channels.

Important APIs/types/functions: `connected_socket_v4()` creates a TCP socket using `TCP_REPAIR` to synthesize a connected socket. `compare_cookies()` compares socket cookies across maps. Test functions cover create/update/free, vsock delete-on-close, `test_skmsg_helpers[_with_link]`, `test_sockmap_update()`, `test_sockmap_copy()`, SKB verdict attach/query paths, shutdown/FIONREAD/change-tail/peek behavior, Unix/vsock update restrictions, many sockets/maps replacement, zero-copy, copied-seq, and multi-channel delivery. `test_sockmap_basic()` dispatches all subtests.

Control flow: most subtests load a relevant skeleton, create one or more socket pairs, update a sockmap/sockhash with socket FDs, attach a verdict/parser/msg program through `bpf_prog_attach()` or `bpf_program__attach_sockmap()`, then drive traffic or map operations and assert kernel-visible behavior. Iterator copy tests populate source maps, attach a map-specific iterator, drain it, and compare cookies. Data-path tests send through one endpoint and observe received bytes, `FIONREAD`, `MSG_PEEK`, FIN notification, tail changes, copied sequence recovery, or zero-copy receive behavior.

State and persistence: runtime state includes many transient TCP, UDP, Unix, and vsock sockets; BPF maps from skeletons and explicit `bpf_map_create()` calls; BPF links and attached programs; epoll FDs; and temporary buffers. No durable file state is created. Each subtest closes sockets and destroys skeletons locally.

Dependencies: depends on sockmap/sockhash kernel support, SK_MSG/SK_SKB attach types, BPF links for sockmap programs, BPF iterators over sockmap/sockhash, TCP repair and zero-copy receive support, AF_UNIX and AF_VSOCK support, `FIONREAD`, `MSG_PEEK`, epoll, and multiple generated skeletons.

Integration points: this file is a central integration point between userspace socket APIs, BPF sockmap/sockhash map semantics, libbpf attach/query/link APIs, and kernel stream parser/verdict implementations. It also relies on shared helpers from `sockmap_helpers.h` and `socket_helpers.h`.

Risks: many tests are kernel-version and config sensitive, especially TCP repair, vsock local transport, TCP zero-copy receive, and copied-seq behavior. The source snapshot includes duplicated assignment lines and an extra-looking brace in `test_sockmap_same_sock()`, which are compile/source-quality risks to verify. `fmt_test_name()`-style issues are not here, but some subtests reuse one socket in multiple entries and expect precise delete behavior. Data-path tests can be timing-sensitive, so `wait_for_fionread()` was added for multi-channel readiness.

Test signals: successful subtests across the dispatch list are the signal set: map update/free for sockmap and sockhash, expected failure of unsafe update object load, matching socket cookies after map copy/update, `-EBUSY` for conflicting attaches, correct `bpf_prog_query()` IDs, FIN readiness through epoll, FIONREAD values for pass/drop, MSG_PEEK preserving queued bytes, Unix/vsock expected accept/reject behavior, zero-copy receive success after sockmap removal, copied sequence recovery for native traffic, and TCP/UDP multi-channel data integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_basic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_helpers.h

Purpose: `sockmap_helpers.h` layers sockmap-specific convenience wrappers on top of `socket_helpers.h`. It standardizes failing wrappers for BPF map operations, BPF program attach/detach, pthread creation/join, scalar compound literals, and adding two sockets to a sockmap.

Important APIs/types/functions: `xbpf_map_delete_elem`, `xbpf_map_lookup_elem`, `xbpf_map_update_elem`, `xbpf_prog_attach`, `xbpf_prog_detach2`, `xpthread_create`, and `xpthread_join` mirror the socket wrappers and report selftest failures. `add_to_sockmap()` inserts `fd1` at key `0` and `fd2` at key `1` with `BPF_NOEXIST`. `u32(v)` and `u64(v)` provide addressable compound-literal keys/values.

Control flow: the macros call the underlying libbpf/syscall API, set `errno` where needed for pthread return codes, report failures, and return the raw result. `add_to_sockmap()` performs two updates and returns the second update result when the first succeeds.

State and persistence: the header keeps no state. It operates on caller-owned map/program/socket FDs.

Dependencies: depends on `socket_helpers.h`, libbpf/BPF syscall wrappers made visible through the including translation unit, pthreads for thread wrappers, and selftest failure macros.

Integration points: used by sockmap and kTLS tests to simplify map update and attach error handling while preserving selftest diagnostics.

Risks: like other assertion wrappers, failures are reported but callers must still respect return values. `add_to_sockmap()` assumes integer keys `0` and `1` and 64-bit socket FD values, matching sockmap selftest map definitions but not arbitrary maps.

Test signals: indirect; users should see clear selftest failures for map/attach/pthread errors, and `add_to_sockmap()` should populate two map entries without overwriting existing keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_ktls.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_ktls.c

Purpose: `sockmap_ktls.c` tests interactions between sockmap/sockhash and kernel TLS sockets. It validates that sockmap update rejects sockets already using a ULP, that basic kTLS offload data transfer works, and that SK_MSG verdict programs can cork, push, redirect under buffer pressure, and pop bytes on kTLS TX paths.

Important APIs/types/functions: `init_ktls_pairs()` enables TCP ULP `"tls"` on both endpoints and configures TLS 1.2 AES-GCM-128 TX/RX crypto info. `create_ktls_pairs()` creates a connected pair and initializes kTLS. `test_sockmap_ktls_update_fails_when_sock_has_ulp()` checks map update rejection after TCP_ULP is set. `test_sockmap_ktls_offload()`, `test_sockmap_ktls_tx_cork()`, `test_sockmap_ktls_tx_no_buf()`, and `test_sockmap_ktls_tx_pop()` exercise data transfer and SK_MSG policy operations. `test_sockmap_ktls()` dispatches map/family combinations and IPv4/IPv6 stream kTLS tests.

Control flow: map update tests create an explicit sockmap or sockhash, create/connect a TCP socket, set TCP_ULP to TLS, assert `bpf_map_update_elem()` fails, then confirm normal TCP setsockopt still dispatches through saved protocol operations. kTLS data tests create socket pairs, attach SK_MSG verdict programs to a sockmap, insert sockets, initialize TLS, set BSS policy knobs (`cork_byte`, `push_start/end`, `apply_bytes`, `pop_start/end`), send data, and validate received length/content or send-loop behavior under buffer pressure.

State and persistence: state includes transient TCP socket pairs, kTLS socket state and crypto info, BPF sockmaps, attached SK_MSG verdict programs, skeleton BSS policy fields, and send/receive buffers. No durable files are created.

Dependencies: requires kernel TLS (`TCP_ULP` `"tls"`, `SOL_TLS`, `TLS_TX`, `TLS_RX`), TLS 1.2 AES-GCM-128 support, sockmap/sockhash, SK_MSG verdict helpers, IPv4/IPv6 TCP, and generated skeletons `test_skmsg_load_helpers` and `test_sockmap_ktls`.

Integration points: bridges kernel TLS protocol replacement with sockmap map-update rules and SK_MSG data manipulation helpers (`cork`, `push`, `pop`, redirect/apply-bytes behavior) on encrypted socket paths.

Risks: kTLS availability is kernel/config dependent and may require crypto support. The source snapshot contains likely bugs in helper formatting (`fmt_test_name()` uses constants rather than parameters) and duplicated `ASSERT_OK(create_pair())` text in `test_sockmap_ktls_tx_no_buf()`. The offload test checks `ASSERT_OK(err, "send(msg)")` after `send()` without assigning `err`, so content/length assertions are more meaningful than that check. Buffer-pressure send loops rely on nonblocking send eventually failing.

Test signals: map update fails for ULP sockets across IPv4/IPv6 and sockmap/sockhash, simple TLS send/recv preserves data and length, cork delays data until full message, push increases received length with expected skipped bytes, no-buffer path exits cleanly under constrained buffers, and pop policies remove the requested byte ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_ktls.c -->
