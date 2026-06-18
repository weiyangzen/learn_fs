# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ctx_skb.c

Purpose: broad `struct __sk_buff` context access matrix covering sockets, sk_skb, tc cls/act, cgroup skb, and direct packet access.

Important APIs/types/functions: uses `offsetof(struct __sk_buff, ...)`, `offsetofend`, `BPF_LDX_MEM`, `BPF_STX_MEM`, direct packet `data` and `data_end`, program types `BPF_PROG_TYPE_SK_SKB`, `SCHED_CLS`, `SCHED_ACT`, `CGROUP_SKB`, and `CGROUP_SOCK`.

Control flow: early cases accept common skb field reads and reject invalid negative offsets or pointer comparisons. The SK_SKB section distinguishes socket tuple fields that are valid only for SK_SKB, rejects `tc_classid` and `mark`, permits selected writes (`tc_index`, `priority`), and verifies direct packet read/write after bounds checks. The `cb[]` section tests byte, half, word, and doubleword reads/writes, misalignment, out-of-bounds access, and wrong program type. Later cases cover writable fields in socket and tc programs, partial loads from fields such as `hash`, read-only `gso_segs`, `gso_size`, `hwtstamp`, padding after `gso_size`, and `wire_len` visibility. Final packet tests prove equivalent `pkt > pkt_end` and `pkt_end < pkt` checks refine packet safety.

State and persistence behavior: verifier state includes context field permissions, packet pointer bounds, endianness-sensitive partial loads, and unprivileged pointer-leak checks. No external state persists.

Dependencies and integration points: tied to `__sk_buff` ABI and per-program-type access tables in the kernel verifier. Some cases are architecture/alignment sensitive through `F_LOAD_WITH_STRICT_ALIGNMENT` and `F_NEEDS_EFFICIENT_UNALIGNED_ACCESS`.

Risks: field permission drift can expose writes from wrong program types or reject valid tc/sk_skb programs. Packet-bound equivalence is subtle and guards verifier range reasoning.

Test signals: expected diagnostics include `invalid bpf_context access`, `misaligned context access`, `different pointers`, and unprivileged `R1 leaks addr`; accepted cases often depend on explicit `.prog_type`.
