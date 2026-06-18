<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_load_bytes.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_load_bytes.c

Purpose: `skb_load_bytes.c` verifies `bpf_skb_load_bytes()` behavior for invalid and valid offsets in a SCHED_CLS-style test-run. It checks that an all-ones offset fails with `-EFAULT` while a normal offset succeeds.

Important APIs/types/functions: `test_skb_load_bytes()` opens and loads `skb_load_bytes.skel.h`, obtains the `skb_process` program FD, sets BSS field `load_offset`, runs `bpf_prog_test_run_opts()`, and reads BSS `test_result`. It uses `pkt_v4` and an empty `struct __sk_buff`.

Control flow: after skeleton load, the test sets `load_offset` to `(uint32_t)-1`, runs the program, and expects `test_result == -EFAULT`. It then sets offset `10`, reruns, and expects `test_result == 0`. Cleanup destroys the skeleton.

State and persistence: state is in skeleton BSS fields and the local test-run context. There is no persistent external state.

Dependencies: depends on the `skb_load_bytes` BPF skeleton, SCHED_CLS test-run support, `bpf_skb_load_bytes()` helper behavior, and the IPv4 packet fixture.

Integration points: links userspace test-run setup to BPF-side helper return codes for packet byte access.

Risks: expected errno is exact; helper or verifier behavior changes for out-of-range offsets would require updating the test. The valid offset assumes the packet fixture is long enough for the BPF program's load size.

Test signals: two successful test-run calls with BSS `test_result` equal to `-EFAULT` and `0`, respectively.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_load_bytes.c -->
