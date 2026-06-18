# sources/distributed-fs/ceph-client/samples/bpf/sockex1_kern.c

Purpose: simple socket filter BPF program that counts packets by IPv4 protocol number.

Important APIs/types/functions: BPF map for counters and `SEC("socket1") int bpf_prog1(struct __sk_buff *skb)`.

Control flow: loads the IP protocol byte at Ethernet header plus IPv4 protocol offset, looks up a counter map entry, increments it, and returns zero/pass behavior appropriate for the sample.

State and persistence: protocol counters live in a BPF map while attached.

Dependencies and integration: loaded by `sockex1_user.c`, uses `bpf_legacy.h` absolute load helper and packet socket attachment.

Risks: assumes Ethernet plus IPv4 header offset and does not parse VLAN/IPv6. Map key is protocol byte.

Test signals: attach to interface, generate TCP/UDP/ICMP traffic, and see counters update.
