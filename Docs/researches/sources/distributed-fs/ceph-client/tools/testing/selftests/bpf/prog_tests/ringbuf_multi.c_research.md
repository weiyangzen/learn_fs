# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ringbuf_multi.c

## Purpose
Tests libbpf multi-ring manager behavior, ring indexes, dynamic resize/reset, and polling across multiple BPF ring buffers. The source was read as a complete 148-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `process_sample()`, `test_ringbuf_multi()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <sys/epoll.h>`, `#include "test_ringbuf_multi.skel.h"`.
- Generated skeletons/objects referenced: `test_ringbuf_multi`.
- Primary APIs and types: `test_ringbuf_multi__open/load/attach()`, `ring_buffer__new()`, `ring_buffer__add()`, `ring_buffer__ring()`, `ring_buffer__poll()`, `ring__map_fd()`, resize/reset helpers, and `epoll` integration.

## Control Flow
The test adjusts ring sizes before load, verifies resize/reset behavior, loads/attaches the skeleton, creates a multi-ring buffer manager, triggers samples into multiple rings, checks ring index/map fd lookup, and validates polling again returns expected callback results.

## State and Persistence Behavior
BPF maps for two ring buffers persist during skeleton lifetime. User-space callback state records which samples arrived. Resize/reset changes map max_entries before load.

## Dependencies and Integration Points
Depends on `test_ringbuf_multi.skel.h`, libbpf multi-ring APIs, epoll, and ringbuf map resize support.

## Risks and Edge Cases
Resize after load should fail; ring index ordering matters; epoll readiness can be timing-sensitive.

## Test Signals
Assertions check size before/after resize/reset, rejected resize after load, ring index lookup, and expected repeated polling behavior. Named assertion/check labels observed in the source include: `exp %d, got %d\n`, `exp %ld, got %ld\n`, `unexpected sample seq %d, val %ld\n`, `skeleton open failed\n`, `rb1_size_before`, `rb1_resize`, `rb1_size_after`, `rb1_reset`, `rb1_size_final`, `bpf_map_create failed\n`, `bpf_map__set_inner_map_fd failed\n`, `skeleton load failed\n`.
