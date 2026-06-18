# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_helpers.h

Purpose: `tc_helpers.h` provides small inline helpers shared by TCX and netkit BPF selftests. It centralizes program-count queries, TCX link ifindex extraction, and skeleton BSS reset logic for generated `test_tc_link` skeletons.

Important APIs/types/functions: `ifindex_from_link_fd()` calls `bpf_link_get_info_by_fd()` and returns `link_info.tcx.ifindex`, using `ASSERT_OK` to report failures. `__assert_mprog_count()` wraps `bpf_prog_query()` for a target attach type and asserts both the returned count and zero errno. `assert_mprog_count()` applies that query to the default `loopback` ifindex. `assert_mprog_count_ifindex()` makes the ifindex explicit for veth/netkit tests. `tc_skel_reset_all_seen()` zeroes the skeleton BSS so packet-seen flags start fresh.

Control flow: callers use the count helpers before attachment, after attachment/replacement, and after cleanup to prove kernel multi-program state matches the expected number of attached programs. `ifindex_from_link_fd()` is used after device deletion to verify a link's TCX ifindex becomes 0. `tc_skel_reset_all_seen()` is typically called before injecting ping/ICMP traffic so subsequent BSS flags prove the current packet traversal rather than a previous packet.

State and persistence: the header does not own persistent state. It reads kernel link/query state and writes only to a skeleton's BSS memory. The `loopback` default is a macro with fallback value 1, so state is coupled to a conventional loopback ifindex unless a source file defines `loopback` first.

Dependencies: depends on `test_progs.h`, libbpf BPF link/query APIs, `struct bpf_link_info` with TCX fields, and generated `struct test_tc_link` definitions in translation units that include the header.

Integration points: included by `tc_links.c`, `tc_opts.c`, `tc_netkit.c`, and similar TCX selftests. It creates a shared assertion vocabulary for program counts and seen-flag resets across link-based and fd-based attach tests.

Risks: the header assumes `struct test_tc_link` is visible when `tc_skel_reset_all_seen()` is compiled. It also assumes that querying with `prog_ids == NULL` and `count` pointer is sufficient for every tested attach type. The fallback `loopback 1` can hide portability issues on unusual test environments where loopback ifindex differs.

Test signals: this header's behavior is indirectly tested whenever the including selftests assert program counts before and after attach/detach and when BSS flags are reset before packet injection. A broken helper would cause widespread count or stale-BSS assertion failures.
