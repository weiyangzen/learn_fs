# sources/distributed-fs/ceph-client/samples/bpf/sockex3_user.c

Purpose: userspace loader for the tail-call socket flow dissector sample.

Important APIs/types/functions: user-side `struct flow_key_record` and `struct pair`, BPF object/program/map FDs, program array setup, raw socket attach, and map iteration.

Control flow: loads BPF object, finds main program and maps, populates program array with parser stage FDs, attaches main program to a raw socket, waits for traffic, then dumps flow counters.

State and persistence: program array and flow hash map persist during object lifetime; socket attach persists until socket close.

Dependencies and integration: pairs with `sockex3_kern.c` and `sock_example.h`, requires libbpf, tail-call map support, and privileges.

Risks: user and kernel definitions of flow key must stay in sync. Missing parser program names or map names break tail calls. Output decoding is sample-level.

Test signals: verify all tail-call entries update successfully and flow map contains packet/byte counts after traffic.
