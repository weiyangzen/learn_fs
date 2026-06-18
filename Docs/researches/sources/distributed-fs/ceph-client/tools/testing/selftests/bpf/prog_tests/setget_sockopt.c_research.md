# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/setget_sockopt.c

## Purpose
Tests BPF cgroup socket hooks that get/set socket options across TCP, UDP, kTLS, and nonstandard option paths. The source was read as a complete 246-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `create_netns()`, `test_tcp()`, `test_udp()`, `test_ktls()`, `test_nonstandard_opt()`, `test_setget_sockopt()`.
- Includes and fixtures: `#include <sched.h>`, `#include <linux/socket.h>`, `#include <linux/tls.h>`, `#include <net/if.h>`, `#include "test_progs.h"`, `#include "cgroup_helpers.h"`, `#include "network_helpers.h"`, `#include "setget_sockopt.skel.h"`.
- Generated skeletons/objects referenced: `bpf_link`, `bpf_program`, `setget_sockopt`.
- Primary APIs and types: `setget_sockopt__open/load/attach()`, cgroup helpers, `start_server()`, `connect_to_fd_server()`, `connect_to_fd()`, `accept()`, `setsockopt()/getsockopt()`, TLS socket options, netns/veth helpers, and skeleton BSS counters.

## Control Flow
`test_setget_sockopt()` creates a netns/cgroup environment, attaches cgroup programs, then runs TCP, UDP, kTLS, and nonstandard option subtests. Each creates sockets, triggers cgroup hooks, and validates BPF counters and socket option effects.

## State and Persistence Behavior
State includes cgroup attachments/links, netns/veth setup, server/client sockets, TLS state, and skeleton BSS counters for listen/connect/active/passive/post_create/bind hooks. Cleanup detaches links and tears down namespace/cgroup state.

## Dependencies and Integration Points
Depends on `setget_sockopt.skel.h`, cgroup v2 helpers, network helpers, kTLS support for TLS subtest, and socket hook program types.

## Risks and Edge Cases
kTLS and cgroup permissions may be unavailable; socket option semantics differ by protocol; leaked cgroup links can affect later tests.

## Test Signals
Assertions check veth setup, server/client connections, hook counters, TLS setsockopt/read behavior, and nonstandard option handling. Named assertion/check labels observed in the source include: `bring veth up`, `start_server`, `connect_to_fd_server`, `nr_listen`, `nr_connect`, `nr_active`, `nr_passive`, `nr_socket_post_create`, `nr_bind`, `connect_to_fd`, `accept`, `tls`.
