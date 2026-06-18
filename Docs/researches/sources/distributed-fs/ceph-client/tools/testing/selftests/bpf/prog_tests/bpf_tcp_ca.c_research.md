# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_tcp_ca.c

## Purpose
This selftest validates BPF TCP congestion-control struct_ops programs, including DCTCP and Cubic behavior, socket-local storage interaction, autoattach, license and helper restrictions, fallback behavior, link update semantics, unsupported operation rejection, and TCP CA kfunc loading.

## Important APIs, Types, And Functions
Important helpers include `settcpca()`, `start_test()`, `do_test()`, `cc_cb()`, `stg_post_socket_cb()`, `libbpf_debug_print()`, and test functions such as `test_cubic()`, `test_dctcp()`, `test_dctcp_autoattach_map()`, `test_invalid_license()`, `test_dctcp_fallback()`, `test_rel_setsockopt()`, `test_update_ca()`, `test_update_wrong()`, `test_mixed_links()`, `test_multi_links()`, `test_link_replace()`, `test_tcp_ca_kfunc()`, and `test_cc_cubic()`. It uses `setsockopt(TCP_CONGESTION)`, `getsockopt()`, `bpf_map__attach_struct_ops()`, `bpf_link__update_map()`, and `bpf_link_update()`.

## Control Flow
`test_bpf_tcp_ca()` dispatches subtests. Positive congestion-control tests load a skeleton, attach its struct_ops map, set sockets to the BPF CA name through network helper callbacks, send 10 MiB, and inspect BSS counters or socket-local storage values. Negative tests install libbpf print hooks to verify expected verifier/libbpf warnings, or attach incomplete/unsupported struct_ops and expect failure. Link update tests attach one CA map, run traffic, update or replace the backing map, then verify either new counters advanced or invalid updates failed.

## State And Persistence Behavior
State is transient in TCP sockets, struct_ops links, BPF maps, BSS counters, libbpf print callback globals `err_str` and `found`, and socket-local storage. The file does not pin objects. The fallback test checks recursive `setsockopt(TCP_CONGESTION)` behavior during CA init and reads the resulting server-side algorithm.

## Dependencies And Integration Points
It depends on IPv6 TCP loopback helpers, BPF struct_ops support for TCP congestion control, generated skeletons for several valid and invalid CA programs, socket-local storage maps, libbpf logging, and kernel support for link update/replace semantics.

## Risks And Edge Cases
Traffic volume and TCP state transitions make the test timing-sensitive. Exact warning substrings are part of negative checks. System congestion-control availability, permissions, and struct_ops feature support can gate execution. Link update tests rely on precise map compatibility checks.

## Test Signals
Passing signals include data transfer success, BPF Cubic ack callbacks, DCTCP socket-local storage result `0xeB9F`, expected GPL/helper/unsupported-op diagnostics, fallback to `cubic` with `-ENOTSUPP` and `EBUSY` counts, rejection of incomplete ops, successful and failed map updates as appropriate, successful `BPF_F_REPLACE` only with the correct old map FD, and successful TCP CA kfunc skeleton load.
