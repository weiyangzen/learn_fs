# sources/distributed-fs/ceph-client/samples/bpf/sock_example.c

Purpose: standalone socket filter example using a hand-written BPF instruction array.

Important APIs/types/functions: `test_sock`, a manual `struct bpf_insn` program, BPF map creation, socket creation, `setsockopt(SO_ATTACH_BPF)`, and map lookups for TCP/UDP/ICMP protocol counters.

Control flow: creates a map, loads a socket filter that reads IP protocol and increments map counters, opens a raw socket, attaches the program, sleeps while traffic arrives, reads counters, prints them, and exits.

State and persistence: map and program live through FDs during process lifetime; no pinned persistence.

Dependencies and integration: uses `sock_example.h` for raw socket setup, BPF syscall/libbpf helpers, and a network interface argument or default.

Risks: raw socket and BPF attach require privileges. Manual instruction offsets assume Ethernet/IP layout. Traffic must arrive during the sample interval.

Test signals: run on an active interface and observe protocol counters increasing.
