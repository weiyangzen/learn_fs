# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/user_ringbuf.c

## Purpose

Host-side selftest coverage for libbpf user ring buffer maps. It validates mmap protections, malformed producer records, reserve/submit/discard behavior, wraparound/overfill handling, blocking reserve wakeups, and a bidirectional message protocol between a userspace producer and BPF programs in `user_ringbuf_success`/`user_ringbuf_fail`. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`user_ring_buffer__new()`, `user_ring_buffer__reserve()`, `user_ring_buffer__reserve_blocking()`, `user_ring_buffer__submit()`, `user_ring_buffer__discard()`, `ring_buffer__new()`, `ring_buffer__consume()`, `bpf_map__set_max_entries()`, `mmap()`, `mprotect()`, `mremap()`, `pthread_create()`, and syscall triggers such as `getpgid`, `prctl`, and `prlimit64`. Key helpers are `write_samples()`, `open_load_ringbuf_skel()`, `load_skel_create_ringbufs()`, `manually_write_test_invalid_sample()`, `send_test_message()`, and `handle_kernel_msg()`.

## Control Flow

`test_user_ringbuf()` sets page-sized ring buffers, runs the success subtest table, then runs failure skeleton tests. Each success test loads a skeleton, scopes the BPF program to the current PID, attaches it, writes or corrupts ring data, triggers kernel consumption through syscalls, and asserts BSS counters/errors. The protocol test alternates user-to-kernel messages and kernel-to-user ring buffer consumption; the blocking test fills the ring, proves timeout behavior, then wakes a blocking reserve from another thread.

## State and Persistence Behavior

State is transient: libbpf ring buffer mappings, kernel/user ring buffer maps, skeleton BSS counters (`read`, `err`, `kern_mutated`, `user_mutated`), and a temporary pthread. There is no file persistence; mmaped producer/data pages are explicitly unmapped and skeleton/ring buffers are destroyed per subtest.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

The tests depend on page size, exact ring buffer header alignment, kernel memory-ordering semantics for producer position, and errno behavior for malformed samples. Missed cleanup can leave mappings or threads alive; log noise is intentionally minimized by asserting mostly on error paths.

## Test Signals

Expected signals include successful subtest table execution, `RUN_TESTS(user_ringbuf_fail)` verifier/load failures, exact BSS read/error counts, `-EINVAL`/`-E2BIG` for malformed records, no reads for discarded samples, and blocking reserve timeout-then-success behavior.
