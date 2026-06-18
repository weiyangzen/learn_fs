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
