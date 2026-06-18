# sources/distributed-fs/ceph-client/samples/bpf/sockex2_user.c

Purpose: userspace loader and map dumper for flow-counting socket filter example 2.

Important APIs/types/functions: local `struct pair`, libbpf object/program/map lookup, `open_raw_sock`, socket attach, and map key iteration with `bpf_map_get_next_key`.

Control flow: loads object, attaches socket filter, sleeps or waits, then iterates flow map entries and prints packet/byte counts.

State and persistence: BPF map stores flow counters during process lifetime.

Dependencies and integration: pairs with `sockex2_kern.c`; requires interface argument and privileges.

Risks: user-side key interpretation is minimal compared with kernel-side flow key. High-cardinality traffic can fill the map.

Test signals: run during network traffic and verify flow entries are printed with nonzero counts.
