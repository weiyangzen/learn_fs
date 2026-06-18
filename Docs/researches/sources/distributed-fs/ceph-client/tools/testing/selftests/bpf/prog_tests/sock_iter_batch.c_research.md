<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_iter_batch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_iter_batch.c

Purpose: `sock_iter_batch.c` stress-tests batched BPF socket iterator resume behavior. It verifies that iterating socket hash buckets remains correct when sockets are removed, added, or force iterator batch reallocation while iteration is in progress for UDP, TCP listening sockets, and TCP established sockets.

Important APIs/types/functions: `struct iter_out` is the BPF iterator output record with bucket index and socket cookie. `struct sock_count` tracks unique cookies and occurrence counts. `read_n()` drains a requested number of iterator records. `get_nth_socket()`, `was_seen()`, and `check_n_were_seen_once()` correlate iterator cookies with userspace socket FDs. Mutation helpers include `remove_seen`, `remove_unseen`, `remove_all`, `add_some`, `force_realloc`, and established-socket variants. `do_resume_test()` runs table-driven mutation scenarios. `do_test()` verifies simple two-bucket batched reads.

Control flow: `test_sock_iter_batch()` creates netns `sock_iter_batch_netns`, enters it, runs TCP and UDP simple batch tests with one-by-one and bulk reads, then runs `do_resume_tests()`. Simple tests create two reuseport groups, load the iterator skeleton with target ports/family/state, attach the TCP or UDP iterator, partially read one bucket, close that bucket, then verify the second bucket is read fully. Resume tests create reuseport groups and optionally established TCP connections, attach an iterator, read part of the stream, mutate sockets according to the test case, then confirm remaining original sockets are seen exactly once or no extra sockets are returned.

State and persistence: state includes named parent and child netns, optional sysctl `net.ipv4.tcp_child_ehash_entries`, reuseport listener arrays, accepted/connected socket arrays, BPF iterator links/FDs, skeleton rodata filter fields, and in-memory cookie counts. Cleanup deletes netns, resets the sysctl to `0`, frees FD arrays, and destroys links/skeletons.

Dependencies: depends on BPF socket iterators, reuseport server helpers, socket cookies, TCP/UDP IPv4/IPv6 loopback, `poll()`/accept helpers, network namespace tools, and permission to set `net.ipv4.tcp_child_ehash_entries` for established-socket collision scenarios.

Integration points: exercises the kernel BPF iterator batch/resume implementation under concurrent socket table mutations, including direct BPF-side socket destruction through `iter_tcp_destroy`.

Risks: timing and hash bucket placement are central. The test intentionally forces buckets and collisions, but port hashing can still produce rare collisions handled by conditional assertions. The source snapshot shows duplicated parameter text in `remove_seen()` and duplicated `.sock_type` assignment in the test table; these are source-quality risks. Mutation helpers can leak `close_idx` allocation on early return in `remove_all_established`. Sysctl manipulation must be restored or later networking tests may be affected.

Test signals: no duplicate cookie sightings, expected counts of sockets seen exactly once after each mutation, iterator EOF when all sockets are removed, successful realloc stress cases, and successful TCP/UDP simple batch reads in both one-by-one and bulk modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_iter_batch.c -->
