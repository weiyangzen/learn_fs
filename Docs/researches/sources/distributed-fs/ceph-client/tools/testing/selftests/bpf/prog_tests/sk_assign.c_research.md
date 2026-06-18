# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_assign.c

## Purpose
Integration test for `bpf_sk_assign()` in TC ingress, proving traffic can be redirected to a selected socket even when destination port/address differs. The source was read as a complete 300-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `configure_stack()`, `rcv_msg()`, `run_test()`, `prepare_addr()`, `test_sk_assign()`.
- Includes and fixtures: `#include <fcntl.h>`, `#include <signal.h>`, `#include <stdlib.h>`, `#include <unistd.h>`, `#include "test_progs.h"`, `#include "network_helpers.h"`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `tc` command invocation, `ip` route/link commands, `unshare(CLONE_NEWNET)`, `setns()`, `bpf_obj_get()` for `/sys/fs/bpf/tc/globals/server_map`, `bpf_map_update_elem()`, `start_server_addr()`, `connect_to_addr()`, socket read/write helpers, and IPv4/IPv6 address preparation.

## Control Flow
`test_sk_assign()` saves the original netns, configures a new netns and TC clsact program, opens the pinned server map, then runs eight TCP/UDP IPv4/IPv6 port/address rewrite subtests. Each starts a server on `BIND_PORT`, updates the BPF map with its fd, connects to `CONNECT_PORT` or rewritten address, sends data, and checks the receiving socket port.

## State and Persistence Behavior
Persistent during the test: a new netns, loopback routes, TC qdisc/filter, pinned TC globals map, and server socket fd stored in `server_map`. Cleanup unlinks the map path and returns to the original netns.

## Dependencies and Integration Points
Depends on external `tc` and `ip`, tc built with or without libbpf selecting different object files, CAP_NET_ADMIN, bpffs TC globals path, and network helpers.

## Risks and Edge Cases
External command availability/version matters; cleanup after netns/TC failure is delicate; fixed test ports can conflict inside namespace only if setup leaks.

## Test Signals
Subtests pass when data arrives and accepted TCP sockets report `CONNECT_PORT` while UDP server remains on `BIND_PORT`; setup failures print command-specific diagnostics. Named assertion/check labels observed in the source include: `%d\n`.
