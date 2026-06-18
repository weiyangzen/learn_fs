<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/snprintf_btf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/snprintf_btf.c

Purpose: `snprintf_btf.c` demonstrates and validates `bpf_snprintf_btf()` formatting for multiple data types from a network receive hook. It ensures the BPF program ran, returned a positive formatting result, and executed all BPF-side subtests.

Important APIs/types/functions: `serial_test_snprintf_btf()` opens, loads, and attaches `netif_receive_skb.skel.h`, triggers receive processing with `system("ping -c 1 127.0.0.1 > /dev/null")`, then checks BSS fields `skip`, `ret`, `ran_subtests`, and `num_subtests`.

Control flow: open skeleton, load, attach, run a loopback ping, handle BPF-side `skip` if `__builtin_btf_type_id` is unavailable, assert positive `bpf_snprintf_btf` return, assert at least one subtest ran, and assert all declared subtests ran.

State and persistence: state is skeleton BSS counters and transient ICMP loopback traffic. No durable files are produced, but the test shells out to `ping`.

Dependencies: requires BTF support, `bpf_snprintf_btf()`, BPF program attachment to the receive path, loopback networking, the `ping` command, and serial execution to avoid shared network/BTF side effects.

Integration points: links BPF BTF pretty-print formatting with a real `netif_receive_skb` trigger and userspace selftest skip/pass accounting.

Risks: depends on external `ping` availability and permission. Systems lacking compiler/kernel support for `__builtin_btf_type_id` intentionally skip. If loopback receive path is filtered or ping unavailable, the BPF program may not run.

Test signals: no skip unless expected, positive `ret`, nonzero `ran_subtests`, and `ran_subtests == num_subtests`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/snprintf_btf.c -->
