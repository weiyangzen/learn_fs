# sources/distributed-fs/ceph-client/net/netfilter/xt_bpf.c

Purpose: `bpf` match runs socket-filter BPF programs against packets.

Important APIs/types/functions: bytecode/fd/path check helpers, `bpf_mt_check()`, `bpf_mt_check_v1()`, `bpf_mt()`, `bpf_mt_v1()`, and destroy helpers.

Control flow: check loads a `BPF_PROG_TYPE_SOCKET_FILTER` program from classic bytecode, fd, or pinned path and stores a hidden program pointer. Runtime executes it against the skb, using callback-save execution for v1. Destroy releases the program.

State and persistence: per-rule `bpf_prog` reference. Dependencies include BPF verifier/program APIs, x_tables, fd and pinned path lookup, and skb execution. Risks: bytecode length, path termination, fd type mismatch, callback state, and program ref release. Test signals: bytecode/fd/path modes, invalid mode, oversized bytecode, missing path, true/false results, destroy cleanup, and family-independent registration.
