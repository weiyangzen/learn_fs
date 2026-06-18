# sources/distributed-fs/ceph-client/samples/bpf/ibumad_user.c

Purpose: userspace loader and dumper for the InfiniBand UMAD BPF tracepoint sample.

Important APIs/types/functions: globals for three tracepoint links, BPF object, map FDs, `dump_counts`, `dump_all_counts`, `dump_exit`, CLI `usage`, and `main`.

Control flow: opens and loads the BPF object, attaches tracepoint programs, locates maps, then sleeps until interrupted. On interval or exit it iterates map keys and prints counts.

State and persistence: BPF links and object live during process execution; counts persist in maps until object close.

Dependencies and integration: requires libbpf, UMAD tracepoints, root/BPF privileges, and the `ibumad_kern.o` object.

Risks: no useful output on systems without UMAD traffic. Signal-triggered dump performs nontrivial work. Map layout must match kernel program.

Test signals: run with generated UMAD traffic, observe per-class counters, and confirm links are destroyed on exit.
