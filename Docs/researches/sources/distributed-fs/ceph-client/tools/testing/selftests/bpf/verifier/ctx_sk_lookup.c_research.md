# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ctx_sk_lookup.c

Purpose: validates allowed and disallowed direct context accesses for `struct bpf_sk_lookup` programs.

Important APIs/types/functions: uses `offsetof(struct bpf_sk_lookup, ...)`, `sizeof(struct bpf_sk_lookup)`, `BPF_LDX_MEM`, `BPF_STX_MEM`, `BPF_PROG_TYPE_SK_LOOKUP`, and `BPF_SK_LOOKUP`.

Control flow: the first large accepted test performs all permitted byte, halfword, word, and doubleword reads from `family`, `protocol`, IPv4/IPv6 addresses, ports, ingress interface, and `sk`. Negative tests reject oversized 8-byte reads from 4-byte fields, undersized reads from the 8-byte `sk` pointer, out-of-bounds reads, unaligned reads, and writes of every size.

State and persistence behavior: no persistent state. The tests validate verifier context-field access metadata: width, alignment, read/write permissions, and end-of-struct bounds.

Dependencies and integration points: must run as `BPF_PROG_TYPE_SK_LOOKUP` with expected attach type `BPF_SK_LOOKUP`; most entries use `.runs = -1` or verifier-only behavior.

Risks: context ABI field size or offset changes can break these tests. Accidentally allowing writes or partial pointer reads would expose unsafe context mutation or pointer disclosure.

Test signals: valid multi-size reads accept; invalid reads/writes reject with `invalid bpf_context access`. Some unaligned cases require `F_NEEDS_EFFICIENT_UNALIGNED_ACCESS`.
