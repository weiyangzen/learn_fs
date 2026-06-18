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
