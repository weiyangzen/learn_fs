# Research: subset-b-006795

Grouped research for the subset-b-006795 BPF selftest sources. Each file section is source-tree-aligned and bounded by split markers for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/lpm_trie_map_basic_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/lpm_trie_map_basic_ops.c

Purpose: broad userspace selftest coverage for `BPF_MAP_TYPE_LPM_TRIE`. It compares kernel trie behavior against a local linear longest-prefix-match oracle, then exercises deterministic IPv4/IPv6 lookup, deletion, `get_next_key`, concurrent operations, update flags, full-map rejection, and iteration ordering.

Important APIs/types/functions: local `struct tlpm_node`, `struct lpm_trie_bytes_key`, and `struct lpm_trie_int_key` model trie keys. `tlpm_add`, `tlpm_match`, `tlpm_delete`, and `tlpm_clear` are the oracle. The kernel-facing paths are `bpf_map_create`, `bpf_map_update_elem`, `bpf_map_lookup_elem`, `bpf_map_delete_elem`, and `bpf_map_get_next_key`, with `LIBBPF_OPTS(bpf_map_create_opts, .map_flags = BPF_F_NO_PREALLOC)`. Test entry `test_lpm_trie_map_basic_ops` dispatches `test_lpm_basic`, `test_lpm_order`, randomized `test_lpm_map` for 1..16 byte keys, IP address cases, delete cases, multithreaded commands, update flag cases, full map cases, and string/integer iteration cases.

Control flow: the randomized tests seed `srand(0xf00ba1)`, insert random prefixes into both the linked-list oracle and kernel map, issue random lookups with full-length query prefixes, then delete half the inserted entries and repeat verification. Deterministic tests build small IPv4/IPv6 prefix trees, check exact longest-match values, delete leaves/intermediate/root nodes, and verify fallback or `ENOENT`. `test_lpm_get_next_key` validates empty-map `ENOENT` and the post-order traversal shape as prefixes are added. `lpm_test_command` runs update/delete/lookup/get-next-key loops concurrently across four pthreads.

State and persistence behavior: persistent state is limited to BPF map FDs and heap/stack test buffers. The LPM trie map stores prefix length in the key header and values either as copied key bytes plus prefix length or simple integers. The oracle linked list owns heap nodes until `tlpm_clear`. Multithreaded tests share one map FD but no persisted external files. All maps are closed at test end.

Dependencies and integration points: this file depends on Linux UAPI BPF types, libbpf's syscall wrappers, `test_maps.h` `CHECK`/test harness macros, `bpf_util.h`, pthreads, endian conversion, and `inet_pton`. It integrates with the map-test executable through exported `test_lpm_trie_map_basic_ops`.

Risks: assertions abort the process on first failure, so resource leaks are acceptable on failed paths but can obscure later checks. Randomized coverage is deterministic but still probabilistic for prefix-shape variety. Concurrent `get_next_key` accepts `ENOMEM` as tolerable, making this more of a panic/race regression signal than a strict iterator semantic check. Endian-sensitive integer iteration relies on explicit big-endian storage.

Test signals: PASS is printed only after all subtests complete. Strong signals include exact `-EINVAL`, `-ENOENT`, `-EEXIST`, `-ENOSPC` checks, value equality against the oracle, sorted string iteration, sorted big-endian integer iteration with deletion between calls, and successful pthread joins returning the expected context pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/lpm_trie_map_basic_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/lpm_trie_map_batch_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/lpm_trie_map_batch_ops.c

Purpose: validates batch update, lookup, and delete operations on LPM trie maps using IPv4 `/32` keys. It checks that batched traversal returns every inserted entry and that batched deletion drains the map for multiple step sizes.

Important APIs/types/functions: `struct test_lpm_key` combines a prefix field and `struct in_addr`. `map_batch_update` prepares `192.168.1.N` keys and values and calls `bpf_map_update_batch`. `map_batch_verify` validates returned key/value pairs by formatting the IPv4 address and comparing the final octet with the stored value. `test_lpm_trie_map_batch_ops` creates the map and drives lookup/delete loops with `bpf_map_lookup_batch`, `bpf_map_delete_batch`, and `bpf_map_get_next_key`.

Control flow: the test creates a no-prealloc LPM trie with ten entries. For each step size from 1 to 9, it repopulates the map, zeroes result arrays, walks batches until `ENOENT`, verifies that all entries were visited, deletes the same keys in batches of the current step, then confirms the map is empty by expecting `bpf_map_get_next_key(NULL)` to fail with `ENOENT`.

State and persistence behavior: state is only a transient BPF map plus heap arrays for keys, values, and visitation. Batch cursor state is the userspace `__u64 batch` token passed as in/out batch. No state persists after the map FD is closed and arrays are freed.

Dependencies and integration points: uses libbpf batch APIs, `test_maps.h`, IPv4 conversion via `inet_pton`/`inet_ntop`, and standard allocation. Exported `test_lpm_trie_map_batch_ops` is invoked by the map test runner.

Risks: `map_batch_verify` treats the returned order as arbitrary but assumes every address encodes an integer 1..10; malformed output could index `visited` incorrectly if the kernel returned an unexpected lower byte. The test does not cover prefixes other than `/32` or mixed prefix lengths, leaving more complex trie-order batch behavior to other tests.

Test signals: errors are surfaced through `CHECK`. Successful completion means every step size returned exactly ten entries, key/value pairs matched the encoded IPv4 address, batched delete removed all entries, and the final empty-map probe returned `ENOENT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/lpm_trie_map_batch_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/lpm_trie_map_get_next_key.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/lpm_trie_map_get_next_key.c

Purpose: stress/regression test for concurrent `bpf_map_get_next_key` on an LPM trie. The stated success condition is absence of kernel panic or userspace crash while many threads repeatedly iterate from the same key.

Important APIs/types/functions: `struct test_lpm_key` stores prefix and data; `struct get_next_key_ctx` shares start/stop flags, the map FD, key, and loop count. `get_next_key_fn` busy-waits for start and repeatedly calls `bpf_map_get_next_key`. `abort_get_next_key` unblocks and joins already-created threads on setup failure. Entry point is `test_lpm_trie_map_get_next_key`.

Control flow: create a no-prealloc LPM trie whose `max_entries` covers all possible prefix lengths for the data field, insert prefixes from 0 to max prefix length, copy the final key into the shared context, spawn up to eight threads, release them by setting `ctx.start`, and join after each thread performs 65,536 calls or sees stop.

State and persistence behavior: shared state is a single mutable context with non-atomic bool flags and a read-only key/map FD after setup. The map contents remain constant during the stress phase. All state is process-local and the map FD is closed at the end.

Dependencies and integration points: uses pthreads, libbpf map APIs, `test_maps.h`, and the map test runner via `test_lpm_trie_map_get_next_key`.

Risks: because return values from `bpf_map_get_next_key` inside worker threads are intentionally ignored, semantic regressions in returned keys are not detected. The `start`/`stop` flags are plain bools, which is acceptable for this stress pattern but not a strict synchronization model. The test assumes enough thread resources to create eight workers.

Test signals: setup uses `CHECK` for map creation, element insertion, and thread creation. Once setup succeeds, the main signal is all worker joins returning without process failure, followed by `PASS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/lpm_trie_map_get_next_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/map_in_map_batch_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/map_in_map_batch_ops.c

Purpose: verifies batch operations on map-in-map outer maps, covering `ARRAY_OF_MAPS` and `HASH_OF_MAPS` with inner array and hash maps. It validates that batch lookup and lookup-delete return map IDs that correspond to real inner maps and that array holes are handled correctly.

Important APIs/types/functions: `get_map_id_from_fd` reads `bpf_map_info.id`; `create_inner_maps` creates ten inner maps and stores each map's ID as its value; `create_outer_map` uses `bpf_map_create_opts.inner_map_fd`; `validate_fetch_results` reopens inner maps by ID and checks their contents; `fetch_and_validate` wraps `bpf_map_lookup_batch` and `bpf_map_lookup_and_delete_batch`; `_map_in_map_batch_ops` drives each map type combination.

Control flow: inner maps are created and initialized first. The outer map is created from the first inner map template, then populated with keys that differ for array and hash cases. The optional `has_holes` branch changes the final array key to leave key 1 absent. Batch lookup is run with batch sizes 5 and 10. For hash-of-maps, lookup-and-delete is also tested because array-of-maps cannot delete elements the same way.

State and persistence behavior: BPF map IDs outlive individual FDs while references remain in the outer map. Validation temporarily opens inner maps by ID and closes those FDs after lookup. The file carefully closes all original inner map FDs and the outer map FD at the end of each scenario.

Dependencies and integration points: depends on libbpf map create, info, update, batch, and map-id APIs plus `test_maps.h`. Exports `test_map_in_map_batch_ops_array` and `test_map_in_map_batch_ops_hash`.

Risks: the fetch loop retries on `ENOSPC` by increasing step size and resetting total, which handles hash batch short reads but can mask inefficient cursor behavior. Validation assumes each inner map has one key/value and that the value equals its map ID. It does not verify exact returned outer keys beyond total count and inner map identity.

Test signals: `CHECK` failures identify map creation, update, lookup, delete, open-by-ID, and inner value mismatch. PASS lines are emitted for each outer/inner combination including array holes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/map_in_map_batch_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/map_percpu_stats.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/map_percpu_stats.c

Purpose: exercises BPF map element accounting as observed through both userspace key iteration and a BPF iterator program, with emphasis on per-CPU maps, LRU maps, non-preallocated maps, hash-of-maps, batch deletion, and maximum per-CPU value sizing.

Important APIs/types/functions: `map_info`, `map_count_elements`, `delete_and_lookup_batch`, `delete_all_elements`, `patch_map_thread`, `upsert_elements`, `get_cur_elements`, and `check_expected_number_elements` are the core helpers. The file uses generated `map_percpu_stats.skel.h` to attach an iterator program `dump_bpf_map` and read the current element count from an iterator FD. Map creators cover hash, percpu hash, preallocated variants, common and no-common LRU, percpu LRU, and hash-of-maps.

Control flow: each map scenario calls `__test`. It obtains map metadata, reduces the update count to avoid expected capacity failures, spawns eight worker threads that upsert overlapping key ranges, compares real key iteration count to BPF iterator count, deletes all elements via element-by-element paths, rechecks zero, then repeats update/count/delete using batch lookup-and-delete. Hash-of-maps creates small inner maps as temporary values. The final value-size test attempts to create large per-CPU values and treats either success or `E2BIG` as acceptable depending on kernel support.

State and persistence behavior: maps are transient. For hash-of-maps each update creates a temporary inner map FD, updates the outer map, then closes the local FD while the outer map keeps its reference. Per-CPU maps use a shared static 8 KiB blob as value storage for all update threads. Iterator state is opened, read once, and destroyed for each count.

Dependencies and integration points: relies on libbpf map APIs, BPF iterator skeleton generation, pthreads, `map_update_retriable` from `bpf_util.h`, and `test_maps.h`. Exported entry is `test_map_percpu_stats`.

Risks: thread updates race on identical keys by design; the expected count is element presence, not value stability. For LRU maps the real count may be below inserted count because eviction is allowed. Non-preallocated per-CPU maps can temporarily return `ENOMEM`, so retry logic is used only for that class. The static value buffers assume enough size for up to 1024 CPUs.

Test signals: core signal is equality between userspace `get_next_key` counting and BPF iterator counting after updates and after deletions. Additional signals are successful mixed delete/lookup-delete paths, successful batch lookup-and-delete of all counted keys, map creation across variants, and accepted handling of oversized per-CPU value creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/map_percpu_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/sk_storage_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/sk_storage_map.c

Purpose: tests `BPF_MAP_TYPE_SK_STORAGE` creation, BTF requirements, locked updates/lookups, deletion semantics, invalid creation arguments, and two stress modes around socket lifetime and concurrent update/delete behavior.

Important APIs/types/functions: `load_btf` builds raw BTF for a value containing `bpf_spin_lock`; `create_sk_storage_map` creates the storage map with BTF type IDs and `BPF_F_NO_PREALLOC`. `test_sk_storage_map_basic` covers functional operations. `insert_close_thread` plus `do_sk_storage_map_stress_free` stress map destruction while many sockets with storage are closed. `update_thread`, `delete_thread`, and `do_sk_storage_map_stress_change` race updates and deletes on one socket. Environment-controlled entry is `test_sk_storage_map`.

Control flow: the basic test loads BTF, creates an IPv6 stream socket and storage map, performs `BPF_NOEXIST | BPF_F_LOCK`, `BPF_EXIST | BPF_F_LOCK`, `BPF_EXIST`, duplicate `BPF_NOEXIST` failure, plain update, lookup with `BPF_F_LOCK`, deletion, missing lookup/delete checks, then invalid map create variants. Stress-free creates worker threads that wait for a shared map FD, create many sockets, attach storage, signal completion, wait for the main thread to close the map, then close sockets and repeat until alarm/stop. Stress-change creates one socket and one map, then runs alternating updater/deleter threads until timeout or error.

State and persistence behavior: global variables track stop state, thread done/error counters, thread/socket counts, runtime, and the shared map FD. Signals set the stop flag. Socket storage is attached to socket FDs and should be released when sockets or maps are closed. BTF FDs are closed after map creation.

Dependencies and integration points: uses raw BTF encoding macros from `test_btf.h`, libbpf map/BTF APIs, pthreads, signals, sockets, resource limits, and `test_maps.h`. The exported `test_sk_storage_map` can select `basic`, `stress_free`, or `stress_change` by environment variables.

Risks: stress tests are timing-sensitive and depend on `RLIMIT_NOFILE`, system socket capacity, and scheduler behavior. `wait_for_map_close` spins without sleeping. Global stop/counter state is reused across subtests, so test order and environment overrides matter. Error acceptance for concurrent update includes `EAGAIN`; delete accepts `ENOENT`.

Test signals: functional checks expect exact locked lookup values, duplicate/missing errors, and `EINVAL` for bad BTF/key/max_entries/map_flags. Stress tests pass when all threads join without an unexpected error before the alarm-driven stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/sk_storage_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/netcnt_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/netcnt_common.h

Purpose: shared layout definitions for network counter selftests using BPF local storage and per-CPU values. It provides conservative value-size constants and unions that can be used as either typed counters or raw padding buffers.

Important APIs/types/functions: defines `MAX_PERCPU_PACKETS`, `SIZEOF_BPF_LOCAL_STORAGE_ELEM`, estimated `BPF_LOCAL_STORAGE_MAX_VALUE_SIZE`, and `PCPU_MIN_UNIT_SIZE`. `union percpu_net_cnt` contains packet/byte counters plus previous timestamp and previous packet/byte snapshots, padded to `PCPU_MIN_UNIT_SIZE`. `union net_cnt` contains packet/byte counters padded to the estimated maximum local storage value size.

Control flow: header only; no executable control flow.

State and persistence behavior: no runtime state is owned here. The unions define map value memory layout used by BPF programs/userspace tests elsewhere. Padding intentionally stresses allocator and maximum value size behavior.

Dependencies and integration points: includes `linux/types.h` and is included by net counter tests and BPF programs that need consistent value layout between kernel and userspace.

Risks: `BPF_LOCAL_STORAGE_MAX_VALUE_SIZE` is an estimate derived from assumed local storage element overhead. Architecture or kernel layout changes can make the estimate conservative or stale. Large padded unions can materially affect memory use in tests.

Test signals: indirect only; consumers can verify counter values, allocation behavior, and maximum value handling when using these layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/netcnt_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/netlink_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/netlink_helpers.c

Purpose: small route-netlink helper library, adapted from iproute2, for BPF selftests that need to build netlink requests, send them, receive acknowledgements or replies, and append rtattrs safely.

Important APIs/types/functions: `rtnl_open_byproto` and `rtnl_open` create netlink sockets and initialize `struct rtnl_handle`; `rtnl_close` closes them. `rtnl_recvmsg` peeks with `MSG_TRUNC`, allocates a large enough buffer, then receives. `__rtnl_talk_iov` sends one or more netlink messages, tracks sequence numbers, filters replies, handles `NLMSG_ERROR`, and optionally returns an answer buffer. Attribute helpers include `addattr`, typed `addattr8/16/32/64`, `addattrstrz`, `addattr_l`, `addraw_l`, `addattr_nest`, and `addattr_nest_end`.

Control flow: opening sets send/receive buffers, best-effort enables extended ACKs, binds to requested groups, validates sockaddr fields, and seeds sequence from `time(NULL)`. Talk sends messages, then loops receiving and scanning netlink headers until it finds matching pid/sequence acknowledgements or an answer. Attribute helpers append aligned payloads to the tail of an existing `nlmsghdr`.

State and persistence behavior: `struct rtnl_handle` owns the socket FD, protocol, local sockaddr, and increasing sequence. Receive buffers are heap allocated per response and handed to the caller only when an answer is requested. No persistent files are touched.

Dependencies and integration points: depends on Linux netlink/rtnetlink headers through `netlink_helpers.h`, standard sockets, and stderr/perror diagnostics. Used by tests that manipulate links, routes, qdiscs, or netdev state without shelling out.

Risks: some malformed netlink replies call `exit(1)`, which is acceptable for selftests but harsh for reusable library code. Extended ACK callback plumbing is declared but the default error printer ignores details. The returned answer buffer must be freed by callers. The `rtnl_talk` public wrapper always shows route errors except for sock diag suppression in the internal path.

Test signals: direct signals are negative errno returns or `-1` on open/send/malformed failures. Attribute helpers return `-1` if a message would exceed caller-provided bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/netlink_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/netlink_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/netlink_helpers.h

Purpose: public declarations and data structures for the netlink helper implementation.

Important APIs/types/functions: declares `struct rtnl_handle`, handle flags, `NLMSG_TAIL`, `nl_ext_ack_fn_t`, `rtnl_open`, `rtnl_close`, `rtnl_talk`, and all attribute append helpers. `rtnl_open` and `rtnl_talk` are marked `warn_unused_result` to push callers to check failures.

Control flow: header only; it shapes caller behavior through prototypes and macros.

State and persistence behavior: `struct rtnl_handle` stores socket FD, local/peer addresses, sequence/dump counters, protocol, optional dump file pointer, and flags. The header owns no state itself.

Dependencies and integration points: includes `linux/netlink.h` and `linux/rtnetlink.h`; consumed by BPF selftest code that needs rtnetlink request construction.

Risks: exposes low-level mutable fields, so callers can desynchronize sequence/protocol state if they modify the struct incorrectly. `NLMSG_TAIL` assumes `nlmsg_len` is valid and aligned enough for appending.

Test signals: indirect; callers check helper return values and resulting kernel netlink responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/netlink_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/network_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/network_helpers.c

Purpose: shared network helper implementation for BPF selftests. It provides socket server/client setup, namespace switching, TUN/TAP and ethtool helpers, data transfer helpers, TC attach helper, canned packet vectors, and optional libpcap-based traffic monitoring.

Important APIs/types/functions: socket helpers include `settimeo`, `start_server_addr`, `start_server_str`, `start_server`, `start_reuseport_server`, `client_socket`, `connect_to_addr`, `connect_to_addr_str`, `connect_to_fd_opts`, `connect_to_fd`, `connect_fd_to_fd`, and `fastopen_connect`. Namespace/helpers include `make_sockaddr`, `ping_command`, `append_tid`, `make_netns`, `remove_netns`, `open_netns`, `close_netns`, `open_tuntap`, `get_socket_local_port`, `get_hw_ring_size`, `set_hw_ring_size`, `send_recv_data`, and `tc_prog_attach`. Under `TRAFFIC_MONITOR`, `traffic_monitor_start`, `traffic_monitor_stop`, and packet pretty-printers capture and dump traffic.

Control flow: server creation makes a socket, applies timeouts and optional post-socket callbacks, binds, and listens for streams. Client helpers infer address/type/protocol and connect. Namespace helpers shell out for netns creation/deletion and use `setns` with an `nstoken` to restore the original namespace. `send_recv_data` starts a server thread that accepts and sends fixed byte counts while the client receives. `tc_prog_attach` creates a libbpf TC hook and attaches ingress and/or egress programs. Traffic monitor switches namespace if requested, configures a nonblocking immediate-mode pcap on `any`, starts a select loop on pcap and eventfd, dumps captured packets, and decodes IPv4/IPv6/TCP/UDP/ICMP summaries.

State and persistence behavior: global packet templates `pkt_v4` and `pkt_v6` are exported. Most helpers own only FDs returned to callers. `open_netns` allocates a token holding the original namespace FD until `close_netns`. Traffic monitor writes pcap files under `/tmp/tmon_pcap`, owns pcap/dumper/eventfd/thread state, and frees it on stop.

Dependencies and integration points: depends on sockets, netns mount paths, ioctl, fcntl, libbpf TC APIs, `test_progs.h` assertions, `bpf_util.h`, and optionally libpcap. Many prog tests in this subset use these helpers for loopback servers, netns setup, packet contexts, and TC attachment.

Risks: helpers mix assertion-based test failures and negative errno returns. Netns creation/removal shells out to `ip`, so tests depend on userspace tooling and privileges. `get_socket_local_port` returns network byte order port values. Traffic monitoring only parses Ethernet-compatible SLL2 captures and writes to `/tmp`, so permissions and cleanup matter. `start_server_addr` has a typo in one log string but not behavior.

Test signals: callers observe valid FDs, zero returns, `ASSERT_*` failures, or negative errnos. Traffic monitor provides diagnostic pcap/log output rather than primary pass/fail criteria.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/network_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/network_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/network_helpers.h

Purpose: public interface and inline checksum helpers for network-oriented BPF selftests.

Important APIs/types/functions: defines constants `MAGIC_VAL`, `NUM_ITER`, `VIP_NUM`, and `MAGIC_BYTES`; `struct network_helper_opts`; packed IPv4/IPv6 packet fixtures; prototypes for socket, namespace, TUN/TAP, ethtool, data transfer, TC attach, and traffic monitor helpers. Inline checksum routines are `csum_fold`, `csum_partial`, `build_ip_csum`, `csum_tcpudp_magic`, `csum_ipv6_magic`, `build_udp_v4_csum`, and `build_udp_v6_csum`.

Control flow: header-only inline logic computes simple Internet checksums by accumulating 16-bit words, adding pseudo-header fields, and folding to a `__sum16`. Traffic monitor APIs become no-op inline stubs when `TRAFFIC_MONITOR` is not enabled.

State and persistence behavior: declares exported packet globals and opaque `struct nstoken`/`struct tmonitor_ctx`. No owned state in the header.

Dependencies and integration points: includes Linux packet/IP/TUN/ethtool headers, TCP/UDP headers, libbpf endian helpers, and `net/if.h`. Used broadly by BPF selftests that need stable socket helpers and packet fixtures.

Risks: checksum helpers assume even-length handling suitable for the constructed tests and do not perform full generic checksum validation. `append_tid` reserves a fixed seven-digit field, so very large TIDs or small buffers fail. Stubbed traffic monitor functions silently do nothing when not compiled in.

Test signals: indirect; consumers use helpers to build valid packets, attach TC programs, or orchestrate network namespaces. Compile-time interface mismatches would surface across many selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/network_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_atomics.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_atomics.c

Purpose: validates atomic operations on BPF arena memory, including arithmetic/bitwise atomics, compare-and-exchange, exchange, use-after-free recovery, and optional load-acquire/store-release semantics.

Important APIs/types/functions: uses generated `arena_atomics.skel.h`. Per-operation helpers (`test_add`, `test_sub`, `test_and`, `test_or`, `test_xor`, `test_cmpxchg`, `test_xchg`, `test_uaf`, `test_load_acquire`, `test_store_release`) run individual BPF programs with `bpf_prog_test_run_opts` and inspect `skel->arena`, `skel->data`, and `skel->bss`.

Control flow: `test_arena_atomics` opens the skeleton, skips all tests if the BPF object reports missing compiler/JIT support, loads it, stores the current PID, and dispatches named subtests. Each subtest runs one program directly and asserts exact arena values/results.

State and persistence behavior: arena memory is mapped through the skeleton and mutated by BPF programs, then inspected from userspace. State is per skeleton instance and destroyed at cleanup. Optional support flags in `.data` drive skip behavior.

Dependencies and integration points: relies on libbpf skeleton generation, arena map support, BPF atomics compiler support, `test_progs.h` assertions, and `bpf_prog_test_run_opts`.

Risks: load-acquire/store-release tests are capability-gated and skip if toolchain or JIT lacks support, so they may not exercise on every environment. Return-value and arena-value assertions assume the paired BPF source keeps field names/semantics stable.

Test signals: exact `ASSERT_EQ` checks for every expected arena field, plus skip annotations for unsupported atomics or memory-order operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_atomics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_htab.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_htab.c

Purpose: tests hash table data structures allocated in BPF arena memory, for both compiler-generated and hand-written assembly variants.

Important APIs/types/functions: generated skeletons `arena_htab.skel.h` and `arena_htab_asm.skel.h` expose BPF programs. Shared validation `test_arena_htab_common` checks `struct htab` from `bpf_arena_htab.h`, verifies buckets exist, and calls `htab_lookup_elem` on keys 0, 4, 8, and 12 expecting key-value equality.

Control flow: LLVM path opens/loads skeleton, faults in arena page zero via `bpf_map__initial_value`, runs `arena_htab_llvm`, handles compiler support skip, then validates the user-visible arena hash table pointer. ASM path opens/loads, runs `arena_htab_asm`, and validates the same structure.

State and persistence behavior: arena pages contain the hash table buckets and nodes created by BPF. Userspace reads arena pointers and traverses bucket lists after the BPF program returns. State disappears with skeleton destruction.

Dependencies and integration points: depends on arena map support, generated skeletons, `bpf_arena_htab.h`, mmap-visible arena initial value access, and `test_progs.h`.

Risks: direct userspace traversal of arena pointers assumes pointer relocation and arena mapping are correct. LLVM variant can skip on missing `arena_cast` support, reducing coverage on older toolchains.

Test signals: successful BPF test run, non-null buckets, and matching lookup values. Two subtests isolate LLVM and ASM paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_htab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_list.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_list.c

Purpose: validates linked-list allocation and traversal in BPF arena memory, including sleepable and nonsleepable program modes and small/large list sizes.

Important APIs/types/functions: local `struct elem` embeds `arena_list_node`; `list_sum` walks an `arena_list_head` with `list_for_each_entry`. `test_arena_list_add_del` loads `arena_list.skel.h`, sets the `nonsleepable` rodata flag, runs add and delete programs, and checks BPF/user sums.

Control flow: for counts 1 and 1000, in both sleepable and nonsleepable modes, the test loads the skeleton, sets `cnt`, runs `arena_list_add`, verifies userspace traversal sum and arena counters, runs `arena_list_del`, then verifies the list is empty while stored sums remain expected.

State and persistence behavior: list nodes and summary fields live in arena memory and BSS fields. Userspace reads the arena list head pointer and list nodes after BPF mutation. State is destroyed with the skeleton.

Dependencies and integration points: depends on `bpf_arena_list.h`, arena skeleton support, and `test_progs.h`.

Risks: skips if compiler lacks `arena_cast`. The 1000 element case stresses allocation and traversal but still assumes enough arena resources. Direct pointer traversal depends on arena pointer validity in userspace.

Test signals: expected arithmetic sum `cnt * (cnt - 1) / 2`, `arena_sum`, `test_val`, zero post-delete userspace sum, and BPF-computed `list_sum` equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_spin_lock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_spin_lock.c

Purpose: concurrency stress test for BPF arena spin locks under multiple userspace threads running the same BPF program on distinct CPUs.

Important APIs/types/functions: defines local qspinlock-compatible structs before including `arena_spin_lock.skel.h`. `spin_lock_thread` sets CPU affinity, synchronizes with a pthread barrier, and runs the BPF program repeatedly with `pkt_v4` as input. `test_arena_spin_lock_size` configures critical-section count/limit and verifies the final counter.

Control flow: each subtest chooses a lock-protected work size, opens/loads the skeleton, initializes a barrier for up to 16 threads or available CPUs, starts threads with increasing CPU affinity, joins them, handles skip flags, and asserts that the BPF counter equals `repeat * nthreads`. The top-level test runs sizes 1, 1000, and 50000 with adjusted repeat counts.

State and persistence behavior: global userspace `cpu`, `repeat`, and `barrier` coordinate threads. Skeleton BSS stores `cs_count`, `limit`, and final `counter`. Arena lock state is internal to the BPF program and reset per skeleton.

Dependencies and integration points: uses pthread barriers/affinity, `get_nprocs`, `network_helpers.h` packet fixture `pkt_v4`, and generated skeleton support.

Risks: requires at least two CPUs for useful coverage and may skip for unsupported kernel CPU count or arena spinlock support. CPU affinity can fail under restricted environments. Large critical-section size stresses timing.

Test signals: successful thread creation/join, test-run return values of zero or explicit unsupported skip, and final counter equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_spin_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_strsearch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_strsearch.c

Purpose: narrow skeleton test for string-search logic implemented against BPF arena memory.

Important APIs/types/functions: `test_arena_str` opens/loads `arena_strsearch.skel.h`, runs the `arena_strsearch` program through `bpf_prog_test_run_opts`, and checks run and program return status.

Control flow: top-level `test_arena_strsearch` starts one subtest. The helper loads the skeleton, runs the BPF program, marks skip if the BPF side set `bss->skip`, then destroys the skeleton.

State and persistence behavior: any tested strings and results are owned inside the skeleton's BPF maps/BSS/arena. Userspace only observes the skip flag and run status in this file.

Dependencies and integration points: generated skeleton, arena support, compiler `arena_cast` support, and `test_progs.h`.

Risks: userspace does not inspect concrete match results, so most semantic checking must happen inside the paired BPF program by returning nonzero or setting skip.

Test signals: successful skeleton load, successful test run, zero BPF retval, or explicit skip on missing compiler support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_strsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arg_parsing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arg_parsing.c

Purpose: unit tests for selftest command-line/filter parsing helpers, covering test lists, subtest filters, wildcard wrapping, duplicate coalescing, comments, whitespace, and files without final newlines.

Important APIs/types/functions: local `init_test_filter_set` and `free_test_filter_set` manage `struct test_filter_set`. `test_parse_test_list` calls `parse_test_list`; `test_parse_test_list_file` writes a temporary file and calls `parse_test_list_file`.

Control flow: list parsing tests build filter strings such as `arg_parsing,bpf_cookie`, `test/subtest`, repeated calls into the same set, non-exact wildcard mode, and duplicate subtest aggregation. File parsing creates `/tmp/bpf_arg_parsing_test.XXXXXX`, writes comments/duplicates/inline comments/no-EOF-newline records, syncs the file, parses it, and validates the resulting ordered filter set.

State and persistence behavior: parsed filters allocate test names and subtest name arrays, then `free_test_filter_set` releases them. The temporary file is removed at the end. No persistent repository state is touched.

Dependencies and integration points: depends on `test_progs.h`, `testing_helpers.h`, libc temp-file APIs, and the shared test filter parser used by the selftest runner.

Risks: temporary file path is under `/tmp`; failures before cleanup can leave a file. Assertions use `strcmp` wrapped in `ASSERT_OK`, so equality is represented by zero.

Test signals: exact counts, names, subtest counts, duplicate suppression, wildcard formatting in non-exact mode, and parser success on trimmed/commented file input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arg_parsing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/assign_reuse.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/assign_reuse.c

Purpose: tests BPF socket assignment and reuseport selection interaction for TCP/UDP over IPv4 and IPv6 inside a dedicated network namespace.

Important APIs/types/functions: `attach_reuseport` applies `SO_ATTACH_REUSEPORT_EBPF`; `cookie` reads `SO_COOKIE`; `echo_test_udp` and `echo_test_tcp` perform one-byte echo flows; `run_assign_reuse` loads `test_assign_reuse.skel.h`, attaches TC ingress and reuseport programs, drives drop and accept cases, and checks BPF-observed socket cookie.

Control flow: top-level creates netns `assign_reuse`, brings loopback up, enters it, and runs four subtests. Each subtest starts one reuseport server, first attaches a drop reuseport program and a TC ingress program that redirects/assigns via a socket map, verifies connection or datagram failure and one reuseport execution, then switches to an accept reuseport program and verifies echo success plus cookie match.

State and persistence behavior: state includes a temporary netns, TC hook on loopback, one server socket FD, one socket-map entry, and skeleton BSS counters. Cleanup detaches TC, destroys hooks, destroys skeleton, frees sockets, restores namespace, and deletes the netns.

Dependencies and integration points: uses `network_helpers.h`, libbpf TC APIs, socket map updates, generated skeleton, `ip netns` commands through `SYS` macros, and CAP/network privileges.

Risks: depends on netns support, loopback index 1, TC hook creation permissions, and timing/errno differences between TCP `ECONNREFUSED` and UDP `EAGAIN`. Cleanup paths must run to avoid lingering netns or TC hooks.

Test signals: drop path expected errors, accept path zero echo result, BPF `reuseport_executed == 1`, and `sk_cookie_seen` equal to userspace `SO_COOKIE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/assign_reuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/async_stack_depth.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/async_stack_depth.c

Purpose: minimal wrapper that runs all subtests embedded in the `async_stack_depth` skeleton/BPF object.

Important APIs/types/functions: includes `async_stack_depth.skel.h` and calls `RUN_TESTS(async_stack_depth)` from `test_progs.h`.

Control flow: the macro handles skeleton open/load/attach/run behavior according to the generated selftest conventions.

State and persistence behavior: no local state; all state belongs to the skeleton and BPF programs.

Dependencies and integration points: generated skeleton and test harness macro support.

Risks: this file provides no additional userspace assertions, so meaningful coverage is entirely in the BPF-side test object and harness macro expansion.

Test signals: pass/fail/skip signals are produced by `RUN_TESTS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/async_stack_depth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/atomic_bounds.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/atomic_bounds.c

Purpose: load-time verifier regression test for atomic bounds behavior encoded in the `atomic_bounds` BPF object.

Important APIs/types/functions: includes `atomic_bounds.skel.h`; `test_atomic_bounds` calls `atomic_bounds__open_and_load` and destroys the skeleton.

Control flow: open/load must succeed; failure is reported by `CHECK`. No program is attached or run from userspace.

State and persistence behavior: no runtime state beyond the skeleton. The test is about verifier acceptance of the BPF program at load time.

Dependencies and integration points: generated skeleton and `test_progs.h`.

Risks: userspace cannot distinguish which specific verifier rule failed without skeleton/load logs. The unused `duration` variable is legacy test-harness residue.

Test signals: successful skeleton load is the pass condition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/atomic_bounds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/atomics.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/atomics.c

Purpose: validates classic BPF atomic operations outside arena memory using a light skeleton, covering add, sub, and/or/xor, compare-and-exchange, and exchange.

Important APIs/types/functions: uses `atomics.lskel.h`. Helpers `test_add`, `test_sub`, `test_and`, `test_or`, `test_xor`, `test_cmpxchg`, and `test_xchg` run individual programs directly by FD and inspect `data` and `bss` fields.

Control flow: `test_atomics` opens the light skeleton, sets `keyring_id`, loads it, skips if `.data->skip_tests` reports missing compiler support, sets PID, then dispatches subtests. Each subtest calls `bpf_prog_test_run_opts`, requires zero retval, and checks exact pre/post atomic result fields.

State and persistence behavior: `.data` holds mutable test variables for some atomics while `.bss` stores results and stack-copy observations. State is per skeleton instance and cleaned up at the end.

Dependencies and integration points: depends on BPF atomics compiler support, light skeleton generation, session keyring setting, and `test_progs.h`.

Risks: skipped on environments without `ENABLE_ATOMICS_TESTS` or Clang support. Field-level assertions are tightly coupled to the paired BPF program's global layout.

Test signals: exact value/result assertions for each atomic operation, plus explicit skip when atomics support is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/atomics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/attach_probe.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/attach_probe.c

Purpose: comprehensive userspace attach API test for kprobes, kretprobes, uprobes, uretprobes, auto-attach, sleepable probe restrictions, duplicate symbols, long event names, reference counters, library symbol uprobes, and kprobe context write restrictions.

Important APIs/types/functions: uses skeletons `test_attach_probe_manual`, `test_attach_probe`, `test_attach_kprobe_sleepable`, and `kprobe_write_ctx`. Local trigger functions provide uprobe targets; `uprobe_ref_ctr` emulates a USDT semaphore. Important helpers include `test_attach_probe_manual`, `test_attach_kprobe_by_addr`, `test_attach_kprobe_legacy_by_addr_reject`, `test_attach_probe_dup_sym`, long-name tests, `test_attach_probe_auto`, `test_uprobe_lib`, `test_uprobe_ref_ctr`, `test_kprobe_sleepable`, `test_uprobe_sleepable`, and x86-only kprobe write/freplace tests.

Control flow: top-level loads the auto-attach skeleton then runs named subtests. Manual mode attaches kprobe/kretprobe and uprobe/uretprobe in default/legacy/perf/link modes, triggers `usleep` and local functions, then checks BSS result counters. Address mode resolves `SYS_NANOSLEEP_KPROBE_NAME` from kallsyms and attaches by address for perf/link while rejecting legacy. Duplicate-symbol tests attach both unqualified vmlinux and module-qualified names. Auto and sleepable tests exercise `bpf_program__attach` behavior. Library/ref-counter tests attach by symbol or offset and validate trigger counters/ref counter cleanup.

State and persistence behavior: BPF links are stored in skeleton link slots or local pointers and destroyed with skeleton cleanup. BSS result fields accumulate trigger observations. The global `uprobe_ref_ctr` should return to zero after skeleton destruction. No persistent files are created.

Dependencies and integration points: depends on libbpf probe attach APIs, kallsyms helpers, `/proc/self/exe`, `libc.so.6` resolution, testmod symbols for duplicate/long-name cases, x86-specific behavior for context write tests, and `test_progs.h`.

Risks: kernel config, architecture, module availability, and symbol names affect coverage. Some subtests verify attach success without triggering when duplicate module symbols are only attach/detach checks. Reference counter cleanup is global and checked once at the end, so earlier failed cleanup can affect later subtests.

Test signals: exact BSS counters for kprobe/uprobe results, expected `-EOPNOTSUPP` or attach failure in negative cases, successful link creation/destruction, and final `uprobe_ref_ctr == 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/attach_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/autoattach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/autoattach.c

Purpose: verifies per-program skeleton auto-attach control.

Important APIs/types/functions: uses `test_autoattach.skel.h`; calls `bpf_program__set_autoattach`, `bpf_program__autoattach`, and `test_autoattach__attach`.

Control flow: open/load skeleton, disable autoattach for `prog2`, assert `prog1` remains autoattachable and `prog2` does not, attach the skeleton, trigger via `usleep`, and assert only `prog1_called` is set.

State and persistence behavior: skeleton BSS booleans record whether each BPF program ran. Link state is owned by the skeleton and cleaned up by destroy.

Dependencies and integration points: generated skeleton and libbpf autoattach APIs.

Risks: relies on the paired BPF object's attach points being triggered by `usleep`. The test intentionally mutates autoattach before attach; changing skeleton defaults can alter expectations.

Test signals: boolean autoattach flags before attach and BSS called flags after trigger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/autoattach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/autoload.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/autoload.c

Purpose: verifies that disabling autoload for a broken program allows the rest of a skeleton to load and attach successfully.

Important APIs/types/functions: uses `test_autoload.skel.h`, `test_autoload__open_and_load`, `test_autoload__open`, `bpf_program__set_autoload`, `test_autoload__load`, and `test_autoload__attach`.

Control flow: first confirms full open-and-load unexpectedly fails because `prog3` is broken. It then opens without loading, disables autoload for `prog3`, loads and attaches, triggers with `usleep`, and checks that `prog1` and `prog2` were called while `prog3` was not.

State and persistence behavior: BSS fields track program calls. Skeleton owns loaded programs and links until destroy.

Dependencies and integration points: generated skeleton and libbpf autoload controls.

Risks: the test's first phase expects load failure for the full skeleton; if the paired BPF program changes and `prog3` is no longer broken, the test fails by design.

Test signals: expected failure of full open/load, successful selective load/attach, and BSS called flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/autoload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bad_struct_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bad_struct_ops.c

Purpose: negative tests for struct_ops program loading and log diagnostics.

Important APIs/types/functions: uses `bad_struct_ops.skel.h`, `bad_struct_ops2.skel.h`, `start_libbpf_log_capture`, and `stop_libbpf_log_capture`. `invalid_prog_reuse` checks invalid reuse of a struct_ops program pointer; `unused_program` checks that an unreferenced struct_ops program still autoloads and fails load.

Control flow: each subtest opens a skeleton, starts libbpf log capture, attempts load expecting error, stops capture, and asserts a diagnostic substring is present. The unused-program test also asserts `foo` has autoload enabled before loading.

State and persistence behavior: only temporary skeletons and captured log buffers are allocated. Logs are freed and skeletons destroyed after each subtest.

Dependencies and integration points: libbpf logging capture helpers, generated skeletons, and a kernel/testmod environment that validates struct_ops.

Risks: substring assertions are sensitive to libbpf/kernel diagnostic wording. Missing log capture leaves limited context. These are intentionally negative load tests.

Test signals: failed skeleton load plus expected log substrings for invalid program reuse and failed unreferenced program load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bad_struct_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bind_perm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bind_perm.c

Purpose: tests cgroup bind hooks enforcing privileged-port bind permissions for IPv4 and IPv6.

Important APIs/types/functions: `create_netns` calls `unshare(CLONE_NEWNET)`. `try_bind` creates a TCP socket for AF_INET or AF_INET6 and checks bind errno for a requested port. `test_bind_perm` loads `bind_perm.skel.h`, attaches cgroup bind programs, disables `CAP_NET_BIND_SERVICE`, and validates expected bind outcomes.

Control flow: create new network namespace, join cgroup `/bind_perm`, load skeleton, attach v4 and v6 bind programs to the cgroup, drop effective net-bind-service capability, then try port 110 expecting `EACCES` and port 111 expecting success for both families. Restore capability if it was previously present.

State and persistence behavior: the process enters a new netns via `unshare`; cgroup FD remains open until cleanup. Capability state is saved and restored. Skeleton links attach to the cgroup and are destroyed at cleanup.

Dependencies and integration points: cgroup test helper, capability helper, generated skeleton, socket bind hooks, and namespace privileges.

Risks: failing to restore capability could affect later tests in the same process. `unshare(CLONE_NEWNET)` changes process namespace state. Port policy is encoded in the paired BPF program; userspace checks only expected errno.

Test signals: cgroup join and attach success, capability disable/restore success, and exact bind errno for blocked/allowed ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bind_perm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bloom_filter_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bloom_filter_map.c

Purpose: validates bloom filter map creation constraints, update/lookup behavior, BPF-side bloom checking, and use as an inner map.

Important APIs/types/functions: `test_fail_cases` creates invalid bloom filter maps and invalid update flag combinations. `test_success_cases` creates a valid bloom filter with `BPF_F_ZERO_SEED | BPF_F_NUMA_NODE`. `setup_progs` loads `bloom_filter_map.skel.h`, fills random-data and bloom maps. `test_inner_map` creates a bloom filter inner map and stores it in an outer map. `check_bloom` attaches the checker program and triggers via `SYS_getpgid`.

Control flow: run negative creation/update tests, run simple create/update/lookup success test, load skeleton and random values, fill both random-data and bloom maps, test bloom filter as inner map, delete the inner map reference, then attach the main checker and trigger it.

State and persistence behavior: random values are heap allocated and stored in BPF maps; bloom filter maps hold probabilistic membership state. Inner map FD is closed after outer map cleanup. Skeleton maps are destroyed at the end.

Dependencies and integration points: bloom filter map kernel support, generated skeleton, syscall trigger, libbpf map create/update/lookup/delete APIs, and NUMA flags.

Risks: bloom filters can have false positives; the paired BPF program should account for intended behavior. Negative tests rely on exact `-EINVAL` for invalid flags. Random values are generated with `rand()` but only used within the same run.

Test signals: invalid cases return failures or `-EINVAL`; success path update/lookup succeeds; BPF checker and inner-map checker leave `skel->bss->error == 0`; inner map delete succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bloom_filter_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_cookie.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_cookie.c

Purpose: broad coverage of BPF link/program cookies across kprobes, multi-kprobes, uprobes, multi-uprobes, tracepoints, perf events, trampoline links, LSM, BTF tracepoints, and raw tracepoints.

Important APIs/types/functions: uses `test_bpf_cookie.skel.h`, `kprobe_multi.skel.h`, and `uprobe_multi.skel.h`. Helpers attach with cookie-bearing option structs: `bpf_kprobe_opts`, `bpf_kprobe_multi_opts`, `bpf_uprobe_opts`, `bpf_uprobe_multi_opts`, `bpf_tracepoint_opts`, `bpf_perf_event_opts`, `bpf_link_create_opts`, `bpf_raw_tp_opts`, `bpf_trace_opts`, and `bpf_raw_tracepoint_opts`. `verify_tracing_link_info` and `verify_raw_tp_link_info` read cookie fields from `bpf_link_info`.

Control flow: top-level loads the cookie skeleton, stores current TID, then runs subtests. Single kprobe/uprobe tests attach duplicate probes with different cookies and assert ORed BSS results after trigger. Multi-kprobe tests use low-level link create by resolved addresses and high-level symbol attach APIs, then run a trigger program. Multi-uprobe attaches symbols in `/proc/self/exe` and triggers local functions. Tracepoint tests detach/reattach to ensure cookies survive prog-array reshuffling. Perf-event test reattaches on the same perf FD after disconnecting a link. Trampoline, LSM, tp_btf, and raw_tp tests create links with cookies, trigger, and verify BSS plus link info.

State and persistence behavior: BSS fields accumulate observed cookies. Link FDs/pointers own attachment lifetime and are explicitly destroyed/closed. Perf event FD is reused across link lifetimes. Some tests depend on testmod symbols and current process executable symbols.

Dependencies and integration points: depends on libbpf attach APIs, BPF link create, perf_event_open, kallsyms/testmod, `network_helpers.h` for `sys_gettid`, executable symbol availability, and `stack_mprotect` helper for LSM trigger.

Risks: high environmental sensitivity: testmod, tracepoint availability, perf permissions, LSM hook support, and CPU affinity for perf triggering. Cookie expectations are exact constants; link-info struct layout must match kernel support. Long CPU burn loops can be slow.

Test signals: BSS cookie fields equal expected bitwise OR or exact cookie values, link-info cookie fields match, expected `EPERM` from LSM-protected `stack_mprotect`, and successful attach/detach/reuse paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_cookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_gotox.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_gotox.c

Purpose: tests BPF indirect jump (`gotox`) and instruction-array jump-table support generated from C switch statements and manually constructed programs.

Important APIs/types/functions: skeleton `bpf_gotox.skel.h` provides programs for switch/jump-table variants. `check_simple` and `check_simple_fentry` run programs or trigger attached fentry paths and inspect `ret_user`. `check_one_map_two_jumps` inspects program map IDs for exactly one `BPF_MAP_TYPE_INSN_ARRAY`. Manual helpers `create_jt_map`, `prog_load`, `__check_ldimm64_off_prog_load`, `__check_ldimm64_gotox_prog_load`, `allow_offsets`, and `reject_offsets` verify verifier handling of instruction-array map-value offsets.

Control flow: top-level opens/loads skeleton, sets PID, and runs subtests if not skipped by BPF data. Switch tests feed input arrays and compare expected outputs. Other-section tests attach fentry-style programs and trigger with `usleep`. Offset tests create frozen instruction-array maps, load raw BPF programs with map-value references and indirect jumps, then allow or reject combinations based on alignment and bounds.

State and persistence behavior: skeleton BSS carries input/output for fentry-triggered cases. Instruction-array maps are populated with `struct bpf_insn_array_value.orig_off`, frozen, and consumed by program load; map FDs are closed after each check.

Dependencies and integration points: depends on kernel `BPF_MAP_TYPE_INSN_ARRAY`, verifier gotox support, libbpf skeletons, raw BPF instruction macros, and test harness assertions.

Risks: skips when the BPF object reports unsupported gotox. Manual tests assume verifier returns `-EACCES` for invalid offsets. Generated switch behavior is tightly coupled to paired BPF C output and compiler code generation.

Test signals: exact return mapping for switch inputs, exactly one instruction-array map for shared jump table, accepted aligned in-bounds offsets, rejected unaligned/out-of-bounds/negative-first offsets, and successful LLVM nonzero-offset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_gotox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_insn_array.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_insn_array.c

Purpose: validates `BPF_MAP_TYPE_INSN_ARRAY` program-load integration: original-to-translated instruction offsets, verifier rejection cases, required freezing, single-program ownership, JIT hardening/blinding effects, and disallowed BPF-side lookup.

Important APIs/types/functions: `map_create` creates instruction-array maps; `prog_load` passes an FD array through `bpf_prog_load_opts`; `__check_success` populates `orig_off`, freezes the map, loads a program, then validates `xlated_off`. Subtests cover one-to-one mapping, helper-call expansion, NOP/dead-code deletion, function bodies, out-of-bounds/mid-instruction indices, JIT hardening via `/proc/sys/net/core/bpf_jit_harden`, unfrozen maps, no map reuse, and BPF-side lookup rejection.

Control flow: on supported architectures, `test_bpf_insn_array` runs named subtests. Success cases populate maps and compare translated offsets after verifier/JIT transformations. Negative cases intentionally set bad `orig_off`, omit freeze, reuse a map for a second program, or call `bpf_map_lookup_elem` on an instruction-array map and assert expected load errors. The blinding test temporarily sets JIT hardening to level 2 and restores the old value.

State and persistence behavior: instruction-array maps store `orig_off` before program load and kernel-filled `xlated_off` after load. A map becomes associated with one loaded program and cannot be reused. The JIT hardening sysctl is process-external state and is restored in cleanup if changed.

Dependencies and integration points: gated to x86_64, powerpc, or aarch64. Uses raw BPF instruction macros, libbpf program load options with `fd_array`, map freeze, map update/lookup, and sysctl file access.

Risks: changing `/proc/sys/net/core/bpf_jit_harden` requires permission and affects global kernel behavior briefly. Expected translated offsets are architecture/kernel-codegen sensitive, hence the architecture guard. Cleanup must restore sysctl even on failure.

Test signals: exact `xlated_off` arrays for success cases, `-EINVAL` for incorrect indices/unfrozen map/BPF-side lookup, `-EBUSY` for map reuse, successful normal array-map lookup program as a control, and skip on unsupported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_insn_array.c -->
