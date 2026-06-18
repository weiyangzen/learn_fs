# sources/distributed-fs/ceph-client/tools/bpf/bpftool/skeleton/pid_iter.h

Purpose: Shared record layout for `pid_iter.bpf.c` and bpftool userspace. It defines the binary entry emitted by the BPF iterator.

Important APIs, types, and functions: `struct pid_iter_entry` contains BPF object id, pid, optional `bpf_cookie`, `has_bpf_cookie`, and 16-byte comm. There are no functions.

Control flow: Not applicable; this header is a data contract.

State and persistence: No state. The struct layout is serialized directly through `bpf_seq_write()`.

Dependencies and integration points: Must stay synchronized with bpftool userspace parsing and the enum/object-type comment in `pid_iter.bpf.c`. Uses kernel fixed-width types and `bool`.

Risks: Layout changes break binary iterator consumers. Padding and bool size assumptions should remain compiler/BPF ABI compatible.

Test signals: Build skeleton and run bpftool reference listing; mismatched layout would show malformed pid/id/cookie output.
