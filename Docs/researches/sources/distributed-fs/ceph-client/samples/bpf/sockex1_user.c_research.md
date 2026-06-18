# sources/distributed-fs/ceph-client/samples/bpf/sockex1_user.c

Purpose: userspace loader for the first socket filter example.

Important APIs/types/functions: opens BPF object/program/map, loads program, opens raw socket with `open_raw_sock`, attaches BPF FD via `SO_ATTACH_BPF`, sleeps/loops, and reads TCP/UDP/ICMP protocol counters.

Control flow: load object, find map/program, attach to selected interface socket, periodically look up protocol keys and print counters.

State and persistence: live socket attachment and BPF map for process lifetime.

Dependencies and integration: pairs with `sockex1_kern.c` and `sock_example.h`; requires libbpf and packet socket privileges.

Risks: assumes map key protocol numbers and kernel object naming. Interface traffic must be present.

Test signals: counters increase for known traffic after attaching to an interface.
