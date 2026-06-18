# sources/distributed-fs/ceph-client/samples/bpf/ibumad_kern.c

Purpose: BPF tracepoint sample that counts InfiniBand UMAD packets by management class.

Important APIs/types/functions: declares two BPF maps for counts, `struct ib_umad_rw_args`, tracepoint handlers `on_ib_umad_read_recv`, `on_ib_umad_read_send`, and `on_ib_umad_write`, and optional `bpf_printk`.

Control flow: each tracepoint reads UMAD tracepoint arguments, derives packet class/direction, looks up or initializes counters in maps, and updates packet counts.

State and persistence: counters live in BPF maps while the program is attached.

Dependencies and integration: paired with `ibumad_user.c`; depends on `ib_umad` tracepoints and matching tracepoint format.

Risks: tracepoint structure must match kernel format. Systems without InfiniBand UMAD support will not produce data or may fail attach. Count keys/classes need to stay aligned with tracepoint semantics.

Test signals: attach on a system with UMAD activity, generate reads/writes, and verify user program dumps nonzero class counters.
