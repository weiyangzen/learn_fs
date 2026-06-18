# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ringbuf.c

## Purpose
Comprehensive libbpf ring-buffer test covering mmap permissions, callback polling, per-ring inspection APIs, notification flags, consume_n batching, map-key use, write/discard behavior, and overwrite mode. The source was read as a complete 576-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `atomic_inc()`, `atomic_xchg()`, `process_sample()`, `trigger_samples()`, `ringbuf_write_subtest()`, `ringbuf_subtest()`, `process_n_sample()`, `ringbuf_n_subtest()`, `process_map_key_sample()`, `ringbuf_map_key_subtest()`, `ringbuf_overwrite_mode_subtest()`, `test_ringbuf()`.
- Includes and fixtures: `#include <linux/compiler.h>`, `#include <asm/barrier.h>`, `#include <test_progs.h>`, `#include <sys/mman.h>`, `#include <sys/epoll.h>`, `#include <time.h>`, `#include <sched.h>`, `#include <signal.h>`, `#include <pthread.h>`, `#include <sys/sysinfo.h>`, and 7 more.
- Generated skeletons/objects referenced: `test_ringbuf`, `test_ringbuf_lskel`, `test_ringbuf_map_key`, `test_ringbuf_map_key_lskel`, `test_ringbuf_n`, `test_ringbuf_n_lskel`, `test_ringbuf_overwrite`, `test_ringbuf_overwrite_lskel`, `test_ringbuf_write`, `test_ringbuf_write_lskel`.
- Primary APIs and types: `test_ringbuf*.lskel.h`, `ring_buffer__new/poll/consume/consume_n/ring`, `ring__map_fd/avail_data_size/size/consumer_pos/producer_pos/consume`, `mmap()`, `mprotect()`, `mremap()`, `pthread_create/tryjoin`, `BPF_RB_NO_WAKEUP`, `BPF_RB_FORCE_WAKEUP`, and ring-buffer header constants.

## Control Flow
`test_ringbuf()` runs five subtests. The main subtest validates mmap protections, triggers samples via `getpgid`, checks ring positions, polls until `-EDONE`, verifies adaptive/no/force wakeups with a background poll thread, and consumes pending samples. Additional subtests cover `consume_n`, map-key samples, user writes/discards, and overwrite accounting.

## State and Persistence Behavior
Global `sample_cnt`, `ringbuf`, and skeleton pointers coordinate callbacks. BPF BSS fields track pid, value, flags, dropped/total/discarded, positions, and overwrite counters. All ring buffers and skeletons are freed/detached.

## Dependencies and Integration Points
Depends on generated light skeletons, ring-buffer mmap ABI, pthreads, syscalls used as triggers, and libbpf ring APIs.

## Risks and Edge Cases
Mmap permission expectations are kernel ABI sensitive; wakeup tests have timing sleeps and background threads; global ringbuf state requires serial-like isolation.

## Test Signals
Assertions check mmap success/failure and errno, ring position/size values, callback sample values, poll return `-EDONE`, sample counts, wakeup blocking/unblocking, consume_n counts, map lookup by sample key, write/discard counters, and overwrite positions. Named assertion/check labels observed in the source include: `exp %ld, got %ld\n`, `skel_open`, `skel_load`, `unmap_rw`, `ringbuf_new`, `skel_attach`, `discarded`, `passed`, `skeleton open failed\n`, `skeleton load failed\n`, `rw_cons_pos`, `exec_cons_pos_protect`.
