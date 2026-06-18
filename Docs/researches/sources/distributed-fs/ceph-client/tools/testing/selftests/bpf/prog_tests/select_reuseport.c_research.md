# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/select_reuseport.c

## Purpose
Large networking integration test for `BPF_PROG_TYPE_SK_REUSEPORT` selection across reuseport sockarray, sockmap, and sockhash inner maps, TCP/UDP, IPv4/IPv6, loopback/inany binds, syncookies, pass-on-error, and detach behavior. The source was read as a complete 861-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `create_maps()`, `prepare_bpf_obj()`, `ss_init_loopback()`, `ss_init_inany()`, `read_int_sysctl()`, `write_int_sysctl()`, `enable_fastopen()`, `enable_syncookie()`, `disable_syncookie()`, `get_linum()`, `check_data()`, `check_results()`, `send_data()`, `do_test()`, `test_err_inner_map()`, `test_err_skb_data()`, `test_err_sk_select_port()`, `test_pass()`, `test_syncookie()`, `test_pass_on_err()`, `test_detach_bpf()`, `prepare_sk_fds()`, `setup_per_test()`, `cleanup_per_test()`, and 5 more.
- Includes and fixtures: `#include <stdlib.h>`, `#include <unistd.h>`, `#include <stdbool.h>`, `#include <string.h>`, `#include <errno.h>`, `#include <assert.h>`, `#include <fcntl.h>`, `#include <linux/bpf.h>`, `#include <linux/err.h>`, `#include <linux/types.h>`, and 10 more.
- Generated skeletons/objects referenced: `bpf_object`.
- Primary APIs and types: `bpf_map_create()`, `BPF_MAP_TYPE_ARRAY_OF_MAPS`, `bpf_map__reuse_fd()`, `bpf_object__open/load()`, `SO_REUSEPORT`, `SO_ATTACH_REUSEPORT_EBPF`, `SO_DETACH_REUSEPORT_BPF`, `epoll`, `sendto(MSG_FASTOPEN)`, socket syscalls, netns helpers, and sysctl read/write for fastopen/syncookies.

## Control Flow
`serial_test_select_reuseport()` runs the full matrix for three map types. Each map type creates inner/outer maps, loads `test_select_reuseport_kern.bpf.o`, then for each socket/family/bind config creates a fresh netns, enables fastopen, disables syncookies, sets up 32 reuseport sockets, installs the inner map, runs error/pass/syncookie/detach subtests, checks result/data maps, and cleans sockets/maps.

## State and Persistence Behavior
Global fds hold maps, BPF object, socket array, epoll fd, server sockaddr, and expected result counters. It temporarily mutates TCP sysctls inside the test netns and BPF maps (`result_map`, `tmp_index_ovr_map`, `linum_map`, `data_check_map`). Cleanup closes fds and removes outer-map entries.

## Dependencies and Integration Points
Depends on network namespace creation, TCP fastopen/syncookie sysctls, BPF reuseport program support, map-in-map, sockmap/sockhash support, and the compiled kernel BPF object plus common header.

## Risks and Edge Cases
Complex environmental sensitivity: netns permissions, sysctl availability, TCP fastopen behavior, syncookie timing, socket ordering, and optional detach socket option. Global state makes serial execution necessary.

## Test Signals
Signals include result-map counters per enum result, data_check map fields for skb protocol/addresses/ports/hash, epoll selected socket index, received command payload, syncookie tmp-index reset, and no BPF runs after detach. Named assertion/check labels observed in the source include: `netns_new`.
